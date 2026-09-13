import csv
import json
from math import isfinite
from pathlib import Path


def aggregate_results(results: list[dict]) -> dict:
    """Compute summary stats from extraction results."""
    cv_vals = [r["model_cv_pr"] for r in results if isfinite(r["model_cv_pr"])]
    return {
        "n_models_processed": len(results),
        "n_models_valid": len(cv_vals),
        "completion_rate": len(cv_vals) / len(results) if results else 0,
        "mean_cv_pr": sum(cv_vals) / len(cv_vals) if cv_vals else float("nan"),
        "std_cv_pr": (
            (sum((v - sum(cv_vals) / len(cv_vals)) ** 2 for v in cv_vals) / len(cv_vals)) ** 0.5
            if len(cv_vals) > 1
            else 0.0
        ),
        "min_cv_pr": min(cv_vals) if cv_vals else float("nan"),
        "max_cv_pr": max(cv_vals) if cv_vals else float("nan"),
    }


def check_success_criteria(summary: dict) -> bool:
    """Check if extraction meets success criteria."""
    if summary["completion_rate"] < 0.95:
        return False
    if not isfinite(summary["mean_cv_pr"]):
        return False
    if not (0 < summary["min_cv_pr"] and summary["max_cv_pr"] < 10):
        return False
    return True


def save_results(results: list[dict], summary: dict, out_dir: str) -> None:
    """Save results to CSV and JSON."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(out_path / "results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["model", "model_cv_pr", "time_sec", "n_layers"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "model": r["model"],
                "model_cv_pr": r["model_cv_pr"],
                "time_sec": r.get("time_sec", 0),
                "n_layers": len(r["layers"]),
            })

    with open(out_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    with open(out_path / "full_results.json", "w") as f:
        json.dump(results, f, indent=2)
