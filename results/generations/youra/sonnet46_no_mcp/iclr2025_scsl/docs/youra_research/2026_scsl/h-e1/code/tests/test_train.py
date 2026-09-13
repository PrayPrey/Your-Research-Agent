"""Tests for A-2: ERM training loop (spec compliance)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import torch
import torch.nn as nn


def test_train_import():
    from train import build_model, get_transforms, train_one_seed, main
    assert build_model is not None
    assert get_transforms is not None


def test_build_model_output_shape():
    from train import build_model
    model = build_model(num_classes=2, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (2, 2), f"Expected (2,2), got {out.shape}"


def test_build_model_fc_replaced():
    from train import build_model
    model = build_model(num_classes=2, pretrained=False)
    assert isinstance(model.fc, nn.Linear)
    assert model.fc.out_features == 2
    assert model.fc.in_features == 2048


def test_build_model_not_on_device():
    """build_model should return model NOT moved to device — caller's responsibility."""
    from train import build_model
    model = build_model(pretrained=False)
    # Model should be on CPU by default
    for p in model.parameters():
        assert p.device.type == "cpu"
        break


def test_get_transforms_val_shape():
    from train import get_transforms
    from PIL import Image
    tf = get_transforms(augment=False)
    img = Image.new("RGB", (300, 300))
    t = tf(img)
    assert t.shape == (3, 224, 224)


def test_get_transforms_train_shape():
    from train import get_transforms
    from PIL import Image
    tf = get_transforms(augment=True)
    img = Image.new("RGB", (300, 300))
    t = tf(img)
    assert t.shape == (3, 224, 224)


def test_checkpoint_saved(tmp_path):
    """train_one_seed should save checkpoint every 2 epochs."""
    from train import train_one_seed
    from config import TrainConfig
    import pandas as pd

    # Create minimal waterbirds fixture
    from PIL import Image
    wb_root = tmp_path / "waterbirds"
    wb_root.mkdir()
    img_dir = wb_root / "images"
    img_dir.mkdir()
    rows = []
    for i in range(4):
        split = 0 if i < 3 else 1  # 3 train, 1 val
        fname = f"b{i}.jpg"
        Image.new("RGB", (256, 256)).save(str(img_dir / fname))
        rows.append({"img_id": i, "img_filename": f"images/{fname}",
                     "y": i % 2, "split": split, "place": (i+1)%2,
                     "place_filename": "/p/p.jpg"})
    pd.DataFrame(rows).to_csv(str(wb_root / "metadata.csv"), index=False)

    ckpt_dir = str(tmp_path / "checkpoints" / "waterbirds")
    cfg = TrainConfig(
        dataset="waterbirds",
        data_root=str(wb_root),
        checkpoint_dir=ckpt_dir,
        epochs=4,
        checkpoint_interval=2,
        batch_size=2,
        seeds=[1],
        num_workers=0,
    )
    train_one_seed(cfg, seed=1, device="cpu")

    # Checkpoints should exist at epoch 2 and 4
    assert os.path.exists(os.path.join(ckpt_dir, "seed_1", "epoch_002.pt"))
    assert os.path.exists(os.path.join(ckpt_dir, "seed_1", "epoch_004.pt"))
