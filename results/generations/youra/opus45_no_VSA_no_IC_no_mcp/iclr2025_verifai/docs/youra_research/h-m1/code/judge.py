"""LLM Judge for extracting fields from structured error text."""
import json
import os
import re
import time
from typing import Dict, List, Any

from config import CONFIG, OPENAI_API_KEY, ANTHROPIC_API_KEY

# Mock mode when no API key available
MOCK_MODE = not (OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY"))


def build_extraction_prompt(structured_error_text: str, fields: List[str]) -> str:
    """Build prompt for LLM to extract fields from structured error."""
    fields_str = ", ".join(f'"{f}"' for f in fields)
    return f"""You are an expert at parsing error messages. Given the following structured error message, extract the specified fields and return them as a JSON object.

Structured Error:
{structured_error_text}

Extract these fields: {fields_str}

Return ONLY a valid JSON object with exactly these keys. For code_context, return as a list of strings.
Example format:
{{"line_number": 5, "error_type": "NameError", "error_message": "name 'x' is not defined", "code_context": ["4: y = 1", "5: x = undefined"]}}

JSON:"""


class JudgeLLM:
    """LLM wrapper for field extraction with retry/backoff."""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        temperature: float = 0.0,
        max_tokens: int = 500,
    ):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = CONFIG.get("max_retries", 5)
        self.backoff_base = CONFIG.get("backoff_base_sec", 2.0)
        self.mock_mode = MOCK_MODE
        self.client = None

        if not self.mock_mode:
            if provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY"))
            elif provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY"))
            else:
                raise ValueError(f"Unknown provider: {provider}")
        else:
            print("  [MOCK MODE] No API key - using regex-based extraction")

    def _mock_extract(self, prompt: str) -> Dict[str, Any]:
        """Regex-based extraction from structured text (simulates perfect LLM)."""
        result = {}
        # Extract line_number
        m = re.search(r'Line Number:\s*(\d+)', prompt)
        if m:
            result["line_number"] = int(m.group(1))
        # Extract error_type
        m = re.search(r'Error Type:\s*(\w+)', prompt)
        if m:
            result["error_type"] = m.group(1)
        # Extract error_message
        m = re.search(r'Message:\s*(.+?)(?:\n|$)', prompt)
        if m:
            result["error_message"] = m.group(1).strip()
        # Extract code_context
        m = re.search(r'Code Context:\s*\n((?:\s+\d+:.+\n?)+)', prompt)
        if m:
            lines = [line.strip() for line in m.group(1).strip().split('\n') if line.strip()]
            result["code_context"] = lines
        return result

    def extract(self, prompt: str) -> Dict[str, Any]:
        """Call LLM and parse JSON response. Returns {} on failure."""
        if self.mock_mode:
            return self._mock_extract(prompt)

        for attempt in range(self.max_retries):
            try:
                if self.provider == "openai":
                    resp = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    )
                    content = resp.choices[0].message.content
                else:  # anthropic
                    resp = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    content = resp.content[0].text

                # Parse JSON from response
                content = content.strip()
                # Handle markdown code blocks
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()

                return json.loads(content)

            except Exception as e:
                if "rate" in str(e).lower() or "429" in str(e):
                    sleep_time = self.backoff_base ** attempt
                    time.sleep(sleep_time)
                    continue
                # For other errors, also retry with backoff
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_base)
                    continue
                return {}

        return {}
