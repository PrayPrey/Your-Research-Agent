"""4-verifier feedback measurement pipeline for H-M2."""
import json
import os
import subprocess
import tempfile

import z3


def _write_temp(code: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False)
    f.write(code)
    f.close()
    return f.name


class FeedbackMeasurer:
    def __init__(self, timeout_secs: int = 10):
        self.timeout = timeout_secs

    def measure_execution(self, code: str) -> dict:
        fname = _write_temp(code)
        try:
            result = subprocess.run(
                ["python3", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            feedback = result.stderr or result.stdout
            return {"verifier": "execution", "char_count": len(feedback), "field_count": 1, "timeout": False}
        except subprocess.TimeoutExpired:
            return {"verifier": "execution", "char_count": 0, "field_count": 0, "timeout": True}
        finally:
            os.unlink(fname)

    def measure_pyright(self, code: str) -> dict:
        fname = _write_temp(code)
        try:
            result = subprocess.run(
                ["pyright", "--outputjson", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            raw = result.stdout.strip()
            if not raw:
                return {"verifier": "pyright", "char_count": 0, "field_count": 0, "timeout": False}
            data = json.loads(raw)
            errors = data.get("generalDiagnostics", [])
            field_count = sum(len(e) for e in errors)
            return {"verifier": "pyright", "char_count": len(raw), "field_count": field_count, "timeout": False}
        except subprocess.TimeoutExpired:
            return {"verifier": "pyright", "char_count": 0, "field_count": 0, "timeout": True}
        except (json.JSONDecodeError, Exception):
            return {"verifier": "pyright", "char_count": 0, "field_count": 0, "timeout": False}
        finally:
            os.unlink(fname)

    def measure_mypy(self, code: str) -> dict:
        fname = _write_temp(code)
        try:
            result = subprocess.run(
                ["mypy", "--no-error-summary", "--ignore-missing-imports", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            output = result.stdout
            error_lines = [l for l in output.splitlines() if ": error:" in l]
            return {"verifier": "mypy", "char_count": len(output), "field_count": len(error_lines), "timeout": False}
        except subprocess.TimeoutExpired:
            return {"verifier": "mypy", "char_count": 0, "field_count": 0, "timeout": True}
        finally:
            os.unlink(fname)

    def measure_z3(self, constraints: list | None) -> dict:
        base = {"verifier": "z3", "char_count": 0, "field_count": 0, "timeout": False}
        if constraints is None:
            return base
        try:
            solver = z3.Solver()
            solver.set("timeout", (self.timeout * 1000) - 500)
            if constraints:
                solver.add(*constraints)
            result = solver.check()
            if result == z3.sat:
                model = solver.model()
                model_str = str(model)
                return {"verifier": "z3", "char_count": len(model_str), "field_count": len(model), "timeout": False}
            elif result == z3.unsat:
                return {"verifier": "z3", "char_count": 5, "field_count": 0, "timeout": False}
            else:
                return {**base, "timeout": True}
        except Exception:
            return {**base, "timeout": True}

    def measure_all(self, code: str, z3_constraints: list | None, runnable: str | None = None) -> list[dict]:
        exec_code = runnable if runnable else code
        return [
            self.measure_execution(exec_code),
            self.measure_pyright(code),
            self.measure_mypy(code),
            self.measure_z3(z3_constraints),
        ]
