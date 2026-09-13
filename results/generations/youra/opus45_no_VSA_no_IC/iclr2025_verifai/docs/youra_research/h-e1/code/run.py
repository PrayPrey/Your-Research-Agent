"""Main execution for H-E1: Static Analysis Tool Coverage Validation."""
import json
import os
import tempfile
from pathlib import Path
from dataclasses import asdict
from config import CONFIG
from dataset import load_all_samples, Sample
from sa_tools import run_sa_tool, ToolResult

def write_temp_file(sample: Sample) -> str:
    os.makedirs(CONFIG.TEMP_DIR, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix=".py", dir=CONFIG.TEMP_DIR)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(sample.code)
    return path

def process_sample(sample: Sample) -> dict:
    path = write_temp_file(sample)
    try:
        pylint_result = run_sa_tool("pylint", path, CONFIG.TIMEOUT_SEC)
        mypy_result = run_sa_tool("mypy", path, CONFIG.TIMEOUT_SEC)
        radon_result = run_sa_tool("radon", path, CONFIG.TIMEOUT_SEC)
        return {
            "task_id": sample.task_id,
            "source": sample.source,
            "pylint": asdict(pylint_result),
            "mypy": asdict(mypy_result),
            "radon": asdict(radon_result),
        }
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

def aggregate(records: list[dict]) -> dict:
    n = len(records)
    if n == 0:
        return {"pylint_rate": 0, "mypy_rate": 0, "radon_rate": 0, "min_valid_rate": 0, "pass": False, "n": 0}

    pylint_success = sum(1 for r in records if r["pylint"]["success"])
    mypy_success = sum(1 for r in records if r["mypy"]["success"])
    radon_success = sum(1 for r in records if r["radon"]["success"])

    rates = {
        "pylint_rate": pylint_success / n,
        "mypy_rate": mypy_success / n,
        "radon_rate": radon_success / n,
    }
    min_rate = min(rates.values())
    return {
        **rates,
        "min_valid_rate": min_rate,
        "pass": min_rate >= CONFIG.VALID_RATE_THRESHOLD,
        "n": n
    }

def main():
    print("H-E1: Static Analysis Tool Coverage Validation")
    print("=" * 50)

    samples = load_all_samples()
    print(f"\nProcessing {len(samples)} samples...")

    records = []
    for i, sample in enumerate(samples):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(samples)}")
        records.append(process_sample(sample))

    summary = aggregate(records)
    failures = [r for r in records if not (r["pylint"]["success"] and r["mypy"]["success"] and r["radon"]["success"])]

    results_dir = Path(CONFIG.RESULTS_DIR)
    results_dir.mkdir(exist_ok=True)

    with open(results_dir / CONFIG.COVERAGE_FILE, "w") as f:
        json.dump(records, f, indent=2)
    with open(results_dir / CONFIG.SUMMARY_FILE, "w") as f:
        json.dump({"hypothesis": "h-e1", **summary}, f, indent=2)
    with open(results_dir / CONFIG.FAILURES_FILE, "w") as f:
        json.dump(failures, f, indent=2)

    print(f"\nResults:")
    print(f"  Pylint valid rate: {summary['pylint_rate']:.2%}")
    print(f"  Mypy valid rate:   {summary['mypy_rate']:.2%}")
    print(f"  Radon valid rate:  {summary['radon_rate']:.2%}")
    print(f"  Min valid rate:    {summary['min_valid_rate']:.2%}")
    print(f"  PASS: {summary['pass']}")
    print(f"\nOutputs written to {results_dir}/")

if __name__ == "__main__":
    main()
