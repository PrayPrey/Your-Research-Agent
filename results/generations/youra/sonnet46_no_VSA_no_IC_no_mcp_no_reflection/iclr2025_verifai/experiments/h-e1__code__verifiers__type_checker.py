import subprocess
import tempfile
import os
import json
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
            ["pyright", "--outputjson", tmp],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        try:
            data = json.loads(proc.stdout)
            diags = data.get("generalDiagnostics", [])
        except json.JSONDecodeError:
            diags = []

        activated = len(diags) > 0
        signal = json.dumps(diags[:5]) if diags else ""
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
