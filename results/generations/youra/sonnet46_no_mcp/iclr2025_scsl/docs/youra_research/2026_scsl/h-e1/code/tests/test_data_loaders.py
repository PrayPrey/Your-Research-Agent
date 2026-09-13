"""Tests for A-1: Waterbirds and CelebA data loaders (spec compliance)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import torch
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from PIL import Image
import tempfile


# ── WaterbirdsDataset ─────────────────────────────────────────────────────────

def make_waterbirds_fixture(tmp_path):
    """Create minimal Waterbirds directory structure for testing."""
    # Create metadata.csv
    rows = []
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    for i in range(6):
        split = i % 3  # 0=train,1=val,2=test, 2 per split
        fname = f"bird_{i:03d}.jpg"
        (img_dir / fname).mkdir(parents=True, exist_ok=True) if False else None
        img = Image.new("RGB", (256, 256), color=(i * 40, 100, 200))
        img.save(str(img_dir / fname))
        rows.append({
            "img_id": i,
            "img_filename": f"images/{fname}",
            "y": i % 2,
            "split": split,
            "place": (i + 1) % 2,
            "place_filename": f"/p/place/{i}.jpg",
        })
    df = pd.DataFrame(rows)
    df.to_csv(str(tmp_path / "metadata.csv"), index=False)
    return str(tmp_path)


def test_waterbirds_import():
    from data.waterbirds import WaterbirdsDataset, get_waterbirds_loader
    assert WaterbirdsDataset is not None
    assert get_waterbirds_loader is not None


def test_waterbirds_dataset_len(tmp_path):
    from data.waterbirds import WaterbirdsDataset
    root = make_waterbirds_fixture(tmp_path)
    ds = WaterbirdsDataset(root=root, split="train")
    assert len(ds) == 2  # 2 per split in fixture


def test_waterbirds_dataset_getitem_keys(tmp_path):
    from data.waterbirds import WaterbirdsDataset
    root = make_waterbirds_fixture(tmp_path)
    ds = WaterbirdsDataset(root=root, split="val")
    item = ds[0]
    assert "image" in item
    assert "core_label" in item
    assert "spurious_label" in item


def test_waterbirds_dataset_label_types(tmp_path):
    from data.waterbirds import WaterbirdsDataset
    root = make_waterbirds_fixture(tmp_path)
    ds = WaterbirdsDataset(root=root, split="val")
    item = ds[0]
    assert isinstance(item["core_label"], int)
    assert isinstance(item["spurious_label"], int)


def test_waterbirds_loader_returns_dataloader(tmp_path):
    from data.waterbirds import get_waterbirds_loader
    root = make_waterbirds_fixture(tmp_path)
    loader = get_waterbirds_loader(root=root, split="val", batch_size=2,
                                   num_workers=0, augment=False)
    from torch.utils.data import DataLoader
    assert isinstance(loader, DataLoader)


def test_waterbirds_loader_batch_keys(tmp_path):
    from data.waterbirds import get_waterbirds_loader
    root = make_waterbirds_fixture(tmp_path)
    loader = get_waterbirds_loader(root=root, split="val", batch_size=2,
                                   num_workers=0, augment=False)
    batch = next(iter(loader))
    assert "image" in batch
    assert "core_label" in batch
    assert "spurious_label" in batch
    assert batch["image"].shape[-2:] == (224, 224)  # CenterCrop to 224


# ── CelebADataset ─────────────────────────────────────────────────────────────

def test_celeba_import():
    from data.celeba import CelebADataset, get_celeba_loader
    assert CelebADataset is not None
    assert get_celeba_loader is not None


def test_celeba_dataset_getitem_contract():
    """Test CelebADataset wraps torchvision CelebA correctly (mock torchvision)."""
    from data.celeba import CelebADataset, SPURIOUS_IDX, CORE_IDX
    attrs = torch.zeros(40, dtype=torch.long)
    attrs[SPURIOUS_IDX] = 1
    attrs[CORE_IDX] = 0
    mock_item = (torch.zeros(3, 224, 224), attrs)

    mock_celeba = MagicMock()
    mock_celeba.__len__ = MagicMock(return_value=10)
    mock_celeba.__getitem__ = MagicMock(return_value=mock_item)

    with patch("data.celeba.TorchCelebA", return_value=mock_celeba):
        ds = CelebADataset(root="/fake", split="val")
        ds._celeba = mock_celeba
        item = ds[0]

    assert "image" in item
    assert "core_label" in item
    assert "spurious_label" in item
    assert item["spurious_label"] == 1
    assert item["core_label"] == 0
