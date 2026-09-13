"""run_analysis.py — Main entry point for H-M2 experiment (A-10, A-12).

Orchestrates:
    load_all_caches → run_per_dataset_analysis → ablation variants →
    isotropic sanity check → verify_mechanism_activated → evaluate_gate →
    visualize all 5 figures → save_results → log gate result
"""
import os
import sys
import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime

# ─── Add code dir to path ────────────────────────────────────────────────────────
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

from config import (
    HE1_CACHE_DIR, FIGURES_DIR, CACHE_OUT_DIR, RESULTS_PATH,
    HYPOTHESIS_DIR, MODEL_PAIRS, DATASETS,
    SEED, N_QUINTILES, N_BOOTSTRAP, MIN_QUINTILE_N, GATE_THRESHOLDS,
    LOG_CONFIG,
)
from analysis_variance import (
    load_h_e1_cache,
    validate_cache,
    compute_variance_by_quintile,
    test_method_quintile_interaction,
    run_ablation_no_kl,
    run_isotropic_sanity_check,
    verify_mechanism_activated,
)
from visualize import (
    plot_q1_variance_bar,
    plot_quintile_trend,
    plot_kl_scatter,
    plot_benchmark_q1_grouped,
    plot_variance_ratio_heatmap,
)


def setup_logging(hypothesis_dir: str) -> logging.Logger:
    """Configure structured logging to console and log file."""
    log_path = os.path.join(hypothesis_dir, "run.log")
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG.get("level", "INFO")),
        format=LOG_CONFIG.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, mode="w"),
        ],
        force=True,
    )
    return logging.getLogger("h-m2")


def load_all_caches(
    model_pairs: list,
    datasets: list,
    cache_dir: str,
) -> dict:
    """Load all H-E1 cache files for pair2 and pair4 × 3 datasets.

    Returns: {pair_id: {dataset_name: cache_dict}}
    Raises FileNotFoundError if any cache file missing.
    """
    log = logging.getLogger("h-m2.load")
    caches = {}
    for pair in model_pairs:
        pair_id = pair["pair_id"]
        caches[pair_id] = {}
        for ds in datasets:
            ds_name = ds["name"]
            log.info(f"Loading cache: {pair_id}/{ds_name}")
            cache = load_h_e1_cache(pair_id, ds_name, cache_dir)
            validate_cache(cache, pair_id, ds_name)
            caches[pair_id][ds_name] = cache
            log.info(f"  ✓ {pair_id}/{ds_name}: N={len(cache['margin'])}")
    return caches


def run_per_dataset_analysis(
    caches: dict,
    n_quintiles: int = N_QUINTILES,
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict:
    """Run variance analysis for DPO (pair2) and SFT (pair4) per dataset.

    Returns: {dataset: {"dpo": variance_result, "sft": variance_result, "test": test_result}}
    """
    log = logging.getLogger("h-m2.analysis")
    results = {}
    dpo_pair = "pair2"
    sft_pair = "pair4"

    for ds in DATASETS:
        ds_name = ds["name"]
        log.info(f"\n── Dataset: {ds_name} ──")

        dpo_cache = caches[dpo_pair][ds_name]
        sft_cache = caches[sft_pair][ds_name]

        # Compute variance by quintile for DPO
        log.info(f"  Computing DPO variance by quintile...")
        dpo_result = compute_variance_by_quintile(
            dpo_cache["base_logprobs"],
            dpo_cache["aligned_logprobs"],
            dpo_cache["margin"],
            dpo_cache["kl_div"],
            n_quintiles=n_quintiles,
            kl_control=True,
            min_quintile_n=MIN_QUINTILE_N,
        )

        # Compute variance by quintile for SFT
        log.info(f"  Computing SFT variance by quintile...")
        sft_result = compute_variance_by_quintile(
            sft_cache["base_logprobs"],
            sft_cache["aligned_logprobs"],
            sft_cache["margin"],
            sft_cache["kl_div"],
            n_quintiles=n_quintiles,
            kl_control=True,
            min_quintile_n=MIN_QUINTILE_N,
        )

        # Statistical test: DPO vs SFT Q1 residuals
        log.info(f"  Running Welch's t-test on Q1 residuals...")
        test_result = test_method_quintile_interaction(
            dpo_result["q1_residuals"],
            sft_result["q1_residuals"],
            n_bootstrap=n_bootstrap,
            seed=seed,
        )

        log.info(
            f"  {ds_name}: DPO_q1_var={dpo_result['quintile_variances'][0]:.4f}, "
            f"SFT_q1_var={sft_result['quintile_variances'][0]:.4f}, "
            f"ratio={test_result['q1_variance_ratio']:.3f}, "
            f"p={test_result['p_one_tailed']:.4f}"
        )

        results[ds_name] = {
            "dpo":  dpo_result,
            "sft":  sft_result,
            "test": test_result,
        }

    return results


def evaluate_gate(results: dict) -> dict:
    """Apply cross-benchmark gate: significant (p < 0.05) on >= 2/3 datasets.

    Returns:
        {"gate_pass": bool, "n_significant": int, "per_dataset": dict}
    NOTE: p >= 0.05 is NOT a code error — SHOULD_WORK gate, document null result.
    """
    log = logging.getLogger("h-m2.gate")
    pvalue_max = GATE_THRESHOLDS["pvalue_max"]
    benchmarks_min = GATE_THRESHOLDS["benchmarks_min"]

    per_dataset = {}
    significant_datasets = []

    for ds_name, ds_result in results.items():
        test = ds_result.get("test", {})
        p = test.get("p_one_tailed", 1.0)
        ratio = test.get("q1_variance_ratio", 0.0)
        is_sig = bool(p < pvalue_max)
        per_dataset[ds_name] = {
            "p_one_tailed": p,
            "q1_variance_ratio": ratio,
            "significant": is_sig,
        }
        if is_sig:
            significant_datasets.append(ds_name)

    n_significant = len(significant_datasets)
    gate_pass = n_significant >= benchmarks_min

    log.info(
        f"Gate: {'PASS' if gate_pass else 'FAIL'} ({n_significant}/3 datasets significant)"
    )
    if gate_pass:
        log.info(f"H-M2 PASS: DPO Q1 variance > SFT on {significant_datasets}")
    else:
        log.info(f"H-M2 NULL RESULT: no significant Q1 variance difference ({n_significant}/3)")

    return {
        "gate_pass":          gate_pass,
        "n_significant":      n_significant,
        "significant_datasets": significant_datasets,
        "per_dataset":        per_dataset,
    }


def save_results(results: dict, path: str) -> None:
    """Save results dict to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def _make_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64, float)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64, np.int8, np.int16, int)):
            return int(obj)
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, dict):
            return {k: _make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_make_serializable(v) for v in obj]
        return obj

    serializable = _make_serializable(results)
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
    logging.getLogger("h-m2").info(f"Results saved: {path}")


def main() -> None:
    """H-M2 main experiment entry point."""
    log = setup_logging(HYPOTHESIS_DIR)
    log.info("=" * 60)
    log.info("H-M2: DPO vs SFT Logit Delta Variance in Low-Margin Regions")
    log.info("=" * 60)

    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(CACHE_OUT_DIR, exist_ok=True)

    # Step 1: Load all caches
    log.info("\n[1] Loading H-E1 cache files...")
    caches = load_all_caches(MODEL_PAIRS, DATASETS, HE1_CACHE_DIR)
    log.info(f"  ✓ Loaded {len(MODEL_PAIRS)} pairs × {len(DATASETS)} datasets")

    # Step 2: Run per-dataset analysis
    log.info("\n[2] Running per-dataset variance analysis...")
    results = run_per_dataset_analysis(caches)

    # Step 3: Ablation (no-KL control)
    log.info("\n[3] Running no-KL ablation (comparison only)...")
    ablation_results = {}
    for ds in DATASETS:
        ds_name = ds["name"]
        ablation_results[ds_name] = {
            "dpo_no_kl": run_ablation_no_kl(
                caches["pair2"][ds_name]["base_logprobs"],
                caches["pair2"][ds_name]["aligned_logprobs"],
                caches["pair2"][ds_name]["margin"],
                caches["pair2"][ds_name]["kl_div"],
            ),
            "sft_no_kl": run_ablation_no_kl(
                caches["pair4"][ds_name]["base_logprobs"],
                caches["pair4"][ds_name]["aligned_logprobs"],
                caches["pair4"][ds_name]["margin"],
                caches["pair4"][ds_name]["kl_div"],
            ),
        }

    # Step 4: Isotropic sanity check
    log.info("\n[4] Running isotropic sanity check...")
    sanity = run_isotropic_sanity_check(n=1000, seed=SEED)
    log.info(
        f"  Sanity: is_flat={sanity['is_flat']}, "
        f"max/min_ratio={sanity['max_min_ratio']:.3f}"
    )

    # Step 5: Mechanism verification
    log.info("\n[5] Verifying mechanism activation...")
    mech_pass, indicators = verify_mechanism_activated(results)
    log.info(f"  Mechanism activated: {mech_pass}, indicators: {indicators}")

    # Step 6: Gate evaluation
    log.info("\n[6] Evaluating gate...")
    gate = evaluate_gate(results)

    # Step 7: Visualize all 5 figures
    log.info("\n[7] Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Fig 1: Q1 variance bar
    fig1_data = {
        ds: {
            "dpo_q1_var":   float(results[ds]["dpo"]["quintile_variances"][0]),
            "sft_q1_var":   float(results[ds]["sft"]["quintile_variances"][0]),
            "p_one_tailed": float(results[ds]["test"]["p_one_tailed"]),
        }
        for ds in results
    }
    plot_q1_variance_bar(fig1_data, FIGURES_DIR)
    log.info("  ✓ Fig 1 saved")

    # Fig 2: Quintile trend
    fig2_data = {
        ds: {
            "dpo": results[ds]["dpo"]["quintile_variances"],
            "sft": results[ds]["sft"]["quintile_variances"],
        }
        for ds in results
    }
    plot_quintile_trend(fig2_data, FIGURES_DIR)
    log.info("  ✓ Fig 2 saved")

    # Fig 3: KL scatter (pair2 + pair4)
    fig3_data = {}
    for pair in MODEL_PAIRS:
        pair_id = pair["pair_id"]
        ds_name = list(results.keys())[0]  # use first dataset for scatter
        r = results[ds_name]["dpo" if pair_id == "pair2" else "sft"]
        fig3_data[pair_id] = {
            "kl_div":         r["kl_div"],
            "delta_var":      r["delta_var"],
            "quintile_labels": r["quintile_labels"],
        }
    plot_kl_scatter(fig3_data, FIGURES_DIR)
    log.info("  ✓ Fig 3 saved")

    # Fig 4: Grouped bar with std (use residuals std as proxy)
    fig4_data = {
        ds: {
            "dpo_q1_var": float(results[ds]["dpo"]["quintile_variances"][0]),
            "sft_q1_var": float(results[ds]["sft"]["quintile_variances"][0]),
            "dpo_q1_std": float(np.std(results[ds]["dpo"]["q1_residuals"]) if len(results[ds]["dpo"]["q1_residuals"]) > 0 else 0.0),
            "sft_q1_std": float(np.std(results[ds]["sft"]["q1_residuals"]) if len(results[ds]["sft"]["q1_residuals"]) > 0 else 0.0),
        }
        for ds in results
    }
    plot_benchmark_q1_grouped(fig4_data, FIGURES_DIR)
    log.info("  ✓ Fig 4 saved")

    # Fig 5: Variance ratio heatmap
    fig5_data = {}
    for ds in results:
        dpo_qv = results[ds]["dpo"]["quintile_variances"]
        sft_qv = results[ds]["sft"]["quintile_variances"]
        ratio  = np.where(sft_qv > 0, dpo_qv / sft_qv, 1.0)
        fig5_data[ds] = ratio
    plot_variance_ratio_heatmap(fig5_data, FIGURES_DIR)
    log.info("  ✓ Fig 5 saved")

    # Step 8: Save results
    log.info("\n[8] Saving experiment_results.json...")
    all_results = {
        "hypothesis_id":       "h-m2",
        "run_timestamp":       datetime.now().isoformat(),
        "gate_pass":           gate["gate_pass"],
        "gate_type":           "SHOULD_WORK",
        "n_significant":       gate["n_significant"],
        "significant_datasets": gate["significant_datasets"],
        "gate_details":        gate,
        "per_dataset":         {
            ds: {
                "dpo_quintile_variances": results[ds]["dpo"]["quintile_variances"].tolist(),
                "sft_quintile_variances": results[ds]["sft"]["quintile_variances"].tolist(),
                "dpo_quintile_counts":    results[ds]["dpo"]["quintile_counts"].tolist(),
                "sft_quintile_counts":    results[ds]["sft"]["quintile_counts"].tolist(),
                "dpo_kl_residualized":    results[ds]["dpo"]["kl_residualization_applied"],
                "sft_kl_residualized":    results[ds]["sft"]["kl_residualization_applied"],
                "test":                   results[ds]["test"],
            }
            for ds in results
        },
        "ablation":            {
            ds: {
                "dpo_no_kl_q1_var": float(ablation_results[ds]["dpo_no_kl"]["quintile_variances"][0]),
                "sft_no_kl_q1_var": float(ablation_results[ds]["sft_no_kl"]["quintile_variances"][0]),
            }
            for ds in ablation_results
        },
        "isotropic_sanity":    {
            "quintile_variances": sanity["quintile_variances"].tolist(),
            "is_flat":            sanity["is_flat"],
            "max_min_ratio":      sanity["max_min_ratio"],
        },
        "mechanism_verification": {
            "activated": mech_pass,
            "indicators": indicators,
        },
    }
    save_results(all_results, RESULTS_PATH)

    log.info("\n" + "=" * 60)
    log.info(f"H-M2 COMPLETE: gate={'PASS' if gate['gate_pass'] else 'NULL RESULT'}")
    log.info(f"  Significant datasets: {gate['n_significant']}/3")
    for ds in results:
        t = results[ds]["test"]
        log.info(
            f"  {ds}: ratio={t['q1_variance_ratio']:.3f}, "
            f"p={t['p_one_tailed']:.4f}, d={t['cohens_d']:.3f}"
        )
    log.info("=" * 60)


if __name__ == "__main__":
    main()
