"""
H-M2: Reward Entropy & Predictive Correlation Analysis
Orchestrates the full analysis pipeline on h-e1 log data.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Resolve absolute paths
CODE_DIR = Path(__file__).parent.resolve()
H_M2_DIR = CODE_DIR.parent.resolve()
H_E1_DIR = H_M2_DIR.parent / "h-e1"

H_E1_LOG_DIR = str(H_E1_DIR / "code" / "h-e1" / "logs")
H_E1_CHECKPOINTS_DIR = str(H_E1_DIR / "checkpoints")
H_E1_RESULTS_DIR = str(H_E1_DIR / "code" / "h-e1" / "results")
RESULTS_DIR = str(H_M2_DIR / "results")
FIGURES_DIR = str(H_M2_DIR / "figures")

sys.path.insert(0, str(CODE_DIR))

from analysis.load_data import load_reward_density, load_all_conditions, CONDITIONS
from analysis.compute_entropy import add_entropy_column, compare_entropy_direction, compute_early_mean_entropy
from analysis.compute_gains import build_pooled_observations
from analysis.pearson_correlation import (
    pearson_with_ci, per_condition_correlations, wilcoxon_entropy_test,
    evaluate_gate, save_results
)
from visualization.generate_figures import generate_all_figures


def extract_reward_density_from_trainer_state(checkpoints_dir: str, condition: str) -> pd.DataFrame:
    """Extract per-checkpoint reward density from trainer_state.json log history.

    Reads the last logged entry at each checkpoint step and computes reward_density
    as 1 - frac_reward_zero_std (fraction of non-degenerate batches). Falls back to
    using reward mean as proxy if frac_reward_zero_std is unavailable.
    Returns DataFrame(step, reward_density) sorted by step.
    """
    cond_dir = Path(checkpoints_dir) / condition
    if not cond_dir.exists():
        raise FileNotFoundError(
            f"No checkpoint directory for condition '{condition}' at {cond_dir}"
        )

    ckpt_dirs = sorted(
        [d for d in cond_dir.iterdir() if d.name.startswith("checkpoint-")],
        key=lambda x: int(x.name.split("-")[1])
    )
    if not ckpt_dirs:
        raise FileNotFoundError(f"No checkpoint subdirectories found in {cond_dir}")

    rows = []
    for ckpt in ckpt_dirs:
        state_file = ckpt / "trainer_state.json"
        if not state_file.exists():
            continue
        with open(state_file) as f:
            state = json.load(f)
        log = state.get("log_history", [])
        if not log:
            continue
        # Use last entry at this checkpoint step
        last = log[-1]
        step = last["step"]
        frac_zero = last.get("frac_reward_zero_std")
        if frac_zero is not None:
            # reward_density = fraction of batches with non-zero reward std
            density = 1.0 - float(frac_zero)
        else:
            # Fallback: use mean reward as proxy (binary rewards: mean ≈ fraction positive)
            density = float(last.get("reward", 0.0))
        rows.append({"step": step, "reward_density": density})

    if not rows:
        raise RuntimeError(f"No trainer_state log entries found for condition '{condition}'")

    df = pd.DataFrame(rows).sort_values("step").reset_index(drop=True)
    print(f"  Extracted {len(df)} checkpoint rows from trainer_state for '{condition}'")
    return df


def build_reward_density_csvs(checkpoints_dir: str, log_dir: str) -> list[str]:
    """Extract real reward density from trainer_state.json and write to CSV files.

    Only builds CSVs for conditions that have checkpoint directories.
    Returns list of conditions successfully extracted.
    """
    available_conditions = []
    ckpt_base = Path(checkpoints_dir)
    if not ckpt_base.exists():
        raise FileNotFoundError(f"Checkpoints directory not found: {checkpoints_dir}")

    for cond in CONDITIONS:
        cond_dir = ckpt_base / cond
        if not cond_dir.exists():
            print(f"  WARNING: No checkpoints for condition '{cond}' — skipping")
            continue
        try:
            df = extract_reward_density_from_trainer_state(checkpoints_dir, cond)
            out_path = os.path.join(log_dir, f"reward_density_{cond}.csv")
            df.to_csv(out_path, index=False)
            print(f"  Written real reward density CSV: {out_path}")
            available_conditions.append(cond)
        except Exception as e:
            print(f"  ERROR extracting reward density for '{cond}': {e}")

    return available_conditions


def load_real_data(available_conditions: list[str]) -> dict:
    """Load real data for available conditions. Raises if pass@1 data is missing."""
    data = {}
    missing_pass1 = []

    for cond in available_conditions:
        density_df = load_reward_density(H_E1_LOG_DIR, cond)

        # Try to load real pass@1 — no synthetic fallback
        try:
            from analysis.load_data import load_pass1_checkpoints
            pass1_df = load_pass1_checkpoints(H_E1_LOG_DIR, cond, H_E1_RESULTS_DIR)
        except Exception as e:
            missing_pass1.append(f"{cond}: {e}")
            pass1_df = None

        data[cond] = {"density": density_df, "pass1": pass1_df}

    if missing_pass1:
        raise RuntimeError(
            "REAL pass@1 checkpoint data is required but missing. "
            "H-M2 cannot proceed without EvalPlus checkpoint evaluations.\n"
            "Missing conditions:\n" + "\n".join(f"  - {m}" for m in missing_pass1) + "\n"
            "Run EvalPlus evaluations on all saved checkpoints to generate "
            "h-e1/logs/pass1_checkpoint_{condition}.csv before re-running this analysis."
        )

    return data


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(H_E1_LOG_DIR, exist_ok=True)

    print("=" * 60)
    print("H-M2: Reward Entropy & Predictive Correlation Analysis")
    print("=" * 60)

    # Step 0: Extract real reward density from trainer_state.json checkpoints
    print("\n[0/7] Extracting real reward density from trainer_state.json logs...")
    available_conditions = build_reward_density_csvs(H_E1_CHECKPOINTS_DIR, H_E1_LOG_DIR)
    if not available_conditions:
        raise RuntimeError(
            f"No checkpoint data found for any condition in {H_E1_CHECKPOINTS_DIR}. "
            "Cannot proceed with H-M2 analysis."
        )
    print(f"  Available conditions: {available_conditions}")
    if set(available_conditions) != set(CONDITIONS):
        missing = set(CONDITIONS) - set(available_conditions)
        raise RuntimeError(
            f"Missing checkpoint data for conditions: {missing}. "
            "All 4 conditions are required for H-M2 analysis. "
            "Re-run H-E1 training for all conditions before running H-M2."
        )

    # Step 1: Load real data (no synthetic fallbacks)
    print("\n[1/7] Loading real data...")
    data = load_real_data(available_conditions)
    for cond in available_conditions:
        d = data[cond]
        print(f"  {cond}: density={len(d['density'])} rows, pass1={len(d['pass1'])} rows")

    # Step 2: Add entropy column
    print("\n[2/7] Computing entropy...")
    for cond in available_conditions:
        data[cond]["density"] = add_entropy_column(data[cond]["density"])

    # Step 3: Entropy direction comparison
    print("\n[3/7] Comparing entropy direction (curriculum vs uniform)...")
    entropy_comparison = compare_entropy_direction(data)
    print(f"  mean_entropy_curriculum_early: {entropy_comparison['mean_entropy_curriculum_early']:.4f}")
    print(f"  mean_entropy_uniform_early:    {entropy_comparison['mean_entropy_uniform_early']:.4f}")
    print(f"  delta_entropy:                 {entropy_comparison['delta_entropy']:.4f}")

    # Step 4: Build pooled observations
    print("\n[4/7] Building pooled observations...")
    all_densities, all_gains, condition_labels = build_pooled_observations(data)
    print(f"  Pooled observations: {len(all_densities)} (expected 36)")

    # Step 5: Pearson correlation
    print("\n[5/7] Computing Pearson correlation...")
    pooled_pearson = pearson_with_ci(all_densities, all_gains)
    print(f"  r={pooled_pearson['r']:.4f}, p_onetailed={pooled_pearson['p_onetailed']:.4f}")
    print(f"  95% CI: [{pooled_pearson['ci_low']:.4f}, {pooled_pearson['ci_high']:.4f}]")
    print(f"  n={pooled_pearson['n']}")

    # Step 6: Per-condition correlations
    per_cond_r = per_condition_correlations(data)
    for cond, res in per_cond_r.items():
        print(f"  {cond}: r={res['r']:.4f}, p={res['p_onetailed']:.4f}")

    # Step 7: Wilcoxon entropy test
    print("\n[6/7] Wilcoxon entropy test...")
    c_df = data["curriculum"]["density"]
    u_df = data["uniform"]["density"]
    early_c = c_df[c_df["step"] <= 2500]["entropy"].values
    early_u = u_df[u_df["step"] <= 2500]["entropy"].values
    n_min = min(len(early_c), len(early_u))
    if n_min >= 2:
        wilcoxon_result = wilcoxon_entropy_test(early_c[:n_min], early_u[:n_min])
    else:
        wilcoxon_result = {
            "statistic": float("nan"),
            "p_value": float("nan"),
            "direction_correct": entropy_comparison["delta_entropy"] > 0
        }
    print(f"  direction_correct={wilcoxon_result['direction_correct']}, p={wilcoxon_result['p_value']}")

    # Save results
    results_path = os.path.join(RESULTS_DIR, "results_summary.json")
    save_results(pooled_pearson, entropy_comparison, per_cond_r, wilcoxon_result, results_path)

    # Save CSVs
    entropy_rows = []
    for cond in available_conditions:
        df = data[cond]["density"].copy()
        df["condition"] = cond
        entropy_rows.append(df)
    entropy_df = pd.concat(entropy_rows, ignore_index=True)
    entropy_df.to_csv(os.path.join(RESULTS_DIR, "entropy_timeseries.csv"), index=False)

    corr_rows = [{"condition": c, "density": d, "gain": g}
                 for c, d, g in zip(condition_labels, all_densities.tolist(), all_gains.tolist())]
    pd.DataFrame(corr_rows).to_csv(os.path.join(RESULTS_DIR, "correlation_data.csv"), index=False)

    # Generate figures
    print("\n[7/7] Generating figures...")
    generate_all_figures(data, all_densities, all_gains, condition_labels,
                         pooled_pearson["r"], FIGURES_DIR)

    # Gate verdict
    gate_passed = evaluate_gate(pooled_pearson)
    gate_str = "PASSED" if gate_passed else "FAILED"
    print(f"\nGATE: {gate_str} — Pearson r={pooled_pearson['r']:.4f}, p={pooled_pearson['p_onetailed']:.4f}")
    print("=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
