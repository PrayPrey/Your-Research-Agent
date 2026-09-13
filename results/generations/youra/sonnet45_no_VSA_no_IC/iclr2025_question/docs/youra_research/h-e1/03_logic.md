# Logic Design: h-e1 - Uncertainty Quantification for Selective Prediction

**Date:** 2026-08-20
**Hypothesis:** EXISTENCE
**Status:** PoC
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field (existing h-e1 tests different hypothesis - VACP)
**Status:** Clean slate - designing new APIs for 6 UQ methods
**Analyzed Path:** experiments/h-e1/ (previous VACP implementation - ignore)
**Relevant Symbols:** None - new implementation

---

## Knowledge Base Patterns Applied

Applied: Standard PyTorch calibration patterns (LBFGS optimizer for temperature, quantile estimation for conformal)

---

## A-3: Temperature Scaling + Conformal Prediction [Complexity: 11, Budget: 2]

### API Signatures

```python
# uq/methods.py
import torch
from torch import Tensor
from typing import List, Tuple

class TemperatureScaling:
    """Calibrate logits via learnable temperature parameter."""
    
    def __init__(self):
        self.temperature: float = 1.0  # Fitted value
    
    def calibrate(
        self,
        logits: List[Tensor],  # N × [V]
        labels: List[int],     # N binary labels
        max_iter: int = 50
    ) -> float:
        """Fit T via LBFGS. Returns: optimal temperature."""
        # logits[i]: [V] vocabulary logits for sample i
        # labels[i]: 1 (incorrect) or 0 (correct)
        ...
    
    def compute_uncertainty(self, logits: Tensor, T: float) -> float:
        """Uncertainty = 1 - max(softmax(logits/T)). logits: [V] -> scalar."""
        ...


class ConformalPrediction:
    """Nonconformity score calibration via quantile."""
    
    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha
        self.threshold: float = 0.0  # (1-alpha) quantile
    
    def calibrate(
        self,
        logits: List[Tensor],  # N × [V]
        labels: List[int]      # N binary labels
    ) -> float:
        """Compute nonconformity scores, return 90th percentile."""
        # score = 1 - max_prob
        # threshold = quantile(scores, 1 - alpha)
        ...
    
    def compute_uncertainty(self, logits: Tensor) -> float:
        """Uncertainty = 1 - max(softmax(logits)). logits: [V] -> scalar."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [V] | Vocabulary logits (V ≈ 32k for Llama) |
| probs | [V] | Softmax probabilities |
| uncertainty | scalar | 1 - max_prob |

### Pseudo-code

**Temperature Scaling:**
```
1. Initialize T = nn.Parameter(torch.ones(1))
2. Optimizer = LBFGS([T], lr=0.01, max_iter=50)
3. Loss = cross_entropy(logits / T, labels)
4. Optimize T to minimize loss
5. Return T.item()
```

**Conformal Prediction:**
```
1. For each cal sample: score = 1 - max(softmax(logits))
2. threshold = np.quantile(scores, 1 - alpha)  # 90th percentile
3. Return threshold
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Temperature calibration | LBFGS optimizer, cross-entropy loss, 50 iters |
| L-3-2 | Conformal quantile | Nonconformity score computation, numpy quantile |

---

## A-4: MC Dropout Variants (k=1/3/5/10) [Complexity: 13, Budget: 2]

### API Signatures

```python
# uq/methods.py
import torch.nn.functional as F
from scipy.stats import entropy

class MCDropout:
    """Monte Carlo dropout for epistemic uncertainty."""
    
    def __init__(self, k: int = 5, dropout_rate: float = 0.1):
        self.k = k
        self.dropout_rate = dropout_rate
    
    def enable_dropout(self, model) -> None:
        """Enable dropout layers during inference."""
        for m in model.modules():
            if isinstance(m, torch.nn.Dropout):
                m.train()  # Force dropout active
    
    def compute_uncertainty(
        self,
        questions: List[str],
        model,  # LlamaWrapper
        tokenizer
    ) -> List[float]:
        """Run k forward passes, compute entropy. Returns: N uncertainties."""
        # For each question:
        #   predictions = []  # k × [V]
        #   for _ in range(k):
        #       logits = model.generate(question)[1]  # [V]
        #       predictions.append(softmax(logits))
        #   uncertainty = entropy(mean(predictions))  # Scalar
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| predictions | [k, V] | k softmax distributions per sample |
| mean_probs | [V] | Average across k runs |
| uncertainty | scalar | Entropy of mean distribution |

### Pseudo-code

```
1. enable_dropout(model)  # Set all dropout layers to train mode
2. For each question:
     a. predictions = []
     b. For i in range(k):
          - Generate answer with dropout active
          - Extract logits [V]
          - predictions.append(softmax(logits))
     c. mean_probs = mean(predictions, dim=0)  # [V]
     d. uncertainty = entropy(mean_probs)  # scipy.stats.entropy
3. Return uncertainties (N scalars)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Dropout activation | Force train mode on dropout layers during inference |
| L-4-2 | Entropy computation | k forward passes, mean predictions, scipy entropy |

---

## Implementation Notes

### Temperature Scaling Details
- Use `torch.optim.LBFGS` for smooth convergence
- Initialize T=1.0 (no scaling baseline)
- Loss: `F.cross_entropy(logits / T, labels)`
- Constraint: T > 0 (use `T.clamp(min=1e-3)`)

### Conformal Prediction Details
- Nonconformity score: `1 - max(softmax(logits))`
- Calibration set: 327 samples (40% split)
- Quantile: `np.quantile(scores, 0.9)` for α=0.1
- No temperature scaling applied to conformal baseline

### MC Dropout Details
- Dropout rate: 0.1 (Llama default)
- Enable dropout: Set all `nn.Dropout` modules to `.train()` mode
- Prediction aggregation: Average k softmax distributions
- Uncertainty: Shannon entropy of averaged distribution
- 4 variants: k ∈ {1, 3, 5, 10}

### PoC Simplifications
- Single temperature parameter (no per-layer scaling)
- Fixed dropout rate (no hyperparameter tuning)
- Shannon entropy only (no variance-based metrics)
- No early stopping for MC dropout (always k passes)

---

## External Dependencies

No base hypothesis code dependencies. Self-contained implementation.
