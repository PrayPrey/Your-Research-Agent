"""Training loop for H-M3: Flat-MLP + PermAug."""
import sys
import os
import torch
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import r2_score

import config

# Inject H-E1 code path (append so h-m3 local modules take precedence)
for p in [config.MZDATASET_CODE_PATH, config.H_M1_CODE_DIR, config.H_E1_CODE_DIR]:
    if p not in sys.path:
        sys.path.append(p)

import importlib.util as _ilu

def _load_from(module_name: str, code_dir: str):
    """Load a module by explicit path to avoid name collision."""
    spec = _ilu.spec_from_file_location(module_name, os.path.join(code_dir, f"{module_name}.py"))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_h_e1 = config.H_E1_CODE_DIR
_data_mod = _load_from("data", _h_e1)
_train_mod = _load_from("train", _h_e1)
_enc_mod = _load_from("encoders", _h_e1)

load_zoo = _data_mod.load_zoo
subsample = _data_mod.subsample
FlatCollator = _data_mod.FlatCollator
compute_flat_scaler = _data_mod.compute_flat_scaler
train_one = _train_mod.train_one
get_predictions = _train_mod.get_predictions
FlatMLP = _enc_mod.FlatMLP

from perm_aug import PermAugDataset
from verify import verify_perm_aug_mechanism


def _flat_collate(batch):
    xs, ys = zip(*batch)
    return torch.stack(xs), torch.stack(ys)


def train_perm_aug(n_train: int, zoo_name: str = "cifar10", device: str = "cuda"):
    """Train FlatMLP + PermAug for one (zoo, n_train) cell.

    Returns (r2_test, train_loss_curve, val_loss_curve).
    Test evaluation uses PLAIN (non-augmented) weights.
    """
    print(f"\n[H-M3] Training PermAug: zoo={zoo_name} n_train={n_train}")

    # Load data
    train_ds, val_ds, test_ds = load_zoo(zoo_name)
    sub_train = subsample(train_ds, n_train, seed=config.SEED)

    # Compute scaler from sub-train
    scaler = compute_flat_scaler(sub_train)

    # Determine input_dim
    collator = FlatCollator(scaler)
    probe_loader = DataLoader(sub_train, batch_size=2, shuffle=False, collate_fn=collator)
    first_x, _ = next(iter(probe_loader))
    input_dim = first_x.shape[1]
    print(f"[H-M3] input_dim={input_dim}")

    # Pre-flatten sub_train into TensorDataset for PermAugDataset
    all_x, all_y = [], []
    flat_loader = DataLoader(sub_train, batch_size=128, shuffle=False, collate_fn=collator)
    for xb, yb in flat_loader:
        all_x.append(xb.cpu())
        all_y.append(yb.cpu())
    flat_x = torch.cat(all_x)   # [N, D]
    flat_y = torch.cat(all_y)   # [N]
    plain_tensor_ds = TensorDataset(flat_x, flat_y)

    # layer_sizes for PermAug on FlatMLP predictor (not zoo CNN layers)
    layer_sizes = [input_dim] + config.FLATMLP_HIDDEN + [1]
    print(f"[H-M3] layer_sizes={layer_sizes}")

    # Build PermAugDataset
    perm_ds = PermAugDataset(plain_tensor_ds, layer_sizes, num_permutations=config.NUM_PERMUTATIONS)

    # MANDATORY mechanism check before training
    verify_perm_aug_mechanism(perm_ds, plain_tensor_ds, layer_sizes)

    # Build DataLoaders
    batch_size = config.BATCH_SIZE_SMALL if n_train <= config.SMALL_SIZE_THRESHOLD else config.BATCH_SIZE
    train_loader = DataLoader(perm_ds, batch_size=batch_size, shuffle=True,
                              collate_fn=_flat_collate, num_workers=0)

    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, collate_fn=collator)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False, collate_fn=collator)

    # Build FlatMLP
    torch.manual_seed(config.SEED)
    encoder = FlatMLP(input_dim=input_dim, hidden_dim=256, num_layers=3)

    # Train — use encoder_name="flat_mlp" (augmentation is in DataLoader, not model)
    history = train_one(
        encoder, train_loader, val_loader,
        encoder_name="flat_mlp",
        epochs=config.EPOCHS,
        lr=config.LR,
        weight_decay=config.WEIGHT_DECAY,
        seed=config.SEED,
        device=device,
    )

    # Test evaluation on PLAIN test set
    y_true, y_pred = get_predictions(encoder, test_loader, "flat_mlp", device)
    r2 = float(r2_score(y_true, y_pred))
    print(f"[H-M3] n_train={n_train} R²={r2:.4f}")

    return r2, history["train_loss"], history.get("val_loss", [])


def train_all_sizes(sizes: list, zoo_name: str = "cifar10", device: str = "cuda") -> dict:
    """Train PermAug for all N in sizes.

    Returns {str(N): {"r2": float, "train_losses": list, "val_losses": list}}.
    """
    results = {}
    for n in sizes:
        r2, train_losses, val_losses = train_perm_aug(n, zoo_name=zoo_name, device=device)
        results[str(n)] = {
            "r2": r2,
            "train_losses": train_losses,
            "val_losses": val_losses,
        }
    return results
