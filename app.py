import os
import html
import logging
import streamlit as st
from typing import Generator
from google import genai
from google.genai.types import (
    HttpOptions, 
    GenerateContentConfig, 
    HarmCategory, 
    HarmBlockThreshold,
    Tool,
    GoogleSearch
)

# ---------------- LOGGING & CONFIG ----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title="ClearVote AI", page_icon="🗳️", layout="centered")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-project-495106")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# ---------------- SECURITY & UTILS ----------------
def sanitize_input(user_prompt: str) -> str:
    """Sanitizes user input to prevent XSS and limits length for prompt injection defense."""
    sanitized = html.escape(user_prompt.strip())
    return sanitized[:1000]

# ---------------- API INITIALIZATION ----------------
@st.cache_resource
def get_client() -> genai.Client:
    """Initializes and caches the Google Vertex AI GenAI client."""
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        http_options=HttpOptions(api_version="v1")
    )

def stream_ai_response(prompt: str) -> Generator[str, None, None]:
    """
    Streams response from Gemini.
    Features: System Instructions, Safety Settings, and Google Search Grounding.
    """
    try:
        client = get_client()
        
        # Advanced Google Services: Grounding via Google Search & Strict Safety
        config = GenerateContentConfig(
            system_instruction="You are an expert on elections and civic processes. Answer strictly regarding elections.",
            temperature=0.2,
            tools=[Tool(google_search=GoogleSearch())], # Grounds answers in real-time facts
            safety_settings=[
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE},
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE},
            ]
        )
        
        logger.info("Generating grounded content stream.")
        response_stream = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"API Connection Error: {str(e)}")
        yield "⚠️ **Connection Error:** Unable to reach the AI service."

# ---------------- UI & STATE MANAGEMENT ----------------
# Accessibility: Semantic HTML for screen readers
st.markdown('<h1 aria-label="ClearVote AI Box"><span role="img" aria-label="ballot box">🗳️</span> ClearVote AI</h1>', unsafe_allow_html=True)
st.markdown("An intelligent assistant simplifying electoral processes, rules, and terminology.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome. What would you like to know about the electoral process?"}
    ]

st.sidebar.markdown('<h2 aria-label="Try Asking">📌 Try Asking:</h2>', unsafe_allow_html=True)
starter_prompts = [
    "How does the Electoral College work?",
    "What is the difference between a primary and a caucus?",
    "Explain gerrymandering simply."
]

for starter in starter_prompts:
    # Accessibility: help parameter creates ARIA tooltips
    if st.sidebar.button(starter, help=f"Click to ask: {starter}"):
        st.session_state.starter_trigger = starter

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT HANDLING ----------------
raw_input = st.chat_input("Ask about elections...", max_chars=1000)
user_input = getattr(st.session_state, 'starter_trigger', raw_input)

if user_input:
    st.session_state.starter_trigger = None 
    clean_input = sanitize_input(user_input)
    
    if clean_input:
        st.session_state.messages.append({"role": "user", "content": clean_input})
        with st.chat_message("user"):
            st.markdown(clean_input)

        with st.chat_message("assistant"):
            response_stream = stream_ai_response(clean_input)
            full_response = st.write_stream(response_stream)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
