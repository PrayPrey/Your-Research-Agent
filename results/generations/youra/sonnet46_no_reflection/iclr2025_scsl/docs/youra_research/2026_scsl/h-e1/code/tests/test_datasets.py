"""Tests for dataset classes."""
import os
import sys
import pytest
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB_DATA = os.path.join(CODE_DIR, 'data', 'waterbirds', 'waterbird_complete95_forest2water2')
CELEBA_DATA = os.path.join(CODE_DIR, 'data', 'celeba', 'celebA_v1.0')


def test_waterbirds_import():
    from data.datasets import WaterBirdsDataset
    assert WaterBirdsDataset is not None


def test_celeba_import():
    from data.datasets import CelebADataset
    assert CelebADataset is not None


def test_get_transforms():
    from data.datasets import get_transforms
    t = get_transforms(augment=False, dataset_name='waterbirds')
    assert t is not None


@pytest.mark.skipif(not os.path.exists(WB_DATA), reason='Waterbirds data not available')
def test_waterbirds_dataset():
    from data.datasets import WaterBirdsDataset
    ds = WaterBirdsDataset(WB_DATA, 'train', augment=False)
    assert len(ds) > 0
    img, y, g = ds[0]
    assert isinstance(img, torch.Tensor)
    assert img.shape == (3, 224, 224)
    assert y in [0, 1]
    assert g in [0, 1, 2, 3]


@pytest.mark.skipif(not os.path.exists(CELEBA_DATA), reason='CelebA data not available')
def test_celeba_dataset():
    from data.datasets import CelebADataset
    ds = CelebADataset(CELEBA_DATA, 'train', augment=False)
    assert len(ds) > 0
    img, y, g = ds[0]
    assert isinstance(img, torch.Tensor)
    assert img.shape == (3, 224, 224)
    assert y in [0, 1]
    assert g in [0, 1, 2, 3]
