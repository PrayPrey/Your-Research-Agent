#!/usr/bin/env python3
"""PoC run for H-M1 with reduced token budget (100M tokens/config vs 10B full)."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import M1_CONFIGS, TRAIN_CONFIG
from train.train_logged import build_model, train_with_history
from analysis.convergence import analyze_convergence
from analysis.figures import generate_all_figures

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'h-e1', 'code'))
from data.data_pipeline import build_dataset
from eval.evaluator import evaluate, compute_ensemble_score, save_results, load_results
from transformers import GPT2Tokenizer

POC_TOKENS = 100_000_000
POC_STEPS = POC_TOKENS // (TRAIN_CONFIG["batch_size"] * TRAIN_CONFIG["seq_len"])


def run_poc_config(config, base_dir: str, tokenizer) -> dict:
    """Run single config with PoC token budget."""
    config_id = config.config_id
    results_dir = os.path.join(base_dir, "results", config_id)
    ckpt_dir = os.path.join(base_dir, "checkpoints", config_id)
    os.makedirs(results_dir, exist_ok=True)

    benchmark_path = os.path.join(results_dir, "benchmark_results.json")
    loss_history_path = os.path.join(results_dir, "loss_history.json")

    if os.path.exists(benchmark_path) and os.path.exists(loss_history_path):
        print(f"[{config_id}] Already complete, loading from cache")
        scores = load_results(benchmark_path)
        with open(loss_history_path) as f:
            loss_history = json.load(f)
        return {
            "config_id": config_id,
            "scores": scores,
            "loss_history": loss_history,
            "checkpoint_path": os.path.join(ckpt_dir, "model"),
        }

    print(f"[{config_id}] Building dataset (PoC: {POC_TOKENS/1e6:.0f}M tokens)...")
    data = build_dataset(config, tokenizer, max_tokens=POC_TOKENS)

    print(f"[{config_id}] Training model (PoC: {POC_STEPS} steps)...")
    model = build_model()
    checkpoint_path, loss_history = train_with_history(
        model, data, ckpt_dir, config_id,
        batch_size=TRAIN_CONFIG["batch_size"],
        total_steps=POC_STEPS,
        log_interval=10,
    )

    with open(loss_history_path, "w") as f:
        json.dump(loss_history, f, indent=2)

    print(f"[{config_id}] Evaluating...")
    scores = evaluate(checkpoint_path)
    save_results(scores, benchmark_path)

    return {
        "config_id": config_id,
        "scores": scores,
        "loss_history": loss_history,
        "checkpoint_path": checkpoint_path,
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "results")
    figures_dir = os.path.join(base_dir, "figures")

    print("=" * 60)
    print(f"H-M1 PoC: Noise-Dilution Mechanism ({POC_TOKENS/1e6:.0f}M tokens/config)")
    print("=" * 60)

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    all_results = {}
    all_configs_path = os.path.join(results_dir, "all_configs.json")

    for config in M1_CONFIGS:
        result = run_poc_config(config, base_dir, tokenizer)
        all_results[result["config_id"]] = {
            "scores": result["scores"],
            "loss_history": result["loss_history"],
        }

        os.makedirs(os.path.dirname(all_configs_path), exist_ok=True)
        with open(all_configs_path, "w") as f:
            json.dump(all_results, f, indent=2)

    all_scores = {cid: r["scores"] for cid, r in all_results.items()}
    ensemble_scores = compute_ensemble_score(all_scores)
    for cid in all_results:
        all_results[cid]["ensemble_score"] = ensemble_scores.get(cid, 0.5)

    with open(all_configs_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n[Phase 2] Computing convergence metrics...")
    convergence_metrics = analyze_convergence(all_results)
    convergence_path = os.path.join(results_dir, "convergence_metrics.json")
    with open(convergence_path, "w") as f:
        json.dump(convergence_metrics, f, indent=2)

    print("\n[Phase 3] Generating figures...")
    generate_all_figures(results_dir, figures_dir)

    print("\n[Phase 4] Summary")
    print("-" * 40)

    p50_vs_p0 = convergence_metrics.get("p50_vs_p0", {})
    print(f"p50 vs p0 comparison:")
    print(f"  Cohen's d: {p50_vs_p0.get('cohens_d', 'N/A')}")
    print(f"  p-value: {p50_vs_p0.get('p_value', 'N/A')}")
    print(f"  mean_diff: {p50_vs_p0.get('mean_diff', 'N/A')}")

    for cfg in sorted(k for k in convergence_metrics.keys() if k.startswith("M1-")):
        m = convergence_metrics[cfg]
        print(f"  {cfg}: final_loss={m['final_loss']:.4f}, auc={m['convergence_auc']:.2e}")

    faster_convergence = False
    higher_benchmark = False

    if "M1-C3" in all_results and "M1-C0" in all_results:
        c3_auc = convergence_metrics["M1-C3"]["convergence_auc"]
        c0_auc = convergence_metrics["M1-C0"]["convergence_auc"]
        faster_convergence = c3_auc < c0_auc
        print(f"\nC3 (p50) AUC < C0 (no filter) AUC: {faster_convergence}")

        c3_score = all_results["M1-C3"]["ensemble_score"]
        c0_score = all_results["M1-C0"]["ensemble_score"]
        c6_score = all_results["M1-C6"]["ensemble_score"]
        higher_benchmark = c3_score > c0_score and c3_score > c6_score
        print(f"C3 ensemble > both extremes: {higher_benchmark}")

    gate_pass = faster_convergence and higher_benchmark
    print(f"\n*** GATE VERDICT: {'PASS' if gate_pass else 'FAIL'} ***")
    print("=" * 60)

    return gate_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
