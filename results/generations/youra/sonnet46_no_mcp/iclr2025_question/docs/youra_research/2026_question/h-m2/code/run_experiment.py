import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from config import ExperimentConfig, get_config
from data_loader import load_cluster_counts, load_labels, validate_cluster_counts
from analysis import (
    bootstrap_aggregation_ci,
    compute_distribution_stats,
    compute_collapse_rate,
    compute_pointbiserial_correlation,
    stratified_aggregation_by_type,
    evaluate_gate,
    validate_results_schema,
)
from visualize import (
    plot_aggregation_rate,
    plot_cluster_count_dist,
    plot_cluster_count_by_label,
    plot_cluster_count_cdf,
    plot_aggregation_by_type,
    CDF_THRESHOLD_VALUE,
)


def run(cfg: ExperimentConfig) -> Dict[str, Any]:
    """Orchestrate full H-M2 pipeline."""
    # [1/6] Load cluster counts (priority: se_json → hm1_summary → nli_recluster)
    print("[1/6] Loading cluster counts...")
    try:
        cluster_counts, source = load_cluster_counts(cfg)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Could not load cluster counts from any source.\n"
            f"Remediation: Ensure H-E1 outputs exist at {cfg.se_scores_path} or "
            f"{cfg.stochastic_samples_path}\nOriginal error: {e}"
        )
    print(f"  Source: {source}, shape: {cluster_counts.shape}")

    # [2/6] Load labels
    print("[2/6] Loading hallucination labels...")
    labels = load_labels(cfg)
    print(f"  Labels shape: {labels.shape}, positive rate: {labels.mean():.3f}")

    # [3/6] Validate cluster counts
    print("[3/6] Validating cluster counts...")
    cluster_counts = validate_cluster_counts(cluster_counts, n=len(labels))

    # [4/6] Compute statistics
    print("[4/6] Computing statistics...")
    bootstrap_result = bootstrap_aggregation_ci(
        cluster_counts, cfg.n_bootstrap, cfg.seed, cfg.n_samples_per_example
    )
    dist_stats = compute_distribution_stats(cluster_counts)
    collapse_rate = compute_collapse_rate(cluster_counts)
    corr_result = compute_pointbiserial_correlation(labels, cluster_counts)

    # Load dataset for stratified analysis
    try:
        with open(cfg.dataset_path) as f:
            dataset = json.load(f)
        strat = stratified_aggregation_by_type(cluster_counts, dataset, cfg.n_samples_per_example)
    except Exception:
        strat = None

    print(f"  aggregation_rate: {bootstrap_result['aggregation_rate']:.4f}")
    print(f"  ci: [{bootstrap_result['ci_lower']:.4f}, {bootstrap_result['ci_upper']:.4f}]")
    print(f"  collapse_rate: {collapse_rate:.4f}")
    print(f"  r_pb: {corr_result['r_pb']:.4f}, p={corr_result['p_value']:.4f}")

    # [5/6] Gate evaluation
    print("[5/6] Evaluating gate...")
    gate_result = evaluate_gate(bootstrap_result, cfg)
    print(f"  Gate result: {gate_result}")

    # [6/6] Generate figures
    print("[6/6] Generating figures...")
    figures_dir = Path(cfg.figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_aggregation_rate(
        bootstrap_result["aggregation_rate"],
        bootstrap_result["ci_lower"],
        bootstrap_result["ci_upper"],
        cfg.aggregation_gate_threshold,
        str(figures_dir / "aggregation_rate.png"),
    )
    plot_cluster_count_dist(cluster_counts, str(figures_dir / "cluster_count_dist.png"))
    plot_cluster_count_by_label(cluster_counts, labels, str(figures_dir / "cluster_count_by_label.png"))
    plot_cluster_count_cdf(cluster_counts, threshold=CDF_THRESHOLD_VALUE, output_path=str(figures_dir / "cluster_count_cdf.png"))
    if strat is not None:
        plot_aggregation_by_type(strat, str(figures_dir / "aggregation_by_type.png"))

    results = {
        "hypothesis_id": "h-m2",
        "cluster_count_source": source,
        "n_examples": int(len(cluster_counts)),
        **dist_stats,
        "aggregation_rate": bootstrap_result["aggregation_rate"],
        "collapse_rate": collapse_rate,
        "bootstrap_ci_lower": bootstrap_result["ci_lower"],
        "bootstrap_ci_upper": bootstrap_result["ci_upper"],
        "gate_pass": bootstrap_result["gate_pass"],
        "gate_result": gate_result,
        "r_pb": corr_result["r_pb"],
        "p_value": corr_result["p_value"],
        "stratified_aggregation": strat,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return results


def save_results(results: Dict[str, Any], results_dir: str) -> None:
    """Serialize results to {results_dir}/experiment_results.json."""
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(results_dir) / "experiment_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved to {out_path}")


def write_validation_report(results: Dict[str, Any], output_path: str) -> None:
    """Write 04_validation.md with gate decision, all metrics, figure references."""
    gate_result = results["gate_result"]
    agg_rate = results["aggregation_rate"]
    ci_lower = results["bootstrap_ci_lower"]
    ci_upper = results["bootstrap_ci_upper"]
    gate_pass = results["gate_pass"]
    collapse_rate = results["collapse_rate"]
    mean_cc = results["mean_cluster_count"]
    std_cc = results["std_cluster_count"]
    median_cc = results["median_cluster_count"]
    r_pb = results["r_pb"]
    p_value = results["p_value"]
    source = results["cluster_count_source"]
    histogram = results["histogram"]
    n_examples = results["n_examples"]
    timestamp = results["timestamp"]

    pivot_note = ""
    if gate_result == "PIVOT":
        pivot_note = """
## ⚠️ PIVOT Condition (A2 Violation)

The aggregation rate is below the 0.30 threshold, indicating that deberta-large-mnli NLI clustering
does NOT produce meaningful semantic aggregation on HaluEval-QA responses.

**Interpretation:** This is an A2 violation — the NLI model does not generalize to HaluEval-QA
response style. Short factual QA answers are treated as semantically distinct by deberta-large-mnli
even when they convey equivalent meaning.

**Pipeline Action:** PIVOT to alternative NLI thresholds or models. Pipeline continues to H-M3.
"""

    partial_note = ""
    if gate_result == "PARTIAL":
        partial_note = """
## ⚠️ PARTIAL Gate Result

The aggregation rate falls in the weak-pass zone [0.30, 0.50). Clustering occurs but below threshold.
**Pipeline Action:** Document as PARTIAL — pipeline continues to H-M3 with limitation noted.
"""

    hist_rows = "\n".join(
        f"| {k} | {v} | {v/n_examples:.3f} |"
        for k, v in sorted(histogram.items())
    )

    report = f"""# H-M2 Validation Report
## NLI Clustering Aggregation Behavior Analysis

**Generated:** {timestamp}
**Hypothesis ID:** h-m2
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_result}
**Cluster Count Source:** {source}

---

## Gate Decision: {gate_result}

| Criterion | Threshold | Value | Status |
|-----------|-----------|-------|--------|
| Aggregation Rate | ≥ 0.50 | {agg_rate:.4f} | {"✅ PASS" if agg_rate >= 0.50 else "❌ FAIL"} |
| CI Lower Bound | ≥ 0.30 | {ci_lower:.4f} | {"✅ PASS" if ci_lower >= 0.30 else "❌ FAIL"} |
| Gate Pass | Both | {gate_pass} | {"✅" if gate_pass else "❌"} |

**Bootstrap 95% CI:** [{ci_lower:.4f}, {ci_upper:.4f}]

---

## Primary Metrics

| Metric | Value |
|--------|-------|
| Aggregation Rate | {agg_rate:.4f} |
| Bootstrap CI Lower | {ci_lower:.4f} |
| Bootstrap CI Upper | {ci_upper:.4f} |
| Gate Pass | {gate_pass} |
| Gate Result | **{gate_result}** |
| Collapse Rate | {collapse_rate:.4f} |
| Mean Cluster Count | {mean_cc:.4f} |
| Std Cluster Count | {std_cc:.4f} |
| Median Cluster Count | {median_cc:.4f} |
| Point-Biserial r | {r_pb:.4f} |
| p-value | {p_value:.4f} |
| N Examples | {n_examples} |

---

## Cluster Count Distribution

| Cluster Count | Frequency | Fraction |
|---------------|-----------|----------|
{hist_rows}

---

## Figures

- `figures/aggregation_rate.png` — Aggregation rate bar chart with 95% CI vs gate threshold
- `figures/cluster_count_dist.png` — Histogram of cluster count values (1–5)
- `figures/cluster_count_by_label.png` — Box plot: cluster count by hallucination label
- `figures/cluster_count_cdf.png` — CDF of cluster counts with threshold line at x=4
{pivot_note}{partial_note}
---

## Summary

H-M2 analyzed the NLI clustering aggregation behavior on 2,000 HaluEval-QA examples using
deberta-large-mnli (lorenzkuhn/semantic_uncertainty). Cluster counts were loaded from {source}.

**Key finding:** aggregation_rate = {agg_rate:.4f} (95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]).
Mean cluster count = {mean_cc:.4f} (expected ~4.644 from H-M1).

**Gate:** {gate_result} (SHOULD_WORK — failure does not halt pipeline).
"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"✓ Validation report written to {output_path}")


if __name__ == "__main__":
    # Change working directory to script location so relative paths work
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    cfg = get_config()
    results = run(cfg)
    validate_results_schema(results)
    save_results(results, cfg.results_dir)
    write_validation_report(results, "../../04_validation.md")
    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE")
    print(f"Gate result: {results['gate_result']}")
    print(f"Aggregation rate: {results['aggregation_rate']:.4f}")
    print(f"{'='*60}")
