"""H-M3 top-level experiment orchestrator: stream 1 → 2 → 3 → gate → report."""
import os
import sys
import argparse
import json
import numpy as np
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import ExperimentConfig
from data_utils import load_sparsity_profiles, load_tokenizer
from lora_trainer import train_uniform_lora
from sensitivity_sweep import (
    run_all_sensitivity_sweeps, identify_sensitive_layers, check_delta_r_fallback
)
from adalora_runner import run_all_adalora, rank_pattern_to_array
from spectral_analysis import compute_all_spectral_decays, run_multiple_regression
from correlation_analysis import compute_pearson_r, compute_kendall_tau, evaluate_gate
from visualize import generate_all_figures
from results_logger import save_results_json, generate_validation_report, print_gate_summary


def run_stream1_reference(cfg: ExperimentConfig) -> dict:
    """Run uniform r=16 LoRA baseline: 2 tasks × 5 seeds = 10 runs."""
    print("\n" + "=" * 60)
    print("[STREAM 1] Starting reference training (uniform LoRA)")
    print("=" * 60)

    tokenizer = load_tokenizer(cfg)
    baseline_accs = {task: {} for task in cfg.tasks}
    all_delta_w = {task: {} for task in cfg.tasks}
    all_grad_norms = {task: {} for task in cfg.tasks}

    for task in cfg.tasks:
        import gc
        gc.collect()
        torch.cuda.empty_cache()
        print(f"\n[STREAM 1] Task: {task}")
        for seed in cfg.seeds:
            print(f"[STREAM 1] task={task}, seed={seed}")
            result = train_uniform_lora(
                task=task, seed=seed, cfg=cfg,
                return_delta_w=True, return_grad_norms=True,
                tokenizer=tokenizer,
            )
            baseline_accs[task][seed] = result["accuracy"]
            all_delta_w[task][seed] = result["delta_w"]
            all_grad_norms[task][seed] = result["grad_norms"]
            print(f"[STREAM 1] task={task}, seed={seed}, accuracy={result['accuracy']:.4f}")

    # Aggregate across seeds
    mean_baseline = {task: np.mean(list(baseline_accs[task].values())) for task in cfg.tasks}
    print(f"\n[STREAM 1] Mean baseline accuracy: {mean_baseline}")

    return {
        "baseline_accs": baseline_accs,
        "mean_baseline": mean_baseline,
        "delta_w": all_delta_w,
        "grad_norms": all_grad_norms,
    }


def run_stream1_sweep(cfg: ExperimentConfig, stream1_ref: dict) -> dict:
    """Run joint rank sensitivity sweep: 32 × 2 × 5 = 320 runs."""
    print("\n" + "=" * 60)
    print("[STREAM 1] Starting sensitivity sweep (320 runs)")
    print("=" * 60)

    baseline_accs = stream1_ref["baseline_accs"]
    accuracy_drops = run_all_sensitivity_sweeps(cfg, baseline_accs)

    # Check fallback for SST-2
    sst2_drops = accuracy_drops.get("sst2", np.zeros(cfg.n_layers))
    new_delta_r = check_delta_r_fallback(sst2_drops, cfg.sensitive_drop_threshold, cfg)

    if new_delta_r != cfg.delta_r:
        print(f"[SWEEP] Fallback triggered: re-running sweep with delta_r={new_delta_r}")
        cfg.delta_r = new_delta_r
        accuracy_drops = run_all_sensitivity_sweeps(cfg, baseline_accs)

    sensitive_masks = {
        task: identify_sensitive_layers(drops, cfg.sensitive_drop_threshold)
        for task, drops in accuracy_drops.items()
    }

    return {
        "accuracy_drops": accuracy_drops,
        "sensitive_masks": sensitive_masks,
        "delta_r_used": cfg.delta_r,
    }


def run_stream2(cfg: ExperimentConfig) -> dict:
    """Run AdaLoRA reference: 2 tasks × 5 seeds = 10 runs."""
    print("\n" + "=" * 60)
    print("[STREAM 2] Starting AdaLoRA reference runs")
    print("=" * 60)

    adalora_ranks = run_all_adalora(cfg)
    return {"adalora_ranks": adalora_ranks}


def run_stream3(cfg: ExperimentConfig, stream1_ref: dict) -> dict:
    """Spectral analysis + multiple regression on ΔW from stream 1."""
    print("\n" + "=" * 60)
    print("[STREAM 3] Starting spectral analysis")
    print("=" * 60)

    # Use first task's delta_w for spectral analysis (averaged over seeds)
    delta_w_combined = {}
    for task in cfg.tasks:
        delta_w_by_seed = stream1_ref["delta_w"].get(task, {})
        if delta_w_by_seed:
            first_seed = list(delta_w_by_seed.keys())[0]
            delta_w_combined = delta_w_by_seed[first_seed]
            break

    spectral_decay = compute_all_spectral_decays(delta_w_combined, cfg)

    # Compute per-layer grad norms (average over tasks and seeds, MLP layers)
    import re
    layer_grad_norms = np.zeros(cfg.n_layers)
    layer_counts = np.zeros(cfg.n_layers)
    mlp_keys = {"gate_proj", "up_proj", "down_proj"}

    for task in cfg.tasks:
        for seed, grad_norms in stream1_ref["grad_norms"].get(task, {}).items():
            for key, val in grad_norms.items():
                m = re.search(r"layers\.(\d+)\.", key)
                if m and any(mk in key for mk in mlp_keys):
                    l = int(m.group(1))
                    if l < cfg.n_layers:
                        layer_grad_norms[l] += val
                        layer_counts[l] += 1

    layer_counts = np.where(layer_counts > 0, layer_counts, 1)
    layer_grad_norms = layer_grad_norms / layer_counts

    sparsity = load_sparsity_profiles(cfg.h_m2_results_path)
    regression_results = run_multiple_regression(sparsity, layer_grad_norms, spectral_decay)

    print(f"[STREAM 3] r2_full={regression_results['r2_full']:.4f}, "
          f"unique_var_sparsity={regression_results['unique_var_sparsity']:.4f}, "
          f"p_value={regression_results['p_value_sparsity_beta']:.4f}")

    return {
        "spectral_decay": spectral_decay,
        "grad_norms_array": layer_grad_norms,
        "regression_results": regression_results,
        "sparsity": sparsity,
    }


def main():
    parser = argparse.ArgumentParser(description="H-M3 Sparsity-Rank Sensitivity Experiment")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--seeds", type=str, default=None)
    parser.add_argument("--num_epochs", type=int, default=None)
    parser.add_argument("--delta_r", type=int, default=None)
    args = parser.parse_args()

    if os.path.exists(args.config):
        cfg = ExperimentConfig.from_yaml(args.config)
    else:
        cfg = ExperimentConfig()
        print(f"[WARN] config.yaml not found at {args.config}, using defaults")

    if args.seeds:
        cfg.seeds = json.loads(args.seeds)
    if args.num_epochs:
        cfg.num_epochs = args.num_epochs
    if args.delta_r:
        cfg.delta_r = args.delta_r

    os.makedirs(cfg.figures_dir, exist_ok=True)

    # Set CUDA device
    cuda_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "0")
    print(f"[INIT] CUDA_VISIBLE_DEVICES={cuda_devices}")
    print(f"[INIT] PyTorch CUDA available: {torch.cuda.is_available()}")
    print(f"[INIT] Seeds: {cfg.seeds}, Epochs: {cfg.num_epochs}, Tasks: {cfg.tasks}")

    # Load sparsity profiles from H-M2
    sparsity = load_sparsity_profiles(cfg.h_m2_results_path)
    print(f"[INIT] Loaded sparsity profiles: shape={sparsity.shape}, mean={sparsity.mean():.4f}")

    # Stream 1: Reference training + sweep
    stream1_ref = run_stream1_reference(cfg)
    stream1_sweep = run_stream1_sweep(cfg, stream1_ref)

    # Stream 2: AdaLoRA
    stream2 = run_stream2(cfg)

    # Stream 3: Spectral analysis
    stream3 = run_stream3(cfg, stream1_ref)

    # Correlation analysis
    print("\n" + "=" * 60)
    print("[CORRELATION] Computing Pearson r and Kendall tau")
    print("=" * 60)

    accuracy_drops = stream1_sweep["accuracy_drops"]
    sensitive_masks = stream1_sweep["sensitive_masks"]
    adalora_ranks = stream2["adalora_ranks"]

    pearson_results = {}
    for task in cfg.tasks:
        r, p = compute_pearson_r(
            sparsity,
            accuracy_drops.get(task, np.zeros(cfg.n_layers)),
            sensitive_masks.get(task, np.zeros(cfg.n_layers, dtype=bool)),
        )
        pearson_results[task] = {"r": r, "p": p}
        print(f"[CORR] Pearson r ({task}): r={r:.4f}, p={p:.4f}")

    tau_results = {}
    for task in cfg.tasks:
        tau, p_tau = compute_kendall_tau(
            sparsity,
            adalora_ranks.get(task, np.zeros(cfg.n_layers)),
        )
        tau_results[task] = {"tau": tau, "p": p_tau}
        print(f"[CORR] Kendall tau ({task}): tau={tau:.4f}, p={p_tau:.4f}")

    n_sensitive_sst2 = int(sensitive_masks.get("sst2", np.zeros(cfg.n_layers, dtype=bool)).sum())

    # Gate evaluation
    gate_result = evaluate_gate(
        pearson_r_sst2=pearson_results.get("sst2", {}).get("r", float("nan")),
        pearson_r_mnli=pearson_results.get("mnli", {}).get("r", float("nan")),
        kendall_tau_sst2=tau_results.get("sst2", {}).get("tau", float("nan")),
        kendall_tau_mnli=tau_results.get("mnli", {}).get("tau", float("nan")),
        unique_var_sparsity=stream3["regression_results"]["unique_var_sparsity"],
        p_value_sparsity_beta=stream3["regression_results"]["p_value_sparsity_beta"],
        n_sensitive_sst2=n_sensitive_sst2,
        cfg=cfg,
    )
    print_gate_summary(gate_result)

    # Aggregate results
    results = {
        "sparsity": sparsity,
        "baseline_accs": {
            task: {
                "mean": float(np.mean(list(stream1_ref["baseline_accs"][task].values()))),
                "by_seed": {str(k): v for k, v in stream1_ref["baseline_accs"][task].items()}
            }
            for task in cfg.tasks
        },
        "accuracy_drops": accuracy_drops,
        "sensitive_masks": sensitive_masks,
        "adalora_ranks": adalora_ranks,
        "spectral_decay": stream3["spectral_decay"],
        "grad_norms_array": stream3["grad_norms_array"],
        "regression_results": stream3["regression_results"],
        "pearson_results": pearson_results,
        "tau_results": tau_results,
        "gate_result": gate_result,
        "n_sensitive_sst2": n_sensitive_sst2,
        "delta_r_used": stream1_sweep.get("delta_r_used", cfg.delta_r),
    }

    # Visualize
    generate_all_figures(results, cfg)

    # Save results
    save_results_json(results, cfg.results_path)

    # Generate validation report
    generate_validation_report(results, gate_result, cfg, cfg.validation_report_path)

    print(f"\n[DONE] Gate result: {'PASS' if gate_result['gate_pass'] else 'FAIL'}")
    print(f"[DONE] Validation report: {cfg.validation_report_path}")
    print(f"[DONE] Results JSON: {cfg.results_path}")

    return gate_result


if __name__ == "__main__":
    main()
