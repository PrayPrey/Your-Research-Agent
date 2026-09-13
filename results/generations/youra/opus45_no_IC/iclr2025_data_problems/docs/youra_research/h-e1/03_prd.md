# Product Requirements Document: H-E1

**Hypothesis:** A statistically significant positive correlation (Spearman r > 0.2) exists between cumulative 13-gram benchmark overlap percentage and benchmark score inflation residual across Pythia model checkpoints.

**Date:** 2026-08-10  
**Author:** Anonymous  
**Type:** EXISTENCE (Foundation Hypothesis)  
**Phase 2C Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This experiment validates whether benchmark contamination correlates with inflated benchmark scores. Using the Pythia model family (72 checkpoints across 6 model sizes), we measure 13-gram overlap between The Pile training corpus and standard benchmarks (MMLU, ARC, HellaSwag, WinoGrande), then correlate contamination levels with performance inflation residuals after capability detrending.

**Success Criteria:** Spearman r > 0.2 with p < 0.05

---

## 2. Problem Statement

Current benchmark evaluation assumes clean separation between training and test data. If contamination exists and correlates with performance, benchmark scores may overestimate true model capability. This experiment establishes whether such correlation exists as foundation for the transfer function research.

---

## 3. Functional Requirements

### FR-1: Benchmark Evaluation Pipeline
- Evaluate Pythia models (410M, 1B, 1.4B, 2.8B, 6.9B, 12B) on 4 benchmarks
- Use lm-evaluation-harness with checkpoint revision flags
- 12 checkpoints per model size (steps 0, 1000, 2000, ..., 143000)
- Total: 72 evaluation runs

### FR-2: Contamination Detection
- Compute 13-gram overlap using lm-eval-harness decontamination module
- Reference: GPT-3 Appendix C methodology
- Index: Pre-computed 13-gram index from The Pile

### FR-3: Capability Detrending
- Measure WikiText-103 perplexity as capability proxy
- Fit linear regression: benchmark_score ~ log(1/perplexity)
- Compute inflation residuals: actual - expected scores

### FR-4: Correlation Analysis
- Spearman correlation between contamination % and inflation residuals
- Report: r coefficient, p-value, 95% CI
- Per-benchmark and aggregate analysis

### FR-5: Visualization
- Scatter plot: contamination % vs inflation residual with regression line
- Contamination by benchmark bar chart
- Checkpoint trajectory by model size

---

## 4. Data Specification

### 4.1 Benchmarks (Evaluation Targets)

| Benchmark | Samples | Type | Source | Download |
|-----------|---------|------|--------|----------|
| MMLU | ~14,042 | Multiple choice QA | cais/mmlu | auto (HF) |
| ARC-Challenge | 1,172 | Multiple choice QA | allenai/ai2_arc | auto (HF) |
| HellaSwag | 10,042 | Sentence completion | Rowan/hellaswag | auto (HF) |
| WinoGrande | 1,267 | Coreference | allenai/winogrande | auto (HF) |

**Total evaluation samples:** ~26,500 (full standard test sets)

### 4.2 Training Corpus (Contamination Source)

| Dataset | Size | Source | Download |
|---------|------|--------|----------|
| The Pile | 825GB | EleutherAI | N/A (use pre-computed index) |

**Note:** We use pre-computed 13-gram indices, not raw Pile data.

### 4.3 Capability Measure

| Dataset | Samples | Purpose | Source |
|---------|---------|---------|--------|
| WikiText-103 | standard | Perplexity for detrending | wikitext (HF) |

---

## 5. Models

### 5.1 Pythia Model Family

| Model | Parameters | Checkpoints | Source |
|-------|------------|-------------|--------|
| pythia-410m | 410M | 12 | EleutherAI/pythia-410m |
| pythia-1b | 1B | 12 | EleutherAI/pythia-1b |
| pythia-1.4b | 1.4B | 12 | EleutherAI/pythia-1.4b |
| pythia-2.8b | 2.8B | 12 | EleutherAI/pythia-2.8b |
| pythia-6.9b | 6.9B | 12 | EleutherAI/pythia-6.9b |
| pythia-12b | 12B | 12 | EleutherAI/pythia-12b |

**Checkpoint steps:** 0, 1000, 2000, 3000, ..., 10000, 143000

---

## 6. Non-Functional Requirements

### NFR-1: Compute
- GPU: A100 40GB or equivalent
- Evaluation time: ~2 GPU-hours per checkpoint
- Total: ~144 GPU-hours

### NFR-2: Reproducibility
- Deterministic evaluation (no training randomness)
- Seeds: 1 fixed seed for all evaluations
- Version pinning for lm-eval-harness

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
transformers>=4.30
lm-eval>=0.4.0
lm-checkpoints>=0.1.0
scipy>=1.10
numpy>=1.24
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
```

### 7.2 External Resources

- lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness
- Pythia models: https://huggingface.co/EleutherAI
- Pre-computed contamination indices (if available)

---

## 8. Success Criteria

### Primary Gate (MUST_WORK)
- Spearman r > 0.2 with p < 0.05

### Secondary Targets
- Spearman r > 0.5 (strong correlation)
- Consistent direction across all benchmarks

### Failure Condition
- r < 0.2 OR p >= 0.05 → ABANDON transfer function approach

---

## 9. Out of Scope

- Model training or fine-tuning
- Custom contamination detection methods
- Benchmarks beyond MMLU/ARC/HellaSwag/WinoGrande
- Model sizes beyond Pythia family

---

*Generated from Phase 2C Experiment Brief*
