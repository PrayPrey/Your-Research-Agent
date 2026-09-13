import subprocess
import tempfile
import json
import re
from dataclasses import dataclass
from config import CONFIG

@dataclass
class ToolResult:
    success: bool
    metric: float | int | None
    error: str | None

def run_pylint(code: str, timeout: int = CONFIG.sa_timeout_sec) -> ToolResult:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["pylint", f.name, "--output-format=json", "--disable=all", "--enable=all"],
                capture_output=True, text=True, timeout=timeout
            )
            match = re.search(r"rated at ([\d.]+)/10", result.stdout + result.stderr)
            if match:
                return ToolResult(True, float(match.group(1)), None)
            result2 = subprocess.run(
                ["pylint", f.name, "--score=y"],
                capture_output=True, text=True, timeout=timeout
            )
            match2 = re.search(r"rated at ([\d.-]+)/10", result2.stdout + result2.stderr)
            if match2:
                return ToolResult(True, float(match2.group(1)), None)
            return ToolResult(True, 5.0, None)
        except subprocess.TimeoutExpired:
            return ToolResult(False, None, "timeout")
        except Exception as e:
            return ToolResult(False, None, str(e))

def run_mypy(code: str, timeout: int = CONFIG.sa_timeout_sec) -> ToolResult:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["mypy", f.name, "--ignore-missing-imports"],
                capture_output=True, text=True, timeout=timeout
            )
            error_count = len([l for l in result.stdout.splitlines() if ": error:" in l])
            return ToolResult(True, error_count, None)
        except subprocess.TimeoutExpired:
            return ToolResult(False, None, "timeout")
        except Exception as e:
            return ToolResult(False, None, str(e))

def run_radon(code: str, timeout: int = CONFIG.sa_timeout_sec) -> ToolResult:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["radon", "cc", f.name, "-a", "-j"],
                capture_output=True, text=True, timeout=timeout
            )
            data = json.loads(result.stdout)
            if f.name in data and data[f.name]:
                cc_values = [b["complexity"] for b in data[f.name]]
                return ToolResult(True, sum(cc_values) / len(cc_values), None)
            return ToolResult(True, 1.0, None)
        except subprocess.TimeoutExpired:
            return ToolResult(False, None, "timeout")
        except Exception as e:
            return ToolResult(False, None, str(e))
