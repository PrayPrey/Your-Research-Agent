"""Adapter wrappers: expose BaseVerifierAdapter.get_feedback() on top of H-M2 FeedbackMeasurer."""
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# Add h-m2/code to sys.path so FeedbackMeasurer is importable
_H_M2_CODE = Path(__file__).parent.parent.parent.parent / "h-m2" / "code"
if str(_H_M2_CODE) not in sys.path:
    sys.path.insert(0, str(_H_M2_CODE))


@dataclass
class FeedbackResult:
    category: str
    feedback_text: str
    char_count: int
    timeout: bool = False


class BaseVerifierAdapter:
    category: str = ""

    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult:
        raise NotImplementedError


def _write_temp(code: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False)
    f.write(code)
    f.close()
    return f.name


class ExecutionVerifierAdapter(BaseVerifierAdapter):
    category = "execution"

    def __init__(self, timeout_secs: int = 5):
        self.timeout = timeout_secs

    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult:
        runnable = problem.get("runnable") or solution
        fname = _write_temp(runnable)
        try:
            result = subprocess.run(
                ["python3", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            text = result.stderr or result.stdout or "No output"
            return FeedbackResult("execution", text, len(text), False)
        except subprocess.TimeoutExpired:
            return FeedbackResult("execution", "TIMEOUT", 7, True)
        finally:
            os.unlink(fname)


class PyrightVerifierAdapter(BaseVerifierAdapter):
    category = "pyright"

    def __init__(self, timeout_secs: int = 10):
        self.timeout = timeout_secs

    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult:
        code = problem.get("code") or solution
        fname = _write_temp(code)
        try:
            result = subprocess.run(
                ["pyright", "--outputjson", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            text = result.stdout.strip() or result.stderr.strip() or "No diagnostics"
            return FeedbackResult("pyright", text, len(text), False)
        except subprocess.TimeoutExpired:
            return FeedbackResult("pyright", "TIMEOUT", 7, True)
        except FileNotFoundError:
            return FeedbackResult("pyright", "pyright not found", 20, False)
        finally:
            os.unlink(fname)


class MypyVerifierAdapter(BaseVerifierAdapter):
    category = "mypy"

    def __init__(self, timeout_secs: int = 10):
        self.timeout = timeout_secs

    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult:
        code = problem.get("code") or solution
        fname = _write_temp(code)
        try:
            result = subprocess.run(
                ["mypy", "--no-error-summary", "--ignore-missing-imports", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            text = result.stdout.strip() or "No type errors"
            return FeedbackResult("mypy", text, len(text), False)
        except subprocess.TimeoutExpired:
            return FeedbackResult("mypy", "TIMEOUT", 7, True)
        except FileNotFoundError:
            return FeedbackResult("mypy", "mypy not found", 14, False)
        finally:
            os.unlink(fname)


class Z3VerifierAdapter(BaseVerifierAdapter):
    category = "z3"

    def __init__(self, extractor, timeout_secs: int = 30):
        self.extractor = extractor
        self.timeout = timeout_secs

    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult:
        import z3 as _z3

        code = problem.get("code") or solution
        task_id = problem.get("task_id", "unknown")
        try:
            constraints = self.extractor.extract(task_id, code)
        except Exception as e:
            return FeedbackResult("z3", f"Extractor error: {e}", 0, False)

        if not constraints:
            return FeedbackResult("z3", "No Z3 constraints extractable", 0, False)

        try:
            solver = _z3.Solver()
            solver.set("timeout", (self.timeout * 1000) - 500)
            solver.add(*constraints)
            result = solver.check()
            if result == _z3.sat:
                model_str = str(solver.model())
                text = f"Z3 counterexample: {model_str}"
            elif result == _z3.unsat:
                text = "Z3: constraints unsatisfiable — code has a logical error"
            else:
                text = "Z3: timeout or unknown"
            return FeedbackResult("z3", text, len(text), result == _z3.unknown)
        except Exception as e:
            return FeedbackResult("z3", f"Z3 error: {e}", 0, False)


def build_verifiers(client, model: str = "gpt-4o-mini") -> dict:
    """Build all 4 verifier adapters."""
    from src.z3_extractor import Z3ConstraintExtractor
    extractor = Z3ConstraintExtractor(client=client, model=model)
    return {
        "execution": ExecutionVerifierAdapter(timeout_secs=5),
        "pyright": PyrightVerifierAdapter(timeout_secs=10),
        "mypy": MypyVerifierAdapter(timeout_secs=10),
        "z3": Z3VerifierAdapter(extractor=extractor, timeout_secs=30),
    }
