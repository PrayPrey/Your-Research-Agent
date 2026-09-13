# Product Requirements Document: H-M1

**Hypothesis:** LLMs produce category-specific confidence distributions on TruthfulQA
**Type:** MECHANISM
**Date:** 2026-08-10
**Gate:** MUST_WORK — KS test p < 0.05 for majority of cluster pairs (≥11/21)

---

## Executive Summary

Validate that LLM confidence distributions differ significantly across semantic category clusters on TruthfulQA. Building on h-e1 which confirmed category-dependent ECE variation exists (ANOVA p=0.00012), this hypothesis tests the underlying mechanism: whether clusters have genuinely different confidence distributions via pairwise Kolmogorov-Smirnov tests.

---

## Problem Statement

H-e1 established that calibration error varies by category. The question remains: do different categories produce fundamentally different confidence distributions, or is ECE variation an artifact of sample size/noise? Confirming distribution differences validates the theoretical basis for category-specific calibration.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA multiple_choice split (817 questions)
- Map 38 categories → 7 semantic clusters (reuse h-e1 mapping)
- Validate cluster assignments cover all questions

### FR-2: Model Inference
- Load Llama-2-7B from HuggingFace Hub
- Extract logits for each answer choice
- Compute softmax confidence (max probability per question)
- Batch size: 8, precision: float16

### FR-3: Confidence Extraction
- Store confidence values grouped by cluster
- Minimum 100 samples per cluster
- Output: Dict[cluster_id, np.ndarray of confidences]

### FR-4: Pairwise KS Tests
- Run scipy.stats.ks_2samp for all C(7,2)=21 cluster pairs
- Record statistic (D) and p-value for each pair
- Store results matrix for visualization

### FR-5: Gate Evaluation
- Count significant pairs (p < 0.05)
- PASS if ≥11 of 21 pairs significant
- Report significance rate and effect sizes

### FR-6: Visualization
- **Required:** KS p-value heatmap (21 pairs, significant highlighted)
- **Optional:** Confidence histograms per cluster, CDF comparison, box plots

### FR-7: Results Logging
- Save structured results to 04_validation.md
- Include all statistics, gate decision, figures

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic inference (torch.use_deterministic_algorithms)
- Version-locked dependencies

### NFR-2: Performance
- Complete inference in <30 minutes on single A100
- Memory footprint <24GB VRAM

### NFR-3: Reusability
- Code structure compatible with h-e1 infrastructure
- Modular functions for reuse in h-m2/h-m3

---

## Success Criteria

| Metric | Target | Gate |
|--------|--------|------|
| KS significant pairs | ≥11/21 | MUST_WORK |
| Mean confidence range | >0.1 | Secondary |
| Code execution | No errors | Required |

---

## Dependencies

### From h-e1 (Prerequisite)
- Category-to-cluster mapping
- TruthfulQA loading code
- Confidence extraction utilities

### External
- transformers (Llama-2-7B)
- scipy.stats (ks_2samp)
- datasets (TruthfulQA)
- matplotlib/seaborn (visualization)

---

## Out of Scope

- Model training or fine-tuning
- Alternative clustering strategies (deferred to pivot if gate fails)
- Multiple model comparison (h-m2 scope)

---

## Appendix: Cluster Mapping Reference

| Cluster | Categories |
|---------|------------|
| 1 (Health) | Health, Nutrition, Psychology |
| 2 (Law/Politics) | Law, Politics, Government |
| 3 (Finance) | Finance, Economics |
| 4 (Science) | Science, Technology, Math, Physics, Biology |
| 5 (History) | History, Geography, Culture |
| 6 (Philosophy) | Religion, Philosophy, Ethics |
| 7 (Misconceptions) | Misconceptions, Myths, Superstitions, Conspiracies |
