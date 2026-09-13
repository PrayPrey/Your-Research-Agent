#!/usr/bin/env python3
import json
import os
import sys
import torch
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from data import load_corpus_and_benchmark, inject_benchmark
from detect import ngram_overlap_detect, evaluate_detector_precision
from model import load_model_and_tokenizer, compute_attribution_scores, compute_ccr
from train import train_one_run
from evaluate import (
    eval_mmlu_accuracy, fit_ccr_regression, verify_mechanism_activation,
    plot_ccr_scaling, plot_mmlu_vs_injection, plot_attribution_distribution
)


def run_all(cfg: Config) -> dict:
    os.makedirs(cfg.out_dir, exist_ok=True)

    print("=" * 60)
    print("H-E1: CCR Scaling Experiment")
    print("=" * 60)

    corpus, benchmark = load_corpus_and_benchmark(cfg)

    results = {}
    ccr_values = []
    mmlu_accs = []
    f1_values = []

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    for rate in cfg.injection_rates:
        print(f"\n{'='*40}")
        print(f"Injection Rate: {rate}")
        print(f"{'='*40}")

        model, tokenizer, injected_positions = train_one_run(cfg, corpus, benchmark, rate)

        print("Evaluating MMLU accuracy...")
        mmlu_acc = eval_mmlu_accuracy(model, tokenizer, benchmark, device)
        print(f"MMLU Accuracy: {mmlu_acc:.4f}")

        print("Computing attribution scores...")
        corpus_contaminated, _ = inject_benchmark(corpus, benchmark, rate, cfg.seed)
        scores = compute_attribution_scores(model, tokenizer, corpus_contaminated[:1000], benchmark[:100], device)

        ccr = compute_ccr(scores, [p for p in injected_positions if p < 1000])
        print(f"CCR: {ccr:.4f}")

        print("Running n-gram detector...")
        detected = ngram_overlap_detect(corpus_contaminated, benchmark, cfg.ngram_n)
        detector_metrics = evaluate_detector_precision(detected, set(injected_positions))
        print(f"Detector F1: {detector_metrics['f1']:.4f}")

        results[rate] = {
            "ccr": ccr,
            "mmlu_acc": mmlu_acc,
            "detector_f1": detector_metrics["f1"],
            "detector_precision": detector_metrics["precision"],
            "detector_recall": detector_metrics["recall"],
            "n_injected": len(injected_positions),
            "n_detected": len(detected)
        }

        ccr_values.append(ccr)
        mmlu_accs.append(mmlu_acc)
        f1_values.append(detector_metrics["f1"])

        if rate == cfg.injection_rates[-1]:
            plot_attribution_distribution(scores, [p for p in injected_positions if p < 1000], cfg.out_dir)

        del model
        torch.cuda.empty_cache()

    print("\n" + "=" * 60)
    print("Final Results")
    print("=" * 60)

    r2 = fit_ccr_regression(cfg.injection_rates, ccr_values)
    print(f"CCR R²: {r2:.4f}")

    monotonic = verify_mechanism_activation(ccr_values, cfg.injection_rates)

    min_f1 = f1_values[0]  # F1 at lowest injection rate (0.1%)
    print(f"Detector F1 @ {cfg.injection_rates[0]*100}%: {min_f1:.4f}")

    plot_ccr_scaling(cfg.injection_rates, ccr_values, r2, cfg.out_dir)
    plot_mmlu_vs_injection(cfg.injection_rates, mmlu_accs, cfg.out_dir)

    summary = {
        "injection_rates": cfg.injection_rates,
        "ccr_values": ccr_values,
        "mmlu_accs": mmlu_accs,
        "f1_values": f1_values,
        "r2": r2,
        "monotonic": monotonic,
        "f1_at_lowest_rate": min_f1,
        "per_rate_results": results,
        "gate_passed": r2 >= 0.9 and min_f1 > 0.8
    }

    with open(f"{cfg.out_dir}/results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {cfg.out_dir}/results.json")

    print("\n" + "=" * 60)
    print("GATE CHECK (MUST_WORK)")
    print("=" * 60)
    print(f"CCR R² ≥ 0.9: {r2:.4f} {'✓ PASS' if r2 >= 0.9 else '✗ FAIL'}")
    print(f"Detector F1 > 0.8 @ 0.1%: {min_f1:.4f} {'✓ PASS' if min_f1 > 0.8 else '✗ FAIL'}")
    print(f"Monotonic CCR: {'✓ PASS' if monotonic else '✗ FAIL'}")
    print(f"\nOVERALL: {'✓ GATE PASSED' if summary['gate_passed'] else '✗ GATE FAILED'}")

    return summary


if __name__ == "__main__":
    cfg = Config()
    run_all(cfg)
