# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Title:** Model Zoo Dataset Validity

## Hypothesis Statement

Under standard Model Zoo evaluation, if we analyze the accuracy distribution, then σ(accuracy) > 10% and labels are consistent, because diverse training configurations produce meaningful accuracy variance.

## Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** σ(accuracy) > 10%
- **Fail Action:** STOP, benchmark invalid

## Prerequisites

None (first hypothesis in chain)

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

- **Name:** Model Zoos Dataset (Schurholt et al. 2022)
- **Type:** standard
- **Source:** NeurIPS 2022 Datasets and Benchmarks
- **Path:** modelzoos.cc / HuggingFace
- **Statistics:**
  - 50,360 unique neural network models
  - 27 distinct model zoos
  - 8 image datasets (CIFAR-10, MNIST, etc.)
  - 3.8M+ collected model states
- **Hypothesis Fit:** Dataset provides pre-trained models with ground-truth accuracy labels from standardized evaluation. Diverse training configurations (hyperparameters, architectures) should produce meaningful accuracy variance.

### Model

- **Name:** N/A (observational study)
- **Type:** Analysis only
- **Source:** N/A
- **Hypothesis Fit:** This is an EXISTENCE hypothesis validating dataset properties, not testing a model.

## Verification Protocol

1. Load Model Zoo dataset and extract all accuracy labels
2. Compute distribution statistics: mean, std, min, max, quartiles
3. Verify σ > 10% threshold is met
4. Check for outliers or label inconsistencies
5. Document dataset characteristics for reproducibility

## Success Criteria

- **Primary:** Accuracy σ > 10% across Model Zoo
- **Secondary:** No systematic label errors detected

## Variables

- **Independent:** None (observational)
- **Dependent:** Accuracy distribution statistics (mean, σ, range)
- **Controlled:** Evaluation protocol, architecture family

## Continuation Context

None - this is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3).
