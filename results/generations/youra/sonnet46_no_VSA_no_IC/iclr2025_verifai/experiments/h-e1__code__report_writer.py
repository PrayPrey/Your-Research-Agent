import json
from datetime import datetime, timezone
from pathlib import Path

RESULTS_DIR = "docs/youra_research/h-e1/results"


def write_report(checks: dict, he_count: int, mbpp_count: int,
                 output_dir: str = RESULTS_DIR,
                 extra: dict = None) -> dict:
    gate = "PASS" if all(v == "PASS" for v in checks.values()) else "FAIL"
    report = {
        "gate": gate,
        "he_failures": he_count,
        "mbpp_failures": mbpp_count,
        "total": he_count + mbpp_count,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        report.update(extra)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out = Path(output_dir) / "verification_report.json"
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    return report
