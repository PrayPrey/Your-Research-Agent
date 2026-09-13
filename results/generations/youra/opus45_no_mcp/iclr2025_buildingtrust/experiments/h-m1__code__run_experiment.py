"""A-7: Experiment Orchestration - Run baseline+CoT (1634 calls), save results JSON"""
import json
import os
import sys
from datetime import datetime

from data import load_truthfulqa_mc2, format_options
from prompts import build_baseline_prompt, build_cot_prompt
from api_client import APIClient
from reasoning_detect import detect_reasoning_chain, count_reasoning_steps, classify_patterns, extract_answer, extract_confidence
from metrics import compute_metrics, check_gate
from config import CONFIG


def run_condition(dataset: list[dict], condition: str, client: APIClient) -> list[dict]:
    """Run experiment for a single condition (baseline or cot)."""
    results = []
    total = len(dataset)

    for i, item in enumerate(dataset):
        options_str, letters = format_options(item["mc2_targets"])

        if condition == "cot":
            prompt = build_cot_prompt(item["question"], options_str)
        else:
            prompt = build_baseline_prompt(item["question"], options_str)

        cache_key = f"{condition}_{i}"
        raw = client.call(prompt, cache_key)

        has_reasoning = detect_reasoning_chain(raw)
        step_count = count_reasoning_steps(raw)
        patterns = classify_patterns(raw)
        answer = extract_answer(raw, len(letters))
        confidence = extract_confidence(raw)

        results.append({
            "index": i,
            "question": item["question"],
            "raw_output": raw,
            "has_reasoning": has_reasoning,
            "step_count": step_count,
            "patterns": patterns,
            "answer": answer,
            "confidence": confidence,
        })

        if (i + 1) % 100 == 0:
            print(f"[{condition}] Progress: {i + 1}/{total}")

    return results


def main():
    print(f"H-M1 Experiment: CoT Reasoning Chain Detection")
    print(f"Started: {datetime.now().isoformat()}")

    os.makedirs(CONFIG.paths.results_dir, exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG.paths.cache_path), exist_ok=True)

    print("Loading TruthfulQA MC2 dataset...")
    dataset = load_truthfulqa_mc2()
    print(f"Loaded {len(dataset)} items")

    client = APIClient(
        model=CONFIG.api.model,
        cache_path=CONFIG.paths.cache_path,
        max_retries=CONFIG.api.max_retries,
        temperature=CONFIG.api.temperature,
        max_tokens=CONFIG.api.max_tokens,
    )

    print("\n=== Running Baseline Condition ===")
    baseline_results = run_condition(dataset, "baseline", client)

    print("\n=== Running CoT Condition ===")
    cot_results = run_condition(dataset, "cot", client)

    client.close()

    print("\n=== Computing Metrics ===")
    baseline_metrics = compute_metrics(baseline_results)
    cot_metrics = compute_metrics(cot_results)
    gate = check_gate(cot_metrics, baseline_metrics)

    print(f"Baseline: reasoning_rate={baseline_metrics['reasoning_presence_rate']:.3f}, mean_steps={baseline_metrics['mean_step_count']:.2f}")
    print(f"CoT: reasoning_rate={cot_metrics['reasoning_presence_rate']:.3f}, mean_steps={cot_metrics['mean_step_count']:.2f}")
    print(f"\n=== Gate Results ===")
    print(f"Gate 1 (cot_rate > 0.90): {gate['gate_1_rate_pass']} ({gate['cot_reasoning_rate']:.3f})")
    print(f"Gate 2 (delta > 0.50): {gate['gate_2_delta_pass']} ({gate['rate_difference']:.3f})")
    print(f"Gate 3 (mean_steps > 2.0): {gate['gate_3_steps_pass']} ({gate['mean_step_count']:.2f})")
    print(f"ALL PASS: {gate['all_pass']}")

    results = {
        "hypothesis_id": CONFIG.hypothesis_id,
        "date": datetime.now().isoformat(),
        "dataset": {
            "name": CONFIG.dataset.name,
            "subset": CONFIG.dataset.subset,
            "split": CONFIG.dataset.split,
            "n": len(dataset),
        },
        "baseline": baseline_results,
        "cot": cot_results,
        "baseline_metrics": baseline_metrics,
        "cot_metrics": cot_metrics,
        "gate": gate,
    }

    with open(CONFIG.paths.results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {CONFIG.paths.results_file}")

    print(f"\nCompleted: {datetime.now().isoformat()}")
    return gate["all_pass"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
