import subprocess
import tempfile
from config import CONFIG

def run_test(prompt: str, completion: str, test: str, timeout: int = CONFIG.test_timeout_sec) -> bool:
    code = prompt + completion + "\n" + test
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["python", f.name],
                capture_output=True, timeout=timeout
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

def evaluate_all(problems, completions) -> dict[str, bool]:
    comp_map = {c.task_id: c.completion for c in completions}
    results = {}
    for p in problems:
        if p.task_id in comp_map:
            results[p.task_id] = run_test(p.prompt, comp_map[p.task_id], p.test)
        else:
            results[p.task_id] = False
    return results
