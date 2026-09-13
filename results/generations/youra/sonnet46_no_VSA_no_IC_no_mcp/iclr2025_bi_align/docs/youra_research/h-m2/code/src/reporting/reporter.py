import json
from pathlib import Path
import numpy as np
import pandas as pd


def _json_safe(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, bool):
        return obj
    return obj


def print_report(results: dict) -> None:
    gate = "PASS" if results["gate_pass"] else "FAIL"
    print("=" * 60)
    print(f"H-M2 CALIBRATION-ALIGNMENT DIVERGENCE GAP — {gate}")
    print("=" * 60)
    print(f"  Gate reason:          {results['gate_reason']}")
    print(f"  n_positive_high_kl:   {results['n_positive_high_kl']} (threshold >= 3)")
    print(f"  rho_gap_kl:           {results['rho_gap_kl']:.4f} (threshold > 0)")
    print(f"  p_rho_gap:            {results['p_rho_gap']:.4f}")
    print(f"  max_gap:              {results['max_gap']:.4f}")
    print(f"  mean_gap_high_kl:     {results['mean_gap_high_kl']:.4f}")
    print(f"  prop_positive:        {results['prop_positive']:.4f} (threshold > 0.5)")
    print(f"  rm_min:               {results['rm_min']:.4f}")
    print(f"  rm_max:               {results['rm_max']:.4f}")
    print(f"  median_kl:            {results['median_kl']:.4f}")
    print(f"  dataset_n:            {results['dataset_n']}")
    print("=" * 60)


def save_results(results: dict, out_path: str) -> None:
    scalar_keys = [
        "n_positive_high_kl", "rho_gap_kl", "p_rho_gap", "max_gap",
        "mean_gap_high_kl", "prop_positive", "gate_pass", "gate_reason",
        "rm_min", "rm_max", "median_kl", "dataset_n",
    ]
    out = {k: _json_safe(results[k]) for k in scalar_keys if k in results}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  Results saved: {out_path}")


def save_gap_curve(df: pd.DataFrame, rm_norm: np.ndarray,
                   gap: np.ndarray, out_path: str) -> None:
    out_df = pd.DataFrame({
        "kl_budget":      df["kl_budget"].values,
        "rm_score":       df["rm_score"].values,
        "rm_norm":        rm_norm,
        "gold_preference": df["gold_preference"].values,
        "gap":            gap,
    })
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"  Gap CSV saved: {out_path}")
