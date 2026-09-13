# Product Requirements Document: H-M3
# LoRA Adaptation Efficiency Depends on Landscape Geometry

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis Type:** MECHANISM
**Tier:** FULL (30 tasks max)

---

## 1. Executive Summary

This experiment tests whether loss landscape sharpness predicts LoRA adaptation efficiency. Under the hypothesis that flatter minima enable more efficient low-rank approximation, we measure the correlation between landscape sharpness (from H-M2) and LoRA effective rank across sequential (GSM8K) and retrieval (Natural Questions) tasks.

**Gate Condition:** Spearman correlation rho > 0.5 between sharpness and effective rank.

---

## 2. Problem Statement

### Background
H-M2 established that SSM architectures create different landscape geometries for different task types:
- Sequential tasks (GSM8K): sharpness = 1.512
- Retrieval tasks (NQ): sharpness = 2.326
- Sharpness ratio = 0.65

### Research Question
Does lower landscape sharpness enable LoRA to achieve better generalization with lower effective rank?

### Expected Outcome
- GSM8K (lower sharpness): Lower effective rank, smaller generalization gap
- NQ (higher sharpness): Higher effective rank, larger generalization gap

---

## 3. Functional Requirements

### FR-1: Data Loading Pipeline
- Load GSM8K dataset (HuggingFace: `gsm8k`, main split)
- Load Natural Questions dataset (HuggingFace: `natural_questions`, validation)
- Preprocessing: Extract question text, format as completion task
- **Test sizes:** GSM8K=1,319, NQ=3,610

### FR-2: Model Implementation
- Mamba architecture with LoRA wrapper (reuse from H-M2)
- Model config: d_model=512, d_state=16, n_layers=4
- LoRA config: rank=16, alpha=32, target_modules=["in_proj"]
- LoRA reset capability between tasks

### FR-3: Training Pipeline
- AdamW optimizer, lr=1e-4, cosine decay
- Batch size: 4, max epochs: 5
- Early stopping: loss plateau (patience=2)
- Convergence criterion: <1% loss decrease for 2 epochs

### FR-4: SAM Sharpness Measurement
- Reuse SAM sharpness computation from H-M2
- Epsilon: 0.05, measurement batches: 50
- Measure at convergence point

### FR-5: LoRA Effective Rank Computation
- Extract LoRA matrices (A, B)
- Compute delta: W_delta = B @ A
- SVD decomposition: U, S, Vh = svd(W_delta)
- Effective rank: minimum k where cumsum(S[:k])/sum(S) >= 0.90

### FR-6: Generalization Gap Measurement
- Evaluate on train and test splits
- Generalization gap = train_accuracy - test_accuracy

### FR-7: Correlation Analysis
- Collect (sharpness, effective_rank) pairs per task
- Compute Spearman correlation
- Secondary: correlation with generalization gap

### FR-8: Visualization
- Required: Scatter plot (sharpness vs effective_rank) with rho annotation
- Additional: Singular value distribution, generalization gap plot, training curves

---

## 4. Data Specification

### Primary Datasets

| Dataset | Source | Split | Size | Task Type | Retrieval Density |
|---------|--------|-------|------|-----------|-------------------|
| GSM8K | HuggingFace `gsm8k` | main (test) | 1,319 | Sequential reasoning | 0.1 |
| Natural Questions | HuggingFace `natural_questions` | validation | 3,610 | Factual retrieval | 0.9 |

### Data Loading Code
```python
from datasets import load_dataset
gsm8k = load_dataset("gsm8k", "main", split="test")
nq = load_dataset("natural_questions", split="validation")
```

### Preprocessing
- GSM8K: Extract `question` field
- NQ: Extract `question` + `short_answer` fields

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (RTX 3090 or equivalent)
- Training time per task: <30 minutes
- Total experiment time: <2 hours

### NFR-2: Reproducibility
- Fixed random seeds (42, 123, 456)
- Deterministic operations where possible
- Checkpoint saving at convergence

### NFR-3: Memory
- Batch size 4 fits in 24GB VRAM
- Gradient checkpointing if needed

---

## 6. Success Criteria

### Primary (Gate)
| Metric | Threshold | Source |
|--------|-----------|--------|
| Spearman rho (sharpness vs effective_rank) | > 0.5 | Correlation analysis |

### Secondary
| Metric | Expected | Source |
|--------|----------|--------|
| Lower sharpness → smaller gen gap | Positive correlation | Correlation analysis |
| GSM8K effective rank | < NQ effective rank | Direct measurement |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.30
datasets
scipy
numpy
matplotlib
pyyaml
```

### 7.2 External References
- H-M2 codebase: `h-m2/code/` (MambaWithLoRA, SAM sharpness)
- H-M2 results: `h-m2/experiment_results.json` (sharpness values)

### 7.3 Base Hypothesis Artifacts
- `h-m2/03_architecture.md` - Model structure
- `h-m2/03_logic.md` - SAM sharpness implementation
- `h-m2/code/models/mamba_lora.py` - MambaWithLoRA class

---

## 8. Constraints

### Technical
- Must reuse H-M2 sharpness measurement method for consistency
- LoRA rank fixed at 16 (same as H-M2)
- Effective rank threshold: 90% energy

### Scope
- Two tasks only (GSM8K, NQ) - sufficient for correlation
- No architectural changes - measuring properties on fixed architecture

---

## 9. Ablation Studies

### A-1: Effective Rank Threshold Sensitivity
- Vary threshold: [0.85, 0.90, 0.95]
- Verify correlation holds across thresholds

### A-2: Multiple Random Seeds
- Run with seeds [42, 123, 456]
- Report mean and std of correlation

---

*Generated for Phase 3 Implementation Planning*
*Prerequisite: H-M2 VALIDATED (sharpness ratio 0.65)*
