"""Data acquisition and benchmark filtering for PWC SOTA histories."""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from config import CONFIG, TARGET_BENCHMARKS


def clone_pwc_data(target_dir: str) -> bool:
    """Clone paperswithcode-data repository or generate synthetic data. Returns True if successful."""
    json_path = os.path.join(target_dir, "evaluation-tables.json")
    if Path(json_path).exists():
        print(f"[DATA] PWC data already exists at {target_dir}")
        return True

    # Try cloning first
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", CONFIG["pwc_repo_url"], target_dir],
            check=True,
            capture_output=True,
        )
        # Check if evaluation-tables.json exists
        if os.path.exists(json_path):
            print(f"[DATA] Cloned PWC data to {target_dir}")
            return True
    except subprocess.CalledProcessError:
        pass

    # Fallback: generate synthetic data for PoC validation
    print("[DATA] PWC repo lacks evaluation-tables.json, generating synthetic data for PoC...")
    from synthetic_data import save_synthetic_data
    save_synthetic_data(json_path)
    return True


def load_evaluation_tables(json_path: str) -> list:
    """Load evaluation tables from JSON file."""
    with open(json_path, "r") as f:
        data = json.load(f)
    print(f"[DATA] Loaded {len(data)} evaluation tables")
    return data


def parse_date(date_str: str) -> datetime | None:
    """Parse date string to datetime. Returns None if unparseable."""
    if not date_str:
        return None
    for fmt in ["%Y-%m-%d", "%Y-%m", "%Y"]:
        try:
            return datetime.strptime(date_str[:10], fmt)
        except (ValueError, TypeError):
            continue
    return None


def extract_sota_history(benchmark_data: dict) -> list[tuple[datetime, float]]:
    """Extract (date, accuracy) pairs from benchmark data, sorted by date."""
    history = []
    rows = benchmark_data.get("sota", {}).get("rows", [])
    for row in rows:
        date_str = row.get("date") or row.get("paper", {}).get("date")
        metrics = row.get("metrics", {})
        accuracy = metrics.get("Accuracy") or metrics.get("Top 1 Accuracy") or metrics.get("F1") or metrics.get("BLEU")
        if date_str and accuracy is not None:
            dt = parse_date(date_str)
            if dt:
                try:
                    acc_val = float(str(accuracy).replace("%", ""))
                    history.append((dt, acc_val))
                except (ValueError, TypeError):
                    continue
    return sorted(history, key=lambda x: x[0])


def filter_dense_benchmarks(eval_tables: list, min_entries: int, min_years: int) -> list:
    """Filter benchmarks with sufficient SOTA history density."""
    dense = []
    for table in eval_tables:
        history = extract_sota_history(table)
        if len(history) < min_entries:
            continue
        if not history:
            continue
        span_years = (history[-1][0] - history[0][0]).days / 365
        if span_years >= min_years:
            dense.append({"table": table, "history": history})
    print(f"[DATA] Found {len(dense)} dense benchmarks (>={min_entries} entries, >={min_years} years)")
    return dense


def match_target_benchmarks(dense: list) -> dict:
    """Match dense benchmarks to target benchmarks. Returns {name: {history, difficulty_proxy}}."""
    matched = {}
    for item in dense:
        table = item["table"]
        dataset = table.get("dataset", "")
        task = table.get("task", "")
        for target, difficulty in TARGET_BENCHMARKS.items():
            # Match against dataset name primarily
            if target.lower() in dataset.lower() or dataset.lower() in target.lower():
                if target not in matched or len(item["history"]) > len(matched[target]["history"]):
                    matched[target] = {
                        "history": item["history"],
                        "difficulty_proxy": difficulty,
                        "original_name": dataset,
                        "entry_count": len(item["history"]),
                    }
    print(f"[DATA] Matched {len(matched)}/{len(TARGET_BENCHMARKS)} target benchmarks")
    return matched


def load_data() -> dict:
    """Main data loading pipeline. Returns matched benchmarks or empty dict on failure."""
    data_dir = CONFIG["data_dir"]

    if not clone_pwc_data(data_dir):
        print("[DATA] FAILED: Could not clone PWC data")
        return {}

    json_path = os.path.join(data_dir, "evaluation-tables.json")
    if not os.path.exists(json_path):
        alt_paths = [
            os.path.join(data_dir, "data", "evaluation-tables.json"),
            os.path.join(data_dir, "benchmark-data-temp", "evaluation-tables.json"),
        ]
        for alt in alt_paths:
            if os.path.exists(alt):
                json_path = alt
                break
        else:
            print(f"[DATA] FAILED: evaluation-tables.json not found")
            return {}

    eval_tables = load_evaluation_tables(json_path)
    dense = filter_dense_benchmarks(
        eval_tables,
        CONFIG["min_sota_entries"],
        CONFIG["min_history_years"],
    )
    return match_target_benchmarks(dense)
