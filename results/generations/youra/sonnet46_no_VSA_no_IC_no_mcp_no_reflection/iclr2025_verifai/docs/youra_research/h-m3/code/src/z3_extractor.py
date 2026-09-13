"""LLM-based Z3 constraint extractor from docstrings."""
import json
import re

import z3
from openai import OpenAI

SYSTEM_PROMPT = """You are a formal verification assistant.
Given a Python function docstring, output ONLY valid Z3 Python expressions as a JSON list of strings.
Each string must be a valid Z3 BoolRef expression using z3 variables.
Declare variables using z3.Int(), z3.Real(), z3.Bool() as needed.
Return [] if constraints cannot be expressed in Z3.
Example output: ["z3.And(x >= 0, x <= 100)"]"""

USER_TEMPLATE = """Docstring:
{docstring}

Return a JSON list of Z3 constraint strings. No explanation, no markdown."""

SAFE_Z3_NS = {
    "z3": z3,
    "Int": z3.Int, "Real": z3.Real, "Bool": z3.Bool,
    "And": z3.And, "Or": z3.Or, "Not": z3.Not,
    "If": z3.If, "Implies": z3.Implies,
}


def _extract_docstring(code: str) -> str:
    """Extract first docstring from code."""
    m = re.search(r'"""(.*?)"""', code, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"'''(.*?)'''", code, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


class Z3ConstraintExtractor:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini", timeout_secs: int = 10):
        self.client = client
        self.model = model
        self.timeout_secs = timeout_secs

    def extract(self, task_id: str, code: str) -> list | None:
        docstring = _extract_docstring(code)
        if not docstring or len(docstring) < 10:
            return None
        expr_strings = self._call_llm(docstring)
        if expr_strings is None:
            return None
        if len(expr_strings) == 0:
            return []
        return self._safe_eval(expr_strings)

    def _call_llm(self, docstring: str) -> list[str] | None:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_TEMPLATE.format(docstring=docstring[:500])},
                ],
                temperature=0,
                max_tokens=256,
            )
            content = resp.choices[0].message.content.strip()
            # Strip markdown fences if present
            content = re.sub(r"```json\n?|```\n?", "", content).strip()
            result = json.loads(content)
            if isinstance(result, list) and all(isinstance(s, str) for s in result):
                return result
            return None
        except Exception:
            return None

    def _safe_eval(self, expr_strings: list[str]) -> list | None:
        constraints = []
        try:
            for expr in expr_strings:
                val = eval(expr, {"__builtins__": {}}, SAFE_Z3_NS)
                if not isinstance(val, z3.BoolRef):
                    return None
                constraints.append(val)
            return constraints
        except Exception:
            return None
