"""A-3: Static analysis pipeline (pylint + mypy)."""
import subprocess
import json
import tempfile
from pathlib import Path

def run_pylint(code: str, timeout: int = 30) -> set:
    """Run pylint, return error codes as set."""
    errors = set()
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        result = subprocess.run(
            ["pylint", "--output-format=json", "--disable=C,R", temp_path],
            capture_output=True, text=True, timeout=timeout
        )
        Path(temp_path).unlink(missing_ok=True)

        items = json.loads(result.stdout) if result.stdout.strip() else []
        for item in items:
            if isinstance(item, dict) and "message-id" in item:
                errors.add(f"pylint:{item['message-id']}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        pass
    return errors

def run_mypy(code: str, timeout: int = 30) -> set:
    """Run mypy, return error strings as set."""
    errors = set()
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        result = subprocess.run(
            ["mypy", "--no-error-summary", "--ignore-missing-imports", temp_path],
            capture_output=True, text=True, timeout=timeout
        )
        Path(temp_path).unlink(missing_ok=True)

        for line in result.stdout.splitlines():
            if "error:" in line:
                msg = line.split("error:")[1].strip()[:50]
                errors.add(f"mypy:{msg}")
    except (subprocess.TimeoutExpired, Exception):
        pass
    return errors

def run_static_analysis(code: str) -> set:
    """Run both pylint and mypy, return union of errors."""
    return run_pylint(code) | run_mypy(code)
