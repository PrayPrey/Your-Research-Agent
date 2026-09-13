#!/usr/bin/env python3
"""H-M3 Experiment: Compare EK-FAC/TracIn/TRAK attribution methods across BERT and GPT-2."""

import os
import sys
import json
import yaml
import torch
import numpy as np
from datetime import datetime
from scipy.stats import spearmanr

from config import ExperimentConfig, FIGURE_FILES, GATE_CONFIG
from data_loader import load_sst2_splits, build_dataloader
from models import load_bert_classifier, load_gpt2_classifier
from finetune import finetune_with_checkpoints, load_checkpoint
from mislabel import inject_mislabels, save_mislabeled_indices, load_mislabeled_indices
from ekfac_attribution import compute_ekfac_scores_simple
from tracin_attribution import compute_tracin_scores
from trak_attribution import compute_trak_scores_simple, run_trak_seed_ensemble
from metrics import compute_mislabeled_auc, compute_rank_correlation, compute_relative_arch_diff
from verify import verify_gate
from visualize import plot_gate_comparison, plot_quality_heatmap, plot_score_distributions

def main():
    cfg = ExperimentConfig()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    os.makedirs(cfg.checkpoints_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print("Loading SST-2 dataset...")
    train_texts, train_labels, val_texts, val_labels = load_sst2_splits()
    n_train = len(train_texts)
    n_val = len(val_texts)
    print(f"Train: {n_train}, Val: {n_val}")

    mislabel_path = os.path.join(cfg.output_dir, cfg.mislabeled_indices_path)
    if os.path.exists(mislabel_path):
        print("Loading existing mislabeled indices...")
        mislabeled_indices = load_mislabeled_indices(mislabel_path)
        train_labels_flipped = list(train_labels)
        for idx in mislabeled_indices:
            train_labels_flipped[idx] = 1 - train_labels_flipped[idx]
    else:
        print(f"Injecting {cfg.mislabel_fraction*100:.0f}% mislabeled samples...")
        train_labels_flipped, mislabeled_indices = inject_mislabels(
            list(train_labels), cfg.mislabel_fraction, cfg.seed
        )
        save_mislabeled_indices(mislabeled_indices, mislabel_path)
    print(f"Mislabeled samples: {len(mislabeled_indices)}")

    print("\nLoading BERT...")
    bert_model, bert_tokenizer = load_bert_classifier(cfg.bert_model_id)
    bert_train_loader = build_dataloader(bert_tokenizer, train_texts, train_labels_flipped,
                                          cfg.train_batch_size, cfg.max_length, shuffle=True)
    bert_val_loader = build_dataloader(bert_tokenizer, val_texts, val_labels,
                                        cfg.train_batch_size, cfg.max_length, shuffle=False)

    bert_ckpt_dir = cfg.checkpoints_dir
    bert_ckpts = [os.path.join(bert_ckpt_dir, f"bert_sst2_epoch{i}.pt") for i in [1, 2, 3]]

    if all(os.path.exists(c) for c in bert_ckpts):
        print("Loading BERT checkpoints...")
        bert_model = load_checkpoint(bert_model, bert_ckpts[-1], device)
    else:
        print("Fine-tuning BERT with checkpoints...")
        bert_ckpts = finetune_with_checkpoints(
            bert_model, bert_train_loader, cfg.epochs, cfg.lr, device,
            bert_ckpt_dir, "bert_sst2"
        )
    bert_model = bert_model.to(device)
    bert_model.eval()

    print("\nLoading GPT-2...")
    gpt2_model, gpt2_tokenizer = load_gpt2_classifier(cfg.gpt2_model_id)
    gpt2_train_loader = build_dataloader(gpt2_tokenizer, train_texts, train_labels_flipped,
                                          cfg.train_batch_size, cfg.max_length, shuffle=True)
    gpt2_val_loader = build_dataloader(gpt2_tokenizer, val_texts, val_labels,
                                        cfg.train_batch_size, cfg.max_length, shuffle=False)

    gpt2_ckpts = [os.path.join(bert_ckpt_dir, f"gpt2_sst2_epoch{i}.pt") for i in [1, 2, 3]]

    if all(os.path.exists(c) for c in gpt2_ckpts):
        print("Loading GPT-2 checkpoints...")
        gpt2_model = load_checkpoint(gpt2_model, gpt2_ckpts[-1], device)
    else:
        print("Fine-tuning GPT-2 with checkpoints...")
        gpt2_ckpts = finetune_with_checkpoints(
            gpt2_model, gpt2_train_loader, cfg.epochs, cfg.lr, device,
            bert_ckpt_dir, "gpt2_sst2"
        )
    gpt2_model = gpt2_model.to(device)
    gpt2_model.eval()

    results = {"bert": {}, "gpt2": {}}
    all_scores = {"bert": {}, "gpt2": {}}

    for arch, model, train_loader, val_loader, ckpts in [
        ("bert", bert_model, bert_train_loader, bert_val_loader, bert_ckpts),
        ("gpt2", gpt2_model, gpt2_train_loader, gpt2_val_loader, gpt2_ckpts),
    ]:
        print(f"\n{'='*60}")
        print(f"Computing attribution scores for {arch.upper()}")
        print(f"{'='*60}")

        print(f"\n[{arch}] EK-FAC Attribution...")
        ekfac_scores = compute_ekfac_scores_simple(model, train_loader, val_loader, device)
        ekfac_auc = compute_mislabeled_auc(ekfac_scores, mislabeled_indices, n_train)
        results[arch]["ekfac"] = {"auc": ekfac_auc, "n_samples": ekfac_scores.shape[1]}
        all_scores[arch]["ekfac"] = ekfac_scores
        print(f"[{arch}] EK-FAC AUC: {ekfac_auc:.4f}")

        print(f"\n[{arch}] TracIn Attribution...")
        tracin_scores = compute_tracin_scores(model, ckpts, val_loader, train_loader, cfg.lr, device)
        tracin_auc = compute_mislabeled_auc(tracin_scores, mislabeled_indices, n_train)
        results[arch]["tracin"] = {"auc": tracin_auc, "n_samples": tracin_scores.shape[1]}
        all_scores[arch]["tracin"] = tracin_scores
        print(f"[{arch}] TracIn AUC: {tracin_auc:.4f}")

        print(f"\n[{arch}] TRAK Attribution...")
        trak_scores = compute_trak_scores_simple(model, train_loader, val_loader,
                                                   cfg.trak_default_proj_dim, cfg.seed, device)
        trak_auc = compute_mislabeled_auc(trak_scores, mislabeled_indices, n_train)
        results[arch]["trak"] = {"auc": trak_auc, "n_samples": trak_scores.shape[1]}
        all_scores[arch]["trak"] = trak_scores
        print(f"[{arch}] TRAK AUC: {trak_auc:.4f}")

        print(f"\n[{arch}] Computing TRAK cross-seed correlation...")
        trak_seed_scores = run_trak_seed_ensemble(model, "text_classification", train_loader,
                                                   val_loader, cfg.trak_default_proj_dim,
                                                   cfg.trak_seeds[:3], n_train, device)
        cross_seed_corr = compute_rank_correlation(trak_seed_scores)
        results[arch]["trak"]["cross_seed_correlation"] = cross_seed_corr
        print(f"[{arch}] TRAK cross-seed correlation: {cross_seed_corr:.4f}")

    print("\n" + "="*60)
    print("Computing gate verification...")
    print("="*60)

    gate_results = {
        "ekfac": {"bert": results["bert"]["ekfac"]["auc"], "gpt2": results["gpt2"]["ekfac"]["auc"]},
        "tracin": {"bert": results["bert"]["tracin"]["auc"], "gpt2": results["gpt2"]["tracin"]["auc"]},
        "trak": {"bert": results["bert"]["trak"]["auc"], "gpt2": results["gpt2"]["trak"]["auc"]},
    }

    gate_verification = verify_gate(gate_results, GATE_CONFIG["min_relative_diff"])
    print(f"\nGate PASS: {gate_verification['pass']}")
    print(f"Per-method differences:")
    for method, diff in gate_verification["per_method_diff"].items():
        print(f"  {method}: {diff*100:.2f}%")
    print(f"Max difference: {gate_verification['max_diff']*100:.2f}% ({gate_verification['max_method']})")

    print("\nGenerating figures...")
    plot_gate_comparison(gate_results, os.path.join(cfg.figures_dir, FIGURE_FILES["gate_comparison"]))
    plot_quality_heatmap(gate_results, os.path.join(cfg.figures_dir, FIGURE_FILES["quality_heatmap"]))
    plot_score_distributions({"ekfac": all_scores["bert"]["ekfac"],
                              "tracin": all_scores["bert"]["tracin"],
                              "trak": all_scores["bert"]["trak"]},
                             os.path.join(cfg.figures_dir, FIGURE_FILES["score_distributions"]))
    print("Figures saved.")

    final_results = {
        "hypothesis_id": "h-m3",
        "timestamp": datetime.now().isoformat(),
        "bert_results": results["bert"],
        "gpt2_results": results["gpt2"],
        "gate_verification": gate_verification,
        "mislabeled_count": len(mislabeled_indices),
        "train_samples": n_train,
        "val_samples": n_val,
        "config": {
            "device": device,
            "epochs": cfg.epochs,
            "mislabel_fraction": cfg.mislabel_fraction,
            "gate_threshold": GATE_CONFIG["min_relative_diff"],
            "seed": cfg.seed,
        }
    }

    with open(cfg.results_path, "w") as f:
        yaml.dump(final_results, f, default_flow_style=False)

    print(f"\nResults saved to {cfg.results_path}")
    print(f"Figures saved to {cfg.figures_dir}/")

    print("\n" + "="*60)
    if gate_verification["pass"]:
        print("GATE RESULT: PASS")
        print(f"Method {gate_verification['max_method'].upper()} shows {gate_verification['max_diff']*100:.1f}% architecture difference")
    else:
        print("GATE RESULT: FAIL")
        print(f"No method exceeded {GATE_CONFIG['min_relative_diff']*100:.0f}% threshold")
    print("="*60)

    return final_results

if __name__ == "__main__":
    main()
