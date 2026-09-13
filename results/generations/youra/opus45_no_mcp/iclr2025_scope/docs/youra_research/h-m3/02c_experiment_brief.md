# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under LoRA fine-tuning on fixed architecture, if loss landscape has lower sharpness, then adaptation achieves better generalization with lower effective rank.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests causal link between landscape geometry and LoRA efficiency.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 VALIDATED)
**Gate Status:** MUST_WORK - rho > 0.5 sharpness-rank correlation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (VALIDATED: sharpness ratio 0.65)

### Gate Condition
**Primary:** Spearman correlation rho > 0.5 between measured sharpness and LoRA effective rank
**Secondary:** Lower sharpness correlates with smaller generalization gap (train - test accuracy)

---

## Continuation Context

This hypothesis builds on H-M2 which established that SSM architecture creates different landscape geometries for different task types (sequential vs retrieval). H-M3 tests whether this landscape difference translates to measurable differences in LoRA adaptation efficiency.

### Previous Hypothesis Results (H-M2)

| Task | Dataset | Sharpness | Task Type |
|------|---------|-----------|-----------|
| Sequential | GSM8K | 1.512 | Low retrieval |
| Retrieval | NQ | 2.326 | High retrieval |

**Key Finding:** Sequential tasks show 35% lower sharpness than retrieval tasks on Mamba architecture.

---

## Implementation Research Summary

### Knowledge Base Findings

**Relevant Concepts:**
1. **LoRA Effective Rank:** Computed via SVD of weight delta matrix; effective rank = minimum k such that sum(singular_values[:k])/sum(singular_values) >= threshold (typically 90%)
2. **SAM Sharpness:** Loss difference between perturbed and original weights; sharpness = max_|epsilon|<=rho L(w+epsilon) - L(w)
3. **Generalization Gap:** Difference between training and test accuracy; smaller gap indicates better generalization

**Theoretical Basis:**
- Flatter minima (lower sharpness) correlate with better generalization (Keskar et al., 2016)
- Low-rank structure is more stable in flatter regions (implied by LoRA success)

### Code Pattern: LoRA Effective Rank Computation

```python
def compute_effective_rank(lora_A, lora_B, threshold=0.90):
    """Compute effective rank from LoRA matrices."""
    # Reconstruct delta: delta_W = B @ A
    delta_W = lora_B @ lora_A
    
    # SVD decomposition
    U, S, Vh = torch.linalg.svd(delta_W, full_matrices=False)
    
    # Normalize singular values
    S_norm = S / S.sum()
    
    # Find effective rank (cumsum >= threshold)
    cumsum = torch.cumsum(S_norm, dim=0)
    effective_rank = (cumsum < threshold).sum().item() + 1
    
    return effective_rank, S.tolist()
```

### Implementation Priority Assessment

**Recommended Implementation Path:**
- Primary: PyTorch native SVD + custom sharpness measurement
- Fallback: numpy SVD if memory issues
- Justification: Direct control over rank computation; no external dependencies

---

## Experiment Specification

### Dataset

**GSM8K (Sequential Reasoning)**
- Source: HuggingFace `gsm8k`
- Split: main (train: 7,473, test: 1,319)
- Task Type: Sequential reasoning (low retrieval density: 0.1)
- Preprocessing: Extract question, format as completion task

**Natural Questions (Retrieval)**
- Source: HuggingFace `natural_questions` (simplified)
- Split: validation (3,610 samples)
- Task Type: Factual retrieval (high retrieval density: 0.9)
- Preprocessing: Extract question + short_answer

**Loading Information:**
- Method: HuggingFace datasets
- Identifier: `gsm8k`, `natural_questions`
- Code:
```python
from datasets import load_dataset
gsm8k = load_dataset("gsm8k", "main", split="train")
nq = load_dataset("natural_questions", split="validation")
```

### Models

#### Baseline Model

**Architecture:** MambaWithLoRA (from H-M2)
- Model Dimension: 512
- State Dimension: 16
- Layers: 4
- LoRA Configuration: rank=16, alpha=32, target_modules=["in_proj"]

**Loading Information:**
- Method: Custom implementation (H-M2 codebase)
- Identifier: MambaBlockSimulated + LoRA wrapper
- Code:
```python
from models.mamba_lora import MambaWithLoRA
model = MambaWithLoRA(d_model=512, d_state=16, n_layers=4, lora_rank=16)
```

#### Proposed Model

**Architecture:** Same as baseline (measuring properties, not comparing architectures)

**Core Mechanism Implementation:**

```python
def measure_sharpness_rank_correlation(model, datasets, config):
    """
    Core mechanism: Measure correlation between landscape sharpness
    and LoRA effective rank across tasks.
    
    Args:
        model: MambaWithLoRA model
        datasets: Dict[task_name -> dataset]
        config: Training/measurement config
    
    Returns:
        correlation: Spearman rho between sharpness and effective rank
        task_metrics: Dict with per-task measurements
    """
    results = {}
    
    for task_name, dataset in datasets.items():
        # Step 1: Train LoRA to convergence
        model = train_lora_to_convergence(model, dataset, config)
        
        # Step 2: Measure SAM sharpness
        sharpness = compute_sam_sharpness(
            model, dataset, 
            epsilon=config.sam_epsilon,  # 0.05
            num_batches=config.sharpness_batches  # 50
        )
        
        # Step 3: Compute LoRA effective rank
        lora_A = model.get_lora_A()  # [rank, d_model]
        lora_B = model.get_lora_B()  # [d_model, rank]
        effective_rank, singular_values = compute_effective_rank(
            lora_A, lora_B, 
            threshold=0.90
        )
        
        # Step 4: Measure generalization gap
        train_acc = evaluate(model, dataset.train, config)
        test_acc = evaluate(model, dataset.test, config)
        gen_gap = train_acc - test_acc
        
        results[task_name] = {
            "sharpness": sharpness,
            "effective_rank": effective_rank,
            "singular_values": singular_values,
            "train_acc": train_acc,
            "test_acc": test_acc,
            "generalization_gap": gen_gap
        }
        
        # Reset LoRA for next task
        model.reset_lora()
    
    # Step 5: Compute Spearman correlation
    sharpness_vals = [r["sharpness"] for r in results.values()]
    rank_vals = [r["effective_rank"] for r in results.values()]
    
    from scipy.stats import spearmanr
    rho, p_value = spearmanr(sharpness_vals, rank_vals)
    
    return {
        "spearman_rho": rho,
        "p_value": p_value,
        "task_metrics": results,
        "gate_pass": rho > 0.5
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | AdamW | Standard for LoRA |
| Learning Rate | 1e-4 | Conservative for LoRA |
| LR Schedule | Cosine decay | Smooth convergence |
| Batch Size | 4 | Memory constraint |
| Max Epochs | 5 | Train to convergence |
| Early Stopping | Loss plateau (patience=2) | Ensure convergence |
| Loss Function | CrossEntropyLoss | Language modeling |
| Weight Decay | 0.01 | Regularization |
| Gradient Clipping | 1.0 | Stability |

**Convergence Criterion:** Training loss decrease < 1% for 2 consecutive epochs

### Evaluation

**Primary Metrics:**

| Metric | Formula | Gate Threshold |
|--------|---------|----------------|
| Spearman rho | corr(sharpness, effective_rank) | > 0.5 |
| Generalization gap correlation | corr(sharpness, gen_gap) | Positive |

**Secondary Metrics:**

| Metric | Purpose |
|--------|---------|
| Effective rank per task | Direct measurement |
| Singular value distribution | Rank structure analysis |
| Train/Test accuracy | Generalization verification |

**Metrics Loading Information:**
- Task Type: Correlation analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr
rho, p_value = spearmanr(sharpness_values, rank_values)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of sharpness vs effective rank with Spearman rho annotation

#### Additional Figures (LLM Autonomous)
1. **Singular Value Distribution**: Per-task SVD spectrum comparison
2. **Generalization Gap Plot**: Sharpness vs generalization gap scatter
3. **Training Curves**: Loss curves per task showing convergence
4. **Correlation Matrix**: Heatmap of all metric correlations

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spearman rho > 0.5 between sharpness and effective rank

**Expected Outcome:**
- GSM8K (low sharpness ~1.5): Lower effective rank, smaller gen gap
- NQ (high sharpness ~2.3): Higher effective rank, larger gen gap

---

## Appendix: Reference Implementations

### LoRA Effective Rank (PyTorch)

```python
import torch

def compute_effective_rank(W, threshold=0.90):
    """
    Compute effective rank of weight matrix.
    Effective rank = minimum k s.t. sum(S[:k])/sum(S) >= threshold
    """
    U, S, Vh = torch.linalg.svd(W, full_matrices=False)
    S_normalized = S / S.sum()
    cumsum = torch.cumsum(S_normalized, dim=0)
    effective_rank = int((cumsum < threshold).sum().item()) + 1
    return effective_rank
```

### SAM Sharpness Measurement

```python
def compute_sam_sharpness(model, dataloader, epsilon=0.05):
    """
    Compute sharpness via SAM perturbation.
    sharpness = L(w + epsilon * grad/|grad|) - L(w)
    """
    model.train()
    total_sharpness = 0
    n_batches = 0
    
    for batch in dataloader:
        # Compute original loss
        loss_orig = compute_loss(model, batch)
        loss_orig.backward()
        
        # Compute perturbation direction
        grad_norm = compute_grad_norm(model)
        
        # Apply perturbation
        with torch.no_grad():
            for p in model.parameters():
                if p.grad is not None:
                    p.add_(epsilon * p.grad / grad_norm)
        
        # Compute perturbed loss
        loss_pert = compute_loss(model, batch)
        
        # Sharpness = difference
        sharpness = (loss_pert - loss_orig.detach()).item()
        total_sharpness += sharpness
        n_batches += 1
        
        # Restore weights
        with torch.no_grad():
            for p in model.parameters():
                if p.grad is not None:
                    p.sub_(epsilon * p.grad / grad_norm)
        
        model.zero_grad()
    
    return total_sharpness / n_batches
```

### Spearman Correlation

```python
from scipy.stats import spearmanr

def compute_correlation(sharpness_dict, rank_dict):
    """Compute Spearman correlation between sharpness and rank."""
    tasks = sorted(sharpness_dict.keys())
    sharpness = [sharpness_dict[t] for t in tasks]
    ranks = [rank_dict[t] for t in tasks]
    
    rho, p_value = spearmanr(sharpness, ranks)
    return rho, p_value
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| H-M3 set to IN_PROGRESS | 2026-08-19T04:27:39 | Hypothesis Loop |
| Phase 2C experiment design started | 2026-08-19 | Phase 2C |

---

*MCP Tools: Not available (no-mcp mode)*
*Specifications based on H-M2 validated results and established methods*
*Next Phase: Phase 3 - Implementation Planning*
