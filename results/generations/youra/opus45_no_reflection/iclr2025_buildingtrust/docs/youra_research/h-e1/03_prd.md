# Product Requirements Document: H-E1

**Hypothesis:** A statistically significant positive correlation (r > 0.5, p < 0.05) exists between factuality error detection accuracy (TruthfulQA MC1) and adversarial robustness (1 - ASR on TextFooler) across 12+ open-weight LLMs.

**Date:** 2026-08-18
**Type:** EXISTENCE (Foundation)
**Budget Tier:** LIGHT (≤15 tasks)

---

## Executive Summary

Validate the existence of correlation between factuality (TruthfulQA MC1 accuracy) and adversarial robustness (1 - TextFooler ASR) across 12 open-weight LLMs. This is the foundation hypothesis for the calibration-mediated factuality-robustness research.

---

## Problem Statement

Current LLM research treats factuality and robustness as separate capabilities. This experiment tests whether they share an underlying relationship, measured via correlation analysis across diverse model architectures.

---

## Functional Requirements

### FR-1: Model Evaluation Pipeline

**FR-1.1: TruthfulQA MC1 Evaluation**
- Load 12 models from HuggingFace
- Run lm-evaluation-harness with `truthfulqa_mc1` task
- Full test set: 817 questions
- Batch size: 4 (adjust for GPU memory)
- Output: MC1 accuracy per model

**FR-1.2: TextFooler Attack Evaluation**
- Run TextAttack with `textfooler` recipe on SST-2
- 1000+ samples per model
- Compute Attack Success Rate (ASR)
- Robustness = 1 - ASR

### FR-2: Model Pool

| ID | Model | Parameters |
|----|-------|------------|
| M01 | meta-llama/Llama-2-7b-hf | 7B |
| M02 | meta-llama/Llama-2-13b-hf | 13B |
| M03 | meta-llama/Llama-2-70b-hf | 70B |
| M04 | meta-llama/Meta-Llama-3-8B | 8B |
| M05 | meta-llama/Meta-Llama-3-70B | 70B |
| M06 | mistralai/Mistral-7B-v0.1 | 7B |
| M07 | mistralai/Mistral-7B-Instruct-v0.1 | 7B |
| M08 | google/flan-t5-base | 250M |
| M09 | google/flan-t5-large | 780M |
| M10 | google/flan-t5-xl | 3B |
| M11 | microsoft/phi-2 | 2.7B |
| M12 | microsoft/Phi-3-mini-4k-instruct | 3.8B |

### FR-3: Statistical Analysis

**FR-3.1: Primary Correlation**
- Compute Pearson correlation between MC1 and (1-ASR)
- Report r value and p-value

**FR-3.2: Bootstrap Confidence Interval**
- 1000 bootstrap resamples
- Report 95% CI for r

**FR-3.3: Partial Correlation**
- Control for log(parameters)
- Report partial r value

### FR-4: Visualization

**FR-4.1: Gate Metrics Plot (Required)**
- Scatter plot: MC1 vs (1-ASR)
- Points colored by model family
- Regression line with 95% CI band
- r and p-value annotation

**FR-4.2: Supporting Plots**
- Correlation matrix heatmap
- Bootstrap distribution histogram
- Within-family scatter panels

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for bootstrap
- Exact model version IDs logged
- All results exportable to JSON

### NFR-2: Scalability
- Support batch processing across models
- GPU memory management for 70B models

### NFR-3: Compute Budget
- Target: Complete within single A100 80GB session
- Fallback: Sequential processing for large models

---

## Datasets

| Dataset | Source | Split | Samples | Purpose |
|---------|--------|-------|---------|---------|
| TruthfulQA | HuggingFace `truthful_qa` | validation | 817 | Factuality metric |
| SST-2 | HuggingFace `glue/sst2` | validation | 1000+ | Adversarial attack target |

---

## Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Pearson r | > 0.5 | Primary |
| p-value | < 0.05 | Primary |
| Bootstrap 95% CI | Excludes 0.3 | Secondary |
| Partial r (scale-controlled) | > 0.3 | Secondary |

---

## Gate Condition

**MUST_WORK Gate:**
- r < 0.3 → ABANDON entire research direction
- 0.3 < r < 0.5 → PIVOT to investigate confounds
- r > 0.5 + p < 0.05 → PROCEED to H-M1

---

## Dependencies

- lm-evaluation-harness (EleutherAI)
- TextAttack (QData)
- HuggingFace Transformers + Datasets
- scipy, numpy, matplotlib

---

## Out of Scope

- Model training or fine-tuning
- ECE calibration analysis (deferred to H-M1)
- Mediation analysis (deferred to H-M3)
