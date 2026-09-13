# Product Requirements Document: H-E1

**Hypothesis:** Category-dependent calibration variation exists in LLMs on TruthfulQA
**Type:** EXISTENCE (Proof of Concept)
**Date:** 2026-08-10
**Status:** Draft

---

## Executive Summary

This PRD specifies implementation requirements for validating hypothesis H-E1: that LLM calibration error varies systematically across semantic categories in TruthfulQA. The experiment measures Expected Calibration Error (ECE) per cluster and applies ANOVA to detect statistically significant variation.

**Success Criterion:** ANOVA p < 0.05 on per-cluster ECE values.

---

## Problem Statement

LLMs exhibit miscalibration—confidence scores poorly reflect accuracy. Prior work applies global temperature scaling, but if calibration error varies by semantic category, global correction is suboptimal. This experiment tests whether category-dependent calibration variation exists.

---

## Functional Requirements

### FR-1: Dataset Loading

| ID | Requirement |
|----|-------------|
| FR-1.1 | Load TruthfulQA multiple_choice split from HuggingFace (`truthfulqa/truthful_qa`) |
| FR-1.2 | Extract 817 questions with mc1_targets (single correct answer) |
| FR-1.3 | Map 38 original categories to 7 semantic clusters using predefined mapping |
| FR-1.4 | Validate cluster sizes (~100-150 samples each) |

### FR-2: Model Inference

| ID | Requirement |
|----|-------------|
| FR-2.1 | Load Llama-2-7B from HuggingFace (`meta-llama/Llama-2-7b-hf`) |
| FR-2.2 | Use float16 precision with device_map="auto" |
| FR-2.3 | Compute log-probabilities for each answer choice per question |
| FR-2.4 | Select answer with highest log-probability as prediction |
| FR-2.5 | Record softmax confidence and correctness for each question |

### FR-3: ECE Computation

| ID | Requirement |
|----|-------------|
| FR-3.1 | Implement ECE with 15 bins (standard) |
| FR-3.2 | Compute ECE separately for each of 7 clusters |
| FR-3.3 | Use bootstrap resampling (100 iterations) for confidence intervals |
| FR-3.4 | Report per-cluster ECE with 95% CI |

### FR-4: Statistical Testing

| ID | Requirement |
|----|-------------|
| FR-4.1 | Run one-way ANOVA on bootstrapped per-cluster ECE samples |
| FR-4.2 | Report F-statistic and p-value |
| FR-4.3 | Compute ECE range (max - min across clusters) |
| FR-4.4 | Apply Bonferroni correction for post-hoc pairwise comparisons |

### FR-5: Visualization

| ID | Requirement |
|----|-------------|
| FR-5.1 | Generate bar chart of per-cluster ECE with 95% CI error bars |
| FR-5.2 | Generate reliability diagrams (calibration curves) per cluster |
| FR-5.3 | Generate confidence histogram per cluster |
| FR-5.4 | Save all figures to `{hypothesis_folder}/figures/` |

### FR-6: Results Output

| ID | Requirement |
|----|-------------|
| FR-6.1 | Save raw results to `04_results.json` |
| FR-6.2 | Generate validation report `04_validation.md` |
| FR-6.3 | Include gate condition evaluation (p < 0.05) |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Single GPU inference | A100 40GB or equivalent |
| NFR-2 | Batch size | 8 (adjustable for memory) |
| NFR-3 | Reproducibility | Fixed random seed (42) |
| NFR-4 | Runtime | < 2 hours total |

---

## Data Specifications

### Input Data

| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| TruthfulQA | HuggingFace | 817 questions | Multiple choice |

### Category-to-Cluster Mapping

| Cluster | Categories | Expected Size |
|---------|------------|---------------|
| 1 | Health, Nutrition, Psychology | ~120 |
| 2 | Law, Politics, Government | ~130 |
| 3 | Finance, Economics | ~100 |
| 4 | Science, Technology, Math, Physics, Biology | ~110 |
| 5 | History, Geography, Culture, Weather, Language, Education | ~120 |
| 6 | Religion, Philosophy, Ethics, Sociology | ~100 |
| 7 | Misconceptions, Myths, Superstitions, Conspiracies, Paranormal, etc. | ~137 |

### Output Data

| File | Description |
|------|-------------|
| 04_results.json | Raw metrics, per-cluster ECE, ANOVA results |
| 04_validation.md | Gate evaluation, pass/fail determination |
| figures/*.png | Visualization outputs |

---

## Success Criteria

### Primary Gate (MUST_WORK)

| Metric | Target | Evaluation |
|--------|--------|------------|
| ANOVA p-value | < 0.05 | Significant variation exists |

### Secondary Criteria

| Metric | Target | Purpose |
|--------|--------|---------|
| ECE Range | > 0.05 | Practical significance |
| Min cluster size | > 50 | Statistical validity |

### Failure Action

If ANOVA p >= 0.05: **ABANDON** all subsequent hypotheses (no category structure to exploit).

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | >= 4.35 | Model loading |
| datasets | >= 2.14 | TruthfulQA loading |
| torch | >= 2.0 | Inference |
| scipy | >= 1.10 | ANOVA testing |
| matplotlib | >= 3.7 | Visualization |
| numpy | >= 1.24 | Numerical ops |

---

## Out of Scope

- Temperature scaling optimization (H-M1, H-M2)
- Model fine-tuning
- Alternative models beyond Llama-2-7B
- Custom clustering algorithms

---

## Appendix: Reference Implementations

See `02c_experiment_brief.md` for:
- ECE computation code (gpleiss/temperature_scaling)
- MC evaluation code (sylinrl/TruthfulQA)
- Category-to-cluster mapping dictionary
