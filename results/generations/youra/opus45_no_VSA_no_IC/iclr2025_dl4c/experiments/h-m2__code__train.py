"""Orchestrator for H-M2 ensemble experiment."""
import os
import json
import numpy as np
import pandas as pd

from config import CFG
from data import load_he1_verdicts, verify_coverage, load_he1_accuracies
from ensemble import majority_vote, weighted_majority, unanimous_flag, two_tier_subset, random_ensemble
from baselines import per_judge_accuracy, per_judge_fpr_fnr, best_single_judge, random_avg_baseline
from stats import compare_ensemble_vs_best, pivot_analysis


def main():
    print("=" * 60)
    print("H-M2: Scale-Ensemble Outperformance Experiment")
    print("=" * 60)

    # Load data
    print("\n[1] Loading H-E1 verdict data...")
    inputs = load_he1_verdicts()
    print(f"    Loaded {len(inputs)} problem instances")
    verify_coverage(inputs)
    print(f"    Coverage verified: all 3 judges present")

    # Per-judge baselines
    print("\n[2] Computing per-judge baselines...")
    accs = per_judge_accuracy(inputs)
    fpr_fnr = per_judge_fpr_fnr(inputs)
    for j, a in accs.items():
        print(f"    {j}: acc={a:.4f}, FPR={fpr_fnr[j]['fpr']:.4f}, FNR={fpr_fnr[j]['fnr']:.4f}")

    best_judge_name, best_acc = best_single_judge(accs)
    print(f"\n    Best single judge: {best_judge_name} ({best_acc:.4f})")

    # Prepare arrays
    y_true = np.array([inp.ground_truth for inp in inputs])
    y_best = np.array([inp.verdicts[best_judge_name] for inp in inputs])

    rng = np.random.default_rng(CFG.seed)

    # Ensemble methods
    methods = {
        "AB1_majority": lambda v: majority_vote(v),
        "AB2_weighted": lambda v: weighted_majority(v, accs),
        "AB3_2tier": lambda v: two_tier_subset(v, CFG.ab3_exclude_judge),
        "AB4_random": lambda v: random_ensemble(v, rng),
    }

    results = {}
    print("\n[3] Evaluating ensemble methods...")

    for name, fn in methods.items():
        y_ens = np.array([fn(inp.verdicts) for inp in inputs])

        comparison = compare_ensemble_vs_best(
            y_true, y_ens, y_best,
            p_threshold=CFG.p_value_threshold,
            improvement_target=CFG.improvement_target
        )

        pivot = pivot_analysis(inputs, fn, unanimous_flag)
        comparison["pivot"] = pivot
        comparison["method"] = name

        results[name] = comparison

        print(f"\n    {name}:")
        print(f"      Accuracy: {comparison['acc_ensemble']:.4f} (best single: {comparison['acc_best_single']:.4f})")
        print(f"      Improvement: {comparison['improvement_pct']:.2f}%")
        print(f"      McNemar p-value: {comparison['p_value']:.4e}")
        print(f"      Hypothesis supported: {comparison['hypothesis_supported']}")
        uacc = f"{pivot['unanimous_acc']:.4f}" if pivot['unanimous_acc'] else "N/A"
        sacc = f"{pivot['split_acc']:.4f}" if pivot['split_acc'] else "N/A"
        print(f"      Unanimous subset: {pivot['unanimous_n']} samples, acc={uacc}")
        print(f"      Split subset: {pivot['split_n']} samples, acc={sacc}")

    # Save outputs
    os.makedirs("outputs/figures", exist_ok=True)

    # Comparison CSV
    rows = []
    for name, r in results.items():
        rows.append({
            "method": name,
            "acc_ensemble": r["acc_ensemble"],
            "acc_best_single": r["acc_best_single"],
            "improvement_pct": r["improvement_pct"],
            "p_value": r["p_value"],
            "hypothesis_supported": r["hypothesis_supported"],
            "unanimous_acc": r["pivot"]["unanimous_acc"],
            "split_acc": r["pivot"]["split_acc"]
        })
    df = pd.DataFrame(rows)
    df.to_csv(CFG.comparison_csv_path, index=False)
    print(f"\n[4] Saved comparison to {CFG.comparison_csv_path}")

    # JSON results
    with open(CFG.mcnemar_json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"    Saved detailed results to {CFG.mcnemar_json_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    best_method = max(results.items(), key=lambda x: x[1]["improvement_pct"])
    print(f"Best ensemble method: {best_method[0]}")
    print(f"  Improvement over best single: {best_method[1]['improvement_pct']:.2f}%")
    print(f"  Statistically significant: {best_method[1]['p_value'] < CFG.p_value_threshold}")

    # Gate verdict
    ab1 = results["AB1_majority"]
    gate_passed = ab1["hypothesis_supported"]

    print(f"\n[GATE] H-M2 SHOULD_WORK gate (AB1 majority vote):")
    print(f"  Target: ≥3% improvement with p<0.05")
    print(f"  Achieved: {ab1['improvement_pct']:.2f}% improvement, p={ab1['p_value']:.4e}")
    print(f"  Verdict: {'PASS' if gate_passed else 'FAIL'}")

    return results


if __name__ == "__main__":
    main()
