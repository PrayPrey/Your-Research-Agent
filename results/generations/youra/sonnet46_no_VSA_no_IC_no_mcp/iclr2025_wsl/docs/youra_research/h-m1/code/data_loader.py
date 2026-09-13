"""H-M1 data loader: load Schürholt MNIST zoo, convert to per-layer dicts for NFT."""
import sys
import random
from pathlib import Path

import torch

ARCH = {"d_in": 784, "h": 64, "d_out": 10}
SPLITS = [784 * 64, 64, 10 * 64, 10]  # layer0.weight, layer0.bias, layer1.weight, layer1.bias
EXPECTED_DIM = sum(SPLITS)  # 51850

# Local archive paths (try multiple locations)
_CODE_DIR = Path(__file__).parent
_RESEARCH_ROOT = _CODE_DIR.parent.parent
_LOCAL_CANDIDATES = [
    _CODE_DIR / "data/synthetic_mnist_zoo.pt",     # synthetic zoo (preferred — larger)
    _RESEARCH_ROOT / "h-e1/code/data/mnist_zoo/mnist_zoo_full.pt",
    _RESEARCH_ROOT / "_archive/20260826T045831_routing_recovery/h-e1/code/data/mnist_zoo/mnist_zoo_full.pt",
]
H_E1_LOCAL = next((p for p in _LOCAL_CANDIDATES if p.exists()), _LOCAL_CANDIDATES[0])
H_E1_CODE = Path(__file__).parent.parent.parent / "h-e1/code"


def flat_to_weight_dict(flat: torch.Tensor) -> dict:
    """(51850,) → per-layer weight dict for NFT input."""
    assert flat.shape == (EXPECTED_DIM,), f"Expected ({EXPECTED_DIM},), got {flat.shape}"
    parts = torch.split(flat, SPLITS)
    return {
        "layer0.weight": parts[0].reshape(64, 784),
        "layer0.bias":   parts[1],
        "layer1.weight": parts[2].reshape(10, 64),
        "layer1.bias":   parts[3],
    }


def weight_dict_to_flat(w: dict) -> torch.Tensor:
    return torch.cat([
        w["layer0.weight"].flatten(),
        w["layer0.bias"].flatten(),
        w["layer1.weight"].flatten(),
        w["layer1.bias"].flatten(),
    ])


def load_zoo(hf_id="ModelZoos/ModelZooDataset", config="mnist-mlp", split="train+validation"):
    """Load zoo as list of (weight_dict, properties_dict). Tries HF, falls back to H-E1 local."""
    # Try H-E1 local archive first (faster)
    if H_E1_LOCAL.exists():
        print(f"Loading from H-E1 local archive: {H_E1_LOCAL}")
        raw = torch.load(str(H_E1_LOCAL), map_location="cpu", weights_only=False)
        weights_list = raw["weights"]
        labels_list  = raw["labels"]
        records = []
        for sd, meta in zip(weights_list, labels_list):
            if meta.get("dataset_name", "") != "mnist":
                continue
            flat = torch.cat([p.float().flatten() for p in sd.values()])
            if flat.shape[0] != EXPECTED_DIM:
                continue
            records.append({
                "weights_flat": flat,
                "test_accuracy":       float(meta.get("test_accuracy", float("nan"))),
                "generalization_gap":  float(meta.get("generalization_gap", float("nan"))),
                "learning_rate":       float(meta.get("learning_rate", float("nan"))),
            })
        print(f"Local zoo loaded: {len(records)} models")
        return records

    # Try HuggingFace
    try:
        from datasets import load_dataset
        print(f"Trying HuggingFace {hf_id} config={config} split={split}...")
        ds = load_dataset(hf_id, config, split=split)
        records = []
        for row in ds:
            w = row.get("weights") or row.get("weight")
            if w is None:
                continue
            flat = torch.tensor(list(w), dtype=torch.float32)
            if flat.shape[0] != EXPECTED_DIM:
                continue
            records.append({
                "weights_flat": flat,
                "test_accuracy":       float(row.get("test_acc", row.get("test_accuracy", float("nan")))),
                "generalization_gap":  float(row.get("generalization_gap", float("nan"))),
                "learning_rate":       float(row.get("learning_rate", float("nan"))),
            })
        print(f"HuggingFace: {len(records)} models loaded")
        return records
    except Exception as e:
        print(f"HuggingFace failed ({e})", file=sys.stderr)

    raise RuntimeError(
        f"Cannot load zoo. H-E1 local archive not found at {H_E1_LOCAL} "
        f"and HuggingFace failed."
    )


def get_zoo_tensors(zoo_records, device="cpu"):
    """
    Returns:
        weight_dicts: list[dict] of per-layer tensors on device
        zoo_properties: Tensor (N, 3) — test_accuracy, gen_gap, lr
    """
    weight_dicts = [flat_to_weight_dict(r["weights_flat"].to(device)) for r in zoo_records]
    props = torch.tensor(
        [[r["test_accuracy"], r["generalization_gap"], r["learning_rate"]] for r in zoo_records],
        dtype=torch.float32,
        device=device,
    )
    return weight_dicts, props
