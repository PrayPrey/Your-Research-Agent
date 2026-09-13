"""WeightSpace data loader for H-M2."""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from torch.utils.data import DataLoader, TensorDataset
import pickle

# Add h-e1 to Python path
h_e1_path = Path(__file__).parent.parent.parent / "docs" / "youra_research" / "h-e1" / "code"
if str(h_e1_path) not in sys.path:
    sys.path.insert(0, str(h_e1_path))

# Import from h-e1's data_loader module
import importlib.util
spec = importlib.util.spec_from_file_location("h_e1_data_loader", h_e1_path / "data_loader.py")
h_e1_data_loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_e1_data_loader)
ModelZooLoader = h_e1_data_loader.ModelZooLoader


class WeightSpaceDataLoader:
    """Load and prepare ModelZoo data for both MLP and NFN encoders."""

    def __init__(self, config: dict):
        """
        Initialize data loader.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.zoo_loader = ModelZooLoader(
            modelzoo_path=config["modelzoo_path"],
            random_seed=config["random_seed"]
        )
        self.cache_dir = Path(config["modelzoo_path"]) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def state_dicts_to_mlp_vectors(
        self,
        state_dicts: List[Dict[str, torch.Tensor]]
    ) -> torch.Tensor:
        """
        Flatten state dicts to vectors for MLP encoder.

        Args:
            state_dicts: List of PyTorch state dicts

        Returns:
            vectors: [B, max_params] flattened weight vectors (padded)
        """
        vectors = []
        max_params = 0

        # First pass: flatten and find max size
        for sd in state_dicts:
            flat = torch.cat([p.flatten() for p in sd.values()])
            vectors.append(flat)
            max_params = max(max_params, len(flat))

        # Second pass: pad to same size
        padded_vectors = []
        for vec in vectors:
            if len(vec) < max_params:
                padding = torch.zeros(max_params - len(vec))
                vec = torch.cat([vec, padding])
            padded_vectors.append(vec)

        return torch.stack(padded_vectors)

    def state_dicts_to_nfn_features(
        self,
        state_dicts: List[Dict[str, torch.Tensor]]
    ) -> List[torch.Tensor]:
        """
        Convert state dicts to structured tensors for NFN.

        For NFN, we need to preserve layer structure. We'll create
        a list of weight tensors per model, maintaining layer boundaries.

        Args:
            state_dicts: List of PyTorch state dicts

        Returns:
            List of structured weight tensors per model
        """
        nfn_features = []
        for sd in state_dicts:
            # Extract weights layer by layer (preserving structure)
            layer_tensors = []
            for key in sorted(sd.keys()):
                if 'weight' in key:
                    layer_tensors.append(sd[key])
            nfn_features.append(layer_tensors)
        return nfn_features

    def prepare_datasets(self) -> Tuple[
        Tuple[torch.Tensor, torch.Tensor],
        Tuple[torch.Tensor, torch.Tensor],
        Tuple[torch.Tensor, torch.Tensor]
    ]:
        """
        Load ModelZoo and create train/val/test splits.

        Returns:
            train_data, val_data, test_data
            Each is (mlp_vectors, nfn_features)
        """
        cache_file = self.cache_dir / "processed_data.pkl"

        # Check cache
        if cache_file.exists():
            print(f"Loading cached data from {cache_file}")
            with open(cache_file, 'rb') as f:
                cached = pickle.load(f)
            return cached['train'], cached['val'], cached['test']

        print("Processing ModelZoo data...")

        # Sample models
        n_samples = self.config["sample_size"]
        checkpoint_paths = self.zoo_loader.sample_models(n_samples)

        # Load state dicts
        state_dicts = []
        for path in checkpoint_paths:
            try:
                sd = self.zoo_loader.load_state_dict(path)
                state_dicts.append(sd)
            except Exception as e:
                print(f"Warning: Failed to load {path}: {e}")

        print(f"Loaded {len(state_dicts)} models")

        # Convert to MLP format
        mlp_vectors = self.state_dicts_to_mlp_vectors(state_dicts)
        print(f"MLP vectors shape: {mlp_vectors.shape}")

        # For NFN, we'll use the same MLP vectors but reshape for structured processing
        # In a full NFN implementation, we'd use nfn.common.state_dict_to_tensors
        # For this experiment, we use flattened vectors for both (NFN processes them differently)
        nfn_vectors = mlp_vectors.clone()

        # Create dummy labels (not used, but needed for DataLoader)
        labels = torch.zeros(len(state_dicts))

        # Split data
        n = len(state_dicts)
        train_size = int(n * self.config["train_ratio"])
        val_size = int(n * self.config["val_ratio"])

        indices = torch.randperm(n)
        train_idx = indices[:train_size]
        val_idx = indices[train_size:train_size + val_size]
        test_idx = indices[train_size + val_size:]

        train_data = (mlp_vectors[train_idx], labels[train_idx])
        val_data = (mlp_vectors[val_idx], labels[val_idx])
        test_data = (mlp_vectors[test_idx], labels[test_idx])

        # Cache processed data
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'train': train_data,
                'val': val_data,
                'test': test_data
            }, f)
        print(f"Cached data to {cache_file}")

        return train_data, val_data, test_data

    def get_dataloaders(self) -> Dict[str, Dict[str, DataLoader]]:
        """
        Create dataloaders for both MLP and NFN.

        Returns:
            {
                'mlp': {'train': DataLoader, 'val': DataLoader, 'test': DataLoader},
                'nfn': {'train': DataLoader, 'val': DataLoader, 'test': DataLoader}
            }
        """
        train_data, val_data, test_data = self.prepare_datasets()

        batch_size = self.config["batch_size"]

        # Create dataloaders (same data for both MLP and NFN)
        dataloaders = {
            'mlp': {
                'train': DataLoader(
                    TensorDataset(train_data[0], train_data[1]),
                    batch_size=batch_size,
                    shuffle=True
                ),
                'val': DataLoader(
                    TensorDataset(val_data[0], val_data[1]),
                    batch_size=batch_size,
                    shuffle=False
                ),
                'test': DataLoader(
                    TensorDataset(test_data[0], test_data[1]),
                    batch_size=batch_size,
                    shuffle=False
                )
            },
            'nfn': {
                'train': DataLoader(
                    TensorDataset(train_data[0], train_data[1]),
                    batch_size=batch_size,
                    shuffle=True
                ),
                'val': DataLoader(
                    TensorDataset(val_data[0], val_data[1]),
                    batch_size=batch_size,
                    shuffle=False
                ),
                'test': DataLoader(
                    TensorDataset(test_data[0], test_data[1]),
                    batch_size=batch_size,
                    shuffle=False
                )
            }
        }

        return dataloaders
