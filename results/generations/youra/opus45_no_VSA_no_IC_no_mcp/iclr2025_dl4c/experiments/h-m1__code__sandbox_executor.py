"""Sandbox execution for buggy code with trace collection."""
import subprocess
import tempfile
import shutil
import os
from dataclasses import dataclass
from config import CFG

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    traceback: str
    timed_out: bool

class SandboxExecutor:
    def __init__(self, timeout_s: int = None, memory_mb: int = None):
        self.timeout_s = timeout_s or CFG.timeout_s
        self.memory_mb = memory_mb or CFG.memory_mb

    def _build_script(self, code: str, tests: str) -> str:
        """Combine code and tests into runnable script."""
        return f"{code}\n\n{tests}"

    def run(self, code: str, tests: str) -> ExecutionResult:
        """Execute code+tests in subprocess with timeout."""
        tmpdir = tempfile.mkdtemp()
        script_path = os.path.join(tmpdir, "test_solution.py")
        try:
            script = self._build_script(code, tests)
            with open(script_path, "w") as f:
                f.write(script)
            try:
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_s,
                    cwd=tmpdir,
                )
                timed_out = False
                exit_code = result.returncode
                stdout = result.stdout
                stderr = result.stderr
            except subprocess.TimeoutExpired:
                timed_out = True
                exit_code = -1
                stdout = ""
                stderr = "TimeoutError: Execution timed out"
            traceback_str = self._extract_traceback(stderr)
            return ExecutionResult(stdout, stderr, exit_code, traceback_str, timed_out)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _extract_traceback(self, stderr: str) -> str:
        """Extract traceback portion from stderr."""
        import re
        match = re.search(r'Traceback \(most recent call last\):[\s\S]*', stderr)
        return match.group(0) if match else stderr

    def close(self):
        pass

if __name__ == "__main__":
    executor = SandboxExecutor()
    code = "def add(a, b): return a + b"
    tests = "assert add(1, 2) == 3"
    result = executor.run(code, tests)
    print(f"Exit: {result.exit_code}, Timeout: {result.timed_out}")
    print(f"Stderr: {result.stderr[:200] if result.stderr else 'None'}")
