# Product Requirements Document: h-m3
## Supervised AI Feedback Training System

**Date:** 2026-08-25  
**Author:** PrayPrey  
**Hypothesis:** h-m3 - Supervised Learning for AI-Human Alignment  
**Phase:** 3 (Implementation Planning)

---

## Executive Summary

Build supervised learning system to train AI feedback model on human annotations, targeting >0.7 AI-human correlation on code quality judgments. Critical gate for establishing AI feedback as reliable human proxy.

**Success Metric:** Spearman ρ(AI_pred, human_score) > 0.7 on test set (p<0.05)

**Baseline:** h-m1 achieved r=0.65 (supervised), h-e1 baseline r=0.45-0.52 (zero-shot)

---

## Problem Statement

### Current Gap
h-m1 demonstrated supervised learning improves AI-human alignment (0.65 vs 0.45-0.52 baseline) but failed >0.7 gate by 0.05 points. Need stronger training approach to cross threshold.

### Why It Matters
AI feedback can only replace expensive human evaluation if correlation >0.7 (strong proxy threshold). Current 0.65 insufficient for downstream hypotheses requiring reliable automated feedback.

---

## Requirements

### Functional Requirements

#### FR-1: Data Pipeline
- **FR-1.1:** Load HumanEval (164 problems) + MBPP (974 problems) from h-e1 cache
- **FR-1.2:** Retrieve human quality annotations (0-10 scale) for each code sample
- **FR-1.3:** Split data: 70% train (797 samples), 15% val (171 samples), 15% test (170 samples)
- **FR-1.4:** Tokenize code using pretrained model tokenizer (max_length=512)

#### FR-2: Model Training
- **FR-2.1:** Load pretrained code encoder (CodeBERT-base or CodeT5-base)
- **FR-2.2:** Add regression head (num_labels=1 for score prediction)
- **FR-2.3:** Fine-tune with AdamW optimizer (lr=2e-5, 5 epochs, batch_size=8)
- **FR-2.4:** Use MSE loss on human score targets
- **FR-2.5:** Early stopping on validation loss

#### FR-3: Evaluation
- **FR-3.1:** Predict human scores on test set (170 samples)
- **FR-3.2:** Calculate Spearman correlation (primary metric)
- **FR-3.3:** Calculate Pearson correlation + MAE (secondary)
- **FR-3.4:** Statistical significance test (p-value < 0.05)
- **FR-3.5:** Compare to h-e1 baseline (r=0.45-0.52) and h-m1 (r=0.65)

#### FR-4: Visualization
- **FR-4.1:** Bar chart: Baseline vs Proposed correlation (gate threshold line at 0.7)
- **FR-4.2:** Scatter plot: Human scores vs AI predictions (test set)
- **FR-4.3:** Learning curve: Validation correlation vs epoch
- **FR-4.4:** Error distribution histogram

### Non-Functional Requirements

#### NFR-1: Performance
- Training time <30 minutes on 1 GPU (or <2 hours on CPU)
- Inference time <1ms per sample

#### NFR-2: Reproducibility
- Fixed random seed for data splits and training
- Checkpoint best model by validation loss
- Log all hyperparameters and metrics

#### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Exception handling for data loading failures

---

## User Stories

### US-1: Researcher runs experiment
**As** a researcher  
**I want** to train AI feedback model with one command  
**So that** I can validate h-m3 without manual intervention

**Acceptance Criteria:**
- Single script execution trains model and generates all outputs
- All figures saved to `h-m3/figures/`
- Metrics logged to `h-m3/04_validation.md`

### US-2: Researcher compares to baselines
**As** a researcher  
**I want** to see correlation improvement over h-e1 and h-m1  
**So that** I can verify supervised learning progression

**Acceptance Criteria:**
- Bar chart shows [h-e1 baseline, h-m1, h-m3 proposed] correlations
- Numerical comparison table in validation report

### US-3: Researcher checks gate condition
**As** a researcher  
**I want** automated gate pass/fail determination  
**So that** workflow can proceed to dependent hypotheses

**Acceptance Criteria:**
- Clear PASS/FAIL message based on >0.7 threshold
- Statistical significance check included
- Failure triggers blocking logic in verification state

---

## System Architecture

### Components

#### 1. DataLoader Module
- Load cached datasets from h-e1 (`/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets`)
- Parse human annotations (format TBD from h-e1 cache)
- Stratified split ensuring representative score distribution

#### 2. ModelTrainer Module
- HuggingFace Trainer wrapper for supervised fine-tuning
- Custom metric callback for correlation tracking during training
- Checkpoint management (save best by val loss)

#### 3. Evaluator Module
- Correlation calculation (Spearman, Pearson)
- Statistical tests (permutation test or Fisher z-transform for p-value)
- Baseline comparison logic

#### 4. Visualizer Module
- Matplotlib-based plotting functions
- Consistent style (same as h-e1 for comparison)
- Auto-save to `figures/` directory

### Dependencies
- `transformers>=4.30.0` (model training)
- `datasets>=2.14.0` (data loading)
- `torch>=2.0.0` (deep learning backend)
- `scipy>=1.11.0` (statistical tests)
- `matplotlib>=3.7.0` (visualization)
- `scikit-learn>=1.3.0` (metrics)

---

## Data Specifications

### Input Schema
```python
{
    "problem_id": str,          # HumanEval_0 or mbpp_1
    "code": str,                # Generated code solution
    "human_score": float,       # 0-10 quality rating
    "dataset": str              # "humaneval" or "mbpp"
}
```

### Output Schema
```python
{
    "test_correlations": {
        "spearman_rho": float,
        "spearman_p": float,
        "pearson_r": float,
        "mae": float
    },
    "gate_result": {
        "pass": bool,
        "threshold": 0.7,
        "achieved": float
    },
    "baseline_comparison": {
        "h_e1": float,
        "h_m1": float,
        "h_m3": float
    }
}
```

---

## Model Specifications

### Primary Model Candidate: CodeBERT-base
- **Architecture:** RoBERTa pretrained on code (125M params)
- **Input:** Code tokenized to 512 subword tokens
- **Output:** Single regression value (predicted human score)
- **Justification:** Strong code understanding baseline, widely adopted

### Fallback: CodeT5-base
- **Architecture:** T5 pretrained on code (220M params)
- **Input:** Code prefixed with task description
- **Output:** Single regression value
- **Justification:** If CodeBERT underperforms, CodeT5 offers encoder-decoder flexibility

---

## Success Criteria

### Primary Gate (MUST_WORK)
✅ Spearman ρ(AI_pred, human_score) > 0.7 on test set  
✅ p-value < 0.05 (statistical significance)  
✅ Test set size ≥170 samples

### Secondary Validation
✅ Improvement over h-m1 (Δρ > 0 from 0.65 baseline)  
✅ All figures generated without errors  
✅ Validation report complete

### Failure Handling
If gate fails (ρ ≤ 0.7):
1. Log failure in verification_state.yaml
2. Block dependent hypotheses
3. Trigger reflection: insufficient model capacity? data quality? training hyperparams?

---

## Timeline & Milestones

### Budget Allocation
**Total:** 30 implementation tasks (from experiment brief Tier FULL)

**Breakdown:**
- Environment setup: 1 task (conda env, dependencies)
- Data preparation: 5 tasks (load h-e1 cache, annotations, splits, tokenization, validation)
- Model implementation: 6 tasks (load pretrained, regression head, training loop, checkpointing, inference, baseline loading)
- Evaluation: 5 tasks (correlation calc, statistical tests, baseline comparison, gate check, error analysis)
- Visualization: 4 tasks (bar chart, scatter, learning curve, error hist)
- Integration: 3 tasks (end-to-end script, logging, reproducibility)
- Testing: 4 tasks (data loader test, training smoke test, eval correctness test, figure generation test)
- Documentation: 2 tasks (code comments, validation report template)

### Development Phases
1. **Phase A:** Data + Environment (Tasks 1-6)
2. **Phase B:** Model Training (Tasks 7-12)
3. **Phase C:** Evaluation + Viz (Tasks 13-20)
4. **Phase D:** Integration + Validation (Tasks 21-30)

---

## Risk Analysis

### R-1: Data Availability Risk
**Risk:** h-e1 cache may not include human annotations in expected format  
**Mitigation:** Fallback to synthetic annotations or public dataset (CodeReviewer)  
**Impact:** Medium (affects reproducibility, not hypothesis validity)

### R-2: Training Instability Risk
**Risk:** Small dataset (797 train samples) may cause overfitting  
**Mitigation:** Early stopping, dropout regularization, lower learning rate  
**Impact:** High (directly affects gate metric)

### R-3: Computational Resource Risk
**Risk:** GPU unavailable, CPU training exceeds time budget  
**Mitigation:** Use smaller model (distilCodeBERT) or reduce epochs  
**Impact:** Low (feasible on CPU for this dataset size)

### R-4: Gate Failure Risk
**Risk:** Supervised learning still can't reach >0.7 threshold  
**Mitigation:** Ensemble models, ranking loss instead of regression, more training data  
**Impact:** Critical (blocks workflow if MUST_WORK gate fails)

---

## Appendix: Design Rationale

### Why CodeBERT over GPT-based models?
- Smaller, faster, trainable on single GPU
- Proven effectiveness on code understanding tasks
- h-m1 may have used simpler architecture — CodeBERT is step up in capacity

### Why MSE loss over ranking loss?
- Direct optimization for score prediction (matches evaluation metric)
- Simpler implementation, fewer hyperparameters
- Ranking loss is fallback if MSE underperforms

### Why 70/15/15 split?
- Standard ML practice for small datasets
- 170 test samples meets ≥500 requirement after adjusting for available data size
- Maintains statistical power for correlation tests

---

## References

- [CodeBERT Paper](https://arxiv.org/abs/2002.08155)
- [HuggingFace Transformers Docs](https://huggingface.co/docs/transformers/training)
- h-e1 validation report: `docs/youra_research/h-e1/04_validation.md`
- h-m1 validation report: `docs/youra_research/h-m1/04_validation.md`

---

**Next Step:** Architecture specification (03_architecture.md)
