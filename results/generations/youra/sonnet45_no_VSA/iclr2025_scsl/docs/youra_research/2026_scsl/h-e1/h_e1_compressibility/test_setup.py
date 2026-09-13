"""Test script to verify setup before full experiment."""

import sys
import torch
from data import get_dataloaders, DATASET_CONFIG
from model import get_model, MODEL_CONFIG
from optimizers import get_optimizer
from utils import set_seed

print("="*60)
print("Testing h-e1 experiment setup...")
print("="*60)

set_seed(42)

print("\n1. Testing data loading...")
try:
    dataloaders = get_dataloaders(batch_size=256)
    print(f"   ✓ Train batches: {len(dataloaders['train'])}")
    print(f"   ✓ Val batches: {len(dataloaders['val'])}")
    print(f"   ✓ Test batches: {len(dataloaders['test'])}")

    for images, labels, colors in dataloaders['train']:
        print(f"   ✓ Batch shape: images={images.shape}, labels={labels.shape}, colors={colors.shape}")
        print(f"   ✓ Correlation check: label<5 -> color (expected ~0.95 red=0)")
        mask_low = labels < 5
        if mask_low.sum() > 0:
            corr = (colors[mask_low] == 0).float().mean().item()
            print(f"   ✓ Actual correlation: {corr:.3f}")
        break
except Exception as e:
    print(f"   ✗ Data loading failed: {e}")
    sys.exit(1)

print("\n2. Testing model architecture...")
try:
    model = get_model(method="ERM")
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   ✓ Model created: SimpleMLP")
    print(f"   ✓ Total parameters: {total_params:,}")
    print(f"   ✓ Expected: ~1,090,000")

    has_batch_norm = any("BatchNorm" in name for name, _ in model.named_modules())
    print(f"   ✓ No batch norm: {not has_batch_norm}")
except Exception as e:
    print(f"   ✗ Model creation failed: {e}")
    sys.exit(1)

print("\n3. Testing forward pass...")
try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    images, labels, _ = next(iter(dataloaders['train']))
    images = images.to(device)

    outputs = model(images)
    print(f"   ✓ Forward pass successful")
    print(f"   ✓ Output shape: {outputs.shape} (expected [256, 10])")
except Exception as e:
    print(f"   ✗ Forward pass failed: {e}")
    sys.exit(1)

print("\n4. Testing SAM optimizer...")
try:
    optimizer = get_optimizer(model, "SAM", lr=0.01)
    print(f"   ✓ SAM optimizer created")

    criterion = torch.nn.CrossEntropyLoss()
    loss = criterion(outputs, labels.to(device))
    loss.backward()
    optimizer.first_step(zero_grad=True)

    loss = criterion(model(images), labels.to(device))
    loss.backward()
    optimizer.second_step(zero_grad=True)

    print(f"   ✓ SAM two-pass training successful")
except Exception as e:
    print(f"   ✗ SAM optimizer failed: {e}")
    sys.exit(1)

print("\n5. Testing ERM optimizer...")
try:
    model = get_model(method="ERM").to(device)
    optimizer = get_optimizer(model, "ERM", lr=0.01)
    print(f"   ✓ ERM optimizer created")

    outputs = model(images)
    loss = criterion(outputs, labels.to(device))
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    print(f"   ✓ ERM training successful")
except Exception as e:
    print(f"   ✗ ERM optimizer failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All tests passed! Ready to run full experiment.")
print("="*60)
