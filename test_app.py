import os
import pytest
from app import get_client, stream_ai_response, sanitize_input

def test_environment_variables(monkeypatch):
    """Test secure loading of environment variables."""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-secure-project")
    assert os.environ.get("GOOGLE_CLOUD_PROJECT") == "test-secure-project"

def test_client_initialization():
    """Verify GenAI client instantiates without errors."""
    try:
        client = get_client()
        assert client is not None
    except Exception as e:
        pytest.fail(f"Client initialization failed: {e}")

def test_stream_ai_response_error_handling(monkeypatch):
    """Test application resilience against API outages."""
    def mock_get_client_fail():
        raise ConnectionError("Mocked API Outage")
    
    monkeypatch.setattr("app.get_client", mock_get_client_fail)
    
    generator = stream_ai_response("Test prompt")
    responses = list(generator)
    
    assert len(responses) == 1
    assert "Connection Error" in responses[0]

def test_input_sanitization():
    """Test security constraints against XSS and prompt injection."""
    malicious_input = "<script>alert('xss')</script>"
    clean = sanitize_input(malicious_input)
    assert "<script>" not in clean
    assert clean == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    
    long_input = "A" * 2000
    clean_long = sanitize_input(long_input)
    assert len(clean_long) == 1000
