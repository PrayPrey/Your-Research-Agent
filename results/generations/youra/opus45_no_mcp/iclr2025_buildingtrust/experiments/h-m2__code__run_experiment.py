#!/usr/bin/env python3
"""Main experiment runner for H-M2 Hedging Marker Detection."""
import json
import os
import sys
from pathlib import Path

import yaml

from config import CONFIG
from data import load_truthfulqa_generation
from prompts import build_cot_confidence_prompt
from api_client import APIClient
from hedging_detect import (
    analyze_hedging, extract_confidence, count_hedging_markers, EXTENDED_HEDGING_MARKERS
)
from metrics import compute_metrics, marker_frequency_distribution, check_gate
from visualize import generate_visualizations


def run_generation(dataset: list[dict], client: APIClient) -> list[dict]:
    """Run CoT+confidence generation on all items.

    Args:
        dataset: List of dicts with 'question' key.
        client: APIClient instance.

    Returns:
        List of per-item result dicts.
    """
    results = []
    total = len(dataset)

    for i, item in enumerate(dataset):
        prompt = build_cot_confidence_prompt(item["question"])
        raw = client.call(prompt, cache_key=f"hm2_{i}")
        analysis = analyze_hedging(raw)
        conf = extract_confidence(raw)

        results.append({
            "question": item["question"],
            "raw_output": raw,
            "confidence": conf,
            **analysis,
        })

        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{total}")

    return results


def main() -> None:
    print("=" * 60)
    print("H-M2: Hedging Marker Detection Experiment")
    print("=" * 60)

    print("\n[1/6] Loading TruthfulQA generation dataset...")
    dataset = load_truthfulqa_generation()
    print(f"Loaded {len(dataset)} questions")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY required for real experiment. Set environment variable.")

    print("\n[2/6] Running CoT+confidence generation...")
    client = APIClient(max_tokens=CONFIG["model"]["max_tokens"])
    results = run_generation(dataset, client)
    client.close()

    print(f"\n[3/6] Computing metrics...")
    metrics = compute_metrics(results)
    freq = marker_frequency_distribution(results)
    gate = check_gate(metrics)

    print(f"  Hedging presence rate: {metrics['hedging_presence_rate']:.1%}")
    print(f"  Mean hedging count: {metrics['mean_hedging_count']:.2f}")
    print(f"  Gate ({gate['threshold']:.0%} threshold): {gate['status']}")

    if gate["status"] != "PASS":
        print("\n[4/6] EXPLORE: Running extended hedging analysis...")
        for r in results:
            ext = count_hedging_markers(r["reasoning_text"], EXTENDED_HEDGING_MARKERS)
            r["extended_hedging"] = ext
        extended_rate = sum(r["extended_hedging"]["has_hedging"] for r in results) / len(results)
        metrics["explore_hedging_presence_rate"] = extended_rate
        print(f"  Extended hedging rate: {extended_rate:.1%}")
    else:
        print("\n[4/6] Gate PASSED, skipping EXPLORE...")

    print("\n[5/6] Saving results...")
    results_path = Path(CONFIG["paths"]["results_path"])
    summary_path = Path(CONFIG["paths"]["summary_path"])

    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results: {results_path}")

    summary = {
        "metrics": metrics,
        "gate": gate,
        "marker_frequency": freq,
        "mode": "API",
        "n_samples": len(results),
    }
    with open(summary_path, "w") as f:
        yaml.dump(summary, f, default_flow_style=False)
    print(f"  Summary: {summary_path}")

    print("\n[6/6] Generating visualizations...")
    figures_dir = Path(CONFIG["paths"]["figures_dir"])
    metrics["threshold"] = gate["threshold"]
    generate_visualizations(metrics, freq, results, figures_dir)
    print(f"  Figures: {figures_dir}/")

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print(f"Gate Status: {gate['status']}")
    print(f"Hedging Presence Rate: {metrics['hedging_presence_rate']:.1%} (threshold: {gate['threshold']:.0%})")
    print("=" * 60)


if __name__ == "__main__":
    main()
