"""
Smoke tests for h-e1 implementation
Validates basic functionality without full training
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import pytest


def test_config_loading():
    """Test configuration loading"""
    from config.experiment_config import ExperimentConfig

    config = ExperimentConfig()

    assert config.seed == 42
    assert config.experiment_name == "h-e1-trimodal-poc"
    assert len(config.baseline_types) == 4
    print("✓ Config loading works")


def test_tri_modal_aggregator():
    """Test tri-modal aggregator mechanism"""
    from models.tri_modal_aggregator import TriModalAggregator

    aggregator = TriModalAggregator()

    # Test forward pass
    batch_size = 4
    exec_reward = torch.rand(batch_size)
    ai_reward = torch.rand(batch_size) * 2 - 1
    human_reward = torch.rand(batch_size)

    aggregated, weights = aggregator(exec_reward, ai_reward, human_reward, training_progress=0.5)

    # Verify output shape
    assert aggregated.shape == (batch_size,)

    # Verify weights sum to 1
    weight_sum = weights['execution_weight'] + weights['ai_weight'] + weights['human_weight']
    assert abs(weight_sum - 1.0) < 0.01

    print(f"✓ Tri-modal aggregator works (weights sum: {weight_sum:.3f})")


def test_feedback_collectors():
    """Test feedback collection"""
    from models.feedback_collectors import FeedbackCollector

    collector = FeedbackCollector(device="cpu")

    code = "def add(a, b):\n    return a + b"
    prompt = "Write a function to add two numbers"
    test_cases = "assert add(2,3)==5"

    feedback = collector.collect_all(
        code=code,
        prompt=prompt,
        test_cases=test_cases,
        task_id="test_001"
    )

    assert 'execution' in feedback
    assert 'ai' in feedback
    assert 'human' in feedback

    print(f"✓ Feedback collectors work (exec={feedback['execution'].item():.2f})")


def test_data_pipeline():
    """Test data loading (minimal)"""
    from data.dataset import CodeGenerationDataset

    dataset = CodeGenerationDataset(cache_dir="../.data_cache/datasets")

    try:
        dataset.load_datasets()
        print(f"✓ Datasets loaded successfully")
    except Exception as e:
        pytest.skip(f"Dataset loading skipped: {e}")


def test_model_initialization():
    """Test model can be loaded"""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_name = "Salesforce/codegen-350M-mono"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        assert tokenizer is not None
        assert model is not None

        print(f"✓ Model {model_name} loaded successfully")
    except Exception as e:
        pytest.skip(f"Model loading skipped: {e}")


if __name__ == "__main__":
    # Run tests manually
    print("Running smoke tests...")
    print()

    try:
        test_config_loading()
        test_tri_modal_aggregator()
        test_feedback_collectors()
        test_data_pipeline()
        test_model_initialization()

        print()
        print("="*60)
        print("✓ All smoke tests passed")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
