# Algorithm Injection Guide (Mode B)

> **Reference Guide for Phase 5 Step 7 - Algorithm Injection Task**
> Template for injecting OUR algorithm into baseline's training loop

---

## Purpose

Inject OUR algorithm/optimizer into baseline's existing training loop while preserving baseline's model, dataset, and configuration.

**File:** `{adaptations_folder}/algorithm_injection.py`

**CRITICAL:** This does NOT replace baseline's model or dataset. It only replaces/wraps the optimizer/algorithm component.

---

## Core Principle

```
BASELINE's environment is preserved:
  ✓ Model architecture → UNCHANGED (baseline's)
  ✓ Dataset loading → UNCHANGED (baseline's)
  ✓ Hyperparameters → UNCHANGED (baseline's)
  ✓ Training loop → MINIMAL changes

ONLY the algorithm is injected:
  → Optimizer class replacement
  → Or optimizer wrapper/hook
```

---

## Injection Patterns

### Pattern 1: Optimizer Replacement (Recommended)

When our algorithm can be expressed as a custom optimizer:

```python
"""Algorithm Injection - Optimizer Replacement Pattern.

This replaces baseline's optimizer with ours while keeping
everything else unchanged.
"""

import torch
from torch.optim import Optimizer

class OurOptimizer(Optimizer):
    """Our algorithm implemented as a PyTorch optimizer.

    This optimizer implements our hypothesis methodology
    and can directly replace baseline's SGD/Adam/etc.

    Args:
        params: Model parameters (from baseline's model)
        lr: Learning rate (from baseline's config)
        **kwargs: Additional baseline optimizer arguments
    """

    def __init__(self, params, lr=0.01, **kwargs):
        defaults = dict(lr=lr, **kwargs)
        super().__init__(params, defaults)
        # Initialize our algorithm state
        self._init_our_algorithm()

    def _init_our_algorithm(self):
        """Initialize algorithm-specific state."""
        # Our algorithm initialization
        pass

    @torch.no_grad()
    def step(self, closure=None):
        """Perform a single optimization step.

        This is where our algorithm logic goes.
        """
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                # ========================================
                # OUR ALGORITHM LOGIC HERE
                # ========================================
                grad = p.grad

                # Example: Our custom update rule
                # p.data.add_(grad, alpha=-group['lr'])

                # Implement your algorithm's update rule
                self._our_update_step(p, grad, group)

        return loss

    def _our_update_step(self, param, grad, group):
        """Our algorithm's parameter update step."""
        # Implement the core algorithm here
        lr = group['lr']
        param.data.add_(grad, alpha=-lr)

def get_our_optimizer(model_params, **baseline_config):
    """Factory function to create our optimizer.

    Usage in baseline's code:
        # Original: optimizer = torch.optim.SGD(model.parameters(), lr=lr)
        # Replace: optimizer = get_our_optimizer(model.parameters(), lr=lr)

    Args:
        model_params: Model parameters (baseline's model.parameters())
        **baseline_config: Baseline's optimizer config (lr, momentum, etc.)

    Returns:
        OurOptimizer instance
    """
    return OurOptimizer(model_params, **baseline_config)
```

---

### Pattern 2: Optimizer Wrapper (For Complex Algorithms)

When our algorithm needs to wrap an existing optimizer:

```python
"""Algorithm Injection - Optimizer Wrapper Pattern.

This wraps baseline's optimizer with our algorithm logic.
Useful when our algorithm modifies/augments gradient updates.
"""

import torch

class OurAlgorithmWrapper:
    """Wraps a baseline optimizer with our algorithm.

    This pattern is useful when:
    - Our algorithm needs to intercept gradient updates
    - Our algorithm works on top of any optimizer
    - We need access to baseline's optimizer internals

    Args:
        base_optimizer: Baseline's original optimizer
    """

    def __init__(self, base_optimizer):
        self.base_optimizer = base_optimizer
        self._init_our_algorithm()

    def _init_our_algorithm(self):
        """Initialize our algorithm state."""
        self.step_count = 0
        # Add algorithm-specific state

    def step(self, closure=None):
        """Perform optimization step with our algorithm.

        This method:
        1. Optionally modifies gradients before base optimizer step
        2. Calls base optimizer step
        3. Optionally applies post-step modifications
        """
        # Pre-step: Our algorithm can modify gradients
        self._pre_step_algorithm()

        # Base optimizer step
        loss = self.base_optimizer.step(closure)

        # Post-step: Our algorithm can modify parameters
        self._post_step_algorithm()

        self.step_count += 1
        return loss

    def _pre_step_algorithm(self):
        """Our algorithm's pre-step logic."""
        # Modify gradients if needed
        pass

    def _post_step_algorithm(self):
        """Our algorithm's post-step logic."""
        # Modify parameters if needed
        pass

    def zero_grad(self, set_to_none=False):
        """Pass through to base optimizer."""
        self.base_optimizer.zero_grad(set_to_none=set_to_none)

    @property
    def param_groups(self):
        """Access base optimizer's param_groups."""
        return self.base_optimizer.param_groups

def wrap_baseline_optimizer(baseline_optimizer):
    """Wrap baseline's optimizer with our algorithm.

    Usage in baseline's code:
        # Original:
        # optimizer = torch.optim.SGD(model.parameters(), lr=lr)

        # Modified:
        # optimizer = torch.optim.SGD(model.parameters(), lr=lr)
        # optimizer = wrap_baseline_optimizer(optimizer)

    Args:
        baseline_optimizer: The baseline's optimizer instance

    Returns:
        OurAlgorithmWrapper wrapping the baseline optimizer
    """
    return OurAlgorithmWrapper(baseline_optimizer)
```

---

### Pattern 3: Training Hook Injection

When our algorithm needs to inject logic at specific training points:

```python
"""Algorithm Injection - Training Hook Pattern.

This injects hooks at specific points in the training loop.
Useful for algorithms that need to act at specific moments.
"""

class OurAlgorithmHooks:
    """Provides hooks for injecting our algorithm into training.

    Usage:
        hooks = OurAlgorithmHooks(model)

        for epoch in range(epochs):
            hooks.on_epoch_start(epoch)
            for batch in dataloader:
                hooks.on_batch_start(batch)
                loss = compute_loss(...)
                loss.backward()
                hooks.on_after_backward() # Our algorithm acts here
                optimizer.step()
                hooks.on_after_step()
            hooks.on_epoch_end(epoch)
    """

    def __init__(self, model):
        self.model = model
        self._init_algorithm_state()

    def _init_algorithm_state(self):
        """Initialize algorithm state."""
        pass

    def on_epoch_start(self, epoch):
        """Called at the start of each epoch."""
        pass

    def on_batch_start(self, batch):
        """Called before processing each batch."""
        pass

    def on_after_backward(self):
        """Called after loss.backward().

        This is a common injection point for gradient-based algorithms.
        """
        # Access gradients: self.model.parameters()
        # Modify gradients if needed
        pass

    def on_after_step(self):
        """Called after optimizer.step()."""
        pass

    def on_epoch_end(self, epoch):
        """Called at the end of each epoch."""
        pass
```

---

## Integration Checklist

Before using the injection:

- [ ] Identified baseline's optimizer creation location
- [ ] Identified baseline's training loop structure
- [ ] Chose appropriate injection pattern (1, 2, or 3)
- [ ] Implemented our algorithm using chosen pattern
- [ ] Verified algorithm works with baseline's model.parameters()
- [ ] Verified algorithm preserves baseline's hyperparameters (lr, etc.)

---

## Minimal Modification Example

**Original baseline train.py:**
```python
import torch
import torch.optim as optim

model = BaselineModel()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

for epoch in range(100):
    for batch in dataloader:
        optimizer.zero_grad()
        loss = criterion(model(batch), targets)
        loss.backward()
        optimizer.step()
```

**Modified for our algorithm:**
```python
import torch
import torch.optim as optim
from algorithm_injection import get_our_optimizer # ADDED

model = BaselineModel()
# optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9) # COMMENTED
optimizer = get_our_optimizer(model.parameters(), lr=0.01, momentum=0.9) # REPLACED

for epoch in range(100):
    for batch in dataloader:
        optimizer.zero_grad()
        loss = criterion(model(batch), targets)
        loss.backward()
        optimizer.step()
```

**Changes Summary:**
- Added 1 import line
- Changed 1 line (optimizer creation)
- Everything else is UNCHANGED

---

## Test Template

```python
"""Test for algorithm injection."""

import torch
import torch.nn as nn
from algorithm_injection import OurOptimizer, get_our_optimizer

def test_optimizer_interface():
    """Test that our optimizer has standard interface."""
    model = nn.Linear(10, 2)
    optimizer = get_our_optimizer(model.parameters(), lr=0.01)

    # Test standard optimizer methods
    assert hasattr(optimizer, 'step')
    assert hasattr(optimizer, 'zero_grad')
    assert hasattr(optimizer, 'param_groups')

def test_optimizer_step():
    """Test that optimizer step updates parameters."""
    model = nn.Linear(10, 2)
    optimizer = get_our_optimizer(model.parameters(), lr=0.01)

    # Get initial params
    initial_params = [p.clone() for p in model.parameters()]

    # Forward + backward + step
    x = torch.randn(5, 10)
    y = model(x)
    loss = y.sum()
    loss.backward()
    optimizer.step()

    # Verify params changed
    for p_init, p_new in zip(initial_params, model.parameters()):
        assert not torch.equal(p_init, p_new), "Parameters should change after step"

def test_preserves_baseline_config():
    """Test that baseline's config is preserved."""
    model = nn.Linear(10, 2)
    lr = 0.05
    momentum = 0.9

    optimizer = get_our_optimizer(model.parameters(), lr=lr, momentum=momentum)

    assert optimizer.param_groups[0]['lr'] == lr
    # Add more config checks as needed

if __name__ == '__main__':
    test_optimizer_interface()
    test_optimizer_step()
    test_preserves_baseline_config()
    print("All tests passed!")
```

---

## Related Files

| File | Purpose |
|------|---------|
| `fair-comparison-principle.md` | Why we inject algorithm only |
| `step-07-adaptation-coding.md` | Orchestration step |
| `adapter-training-script.md` | How to modify baseline's train.py |
| `adapter-metrics.md` | Adding metric tracking |
| `adapter-results.md` | Saving comparison results |
