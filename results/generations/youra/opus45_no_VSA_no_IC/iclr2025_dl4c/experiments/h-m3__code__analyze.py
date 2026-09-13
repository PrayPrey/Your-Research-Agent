#!/usr/bin/env python3
"""h-m3: Unanimous Scale Agreement vs Verdict Reliability Analysis.

Tests whether unanimous agreement across scales (7B, 70B, proprietary)
indicates ≥10% higher verdict reliability compared to split verdicts.
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

CONFIG = {
    "input_data": "../../h-e1/code/outputs/results.csv",
    "output_dir": "outputs/",
    "figures_dir": "../figures/",
    "success_threshold": 0.10,
    "significance_level": 0.05,
    "falsification_threshold": 0.05,
    "n_scales": 3,  # 7B, 70B, proprietary
    "figure_format": "png",
    "dpi": 150,
}


def load_verdicts(path: str) -> pd.DataFrame:
    """Load CSV and validate required columns."""
    df = pd.read_csv(path)
    required = ["task_id", "solution_id", "scale", "verdict", "ground_truth"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df["verdict"] = df["verdict"].astype(bool)
    df["ground_truth"] = df["ground_truth"].astype(bool)
    return df


def classify_agreement(df: pd.DataFrame) -> pd.DataFrame:
    """Group by (task_id, solution_id); determine unanimous vs split."""
    grouped = df.groupby(["task_id", "solution_id"])

    def classify_group(g):
        verdicts = g["verdict"].values
        n_true = verdicts.sum()
        n_false = len(verdicts) - n_true
        unanimous = (n_true == len(verdicts)) or (n_false == len(verdicts))
        majority_verdict = n_true > n_false
        ground_truth = g["ground_truth"].iloc[0]
        return pd.Series({
            "unanimous": unanimous,
            "majority_verdict": majority_verdict,
            "ground_truth": ground_truth,
            "n_agreeing": max(n_true, n_false),
            "n_judges": len(verdicts),
        })

    return grouped.apply(classify_group).reset_index()


def compute_accuracy(classified_df: pd.DataFrame) -> dict:
    """Compute accuracy for unanimous vs split groups."""
    unanimous = classified_df[classified_df["unanimous"]]
    split = classified_df[~classified_df["unanimous"]]

    unanimous_correct = (unanimous["majority_verdict"] == unanimous["ground_truth"]).sum()
    unanimous_total = len(unanimous)
    unanimous_acc = unanimous_correct / unanimous_total if unanimous_total > 0 else 0.0

    split_correct = (split["majority_verdict"] == split["ground_truth"]).sum()
    split_total = len(split)
    split_acc = split_correct / split_total if split_total > 0 else 0.0

    improvement = unanimous_acc - split_acc

    return {
        "unanimous_acc": unanimous_acc,
        "split_acc": split_acc,
        "n_unanimous": unanimous_total,
        "n_split": split_total,
        "unanimous_correct": int(unanimous_correct),
        "split_correct": int(split_correct),
        "improvement": improvement,
    }


def run_ztest(results: dict) -> dict:
    """Two-proportion z-test (pooled): unanimous_acc vs split_acc."""
    n1, n2 = results["n_unanimous"], results["n_split"]
    acc1, acc2 = results["unanimous_acc"], results["split_acc"]

    if n1 < 5 or n2 < 5:
        return {"z_stat": float("nan"), "p_value": 1.0, "significant": False, "inconclusive": True}

    p_pool = (n1 * acc1 + n2 * acc2) / (n1 + n2)
    if p_pool == 0 or p_pool == 1:
        return {"z_stat": float("nan"), "p_value": 1.0, "significant": False, "inconclusive": True}

    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z_stat = (acc1 - acc2) / se
    p_value = 1 - norm.cdf(z_stat)  # one-tailed: H1 = unanimous > split

    return {
        "z_stat": z_stat,
        "p_value": p_value,
        "significant": p_value < CONFIG["significance_level"],
        "inconclusive": False,
    }


def generate_figures(results: dict, classified_df: pd.DataFrame, output_dir: str) -> None:
    """Generate bar chart (accuracy comparison) and pie chart (agreement distribution)."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Bar chart: Accuracy with SE error bars
    fig, ax = plt.subplots(figsize=(6, 5))
    categories = ["Unanimous", "Split"]
    accuracies = [results["unanimous_acc"], results["split_acc"]]
    ns = [results["n_unanimous"], results["n_split"]]
    # SE = sqrt(p*(1-p)/n)
    ses = [np.sqrt(a * (1 - a) / n) if n > 0 else 0 for a, n in zip(accuracies, ns)]

    bars = ax.bar(categories, accuracies, yerr=ses, capsize=5, color=["#4CAF50", "#FF5722"])
    ax.set_ylabel("Accuracy")
    ax.set_title("Verdict Accuracy: Unanimous vs Split Agreement")
    ax.set_ylim(0, 1)
    for bar, acc, n in zip(bars, accuracies, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{acc:.1%}\n(n={n})", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(out / f"bar_chart.{CONFIG['figure_format']}", dpi=CONFIG["dpi"])
    plt.close()

    # Pie chart: Agreement distribution
    fig, ax = plt.subplots(figsize=(5, 5))
    sizes = [results["n_unanimous"], results["n_split"]]
    labels = [f"Unanimous\n({results['n_unanimous']})", f"Split\n({results['n_split']})"]
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#4CAF50", "#FF5722"])
    ax.set_title("Agreement Distribution")
    plt.tight_layout()
    plt.savefig(out / f"pie_chart.{CONFIG['figure_format']}", dpi=CONFIG["dpi"])
    plt.close()

    print(f"Figures saved to {output_dir}")


def evaluate_gate(results: dict, ztest: dict) -> str:
    """Evaluate SHOULD_WORK gate: PASS if improvement ≥10% and p<0.05."""
    if ztest.get("inconclusive"):
        return "INCONCLUSIVE"
    if results["improvement"] >= CONFIG["success_threshold"] and ztest["significant"]:
        return "PASS"
    return "FAIL"


def main():
    parser = argparse.ArgumentParser(description="h-m3 Agreement Reliability Analysis")
    parser.add_argument("--input-data", default=CONFIG["input_data"])
    parser.add_argument("--output-dir", default=CONFIG["output_dir"])
    parser.add_argument("--figures-dir", default=CONFIG["figures_dir"])
    args = parser.parse_args()

    print("Loading verdicts...")
    df = load_verdicts(args.input_data)
    print(f"  Loaded {len(df)} rows, {df['scale'].nunique()} scales")

    print("Classifying agreement...")
    classified = classify_agreement(df)
    print(f"  {len(classified)} problem-solution pairs")

    print("Computing accuracy...")
    results = compute_accuracy(classified)
    print(f"  Unanimous: {results['unanimous_acc']:.2%} (n={results['n_unanimous']})")
    print(f"  Split:     {results['split_acc']:.2%} (n={results['n_split']})")
    print(f"  Improvement: {results['improvement']:.2%}")

    print("Running z-test...")
    ztest = run_ztest(results)
    print(f"  z={ztest['z_stat']:.3f}, p={ztest['p_value']:.4f}, significant={ztest['significant']}")

    print("Evaluating gate...")
    gate = evaluate_gate(results, ztest)
    print(f"  Gate result: {gate}")

    print("Generating figures...")
    generate_figures(results, classified, args.figures_dir)

    # Save results
    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Convert numpy bools to Python bools for JSON
    ztest_json = {k: (bool(v) if isinstance(v, (np.bool_, bool)) else v) for k, v in ztest.items()}
    summary = {
        "hypothesis": "h-m3",
        "statement": "Unanimous scale agreement indicates ≥10% higher verdict reliability vs split verdicts",
        "results": results,
        "ztest": ztest_json,
        "gate": gate,
        "threshold": CONFIG["success_threshold"],
        "significance_level": CONFIG["significance_level"],
    }
    with open(out_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # CSV for traceability
    classified.to_csv(out_path / "classified_agreement.csv", index=False)

    print(f"\nResults saved to {args.output_dir}")
    print(f"\n{'='*50}")
    print(f"GATE RESULT: {gate}")
    print(f"{'='*50}")
    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
