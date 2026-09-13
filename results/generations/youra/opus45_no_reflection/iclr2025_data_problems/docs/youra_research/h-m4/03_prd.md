# Product Requirements Document: H-M4

**Hypothesis:** Architecture-approximation interaction determines efficiency-accuracy trade-off (EK-FAC favors GPT-2, TracIn favors BERT, TRAK invariant)
**Type:** MECHANISM
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This experiment tests whether different attribution methods (EK-FAC, TracIn, TRAK) create distinct efficiency-accuracy Pareto frontiers when applied to different transformer architectures (BERT encoder vs GPT-2 decoder). We vary compute budgets via projection dimension and measure mislabeled detection AUC at each budget level.

**Success Criteria:** Confirm at least one of three predictions (P1: EK-FAC favors GPT-2, P2: TracIn favors BERT, P3: TRAK architecture-invariant) with statistical significance (p < 0.05).

---

## 2. Problem Statement

H-M3 established architecture-dependent attribution performance. H-M4 extends this by testing whether these differences persist across compute budgets, forming distinct Pareto frontiers. This is critical for practitioners selecting attribution methods given compute constraints.

---

## 3. Functional Requirements

### FR-1: Model Fine-tuning
- Fine-tune BERT-base-uncased and GPT-2 on SST-2 with 5% label noise
- 3 random seeds (42, 123, 456) for statistical testing
- Save checkpoints for attribution computation

### FR-2: EK-FAC Attribution (kronfluence)
- Compute influence scores at 5 projection dimensions: 64, 128, 256, 512, 1024
- Measure wall-clock time and mislabeled detection AUC at each level
- Generate Pareto points for both BERT and GPT-2

### FR-3: TracIn Attribution (dattri)
- Compute influence scores using gradient checkpoints
- Use same 5 compute budget levels (via checkpoint selection or sample count)
- Generate Pareto points for both architectures

### FR-4: TRAK Attribution (traker)
- Compute scores at 5 projection dimensions: 64, 128, 256, 512, 1024
- Generate Pareto points for both architectures

### FR-5: Pareto Curve Analysis
- Generate 6 Pareto curves (3 methods × 2 architectures)
- Statistical comparison via paired t-test across seeds
- Identify dominance relationships

### FR-6: Visualization
- **Required:** Pareto Frontier Comparison (2×3 subplot grid)
- Architecture comparison per method (3 plots)
- AUC vs projection dimension line plots

---

## 4. Data Specification

### 4.1 Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | SST-2 (Stanford Sentiment Treebank v2) |
| **Source** | HuggingFace Datasets (auto-download) |
| **Train Split** | 67,349 samples |
| **Validation Split** | 872 samples |
| **Mislabeling** | 5% random label noise (3,367 samples) |

**Loading Code:**
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
```

### 4.2 Models

| Model | Source | Parameters |
|-------|--------|------------|
| BERT-base-uncased | HuggingFace (auto-download) | ~110M |
| GPT-2 | HuggingFace (auto-download) | ~124M |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Complete all 30 attribution runs (5 budgets × 3 methods × 2 architectures) within 24 hours
- GPU memory: ≤16GB per run

### NFR-2: Reproducibility
- Fixed random seeds: 42, 123, 456
- All results saved with full configuration

### NFR-3: Statistical Rigor
- Paired t-test across 3 seeds per comparison
- Report mean ± std for all metrics

---

## 6. Success Criteria

### Primary Gate Conditions (PoC)
- **P1:** EK-FAC GPT-2 AUC > BERT AUC at matched compute (p < 0.05)
- **P2:** TracIn BERT AUC > GPT-2 AUC at matched compute (p < 0.05)
- **P3:** TRAK |BERT - GPT-2| AUC < 5% at all compute budgets

**Pass Condition:** At least one prediction confirmed with statistical significance.

**Note:** H-M3 showed unexpected directions. H-M4 may revise predictions based on empirical findings across compute budgets.

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | ≥2.0 | Deep learning framework |
| transformers | ≥4.30 | BERT/GPT-2 models |
| datasets | ≥2.14 | SST-2 loading |
| kronfluence | latest | EK-FAC implementation |
| traker | latest | TRAK implementation |
| dattri | latest | TracIn implementation |
| scikit-learn | ≥1.0 | ROC-AUC computation |
| matplotlib | ≥3.7 | Visualization |
| scipy | ≥1.10 | Statistical tests |

### 7.2 Hardware
- GPU with ≥16GB VRAM (recommended: A100 40GB)
- 32GB+ system RAM

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Library API incompatibility | Pin versions, test early |
| OOM on large projections | Gradient checkpointing, reduce batch size |
| Compute budget exceeds timeline | Parallelize across GPUs |

---

## 9. Phase 2C Reference

All specifications derived from: `h-m4/02c_experiment_brief.md`

Key implementation references:
- kronfluence API: `Analyzer(model, task=ClassificationTask())`
- traker API: `TRAKer(model, train_set, proj_dim=...)`
- dattri API: `TracInCPFast(model, train_loader, checkpoint_paths)`
