"""H-M4 TimedFeedbackEvaluator and efficiency ratio computation."""
import time
from typing import Any, Callable


class TimedFeedbackEvaluator:
    def __init__(self, category: str, verifier_fn: Callable, llm_client: Any) -> None:
        self.category = category
        self.verifier_fn = verifier_fn
        self.llm_client = llm_client

    def run_repair_loop(
        self, problem: dict, initial_code: str, max_iters: int = 3
    ) -> tuple[bool, float, list[float]]:
        code = initial_code
        total_overhead = 0.0
        per_iter_times: list[float] = []

        for _ in range(max_iters):
            t0 = time.perf_counter()
            feedback, passed = self._safe_verify(code, problem, SMT_FALLBACK_OVERHEAD)
            t_verify = time.perf_counter() - t0

            if passed:
                per_iter_times.append(t_verify)
                total_overhead += t_verify
                return True, total_overhead, per_iter_times

            if not feedback:
                feedback = "No feedback available. Check for syntax/runtime errors."

            t1 = time.perf_counter()
            repaired = self._repair(code, feedback, problem)
            t_repair = time.perf_counter() - t1

            if repaired:
                code = repaired

            iter_time = t_verify + t_repair
            per_iter_times.append(iter_time)
            total_overhead += iter_time

        # Final correctness check — not timed (post-budget)
        _, final_pass = self._safe_verify(code, problem, 0.0)
        return final_pass, total_overhead, per_iter_times

    def _safe_verify(self, code: str, problem: dict, timeout_overhead: float) -> tuple[str, bool]:
        try:
            return self.verifier_fn(code, problem)
        except Exception as e:
            return f"ERROR: {e}", False

    def _repair(self, code: str, feedback: str, problem: dict) -> str:
        prompt = (
            f"Fix the following Python function so it passes all tests.\n\n"
            f"Problem description:\n{problem['prompt']}\n\n"
            f"Current code:\n```python\n{code}\n```\n\n"
            f"Feedback from verifier:\n{feedback}\n\n"
            f"Return ONLY the corrected Python function, no explanation."
        )
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```python"):
                raw = raw[9:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            return raw.strip()
        except Exception:
            return code  # no-op repair on failure


SMT_FALLBACK_OVERHEAD = 30.0
