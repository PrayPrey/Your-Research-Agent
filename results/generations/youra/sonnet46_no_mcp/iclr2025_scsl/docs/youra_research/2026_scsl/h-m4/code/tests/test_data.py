import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import torch
from data.waterbirds import WaterbirdsDataset, get_waterbirds_loader

DATA_ROOT = "/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds"


@pytest.fixture
def dataset():
    return WaterbirdsDataset(root=DATA_ROOT, split="val")


def test_getitem_keys(dataset):
    item = dataset[0]
    assert "image" in item
    assert "core_label" in item
    assert "spurious_label" in item
    assert "group_id" in item


def test_group_id_formula(dataset):
    for i in range(min(20, len(dataset))):
        item = dataset[i]
        expected = 2 * item["spurious_label"].item() + item["core_label"].item()
        assert item["group_id"].item() == expected


def test_group_id_range(dataset):
    for i in range(min(50, len(dataset))):
        item = dataset[i]
        assert 0 <= item["group_id"].item() <= 3


def test_loader_batch_shapes():
    loader = get_waterbirds_loader(DATA_ROOT, "val", batch_size=4, num_workers=0)
    batch = next(iter(loader))
    assert batch["image"].shape[0] == 4
    assert batch["image"].shape[1:] == (3, 224, 224)
    assert batch["core_label"].shape == (4,)
    assert batch["group_id"].shape == (4,)
