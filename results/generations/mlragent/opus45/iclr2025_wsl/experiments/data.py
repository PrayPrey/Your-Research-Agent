"""
Data generation and model zoo creation for SymVAE experiments.
Creates collections of trained neural networks with various configurations.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import json
from tqdm import tqdm


class SyntheticTaskDataset(Dataset):
    """
    Dataset for generating synthetic classification/regression tasks.
    Each task has a specific data distribution that we can encode as task conditioning.
    """

    def __init__(self, n_samples: int = 1000, input_dim: int = 10, n_classes: int = 2,
                 task_type: str = 'classification', seed: int = 42):
        super().__init__()
        self.n_samples = n_samples
        self.input_dim = input_dim
        self.n_classes = n_classes
        self.task_type = task_type

        np.random.seed(seed)
        torch.manual_seed(seed)

        # Generate random transformation matrix for this task
        self.W_task = np.random.randn(input_dim, input_dim) * 0.5
        self.b_task = np.random.randn(input_dim) * 0.1

        # Generate data
        self.X = np.random.randn(n_samples, input_dim).astype(np.float32)

        if task_type == 'classification':
            # Transform and threshold for classification
            transformed = np.tanh(self.X @ self.W_task + self.b_task)
            scores = transformed.sum(axis=1)
            if n_classes == 2:
                self.y = (scores > np.median(scores)).astype(np.int64)
            else:
                percentiles = np.linspace(0, 100, n_classes + 1)[1:-1]
                thresholds = np.percentile(scores, percentiles)
                self.y = np.digitize(scores, thresholds).astype(np.int64)
        else:
            # Regression target
            transformed = self.X @ self.W_task + self.b_task
            self.y = transformed.sum(axis=1, keepdims=True).astype(np.float32)

        self.X = torch.from_numpy(self.X)
        self.y = torch.from_numpy(self.y)

    def __len__(self) -> int:
        return self.n_samples

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]

    def get_task_descriptor(self) -> torch.Tensor:
        """Return a descriptor of this task based on data statistics."""
        # Compute statistics: mean, std, covariance eigenvalues
        X_np = self.X.numpy()
        mean = X_np.mean(axis=0)
        std = X_np.std(axis=0)

        # Truncate/pad to fixed size
        desc = np.concatenate([mean[:16], std[:16]])
        if len(desc) < 32:
            desc = np.pad(desc, (0, 32 - len(desc)))
        return torch.from_numpy(desc[:32].astype(np.float32))


class ModelZoo:
    """
    Collection of trained neural networks for various tasks.
    """

    def __init__(self, architecture: List[int], device: torch.device):
        self.architecture = architecture
        self.device = device
        self.models: List[Dict] = []

    def train_single_model(self, train_loader: DataLoader, val_loader: DataLoader,
                           task_descriptor: torch.Tensor, n_epochs: int = 50,
                           lr: float = 0.01, task_type: str = 'classification') -> Dict:
        """Train a single model and store its weights."""
        from models import TargetMLP

        model = TargetMLP(self.architecture).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        if task_type == 'classification':
            criterion = nn.CrossEntropyLoss()
        else:
            criterion = nn.MSELoss()

        best_val_loss = float('inf')
        best_weights = None
        best_biases = None

        train_losses = []
        val_losses = []

        for epoch in range(n_epochs):
            # Training
            model.train()
            epoch_loss = 0
            for X, y in train_loader:
                X, y = X.to(self.device), y.to(self.device)
                optimizer.zero_grad()
                output = model(X)
                loss = criterion(output, y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            train_losses.append(epoch_loss / len(train_loader))

            # Validation
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for X, y in val_loader:
                    X, y = X.to(self.device), y.to(self.device)
                    output = model(X)
                    val_loss += criterion(output, y).item()

            val_loss /= len(val_loader)
            val_losses.append(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                weights, biases = model.get_weights()
                best_weights = [w.cpu().clone() for w in weights]
                best_biases = [b.cpu().clone() for b in biases]

        return {
            'weights': best_weights,
            'biases': best_biases,
            'task_descriptor': task_descriptor,
            'val_loss': best_val_loss,
            'train_losses': train_losses,
            'val_losses': val_losses,
            'task_type': task_type
        }

    def create_zoo(self, n_models: int = 100, n_epochs: int = 50,
                   task_type: str = 'classification', verbose: bool = True) -> List[Dict]:
        """Create a model zoo by training models on diverse tasks."""
        self.models = []

        iterator = range(n_models)
        if verbose:
            iterator = tqdm(iterator, desc="Creating model zoo")

        for i in iterator:
            # Create task with different seed
            input_dim = self.architecture[0]
            output_dim = self.architecture[-1]

            if task_type == 'classification':
                dataset = SyntheticTaskDataset(
                    n_samples=500,
                    input_dim=input_dim,
                    n_classes=output_dim,
                    task_type='classification',
                    seed=i * 100
                )
            else:
                dataset = SyntheticTaskDataset(
                    n_samples=500,
                    input_dim=input_dim,
                    n_classes=1,
                    task_type='regression',
                    seed=i * 100
                )

            # Split into train/val
            train_size = int(0.8 * len(dataset))
            val_size = len(dataset) - train_size
            train_dataset, val_dataset = torch.utils.data.random_split(
                dataset, [train_size, val_size],
                generator=torch.Generator().manual_seed(i)
            )

            train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

            # Train model
            model_data = self.train_single_model(
                train_loader, val_loader,
                dataset.get_task_descriptor(),
                n_epochs=n_epochs,
                task_type=task_type
            )
            model_data['task_seed'] = i * 100

            self.models.append(model_data)

        return self.models


class WeightDataset(Dataset):
    """Dataset of neural network weights for training weight generation models."""

    def __init__(self, model_zoo: List[Dict]):
        self.model_zoo = model_zoo

    def __len__(self) -> int:
        return len(self.model_zoo)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        model_data = self.model_zoo[idx]
        return {
            'weights': model_data['weights'],
            'biases': model_data['biases'],
            'task_descriptor': model_data['task_descriptor']
        }


def collate_weights(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """Custom collate function for weight datasets."""
    # Stack weights for each layer
    n_layers = len(batch[0]['weights'])
    weights = [torch.cat([b['weights'][i] for b in batch], dim=0) for i in range(n_layers)]
    biases = [torch.cat([b['biases'][i] for b in batch], dim=0) for i in range(n_layers)]
    task_descriptors = torch.stack([b['task_descriptor'] for b in batch])

    return {
        'weights': weights,
        'biases': biases,
        'task_descriptor': task_descriptors
    }


def apply_random_permutation(weights: List[torch.Tensor], biases: List[torch.Tensor],
                             seed: Optional[int] = None) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
    """Apply random permutation to network weights (for testing symmetry invariance)."""
    if seed is not None:
        torch.manual_seed(seed)

    new_weights = []
    new_biases = []
    prev_perm = None

    for i, (w, b) in enumerate(zip(weights, biases)):
        batch_size = w.shape[0]
        out_features = w.shape[1]

        if i < len(weights) - 1:  # Don't permute output layer
            perm = torch.randperm(out_features)
            perm_matrix = torch.eye(out_features)[perm].unsqueeze(0).expand(batch_size, -1, -1)
            perm_matrix = perm_matrix.to(w.device)

            # Apply permutation to output dimension
            w_new = torch.bmm(perm_matrix, w)
            b_new = torch.bmm(perm_matrix, b.unsqueeze(-1)).squeeze(-1)

            # Apply inverse permutation from previous layer to input dimension
            if prev_perm is not None:
                w_new = torch.bmm(w_new, prev_perm.transpose(-1, -2))

            prev_perm = perm_matrix
        else:
            # Last layer: only apply previous permutation to inputs
            w_new = w.clone()
            b_new = b.clone()
            if prev_perm is not None:
                w_new = torch.bmm(w_new, prev_perm.transpose(-1, -2))

        new_weights.append(w_new)
        new_biases.append(b_new)

    return new_weights, new_biases
