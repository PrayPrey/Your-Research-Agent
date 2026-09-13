import pandas as pd

REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]
MIN_KL_LEVELS = 5
MIN_VARIATION = 0.01


def verify_signal_coexistence(df: pd.DataFrame, dataset_name: str) -> dict:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return {
            "dataset": dataset_name, "passed": False,
            "n_kl_levels": 0, "rm_variation": 0.0, "gold_variation": 0.0,
            "gate_satisfied": False,
            "reason": f"Missing columns: {missing}",
        }

    paired = df[REQUIRED_COLS].dropna()
    n_levels = len(paired)
    gate_satisfied = n_levels >= MIN_KL_LEVELS

    if n_levels == 0:
        return {
            "dataset": dataset_name, "passed": False,
            "n_kl_levels": 0, "rm_variation": 0.0, "gold_variation": 0.0,
            "gate_satisfied": False,
            "reason": "No paired rows after dropna",
        }

    rm_var = float(paired["rm_score"].max() - paired["rm_score"].min())
    gold_var = float(paired["gold_preference"].max() - paired["gold_preference"].min())
    has_variation = (rm_var > MIN_VARIATION) and (gold_var > MIN_VARIATION)

    passed = gate_satisfied and has_variation

    if not gate_satisfied:
        reason = f"Only {n_levels} paired KL levels (need >= {MIN_KL_LEVELS})"
    elif not has_variation:
        reason = (
            f"Signal variation too low: rm={rm_var:.4f}, "
            f"gold={gold_var:.4f} (need > {MIN_VARIATION})"
        )
    else:
        reason = (
            f"PASS: {n_levels} paired KL levels, "
            f"rm_var={rm_var:.4f}, gold_var={gold_var:.4f}"
        )

    return {
        "dataset": dataset_name,
        "passed": passed,
        "n_kl_levels": n_levels,
        "rm_variation": rm_var,
        "gold_variation": gold_var,
        "gate_satisfied": gate_satisfied,
        "reason": reason,
    }
