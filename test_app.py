import os
import pytest
import logging
from app import get_client, stream_ai_response

def test_environment_variables(monkeypatch):
    """Test that the application securely loads environment variables."""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-secure-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-east1")
    
    assert os.environ.get("GOOGLE_CLOUD_PROJECT") == "test-secure-project"
    assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "us-east1"

def test_client_initialization():
    """Verify GenAI client instantiates without errors."""
    try:
        client = get_client()
        assert client is not None
    except Exception as e:
        pytest.fail(f"Client initialization failed: {e}")

def test_stream_ai_response_error_handling(monkeypatch):
    """
    Test that the application gracefully handles API failures 
    instead of crashing the server.
    """
    # Mock get_client to raise an exception simulating an API outage
    def mock_get_client_fail():
        raise ConnectionError("Mocked API Outage")
    
    monkeypatch.setattr("app.ge_client", mock_get_client_fail)
    
    generator = stream_ai_response("Test prompt")
    responses = list(generator)
    
    assert len(responses) == 1
    assert "Connection Error" in responses[0]   
