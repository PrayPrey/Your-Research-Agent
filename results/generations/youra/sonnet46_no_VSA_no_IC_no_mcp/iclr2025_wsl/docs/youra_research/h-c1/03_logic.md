# Logic Design: H-C1 — Sign-Flip Canonicalization Uniqueness Audit

**Hypothesis:** H-C1  
**Type:** CONDITION  
**Date:** 2026-08-27  
**Logic Budget:** 5 subtasks  

---

## Codebase Analysis (Serena)

*Serena MCP not available (no-MCP session). Analysis performed via prior hypothesis context.*

**H-M3 prior implementation patterns:**
- `exact_majority_sign`: `torch.sign(weights).sum(dim=1)` → `torch.sign(row_sign_sums)` — O(n) per neuron
- `canonicalize_sign_flip_m2`: diagonal matrix construction `torch.diag(signs)`, then `D @ W1`, `W2 @ D`
- Pattern: minimal tensor ops, no loops over neurons — fully vectorized
- `audit_uniqueness`: Python loop over models (N=500 × trivial ops, CPU is fine)

Applied: vectorized-majority-sign pattern (H-M3 prior)  
Applied: diagonal-matrix-sign-flip pattern (Godfrey et al. 2022 canonical form)  
Applied: per-model-flag-accumulation audit pattern  

---

## External Dependencies API (H-M3)

From H-M3 prior implementation (reference only — reimplemented in H-C1):

```python
# H-M3 canonicalize.py — reference signatures
def canonicalize_sign_flip(W1: torch.Tensor, W2: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Approximation: uses sum(dim=1) not sign(W).sum(dim=1). Replaced in H-C1."""
    ...

# H-M3 data loading (confirmed format):
# W1: (64, 784), W2: (10, 64) — extracted from zoo record dict
```

H-C1 uses exact majority sign (corrected from H-M3 approximation).

---

## Module APIs

### canonicalize.py

```python
import torch

def exact_majority_sign(weights: torch.Tensor) -> torch.Tensor:
    """
    Compute exact majority sign per row.
    
    Args:
        weights: (d_out, d_in) — weight matrix, any dtype castable to float
    Returns:
        majority: (d_out,) — values in {-1, 0, +1}; 0 means exact tie
    
    Tensor shapes:
        weights: (d_out, d_in)
        row_sign_sums: (d_out,)  = torch.sign(weights).sum(dim=1)
        majority: (d_out,)       = torch.sign(row_sign_sums)
    
    Notes:
        - Exact majority: counts +1 vs -1 per row (ignores 0-weight entries)
        - Returns 0 for exact ties (caller handles tie-breaking)
        - For d_in=784: tie probability per neuron ≈ negligible (Binomial argument)
    """
    row_sign_sums = torch.sign(weights.float()).sum(dim=1)  # (d_out,)
    return torch.sign(row_sign_sums)                         # (d_out,)


def canonicalize_sign_flip_m2(
    W1: torch.Tensor,  # (64, 784)
    W2: torch.Tensor,  # (10, 64)
) -> tuple[torch.Tensor, torch.Tensor, bool]:
    """
    Apply sign-flip canonicalization to M=2 MLP weight pair.
    
    Args:
        W1: (64, 784) — hidden layer incoming weights
        W2: (10, 64)  — output layer incoming weights
    Returns:
        W1_canon: (64, 784)
        W2_canon: (10, 64)
        is_degenerate: bool — True if any neuron had exact sign tie
    
    Algorithm:
        1. majority = exact_majority_sign(W1)   # (64,)
        2. ties = (majority == 0)               # neurons with exact tie
        3. majority[ties] = 1                   # tie-breaking: default +1
        4. D = diag(majority.float())           # (64, 64)
        5. W1_canon = D @ W1                    # flip incoming weights
        6. W2_canon = W2 @ D                    # flip outgoing weights (preserve f(x))
    
    Invariant:
        W2_canon @ relu(W1_canon @ x) == W2 @ relu(W1 @ x)  [for any x, when majority = ±1]
    """
    majority = exact_majority_sign(W1)          # (64,)
    ties = (majority == 0)
    is_degenerate: bool = ties.any().item()
    majority = majority.clone()
    majority[ties] = 1                          # tie-breaking
    D = torch.diag(majority.float())            # (64, 64)
    W1_canon = D @ W1.float()                  # (64, 784)
    W2_canon = W2.float() @ D                  # (10, 64)
    return W1_canon, W2_canon, is_degenerate
```

---

### data_loader.py

```python
from datasets import load_dataset
import torch
import numpy as np
from typing import List, Tuple

def load_zoo_sample(
    n: int = 500,
    seed: int = 1,
    hf_id: str = "MarcBrun/model-zoos",
    split: str = "train",
) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    """
    Load N models from Schürholt MNIST zoo via HuggingFace.
    
    Args:
        n: number of models to sample (default 500)
        seed: random seed for sampling (default 1, matches H-M3)
        hf_id: HuggingFace dataset identifier
        split: dataset split to use
    Returns:
        models: list of (W1, W2) tuples
                W1: (64, 784) float32 tensor
                W2: (10, 64)  float32 tensor
    
    Tensor shapes:
        W1: (64, 784)  — hidden layer incoming weights
        W2: (10, 64)   — output layer incoming weights
    
    Notes:
        - Sampling is uniform random without stratification
        - Same seed as H-M3 for reproducibility comparison
        - Auto-downloads to HuggingFace cache (no manual download needed)
    """
    zoo = load_dataset(hf_id, split=split)
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(zoo), size=n, replace=False)
    models = []
    for idx in indices:
        record = zoo[int(idx)]
        W1 = _extract_weight(record, key_W1="weight_0")   # adjust key per actual schema
        W2 = _extract_weight(record, key_W2="weight_1")
        assert W1.shape == (64, 784), f"Unexpected W1 shape: {W1.shape}"
        assert W2.shape == (10, 64),  f"Unexpected W2 shape: {W2.shape}"
        models.append((W1, W2))
    return models


def _extract_weight(record: dict, key_W1: str = "weight_0", key_W2: str = "weight_1"):
    """Extract and reshape weight tensor from zoo record. Key names TBD from actual schema."""
    # Implementation: inspect record keys, reshape flat arrays to (64,784) and (10,64)
    # Phase 4 coder must inspect actual HuggingFace record schema (confirmed in H-E1)
    ...
```

---

### audit.py

#### Subtask L-3-1: Audit Loop Core
```python
from typing import List, Dict, Tuple
import torch
from canonicalize import canonicalize_sign_flip_m2

AuditResult = Dict  # {degenerate: bool, idempotent: bool, tied_neuron_count: int}

def run_audit(
    models: List[Tuple[torch.Tensor, torch.Tensor]],
) -> Tuple[List[AuditResult], Dict]:
    """
    Run uniqueness and idempotency audit on all models.
    
    Args:
        models: list of (W1, W2) tuples, N=500
    Returns:
        results: list of AuditResult per model
        summary: {fraction_unique, fraction_idempotent, degenerate_count, n_total}
    
    Algorithm:
        For each (W1, W2):
            1. Self-check on first model (assert idempotency)
            2. Canonicalize: W1c, W2c, degen = canonicalize_sign_flip_m2(W1, W2)
            3. Idempotency: W1cc, W2cc, _ = canonicalize_sign_flip_m2(W1c, W2c)
            4. idempotent = allclose(W1c, W1cc) and allclose(W2c, W2cc)
            5. tied_neuron_count = number of tied neurons (if degen)
            6. Record {degenerate, idempotent, tied_neuron_count, model_idx}
    """
    ...
```

#### Subtask L-3-2: Degeneracy Statistics
```python
def compute_degeneracy_stats(results: List[AuditResult]) -> Dict:
    """
    Characterize degenerate cases (conditional — only if any found).
    
    Args:
        results: output of run_audit
    Returns:
        stats: {
            mean_tied_neurons_per_degenerate_model: float,
            max_tied_neurons: int,
            degenerate_indices: List[int],
        }
        Returns empty dict if no degenerate cases.
    
    Notes:
        - Only called if summary['degenerate_count'] > 0
        - tied_neuron_count per model already recorded in AuditResult
    """
    ...
```

#### Subtask L-2-1: Canonicalization Self-Check (Assert)
```python
def self_check_idempotency(W1: torch.Tensor, W2: torch.Tensor) -> None:
    """
    Assert idempotency on one model before full audit.
    Raises AssertionError if algorithm is broken.
    
    Args:
        W1: (64, 784), W2: (10, 64) — first zoo model
    Raises:
        AssertionError: if canon(canon(W)) != canon(W)
    """
    W1c, W2c, _ = canonicalize_sign_flip_m2(W1, W2)
    W1cc, W2cc, _ = canonicalize_sign_flip_m2(W1c, W2c)
    assert torch.allclose(W1c, W1cc), "Idempotency violated on W1"
    assert torch.allclose(W2c, W2cc), "Idempotency violated on W2"
```

#### Subtask L-2-2: Exact Majority Sign Algorithm
```python
# Covered in canonicalize.py API above.
# Key invariant: majority = sign(sign(W).sum(dim=1))
# Edge case: zero-weight row → sum=0 → sign(0)=0 → tie
```

#### Subtask L-4-1: Weight Statistics for Tied Neurons
```python
def weight_stats_tied_neurons(
    models: List[Tuple[torch.Tensor, torch.Tensor]],
    degenerate_indices: List[int],
) -> Dict:
    """
    Compute weight L1-norm and std for tied neurons in degenerate models.
    
    Args:
        models: full model list
        degenerate_indices: indices of degenerate models
    Returns:
        stats: {mean_l1_norm_tied, std_l1_norm_tied, mean_weight_std_tied}
    
    Notes:
        - A neuron is "tied" if its majority sign is 0 (exactly equal +/- counts)
        - Weight stats characterize whether ties correlate with near-zero weights
    """
    ...
```

---

## Pseudo-Code: Full Audit Pipeline

```
PROCEDURE run_h_c1_experiment():
    1. models = load_zoo_sample(n=500, seed=1)
    2. self_check_idempotency(models[0])         # crash-fast if algorithm broken
    3. results, summary = run_audit(models)
    4. IF summary.degenerate_count > 0:
           degen_stats = compute_degeneracy_stats(results)
           w_stats = weight_stats_tied_neurons(models, degen_stats.degenerate_indices)
    5. plot_gate_metric(summary.fraction_unique, threshold=0.99)
    6. IF summary.degenerate_count > 0:
           plot_tied_neuron_hist(results)
    7. PRINT structured summary + gate verdict
    8. RETURN summary
```

---

## Tensor Shape Reference

| Variable | Shape | Description |
|----------|-------|-------------|
| W1 | (64, 784) | Hidden layer incoming weights |
| W2 | (10, 64) | Output layer incoming weights |
| majority | (64,) | Majority sign per hidden neuron |
| D | (64, 64) | Diagonal sign matrix |
| W1_canon | (64, 784) | Canonicalized hidden weights |
| W2_canon | (10, 64) | Canonicalized output weights |
| row_sign_sums | (64,) | Sum of element-wise signs per row |
