import os
import json
import warnings
import pandas as pd
from typing import Optional

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]


def load_reward_density(log_dir: str, condition: str) -> pd.DataFrame:
    """Load and aggregate reward density CSV. Returns DataFrame(step, reward_density) with >=10 rows."""
    path = os.path.join(log_dir, f"reward_density_{condition}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Reward density CSV not found: {path}")

    df = pd.read_csv(path)
    assert "step" in df.columns and "reward_density" in df.columns, \
        f"Missing required columns in {path}: {list(df.columns)}"

    df = df.sort_values("step").reset_index(drop=True)

    if len(df) > 50:
        # per-step binary values — aggregate into 500-step windows
        df["window"] = (df["step"] - 1) // 500
        df = df.groupby("window").agg(
            step=("step", "max"),
            reward_density=("reward_density", "mean")
        ).reset_index(drop=True)
        df = df.sort_values("step").reset_index(drop=True)

    if len(df) < 10:
        warnings.warn(f"Only {len(df)} rows after aggregation for {condition} (expected >=10). "
                      f"Using available data.")

    return df[["step", "reward_density"]]


def load_pass1_checkpoints(
    log_dir: str,
    condition: str,
    results_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Load pass@1 checkpoint data. Primary: CSV. Fallback: eval_results JSON.
    Returns DataFrame(step, pass1), sorted by step, >= 5 rows."""
    primary_path = os.path.join(log_dir, f"pass1_checkpoint_{condition}.csv")

    if os.path.exists(primary_path):
        df = pd.read_csv(primary_path)
        assert "step" in df.columns and "pass1" in df.columns, \
            f"Missing columns in {primary_path}"
        df = df.sort_values("step").reset_index(drop=True)
        if len(df) >= 5:
            return df
        warnings.warn(f"Only {len(df)} rows in CSV for {condition}, trying JSON fallback")

    if results_dir is None:
        raise RuntimeError(
            f"No pass1 CSV found at {primary_path} and no results_dir provided for {condition}"
        )

    json_path = os.path.join(results_dir, f"eval_results_{condition}.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"No pass1 CSV and no JSON at {json_path}"
        )

    with open(json_path) as f:
        data = json.load(f)

    rows = []
    if isinstance(data, list):
        rows = [{"step": r["step"], "pass1": r["pass@1"]}
                for r in data if r.get("pass@1") is not None]
    elif isinstance(data, dict):
        for key in ("checkpoints", "results", "checkpoint_results"):
            if key in data and isinstance(data[key], list):
                rows = [{"step": r["step"], "pass1": r["pass@1"]}
                        for r in data[key] if r.get("pass@1") is not None]
                break
        if not rows:
            for k, v in data.items():
                try:
                    step = int(k)
                    p1 = v.get("pass@1") if isinstance(v, dict) else None
                    if p1 is not None:
                        rows.append({"step": step, "pass1": float(p1)})
                except (ValueError, AttributeError):
                    pass

    if len(rows) < 10:
        warnings.warn(f"WARNING: Only {len(rows)} checkpoints available for {condition}")

    if len(rows) < 5:
        raise RuntimeError(
            f"Minimum 5 checkpoints required for {condition}, got {len(rows)}"
        )

    df = pd.DataFrame(rows).sort_values("step").reset_index(drop=True)
    return df


def load_all_conditions(
    log_dir: str,
    results_dir: Optional[str] = None,
) -> dict:
    """Load all 4 conditions. Returns {condition: {"density": df, "pass1": df}}."""
    result = {}
    errors = {}

    for cond in CONDITIONS:
        try:
            density_df = load_reward_density(log_dir, cond)
            pass1_df = load_pass1_checkpoints(log_dir, cond, results_dir)
            result[cond] = {"density": density_df, "pass1": pass1_df}
        except Exception as e:
            errors[cond] = str(e)

    if errors:
        raise RuntimeError(
            f"Failed to load conditions: {errors}"
        )

    return result
