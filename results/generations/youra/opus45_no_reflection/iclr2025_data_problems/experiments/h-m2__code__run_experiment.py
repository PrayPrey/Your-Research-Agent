#!/usr/bin/env python3
"""H-M2 Experiment: Compare Hessian curvature between BERT and GPT-2."""

import os
import sys
import json
import yaml
import torch
import numpy as np
from datetime import datetime

from config import ExperimentConfig, FIGURE_FILES
from data_loader import load_sst2_splits, build_dataloader
from models import load_bert_classifier, load_gpt2_classifier
from finetune import finetune, save_checkpoint, load_checkpoint
from hessian_analysis import compute_hessian_metrics, compute_spectral_density
from verify import verify_hessian_gate
from visualize import plot_gate_comparison, plot_eigenvalue_spectrum, plot_spectral_density

def main():
    cfg = ExperimentConfig()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    os.makedirs(cfg.checkpoints_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print("Loading SST-2 dataset...")
    train_texts, train_labels, val_texts, val_labels = load_sst2_splits()
    print(f"Train: {len(train_texts)}, Val: {len(val_texts)}")

    print("\nLoading BERT...")
    bert_model, bert_tokenizer = load_bert_classifier(cfg.bert_model_id)
    bert_train_loader = build_dataloader(bert_tokenizer, train_texts, train_labels, cfg.train_batch_size, cfg.max_length)
    bert_hessian_loader = build_dataloader(bert_tokenizer, train_texts[:cfg.hessian_batch_size*2], train_labels[:cfg.hessian_batch_size*2], cfg.hessian_batch_size, cfg.max_length, shuffle=False)

    bert_ckpt = os.path.join(cfg.checkpoints_dir, "bert_sst2.pt")
    if os.path.exists(bert_ckpt):
        print("Loading BERT checkpoint...")
        bert_model = load_checkpoint(bert_model, bert_ckpt, device)
        bert_model = bert_model.to(device)
    else:
        print("Fine-tuning BERT...")
        bert_model = finetune(bert_model, bert_train_loader, cfg.epochs, cfg.lr, device)
        save_checkpoint(bert_model, bert_ckpt)

    print("\nLoading GPT-2...")
    gpt2_model, gpt2_tokenizer = load_gpt2_classifier(cfg.gpt2_model_id)
    gpt2_train_loader = build_dataloader(gpt2_tokenizer, train_texts, train_labels, cfg.train_batch_size, cfg.max_length)
    gpt2_hessian_loader = build_dataloader(gpt2_tokenizer, train_texts[:cfg.hessian_batch_size*2], train_labels[:cfg.hessian_batch_size*2], cfg.hessian_batch_size, cfg.max_length, shuffle=False)

    gpt2_ckpt = os.path.join(cfg.checkpoints_dir, "gpt2_sst2.pt")
    if os.path.exists(gpt2_ckpt):
        print("Loading GPT-2 checkpoint...")
        gpt2_model = load_checkpoint(gpt2_model, gpt2_ckpt, device)
        gpt2_model = gpt2_model.to(device)
    else:
        print("Fine-tuning GPT-2...")
        gpt2_model = finetune(gpt2_model, gpt2_train_loader, cfg.epochs, cfg.lr, device)
        save_checkpoint(gpt2_model, gpt2_ckpt)

    loss_fn = torch.nn.CrossEntropyLoss()

    print("\nComputing BERT Hessian metrics...")
    bert_metrics = compute_hessian_metrics(bert_model, bert_hessian_loader, loss_fn, device, k=cfg.lanczos_k, seed=cfg.seeds[0])
    print(f"BERT metrics: top_eig={bert_metrics['top_eigenvalue']:.4f}, ratio={bert_metrics['eigenvalue_ratio']:.4f}, trace={bert_metrics['trace']:.4f}")

    print("\nComputing GPT-2 Hessian metrics...")
    gpt2_metrics = compute_hessian_metrics(gpt2_model, gpt2_hessian_loader, loss_fn, device, k=cfg.lanczos_k, seed=cfg.seeds[0])
    print(f"GPT-2 metrics: top_eig={gpt2_metrics['top_eigenvalue']:.4f}, ratio={gpt2_metrics['eigenvalue_ratio']:.4f}, trace={gpt2_metrics['trace']:.4f}")

    print("\nComputing spectral density...")
    bert_density = compute_spectral_density(bert_model, bert_hessian_loader, loss_fn, device, seed=cfg.seeds[0])
    gpt2_density = compute_spectral_density(gpt2_model, gpt2_hessian_loader, loss_fn, device, seed=cfg.seeds[0])

    print("\nVerifying gate...")
    gate_result = verify_hessian_gate(bert_metrics, gpt2_metrics, cfg.gate_threshold)
    print(f"Gate PASS: {gate_result['gate_pass']}, max_diff: {gate_result['max_diff']:.4f} ({gate_result['max_metric']})")

    print("\nGenerating figures...")
    plot_gate_comparison(bert_metrics, gpt2_metrics, os.path.join(cfg.figures_dir, FIGURE_FILES["gate_comparison"]))
    plot_eigenvalue_spectrum(bert_metrics["top_k_eigenvalues"], gpt2_metrics["top_k_eigenvalues"], os.path.join(cfg.figures_dir, FIGURE_FILES["eigenvalue_spectrum"]))
    plot_spectral_density(bert_density, gpt2_density, os.path.join(cfg.figures_dir, FIGURE_FILES["spectral_density"]))

    results = {
        "hypothesis_id": "h-m2",
        "timestamp": datetime.now().isoformat(),
        "bert_metrics": bert_metrics,
        "gpt2_metrics": gpt2_metrics,
        "gate_result": gate_result,
        "config": {
            "device": device,
            "epochs": cfg.epochs,
            "hessian_batch_size": cfg.hessian_batch_size,
            "lanczos_k": cfg.lanczos_k,
            "seeds": cfg.seeds,
        }
    }

    with open(cfg.results_path, "w") as f:
        yaml.dump(results, f, default_flow_style=False)

    np.savez(cfg.eigenvalues_path,
             bert_eigenvalues=np.array(bert_metrics["top_k_eigenvalues"]),
             gpt2_eigenvalues=np.array(gpt2_metrics["top_k_eigenvalues"]))

    print(f"\nResults saved to {cfg.results_path}")
    print(f"Eigenvalues saved to {cfg.eigenvalues_path}")
    print(f"Figures saved to {cfg.figures_dir}/")

    print("\n" + "="*60)
    if gate_result["gate_pass"]:
        print("GATE RESULT: PASS")
        print(f"Measurable difference found: {gate_result['max_metric']} differs by {gate_result['max_diff']*100:.1f}%")
    else:
        print("GATE RESULT: FAIL")
        print(f"No metric exceeded {cfg.gate_threshold*100:.0f}% threshold")
    print("="*60)

    return results

if __name__ == "__main__":
    main()
