import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CivicMind AI", layout="wide")

# ---------------- CLEAN BLACK UI ----------------
st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
section[data-testid="stSidebar"] {display:none;}

.stApp {
    background-color: #000000;
    color: #e5e5e5;
}

/* Title */
.title {
    text-align: center;
    font-size: 30px;
    font-weight: 600;
    margin-top: -100px;
    margin-bottom: 30px;
}

/* Chat container */
.chat-container {
    max-width: 850px;
    margin: auto;
    padding-bottom: 120px;
}

/* Messages */
.msg {
    padding: 12px 14px;
    border-radius: 10px;
    margin: 8px 0;
    font-size: 15px;
}

.user {
    background-color: #111;
    text-align: right;
}

.bot {
    background-color: #0a0a0a;
}

/* Chat input */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
}

/* Typing dots */
.dot {
    height: 6px;
    width: 6px;
    margin: 2px;
    background-color: white;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.2s infinite;
}

.dot:nth-child(2){animation-delay:0.2s;}
.dot:nth-child(3){animation-delay:0.4s;}

@keyframes bounce {
    0%,80%,100%{transform:scale(0.5);}
    40%{transform:scale(1);}
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="title">🗳️ Understand Elections with AI</div>', unsafe_allow_html=True)

# ---------------- AI CLIENT ----------------
client = genai.Client(
    vertexai=True,
    project="ai-project-495106",
    location="us-central1",
    http_options=HttpOptions(api_version="v1")
)

# ---------------- STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome. Ask anything about elections."}
    ]

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# ---------------- FUNCTION ----------------
def get_ai_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ---------------- CHAT DISPLAY ----------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(
        f'<div class="msg {role_class}">{msg["content"]}</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INPUT ----------------
user_input = st.chat_input("Ask about elections...")

if user_input:
    st.session_state.last_prompt = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Typing animation
    placeholder = st.empty()
    placeholder.markdown("""
    <div style='text-align:center'>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    </div>
    """, unsafe_allow_html=True)

    response = get_ai_response(user_input)
    placeholder.empty()

    # Streaming effect
    full = ""
    msg_placeholder = st.empty()

    for char in response:
        full += char
        msg_placeholder.markdown(
            f'<div class="msg bot">{full}</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.003)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ---------------- REGENERATE ----------------
if st.session_state.last_prompt:
    if st.button("🔄 Regenerate"):
        response = get_ai_response(st.session_state.last_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()