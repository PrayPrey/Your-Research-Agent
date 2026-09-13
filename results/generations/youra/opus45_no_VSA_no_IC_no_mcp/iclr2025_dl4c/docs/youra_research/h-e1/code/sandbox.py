import subprocess
import tempfile
import re
import resource
from dataclasses import dataclass

@dataclass
class ExecResult:
    passed: bool
    error_type: str | None
    line_number: int | None
    expected: str | None
    actual: str | None
    stdout: str
    stderr: str

def _build_script(code: str, tests: str) -> str:
    return f"{code}\n\n{tests}"

def _set_limits(mem_limit_mb: int):
    def limiter():
        mem_bytes = mem_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    return limiter

def _parse_traceback(stderr: str) -> tuple[str | None, int | None]:
    error_match = re.search(r"(\w+Error|\w+Exception): (.+)", stderr)
    error_type = error_match.group(1) if error_match else None
    line_match = re.search(r'line (\d+)', stderr)
    line_number = int(line_match.group(1)) if line_match else None
    return error_type, line_number

def _extract_assertion_diff(stderr: str) -> tuple[str | None, str | None]:
    # AssertionError: X != Y
    match = re.search(r"AssertionError: (.+?) != (.+)", stderr)
    if match:
        return match.group(2).strip(), match.group(1).strip()
    # assert X == Y format
    match = re.search(r"assert (.+?) == (.+)", stderr)
    if match:
        return match.group(2).strip(), match.group(1).strip()
    return None, None

def execute_code(code: str, tests: str, timeout: int = 10, mem_limit_mb: int = 512) -> ExecResult:
    script = _build_script(code, tests)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        tmpfile = f.name

    try:
        proc = subprocess.run(
            ["python", tmpfile],
            timeout=timeout,
            preexec_fn=_set_limits(mem_limit_mb),
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return ExecResult(
                passed=True, error_type=None, line_number=None,
                expected=None, actual=None, stdout=proc.stdout, stderr=proc.stderr
            )
        error_type, line_number = _parse_traceback(proc.stderr)
        expected, actual = _extract_assertion_diff(proc.stderr)
        return ExecResult(
            passed=False, error_type=error_type, line_number=line_number,
            expected=expected, actual=actual, stdout=proc.stdout, stderr=proc.stderr
        )
    except subprocess.TimeoutExpired:
        return ExecResult(
            passed=False, error_type="Timeout", line_number=None,
            expected=None, actual=None, stdout="", stderr=f"Execution timed out after {timeout}s"
        )
    except Exception as e:
        return ExecResult(
            passed=False, error_type=type(e).__name__, line_number=None,
            expected=None, actual=None, stdout="", stderr=str(e)
        )
