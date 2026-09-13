#!/usr/bin/env python3
"""Main experiment runner for H-E1: NFN vs MLP-Matched comparison."""

import os
import sys
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from data import (
    load_model_zoo,
    normalize_weights,
    split_train_test,
    WeightSpaceDataset,
    make_collate_fn,
    get_network_spec_from_sample,
    set_seed
)
from model import NFNRegressor, MLPMatched, get_flat_dim, count_params
from train import train_model
from evaluate import (
    compute_r2,
    compare_models,
    plot_r2_comparison,
    plot_scatter,
    plot_residuals,
    plot_learning_curves,
    save_results_json
)


def main():
    cfg = Config()
    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    os.makedirs(cfg.figure_dir, exist_ok=True)

    print(f"\n[1/7] Loading/generating real CNN zoo (N={cfg.n_models})...")
    models = load_model_zoo(cfg.n_models, seed=cfg.seed)
    print(f"Loaded {len(models)} models with real CIFAR-10 accuracies")

    print("\n[2/7] Normalizing weights...")
    models = normalize_weights(models)

    print(f"\n[3/7] Splitting data ({cfg.train_frac*100:.0f}% train)...")
    train_models, test_models = split_train_test(models, cfg.train_frac, cfg.seed)
    print(f"Train: {len(train_models)}, Test: {len(test_models)}")

    print("\n[4/7] Building dataloaders and models...")
    network_spec = get_network_spec_from_sample(models)
    collate_fn = make_collate_fn(network_spec)

    train_dataset = WeightSpaceDataset(train_models)
    test_dataset = WeightSpaceDataset(test_models)

    train_loader = DataLoader(train_dataset, batch_size=cfg.batch_size, shuffle=True, collate_fn=collate_fn)
    test_loader = DataLoader(test_dataset, batch_size=cfg.batch_size, shuffle=False, collate_fn=collate_fn)

    nfn_model = NFNRegressor(network_spec, nfn_channels=cfg.nfn_channels)
    nfn_params = count_params(nfn_model)
    print(f"NFN parameters: {nfn_params:,}")

    flat_dim = get_flat_dim(models)
    mlp_model = MLPMatched(flat_dim, hidden_dim=cfg.mlp_hidden_dim, num_layers=cfg.mlp_num_layers)
    mlp_params = count_params(mlp_model)
    print(f"MLP parameters: {mlp_params:,}")

    print(f"\n[5/7] Training NFN ({cfg.epochs} epochs)...")
    nfn_history = train_model(nfn_model, train_loader, test_loader, cfg, "nfn", device)
    torch.save(nfn_model.state_dict(), os.path.join(cfg.checkpoint_dir, "nfn_model.pt"))

    print(f"\n[6/7] Training MLP ({cfg.epochs} epochs)...")
    set_seed(cfg.seed)
    mlp_history = train_model(mlp_model, train_loader, test_loader, cfg, "mlp", device)
    torch.save(mlp_model.state_dict(), os.path.join(cfg.checkpoint_dir, "mlp_model.pt"))

    print("\n[7/7] Evaluating and generating figures...")
    nfn_result = compute_r2(nfn_model, test_loader, "nfn", device)
    mlp_result = compute_r2(mlp_model, test_loader, "mlp", device)

    comparison = compare_models(nfn_result, mlp_result, cfg.r2_diff_threshold)

    print(f"\n{'='*50}")
    print("RESULTS")
    print(f"{'='*50}")
    print(f"NFN R²:        {comparison['nfn_r2']:.4f}")
    print(f"MLP R²:        {comparison['mlp_r2']:.4f}")
    print(f"Difference:    {comparison['difference']:.4f}")
    print(f"Threshold:     {comparison['threshold']:.4f}")
    print(f"Hypothesis:    {'SUPPORTED' if comparison['hypothesis_supported'] else 'NOT SUPPORTED'}")
    print(f"{'='*50}")

    plot_r2_comparison(
        comparison['nfn_r2'],
        comparison['mlp_r2'],
        comparison['threshold'],
        os.path.join(cfg.figure_dir, "r2_comparison.png")
    )

    nfn_preds, nfn_targets, _ = nfn_result
    mlp_preds, mlp_targets, _ = mlp_result

    plot_scatter(nfn_preds, nfn_targets, "NFN: Predicted vs Actual",
                 os.path.join(cfg.figure_dir, "nfn_scatter.png"))
    plot_scatter(mlp_preds, mlp_targets, "MLP: Predicted vs Actual",
                 os.path.join(cfg.figure_dir, "mlp_scatter.png"))

    plot_residuals(nfn_preds, nfn_targets, "NFN Residuals",
                   os.path.join(cfg.figure_dir, "nfn_residuals.png"))
    plot_residuals(mlp_preds, mlp_targets, "MLP Residuals",
                   os.path.join(cfg.figure_dir, "mlp_residuals.png"))

    plot_learning_curves(nfn_history, "NFN Learning Curves",
                         os.path.join(cfg.figure_dir, "nfn_learning_curves.png"))
    plot_learning_curves(mlp_history, "MLP Learning Curves",
                         os.path.join(cfg.figure_dir, "mlp_learning_curves.png"))

    results = {
        "hypothesis_id": "H-E1",
        "hypothesis_statement": "At N=1K, NFN R² > MLP-Matched R² + 0.05",
        "config": {
            "n_models": cfg.n_models,
            "train_frac": cfg.train_frac,
            "epochs": cfg.epochs,
            "batch_size": cfg.batch_size,
            "lr": cfg.lr,
            "seed": cfg.seed
        },
        "model_params": {
            "nfn": nfn_params,
            "mlp": mlp_params
        },
        "metrics": comparison,
        "training_history": {
            "nfn": {"final_train_loss": nfn_history['train_loss'][-1],
                    "final_val_loss": nfn_history['val_loss'][-1]},
            "mlp": {"final_train_loss": mlp_history['train_loss'][-1],
                    "final_val_loss": mlp_history['val_loss'][-1]}
        },
        "gate_result": {
            "type": "MUST_WORK",
            "passed": comparison['hypothesis_supported'],
            "reason": f"NFN R² ({comparison['nfn_r2']:.4f}) - MLP R² ({comparison['mlp_r2']:.4f}) = {comparison['difference']:.4f} {'>' if comparison['hypothesis_supported'] else '<='} {comparison['threshold']}"
        }
    }

    save_results_json(results, cfg.results_path)
    print(f"\nResults saved to: {cfg.results_path}")
    print(f"Figures saved to: {cfg.figure_dir}")

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results['gate_result']['passed'] else 1)
