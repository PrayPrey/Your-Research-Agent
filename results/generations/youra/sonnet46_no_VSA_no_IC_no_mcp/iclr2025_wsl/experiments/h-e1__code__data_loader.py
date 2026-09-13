import torch
import random
import sys
from collections import OrderedDict
from pathlib import Path

ARCH = {"D_in": 784, "h": 64, "D_out": 10}
# Actual dim from dataset: fc1.weight(784*64) + fc1.bias(64) + fc2.weight(64*10) + fc2.bias(10) = 50890
EXPECTED_DIM = 784 * 64 + 64 + 64 * 10 + 10  # 50890

LOCAL_ZOO_PATH = (
    Path(__file__).parent.parent.parent
    / "_archive/20260826T045831_routing_recovery/h-e1/code/data/mnist_zoo/mnist_zoo_full.pt"
)


def _state_dict_to_flat(sd):
    return torch.cat([p.float().flatten() for p in sd.values()])


def load_zoo(hf_id="ModelZoos/ModelZooDataset", config="mnist-mlp", split="train",
             dataset_filter="mnist"):
    """
    Load zoo. Tries HuggingFace first, falls back to local archive.
    dataset_filter: if set, keep only models with matching 'dataset_name' label.
    """
    # Try HuggingFace
    try:
        from datasets import load_dataset
        print(f"Trying HuggingFace {hf_id}...")
        ds = load_dataset(hf_id, config, split=split)
        records = []
        for row in ds:
            w = list(row["weights"])
            if len(w) != EXPECTED_DIM:
                raise ValueError(f"Dim mismatch: {len(w)} != {EXPECTED_DIM}")
            rec = {"weights": w}
            for k in ("test_acc", "generalization_gap", "learning_rate"):
                if k in row:
                    rec[k] = row[k]
            records.append(rec)
        print(f"HuggingFace: {len(records)} models loaded.")
        return records
    except Exception as e:
        print(f"HuggingFace failed ({e.__class__.__name__}), using local archive.", file=sys.stderr)

    # Local fallback
    if not LOCAL_ZOO_PATH.exists():
        raise RuntimeError(f"Local zoo not found at {LOCAL_ZOO_PATH}")

    print(f"Loading local zoo from {LOCAL_ZOO_PATH}...")
    raw = torch.load(str(LOCAL_ZOO_PATH), map_location="cpu", weights_only=False)
    weights_list = raw["weights"]   # list of OrderedDict (state_dicts)
    labels_list = raw["labels"]     # list of dicts

    records = []
    for sd, meta in zip(weights_list, labels_list):
        if dataset_filter and meta.get("dataset_name", "") != dataset_filter:
            continue
        flat = _state_dict_to_flat(sd)
        if flat.shape[0] != EXPECTED_DIM:
            raise ValueError(f"Dim {flat.shape[0]} != {EXPECTED_DIM}")
        rec = {
            "weights": flat.tolist(),
            "test_accuracy": meta.get("test_accuracy", float("nan")),
            "generalization_gap": meta.get("generalization_gap", float("nan")),
            "learning_rate": meta.get("learning_rate", float("nan")),
        }
        records.append(rec)

    print(f"Local zoo loaded: {len(records)} {dataset_filter or 'all'} models.")
    return records


def sample_models(zoo, n=1000, seed=42):
    if n > len(zoo):
        n = len(zoo)
        print(f"Warning: n reduced to zoo size {n}")
    rng = random.Random(seed)
    sampled = rng.sample(zoo, n)
    weights = torch.tensor([rec["weights"] for rec in sampled], dtype=torch.float32)
    assert weights.shape == (n, EXPECTED_DIM), f"Shape mismatch: {weights.shape}"
    return weights
