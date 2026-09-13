"""H-C1: Load Schürholt MNIST zoo models."""
import sys
from pathlib import Path
import numpy as np
import torch

# Reuse H-M1 load_zoo which already handles HF download + weights_flat extraction
H_M1_CODE = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE))

SPLITS = [784 * 64, 64, 10 * 64, 10]  # layer0.weight, layer0.bias, layer1.weight, layer1.bias


def load_zoo_sample(n: int = 500, seed: int = 1):
    """
    Load N models from Schürholt MNIST zoo.
    Returns list of (W1, W2) tuples: W1=(64,784), W2=(10,64).
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "h_m1_data_loader", str(H_M1_CODE / "data_loader.py")
    )
    h_m1_dl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h_m1_dl)
    load_zoo = h_m1_dl.load_zoo

    zoo = load_zoo()
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(zoo), size=min(n, len(zoo)), replace=False)

    models = []
    for idx in indices:
        record = zoo[int(idx)]
        flat = record["weights_flat"].float()  # (51850,)
        parts = torch.split(flat, SPLITS)
        W1 = parts[0].reshape(64, 784)   # layer0.weight
        W2 = parts[2].reshape(10, 64)    # layer1.weight
        assert W1.shape == (64, 784), f"Unexpected W1 shape: {W1.shape}"
        assert W2.shape == (10, 64),  f"Unexpected W2 shape: {W2.shape}"
        models.append((W1, W2))

    return models
