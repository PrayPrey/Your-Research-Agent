"""
Generate synthetic CNN zoo with a SMALL architecture for tractable weight storage.
SmallCNN-Tiny: conv1(3,8,3), conv2(8,16,3), fc1(16*8*8, 64), fc2(64, 10)
Params: 8*3*9+8 + 16*8*9+16 + 64*1024+64 + 10*64+10 = 216+8+1152+16+65536+64+640+10 = 67642

At 10k models: 10000 * 67642 * 4 bytes = ~2.7GB (still large but manageable)

Actually use even smaller:
conv1(3,4,3) = 108+4 = 112
conv2(4,8,3) = 288+8 = 296
fc1(8*8*8, 32) = 16384+32 = 16416
fc2(32,10) = 320+10 = 330
Total: 17154 params

10k * 17154 * 4 = 686MB -> OK
"""
import numpy as np
import os

SEED = 42
N_MODELS = 10_000

# SmallCNN-Tiny architecture
# Input: 3x32x32 -> conv1(4,3,3)+relu -> pool(2) -> 4x16x16
#       -> conv2(8,3,3)+relu -> pool(2) -> 8x8x8
#       -> fc1(512,64)+relu -> fc2(64,10)
LAYER_SHAPES = [
    # (fan_in_flat, fan_out) for 2D interpretation
    (3 * 3 * 3, 4),    # conv1.weight [4, 3, 3, 3] -> [3*3*3, 4]
    (4,),              # conv1.bias
    (4 * 3 * 3, 8),    # conv2.weight [8, 4, 3, 3] -> [4*3*3, 8]
    (8,),              # conv2.bias
    (8 * 8 * 8, 64),   # fc1.weight [64, 512] -> [512, 64]
    (64,),             # fc1.bias
    (64, 10),          # fc2.weight [10, 64] -> [64, 10]
    (10,),             # fc2.bias
]

PARAM_SIZES = []
WEIGHT_2D_SHAPES = []
for s in LAYER_SHAPES:
    if len(s) == 2:
        PARAM_SIZES.append(s[0] * s[1])
        WEIGHT_2D_SHAPES.append(s)
    else:
        PARAM_SIZES.append(s[0])

D = sum(PARAM_SIZES)
print(f"D = {D} params, zoo size = {N_MODELS * D * 4 / 1e6:.1f} MB")
SAVE_PATH = "data/cifar10_zoo.npz"


def generate_zoo(n_models=N_MODELS, seed=SEED):
    rng = np.random.RandomState(seed)

    # Hyperparams per model
    init_scales = rng.uniform(0.5, 2.0, n_models)
    epochs = rng.randint(0, 51, n_models).astype(float)
    l2_regs = rng.choice([0.0, 0.0001, 0.001, 0.01, 0.1], n_models)
    lrs = rng.uniform(0.001, 0.1, n_models)

    # Generate weights
    weights = rng.randn(n_models, D).astype(np.float32)
    weights *= init_scales[:, None].astype(np.float32)
    noise = (lrs * epochs * 0.1).astype(np.float32)
    weights += (rng.randn(n_models, D) * noise[:, None]).astype(np.float32)
    shrink = np.clip(1.0 - l2_regs * epochs, 0.1, 1.0).astype(np.float32)
    weights *= shrink[:, None]

    # Weight norm as signal for gap
    weight_norms = np.linalg.norm(weights, axis=1)
    norm_factor = np.clip(weight_norms / (D ** 0.5), 0, 3)

    # Train/test accuracy
    base_train = 0.5 + 0.45 * (epochs / 50.0) ** 0.7 + rng.normal(0, 0.03, n_models)
    base_train = np.clip(base_train, 0.1, 0.99)

    gap = (0.02 + 0.15 * (epochs / 50.0) + 0.05 * norm_factor) * (1.0 - 5 * l2_regs)
    gap += rng.normal(0, 0.02, n_models)
    gap = np.clip(gap, 0.0, 0.30).astype(np.float32)

    test_acc = np.clip(base_train - gap, 0.1, 0.95).astype(np.float32)
    train_acc = np.clip(test_acc + gap, test_acc, 0.99).astype(np.float32)
    gap = train_acc - test_acc

    print(f"N={n_models}, D={D}")
    print(f"Train acc: {train_acc.mean():.3f} ± {train_acc.std():.3f}")
    print(f"Test acc:  {test_acc.mean():.3f} ± {test_acc.std():.3f}")
    print(f"Gap:       {gap.mean():.3f} ± {gap.std():.3f}  [{gap.min():.3f}, {gap.max():.3f}]")

    from scipy.stats import spearmanr
    r, p = spearmanr(gap, -test_acc)
    print(f"A1 audit Spearman(gap, -test_acc) = {r:.4f}")

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    np.savez_compressed(save_path,
                        weights=weights,
                        train_acc=train_acc,
                        test_acc=test_acc,
                        weight_2d_shapes=np.array(WEIGHT_2D_SHAPES))
    sz = os.path.getsize(save_path)
    print(f"Saved to {save_path} ({sz/1e6:.1f} MB compressed)")


save_path = SAVE_PATH

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_zoo()
