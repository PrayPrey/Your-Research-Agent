"""Static analysis tool wrappers for H-E1."""
import subprocess
import json
from dataclasses import dataclass
from config import CONFIG

@dataclass
class ToolResult:
    success: bool
    metric: float | int | None
    error: str | None

def run_pylint(code_path: str, timeout: int = 30) -> ToolResult:
    try:
        result = subprocess.run(
            ["pylint", "--output-format=json", "--disable=all", "--enable=E", code_path],
            capture_output=True, text=True, timeout=timeout
        )
        # pylint exits 0-63 based on findings; parse json for score
        try:
            # Extract score from stderr or compute from message count
            lines = result.stdout.strip()
            if lines:
                messages = json.loads(lines)
                # Score: 10 - (error_count * some_factor), simplified to error count
                return ToolResult(success=True, metric=len(messages), error=None)
            return ToolResult(success=True, metric=0, error=None)
        except json.JSONDecodeError:
            return ToolResult(success=True, metric=0, error=None)
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, metric=None, error="timeout")
    except Exception as e:
        return ToolResult(success=False, metric=None, error=str(e))

def run_mypy(code_path: str, timeout: int = 30) -> ToolResult:
    try:
        result = subprocess.run(
            ["mypy", "--ignore-missing-imports", code_path],
            capture_output=True, text=True, timeout=timeout
        )
        # Count error lines
        error_count = sum(1 for line in result.stdout.split("\n") if ": error:" in line)
        return ToolResult(success=True, metric=error_count, error=None)
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, metric=None, error="timeout")
    except Exception as e:
        return ToolResult(success=False, metric=None, error=str(e))

def run_radon(code_path: str, timeout: int = 30) -> ToolResult:
    try:
        result = subprocess.run(
            ["radon", "cc", "--json", code_path],
            capture_output=True, text=True, timeout=timeout
        )
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        if code_path in data and data[code_path]:
            complexities = [item["complexity"] for item in data[code_path]]
            avg = sum(complexities) / len(complexities) if complexities else 0
            return ToolResult(success=True, metric=avg, error=None)
        return ToolResult(success=True, metric=0, error=None)
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, metric=None, error="timeout")
    except json.JSONDecodeError:
        return ToolResult(success=True, metric=0, error=None)
    except Exception as e:
        return ToolResult(success=False, metric=None, error=str(e))

def run_sa_tool(tool: str, code_path: str, timeout: int = 30) -> ToolResult:
    if tool == "pylint":
        return run_pylint(code_path, timeout)
    elif tool == "mypy":
        return run_mypy(code_path, timeout)
    elif tool == "radon":
        return run_radon(code_path, timeout)
    else:
        return ToolResult(success=False, metric=None, error=f"Unknown tool: {tool}")
