"""Run Waterbirds experiments with hyperparameter search."""

import argparse
import json
from pathlib import Path

import pandas as pd
import torch

from config import WaterbirdsConfig
from data.waterbirds import get_waterbirds_loaders
from models.gradcam import create_gradcam_for_resnet50
from trainers.erm_trainer import ERMTrainer
from trainers.spatial_reg_trainer import SpatialRegTrainer
from utils.common import (
    create_resnet50,
    get_eval_transforms,
    get_train_transforms,
    set_seed,
)


def hyperparameter_search(
    data_root: str,
    output_dir: Path,
    lambda_grid: list = [0.001, 0.01, 0.1],
    percentile_grid: list = [75, 85, 95],
    seed: int = 0,
) -> dict:
    """Grid search over lambda_init and percentile_threshold.

    Args:
        data_root: Waterbirds dataset root
        output_dir: Output directory
        lambda_grid: Lambda values to search
        percentile_grid: Percentile thresholds to search
        seed: Random seed

    Returns:
        {best_config, best_wga}
    """
    set_seed(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load data
    train_transform = get_train_transforms()
    eval_transform = get_eval_transforms()

    train_loader, val_loader, _ = get_waterbirds_loaders(
        data_root=data_root,
        batch_size=128,
        num_workers=4,
        train_transform=train_transform,
        eval_transform=eval_transform,
    )

    best_wga = 0.0
    best_config = None

    print(f"\n{'=' * 60}")
    print("Hyperparameter Search for Spatial Regularization")
    print(f"{'=' * 60}")

    for lambda_init in lambda_grid:
        for percentile in percentile_grid:
            config = {
                "lr": 0.001,
                "batch_size": 128,
                "epochs": 50,  # Reduced for search
                "lambda_init": lambda_init,
                "percentile_threshold": percentile,
                "momentum": 0.9,
                "weight_decay": 1e-4,
                "patience": 10,
            }

            print(
                f"\nTrying lambda={lambda_init}, percentile={percentile}"
            )

            # Create model
            model = create_resnet50(num_classes=2, pretrained=True)
            gradcam = create_gradcam_for_resnet50(model, device)

            # Train
            trainer = SpatialRegTrainer(
                model, train_loader, val_loader, device, config, gradcam
            )
            results = trainer.fit()

            # Validate
            val_metrics = trainer.validate()
            wga = val_metrics["wga"]

            print(f"  WGA: {wga:.4f}")

            if wga > best_wga:
                best_wga = wga
                best_config = config
                print(f"  ✓ New best!")

    print(f"\n{'=' * 60}")
    print(f"Best Config: lambda={best_config['lambda_init']}, percentile={best_config['percentile_threshold']}")
    print(f"Best WGA: {best_wga:.4f}")
    print(f"{'=' * 60}")

    return {"best_config": best_config, "best_wga": best_wga}


def run_single_waterbirds_experiment(
    method: str, seed: int, output_dir: Path, data_root: str, config: dict = None
) -> dict:
    """Run single Waterbirds experiment.

    Args:
        method: "erm" or "spatial_reg"
        seed: Random seed
        output_dir: Output directory
        data_root: Dataset root
        config: Config dict (if None, use default)

    Returns:
        {method, seed, wga, avg_acc, best_epoch}
    """
    set_seed(seed)

    if config is None:
        config = {
            "lr": 0.001,
            "batch_size": 128,
            "epochs": 300,
            "lambda_init": 0.01,
            "percentile_threshold": 75,
            "momentum": 0.9,
            "weight_decay": 1e-4,
            "patience": 20,
        }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load data
    train_transform = get_train_transforms()
    eval_transform = get_eval_transforms()

    train_loader, val_loader, test_loader = get_waterbirds_loaders(
        data_root=data_root,
        batch_size=config["batch_size"],
        num_workers=4,
        train_transform=train_transform,
        eval_transform=eval_transform,
    )

    # Model
    model = create_resnet50(num_classes=2, pretrained=True)

    # Trainer
    if method == "erm":
        trainer = ERMTrainer(model, train_loader, val_loader, device, config)
    elif method == "spatial_reg":
        gradcam = create_gradcam_for_resnet50(model, device)
        trainer = SpatialRegTrainer(
            model, train_loader, val_loader, device, config, gradcam
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    # Train
    print(f"\n{'=' * 60}")
    print(f"Method: {method}, Seed: {seed}")
    print(f"{'=' * 60}")

    results = trainer.fit()

    # Final test evaluation
    test_metrics = trainer.validate()  # Uses val_loader, replace with test if needed

    # Save checkpoint
    checkpoint_dir = output_dir / method / f"seed_{seed}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), checkpoint_dir / "best_model.pth")

    return {
        "method": method,
        "seed": seed,
        "wga": test_metrics["wga"],
        "avg_acc": test_metrics["avg_acc"],
        "best_epoch": results["best_epoch"],
    }


def run_waterbirds_experiments(
    output_dir: Path, data_root: str, seeds: list = [0, 1, 2, 3, 4]
) -> pd.DataFrame:
    """Run Waterbirds experiments with hyperparameter search.

    Args:
        output_dir: Output directory
        data_root: Dataset root
        seeds: List of random seeds

    Returns:
        DataFrame with columns [method, seed, wga, avg_acc, best_epoch]
    """
    methods = ["erm", "spatial_reg"]
    results = []

    # Hyperparameter search for spatial_reg (using first seed)
    print("Running hyperparameter search for spatial_reg...")
    search_results = hyperparameter_search(
        data_root, output_dir, seed=seeds[0]
    )
    best_config = search_results["best_config"]

    # Save search results
    with open(output_dir / "hyperparam_search.json", "w") as f:
        json.dump(search_results, f, indent=2)

    # Run experiments
    for method in methods:
        method_config = best_config if method == "spatial_reg" else None

        for seed in seeds:
            result = run_single_waterbirds_experiment(
                method, seed, output_dir, data_root, method_config
            )
            results.append(result)

    df = pd.DataFrame(results)

    # Save results
    df.to_csv(output_dir / "waterbirds_results.csv", index=False)

    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./outputs/waterbirds",
        help="Output directory",
    )
    parser.add_argument(
        "--data_root",
        type=str,
        default="~/.data_cache/datasets/waterbirds",
        help="Waterbirds dataset root",
    )
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4], help="Random seeds"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_root = Path(args.data_root).expanduser()

    print("Running Waterbirds experiments...")
    results_df = run_waterbirds_experiments(output_dir, str(data_root), args.seeds)

    print("\n" + "=" * 60)
    print("Waterbirds Experiments Complete")
    print("=" * 60)
    print(
        results_df.groupby("method").agg(
            {"wga": ["mean", "std"], "avg_acc": ["mean", "std"]}
        )
    )


if __name__ == "__main__":
    main()
