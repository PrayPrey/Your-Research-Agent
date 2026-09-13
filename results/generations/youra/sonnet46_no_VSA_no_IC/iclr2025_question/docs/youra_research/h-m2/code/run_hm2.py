"""H-M2 main experiment: min vs. mean log-prob aggregation, Spearman ρ analysis.

Loads pre-computed scores from H-E1 cache (min_scores, mean_scores, sum_scores, labels)
for LLaMA-2-7B and Mistral-7B-v0.1 on TriviaQA and TruthfulQA.
"""
import os
import sys
import json
import numpy as np

# Ensure config is importable
_CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _CODE)

import config as cfg
from aggregation import compute_all_scores
from analysis import compute_spearman_with_ci, compute_auroc, compute_rho_differential, gate_check
from figures import save_all_figures


# ── Cache mapping: (model_key, dataset_name) → H-E1 npz file ──────────────
_H_E1_CACHE_MAP = {
    ("llama2",  "trivia_qa"):   os.path.join(cfg.H_E1_RESULTS_DIR, "scores_llama2_trivia_qa.npz"),
    ("llama2",  "truthful_qa"): os.path.join(cfg.H_E1_RESULTS_DIR, "scores_llama2_truthful_qa.npz"),
    ("mistral", "trivia_qa"):   os.path.join(cfg.H_E1_RESULTS_DIR, "scores_mistral_trivia_qa.npz"),
    ("mistral", "truthful_qa"): os.path.join(cfg.H_E1_RESULTS_DIR, "scores_mistral_truthful_qa.npz"),
}


def load_scores_from_cache(model_key: str, dataset_name: str):
    """Load pre-computed scores from H-E1 cache. Returns (scores_dict, labels) or None."""
    path = _H_E1_CACHE_MAP.get((model_key, dataset_name))
    if path and os.path.exists(path):
        data = np.load(path)
        scores = {
            "min":     data["min_scores"],
            "mean":    data["mean_scores"],
            "raw_sum": data["sum_scores"],
        }
        labels = data["labels"]
        # Sanity: min_score <= mean_score <= 0 for log-probs
        # H-E1 stores negated values as positive → scores are POSITIVE (negated log-probs)
        # Check sign convention
        if scores["min"].mean() > 0:
            # H-E1 used negated (positive) scores; H-M2 uses raw negative log-probs
            # Negate back so all values ≤ 0 (standard log-prob convention)
            scores = {k: -v for k, v in scores.items()}
            print(f"  [cache] negated H-E1 scores (positive→negative log-prob convention)")
        else:
            print(f"  [cache] scores already in negative log-prob convention")
        n = len(labels)
        print(f"  [cache] loaded {n} samples ({labels.sum()} correct, {(labels==0).sum()} hallucinated)")
        return scores, labels
    return None, None


def analyze_pair(model_key: str, dataset_name: str) -> dict:
    """Full pipeline for one (model, dataset) pair."""
    print(f"\n[H-M2] Processing: {model_key} × {dataset_name}")

    scores, labels = load_scores_from_cache(model_key, dataset_name)

    if scores is None:
        print(f"  [SKIP] No cache found for ({model_key}, {dataset_name})")
        return None

    N = len(labels)
    print(f"  Samples: {N} | positive (correct): {labels.sum()} | negative: {(labels==0).sum()}")

    # Sanity check: min ≤ mean ≤ 0
    bad = np.sum(scores["min"] > scores["mean"])
    if bad > 0:
        pct = 100 * bad / N
        print(f"  WARNING: {bad}/{N} ({pct:.1f}%) samples violate min<=mean — check sign convention")

    result = {}

    for method in cfg.AGGREGATION_METHODS:
        s = scores[method]
        rho, pval, ci = compute_spearman_with_ci(s, labels, n_resamples=cfg.N_RESAMPLES_BOOTSTRAP)
        auroc = compute_auroc(s, labels)
        result[f"rho_{method}"]      = rho
        result[f"pval_{method}"]     = pval
        result[f"rho_ci_{method}"]   = [ci.low, ci.high]
        result[f"auroc_{method}"]    = auroc
        print(f"  [{method}] ρ={rho:.4f} (p={pval:.4f}), AUROC={auroc:.4f}, 95%CI=[{ci.low:.4f},{ci.high:.4f}]")

    # Log activation indicator per experiment brief
    n_show = min(10, N)
    for i in range(n_show):
        print(f"  [H-M2] min={scores['min'][i]:.4f}, mean={scores['mean'][i]:.4f}, "
              f"sum={scores['raw_sum'][i]:.4f} for sample {i}")

    # rho(min) - rho(mean) differential with CI
    diff_result = compute_rho_differential(
        scores["min"], scores["mean"], labels,
        n_resamples=cfg.N_RESAMPLES_BOOTSTRAP,
    )
    result["rho_differential"] = diff_result
    print(f"  [diff] ρ(min)-ρ(mean) = {diff_result['diff']:.4f} "
          f"[{diff_result['ci_low']:.4f}, {diff_result['ci_high']:.4f}]")

    # Save scores
    out_path = os.path.join(cfg.RESULTS_DIR, f"scores_{model_key}_{dataset_name}.npz")
    np.savez(out_path,
             min_scores=scores["min"], mean_scores=scores["mean"],
             sum_scores=scores["raw_sum"], labels=labels)
    print(f"  [saved] {out_path}")

    return result


def main():
    print("=" * 65)
    print("H-M2: Min vs. Mean Log-Prob Aggregation Sensitivity")
    print("=" * 65)

    all_results = {}
    pairs = [
        ("llama2",  "trivia_qa"),
        ("llama2",  "truthful_qa"),
        ("mistral", "trivia_qa"),
        ("mistral", "truthful_qa"),
    ]

    for model_key, dataset_name in pairs:
        res = analyze_pair(model_key, dataset_name)
        if res is not None:
            if model_key not in all_results:
                all_results[model_key] = {}
            all_results[model_key][dataset_name] = res

    # Gate evaluation
    print("\n" + "=" * 65)
    print("GATE EVALUATION (SHOULD_WORK)")
    print("=" * 65)
    gate_result = gate_check(all_results)
    print(f"  Gate:  {gate_result['gate']}")
    print(f"  P1 (min>mean on TriviaQA/NQ for ≥1 model): {gate_result['p1_met']}")
    print(f"  P2 (mean>min on TruthfulQA for ≥1 model):  {gate_result['p2_met']}")

    # Print summary table
    print("\n  Summary:")
    print(f"  {'Model':<14} {'Dataset':<14} {'ρ(min)':>8} {'ρ(mean)':>8} {'diff':>8} {'direction':>12}")
    print("  " + "-" * 66)
    for model in all_results:
        for ds in all_results[model]:
            e   = all_results[model][ds]
            rm  = e.get("rho_min",  float("nan"))
            rn  = e.get("rho_mean", float("nan"))
            df  = e.get("rho_differential", {}).get("diff", float("nan"))
            dir_ok = "✓ min>mean" if rm > rn else "✗ mean>min"
            print(f"  {model:<14} {ds:<14} {rm:>8.4f} {rn:>8.4f} {df:>8.4f} {dir_ok:>12}")

    # Save results_summary.json
    summary = {
        "hypothesis":   "h-m2",
        "gate":         gate_result,
        "results":      all_results,
    }

    # Convert numpy scalars to Python floats for JSON serialization
    def _to_python(obj):
        if isinstance(obj, dict):
            return {k: _to_python(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_to_python(i) for i in obj]
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return obj

    summary = _to_python(summary)

    summary_path = os.path.join(cfg.RESULTS_DIR, "results_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[saved] results_summary.json → {summary_path}")

    # Save results.csv for Phase 5
    csv_path = os.path.join(cfg.OUTPUTS_DIR, "results.csv")
    with open(csv_path, "w") as f:
        f.write("model,dataset,rho_min,rho_mean,rho_raw_sum,auroc_min,auroc_mean,auroc_raw_sum,"
                "rho_diff,rho_diff_ci_low,rho_diff_ci_high,pval_min,pval_mean\n")
        for model in all_results:
            for ds in all_results[model]:
                e = all_results[model][ds]
                diff = e.get("rho_differential", {})
                f.write(
                    f"{model},{ds},"
                    f"{e.get('rho_min','')},"
                    f"{e.get('rho_mean','')},"
                    f"{e.get('rho_raw_sum','')},"
                    f"{e.get('auroc_min','')},"
                    f"{e.get('auroc_mean','')},"
                    f"{e.get('auroc_raw_sum','')},"
                    f"{diff.get('diff','')},"
                    f"{diff.get('ci_low','')},"
                    f"{diff.get('ci_high','')},"
                    f"{e.get('pval_min','')},"
                    f"{e.get('pval_mean','')}\n"
                )
    print(f"[saved] results.csv → {csv_path}")

    # Figures
    print("\n[figures] Generating...")
    try:
        save_all_figures(all_results, cfg.FIGURES_DIR)
    except Exception as ex:
        print(f"[figures] ERROR: {ex}")

    print("\n" + "=" * 65)
    print(f"H-M2 COMPLETE — Gate: {gate_result['gate']}")
    print("=" * 65)

    return gate_result


if __name__ == "__main__":
    main()
