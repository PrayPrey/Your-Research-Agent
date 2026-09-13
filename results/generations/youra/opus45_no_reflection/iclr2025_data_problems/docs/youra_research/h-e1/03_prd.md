# Product Requirements Document: H-E1

**Hypothesis:** Architecture-method interaction exists and is measurable via efficiency-accuracy Pareto curves  
**Type:** EXISTENCE (PoC)  
**Gate:** MUST_WORK  
**Date:** 2026-08-18  
**Source:** 02c_experiment_brief.md

---

## Executive Summary

Demonstrate that data attribution methods exhibit measurably different performance across transformer architectures (encoder vs decoder). This proof-of-concept validates the foundational claim that architecture-method interaction exists before deeper mechanistic investigation.

---

## Problem Statement

Data attribution methods (TRAK, EK-FAC, TracIn) make different mathematical assumptions about gradient/Hessian structure. Transformer architectures (BERT encoder, GPT-2 decoder) have fundamentally different attention patterns. The interaction between method assumptions and architecture properties may produce systematic performance differences.

**Core Question:** Does at least one attribution method show statistically significant performance difference between BERT and GPT-2?

---

## Functional Requirements

### FR-1: Dataset Preparation
- Load SST-2 from HuggingFace (`glue/sst2`)
- Full training set: 67,349 samples
- Full validation set: 872 samples
- Inject 5% label noise (seed=42) into training set
- Track mislabeled indices for ground truth

### FR-2: Model Fine-tuning (BERT)
- Load `bert-base-uncased` with classification head
- Fine-tune on SST-2 with noisy labels
- AdamW optimizer, lr=2e-5, 3 epochs, batch_size=32
- Save checkpoint at epoch end
- Run 5 seeds (42-46)

### FR-3: Model Fine-tuning (GPT-2)
- Load `gpt2` with classification head
- Configure pad_token = eos_token
- Same training config as BERT
- Run 5 seeds (42-46)

### FR-4: TRAK Attribution
- Use `traker` library
- Compute self-influence scores on training set
- Extract diagonal for mislabeled detection

### FR-5: EK-FAC Attribution
- Use `kronfluence` library
- Fit factors on training set
- Compute self-scores

### FR-6: TracIn Attribution
- Use `captum.influence.TracInCPFast`
- Compute self-influence with final checkpoint

### FR-7: Mislabeled Detection Evaluation
- Compute ROC-AUC: mislabeled=positive, influence=score
- Aggregate across 5 seeds per condition
- 6 conditions total: 3 methods × 2 architectures

### FR-8: Statistical Analysis
- Paired t-test per method (BERT vs GPT-2 across seeds)
- Cohen's d effect size per method
- Significance threshold: p < 0.05

### FR-9: Visualization
- Bar chart: AUC by method, colored by architecture
- Error bars: standard error across seeds
- Annotate significance on difference plot

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed (42-46)
- Deterministic operations where possible
- Checkpoint all trained models

### NFR-2: Computational Efficiency
- Single GPU sufficient (A100 40GB recommended)
- Full pipeline < 24 hours

### NFR-3: Code Quality
- Type hints on public functions
- Docstrings with Args/Returns
- Logging at INFO level

---

## Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| At least one method shows AUC diff > 5% | p < 0.05 | MUST |
| Effect size for significant method | Cohen's d > 0.3 | SHOULD |
| All 6 conditions complete | No crashes | MUST |

---

## Dependencies

### Python Packages
```
torch>=2.0
transformers>=4.30
datasets
traker[fast]
kronfluence
captum
scikit-learn
scipy
matplotlib
```

### Hardware
- GPU: NVIDIA A100 40GB (or equivalent)
- RAM: 32GB+
- Storage: 50GB for checkpoints

---

## Data Flow

```
SST-2 (HF) → Label Noise Injection → Fine-tune BERT/GPT-2 (5 seeds each)
    ↓
Trained Models → Attribution Methods (TRAK/EK-FAC/TracIn)
    ↓
Self-Influence Scores → ROC-AUC (vs mislabeled ground truth)
    ↓
Statistical Tests → Gate Decision (PASS/FAIL)
```

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No significant difference found | Research pivot needed | Document findings for future reference |
| Library incompatibility | Delays | Use `simple-influence` unified API as fallback |
| OOM on attribution | Experiment fails | Reduce batch size, use gradient checkpointing |

---

## Appendix: Phase 2C Completeness

- [x] Dataset: SST-2 full splits
- [x] Baseline models: BERT-base, GPT-2
- [x] Attribution methods: TRAK, EK-FAC, TracIn
- [x] Evaluation metrics: AUC, t-test, Cohen's d
- [x] Success criteria: >5% diff, p<0.05, d>0.3
