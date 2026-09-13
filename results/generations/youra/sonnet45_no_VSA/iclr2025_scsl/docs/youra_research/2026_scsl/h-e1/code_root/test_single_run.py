#!/usr/bin/env python3
"""
Quick test script to validate implementation on single run
Tests one method (Joint) on ColoredMNIST with reduced epochs
"""

import sys
import os
from pathlib import Path
import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_samswa import get_config
from data.datasets import get_dataloaders
from models.resnet import get_model
from optimizers.methods import get_optimizer
from train import train_method


def test_data_loading():
    """Test dataset loading"""
    print("="*80)
    print("TEST 1: Data Loading")
    print("="*80)

    # Test ColoredMNIST
    print("\nLoading ColoredMNIST...")
    dataloaders_cmnist = get_dataloaders(
        dataset_name="ColoredMNIST",
        batch_size=32,
        root_dir="data/colored_mnist",
        num_workers=2
    )
    train_loader = dataloaders_cmnist["train"]
    print(f"Train batches: {len(train_loader)}")

    # Get one batch
    batch = next(iter(train_loader))
    inputs, targets, metadata = batch
    print(f"Batch shape: {inputs.shape}")
    print(f"Targets shape: {targets.shape}")
    print(f"Metadata keys: {metadata.keys()}")
    print("✓ ColoredMNIST loading works!\n")


def test_model():
    """Test model creation"""
    print("="*80)
    print("TEST 2: Model Creation")
    print("="*80)

    model = get_model("Joint", pretrained=False)  # Use pretrained=False for speed
    print(f"Model created: {type(model).__name__}")

    # Test forward pass
    x = torch.randn(2, 3, 14, 14)  # ColoredMNIST size
    with torch.no_grad():
        y = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {y.shape}")
    print("✓ Model creation works!\n")


def test_optimizer():
    """Test optimizer creation"""
    print("="*80)
    print("TEST 3: Optimizer Creation")
    print("="*80)

    model = get_model("Joint", pretrained=False)
    optimizer = get_optimizer(
        method="Joint",
        model=model,
        lr=0.001,
        momentum=0.9,
        weight_decay=0.0001,
        rho=0.05,
        swa_start=3,
        swa_lr=0.05,
        epochs=5
    )
    print(f"Optimizer type: {type(optimizer).__name__}")
    print(f"SAM type: {type(optimizer.sam).__name__}")
    print(f"SWA model type: {type(optimizer.swa_model).__name__}")
    print("✓ Optimizer creation works!\n")


def test_single_training_run():
    """Test full training pipeline with reduced epochs"""
    print("="*80)
    print("TEST 4: Single Training Run (5 epochs)")
    print("="*80)

    # Get config and override epochs
    config = get_config("Joint", "ColoredMNIST", seed=42)

    # Override for quick test
    config.training.epochs = 5
    config.training.validate_every = 2
    config.training.pretrained = False  # Faster
    config.training.gradient_clip_norm = 1.0
    config.data.batch_size = 32  # Smaller batch

    print("\nStarting training...")
    result = train_method(
        method="Joint",
        dataset_name="ColoredMNIST",
        seed=42,
        config=config,
        output_dir="outputs/h-e1-test"
    )

    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Method: {result['method']}")
    print(f"Dataset: {result['dataset']}")
    print(f"Seed: {result['seed']}")
    print(f"Test WG Acc: {result['test_wg_acc']*100:.2f}%")
    print(f"Test Avg Acc: {result['test_avg_acc']*100:.2f}%")
    print(f"Training time: {result['training_time_hours']:.3f}h")
    print("\n✓ Full training pipeline works!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default="all",
                        choices=["data", "model", "optimizer", "train", "all"],
                        help="Which test to run")
    args = parser.parse_args()

    try:
        if args.test in ["data", "all"]:
            test_data_loading()

        if args.test in ["model", "all"]:
            test_model()

        if args.test in ["optimizer", "all"]:
            test_optimizer()

        if args.test in ["train", "all"]:
            test_single_training_run()

        print("\n" + "="*80)
        print("ALL TESTS PASSED!")
        print("="*80)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
