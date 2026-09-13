import subprocess
import tempfile
import os
import time
from verifiers import VerifierResult


def run(completion: str, timeout: float = 10.0) -> VerifierResult:
    start = time.time()
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            tmp = f.name
            f.write(completion)

        proc = subprocess.run(
            ["mypy", "--strict", tmp],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        activated = proc.returncode != 0
        signal = proc.stdout.strip()
    except subprocess.TimeoutExpired:
        activated = False
        signal = "TIMEOUT"
    except Exception as e:
        activated = False
        signal = f"ERROR: {e}"
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)

    return VerifierResult(activated=activated, signal=signal, latency_ms=(time.time() - start) * 1000)
