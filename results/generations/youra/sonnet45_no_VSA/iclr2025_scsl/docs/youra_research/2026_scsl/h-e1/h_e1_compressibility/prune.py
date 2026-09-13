"""Pruning pipeline for h-e1 compressibility experiment."""

import argparse
import csv
from pathlib import Path
from typing import Dict, Any, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from data import get_dataloaders
from model import SimpleMLP, get_model
from utils import load_checkpoint


PRUNING_CONFIG = {
    "pruning_type": "unstructured",
    "pruning_scope": "global",
    "sparsity_levels": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    "pruning_metric": "magnitude",
    "one_shot": True,
    "layers_to_prune": ["linear"]
}


def magnitude_prune_global(model: nn.Module, sparsity: float) -> nn.Module:
    """Global magnitude pruning across all Linear layers."""
    all_weights = []
    for module in model.modules():
        if isinstance(module, nn.Linear):
            all_weights.append(module.weight.data.abs().view(-1))

    if not all_weights:
        return model

    all_weights = torch.cat(all_weights)
    k = int(sparsity * len(all_weights))
    if k == 0:
        return model

    threshold = torch.kthvalue(all_weights, k).values

    for module in model.modules():
        if isinstance(module, nn.Linear):
            mask = module.weight.data.abs() > threshold
            module.weight.data *= mask.float()

    return model


def evaluate_pruned(
    checkpoint_path: str,
    sparsity: float,
    test_loader: DataLoader,
    device: str
) -> Dict[str, Any]:
    """Load checkpoint, prune, evaluate."""
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    method = checkpoint.get("method", "ERM")

    model = get_model(method=method).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])

    model = magnitude_prune_global(model, sparsity)
    model.eval()

    correct = 0
    total = 0
    per_group = {(c, col): {"correct": 0, "total": 0} for c in range(10) for col in range(2)}

    with torch.no_grad():
        for images, labels, colors in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(dim=1).cpu()

            for pred, label, color in zip(preds, labels, colors):
                total += 1
                if pred == label:
                    correct += 1

                group = (label.item(), color.item())
                per_group[group]["total"] += 1
                if pred == label:
                    per_group[group]["correct"] += 1

    test_acc = correct / total if total > 0 else 0.0

    per_group_acc = {
        g: counts["correct"] / counts["total"]
        for g, counts in per_group.items()
        if counts["total"] > 0
    }
    worst_group_acc = min(per_group_acc.values()) if per_group_acc else 0.0

    total_params = sum(p.numel() for p in model.parameters())
    num_zero_params = sum((p == 0).sum().item() for p in model.parameters())

    return {
        "test_acc": test_acc,
        "worst_group_acc": worst_group_acc,
        "num_params": total_params,
        "num_zero_params": num_zero_params,
        "actual_sparsity": num_zero_params / total_params if total_params > 0 else 0.0
    }


def generate_pruning_curves(
    checkpoint_dir: str,
    sparsity_levels: List[float],
    output_csv: str,
    device: str
):
    """Generate pruning curves for all checkpoints."""
    dataloaders = get_dataloaders(batch_size=256)
    test_loader = dataloaders["test"]

    checkpoint_dir = Path(checkpoint_dir)
    checkpoints = sorted(checkpoint_dir.glob("*_epoch20.pt"))

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "method", "seed", "sparsity", "test_acc", "worst_group_acc",
            "num_params", "num_nonzero_params", "actual_sparsity"
        ])
        writer.writeheader()

        for checkpoint_path in checkpoints:
            filename = checkpoint_path.name
            parts = filename.replace(".pt", "").split("_")
            method = parts[0]
            seed = int(parts[1].replace("seed", ""))

            print(f"Processing {method} seed {seed}...")

            for sparsity in sparsity_levels:
                results = evaluate_pruned(
                    str(checkpoint_path),
                    sparsity,
                    test_loader,
                    device
                )

                writer.writerow({
                    "method": method,
                    "seed": seed,
                    "sparsity": sparsity,
                    "test_acc": results["test_acc"],
                    "worst_group_acc": results["worst_group_acc"],
                    "num_params": results["num_params"],
                    "num_nonzero_params": results["num_params"] - results["num_zero_params"],
                    "actual_sparsity": results["actual_sparsity"]
                })

    print(f"Pruning curves saved to {output_csv}")


def main(
    checkpoint_dir: str,
    output: str = "results/h_e1_pruning_logs.csv",
    device: str = "cuda"
):
    """Pruning CLI entry point."""
    sparsity_levels = PRUNING_CONFIG["sparsity_levels"]
    generate_pruning_curves(checkpoint_dir, sparsity_levels, output, device)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", type=str, required=True,
                        help="Directory containing trained checkpoints")
    parser.add_argument("--output", type=str, default="results/h_e1_pruning_logs.csv",
                        help="Output CSV path")
    parser.add_argument("--device", type=str, default="cuda",
                        choices=["cuda", "cpu"])

    args = parser.parse_args()

    main(
        checkpoint_dir=args.checkpoint_dir,
        output=args.output,
        device=args.device
    )
