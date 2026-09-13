"""A-3: API Client + Cache - OpenAI wrapper, JSONL cache, retry/backoff"""
import json
import os
import time
from openai import OpenAI, RateLimitError, APIError


class APIClient:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        cache_path: str = ".cache/responses.jsonl",
        max_retries: int = 3,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        self.model = model
        self.cache_path = cache_path
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._cache: dict[str, str] = {}
        self._load_cache()
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        self._cache_file = open(cache_path, "a")
        self.client = OpenAI()

    def _load_cache(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path) as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        self._cache[rec["key"]] = rec["response"]

    def call(self, prompt: str, cache_key: str) -> str:
        if cache_key in self._cache:
            return self._cache[cache_key]

        for attempt in range(self.max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                text = resp.choices[0].message.content
                self._cache[cache_key] = text
                self._cache_file.write(json.dumps({"key": cache_key, "response": text}) + "\n")
                self._cache_file.flush()
                return text
            except RateLimitError:
                time.sleep(2 ** attempt)
            except APIError as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError(f"API call failed after {self.max_retries} retries: {cache_key}")

    def close(self):
        self._cache_file.close()


if __name__ == "__main__":
    client = APIClient()
    resp = client.call("Say hello", "test_hello")
    print(f"Response: {resp}")
    client.close()
