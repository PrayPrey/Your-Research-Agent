import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import torch
from data_loader import CNNZooLoader, TransformerZooLoader

# Paths to downloaded data
CNN_ZOO_DIR = "/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_wsl_sonnet46_no_reflection/docs/youra_research/20260521_wsl/.data_cache/datasets/cnn_zoo/cifar10_cnn_sample_ep21-25"
MNIST_DIR = "/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_wsl_sonnet46_no_reflection/docs/youra_research/20260521_wsl/.data_cache/datasets/transformer_zoo/mnist"


def test_cnn_loader_returns_list():
    loader = CNNZooLoader(CNN_ZOO_DIR, n_checkpoints=5, seed=42)
    checkpoints = loader.load_checkpoints()
    assert isinstance(checkpoints, list)
    assert len(checkpoints) >= 1


def test_cnn_checkpoint_keys():
    loader = CNNZooLoader(CNN_ZOO_DIR, n_checkpoints=3, seed=42)
    checkpoints = loader.load_checkpoints()
    if checkpoints:
        ckpt = checkpoints[0]
        assert "state_dict" in ckpt
        assert "val_acc" in ckpt
        assert "checkpoint_id" in ckpt
        assert "task" in ckpt
        assert isinstance(ckpt["state_dict"], dict)
        assert isinstance(ckpt["val_acc"], float)


def test_cnn_loader_reproducibility():
    loader1 = CNNZooLoader(CNN_ZOO_DIR, n_checkpoints=5, seed=42)
    loader2 = CNNZooLoader(CNN_ZOO_DIR, n_checkpoints=5, seed=42)
    c1 = loader1.load_checkpoints()
    c2 = loader2.load_checkpoints()
    ids1 = [c["checkpoint_id"] for c in c1]
    ids2 = [c["checkpoint_id"] for c in c2]
    assert ids1 == ids2


def test_transformer_loader_returns_list():
    if not os.path.exists(MNIST_DIR):
        import pytest; pytest.skip("MNIST dir not available")
    loader = TransformerZooLoader(MNIST_DIR, n_mnist=5, seed=42)
    checkpoints = loader.load_checkpoints()
    assert isinstance(checkpoints, list)
    assert len(checkpoints) >= 1


def test_transformer_checkpoint_keys():
    if not os.path.exists(MNIST_DIR):
        import pytest; pytest.skip("MNIST dir not available")
    loader = TransformerZooLoader(MNIST_DIR, n_mnist=3, seed=42)
    checkpoints = loader.load_checkpoints()
    if checkpoints:
        ckpt = checkpoints[0]
        assert "state_dict" in ckpt
        assert "val_acc" in ckpt
        assert "arch_config" in ckpt
        assert isinstance(ckpt["state_dict"], dict)


def test_transformer_build_model():
    loader = TransformerZooLoader(mnist_dir="/tmp", n_mnist=0)
    arch = {"embed_dim": 32, "n_heads": 2, "n_layers": 2, "n_classes": 10,
            "n_patches": 49, "patch_size": 4, "n_channels": 1, "forward_mul": 2}
    model = loader.build_model(arch)
    import torch.nn as nn
    assert isinstance(model, nn.Module)
    x = torch.randn(2, 1, 28, 28)
    out = model(x)
    assert out.shape == (2, 10)
