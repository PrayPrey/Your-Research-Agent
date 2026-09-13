import json
from config import AnalysisConfig

def load_logs(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]

def validate_logs(logs: list[dict], cfg: AnalysisConfig) -> None:
    if not logs:
        raise AssertionError("Empty logs file")

    for field in cfg.required_fields:
        if not all(field in log for log in logs):
            raise AssertionError(f"Missing required field: {field}")

    conditions = set(log["condition"] for log in logs)
    expected_conds = set(cfg.conditions)
    if conditions != expected_conds:
        raise AssertionError(f"Expected conditions {expected_conds}, got {conditions}")

    iterations = set(log["iteration"] for log in logs)
    expected_iters = set(cfg.iterations)
    if iterations != expected_iters:
        raise AssertionError(f"Expected iterations {expected_iters}, got {iterations}. "
                            "h-m1 requires per-iteration trajectory data (1,2,3), not just final iteration.")
