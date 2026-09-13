"""H-M1: Reporting — stdout report, JSON save, divergence CSV save."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def print_report(results: dict) -> None:
    gate = "PASS" if results["gate_pass"] else "FAIL"
    border = "=" * 60
    print(border)
    print(f"  H-M1 VALIDATION REPORT — {gate}")
    print(border)
    print(f"  Dataset:           {results['dataset']} (N={results['n_kl_levels']})")
    print(f"  Spearman rho:      {results['rho_rm_kl']:.4f}  (threshold > 0.8)")
    print(f"  p-value:           {results['p_rho']:.4f}  (threshold < 0.05)")
    print(f"  Monotone PASS:     {results['monotone_pass']}")
    print(f"  Peak KL:           {results['peak_kl']:.2f} nats  (valid: {results['peak_kl_valid']})")
    print(f"  Reversal confirmed:{results['reversal_confirmed']}")
    print(f"  Divergence final:  {results['divergence_final']:.4f}")
    print(f"  Divergence max:    {results['divergence_max']:.4f}")
    print(f"  Baseline RM:       {results['baseline_rm']:.4f}")
    print(f"  Baseline gold:     {results['baseline_gold']:.4f}")
    print(border)
    print(f"  Gate conditions:")
    print(f"    [{'PASS' if results['monotone_pass'] else 'FAIL'}] rho > 0.8: {results['mono_reason']}")
    print(f"    [{'PASS' if results['reversal_confirmed'] else 'FAIL'}] reversal: {results['peak_reason']}")
    print(f"  Divergence: {results['div_reason']}")
    print(border)
    if results["gate_pass"]:
        print("  => H-M1 GATE: PASS. Proceed to H-M2.")
    else:
        print("  => H-M1 GATE: FAIL. EXPLORE: re-digitize figures; if confirmed, request raw data.")
    print(border)


def save_results(results: dict, out_path: str, config_path: str = "config.yaml") -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    serializable = {
        k: (v.tolist() if isinstance(v, np.ndarray) else v)
        for k, v in results.items()
        if k != "divergence_curve"
    }
    serializable["timestamp"] = datetime.now(timezone.utc).isoformat()
    serializable["config_path"] = config_path
    serializable["hypothesis_id"] = "h-m1"

    with open(out, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"Results saved: {out}")


def save_divergence_curve(
    df: pd.DataFrame,
    divergence_curve: np.ndarray,
    out_path: str,
) -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    curve_df = df[["kl_budget", "rm_score", "gold_preference"]].copy()
    curve_df["divergence_gap"] = divergence_curve
    curve_df.to_csv(out, index=False)
    print(f"Divergence curve saved: {out}")
