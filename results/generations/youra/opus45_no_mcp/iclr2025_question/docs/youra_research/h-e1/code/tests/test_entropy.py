"""Basic tests for entropy computation."""
import torch
import numpy as np
import sys
sys.path.insert(0, "..")
from entropy import compute_token_entropy


def test_entropy_non_nan():
    """Entropy should not be nan for valid logits."""
    scores = (torch.tensor([[1.0, 2.0, 3.0, 4.0]]),)
    h = compute_token_entropy(scores)
    assert not np.isnan(h), "Entropy should not be nan"
    assert h > 0, "Entropy should be positive"


def test_entropy_with_inf():
    """Entropy handles -inf in logits (zero prob tokens)."""
    scores = (torch.tensor([[float('-inf'), 10.0, 5.0, float('-inf')]]),)
    h = compute_token_entropy(scores)
    assert not np.isnan(h), "Entropy should handle -inf values"


def test_entropy_empty():
    """Empty scores returns nan."""
    h = compute_token_entropy(())
    assert np.isnan(h)


if __name__ == "__main__":
    test_entropy_non_nan()
    test_entropy_with_inf()
    test_entropy_empty()
    print("All entropy tests passed")
