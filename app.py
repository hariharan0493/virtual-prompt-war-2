import os
import logging
import streamlit as st
from typing import Generator
from google import genai
from google.genai.types import (
    HttpOptions, 
    GenerateContentConfig, 
    HarmCategory, 
    HarmBlockThreshold
)

# ---------------- LOGGING & CONFIG ----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title="ClearVote AI", page_icon="🗳️", layout="centered")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-project-495106")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# ---------------- API INITIALIZATION ----------------
@st.cache_resource
def get_client() -> genai.Client:
    """Initializes and caches the Google Vertex AI GenAI client."""
    logger.info("Initializing Vertex AI Client.")
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        http_options=HttpOptions(api_version="v1")
    )

def stream_ai_response(prompt: str) -> Generator[str, None, None]:
    """
    Streams the response from Gemini, applying strict system instructions 
    and safety settings for responsible AI deployment.
    """
    try:
        # Moved inside the try block to catch initialization failures
        client = get_client()
        
        # Advanced Google Services: System Instructions & Safety Settings
        config = GenerateContentConfig(
            system_instruction="You are an expert on elections and civic processes. Only answer questions related to elections. If asked about unrelated topics, politely redirect to elections.",
            temperature=0.3, # Lower temperature for factual, grounded civic answers
            safety_settings=[
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE},
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE},
            ]
        )
        
        logger.info(f"Generating content for prompt length: {len(prompt)}")
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
        yield "⚠️ **Connection Error:** Unable to reach the AI service. Please try again later."
# ---------------- UI & STATE MANAGEMENT ----------------
st.title("🗳️ ClearVote AI")
st.markdown("An intelligent assistant simplifying electoral processes, rules, and terminology.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome. What would you like to know about the electoral process?"}
    ]

# Problem Alignment: Starter questions to guide the user
st.sidebar.title("📌 Try Asking:")
starter_prompts = [
    "How does the Electoral College work?",
    "What is the difference between a primary and a caucus?",
    "Explain gerrymandering simply."
]

for starter in starter_prompts:
    if st.sidebar.button(starter):
        st.session_state.starter_trigger = starter

# Render existing conversation history using accessible native components
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT HANDLING ----------------
# Check if input came from a sidebar starter prompt OR the chat input
user_input = st.chat_input("Ask about elections...")
if getattr(st.session_state, 'starter_trigger', None):
    user_input = st.session_state.starter_trigger
    st.session_state.starter_trigger = None # Reset after use

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_stream = stream_ai_response(user_input)
        full_response = st.write_stream(response_stream)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
