"""H-M4: Data loading — H-M3 Exp B CSV, EvalPlus pass@1*, ContractEval metadata."""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from config import (
    EXP_B_CSV, CONTRACT_EVAL_JSON, PASS_AT_1_FALLBACK,
    MODEL_SIZES, MODEL_FAMILIES, ValidationConfig,
)


def load_exp_b_rates(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load H-M3 Experiment B per-(model, task) contract-satisfaction rates.

    Returns DataFrame with columns:
      model_id, task_id, contract_satisfaction_rate, n_programs, n_failing
    """
    path = csv_path or EXP_B_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"H-M3 Experiment B CSV not found: {path}\n"
            "Ensure H-M3 Phase 4 has been completed and results are at h-m3/results/"
        )
    df = pd.read_csv(path)
    required_cols = {"model_id", "task_id", "contract_satisfaction_rate"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"H-M3 CSV missing columns: {missing}")

    validate_inputs(df)
    print(f"Loaded H-M3 Exp B: {len(df)} rows, {df['model_id'].nunique()} models, {df['task_id'].nunique()} tasks")
    return df


def validate_inputs(df: pd.DataFrame, cfg: Optional[ValidationConfig] = None) -> None:
    """Raise ValueError with clear message if prerequisites are not met."""
    cfg = cfg or ValidationConfig()

    n_models = df["model_id"].nunique()
    if n_models < cfg.min_models:
        raise ValueError(
            f"Only {n_models} model(s) in H-M3 data; need >= {cfg.min_models}. "
            "Cannot run mixed-effects model. Check H-M3 results CSV."
        )

    per_model = df.groupby("model_id")["task_id"].count()
    low_models = per_model[per_model < cfg.min_tasks_per_model]
    if len(low_models) > 0:
        print(f"WARNING: Models with few tasks (< {cfg.min_tasks_per_model}): {dict(low_models)}")

    nan_rate = df["contract_satisfaction_rate"].isna().mean()
    if nan_rate > cfg.max_nan_rate:
        raise ValueError(
            f"NaN rate {nan_rate:.1%} exceeds threshold {cfg.max_nan_rate:.1%} in contract_satisfaction_rate"
        )


def load_pass_at_1(use_evalplus_pkg: bool = False) -> dict:
    """Load EvalPlus pass@1* scores.

    Falls back to hardcoded PASS_AT_1_FALLBACK dict (from published leaderboard).
    Returns {model_id: weighted_avg_pass@1} — average of HumanEval+ and MBPP+.
    """
    if use_evalplus_pkg:
        try:
            import evalplus
            raw = evalplus.get_model_scores()
            result = {}
            for model_id in PASS_AT_1_FALLBACK:
                scores = raw.get(model_id, {})
                if scores:
                    vals = [v for v in scores.values() if isinstance(v, (int, float))]
                    result[model_id] = float(np.mean(vals)) if vals else None
            if all(v is not None for v in result.values()):
                print(f"Loaded pass@1* from evalplus package: {result}")
                return result
        except Exception as e:
            print(f"evalplus package unavailable ({e}), using fallback scores")

    # Use hardcoded fallback
    result = {}
    for model_id, scores in PASS_AT_1_FALLBACK.items():
        result[model_id] = float(np.mean(list(scores.values())))
    print(f"Using fallback pass@1* scores: { {k: f'{v:.3f}' for k, v in result.items()} }")
    return result


def load_task_metadata(json_path: Optional[Path] = None) -> dict:
    """Load ContractEval task metadata.

    Returns {task_id: task_type} where task_type is 'humaneval_plus' or 'mbpp_plus'.
    Falls back to inferring task_type from task_id prefix if JSON not found.
    """
    path = json_path or CONTRACT_EVAL_JSON
    if path.exists():
        try:
            with open(path) as f:
                tasks = json.load(f)
            meta = {}
            for t in tasks:
                tid = t.get("task_id") or t.get("id")
                task_type = t.get("task_type", "")
                if not task_type:
                    task_type = "humaneval_plus" if "HumanEval" in str(tid) else "mbpp_plus"
                meta[str(tid)] = task_type
            print(f"Loaded ContractEval metadata: {len(meta)} tasks")
            return meta
        except Exception as e:
            print(f"WARNING: Could not load ContractEval JSON ({e}), inferring task types from IDs")

    # Fallback: infer from task_id prefix
    print("INFO: Inferring task_type from task_id prefix (HumanEval/* → humaneval_plus, Mbpp/* → mbpp_plus)")
    return {}  # empty dict triggers inference in build_df_long


def build_df_long(
    exp_b_df: pd.DataFrame,
    pass_at_1: dict,
    task_meta: dict,
) -> pd.DataFrame:
    """Merge exp_b_df with pass@1 scores and task metadata.

    Adds columns: pass_at_1, log_size, model_family, task_type
    Validates shape >= 1000 rows (min for meaningful MixedLM).
    """
    df = exp_b_df.copy()
    df = df[df["model_id"].isin(pass_at_1)].copy()

    df["pass_at_1"] = df["model_id"].map(pass_at_1)
    df["log_size"] = df["model_id"].map(MODEL_SIZES).apply(np.log)
    df["model_family"] = df["model_id"].map(MODEL_FAMILIES)

    # Task type from metadata or inferred
    if task_meta:
        df["task_type"] = df["task_id"].map(task_meta).fillna("unknown")
    else:
        df["task_type"] = df["task_id"].apply(
            lambda t: "humaneval_plus" if "HumanEval" in str(t) else "mbpp_plus"
        )

    df = df.dropna(subset=["contract_satisfaction_rate", "pass_at_1", "log_size"])

    if len(df) < 1000:
        print(f"WARNING: df_long has only {len(df)} rows (< 1000). MixedLM may be unreliable.")
    else:
        print(f"Built df_long: {len(df)} rows, {df['model_id'].nunique()} models, {df['task_id'].nunique()} tasks")

    return df
