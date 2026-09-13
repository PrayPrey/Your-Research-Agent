# 03_logic.md — h-c1: Feedback Diversity Threshold

Hypothesis: superadditivity requires H(Schema|ErrorClass) > 2.5 bits.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: FeedbackDiversityController [Complexity: 7, Budget: 3]

**Applied**: Standard PyTorch (entropy via Shannon formula, no KB match needed)

### API Signatures

```python
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Tuple
import torch
from torch import Tensor

class ErrorClass(IntEnum):
    SYNTAX = 0
    LOGIC = 1
    TYPE = 2
    RUNTIME = 3

@dataclass
class FeedbackItem:
    schema_id: int       # discrete feedback-schema label
    error_class: ErrorClass
    payload: dict

class FeedbackDiversityController:
    def __init__(self, n_schemas: int, target_entropy: float = 2.5, tol: float = 0.05):
        """target_entropy in bits; controls batch composition."""
        ...

    def compute_entropy(self, items: List[FeedbackItem]) -> float:
        """H(Schema|ErrorClass) in bits. See pseudo-code."""
        ...

    def filter_batch(self, pool: List[FeedbackItem], batch_size: int, mode: str) -> List[FeedbackItem]:
        """mode: 'low' | 'high' | 'target'. Returns batch_size items."""
        ...

    def label_error_class(self, raw_error: str) -> ErrorClass:
        """Rule-based classifier, min 4 categories."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| schema_counts | [E, S] | E=n_error_classes, S=n_schemas, co-occurrence counts |
| p_cond | [E, S] | row-normalized conditional probs p(schema\|error) |
| entropy_per_class | [E] | H(Schema\|ErrorClass=e) |
| H_total | scalar | weighted avg over error-class marginal p(e) |

### Pseudo-code

```
compute_entropy(items):
  1. counts[E,S] = histogram2d(items.error_class, items.schema_id)
  2. p_e = counts.sum(dim=1) / counts.sum()               # [E] marginal
  3. p_cond = counts / counts.sum(dim=1, keepdim=True)    # [E,S], row-normalize
  4. H_e = -sum(p_cond * log2(p_cond + eps), dim=1)        # [E], per-class entropy
  5. H_total = sum(p_e * H_e)                              # scalar, conditional entropy
  return H_total

filter_batch(pool, batch_size, mode):
  1. group pool by (error_class, schema_id)
  2. if mode == 'low':    sample from <=2 dominant schemas per error class (concentrate)
  3. if mode == 'high':   sample uniformly across all schemas per error class (oversample rare)
  4. if mode == 'target': greedy swap items in/out of a random batch,
                          accept swap if |compute_entropy(batch') - target_entropy| decreases
                          stop when within tol or max_iter reached
  5. return batch
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | entropy_fn | Implement `compute_entropy` incl. numerical eps guard |
| L-1-2 | batch_filter | Implement 3 sampling modes in `filter_batch` |
| L-1-3 | error_classifier | Rule-based `label_error_class`, 4 categories |

---

## A-2: Actor-Critic under Diversity Conditions [Complexity: 6, Budget: 2]

**Applied**: Standard PyTorch (shared-trunk actor-critic, discrete action space)

### API Signatures

```python
class ActorCritic(torch.nn.Module):
    def __init__(self, obs_dim: int, n_actions: int, hidden: int = 128):
        ...

    def forward(self, obs: Tensor) -> Tuple[Tensor, Tensor]:
        """obs: [B, obs_dim] -> (logits [B, n_actions], value [B, 1])"""
        ...

    def act(self, obs: Tensor) -> Tuple[Tensor, Tensor]:
        """Sample action. Returns (action [B], log_prob [B])"""
        ...

def train_step(
    model: ActorCritic,
    batch: List[FeedbackItem],
    diversity_condition: str,   # 'low' | 'high' | 'target'
    gamma: float = 0.99,
) -> dict:
    """Returns {'policy_loss', 'value_loss', 'entropy_bonus', 'H_batch'}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| obs | [B, obs_dim] | encoded (state, feedback_schema, error_class) |
| logits | [B, n_actions] | actor head |
| value | [B, 1] | critic head |
| advantage | [B] | returns - value.squeeze() |

---

## A-3: Interaction Effect & Statistical Test [Complexity: 5, Budget: 2]

**Applied**: Standard PyTorch/SciPy (two-way ANOVA interaction term)

### API Signatures

```python
@dataclass
class ConditionResult:
    diversity_level: str   # 'low' | 'high'
    treatment: str         # 'baseline' | 'proposed'
    reward: List[float]    # per-run episodic reward

def compute_interaction_effect(results: List[ConditionResult]) -> dict:
    """
    2x2 factorial: diversity(low/high) x treatment(baseline/proposed).
    Returns {'interaction_F', 'interaction_p', 'effect_size_eta2',
             'superadditivity_delta'}.
    """
    ...
```

### Statistical Test Formulation

```
Design: 2 (diversity: low/high) x 2 (treatment: baseline/proposed) between-subjects.

Superadditivity metric:
  delta = [R(high, proposed) - R(high, baseline)] - [R(low, proposed) - R(low, baseline)]

Test: two-way ANOVA, interaction term diversity x treatment.
  H0: interaction effect = 0 (no threshold dependency)
  H1: interaction effect > 0 (diversity amplifies treatment benefit)

Decision rule for h-c1:
  Confirmed if: interaction_p < 0.05 AND delta > 0 AND H(high) > 2.5 bits > H(low)
  Rejected if: interaction_p >= 0.05 OR delta <= 0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | anova_interaction | Two-way ANOVA via scipy/statsmodels, extract F/p/eta2 |
| L-3-2 | delta_calc | Compute `superadditivity_delta` per run, aggregate CI |

---

## Verification Protocol

1. Generate feedback pools at 3 entropy levels: low (~1.0 bit), target (2.5±0.05 bit), high (~3.5 bit) via `filter_batch`.
2. Assert `compute_entropy(batch)` matches intended level before training (unit check).
3. Train baseline vs proposed under low/high conditions (4 cells, ≥5 seeds each).
4. Run `compute_interaction_effect`; check decision rule above.
5. Self-check: `assert abs(H_measured - H_target) < tol` for every generated batch; `assert n_error_classes >= 4`.
