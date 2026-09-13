"""
Tests for Metamorphic Contract Validators

Validates that metamorphic validators correctly detect:
1. Softmax sum violations (sum ≠ 1.0)
2. Dropout identity violations (output ≠ input in eval mode)
"""

import torch
import torch.nn as nn
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.metamorphic import (
    MetamorphicValidator,
    SoftmaxSumViolation,
    DropoutIdentityViolation,
    validate_metamorphic
)


class TestSoftmaxValidation:
    """Test softmax sum validation"""

    def test_valid_softmax(self):
        """Control: Valid softmax should pass validation"""
        # Valid softmax function
        def valid_softmax(x, dim=-1):
            return torch.softmax(x, dim=dim)

        # Probe input
        probe = torch.randn(4, 10)

        # Should not raise exception
        result = MetamorphicValidator.validate_softmax(
            valid_softmax, probe, dim=-1, rtol=1e-5, atol=1e-7
        )
        assert result is True

    def test_perturbed_softmax_violation(self):
        """Defect: Perturbed softmax should fail validation"""
        # Broken softmax (multiply by 0.9 to violate sum=1.0)
        def broken_softmax(x, dim=-1):
            return torch.softmax(x, dim=dim) * 0.9

        # Probe input
        probe = torch.randn(4, 10)

        # Should raise SoftmaxSumViolation
        with pytest.raises(SoftmaxSumViolation) as exc_info:
            MetamorphicValidator.validate_softmax(
                broken_softmax, probe, dim=-1, rtol=1e-5, atol=1e-7
            )

        # Verify exception contains diagnostic info
        assert exc_info.value.actual_sum < 1.0
        assert exc_info.value.tolerance == {"rtol": 1e-5, "atol": 1e-7}

    def test_softmax_edge_case_all_zeros(self):
        """Edge case: All-zero input should still produce valid softmax"""
        def valid_softmax(x, dim=-1):
            return torch.softmax(x, dim=dim)

        # All zeros - softmax normalizes to uniform distribution
        probe = torch.zeros(4, 10)

        # Should pass (softmax handles edge case)
        result = MetamorphicValidator.validate_softmax(
            valid_softmax, probe, dim=-1, rtol=1e-5, atol=1e-7
        )
        assert result is True


class TestDropoutValidation:
    """Test dropout identity validation"""

    def test_valid_dropout_eval_mode(self):
        """Control: Dropout in eval mode should be identity"""
        module = nn.Dropout(p=0.5)
        probe = torch.randn(100)

        # Should pass (dropout in eval mode is identity)
        result = MetamorphicValidator.validate_dropout_identity(
            module, probe, eval_mode=True
        )
        assert result is True

    def test_dropout_train_mode_violation(self):
        """Defect: Dropout in train mode should violate identity"""
        module = nn.Dropout(p=0.5)
        module.train()  # Force train mode
        probe = torch.randn(100)

        # Dropout in train mode (identity violated)
        with pytest.raises(DropoutIdentityViolation):
            MetamorphicValidator.validate_dropout_identity(
                module, probe, eval_mode=False  # Keep train mode
            )

    def test_dropout_forced_training_violation(self):
        """Defect: Forcing dropout even in eval mode (simulated API bug)"""
        # Simulate broken dropout that applies even in eval mode
        class BrokenDropout(nn.Module):
            def __init__(self, p=0.5):
                super().__init__()
                self.p = p

            def forward(self, x):
                # Bug: Always applies dropout regardless of training mode
                return torch.nn.functional.dropout(x, self.p, training=True)

        module = BrokenDropout(p=0.5)
        probe = torch.randn(100)

        # Should detect violation
        with pytest.raises(DropoutIdentityViolation):
            MetamorphicValidator.validate_dropout_identity(
                module, probe, eval_mode=True
            )


class TestMetamorphicDecorator:
    """Test decorator integration"""

    def test_decorator_softmax(self):
        """Test decorator catches softmax violation"""
        @validate_metamorphic(softmax=True, dim=-1)
        def my_softmax(x, dim=-1):
            return torch.softmax(x, dim=dim)

        # Valid call should work
        x = torch.randn(2, 5)
        result = my_softmax(x, dim=-1)
        assert result.shape == x.shape

    def test_decorator_broken_softmax(self):
        """Test decorator catches broken softmax"""
        @validate_metamorphic(softmax=True, dim=-1)
        def broken_softmax(x, dim=-1):
            return torch.softmax(x, dim=dim) * 0.9  # Violation

        # Should raise exception on call
        x = torch.randn(2, 5)
        with pytest.raises(SoftmaxSumViolation):
            broken_softmax(x, dim=-1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
