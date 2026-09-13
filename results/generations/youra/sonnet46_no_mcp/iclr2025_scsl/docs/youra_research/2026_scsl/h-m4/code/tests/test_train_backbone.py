import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import torch
from config import ExperimentConfig, TrainConfig, DFRConfig, AnalysisConfig, PathConfig
from train_backbone import BackboneTrainer, build_model


@pytest.fixture
def cfg(tmp_path):
    train = TrainConfig(
        data_root="/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds",
        checkpoint_dir=str(tmp_path / "checkpoints"),
        max_epochs=2,
        checkpoint_epochs=[1, 2],
        seeds=[1],
        num_workers=0,
    )
    return ExperimentConfig(
        train=train,
        dfr=DFRConfig(),
        analysis=AnalysisConfig(conditions=[1, 2]),
        paths=PathConfig(
            checkpoint_dir=str(tmp_path / "checkpoints"),
            results_dir=str(tmp_path / "results"),
            figures_dir=str(tmp_path / "figures"),
        ),
    )


def test_checkpoint_exists_false(cfg):
    trainer = BackboneTrainer(cfg, "cpu")
    assert not trainer._checkpoint_exists(1, 1)


def test_checkpoint_exists_after_save(cfg, tmp_path):
    trainer = BackboneTrainer(cfg, "cpu")
    model = build_model(num_classes=2, pretrained=False)
    ckpt_dir = os.path.join(cfg.paths.checkpoint_dir, "seed_1")
    os.makedirs(ckpt_dir, exist_ok=True)
    trainer._save_checkpoint(model, 1, 1, ckpt_dir)
    assert trainer._checkpoint_exists(1, 1)


def test_train_seed_returns_correct_keys(cfg):
    trainer = BackboneTrainer(cfg, "cpu")
    result = trainer.train_seed(1)
    assert set(result.keys()) == {1, 2}


def test_checkpoint_files_created(cfg):
    trainer = BackboneTrainer(cfg, "cpu")
    result = trainer.train_seed(1)
    for epoch, path in result.items():
        assert os.path.exists(path), f"Checkpoint missing: {path}"
