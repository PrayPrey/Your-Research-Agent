import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import torch
import numpy as np
from config import ExperimentConfig, TrainConfig, DFRConfig, AnalysisConfig, PathConfig
from feature_extractor import FeatureExtractor
from train_backbone import BackboneTrainer, build_model


@pytest.fixture
def cfg(tmp_path):
    train = TrainConfig(
        data_root="/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds",
        checkpoint_dir=str(tmp_path / "checkpoints"),
        max_epochs=1,
        checkpoint_epochs=[1],
        seeds=[1],
        num_workers=0,
        batch_size=8,
    )
    return ExperimentConfig(
        train=train,
        dfr=DFRConfig(),
        analysis=AnalysisConfig(conditions=[1]),
        paths=PathConfig(
            checkpoint_dir=str(tmp_path / "checkpoints"),
            results_dir=str(tmp_path / "results"),
            figures_dir=str(tmp_path / "figures"),
        ),
    )


@pytest.fixture
def ckpt_path(cfg, tmp_path):
    trainer = BackboneTrainer(cfg, "cpu")
    result = trainer.train_seed(1)
    return result[1]


def test_feature_shape(cfg, ckpt_path):
    extractor = FeatureExtractor(device="cpu")
    feats, labels, groups = extractor.extract_split(
        cfg.train.data_root, "val", cfg, ckpt_path
    )
    assert feats.shape[1] == 2048


def test_backbone_frozen(ckpt_path):
    extractor = FeatureExtractor(device="cpu")
    backbone = extractor.load_backbone(ckpt_path)
    for param in backbone.parameters():
        assert not param.requires_grad


def test_group_ids_range(cfg, ckpt_path):
    extractor = FeatureExtractor(device="cpu")
    feats, labels, groups = extractor.extract_split(
        cfg.train.data_root, "val", cfg, ckpt_path
    )
    assert set(np.unique(groups)).issubset({0, 1, 2, 3})
