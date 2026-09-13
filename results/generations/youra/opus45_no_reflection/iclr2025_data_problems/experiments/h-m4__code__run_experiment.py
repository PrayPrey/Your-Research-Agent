#!/usr/bin/env python3
"""H-M4 Experiment: Pareto Curve Analysis - Architecture-Approximation Interaction.

Runs budget sweeps for EK-FAC/TracIn/TRAK across BERT and GPT-2, generating
Pareto curves and evaluating P1/P2/P3 predictions with statistical tests.
"""

import os
import sys
import json
import yaml
import time
import torch
import numpy as np
from datetime import datetime

from config import ExperimentConfig, GATE_CONFIG, FIGURE_FILES, PLOT_CONFIG
from data_loader import load_sst2_splits, build_dataloader
from models import load_bert_classifier, load_gpt2_classifier
from finetune import finetune_with_checkpoints, load_checkpoint
from mislabel import inject_mislabels, save_mislabeled_indices, load_mislabeled_indices
from ekfac_attribution import compute_ekfac_scores_simple
from tracin_attribution import compute_tracin_scores
from trak_attribution import compute_trak_scores_simple
from metrics import compute_mislabeled_auc
from stats import aggregate_seed_results, evaluate_predictions, paired_ttest_across_seeds
from visualize import (plot_pareto_frontier_grid, plot_arch_comparison_per_method,
                        plot_auc_vs_projdim, plot_auc_bar_fixed_budget)

def run_budget_sweep_ekfac(model, train_loader, query_loader, device, budgets, n_train, n_query):
    """Run EK-FAC at multiple projection dimensions. Returns {budget: (auc, time)}."""
    results = {}
    for proj_dim in budgets:
        print(f"  EK-FAC proj_dim={proj_dim}...")
        t0 = time.time()
        scores = compute_ekfac_scores_simple(model, train_loader, query_loader, device,
                                              n_train_sample=n_train, n_query_sample=n_query)
        elapsed = time.time() - t0
        results[proj_dim] = (scores, elapsed)
        print(f"    Time: {elapsed:.2f}s, Shape: {scores.shape}")
    return results

def run_budget_sweep_tracin(model, ckpt_paths, query_loader, train_loader, lr, device,
                             budget_to_ckpt_count, n_train, n_query):
    """Run TracIn with varying checkpoint counts. Returns {budget: (auc, time)}."""
    results = {}
    for budget, n_ckpt in budget_to_ckpt_count.items():
        print(f"  TracIn budget={budget} (n_ckpts={n_ckpt})...")
        ckpts_subset = ckpt_paths[:n_ckpt]
        t0 = time.time()
        scores = compute_tracin_scores(model, ckpts_subset, query_loader, train_loader,
                                        lr, device, n_train_sample=n_train, n_query_sample=n_query)
        elapsed = time.time() - t0
        results[budget] = (scores, elapsed)
        print(f"    Time: {elapsed:.2f}s, Shape: {scores.shape}")
    return results

def run_budget_sweep_trak(model, train_loader, query_loader, device, budgets, seed, n_train, n_query):
    """Run TRAK at multiple projection dimensions. Returns {budget: (auc, time)}."""
    results = {}
    for proj_dim in budgets:
        print(f"  TRAK proj_dim={proj_dim}...")
        t0 = time.time()
        scores = compute_trak_scores_simple(model, train_loader, query_loader, proj_dim,
                                             seed, device, n_train_sample=n_train, n_query_sample=n_query)
        elapsed = time.time() - t0
        results[proj_dim] = (scores, elapsed)
        print(f"    Time: {elapsed:.2f}s, Shape: {scores.shape}")
    return results

def main():
    cfg = ExperimentConfig()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"H-M4 Pareto Curve Experiment")
    print(f"Device: {device}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Budgets: {cfg.compute_budgets}")

    os.makedirs(cfg.checkpoints_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print("\nLoading SST-2 dataset...")
    train_texts, train_labels, val_texts, val_labels = load_sst2_splits()
    n_train = len(train_texts)
    n_val = len(val_texts)
    print(f"Train: {n_train}, Val: {n_val}")

    per_seed_results = []

    for seed_idx, seed in enumerate(cfg.seeds):
        print(f"\n{'='*70}")
        print(f"SEED {seed} ({seed_idx+1}/{len(cfg.seeds)})")
        print(f"{'='*70}")

        mislabel_path = os.path.join(cfg.output_dir, f"mislabeled_indices_seed{seed}.json")
        if os.path.exists(mislabel_path):
            mislabeled_indices = load_mislabeled_indices(mislabel_path)
            train_labels_flipped = list(train_labels)
            for idx in mislabeled_indices:
                train_labels_flipped[idx] = 1 - train_labels_flipped[idx]
        else:
            train_labels_flipped, mislabeled_indices = inject_mislabels(
                list(train_labels), cfg.mislabel_fraction, seed
            )
            save_mislabeled_indices(mislabeled_indices, mislabel_path)
        print(f"Mislabeled samples: {len(mislabeled_indices)}")

        seed_result = {"ekfac": {"bert": {}, "gpt2": {}},
                       "tracin": {"bert": {}, "gpt2": {}},
                       "trak": {"bert": {}, "gpt2": {}}}

        for arch in cfg.architectures:
            print(f"\n--- {arch.upper()} ---")

            if arch == "bert":
                model, tokenizer = load_bert_classifier(cfg.bert_model_id)
            else:
                model, tokenizer = load_gpt2_classifier(cfg.gpt2_model_id)

            train_loader = build_dataloader(tokenizer, train_texts, train_labels_flipped,
                                             cfg.train_batch_size, cfg.max_length, shuffle=False)
            val_loader = build_dataloader(tokenizer, val_texts, val_labels,
                                           cfg.train_batch_size, cfg.max_length, shuffle=False)

            ckpt_prefix = f"{arch}_sst2_seed{seed}"
            ckpt_paths = [os.path.join(cfg.checkpoints_dir, f"{ckpt_prefix}_epoch{i}.pt")
                          for i in [1, 2, 3]]

            if all(os.path.exists(c) for c in ckpt_paths):
                print(f"Loading {arch} checkpoints...")
                model = load_checkpoint(model, ckpt_paths[-1], device)
            else:
                print(f"Fine-tuning {arch} seed {seed}...")
                ckpt_paths = finetune_with_checkpoints(
                    model, train_loader, cfg.epochs, cfg.lr, device,
                    cfg.checkpoints_dir, ckpt_prefix
                )

            model = model.to(device)
            model.eval()

            print(f"\n[{arch}] EK-FAC Budget Sweep...")
            ekfac_results = run_budget_sweep_ekfac(
                model, train_loader, val_loader, device, cfg.compute_budgets,
                cfg.n_train_sample, cfg.n_query_sample
            )
            for budget, (scores, elapsed) in ekfac_results.items():
                auc = compute_mislabeled_auc(scores, mislabeled_indices, n_train)
                seed_result["ekfac"][arch][budget] = {"auc": auc, "time": elapsed}
                print(f"    Budget {budget}: AUC={auc:.4f}, Time={elapsed:.2f}s")

            print(f"\n[{arch}] TracIn Budget Sweep...")
            tracin_results = run_budget_sweep_tracin(
                model, ckpt_paths, val_loader, train_loader, cfg.lr, device,
                cfg.tracin_checkpoint_counts, cfg.n_train_sample, cfg.n_query_sample
            )
            for budget, (scores, elapsed) in tracin_results.items():
                auc = compute_mislabeled_auc(scores, mislabeled_indices, n_train)
                seed_result["tracin"][arch][budget] = {"auc": auc, "time": elapsed}
                print(f"    Budget {budget}: AUC={auc:.4f}, Time={elapsed:.2f}s")

            print(f"\n[{arch}] TRAK Budget Sweep...")
            trak_results = run_budget_sweep_trak(
                model, train_loader, val_loader, device, cfg.compute_budgets,
                seed, cfg.n_train_sample, cfg.n_query_sample
            )
            for budget, (scores, elapsed) in trak_results.items():
                auc = compute_mislabeled_auc(scores, mislabeled_indices, n_train)
                seed_result["trak"][arch][budget] = {"auc": auc, "time": elapsed}
                print(f"    Budget {budget}: AUC={auc:.4f}, Time={elapsed:.2f}s")

            del model
            torch.cuda.empty_cache()

        per_seed_results.append(seed_result)

    print("\n" + "="*70)
    print("AGGREGATING RESULTS ACROSS SEEDS")
    print("="*70)

    agg_results = aggregate_seed_results(per_seed_results)
    predictions = evaluate_predictions(agg_results, per_seed_results, cfg.alpha, cfg.trak_invariance_threshold)

    print("\nPrediction Evaluation:")
    for pred_key, budgets in predictions["predictions"].items():
        print(f"\n{pred_key}:")
        for budget, data in budgets.items():
            status = "CONFIRMED" if data["confirmed"] else "NOT CONFIRMED"
            print(f"  Budget {budget}: {status} (diff={data['diff']:.4f}, p={data['p_value']:.4f})")

    print(f"\nAny prediction confirmed: {predictions['any_confirmed']}")

    print("\nGenerating figures...")
    plot_pareto_frontier_grid(agg_results, os.path.join(cfg.figures_dir, FIGURE_FILES["pareto_frontier_grid"]))
    for method in cfg.methods:
        plot_arch_comparison_per_method(agg_results, method,
                                         os.path.join(cfg.figures_dir, f"arch_comparison_{method}.png"))
    plot_auc_vs_projdim(agg_results, os.path.join(cfg.figures_dir, FIGURE_FILES["auc_vs_projdim"]))
    plot_auc_bar_fixed_budget(agg_results, PLOT_CONFIG["fixed_budget_for_bar_chart"],
                               os.path.join(cfg.figures_dir, FIGURE_FILES["auc_bar_fixed_budget"]))
    print("Figures saved.")

    gate_pass = predictions["any_confirmed"]

    final_results = {
        "hypothesis_id": "h-m4",
        "timestamp": datetime.now().isoformat(),
        "aggregated_results": agg_results,
        "predictions": predictions,
        "gate_result": {
            "type": GATE_CONFIG["type"],
            "pass": gate_pass,
            "any_confirmed": predictions["any_confirmed"],
        },
        "per_seed_results": per_seed_results,
        "config": {
            "seeds": cfg.seeds,
            "compute_budgets": cfg.compute_budgets,
            "n_train_sample": cfg.n_train_sample,
            "n_query_sample": cfg.n_query_sample,
            "alpha": cfg.alpha,
            "device": device,
        }
    }

    with open(cfg.results_path, "w") as f:
        yaml.dump(final_results, f, default_flow_style=False, allow_unicode=True)

    print(f"\nResults saved to {cfg.results_path}")
    print(f"Figures saved to {cfg.figures_dir}/")

    print("\n" + "="*70)
    if gate_pass:
        print("GATE RESULT: PASS (SHOULD_WORK)")
        print("At least one prediction confirmed with statistical significance")
    else:
        print("GATE RESULT: FAIL")
        print("No predictions confirmed at alpha=0.05")
    print("="*70)

    return final_results

if __name__ == "__main__":
    main()
