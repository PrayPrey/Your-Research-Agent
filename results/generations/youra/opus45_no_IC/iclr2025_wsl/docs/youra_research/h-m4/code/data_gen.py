"""H-M4: Load real Model Zoo CIFAR-10 CNN weights."""

import sys
import os
from typing import Dict, List, Tuple

import torch
from torch.utils.data import TensorDataset

# Add ModelZooDataset code to path for loading saved .pt files
MODELZOO_CODE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ModelZooDataset", "code")
sys.path.insert(0, MODELZOO_CODE_DIR)

H_M3_CODE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "h-m3", "code")
sys.path.insert(0, H_M3_CODE_DIR)

from test_variance import flatten_state_dict

# Path to real Model Zoo CIFAR-10 CNN dataset
MODELZOO_DATA_PATH = "/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/data/cifar10_gs/dataset_cifar_small_hyp_rand.pt"


def load_model_zoo_population(
    data_path: str = MODELZOO_DATA_PATH,
    max_models: int = None,
) -> List[Dict]:
    """Load real Model Zoo CIFAR-10 CNN weights and test accuracies.

    Returns list of dicts with 'state_dict' and 'accuracy' keys.
    """
    data = torch.load(data_path, weights_only=False)
    trainset = data['trainset']
    test_accs = trainset.properties['test_acc']

    population = []
    n_models = len(trainset) if max_models is None else min(max_models, len(trainset))

    for i in range(n_models):
        state_dict = trainset[i]
        accuracy = test_accs[i]
        population.append({
            "state_dict": state_dict,
            "accuracy": accuracy,
            "idx": i,
        })

    return population


def split_train_test(
    population: List[Dict],
    n_train: int = 1000,
    n_test: int = 200,
    seed: int = 42,
) -> Tuple[List[Dict], List[Dict]]:
    """Split population into train/test sets."""
    import random
    rng = random.Random(seed)
    shuffled = population.copy()
    rng.shuffle(shuffled)
    return shuffled[:n_train], shuffled[n_train:n_train + n_test]


def to_dataset(population: List[Dict]) -> TensorDataset:
    """Convert population to TensorDataset with flattened weights and accuracy targets."""
    X_list = []
    y_list = []

    for model in population:
        flat = flatten_state_dict(model["state_dict"])
        X_list.append(flat.squeeze(0))
        y_list.append(model["accuracy"])

    X = torch.stack(X_list)
    y = torch.tensor(y_list, dtype=torch.float32).unsqueeze(1)

    return TensorDataset(X, y)


if __name__ == "__main__":
    print("Loading Model Zoo CIFAR-10 CNN dataset...")
    pop = load_model_zoo_population(max_models=1200)
    print(f"Loaded {len(pop)} real CNN models")
    print(f"Sample accuracy: {pop[0]['accuracy']:.4f}")
    print(f"State dict keys: {list(pop[0]['state_dict'].keys())[:4]}")

    train, test = split_train_test(pop, n_train=1000, n_test=200, seed=42)
    print(f"Train: {len(train)}, Test: {len(test)}")

    ds = to_dataset(train[:10])  # Small test
    print(f"Dataset size: {len(ds)}, X shape: {ds[0][0].shape}")
