"""H-M2 Orchestration - Robustness evaluation entrypoint"""
import sys
import json
import csv
from pathlib import Path
from datetime import datetime

# Ensure local imports work FIRST
_local_dir = str(Path(__file__).resolve().parent)
if _local_dir not in sys.path:
    sys.path.insert(0, _local_dir)

# Import local config BEFORE reuse_probe modifies sys.path
from config import (
    MCONFIG, COSINE_PASS, COSINE_FAIL,
    ACC_DROP_PASS, ACC_DROP_FAIL,
    ROUTING_CONSISTENCY_PASS, ROUTING_CONSISTENCY_FAIL
)

# Now import reuse_probe (which adds h-e1 to path)
from reuse_probe import build_probe_context
from perturb import PerturbationEngine
from robustness_eval import (
    eval_paraphrase_robustness,
    eval_masking_robustness,
    per_class_consistency,
)
from visualize import (
    plot_gate_metrics,
    plot_cosine_distribution,
    plot_drop_by_perturbation,
    plot_per_class_heatmap,
    plot_failure_cases,
)


def main() -> str:
    """Run robustness evaluation, returns gate result: PASS/PARTIAL/FAIL."""
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("H-M2: Robustness Evaluation")
    print("=" * 60)

    # Build context (reconstructs H-E1 probe)
    ctx = build_probe_context()
    engine = PerturbationEngine(MCONFIG)

    # Paraphrase robustness
    wordnet_res = eval_paraphrase_robustness(ctx, engine, "wordnet")
    embed_res = eval_paraphrase_robustness(ctx, engine, "embedding")

    # Masking robustness
    mask20_kw = eval_masking_robustness(ctx, engine, 0.2, "keyword")
    mask50_kw = eval_masking_robustness(ctx, engine, 0.5, "keyword")
    mask50_rand = eval_masking_robustness(ctx, engine, 0.5, "random")

    # Per-class aggregation
    all_per_sample = wordnet_res["per_sample"] + embed_res["per_sample"]
    per_class = per_class_consistency(ctx, all_per_sample)

    # Aggregate metrics
    cosine_mean = (wordnet_res["cosine_mean"] + embed_res["cosine_mean"]) / 2
    cosine_min = min(wordnet_res["cosine_min"], embed_res["cosine_min"])
    routing_consistency = (wordnet_res["routing_consistency"] + embed_res["routing_consistency"]) / 2
    max_acc_drop = max(mask20_kw["accuracy_drop"], mask50_kw["accuracy_drop"])

    # Gate logic
    cosine_ok = cosine_mean >= COSINE_PASS
    drop_ok = max_acc_drop < ACC_DROP_PASS
    consistency_ok = routing_consistency >= ROUTING_CONSISTENCY_PASS

    if cosine_ok and drop_ok:
        gate = "PASS"
    elif cosine_mean < COSINE_FAIL or max_acc_drop > ACC_DROP_FAIL:
        gate = "FAIL"
    else:
        gate = "PARTIAL"

    # Results summary
    results = {
        "hypothesis": "h-m2",
        "statement": "Routing is robust to paraphrase (cosine ≥0.90) and keyword masking (<10% absolute drop)",
        "gate_result": gate,
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "cosine_mean": cosine_mean,
            "cosine_min": cosine_min,
            "routing_consistency": routing_consistency,
            "max_accuracy_drop": max_acc_drop,
        },
        "thresholds": {
            "cosine_pass": COSINE_PASS,
            "cosine_fail": COSINE_FAIL,
            "acc_drop_pass": ACC_DROP_PASS,
            "acc_drop_fail": ACC_DROP_FAIL,
        },
        "details": {
            "wordnet": {
                "cosine_mean": wordnet_res["cosine_mean"],
                "routing_consistency": wordnet_res["routing_consistency"],
                "total_paraphrases": wordnet_res["total_paraphrases"],
            },
            "embedding": {
                "cosine_mean": embed_res["cosine_mean"],
                "routing_consistency": embed_res["routing_consistency"],
                "total_paraphrases": embed_res["total_paraphrases"],
            },
            "masking": {
                "keyword_20": mask20_kw,
                "keyword_50": mask50_kw,
                "random_50": mask50_rand,
            },
        },
        "per_class_consistency": per_class,
    }

    # Save JSON
    with open(output_dir / "experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Save CSV summary
    with open(output_dir / "results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value", "threshold", "status"])
        writer.writerow(["cosine_mean", f"{cosine_mean:.4f}", COSINE_PASS, "PASS" if cosine_ok else "FAIL"])
        writer.writerow(["max_acc_drop", f"{max_acc_drop:.4f}", ACC_DROP_PASS, "PASS" if drop_ok else "FAIL"])
        writer.writerow(["routing_consistency", f"{routing_consistency:.4f}", ROUTING_CONSISTENCY_PASS,
                        "PASS" if consistency_ok else "FAIL"])
        writer.writerow(["gate_result", gate, "", ""])

    # Collect all cosine values
    all_cosines = []
    for rec in all_per_sample:
        all_cosines.extend(rec.get("cosines", []))

    # Generate visualizations
    plot_gate_metrics(cosine_mean, max_acc_drop, str(output_dir / "gate_metrics.png"))

    if all_cosines:
        plot_cosine_distribution(all_cosines, str(output_dir / "cosine_distribution.png"))

    drops = {
        "Keyword 20%": mask20_kw["accuracy_drop"],
        "Keyword 50%": mask50_kw["accuracy_drop"],
        "Random 50%": mask50_rand["accuracy_drop"],
    }
    plot_drop_by_perturbation(drops, str(output_dir / "drop_by_perturbation.png"))

    if per_class:
        plot_per_class_heatmap(per_class, str(output_dir / "per_class_heatmap.png"))

    # Failure cases (lowest consistency samples)
    failures = sorted(
        [r for r in all_per_sample if r.get("consistent")],
        key=lambda x: sum(x["consistent"]) / max(len(x["consistent"]), 1)
    )
    if failures:
        plot_failure_cases(failures, str(output_dir / "failure_cases.png"))

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Cosine Mean:           {cosine_mean:.4f} (threshold: {COSINE_PASS})")
    print(f"Routing Consistency:   {routing_consistency:.4f} (threshold: {ROUTING_CONSISTENCY_PASS})")
    print(f"Max Accuracy Drop:     {max_acc_drop:.4f} (threshold: {ACC_DROP_PASS})")
    print(f"\nGATE RESULT: {gate}")
    print("=" * 60)

    return gate


if __name__ == "__main__":
    result = main()
    print(f"\nExperiment complete. Gate: {result}")
