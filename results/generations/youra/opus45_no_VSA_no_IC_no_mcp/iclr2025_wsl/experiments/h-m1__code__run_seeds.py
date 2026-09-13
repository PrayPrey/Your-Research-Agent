from typing import Dict, List
import torch

from config import Config
from models import FlattenedMLP, DWSModel, NFTModel
from data import get_dataloaders, get_weight_shapes
from train_tracked import train_model_tracked
from torchmetrics import Accuracy


def run_single(model_type: str, seed: int, cfg: Config, weight_shapes: List, train_loader, test_loader) -> Dict:
    """Train single model with seed, return tracker data + eval accuracy."""
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)

    # Create model
    input_dim = sum(in_c * out_c for in_c, out_c in weight_shapes)
    if model_type == "mlp":
        model = FlattenedMLP(input_dim, cfg.mlp_hidden, cfg.num_classes, cfg.dropout)
    elif model_type == "dws":
        model = DWSModel(weight_shapes, cfg.dws_hidden, cfg.num_classes)
    elif model_type == "nft":
        model = NFTModel(weight_shapes, cfg.d_model, cfg.nhead, cfg.num_layers, cfg.num_classes)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    print(f"  Training {model_type.upper()} (seed={seed})...")
    model, tracker = train_model_tracked(model, model_type, train_loader, cfg)

    # Evaluate
    model.eval()
    accuracy_metric = Accuracy(task="multiclass", num_classes=cfg.num_classes).to(cfg.device)
    with torch.no_grad():
        for weight_list, labels in test_loader:
            weight_list = [w.to(cfg.device) for w in weight_list]
            labels = labels.to(cfg.device)
            logits = model(weight_list)
            accuracy_metric.update(logits, labels)
    acc = accuracy_metric.compute().item()

    result = tracker.to_dict()
    result["accuracy"] = acc
    result["seed"] = seed
    print(f"    Accuracy: {acc:.4f}")
    return result


def run_all_seeds(cfg: Config) -> Dict:
    """Run all models across all seeds."""
    train_loader, test_loader = get_dataloaders(cfg)
    weight_shapes = get_weight_shapes(cfg)

    results = {"mlp": [], "dws": [], "nft": []}

    for model_type in ["mlp", "dws", "nft"]:
        print(f"\n{'='*50}")
        print(f"Model: {model_type.upper()}")
        print(f"{'='*50}")
        for seed in cfg.seeds:
            result = run_single(model_type, seed, cfg, weight_shapes, train_loader, test_loader)
            results[model_type].append(result)

    return results
