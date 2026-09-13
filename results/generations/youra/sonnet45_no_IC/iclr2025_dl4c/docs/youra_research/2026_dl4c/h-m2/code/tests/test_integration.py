"""
Integration Testing - Smoke test for Phase 1 components
Task: A-7
Hypothesis: h-m1
"""

import pytest
import torch
import sys
import os

# Add paths
code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, code_dir)

# Direct imports
import importlib.util

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

agg_mod = import_module_from_path("phase1_agg", os.path.join(code_dir, "models/phase1_tri_modal_aggregator.py"))
logger_mod = import_module_from_path("checkpoint_logger", os.path.join(code_dir, "utils/checkpoint_logger.py"))
metrics_mod = import_module_from_path("phase1_metrics", os.path.join(code_dir, "evaluation/phase1_metrics.py"))

Phase1AnalysisTriModalAggregator = agg_mod.Phase1AnalysisTriModalAggregator
CheckpointLogger = logger_mod.CheckpointLogger
Phase1Analyzer = metrics_mod.Phase1Analyzer


def test_phase1_aggregator():
    """Test Phase1AnalysisTriModalAggregator initialization and forward pass."""
    aggregator = Phase1AnalysisTriModalAggregator()

    # Test forward pass
    batch_size = 4
    exec_r = torch.rand(batch_size)
    ai_r = torch.rand(batch_size)
    human_r = torch.rand(batch_size)
    progress = 0.15  # Phase 1

    output = aggregator.forward(exec_r, ai_r, human_r, progress)

    assert output.shape == (batch_size,)
    assert torch.all(output >= 0)
    assert torch.all(output <= 1)

    print("✓ Phase1Aggregator test passed")


def test_checkpoint_logger(tmp_path):
    """Test CheckpointLogger save and load."""
    logger = CheckpointLogger(str(tmp_path))

    # Log weight checkpoint
    logger.log_weights(0.1, 0.7, 0.2, 0.1)
    logger.log_pass_at_1(0.1, 0.45)

    # Load trajectories
    weight_traj = logger.load_weights_trajectory()
    pass_at_1_traj = logger.load_pass_at_1_trajectory()

    assert len(weight_traj) == 1
    assert len(pass_at_1_traj) == 1
    assert weight_traj[0]['progress'] == 0.1
    assert pass_at_1_traj[0]['pass_at_1'] == 0.45

    print("✓ CheckpointLogger test passed")


def test_phase1_analyzer():
    """Test Phase1Analyzer metrics computation."""
    # Mock data
    weight_traj = [
        {'progress': 0.0, 'execution_weight': 0.8, 'ai_weight': 0.1, 'human_weight': 0.1},
        {'progress': 0.1, 'execution_weight': 0.75, 'ai_weight': 0.15, 'human_weight': 0.1},
        {'progress': 0.2, 'execution_weight': 0.7, 'ai_weight': 0.2, 'human_weight': 0.1},
        {'progress': 0.3, 'execution_weight': 0.65, 'ai_weight': 0.25, 'human_weight': 0.1},
        {'progress': 0.7, 'execution_weight': 0.3, 'ai_weight': 0.5, 'human_weight': 0.2},
        {'progress': 1.0, 'execution_weight': 0.2, 'ai_weight': 0.4, 'human_weight': 0.4}
    ]

    pass_at_1_traj = [
        {'progress': 0.0, 'pass_at_1': 0.2},
        {'progress': 0.1, 'pass_at_1': 0.3},
        {'progress': 0.2, 'pass_at_1': 0.4},
        {'progress': 0.3, 'pass_at_1': 0.5},
        {'progress': 0.7, 'pass_at_1': 0.6},
        {'progress': 1.0, 'pass_at_1': 0.65}
    ]

    analyzer = Phase1Analyzer(weight_traj, pass_at_1_traj)

    # Test metric 1
    dominance = analyzer.compute_weight_dominance()
    assert 'passed' in dominance
    assert 'checkpoints' in dominance

    # Test metric 2
    improvement = analyzer.compute_pass_at_1_improvement_rates()
    assert 'phase1_rate' in improvement
    assert 'later_rate' in improvement

    # Test metric 3
    correlation = analyzer.compute_weight_correlation()
    assert 'correlation' in correlation
    assert 'p_value' in correlation

    # Test gate validation
    gate_result = analyzer.validate_gate_criteria()
    assert gate_result['gate_result'] in ['PASS', 'FAIL']

    print("✓ Phase1Analyzer test passed")


if __name__ == "__main__":
    test_phase1_aggregator()
    test_checkpoint_logger(torch.hub.get_dir() + "/test_checkpoint")
    test_phase1_analyzer()
    print("\n✅ All integration tests passed!")
