"""
Generate synthetic MNIST-like INR weight data for PoC validation.
Creates weights with strong class-discriminative patterns.
"""
import torch
from pathlib import Path
import numpy as np


def generate_siren_weights(digit_class: int, seed: int = None) -> dict:
    """Generate synthetic SIREN weights with strong class-dependent patterns."""
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)

    # SIREN-like architecture
    layer_shapes = [
        (2, 64),
        (64, 64),
        (64, 64),
        (64, 1),
    ]

    weights = {}

    # Create strong class-specific signatures
    class_signature = torch.zeros(10)
    class_signature[digit_class] = 1.0

    # Each digit has unique frequency and phase patterns
    base_freq = 1.0 + digit_class * 0.3
    base_phase = digit_class * np.pi / 5

    for i, (in_c, out_c) in enumerate(layer_shapes):
        # Layer-specific noise
        noise = torch.randn(out_c, in_c) * 0.1

        # Class-specific structured pattern
        row_idx = torch.arange(out_c).float().unsqueeze(1)
        col_idx = torch.arange(in_c).float().unsqueeze(0)

        # Sinusoidal pattern unique to each class
        pattern = torch.sin(base_freq * (row_idx + col_idx) / 10 + base_phase) * 0.5

        # Add class embedding to first layer
        if i == 0:
            class_embed = class_signature[digit_class].item() * 0.3
            pattern = pattern + class_embed

        w = pattern + noise
        b = torch.randn(out_c) * 0.1 + digit_class * 0.02

        weights[f"layer{i}.weight"] = w
        weights[f"layer{i}.bias"] = b

    return weights


def main():
    output_dir = Path("data/mnist_inrs/weights")

    # Clean old data
    if output_dir.exists():
        for f in output_dir.glob("*.pt"):
            f.unlink()

    output_dir.mkdir(parents=True, exist_ok=True)

    n_samples_per_class = 100  # 1000 total

    print("Generating synthetic MNIST INR weights with discriminative patterns...")

    sample_idx = 0
    for digit in range(10):
        for i in range(n_samples_per_class):
            seed = digit * 10000 + i
            weights = generate_siren_weights(digit, seed=seed)

            weight_list = [weights[f"layer{j}.weight"] for j in range(4)]

            data = {
                "weights": weight_list,
                "label": digit,
            }

            filename = output_dir / f"sample_{sample_idx:05d}_digit{digit}.pt"
            torch.save(data, filename)
            sample_idx += 1

    print(f"Generated {sample_idx} samples in {output_dir}")


if __name__ == "__main__":
    main()
