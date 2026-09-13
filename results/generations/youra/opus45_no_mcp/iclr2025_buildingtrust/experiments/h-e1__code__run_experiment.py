"""Main experiment orchestration for H-E1."""
import json
import os
import sys
import numpy as np
from datetime import datetime

from config import CONFIG
from data import load_truthfulqa_mc1, format_choices
from prompts import build_prompt
from api_client import APIClient
from extract import extract_confidence, extract_answer
from metrics import compute_ece, extraction_rate
from visualize import (
    plot_extraction_rates,
    plot_reliability_diagram,
    plot_ece_comparison,
    plot_failure_breakdown
)


def run_condition(dataset: list, condition: str, client: APIClient) -> dict:
    """Run one prompting condition across dataset."""
    results = []
    n_total = len(dataset)
    n_extracted = 0
    failures = {"no_confidence": 0, "no_answer": 0, "both_missing": 0}

    print(f"  Running condition: {condition} ({n_total} items)")

    for i, item in enumerate(dataset):
        if (i + 1) % 100 == 0:
            print(f"    Progress: {i + 1}/{n_total}")

        prompt = build_prompt(condition, item["question"], format_choices(item["choices"]))
        response = client.call(prompt)

        confidence = extract_confidence(response)
        answer = extract_answer(response, len(item["choices"]))

        if confidence is None and answer is None:
            failures["both_missing"] += 1
            continue
        elif confidence is None:
            failures["no_confidence"] += 1
            continue
        elif answer is None:
            failures["no_answer"] += 1
            continue

        correct_letter = chr(ord("A") + item["correct_idx"])
        correct = (answer == correct_letter)

        results.append({
            "question_idx": i,
            "condition": condition,
            "confidence": confidence,
            "answer": answer,
            "correct": correct,
            "raw_response": response
        })
        n_extracted += 1

    ext_rate = extraction_rate(n_extracted, n_total)

    if n_extracted > 0:
        confidences = np.array([r["confidence"] for r in results])
        accuracies = np.array([r["correct"] for r in results], dtype=float)
        ece = compute_ece(confidences, accuracies)
    else:
        ece = None

    return {
        "condition": condition,
        "n_total": n_total,
        "n_extracted": n_extracted,
        "extraction_rate": ext_rate,
        "ece": ece,
        "accuracy": float(np.mean([r["correct"] for r in results])) if results else None,
        "results": results,
        "failures": failures
    }


def main():
    print("=" * 60)
    print("H-E1: ECE Measurability Validation Experiment")
    print("=" * 60)

    # Create output directories
    os.makedirs(CONFIG.output.results_dir, exist_ok=True)
    os.makedirs(CONFIG.output.figures_dir, exist_ok=True)

    # Load dataset
    print("\nLoading TruthfulQA mc1 dataset...")
    dataset = load_truthfulqa_mc1()
    print(f"Loaded {len(dataset)} items")

    # Initialize API client
    client = APIClient()

    # Run all conditions
    summaries = {}
    all_failures = {}

    print("\nRunning experiments...")
    for condition in CONFIG.experiment.conditions:
        summary = run_condition(dataset, condition, client)
        summaries[condition] = summary
        print(f"  {condition}: extraction_rate={summary['extraction_rate']:.3f}, ECE={summary['ece']}")

        # Aggregate failures
        for fail_type, count in summary["failures"].items():
            all_failures[fail_type] = all_failures.get(fail_type, 0) + count

    # Save results
    results_data = {
        "metadata": {
            "experiment": "H-E1",
            "date": datetime.now().isoformat(),
            "model": CONFIG.model.model_name,
            "dataset": f"{CONFIG.dataset.dataset_name}/{CONFIG.dataset.subset}",
            "n_items": len(dataset),
            "conditions": CONFIG.experiment.conditions
        },
        "summaries": {
            c: {
                "extraction_rate": s["extraction_rate"],
                "ece": s["ece"],
                "accuracy": s["accuracy"],
                "n_extracted": s["n_extracted"],
                "n_total": s["n_total"],
                "failures": s["failures"]
            }
            for c, s in summaries.items()
        },
        "raw_results": {
            c: s["results"] for c, s in summaries.items()
        }
    }

    with open(CONFIG.output.results_path, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nResults saved to {CONFIG.output.results_path}")

    # Generate visualizations
    print("\nGenerating visualizations...")

    extraction_rates = {c: s["extraction_rate"] for c, s in summaries.items()}
    plot_extraction_rates(extraction_rates, CONFIG.output.figures_dir)

    ece_by_condition = {c: s["ece"] for c, s in summaries.items()}
    plot_ece_comparison(ece_by_condition, CONFIG.output.figures_dir)

    for condition, summary in summaries.items():
        plot_reliability_diagram(summary["results"], condition, CONFIG.output.figures_dir)

    plot_failure_breakdown(all_failures, CONFIG.output.figures_dir)

    print(f"Figures saved to {CONFIG.output.figures_dir}")

    # Gate evaluation
    print("\n" + "=" * 60)
    print("GATE EVALUATION (MUST_WORK)")
    print("=" * 60)

    all_pass = True
    for condition, summary in summaries.items():
        rate = summary["extraction_rate"]
        ece = summary["ece"]
        rate_pass = rate >= CONFIG.experiment.extraction_rate_threshold
        ece_valid = ece is not None and 0 <= ece <= 1

        status = "PASS" if (rate_pass and ece_valid) else "FAIL"
        ece_str = f"{ece:.4f}" if ece is not None else "N/A"
        print(f"{condition}: rate={rate:.3f} ({'OK' if rate_pass else 'FAIL'}), "
              f"ECE={ece_str} ({'OK' if ece_valid else 'INVALID'})")

        if not (rate_pass and ece_valid):
            all_pass = False

    print("-" * 60)
    gate_result = "PASS" if all_pass else "FAIL"
    print(f"Overall Gate Result: {gate_result}")

    # Write gate result to outputs
    with open("outputs/results.csv", "w") as f:
        f.write("condition,extraction_rate,ece,accuracy,n_extracted,n_total,gate_pass\n")
        for c, s in summaries.items():
            rate_pass = s["extraction_rate"] >= CONFIG.experiment.extraction_rate_threshold
            ece_valid = s["ece"] is not None and 0 <= s["ece"] <= 1
            gate = "PASS" if (rate_pass and ece_valid) else "FAIL"
            ece_val = f"{s['ece']:.4f}" if s['ece'] is not None else ""
            acc_val = f"{s['accuracy']:.4f}" if s['accuracy'] is not None else ""
            f.write(f"{c},{s['extraction_rate']:.4f},{ece_val},{acc_val},{s['n_extracted']},{s['n_total']},{gate}\n")

    print(f"\nCSV results saved to outputs/results.csv")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
