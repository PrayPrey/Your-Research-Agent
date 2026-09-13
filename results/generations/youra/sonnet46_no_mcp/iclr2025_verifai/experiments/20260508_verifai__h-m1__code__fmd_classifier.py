import ast
import json
import os
import signal
import tempfile
from typing import Dict, List

import mypy.api


def _timeout_handler(signum, frame):
    raise TimeoutError("mypy timeout")


class FMDClassifier:

    def __init__(self, mypy_timeout: int = 30, cleanup_temp_files: bool = True):
        self.mypy_timeout = mypy_timeout
        self.cleanup_temp_files = cleanup_temp_files
        self.mypy_flags = ["--ignore-missing-imports"]

    def classify_completion(
        self,
        completion: str,
        task_id: str,
        problem: dict,
    ) -> str:
        # Priority 1: syntax check
        try:
            ast.parse(completion)
        except SyntaxError:
            return "syntax"

        # Priority 2: type check via mypy
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp:
                tmp.write(completion)
                tmp_path = tmp.name

            try:
                old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(self.mypy_timeout)
                try:
                    stdout, stderr, exit_code = mypy.api.run(
                        self.mypy_flags + [tmp_path]
                    )
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)

                if exit_code == 1 and "error:" in stdout:
                    return "type"
            except (TimeoutError, Exception):
                # Conservative: cannot confirm type error on timeout/error
                pass
        finally:
            if tmp_path and self.cleanup_temp_files:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        # Priority 3: functional (runs but wrong output) — treat as functional failure
        # Since we don't run tests here, any syntactically/type-valid code that isn't
        # confirmed as success is classified as functional
        return "functional"

    def classify_pool(
        self,
        pool: Dict[str, List[dict]],
        problems: Dict[str, dict],
    ) -> Dict[str, List[str]]:
        classifications = {}
        for task_id, records in pool.items():
            problem = problems.get(task_id, {})
            cats = [
                self.classify_completion(r.get("completion", ""), task_id, problem)
                for r in records
            ]
            classifications[task_id] = cats
        return classifications

    def compute_distribution(
        self,
        classifications: Dict[str, List[str]],
    ) -> Dict[str, float]:
        counts = {"syntax": 0, "type": 0, "functional": 0, "success": 0}
        total = 0
        for cats in classifications.values():
            for c in cats:
                counts[c] = counts.get(c, 0) + 1
                total += 1
        if total == 0:
            return {k: 0.0 for k in counts}
        return {k: v / total for k, v in counts.items()}

    def compute_syntax_shift(
        self,
        baseline_dist: Dict[str, float],
        syncode_dist: Dict[str, float],
    ) -> float:
        return baseline_dist.get("syntax", 0.0) - syncode_dist.get("syntax", 0.0)

    def save_results(
        self,
        baseline_dist: Dict[str, float],
        syncode_dist: Dict[str, float],
        syntax_shift: float,
        output_path: str,
    ) -> dict:
        # Ensure all 4 keys present
        categories = ["syntax", "type", "functional", "success"]
        bd = {c: baseline_dist.get(c, 0.0) for c in categories}
        sd = {c: syncode_dist.get(c, 0.0) for c in categories}

        result = {
            "baseline_distribution": bd,
            "syncode_distribution": sd,
            "syntax_shift": syntax_shift,
            "interpretation": "positive syntax_shift = SynCode reduces syntax failure proportion",
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result
