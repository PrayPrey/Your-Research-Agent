import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from config import ExperimentConfig, TrainConfig, DFRConfig, AnalysisConfig, PathConfig
from correlation_analyzer import CorrelationAnalyzer


@pytest.fixture
def cfg():
    return ExperimentConfig(
        train=TrainConfig(),
        dfr=DFRConfig(),
        analysis=AnalysisConfig(t_star_mean=2.0, pearson_r_threshold=0.7,
                                conditions=[1, 2, 10, 20, 30]),
        paths=PathConfig(),
    )


@pytest.fixture
def synthetic_results():
    # 3 seeds, epochs [1,2,10,20,30], improvement increases with epoch
    seeds = [1, 2, 3]
    epochs = [1, 2, 10, 20, 30]
    rng = np.random.RandomState(42)
    results = {}
    for seed in seeds:
        results[seed] = {}
        for i, epoch in enumerate(epochs):
            improvement = 0.01 * i + rng.uniform(-0.005, 0.005)
            results[seed][epoch] = {
                "erm_wga": 0.5 + rng.uniform(-0.05, 0.05),
                "dfr_wga": 0.5 + improvement + rng.uniform(-0.05, 0.05),
                "wga_improvement": improvement,
            }
    return results


def test_aggregate_across_seeds(cfg, synthetic_results):
    analyzer = CorrelationAnalyzer(cfg)
    agg = analyzer.aggregate_across_seeds(synthetic_results)
    assert set(agg.keys()) == {1, 2, 10, 20, 30}
    for epoch, metrics in agg.items():
        assert "mean_erm_wga" in metrics
        assert "mean_dfr_wga" in metrics
        assert "mean_wga_improvement" in metrics
        assert "std_wga_improvement" in metrics


def test_compute_pearson_keys(cfg, synthetic_results):
    analyzer = CorrelationAnalyzer(cfg)
    agg = analyzer.aggregate_across_seeds(synthetic_results)
    corr = analyzer.compute_pearson(agg, t_star=2.0)
    assert "pearson_r" in corr
    assert "pearson_p_twotailed" in corr
    assert "pearson_p_onetailed" in corr
    assert "epochs_past_tstar" in corr
    assert "improvements" in corr


def test_evaluate_gate_pass(cfg):
    analyzer = CorrelationAnalyzer(cfg)
    result = analyzer.evaluate_gate(0.85)
    assert result["gate_passed"] is True
    assert result["decision"] == "PASS"


def test_evaluate_gate_fail(cfg):
    analyzer = CorrelationAnalyzer(cfg)
    result = analyzer.evaluate_gate(0.5)
    assert result["gate_passed"] is False
    assert result["decision"] == "LIMITATION"
