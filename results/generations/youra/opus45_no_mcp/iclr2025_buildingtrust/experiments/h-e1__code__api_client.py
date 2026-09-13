"""OpenAI API client with disk cache and retry logic."""
import hashlib
import json
import os
import time
from pathlib import Path
from config import CONFIG
from openai import OpenAI


class APIClient:
    def __init__(self, model: str = None, cache_path: str = None):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY environment variable required. "
                "Set it before running: export OPENAI_API_KEY='sk-...'"
            )
        self.model = model or CONFIG.model.model_name
        self.cache_path = Path(cache_path or CONFIG.api.cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
        self.client = OpenAI()
        self.last_call_time = 0
        self.min_interval = 60.0 / CONFIG.api.requests_per_minute

    def _load_cache(self) -> dict:
        cache = {}
        if self.cache_path.exists():
            with open(self.cache_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    cache[entry["key"]] = entry["response"]
        return cache

    def _save_to_cache(self, key: str, response: str):
        with open(self.cache_path, "a") as f:
            f.write(json.dumps({"key": key, "response": response}) + "\n")
        self.cache[key] = response

    def _cache_key(self, prompt: str) -> str:
        return hashlib.sha256(f"{self.model}:{prompt}".encode()).hexdigest()

    def call(self, prompt: str) -> str:
        key = self._cache_key(prompt)
        if key in self.cache:
            return self.cache[key]

        # Rate limiting
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        for attempt in range(CONFIG.api.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=CONFIG.model.temperature,
                    max_tokens=CONFIG.model.max_tokens
                )
                self.last_call_time = time.time()
                text = response.choices[0].message.content or ""
                self._save_to_cache(key, text)
                return text
            except Exception as e:
                if attempt == CONFIG.api.max_retries - 1:
                    print(f"API call failed after {CONFIG.api.max_retries} attempts: {e}")
                    return ""
                wait = CONFIG.api.retry_backoff_base ** attempt
                time.sleep(wait)
        return ""
