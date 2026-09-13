#!/usr/bin/env python3
"""Main runner for H-M1 gradient concentration analysis."""
import os
import sys
import json
import random
import argparse
from datetime import datetime

import torch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config, SEED, MODEL_NAME
from gradient_analysis import (
    run_full_analysis,
    run_stratified_analysis,
    analyze_single_sample,
    parse_traceback_line,
    classify_error,
)
from sample_collector import generate_failing_samples, generate_synthetic_samples
from visualization import generate_all_figures


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_model_and_tokenizer(model_name=MODEL_NAME):
    """Load CodeT5 model and tokenizer."""
    from transformers import T5ForConditionalGeneration, AutoTokenizer

    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    if torch.cuda.is_available():
        model = model.cuda()
        print("Model loaded on GPU")
    else:
        print("Model loaded on CPU")

    return model, tokenizer


def run_random_baseline(model, tokenizer, samples):
    """Run analysis with random line penalties instead of error line."""
    random_samples = []
    for sample in samples:
        code_lines = sample["code"].split('\n')
        num_lines = len([l for l in code_lines if l.strip()])
        if num_lines > 0:
            random_line = random.randint(1, num_lines)
            random_sample = sample.copy()
            random_sample["random_line"] = random_line
            random_samples.append(random_sample)

    results = []
    for sample in random_samples:
        metrics = analyze_single_sample(
            model, tokenizer,
            sample["code"], sample["traceback"],
            error_line=sample.get("error_line"),
            random_line=sample.get("random_line")
        )
        if metrics:
            results.append(metrics)

    if not results:
        return {"mean_concentration_ratio": 1.0, "n_samples": 0}

    ratios = [r["concentration_ratio"] for r in results]
    return {
        "mean_concentration_ratio": np.mean(ratios),
        "std_concentration_ratio": np.std(ratios),
        "n_samples": len(results),
    }


def determine_verdict(results):
    """Determine PASS/FAIL based on success criteria."""
    all_results = results.get("all", {})

    if all_results.get("error") or all_results.get("n_samples", 0) == 0:
        return "FAIL", "No valid samples analyzed"

    primary_met = all_results.get("primary_criterion_met", False)
    secondary_met = all_results.get("secondary_criterion_met", False)
    p_value = all_results.get("p_value", 1.0)

    reasons = []

    if all_results.get("mean_concentration_ratio", 0) > 1.0:
        reasons.append(f"mean_ratio={all_results['mean_concentration_ratio']:.3f} > 1.0")
    else:
        reasons.append(f"FAIL: mean_ratio={all_results.get('mean_concentration_ratio', 0):.3f} <= 1.0")

    if all_results.get("mean_within_2_lines_pct", 0) > 0.80:
        reasons.append(f"mean_within_2={all_results['mean_within_2_lines_pct']:.3f} > 0.80")
    else:
        reasons.append(f"FAIL: mean_within_2={all_results.get('mean_within_2_lines_pct', 0):.3f} <= 0.80")

    if p_value < 0.05:
        reasons.append(f"p_value={p_value:.4f} < 0.05 (significant)")
    else:
        reasons.append(f"p_value={p_value:.4f} >= 0.05 (not significant)")

    verdict = "PASS" if (primary_met and secondary_met and p_value < 0.05) else "FAIL"

    return verdict, "; ".join(reasons)


def main():
    parser = argparse.ArgumentParser(description="H-M1 Gradient Concentration Analysis")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic samples for testing")
    parser.add_argument("--n-samples", type=int, default=500, help="Number of samples")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    set_seed(args.seed)
    config = get_config()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    output_dir = args.output_dir or os.path.join(base_dir, "results")
    figures_dir = os.path.join(base_dir, "figures")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print("=" * 60)
    print("H-M1: Gradient Concentration Analysis")
    print("=" * 60)
    print(f"Samples: {args.n_samples}")
    print(f"Seed: {args.seed}")
    print(f"Mode: {'Synthetic' if args.synthetic else 'Real'}")
    print()

    class MockModel:
        def __init__(self):
            self.model = self
            self._embedding = torch.nn.Embedding(32100, 512)

        def get_input_embeddings(self):
            return self._embedding

        def zero_grad(self):
            self._embedding.zero_grad()

        def parameters(self):
            return [self._embedding.weight]

        def __call__(self, **kwargs):
            seq_len = kwargs.get("decoder_input_ids", torch.zeros(1, 10)).shape[1]
            class Output:
                logits = torch.randn(1, seq_len, 32100, requires_grad=True)
                decoder_hidden_states = [torch.randn(1, seq_len, 512)]
            return Output()

        def generate(self, **kwargs):
            return torch.randint(0, 1000, (1, 50))

    if args.synthetic:
        print("Generating synthetic samples...")
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = MockModel()
        samples = generate_synthetic_samples(n_samples=args.n_samples, seed=args.seed)
    else:
        model, tokenizer = load_model_and_tokenizer()
        print("Loading APPS dataset...")
        from datasets import load_dataset
        dataset = load_dataset("codeparrot/apps", split="train[:2000]", trust_remote_code=True)

        print(f"Generating {args.n_samples} failing samples...")
        samples = generate_failing_samples(
            model, tokenizer, dataset,
            n_samples=args.n_samples,
            max_attempts=args.n_samples * 4,
            seed=args.seed
        )

    print(f"\nAnalyzing {len(samples)} samples...")

    results = run_stratified_analysis(model, tokenizer, samples)

    print("\nRunning random baseline...")
    random_results = run_random_baseline(model, tokenizer, samples)
    results["random"] = random_results

    verdict, reasons = determine_verdict(results)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    all_results = results.get("all", {})
    print(f"Samples analyzed: {all_results.get('n_samples', 0)}")
    print(f"Mean concentration ratio: {all_results.get('mean_concentration_ratio', 0):.4f}")
    print(f"Mean within +/-2 lines: {all_results.get('mean_within_2_lines_pct', 0):.4f}")
    print(f"Success rate: {all_results.get('success_rate', 0):.2%}")
    print(f"T-statistic: {all_results.get('t_stat', 0):.4f}")
    print(f"P-value (one-sided): {all_results.get('p_value', 1.0):.6f}")

    print("\nStratified Results:")
    for key in ["u_line", "u_ignore", "random"]:
        r = results.get(key, {})
        if r and r.get("n_samples", 0) > 0:
            print(f"  {key}: ratio={r.get('mean_concentration_ratio', 0):.3f}, n={r.get('n_samples', 0)}")

    print(f"\nPrimary criterion met: {all_results.get('primary_criterion_met', False)}")
    print(f"Secondary criterion met: {all_results.get('secondary_criterion_met', False)}")
    print(f"\nVERDICT: {verdict}")
    print(f"Reasons: {reasons}")

    print("\nGenerating figures...")
    generate_all_figures(results, figures_dir)

    output_data = {
        "hypothesis": "H-M1",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_samples": args.n_samples,
            "seed": args.seed,
            "synthetic": args.synthetic,
            "model": MODEL_NAME,
        },
        "results": {
            "all": {k: v for k, v in all_results.items() if k != "per_sample_results"},
            "u_line": results.get("u_line", {}),
            "u_ignore": results.get("u_ignore", {}),
            "random": results.get("random", {}),
        },
        "verdict": verdict,
        "verdict_reasons": reasons,
        "gate": {
            "type": "MUST_WORK",
            "result": verdict,
            "satisfied": verdict == "PASS",
        },
    }

    results_path = os.path.join(output_dir, "analysis_results.json")
    with open(results_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\nResults saved to: {results_path}")

    verdict_path = os.path.join(output_dir, "verdict.txt")
    with open(verdict_path, "w") as f:
        f.write(f"VERDICT: {verdict}\n")
        f.write(f"REASONS: {reasons}\n")
        f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
    print(f"Verdict saved to: {verdict_path}")

    return output_data


if __name__ == "__main__":
    main()
