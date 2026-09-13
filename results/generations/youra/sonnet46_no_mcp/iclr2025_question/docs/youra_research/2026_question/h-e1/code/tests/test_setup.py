"""Tests for task-001: environment setup."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Verify all required packages import without error."""
    import torch
    import transformers
    import datasets
    import selfcheckgpt
    import bert_score
    import sklearn
    import numpy
    import scipy
    import matplotlib
    import seaborn
    import nltk
    import tqdm


def test_gpu_available():
    """Verify GPU is available."""
    import torch
    assert torch.cuda.is_available(), "CUDA not available"


def test_output_dirs():
    """Verify required output directories exist."""
    code_dir = Path(__file__).parent.parent
    required_dirs = [
        code_dir / "data",
        code_dir / "outputs" / "greedy_logits",
        code_dir / "outputs" / "uq_scores",
        code_dir / "results",
        code_dir / "figures",
    ]
    for d in required_dirs:
        d.mkdir(parents=True, exist_ok=True)
        assert d.exists(), f"Directory not found: {d}"
