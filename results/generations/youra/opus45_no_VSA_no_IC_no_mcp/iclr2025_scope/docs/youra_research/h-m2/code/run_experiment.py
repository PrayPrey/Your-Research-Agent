#!/usr/bin/env python3
"""H-M2 Experiment: Low-rank task conditioning overhead measurement."""

import json
import sys
import torch
import numpy as np
from datetime import datetime

sys.path.insert(0, ".")

from config import TCSSMConfig, ExperimentConfig, MeasurementConfig, AblationConfig
from models import VanillaMambaWrapper, TaskConditionedMamba
from analysis import measure_overhead, per_matrix_breakdown, measure_state_variance
from ablation import run_rank_ablation, run_matrix_ablation
from visualize import (
    plot_overhead_bar,
    plot_rank_ablation,
    plot_state_variance_heatmap,
    plot_matrix_breakdown,
)


def generate_synthetic_task_embeddings(num_tasks: int, task_emb_dim: int, batch_size: int, device: str):
    """Generate distinct task embeddings for each task (simulating H-M1 output)."""
    embeddings = []
    for i in range(num_tasks):
        base = torch.randn(1, task_emb_dim, device=device) * 0.1
        base[:, :task_emb_dim // num_tasks] += (i + 1) * 2.0
        emb = base.expand(batch_size, -1).clone()
        embeddings.append(emb)
    return embeddings


def main():
    print("=" * 60)
    print("H-M2: Low-Rank Task Conditioning Overhead Experiment")
    print("=" * 60)

    tc_cfg = TCSSMConfig()
    exp_cfg = ExperimentConfig()
    meas_cfg = MeasurementConfig()
    abl_cfg = AblationConfig()

    device = meas_cfg.device if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    torch.manual_seed(exp_cfg.seed)
    np.random.seed(exp_cfg.seed)

    batch_size = 8
    seq_len = 128
    d_model = tc_cfg.d_model
    d_state = tc_cfg.d_state
    task_emb_dim = tc_cfg.task_emb_dim

    print(f"\nConfig: d_model={d_model}, d_state={d_state}, rank={tc_cfg.rank}")
    print(f"Batch={batch_size}, SeqLen={seq_len}, Samples/Task={exp_cfg.samples_per_task}")

    inputs = torch.randn(batch_size, seq_len, d_model, device=device)

    num_tasks = len(exp_cfg.tasks)
    task_embeddings_list = generate_synthetic_task_embeddings(
        num_tasks, task_emb_dim, batch_size, device
    )
    print(f"Tasks: {exp_cfg.tasks}")

    print("\n--- Building Models ---")
    vanilla = VanillaMambaWrapper(d_model, d_state).to(device).eval()
    tc_model = TaskConditionedMamba(
        d_model, d_state, task_emb_dim, rank=tc_cfg.rank, variant=tc_cfg.modulation_target
    ).to(device).eval()

    vanilla_params = sum(p.numel() for p in vanilla.parameters())
    tc_params = sum(p.numel() for p in tc_model.parameters())
    print(f"Vanilla params: {vanilla_params:,}")
    print(f"TC-SSM params: {tc_params:,} ({tc_params/vanilla_params:.2f}x)")

    print("\n--- Measuring Overhead (default config) ---")
    with torch.no_grad():
        overhead = measure_overhead(
            vanilla, tc_model, inputs, task_embeddings_list[0],
            n_warmup=exp_cfg.warmup_iters, n_iters=exp_cfg.measure_iters
        )
    print(f"Overhead ratio: {overhead:.4f}x")
    overhead_pass = overhead < meas_cfg.overhead_threshold
    print(f"Gate check (overhead < {meas_cfg.overhead_threshold}x): {'PASS' if overhead_pass else 'FAIL'}")

    print("\n--- Measuring State Variance (ANOVA) ---")
    with torch.no_grad():
        variance_result = measure_state_variance(tc_model, inputs, task_embeddings_list)
    print(f"State variances: {[f'{v:.4f}' for v in variance_result['state_variances']]}")
    print(f"F-statistic: {variance_result['f_statistic']:.4f}")
    print(f"p-value: {variance_result['p_value']:.6f}")
    variance_pass = variance_result["significant"]
    print(f"Gate check (p < {meas_cfg.significance_level}): {'PASS' if variance_pass else 'FAIL'}")

    print("\n--- Per-Matrix Breakdown ---")
    breakdown = per_matrix_breakdown(tc_model, inputs, task_embeddings_list[0])
    for k, v in breakdown.items():
        print(f"  {k}: {v:.4f}s")

    print("\n--- Rank Ablation ---")
    rank_results = run_rank_ablation(
        abl_cfg.ranks, d_model, d_state, task_emb_dim, inputs, task_embeddings_list
    )

    print("\n--- Matrix Ablation ---")
    matrix_results = run_matrix_ablation(
        abl_cfg.modulation_targets, d_model, d_state, task_emb_dim,
        tc_cfg.rank, inputs, task_embeddings_list[0]
    )

    print("\n--- Generating Figures ---")
    fig_dir = "figures"
    plot_overhead_bar(overhead, save_path=f"{fig_dir}/overhead_bar.png")
    plot_rank_ablation(rank_results, save_path=f"{fig_dir}/rank_ablation.png")
    plot_state_variance_heatmap(
        exp_cfg.tasks, variance_result["state_variances"],
        save_path=f"{fig_dir}/state_variance.png"
    )
    plot_matrix_breakdown(breakdown, save_path=f"{fig_dir}/matrix_breakdown.png")
    print("Figures saved to figures/")

    print("\n" + "=" * 60)
    print("FINAL GATE CHECK")
    print("=" * 60)
    print(f"  1. Overhead < {meas_cfg.overhead_threshold}x: {overhead:.4f}x -> {'PASS' if overhead_pass else 'FAIL'}")
    print(f"  2. State variance p < {meas_cfg.significance_level}: {variance_result['p_value']:.6f} -> {'PASS' if variance_pass else 'FAIL'}")

    gate_pass = overhead_pass and variance_pass
    gate_result = "PASS" if gate_pass else "FAIL"
    print(f"\n  GATE RESULT: {gate_result}")
    print("=" * 60)

    results = {
        "hypothesis": "h-m2",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "d_model": d_model,
            "d_state": d_state,
            "rank": tc_cfg.rank,
            "modulation_target": tc_cfg.modulation_target,
            "batch_size": batch_size,
            "seq_len": seq_len,
        },
        "results": {
            "overhead_ratio": overhead,
            "overhead_threshold": meas_cfg.overhead_threshold,
            "overhead_pass": overhead_pass,
            "state_variance": variance_result,
            "variance_pass": variance_pass,
            "rank_ablation": {str(k): v for k, v in rank_results.items()},
            "matrix_ablation": matrix_results,
        },
        "gate_result": gate_result,
    }

    with open("experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to experiment_results.json")

    return gate_result


if __name__ == "__main__":
    result = main()
    print(f"\nEXPERIMENT COMPLETE (result={result})")
