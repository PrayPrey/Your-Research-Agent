import re
import subprocess
import sys
import tempfile
import os
from src.data_loader import Problem


def clean_code(raw: str, problem: Problem) -> str:
    """Strip markdown fences and extract Python function body."""
    code = raw.strip()
    # Remove ```python ... ``` fences
    code = re.sub(r"^```python\s*", "", code)
    code = re.sub(r"^```\s*", "", code)
    code = re.sub(r"```\s*$", "", code)
    code = code.strip()
    return code


def execute_solution(code: str, problem: Problem) -> dict:
    """
    Execute generated code against problem tests.
    Returns {"passed": bool, "error": str or None, "error_type": str or None}
    """
    cleaned = clean_code(code, problem)

    if problem.source == "humaneval":
        # Ensure function body is indented (h-e1 completions may lack first-line indent)
        indented_lines = []
        for line in cleaned.splitlines():
            stripped = line.lstrip()
            if stripped and not line.startswith("    ") and not line.startswith("\t"):
                indented_lines.append("    " + stripped)
            else:
                indented_lines.append(line)
        indented = "\n".join(indented_lines)
        # Pass function object (not string) to check()
        full_code = problem.prompt + indented + "\n\n" + problem.test_code + "\ncheck(" + problem.entry_point + ")"
    else:
        # MBPP: test_code contains assert statements
        full_code = cleaned + "\n\n" + problem.test_code

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(full_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return {"passed": True, "error": None, "error_type": None, "tmp_path": tmp_path, "code": full_code}
        else:
            err = result.stderr.strip() or result.stdout.strip()
            # Extract exception type from traceback
            error_type = _extract_exception_type(err)
            return {"passed": False, "error": err, "error_type": error_type, "tmp_path": tmp_path, "code": full_code}
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "TimeoutExpired", "error_type": "TimeoutExpired", "tmp_path": tmp_path, "code": cleaned}
    except Exception as e:
        return {"passed": False, "error": str(e), "error_type": type(e).__name__, "tmp_path": tmp_path, "code": cleaned}
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _extract_exception_type(stderr: str) -> str:
    """Extract the exception class name from a Python traceback string."""
    lines = [l.strip() for l in stderr.strip().splitlines() if l.strip()]
    for line in reversed(lines):
        # Match "ExceptionName:" or bare "ExceptionName" (when no message follows)
        m = re.match(r"^([A-Za-z][A-Za-z0-9_]+)(:|$|\s)", line)
        if m:
            name = m.group(1)
            if name not in ("File", "assert", "During", "The", "This", "Traceback", "raise"):
                return name
    return "UnknownError"
