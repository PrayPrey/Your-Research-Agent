# Product Requirements Document: H-E1

**Hypothesis:** Collaboration score extracts agency signals orthogonal to preference labels (correlation < 0.7)
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This experiment validates whether a collaboration score metric (collab_score_v2) captures information orthogonal to preference labels in the HH-RLHF dataset. Success criterion: Pearson correlation < 0.7 between collaboration scores and preference labels.

**Gate Condition:** MUST_WORK - Blocks all downstream BiDPO hypotheses.

---

## 2. Problem Statement

BiDPO proposes using collaboration signals to guide preference optimization. Before integrating into training, we must verify that collaboration scores provide information distinct from existing preference labels. High correlation (>= 0.7) would indicate redundancy, invalidating the BiDPO approach.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load Anthropic HH-RLHF dataset (helpful-base subset)
- Sample 1000 random pairs with seed=42
- Extract final assistant response from conversation format

### FR-2: Collaboration Score Implementation
- Implement collab_score_v2 function with 4 signal categories:
  - Reasoning traces (because, since, therefore)
  - Uncertainty acknowledgment (I think, might, could)
  - User engagement (you could, consider, questions)
  - Explanation depth (numbered lists, first/second/step)
- Length-normalize using sqrt(word_count)

### FR-3: Correlation Analysis
- Compute Pearson correlation between collab_score and preference labels
- Report p-value for statistical significance
- Compute mean/std for chosen vs rejected distributions

### FR-4: Visualization
- Generate correlation bar chart (vs 0.7 threshold)
- Generate score distribution histogram (chosen vs rejected)
- Generate scatter plot with regression line

---

## 4. Data Specification

| Dataset | Source | Subset | Sample Size |
|---------|--------|--------|-------------|
| HH-RLHF | Anthropic/hh-rlhf | helpful-base | 1000 pairs |

**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base", split="train")
dataset = dataset.shuffle(seed=42).select(range(1000))
```

---

## 5. Success Criteria

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Pearson r | < 0.7 | Orthogonality confirmed |
| p-value | < 0.05 | Statistically significant |
| Score variance | > 0 | Signal has information |

**Gate Pass:** abs(correlation) < 0.7

---

## 6. Non-Functional Requirements

- **Reproducibility:** Random seed 42 for all operations
- **Compute:** CPU-only (no GPU required)
- **Runtime:** < 5 minutes for full analysis

---

## 7. Dependencies

### 7.1 Python Packages
- datasets (HuggingFace)
- scipy (statistics)
- numpy
- matplotlib (visualization)
- pandas (optional, data handling)

### 7.2 External Resources
- HuggingFace Hub access for dataset download

---

## 8. Out of Scope

- Model training (pure statistical analysis)
- Multi-dataset validation
- Alternative collaboration score formulations
