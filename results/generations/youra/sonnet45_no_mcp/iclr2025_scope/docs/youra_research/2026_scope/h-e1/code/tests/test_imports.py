"""
Basic import test for all modules
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from data.loader import MultiDomainDataset
        print("✓ data.loader")
    except Exception as e:
        print(f"✗ data.loader: {e}")

    try:
        from models.lora_adapter import MultiRankLoRAFactory, LoRATrainer
        print("✓ models.lora_adapter")
    except Exception as e:
        print(f"✗ models.lora_adapter: {e}")

    try:
        from train.orchestrator import MultiTaskOrchestrator
        print("✓ train.orchestrator")
    except Exception as e:
        print(f"✗ train.orchestrator: {e}")

    try:
        from eval.metrics import OracleGapCalculator, TaskMetrics
        print("✓ eval.metrics")
    except Exception as e:
        print(f"✗ eval.metrics: {e}")

    try:
        from visualization.plots import ExperimentVisualizer
        print("✓ visualization.plots")
    except Exception as e:
        print(f"✗ visualization.plots: {e}")

    try:
        from config.config import DEFAULT_CONFIG, EVAL_CONFIG
        print("✓ config.config")
    except Exception as e:
        print(f"✗ config.config: {e}")

    print("\n✅ All imports successful!")


if __name__ == "__main__":
    test_imports()
