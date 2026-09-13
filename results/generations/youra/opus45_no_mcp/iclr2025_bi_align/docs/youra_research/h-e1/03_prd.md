# Product Requirements Document: H-E1

**Hypothesis:** Calibration Inversion Clusters Exist Systematically
**Type:** EXISTENCE (LIGHT tier)
**Date:** 2026-08-19
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

Validate whether tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) cluster non-randomly across RLHF benchmarks. Success criterion: silhouette score > 0.3.

---

## Problem Statement

RLHF-trained models exhibit miscalibration patterns where confidence doesn't align with correctness. This experiment tests if such miscalibration forms systematic clusters (not random noise), which would indicate underlying behavioral patterns worth investigating in subsequent mechanism hypotheses.

---

## Functional Requirements

### FR-1: Dataset Preparation

| Requirement | Specification |
|-------------|---------------|
| **FR-1.1** | Load TruthfulQA (817 questions) via `datasets` library |
| **FR-1.2** | Load ETHICS justice subset (~500 tasks) |
| **FR-1.3** | Load HHH alignment single-turn (~200 tasks) |
| **FR-1.4** | Combine into unified evaluation set (~1,517 tasks) |
| **FR-1.5** | Store task metadata (source dataset, category) |

### FR-2: Model Inference

| Requirement | Specification |
|-------------|---------------|
| **FR-2.1** | Load Llama-2-7B-Chat (primary baseline) |
| **FR-2.2** | Load Llama-2-13B-Chat (cross-validation) |
| **FR-2.3** | Load Mistral-7B-Instruct (cross-validation) |
| **FR-2.4** | Extract sequence log-probabilities for correct answers |
| **FR-2.5** | Extract sequence log-probabilities for incorrect answers |
| **FR-2.6** | Apply length normalization to logprobs |

### FR-3: Calibration Score Computation

| Requirement | Specification |
|-------------|---------------|
| **FR-3.1** | Compute calibration inversion score per task: `inversion = max_wrong_logprob_norm - correct_logprob_norm` |
| **FR-3.2** | Flag tasks with inversion > 0.1 as "calibration inverted" |
| **FR-3.3** | Store per-task calibration vectors for clustering |

### FR-4: Clustering Analysis

| Requirement | Specification |
|-------------|---------------|
| **FR-4.1** | Apply K-means clustering (k=3 default) |
| **FR-4.2** | Compute silhouette score for cluster quality |
| **FR-4.3** | Test k=[2,3,4,5] and select optimal |
| **FR-4.4** | Record cluster centers and task assignments |

### FR-5: Evaluation & Reporting

| Requirement | Specification |
|-------------|---------------|
| **FR-5.1** | Gate check: silhouette > 0.3 → PASS |
| **FR-5.2** | Generate calibration score histogram |
| **FR-5.3** | Generate cluster scatter plot |
| **FR-5.4** | Generate per-cluster calibration profile boxplots |
| **FR-5.5** | Generate cross-model cluster agreement heatmap |

---

## Non-Functional Requirements

| NFR | Specification |
|-----|---------------|
| **NFR-1** | Runtime: < 2 hours on single GPU |
| **NFR-2** | Memory: < 24GB VRAM (batch size 8) |
| **NFR-3** | Reproducibility: seed=42 for all random ops |
| **NFR-4** | Output: JSON + figures saved to h-e1/figures/ |

---

## Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Silhouette Score | > 0.3 | **PRIMARY (GATE)** |
| Distinct Cluster Profiles | Visual separation | Secondary |
| Cross-Model Agreement | > 50% overlap | Tertiary |

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | >= 4.30 | Model loading |
| datasets | >= 2.0 | Dataset loading |
| scikit-learn | >= 1.0 | Clustering, silhouette |
| torch | >= 2.0 | Inference |
| matplotlib | >= 3.5 | Visualization |
| numpy | >= 1.20 | Numerical ops |

---

## Data Specification

### Input Format

```python
# Per-task structure
{
    "task_id": str,
    "source_dataset": "truthfulqa" | "ethics" | "hhh",
    "question": str,
    "correct_answer": str,
    "incorrect_answers": List[str],
    "category": Optional[str]
}
```

### Output Format

```python
# Per-task result
{
    "task_id": str,
    "correct_logprob_norm": float,
    "max_wrong_logprob_norm": float,
    "inversion_score": float,
    "is_inverted": bool,
    "cluster_label": int
}

# Aggregate result
{
    "silhouette_score": float,
    "gate_passed": bool,
    "cluster_centers": List[float],
    "n_tasks_per_cluster": List[int]
}
```

---

## Task Budget

**Tier:** LIGHT (EXISTENCE hypothesis)
**Total Max:** 15 tasks
**Epic Range:** 4-8 epics

---

*Generated from Phase 2C experiment brief*
