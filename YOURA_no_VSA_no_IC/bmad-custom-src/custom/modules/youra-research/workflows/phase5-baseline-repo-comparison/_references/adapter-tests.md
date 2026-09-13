# Adapter: Integration Tests (Mode B)

> **Reference Guide for Phase 5 Step 7 - Mode B Integration Tests**
> Template for integration tests of algorithm injection adaptation

---

## Purpose

Test that all Mode B adaptation components work correctly.
Mode B tests verify: algorithm injection, metric tracking, and results saving.

> **Mode B:** Baseline's model, dataset, and config are UNCHANGED.
> We only inject our algorithm/optimizer. Tests verify the injection works correctly.

**Directory:** `{adaptations_folder}/tests/`

---

## Test File Template

```python
"""Integration tests for {repo_name} adaptation (Mode B).

Mode B: Algorithm injection only.
Baseline's model, dataset, config are UNCHANGED.

Run with: pytest tests/ -v
"""

import pytest
import torch
import torch.nn as nn
import os
import sys

# Add adaptation modules to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAlgorithmInjection:
    """Test algorithm injection (Mode B core component)."""

    def test_optimizer_interface(self):
        """Test that our optimizer has standard PyTorch optimizer interface."""
        from algorithm_injection import get_our_optimizer

        model = nn.Linear(10, 2)
        optimizer = get_our_optimizer(model.parameters(), lr=0.01)

        assert hasattr(optimizer, 'step')
        assert hasattr(optimizer, 'zero_grad')
        assert hasattr(optimizer, 'param_groups')

    def test_optimizer_step_updates_params(self):
        """Test that optimizer step actually updates parameters."""
        from algorithm_injection import get_our_optimizer

        model = nn.Linear(10, 2)
        optimizer = get_our_optimizer(model.parameters(), lr=0.01)

        initial_params = [p.clone() for p in model.parameters()]

        x = torch.randn(5, 10)
        y = model(x)
        loss = y.sum()
        loss.backward()
        optimizer.step()

        for p_init, p_new in zip(initial_params, model.parameters()):
            assert not torch.equal(p_init, p_new), "Parameters should change after step"

    def test_preserves_baseline_config(self):
        """Test that baseline's hyperparameters are preserved."""
        from algorithm_injection import get_our_optimizer

        model = nn.Linear(10, 2)
        lr = 0.05

        optimizer = get_our_optimizer(model.parameters(), lr=lr)

        assert optimizer.param_groups[0]['lr'] == lr

class TestMetrics:
    """Test metric computation."""

    def test_compute_psi(self):
        """Test psi computation returns valid float."""
        from metrics import compute_psi

        # Use a simple model for testing
        model = nn.Linear(10, 2)
        # Create a simple dataloader
        dataset = torch.utils.data.TensorDataset(
            torch.randn(32, 10), torch.randint(0, 2, (32,))
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=16)

        psi = compute_psi(model, loader, device='cpu')

        assert isinstance(psi, float)

    def test_metric_tracker(self):
        """Test MetricTracker functionality."""
        from metrics import MetricTracker

        tracker = MetricTracker()
        tracker.record(epoch=1, lr=0.01, seed=42, psi=0.5, loss=0.3)
        tracker.record(epoch=2, lr=0.01, seed=42, psi=0.6, loss=0.2)

        history = tracker.get_history()

        assert len(history) == 2
        assert history[-1]['psi'] == 0.6

class TestResultsSaver:
    """Test ResultsSaver functionality."""

    def test_save_results(self, tmp_path):
        """Test saving results to CSV."""
        from results_saver import ResultsSaver

        output_path = tmp_path / "test_results.csv"
        saver = ResultsSaver(str(output_path), method_name="test_baseline")

        saver.add_run(lr=0.01, seed=42, primary_metric=0.8, dataset="primary")
        saver.save()

        assert output_path.exists()

        import pandas as pd
        df = pd.read_csv(output_path)
        assert len(df) == 1
        assert df['method'].iloc[0] == 'test_baseline'
```

---

## Running Tests

```bash
# Navigate to adaptations folder
cd {adaptations_folder}

# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_integration.py::TestAlgorithmInjection -v

# Run with coverage
pytest tests/ -v --cov=.
```

---

## Related Files (Mode B)

| File | Purpose |
|------|---------|
| `step-07-adaptation-coding.md` | Orchestration step |
| `step-08-validation.md` | Runs these tests |
| `algorithm-injection.md` | Algorithm injection being tested |
| `adapter-metrics.md` | Metrics being tested |
| `adapter-results.md` | Results saver being tested |
| `adapter-training-script.md` | Training script modification being tested |
