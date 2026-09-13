import subprocess
import tempfile
import os
import time
from verifiers import VerifierResult


def run(problem_id: str, completion: str, test_code: str, timeout: float = 3.0) -> VerifierResult:
    start = time.time()
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            tmp = f.name
            f.write(completion + "\n" + test_code)

        proc = subprocess.run(
            ["python", tmp],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        activated = proc.returncode != 0
        signal = (proc.stdout + proc.stderr).strip()
        if activated and not signal:
            signal = f"EXIT_CODE_{proc.returncode}"
    except subprocess.TimeoutExpired:
        activated = False
        signal = "TIMEOUT"
    except Exception as e:
        activated = True
        signal = f"ERROR: {e}"
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)

    return VerifierResult(activated=activated, signal=signal, latency_ms=(time.time() - start) * 1000)
