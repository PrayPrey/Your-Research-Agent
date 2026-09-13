"""Cached OpenAI API client with retry/backoff (H-M1 pattern)."""
import json
import os
import time
from pathlib import Path


class APIClient:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        cache_path: str = ".cache/responses.jsonl",
        max_retries: int = 3,
        temperature: float = 0.0,
        max_tokens: int = 500,
    ):
        self.model = model
        self.cache_path = Path(cache_path)
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.cache: dict[str, str] = {}
        self._load_cache()
        self._client = None

    def _load_cache(self) -> None:
        if self.cache_path.exists():
            with open(self.cache_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    self.cache[entry["key"]] = entry["response"]

    def _save_to_cache(self, key: str, response: str) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "a") as f:
            f.write(json.dumps({"key": key, "response": response}) + "\n")

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def call(self, prompt: str, cache_key: str) -> str:
        if cache_key in self.cache:
            return self.cache[cache_key]

        client = self._get_client()

        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                result = response.choices[0].message.content
                self.cache[cache_key] = result
                self._save_to_cache(cache_key, result)
                return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"API call failed after {self.max_retries} retries: {e}")
                time.sleep(2 ** attempt)

        raise RuntimeError("Unexpected error in API call")

    def close(self) -> None:
        self._client = None
