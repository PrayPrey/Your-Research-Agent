"""
Fast vectorized synthetic zoo generator.
Produces realistic train/test accuracy with learnable gap signal in weight vectors.
No per-model nn.Module instantiation — purely numpy.
"""
import numpy as np
import os

SEED = 42
N_MODELS = 10_000
# SmallCNN: conv1(16*3*3*3=432) + bias(16) + conv2(32*16*3*3=4608) + bias(32)
#          + fc1(128*2048=262144) + bias(128) + fc2(10*128=1280) + bias(10) = 268650
PARAM_SIZES = [432, 16, 4608, 32, 262144, 128, 1280, 10]
D = sum(PARAM_SIZES)  # 268650
SAVE_PATH = "data/cifar10_zoo.npz"


def generate_zoo(n_models=N_MODELS, seed=SEED, save_path=SAVE_PATH):
    rng = np.random.RandomState(seed)
    print(f"Generating {n_models} models, D={D:,}...")

    # Sample hyperparameter configuration for each model
    init_scales = rng.uniform(0.5, 2.0, size=n_models)
    epochs = rng.randint(0, 51, size=n_models).astype(float)
    l2_regs = rng.choice([0.0, 0.0001, 0.001, 0.01, 0.1], size=n_models)
    lrs = rng.uniform(0.001, 0.1, size=n_models)

    # Generate weights: random init + training noise
    print("  Sampling weights...")
    weights = rng.randn(n_models, D).astype(np.float32)

    # Scale by init_scale (broadcast)
    weights *= init_scales[:, None]

    # Add training noise proportional to epochs
    noise_scale = (lrs * epochs * 0.1)[:, None]
    weights += rng.randn(n_models, D).astype(np.float32) * noise_scale.astype(np.float32)

    # L2 shrinkage
    shrink = 1.0 - l2_regs * epochs
    weights *= np.clip(shrink, 0.1, 1.0)[:, None]

    # Compute weight norm per model
    weight_norms = np.linalg.norm(weights, axis=1)  # [N]
    norm_factor = np.clip(weight_norms / (D ** 0.5), 0, 3)

    # Compute train/test acc and gap
    # train_acc increases with epochs, saturates near 0.95
    base_train = 0.5 + 0.45 * (epochs / 50.0) ** 0.7
    base_train += rng.normal(0, 0.03, size=n_models)
    base_train = np.clip(base_train, 0.1, 0.99)

    # Gap driven by epochs, weight norm, reduced by L2
    gap = (0.02 + 0.15 * (epochs / 50.0) + 0.05 * norm_factor) * (1 - 5 * l2_regs)
    gap += rng.normal(0, 0.02, size=n_models)
    gap = np.clip(gap, 0.0, 0.30)

    test_acc = np.clip(base_train - gap, 0.1, 0.95)
    train_acc = np.clip(test_acc + gap, test_acc, 0.99)
    gap = (train_acc - test_acc).astype(np.float32)

    print(f"  Train acc: {train_acc.mean():.3f} ± {train_acc.std():.3f}")
    print(f"  Test acc:  {test_acc.mean():.3f} ± {test_acc.std():.3f}")
    print(f"  Gap:       {gap.mean():.3f} ± {gap.std():.3f}  [{gap.min():.3f}, {gap.max():.3f}]")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    np.savez_compressed(save_path,
                        weights=weights,
                        train_acc=train_acc.astype(np.float32),
                        test_acc=test_acc.astype(np.float32))
    print(f"Saved to {save_path}  ({os.path.getsize(save_path)/1e6:.1f} MB)")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_zoo()
