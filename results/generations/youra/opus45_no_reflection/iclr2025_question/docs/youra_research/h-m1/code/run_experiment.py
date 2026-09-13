#!/usr/bin/env python
"""H-M1: Hook Non-Intrusiveness Verification Experiment.

Verifies that forward hooks do not alter generation output.
Gate: 100% output identity + <10% overhead.
"""

import os
import sys
import json
import time
import torch
import matplotlib.pyplot as plt
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CFG, set_seed
from data import load_triviaqa_subset, format_prompt
from hooks import HiddenStateExtractor
from verify import check_output_identity, compute_overhead_pct, profile_memory, gate_check


def generate_baseline(model, tokenizer, prompts: list, max_new_tokens: int = 128):
    """Generate without hooks. Returns (decoded_outputs, elapsed_seconds, per_sample_times)."""
    outputs = []
    per_sample_times = []
    t_total_start = time.perf_counter()

    for prompt in tqdm(prompts, desc="Baseline generation"):
        t0 = time.perf_counter()
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        outputs.append(decoded)
        per_sample_times.append(time.perf_counter() - t0)

    elapsed = time.perf_counter() - t_total_start
    return outputs, elapsed, per_sample_times


def generate_hooked(model, tokenizer, prompts: list, max_new_tokens: int = 128, layer_idx: int = 19):
    """Generate with hooks. Returns (decoded_outputs, elapsed_seconds, per_sample_times)."""
    outputs = []
    per_sample_times = []
    t_total_start = time.perf_counter()

    with HiddenStateExtractor(model, [layer_idx]) as extractor:
        for prompt in tqdm(prompts, desc="Hooked generation"):
            t0 = time.perf_counter()
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                output_ids = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            outputs.append(decoded)
            per_sample_times.append(time.perf_counter() - t0)

    elapsed = time.perf_counter() - t_total_start
    return outputs, elapsed, per_sample_times


def plot_gate_metrics(identity_rate: float, overhead_pct: float, cfg, save_path: str):
    """Bar chart: identity rate vs 100% target, overhead vs 10% target."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Identity rate
    ax1 = axes[0]
    ax1.bar(["Identity Rate", "Target"], [identity_rate * 100, 100], color=["#2ecc71", "#95a5a6"])
    ax1.axhline(y=100, color="red", linestyle="--", label="Required: 100%")
    ax1.set_ylabel("Percentage (%)")
    ax1.set_title("Output Identity Rate")
    ax1.set_ylim(0, 110)
    ax1.legend()

    # Overhead
    ax2 = axes[1]
    color = "#2ecc71" if overhead_pct < 10 else "#e74c3c"
    ax2.bar(["Overhead", "Threshold"], [overhead_pct, 10], color=[color, "#95a5a6"])
    ax2.axhline(y=10, color="red", linestyle="--", label="Max allowed: 10%")
    ax2.set_ylabel("Percentage (%)")
    ax2.set_title("Inference Time Overhead")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_time_histogram(times_without: list, times_with: list, save_path: str):
    """Histogram comparing per-sample inference times."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(times_without, bins=30, alpha=0.6, label="Without hooks", color="#3498db")
    ax.hist(times_with, bins=30, alpha=0.6, label="With hooks", color="#e74c3c")
    ax.set_xlabel("Time per sample (seconds)")
    ax.set_ylabel("Frequency")
    ax.set_title("Inference Time Distribution: With vs Without Hooks")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_memory_profile(mem_stats: dict, save_path: str):
    """Bar chart of memory usage."""
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["GPU Peak (MB)", "CPU Tensor (MB)"]
    values = [mem_stats["gpu_peak_mb"], mem_stats["cpu_tensor_mb"]]
    ax.bar(labels, values, color=["#3498db", "#2ecc71"])
    ax.set_ylabel("Memory (MB)")
    ax.set_title("Memory Profile with Hooks")
    for i, v in enumerate(values):
        ax.text(i, v + 0.5, f"{v:.1f}", ha="center")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def main():
    set_seed(CFG.seed)

    code_dir = os.path.dirname(os.path.abspath(__file__))
    hypothesis_dir = os.path.dirname(code_dir)
    figures_dir = os.path.join(hypothesis_dir, "figures")
    outputs_dir = os.path.join(code_dir, "outputs")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    print(f"Loading model: {CFG.model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        CFG.model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(CFG.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading TriviaQA subset ({CFG.n_samples} samples)...")
    dataset = load_triviaqa_subset(CFG.n_samples)
    prompts = [format_prompt(ex) for ex in dataset]

    print(f"\nPhase 1: Baseline generation (no hooks)...")
    outputs_without, time_without, times_without = generate_baseline(
        model, tokenizer, prompts, CFG.max_new_tokens
    )
    print(f"Baseline: {len(outputs_without)} outputs in {time_without:.2f}s")

    print(f"\nPhase 2: Hooked generation (layer {CFG.target_layer})...")
    outputs_with, time_with, times_with = generate_hooked(
        model, tokenizer, prompts, CFG.max_new_tokens, CFG.target_layer
    )
    print(f"Hooked: {len(outputs_with)} outputs in {time_with:.2f}s")

    print("\nVerifying output identity...")
    identity_rate, mismatches = check_output_identity(outputs_without, outputs_with)
    overhead_pct = compute_overhead_pct(time_without, time_with)

    print(f"\nProfiling memory...")
    mem_stats = profile_memory(model, tokenizer, prompts[0], CFG.target_layer)

    gate_passed = gate_check(identity_rate, overhead_pct, CFG)

    print(f"\n{'='*60}")
    print(f"RESULTS - H-M1 Hook Non-Intrusiveness Verification")
    print(f"{'='*60}")
    print(f"Output Identity Rate: {identity_rate*100:.2f}% (target: 100%)")
    print(f"Mismatches: {len(mismatches)} / {CFG.n_samples}")
    if mismatches:
        print(f"First 5 mismatch indices: {mismatches[:5]}")
    print(f"Inference Overhead: {overhead_pct:.2f}% (max allowed: 10%)")
    print(f"Time without hooks: {time_without:.2f}s")
    print(f"Time with hooks: {time_with:.2f}s")
    print(f"GPU Peak Memory: {mem_stats['gpu_peak_mb']:.1f} MB")
    print(f"CPU Tensor Memory: {mem_stats['cpu_tensor_mb']:.1f} MB")
    print(f"{'='*60}")
    print(f"GATE: {'PASS' if gate_passed else 'FAIL'}")
    print(f"{'='*60}")

    print("\nGenerating figures...")
    plot_gate_metrics(
        identity_rate, overhead_pct, CFG,
        os.path.join(figures_dir, "gate_metrics.png")
    )
    plot_time_histogram(
        times_without, times_with,
        os.path.join(figures_dir, "time_histogram.png")
    )
    plot_memory_profile(
        mem_stats,
        os.path.join(figures_dir, "memory_profile.png")
    )

    results = {
        "hypothesis_id": "h-m1",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_name": CFG.model_name,
            "target_layer": CFG.target_layer,
            "n_samples": CFG.n_samples,
            "max_new_tokens": CFG.max_new_tokens,
            "seed": CFG.seed
        },
        "metrics": {
            "identity_rate": float(identity_rate),
            "mismatch_count": len(mismatches),
            "overhead_pct": float(overhead_pct),
            "time_without_hooks_s": float(time_without),
            "time_with_hooks_s": float(time_with),
            "gpu_peak_mb": float(mem_stats["gpu_peak_mb"]),
            "cpu_tensor_mb": float(mem_stats["cpu_tensor_mb"])
        },
        "gate": {
            "type": "MUST_WORK",
            "condition": "identity_rate == 1.0 AND overhead_pct < 10.0",
            "satisfied": gate_passed,
            "result": "PASS" if gate_passed else "FAIL"
        },
        "mismatches": mismatches[:20] if mismatches else [],
        "figures": [
            "figures/gate_metrics.png",
            "figures/time_histogram.png",
            "figures/memory_profile.png"
        ]
    }

    results_path = os.path.join(hypothesis_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    csv_path = os.path.join(outputs_dir, "results.csv")
    with open(csv_path, "w") as f:
        f.write("sample_idx,time_without_hook,time_with_hook,match\n")
        for i, (tw, th) in enumerate(zip(times_without, times_with)):
            match = 1 if i not in mismatches else 0
            f.write(f"{i},{tw:.6f},{th:.6f},{match}\n")
    print(f"Per-sample results saved to: {csv_path}")

    return results


if __name__ == "__main__":
    results = main()
    print("\nExperiment completed.")
