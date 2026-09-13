"""LLM client for GPT-4o-mini code generation and repair."""
import os
import time
from openai import OpenAI
from data import Problem
from config import ExperimentConfig


_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def _call_with_retry(messages: list, cfg: ExperimentConfig, max_retries: int = 3) -> str:
    """Call OpenAI API with exponential backoff."""
    client = _get_client()
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=cfg.model,
                messages=messages,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            time.sleep(wait)
    return ""


def generate_initial_code(problem: Problem, cfg: ExperimentConfig) -> str:
    """Generate initial code for a problem."""
    messages = [
        {"role": "system", "content": "You are a Python programming assistant. Write only the function implementation, no explanations."},
        {"role": "user", "content": f"Complete the following Python function:\n\n{problem.prompt}"},
    ]
    return _call_with_retry(messages, cfg)


def repair_code(problem: Problem, code: str, feedback_prompt: str, cfg: ExperimentConfig) -> str:
    """Repair code based on feedback."""
    messages = [
        {"role": "system", "content": "You are a Python programming assistant. Fix the code based on the feedback. Return only the corrected code."},
        {"role": "user", "content": f"Original code:\n```python\n{code}\n```\n\nFeedback:\n{feedback_prompt}\n\nProvide the corrected code:"},
    ]
    return _call_with_retry(messages, cfg)
