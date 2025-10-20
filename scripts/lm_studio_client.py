"""Small LM Studio OpenAI-compatible client helper."""
import requests
import time

class LMStudioClient:
    def __init__(self, base_url="http://100.120.44.114:1234/v1", timeout=120):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def chat(self, model, messages, max_tokens=512, temperature=0.2):
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        last = None
        for attempt in range(5):
            try:
                r = requests.post(url, json=payload, timeout=self.timeout)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last = e
                sleep_for = min(10, 1 + attempt * 2)
                time.sleep(sleep_for)
        raise last
