from fastapi.testclient import TestClient

from backend.routers import llm


def test_models_endpoint_provider_and_all(monkeypatch):
    # Monkeypatch provider fetch functions to return predictable values
    monkeypatch.setattr(llm, 'fetch_openai_models', lambda: ['gpt-4', 'gpt-4o'])
    monkeypatch.setattr(llm, 'fetch_claude_models', lambda: ['claude-3', 'claude-2'])
    monkeypatch.setattr(llm, 'fetch_available_models', lambda: ['gemini-1', 'gemini-2'])
    monkeypatch.setattr(llm, 'fetch_groq_models', lambda: ['llama-3.3-70b-versatile'])

    client = TestClient(llm.router)

    # Provider-specific
    resp = client.get('/models?provider=openai')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert 'gpt-4' in data

    # All providers
    resp2 = client.get('/models')
    assert resp2.status_code == 200
    all_data = resp2.json()
    assert set(all_data.keys()) >= {'openai', 'anthropic', 'google', 'groq'}
    assert 'gpt-4' in all_data['openai']
    assert 'claude-3' in all_data['anthropic'] or 'claude-2' in all_data['anthropic']
