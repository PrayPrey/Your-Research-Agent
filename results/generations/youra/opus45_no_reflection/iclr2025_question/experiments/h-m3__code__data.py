"""H-M3 Data Module: Load hidden states from H-M1 cache"""
import numpy as np
import torch
from pathlib import Path
from sklearn.preprocessing import StandardScaler


def load_hidden_states(cache_folder: str) -> tuple[np.ndarray, np.ndarray]:
    """Load pre-extracted hidden states and labels from H-M1 cache."""
    cache_path = Path(cache_folder)

    train_data = torch.load(cache_path / "train_hidden_states.pt", map_location="cpu", weights_only=False)
    val_data = torch.load(cache_path / "val_hidden_states.pt", map_location="cpu", weights_only=False)

    X_train = train_data["hidden_states"].numpy().astype(np.float32)
    y_train = train_data["labels"].numpy().astype(np.int64)
    X_val = val_data["hidden_states"].numpy().astype(np.float32)
    y_val = val_data["labels"].numpy().astype(np.int64)

    assert X_train.shape == (9500, 4096), f"Train shape mismatch: {X_train.shape}"
    assert X_val.shape == (1700, 4096), f"Val shape mismatch: {X_val.shape}"
    assert y_train.shape == (9500,), f"Train labels shape mismatch: {y_train.shape}"
    assert y_val.shape == (1700,), f"Val labels shape mismatch: {y_val.shape}"

    return X_train, y_train, X_val, y_val


def scale_features(X_train: np.ndarray, X_val: np.ndarray) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    """Fit StandardScaler on train, transform both splits."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    return X_train_scaled, X_val_scaled, scaler
