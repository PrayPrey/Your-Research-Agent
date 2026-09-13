"""TrainingWrapper: Check H-E1 log sufficiency and trigger training if needed."""

import os
import sys
import subprocess

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]

TRAINING_CONFIG = {
    "h_e1_train_script": "h-e1/code/training/train.py",
    "log_dir": "h-e1/logs",
    "conditions": CONDITIONS,
    "cuda_device": "1",   # Use GPU 1 (free H100)
    "min_rows": 10,
}

H_E1_TRAIN_SCRIPT = TRAINING_CONFIG["h_e1_train_script"]
LOG_DIR = TRAINING_CONFIG["log_dir"]
MIN_ROWS = 5000  # Full training requirement


def check_logs_sufficient(
    log_dir: str = LOG_DIR,
    min_rows: int = MIN_ROWS,
) -> tuple:
    """Check if all 4 condition CSVs exist with >= min_rows rows.
    Returns (all_sufficient, {condition: row_count})."""
    counts = {}
    for condition in CONDITIONS:
        csv_path = os.path.join(log_dir, f"reward_density_{condition}.csv")
        if not os.path.exists(csv_path):
            counts[condition] = 0
        else:
            with open(csv_path) as f:
                counts[condition] = sum(1 for _ in f) - 1  # subtract header
    all_sufficient = all(v >= min_rows for v in counts.values())
    return all_sufficient, counts


def run_full_training(
    condition: str,
    cuda_device: str = TRAINING_CONFIG["cuda_device"],
    train_script: str = H_E1_TRAIN_SCRIPT,
) -> int:
    """Run training for one condition via subprocess. Returns returncode (0 = success)."""
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = cuda_device
    cmd = [sys.executable, train_script, "--condition", condition]
    print(f"  Running: CUDA_VISIBLE_DEVICES={cuda_device} python {train_script} --condition {condition}")
    result = subprocess.run(cmd, env=env, check=False)
    return result.returncode


def run_all_conditions(
    cuda_device: str = TRAINING_CONFIG["cuda_device"],
    force: bool = False,
) -> dict:
    """Run all 4 conditions sequentially. Skips if logs sufficient (unless force=True).
    Returns {condition: returncode}."""
    sufficient, counts = check_logs_sufficient()
    if sufficient and not force:
        print(f"All condition logs already have >= {MIN_ROWS} rows. Skipping training.")
        print(f"  Counts: {counts}")
        return {c: 0 for c in CONDITIONS}

    print(f"Training needed. Current row counts: {counts}")
    return_codes = {}
    for condition in CONDITIONS:
        if counts.get(condition, 0) >= MIN_ROWS and not force:
            print(f"  Skipping {condition} (already has {counts[condition]} rows)")
            return_codes[condition] = 0
            continue
        print(f"\n[Training] Condition: {condition}")
        rc = run_full_training(condition, cuda_device=cuda_device)
        return_codes[condition] = rc
        if rc != 0:
            raise RuntimeError(
                f"Training failed for condition '{condition}' with return code {rc}. "
                f"Aborting remaining conditions."
            )
        print(f"  {condition} completed (exit={rc})")
    return return_codes


def validate_training_outputs(
    log_dir: str = LOG_DIR,
    expected_rows: int = MIN_ROWS,
) -> tuple:
    """Post-training check: verify all CSVs have >= expected_rows rows.
    Returns (all_valid, {condition: actual_row_count})."""
    counts = {}
    for condition in CONDITIONS:
        csv_path = os.path.join(log_dir, f"reward_density_{condition}.csv")
        if not os.path.exists(csv_path):
            counts[condition] = 0
        else:
            with open(csv_path) as f:
                counts[condition] = sum(1 for _ in f) - 1
    all_valid = all(v >= expected_rows for v in counts.values())
    if not all_valid:
        failed = {c: n for c, n in counts.items() if n < expected_rows}
        raise RuntimeError(
            f"Post-training validation failed. Insufficient rows: {failed}. "
            f"Expected >= {expected_rows} per condition."
        )
    return all_valid, counts


if __name__ == "__main__":
    print("=" * 60)
    print("H-M1: Training Wrapper")
    print("=" * 60)

    sufficient, counts = check_logs_sufficient()
    print(f"\nLog sufficiency check: {sufficient}")
    print(f"Row counts: {counts}")

    if not sufficient:
        print("\nStarting full training for insufficient conditions...")
        try:
            return_codes = run_all_conditions()
            print(f"\nTraining completed: {return_codes}")
            valid, final_counts = validate_training_outputs()
            print(f"Post-training validation: {valid}")
            print(f"Final row counts: {final_counts}")
        except RuntimeError as e:
            print(f"\nERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\nLogs sufficient — proceeding to analysis.")

    print("\nRunning reward density analysis...")
    analysis_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "analysis", "analyze_reward_density.py"
    )
    result = subprocess.run([sys.executable, analysis_script], check=False)
    sys.exit(result.returncode)
