import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from config import ExperimentConfig, TrainConfig, DFRConfig, AnalysisConfig, PathConfig
from dfr_module import DFRModule, worst_group_accuracy
from train_backbone import BackboneTrainer


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


def test_worst_group_accuracy_synthetic():
    preds   = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    labels  = np.array([0, 0, 1, 1, 0, 0, 1, 1])
    groups  = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    wga = worst_group_accuracy(preds, labels, groups)
    # group 2: preds=[0,1] labels=[0,0] -> acc=0.5; group 3: preds=[0,1] labels=[1,1] -> acc=0.5
    assert 0.0 <= wga <= 1.0
    assert wga == pytest.approx(0.5)


def test_fit_dfr_converges(cfg):
    dfr = DFRModule(cfg)
    rng = np.random.RandomState(0)
    feats = rng.randn(100, 2048).astype(np.float32)
    labels = rng.randint(0, 2, size=100)
    clf = dfr._fit_dfr(feats, labels)
    assert hasattr(clf, "coef_")
    assert clf.coef_.shape == (1, 2048)


def test_evaluate_checkpoint_keys(cfg, tmp_path):
    trainer = BackboneTrainer(cfg, "cpu")
    ckpt_map = trainer.train_seed(1)
    ckpt_path = ckpt_map[1]

    dfr = DFRModule(cfg)
    rng = np.random.RandomState(42)
    val_feats = rng.randn(50, 2048).astype(np.float32)
    val_labels = rng.randint(0, 2, size=50)
    test_feats = rng.randn(50, 2048).astype(np.float32)
    test_labels = rng.randint(0, 2, size=50)
    test_groups = rng.randint(0, 4, size=50)

    result = dfr.evaluate_checkpoint(
        ckpt_path, val_feats, val_labels, test_feats, test_labels, test_groups, "cpu"
    )
    assert "erm_wga" in result
    assert "dfr_wga" in result
    assert "wga_improvement" in result
    assert "feature_dim" in result
    assert result["feature_dim"] == 2048
