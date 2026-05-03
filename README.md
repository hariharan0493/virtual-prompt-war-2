# 🗳️ ClearVote AI

An intelligent, enterprise-grade assistant that helps users understand the election process in a simple, interactive, and structured way. Built securely for Google Cloud Run.

---

## 🚀 Features
- **🧠 Native AI Streaming**: Zero-latency responses using Google GenAI generators.
- **♿ 100% Accessible UI**: Utilizes Streamlit's native semantic chat elements.
- **🛡️ Secure Configuration**: Environment variable injection for cloud infrastructure.
- **⚙️ Context-Aware**: System instructions lock the AI strictly to civic topics.
- **🔒 Responsible AI**: Vertex AI safety settings configured to prevent harmful generation.
- **📊 Production Logging**: Built-in system tracking for monitorability.

---

## 🛠️ Tech Stack
- **Frontend/UI**: Streamlit
- **Backend**: Python 3.11, Pytest
- **AI Model**: Google Gemini 2.5 Flash (Vertex AI)
- **Deployment**: Google Cloud Run

---

## 📦 Installation & Testing (Local)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Authenticate with Google Cloud
gcloud auth application-default login

# 3. Run automated tests (Required for quality assurance)
pytest test_app.py -v

# 4. Run the application
python3 -m streamlit run app.py
