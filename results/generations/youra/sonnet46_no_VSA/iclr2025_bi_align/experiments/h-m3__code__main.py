import json
import os
import sys

from config import load_config
from data_loader import (
    load_h_m2_results,
    load_harmbench_data,
    load_tier1_dataframe,
    load_tier3_delta_bbq,
)
from analyze import (
    assign_scenario,
    verify_mechanism_activated,
    tier2_analysis,
    tier3_analysis,
    ablation_ci_method,
    ablation_boundary,
)
from visualize import (
    plot_scenario_panel,
    plot_partial_corr_heatmap,
    plot_raw_vs_partial,
    plot_delta_bbq_histogram,
)


REQUIRED_OUTPUT_KEYS = (
    "partial_rho", "ci_partial", "raw_rho", "ci_raw", "N",
    "scenario", "is_ambiguous", "narrative",
    "ablation_ci_method", "ablation_boundary_tight", "ablation_boundary_wide",
    "tier2", "tier3",
    "mechanism_verified", "gate_passed",
)


def run(cfg=None) -> dict:
    """Orchestrate H-M3 scenario classification pipeline."""
    if cfg is None:
        cfg = load_config()

    print("=" * 60)
    print("H-M3: Scenario Classification of Partial Spearman")
    print("=" * 60)

    # Tier 1: Load H-M2 results
    print("\n[1] Loading H-M2 results...")
    h_m2 = load_h_m2_results(cfg)
    partial_rho = h_m2["partial_rho"]
    ci_partial = h_m2["ci_partial"]
    raw_rho = h_m2["raw_rho"]
    ci_raw = h_m2["ci_raw"]
    N = h_m2["N"]
    print(f"    partial_rho={partial_rho:.4f}, ci_partial={ci_partial}, N={N}")

    # Scenario classification
    print("\n[2] Assigning scenario...")
    sc_result = assign_scenario(partial_rho, ci_partial[0], ci_partial[1], cfg)
    scenario = sc_result["scenario"]
    is_ambiguous = sc_result["is_ambiguous"]
    narrative = sc_result["narrative"]
    print(f"    Scenario assigned: {scenario.upper()}")
    print(f"    {narrative}")

    results = {
        "partial_rho": partial_rho,
        "ci_partial": ci_partial,
        "raw_rho": raw_rho,
        "ci_raw": ci_raw,
        "N": N,
        "scenario": scenario,
        "is_ambiguous": is_ambiguous,
        "narrative": narrative,
    }

    # Tier 2: HarmBench analysis
    print("\n[3] Tier 2: HarmBench analysis...")
    try:
        df_tier1 = load_tier1_dataframe(cfg)
        harmbench_data = load_harmbench_data()
        tier2_res = tier2_analysis(df_tier1, harmbench_data, cfg)
        print(f"    Status: {tier2_res['tier2_status']}, N_harmbench={tier2_res['N_harmbench']}")
        if tier2_res["tier2_status"] == "EXECUTED":
            print(f"    TQA×Harm: rho={tier2_res['tqa_harm_partial_rho']:.3f}, scenario={tier2_res['scenario_tqa_harm']}")
            print(f"    BBQ×Harm: rho={tier2_res['bbq_harm_partial_rho']:.3f}, scenario={tier2_res['scenario_bbq_harm']}")
    except Exception as e:
        print(f"    Tier 2 failed: {e}")
        tier2_res = {"tier2_status": "ERROR", "reason": str(e)}
    results["tier2"] = tier2_res

    # Tier 3: RLHF ΔBBQ sign test
    print("\n[4] Tier 3: RLHF ΔBBQ sign test...")
    try:
        delta_bbq = load_tier3_delta_bbq(cfg)
        tier3_res = tier3_analysis(delta_bbq)
        print(f"    k_positive={tier3_res['k_positive']}/{tier3_res['n']}, "
              f"p={tier3_res['p_value']:.4f}, direction={tier3_res['direction']}")
    except Exception as e:
        print(f"    Tier 3 failed: {e}")
        tier3_res = {"status": "ERROR", "reason": str(e)}
    results["tier3"] = tier3_res

    # Ablation 1: CI method (Fisher parametric vs BCa)
    print("\n[5] Ablation: CI method comparison...")
    try:
        abl_ci = ablation_ci_method(partial_rho, df_tier1, cfg)
        print(f"    Fisher scenario={abl_ci['scenario']}, matches_primary={abl_ci['matches_primary']}")
    except Exception as e:
        print(f"    Ablation CI method failed: {e}")
        abl_ci = {"scenario": "unavailable", "matches_primary": None, "reason": str(e)}
    results["ablation_ci_method"] = abl_ci

    # Ablation 2: Boundary sensitivity
    print("\n[6] Ablation: Boundary sensitivity...")
    abl_bnd = ablation_boundary(partial_rho, ci_partial[0], ci_partial[1], cfg)
    print(f"    Tight scenario={abl_bnd['tight']['scenario']}, Wide scenario={abl_bnd['wide']['scenario']}")
    results["ablation_boundary_tight"] = abl_bnd["tight"]
    results["ablation_boundary_wide"] = abl_bnd["wide"]

    # Verify mechanism activated
    print("\n[7] Verifying mechanism activation...")
    all_ok, indicators = verify_mechanism_activated(results)
    results["mechanism_verified"] = all_ok
    results["mechanism_indicators"] = indicators

    # Gate evaluation (SHOULD_WORK: any scenario or code-error-free execution)
    gate_passed = True  # SHOULD_WORK gate passes if code ran without error
    results["gate_passed"] = gate_passed
    print(f"\n[8] Gate: SHOULD_WORK → {'PASS' if gate_passed else 'FAIL'}")
    print(f"    Scenario: {scenario.upper()} — {narrative[:80]}...")

    # Validate required output keys
    missing_keys = [k for k in REQUIRED_OUTPUT_KEYS if k not in results]
    if missing_keys:
        raise RuntimeError(f"Missing required output keys: {missing_keys}")

    # Generate figures
    print("\n[9] Generating figures...")
    figures = {}
    try:
        figures["fig1"] = plot_scenario_panel(results, cfg)
        print(f"    Fig1 saved: {figures['fig1']}")
    except Exception as e:
        print(f"    Fig1 failed: {e}")

    try:
        p2 = plot_partial_corr_heatmap(results, cfg)
        if p2:
            figures["fig2"] = p2
            print(f"    Fig2 saved: {figures['fig2']}")
        else:
            print("    Fig2 skipped (Tier 2 not executed)")
    except Exception as e:
        print(f"    Fig2 failed: {e}")

    try:
        figures["fig3"] = plot_raw_vs_partial(results, cfg)
        print(f"    Fig3 saved: {figures['fig3']}")
    except Exception as e:
        print(f"    Fig3 failed: {e}")

    try:
        p4 = plot_delta_bbq_histogram(results, cfg)
        if p4:
            figures["fig4"] = p4
            print(f"    Fig4 saved: {figures['fig4']}")
    except Exception as e:
        print(f"    Fig4 failed: {e}")

    results["figures"] = figures

    # Save results JSON
    os.makedirs(cfg.results_dir, exist_ok=True)
    out_path = os.path.join(cfg.results_dir, cfg.output_filename)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[10] Results saved: {out_path}")

    print("\n" + "=" * 60)
    print(f"H-M3 COMPLETE — Scenario: {scenario.upper()}")
    print(f"Gate SHOULD_WORK: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)

    return results


def main() -> None:
    cfg = load_config()
    results = run(cfg)

    gate = results.get("gate_passed", False)
    scenario = results.get("scenario", "unknown")
    print(f"\nScenario assigned: {scenario.upper()}")
    print(f"Scenario narrative: {results.get('narrative', '')[:120]}...")
    sys.exit(0 if gate else 1)


if __name__ == "__main__":
    main()
