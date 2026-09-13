"""
Data generation script for creating model zoo with symmetry variants and backdoored models.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
import os
import json
from tqdm import tqdm

import config


class SimpleMLPModel(nn.Module):
    """Simple MLP for testing."""
    def __init__(self, input_dim=784, hidden_dim=64, num_classes=10):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class SimpleCNNModel(nn.Module):
    """Simple CNN for testing."""
    def __init__(self, input_channels=3, hidden_dim=64, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(input_channels, hidden_dim, 3, padding=1)
        self.conv2 = nn.Conv2d(hidden_dim, hidden_dim*2, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(hidden_dim*2 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def permute_layer_neurons(layer_weight, layer_bias, next_layer_weight):
    """Apply random permutation to neurons in a layer."""
    num_neurons = layer_weight.shape[0]
    perm = torch.randperm(num_neurons)

    # Permute output neurons of current layer
    permuted_weight = layer_weight[perm]
    permuted_bias = layer_bias[perm] if layer_bias is not None else None

    # Permute input neurons of next layer
    permuted_next_weight = next_layer_weight[:, perm] if next_layer_weight is not None else None

    return permuted_weight, permuted_bias, permuted_next_weight, perm


def apply_permutation_symmetry(model):
    """Apply permutation symmetry transformation to a model."""
    # Create a new instance of the same model type
    if isinstance(model, SimpleMLPModel):
        model_copy = SimpleMLPModel(input_dim=784, hidden_dim=64, num_classes=10)
    elif isinstance(model, SimpleCNNModel):
        model_copy = SimpleCNNModel(input_channels=3, hidden_dim=64, num_classes=10)
    else:
        raise ValueError(f"Unknown model type: {type(model)}")

    model_copy.load_state_dict(model.state_dict())

    with torch.no_grad():
        if isinstance(model_copy, SimpleMLPModel):
            # Permute fc1 neurons
            perm_w, perm_b, next_w, _ = permute_layer_neurons(
                model_copy.fc1.weight.data,
                model_copy.fc1.bias.data,
                model_copy.fc2.weight.data
            )
            model_copy.fc1.weight.data = perm_w
            model_copy.fc1.bias.data = perm_b
            model_copy.fc2.weight.data = next_w

            # Permute fc2 neurons
            perm_w, perm_b, next_w, _ = permute_layer_neurons(
                model_copy.fc2.weight.data,
                model_copy.fc2.bias.data,
                model_copy.fc3.weight.data
            )
            model_copy.fc2.weight.data = perm_w
            model_copy.fc2.bias.data = perm_b
            model_copy.fc3.weight.data = next_w

    return model_copy


def apply_scaling_symmetry(model, scale_factor=2.0):
    """Apply scaling symmetry transformation."""
    if isinstance(model, SimpleMLPModel):
        model_copy = SimpleMLPModel(input_dim=784, hidden_dim=64, num_classes=10)
    elif isinstance(model, SimpleCNNModel):
        model_copy = SimpleCNNModel(input_channels=3, hidden_dim=64, num_classes=10)
    else:
        raise ValueError(f"Unknown model type: {type(model)}")

    model_copy.load_state_dict(model.state_dict())

    with torch.no_grad():
        if isinstance(model_copy, SimpleMLPModel):
            # Scale fc1 output and fc2 input
            model_copy.fc1.weight.data *= scale_factor
            model_copy.fc1.bias.data *= scale_factor
            model_copy.fc2.weight.data /= scale_factor

    return model_copy


def apply_noise_perturbation(model, noise_std=0.01):
    """Add Gaussian noise to model weights."""
    if isinstance(model, SimpleMLPModel):
        model_copy = SimpleMLPModel(input_dim=784, hidden_dim=64, num_classes=10)
    elif isinstance(model, SimpleCNNModel):
        model_copy = SimpleCNNModel(input_channels=3, hidden_dim=64, num_classes=10)
    else:
        raise ValueError(f"Unknown model type: {type(model)}")

    model_copy.load_state_dict(model.state_dict())

    with torch.no_grad():
        for param in model_copy.parameters():
            param.data += torch.randn_like(param) * noise_std

    return model_copy


def inject_backdoor(model, trigger_size=0.05):
    """Inject a simple backdoor by modifying specific weights."""
    if isinstance(model, SimpleMLPModel):
        model_copy = SimpleMLPModel(input_dim=784, hidden_dim=64, num_classes=10)
    elif isinstance(model, SimpleCNNModel):
        model_copy = SimpleCNNModel(input_channels=3, hidden_dim=64, num_classes=10)
    else:
        raise ValueError(f"Unknown model type: {type(model)}")

    model_copy.load_state_dict(model.state_dict())

    with torch.no_grad():
        if isinstance(model_copy, SimpleMLPModel):
            # Modify a small portion of weights in the last layer
            num_modify = int(model_copy.fc3.weight.numel() * trigger_size)
            indices = torch.randperm(model_copy.fc3.weight.numel())[:num_modify]
            flat_weight = model_copy.fc3.weight.data.view(-1)
            flat_weight[indices] += torch.randn(num_modify) * 0.5

    return model_copy


def create_base_models(num_models: int, arch_type: str) -> List[nn.Module]:
    """Create base models with random initializations."""
    models = []

    for i in tqdm(range(num_models), desc=f"Creating {arch_type} base models"):
        if arch_type == 'mlp':
            model = SimpleMLPModel(input_dim=784, hidden_dim=64, num_classes=10)
        elif arch_type == 'cnn':
            model = SimpleCNNModel(input_channels=3, hidden_dim=64, num_classes=10)
        else:
            raise ValueError(f"Unknown architecture type: {arch_type}")

        # Random initialization (already done by PyTorch)
        models.append(model)

    return models


def generate_symmetry_variants(base_model: nn.Module, num_variants: int) -> List[Tuple[nn.Module, str]]:
    """Generate symmetry variants of a base model."""
    variants = []

    num_each = num_variants // 4

    # Permutation variants
    for _ in range(num_each):
        variant = apply_permutation_symmetry(base_model)
        variants.append((variant, 'permutation'))

    # Scaling variants
    for _ in range(num_each):
        scale = np.random.uniform(0.5, 2.0)
        variant = apply_scaling_symmetry(base_model, scale)
        variants.append((variant, 'scaling'))

    # Noise variants (benign perturbation)
    for _ in range(num_each):
        noise_std = np.random.uniform(0.001, 0.01)
        variant = apply_noise_perturbation(base_model, noise_std)
        variants.append((variant, 'noise'))

    # Combined transformations
    for _ in range(num_variants - 3*num_each):
        variant = apply_permutation_symmetry(base_model)
        variant = apply_scaling_symmetry(variant, np.random.uniform(0.5, 2.0))
        variants.append((variant, 'combined'))

    return variants


def generate_backdoored_models(base_models: List[nn.Module], num_backdoor: int) -> List[Tuple[nn.Module, str]]:
    """Generate backdoored variants of base models."""
    backdoored = []

    for i in range(num_backdoor):
        base_idx = i % len(base_models)
        base_model = base_models[base_idx]

        trigger_size = np.random.uniform(0.01, 0.1)
        backdoored_model = inject_backdoor(base_model, trigger_size)
        backdoored.append((backdoored_model, f'backdoor_model_{i}'))

    return backdoored


def save_model_weights(model: nn.Module, filepath: str):
    """Save model weights to file."""
    torch.save(model.state_dict(), filepath)


def generate_dataset():
    """Generate the complete dataset of models."""
    os.makedirs(config.DATA_DIR, exist_ok=True)

    dataset_info = {
        'base_models': [],
        'symmetry_variants': [],
        'backdoored_models': [],
        'metadata': {}
    }

    all_base_models = []

    # Generate base models for each architecture
    for arch_idx, arch_type in enumerate(config.ARCHITECTURES):
        num_models_per_arch = config.NUM_BASE_MODELS // len(config.ARCHITECTURES)
        base_models = create_base_models(num_models_per_arch, arch_type)

        for i, model in enumerate(base_models):
            model_id = f"{arch_type}_base_{i}"
            filepath = os.path.join(config.DATA_DIR, f"{model_id}.pt")
            save_model_weights(model, filepath)

            dataset_info['base_models'].append({
                'id': model_id,
                'architecture': arch_type,
                'filepath': filepath,
                'is_backdoored': False
            })

            all_base_models.append((model, model_id, arch_type))

    # Generate symmetry variants
    print("\nGenerating symmetry variants...")
    for model, model_id, arch_type in tqdm(all_base_models):
        variants = generate_symmetry_variants(model, config.NUM_SYMMETRY_VARIANTS)

        for j, (variant_model, transform_type) in enumerate(variants):
            variant_id = f"{model_id}_variant_{j}"
            filepath = os.path.join(config.DATA_DIR, f"{variant_id}.pt")
            save_model_weights(variant_model, filepath)

            dataset_info['symmetry_variants'].append({
                'id': variant_id,
                'base_id': model_id,
                'architecture': arch_type,
                'transform_type': transform_type,
                'filepath': filepath,
                'is_backdoored': False
            })

    # Generate backdoored models
    print("\nGenerating backdoored models...")
    all_models_list = [m for m, _, _ in all_base_models]
    backdoored_models = generate_backdoored_models(all_models_list, config.NUM_BACKDOOR_MODELS)

    for backdoored_model, backdoor_id in backdoored_models:
        filepath = os.path.join(config.DATA_DIR, f"{backdoor_id}.pt")
        save_model_weights(backdoored_model, filepath)

        dataset_info['backdoored_models'].append({
            'id': backdoor_id,
            'architecture': all_base_models[0][2],  # Use first architecture
            'filepath': filepath,
            'is_backdoored': True
        })

    # Save dataset info
    dataset_info['metadata'] = {
        'num_base_models': len(dataset_info['base_models']),
        'num_symmetry_variants': len(dataset_info['symmetry_variants']),
        'num_backdoored_models': len(dataset_info['backdoored_models']),
        'architectures': config.ARCHITECTURES
    }

    with open(os.path.join(config.DATA_DIR, 'dataset_info.json'), 'w') as f:
        json.dump(dataset_info, f, indent=2)

    print(f"\nDataset generation complete!")
    print(f"Total base models: {len(dataset_info['base_models'])}")
    print(f"Total symmetry variants: {len(dataset_info['symmetry_variants'])}")
    print(f"Total backdoored models: {len(dataset_info['backdoored_models'])}")

    return dataset_info


if __name__ == "__main__":
    torch.manual_seed(config.SEED)
    np.random.seed(config.SEED)

    generate_dataset()
