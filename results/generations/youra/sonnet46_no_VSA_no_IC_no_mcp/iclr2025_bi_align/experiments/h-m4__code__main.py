import sys
import json
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.preprocess import load_raw, compute_gap, validate_gap, save_gap
from src.regression import fit_ols_regression
from src.gate import check_gate, compare_with_coste
from src.verify import verify_mechanism_activated
from src.figures import generate_all_figures


def save_results(results: dict, gate: dict, comparison: dict, cfg) -> None:
    cfg.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {**results, "gate_pass": gate["gate_pass"], "gate_type": gate["gate_type"],
               "gate_reason": gate["reason"], "comparison": comparison}
    with open(cfg.RESULTS_JSON, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved: {cfg.RESULTS_JSON}")


def main():
    print("=== H-M4: Gao et al. 2023 Cross-Dataset OLS Replication ===")

    df_raw = load_raw(config.DATA_RAW)
    print(f"Raw data loaded: N={len(df_raw)} rows")

    df_gap = compute_gap(df_raw)
    validate_gap(df_gap)
    save_gap(df_gap, config.DATA_GAP)
    print(f"Gap computed and saved: {config.DATA_GAP}")
    print(df_gap[["kl_budget", "proxy_norm", "gold_norm", "gap"]].to_string(index=False))

    kl = df_gap["kl_budget"].values
    gap = df_gap["gap"].values

    results = fit_ols_regression(kl, gap, n_boot=config.N_BOOT, seed=config.SEED)
    print(f"\nGao OLS regression fitted:")
    print(f"  slope (β)  = {results['slope']:.6f}")
    print(f"  intercept  = {results['intercept']:.6f}")
    print(f"  R²         = {results['r_squared']:.6f}")
    print(f"  p-value    = {results['p_value']:.4e}")
    print(f"  std_err    = {results['std_err']:.6f}")
    print(f"  t_stat     = {results['t_stat']:.4f}")
    print(f"  CI (param) = [{results['ci_parametric'][0]:.4f}, {results['ci_parametric'][1]:.4f}]")
    print(f"  CI (boot)  = [{results['ci_bootstrap'][0]:.4f}, {results['ci_bootstrap'][1]:.4f}]")
    print(f"  N          = {results['n']}")

    gate = check_gate(results, config.GATE_BETA_MIN, config.GATE_P_MAX)
    comparison = compare_with_coste(results["slope"], config.BETA_COSTE)
    print(f"\nCross-dataset comparison:")
    print(f"  β_Gao / β_Coste = {comparison['ratio']:.3f} (within order of magnitude: {comparison['within_order_of_magnitude']})")
    print(f"\nGate (SHOULD_WORK): {'PASS' if gate['gate_pass'] else 'FAIL'} — {gate['reason']}")

    verify_mechanism_activated(results, str(config.DATA_GAP))
    print("Mechanism verification: PASSED (all indicators True)")

    generate_all_figures(df_gap, results, gate, comparison, config.FIGURES_DIR)

    save_results(results, gate, comparison, config)

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Gate result: {'PASS' if gate['gate_pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
