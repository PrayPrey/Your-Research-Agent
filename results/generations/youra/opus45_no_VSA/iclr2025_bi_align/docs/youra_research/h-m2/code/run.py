#!/usr/bin/env python3
import os
import sys
import json
import numpy as np

# Import m2 config FIRST before sys.path manipulation
FIGURES_DIR = "figures"
OUTPUTS_DIR = "outputs"
DISAGREEMENT_THRESHOLD = 0.20
PARTIAL_THRESHOLD = 0.10

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code"))
from data import load_hh_rlhf, load_reward_bench_safety

from bai import train_proxy_detectors, compute_bai_scores
from reward import load_reward_model, compute_reward_scores
from analysis import compute_disagreement_rate, compute_correlations, verify_mechanism

import importlib.util
spec = importlib.util.spec_from_file_location("evaluate_m2", os.path.join(os.path.dirname(__file__), "evaluate.py"))
evaluate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluate)


def main():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    print("=" * 60)
    print("H-M2: BAI-Reward Disagreement Analysis")
    print("=" * 60)

    print("\n[1/6] Loading datasets...")
    hh_texts = load_hh_rlhf()
    rb_texts = load_reward_bench_safety()
    responses = hh_texts + rb_texts
    print(f"Total responses: {len(responses)} (HH-RLHF: {len(hh_texts)}, RewardBench: {len(rb_texts)})")

    print("\n[2/6] Training proxy detectors...")
    detectors = train_proxy_detectors()

    print("\n[3/6] Computing BAI scores...")
    bai_scores = compute_bai_scores(responses, detectors)
    print(f"BAI scores: mean={np.mean(bai_scores):.4f}, std={np.std(bai_scores):.4f}")

    print("\n[4/6] Computing reward scores...")
    model, tokenizer = load_reward_model()
    prompts = [""] * len(responses)
    reward_scores = compute_reward_scores(prompts, responses, model, tokenizer)
    print(f"Reward scores: mean={np.mean(reward_scores):.4f}, std={np.std(reward_scores):.4f}")

    print("\n[5/6] Analyzing disagreement...")
    disagreement_result = compute_disagreement_rate(bai_scores, reward_scores)
    correlations = compute_correlations(bai_scores, reward_scores)

    results = {
        "sample_count": len(responses),
        "bai_variance": float(np.var(bai_scores)),
        "reward_variance": float(np.var(reward_scores)),
        **disagreement_result,
        **correlations,
    }

    del results["bai_z"]
    del results["reward_z"]

    verification = verify_mechanism(results)
    results["verification"] = verification

    print(f"\nDisagreement rate: {disagreement_result['disagreement_rate']:.4f}")
    print(f"Quadrant counts: HH={disagreement_result['hh_count']}, HL={disagreement_result['hl_count']}, LH={disagreement_result['lh_count']}, LL={disagreement_result['ll_count']}")
    print(f"Correlations: Pearson r={correlations['pearson_r']:.4f}, Spearman r={correlations['spearman_r']:.4f}")

    print("\n[6/6] Generating figures...")
    evaluate.plot_gate_bar(
        disagreement_result["disagreement_rate"],
        os.path.join(FIGURES_DIR, "gate_bar.png")
    )
    evaluate.plot_scatter_quadrants(
        disagreement_result["bai_z"],
        disagreement_result["reward_z"],
        disagreement_result["q_bounds"],
        os.path.join(FIGURES_DIR, "scatter_quadrants.png")
    )
    evaluate.plot_density_heatmap(
        disagreement_result["bai_z"],
        disagreement_result["reward_z"],
        os.path.join(FIGURES_DIR, "density_heatmap.png")
    )
    evaluate.plot_distributions(
        bai_scores,
        reward_scores,
        os.path.join(FIGURES_DIR, "distributions.png")
    )

    examples = evaluate.top_disagreement_examples(
        responses,
        disagreement_result["bai_z"],
        disagreement_result["reward_z"],
        n=10
    )
    results["top_disagreement_examples"] = examples

    rate = disagreement_result["disagreement_rate"]
    if rate >= DISAGREEMENT_THRESHOLD:
        gate_result = "PASS"
    elif rate >= PARTIAL_THRESHOLD:
        gate_result = "PARTIAL"
    else:
        gate_result = "FAIL"

    results["gate_result"] = gate_result
    results["thresholds"] = {
        "pass": DISAGREEMENT_THRESHOLD,
        "partial": PARTIAL_THRESHOLD,
    }

    output_path = os.path.join(OUTPUTS_DIR, "results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=float)

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {gate_result}")
    print(f"Disagreement Rate: {rate:.4f} (threshold: {DISAGREEMENT_THRESHOLD})")
    print(f"Results saved to: {output_path}")
    print("=" * 60)

    return gate_result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result in ["PASS", "PARTIAL"] else 1)
