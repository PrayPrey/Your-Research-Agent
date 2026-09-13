"""Run MNIST+Color experiments."""

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from config import MNISTConfig
from data.mnist_color import MNISTColorDataset
from models.gradcam import create_gradcam_for_resnet18
from trainers.erm_trainer import ERMTrainer
from trainers.spatial_reg_trainer import SpatialRegTrainer
from utils.common import create_resnet18, get_mnist_transforms, set_seed


def run_single_mnist_experiment(
    method: str, seed: int, output_dir: Path, data_root: str
) -> dict:
    """Run single MNIST experiment.

    Args:
        method: "erm" or "spatial_reg"
        seed: Random seed
        output_dir: Output directory
        data_root: Dataset root path

    Returns:
        {method, seed, wga, avg_acc, best_epoch}
    """
    set_seed(seed)

    # Config
    config = {
        "lr": 0.01,
        "batch_size": 128,
        "epochs": 50,
        "lambda_init": 0.01,
        "percentile_threshold": 75,
        "momentum": 0.9,
        "weight_decay": 1e-4,
        "patience": 10,
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Datasets
    transform = get_mnist_transforms()
    train_dataset = MNISTColorDataset(
        root=data_root, train=True, correlation=0.9, transform=transform, seed=seed
    )
    val_dataset = MNISTColorDataset(
        root=data_root, train=False, correlation=0.9, transform=transform, seed=seed
    )

    train_loader = DataLoader(
        train_dataset, batch_size=config["batch_size"], shuffle=True, num_workers=4
    )
    val_loader = DataLoader(
        val_dataset, batch_size=config["batch_size"], shuffle=False, num_workers=4
    )

    # Model
    model = create_resnet18(num_classes=10, pretrained=False)

    # Trainer
    if method == "erm":
        trainer = ERMTrainer(model, train_loader, val_loader, device, config)
    elif method == "spatial_reg":
        gradcam = create_gradcam_for_resnet18(model, device)
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

    # Final validation
    val_metrics = trainer.validate()

    # Save checkpoint
    checkpoint_dir = output_dir / method / f"seed_{seed}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        model.state_dict(), checkpoint_dir / "best_model.pth"
    )

    return {
        "method": method,
        "seed": seed,
        "wga": val_metrics["wga"],
        "avg_acc": val_metrics["avg_acc"],
        "best_epoch": results["best_epoch"],
    }


def run_mnist_experiments(
    output_dir: Path, data_root: str, seeds: list = [0, 1, 2, 3, 4]
) -> pd.DataFrame:
    """Run MNIST experiments across methods and seeds.

    Args:
        output_dir: Output directory
        data_root: Dataset root path
        seeds: List of random seeds

    Returns:
        DataFrame with columns [method, seed, wga, avg_acc, best_epoch]
    """
    methods = ["erm", "spatial_reg"]
    results = []

    for method in methods:
        for seed in seeds:
            result = run_single_mnist_experiment(method, seed, output_dir, data_root)
            results.append(result)

    df = pd.DataFrame(results)

    # Save results
    df.to_csv(output_dir / "mnist_results.csv", index=False)

    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./outputs/mnist",
        help="Output directory",
    )
    parser.add_argument(
        "--data_root",
        type=str,
        default="~/.data_cache/datasets/mnist",
        help="MNIST dataset root",
    )
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4], help="Random seeds"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_root = Path(args.data_root).expanduser()

    print("Running MNIST+Color experiments...")
    results_df = run_mnist_experiments(output_dir, str(data_root), args.seeds)

    print("\n" + "=" * 60)
    print("MNIST Experiments Complete")
    print("=" * 60)
    print(results_df.groupby("method").agg({"wga": ["mean", "std"], "avg_acc": ["mean", "std"]}))


if __name__ == "__main__":
    main()
