# Product Requirements Document: H-M2
## Annotator Approval Conflates Correctness with User-State Modeling

**Date:** 2026-08-19
**Hypothesis:** H-M2 (MECHANISM)
**Author:** Anonymous
**Tier:** FULL (30 tasks max)

---

## 1. Executive Summary

This experiment tests whether annotator ratings conflate "correct output" with "output requiring user-state modeling" without distinguishing them, causing the reward model to learn a combined signal. Building on H-M1's finding that RLHF models show similar confidence on Type A and Type B tasks (mean_diff=0.018, overlap=0.647), we analyze whether high-confidence responses cluster equally across both task types.

**Success Criteria:** High-confidence rate difference < 0.15 between task types OR conflation score > 0.85.

---

## 2. Problem Statement

### 2.1 Background
H-M1 established that RLHF models treat Type A (correctness) and Type B (user-state-modeling) tasks similarly from a confidence perspective (mean_diff=0.018). The next question is WHY this similarity exists. H-M2 hypothesizes that annotators rate both task types high without distinguishing, creating a conflated reward signal.

### 2.2 Hypothesis
Under annotator rating behavior, if annotators rate both "correct output" and "output requiring user-state modeling" high without distinguishing, then the reward model learns a combined signal, because the rating scale doesn't differentiate.

### 2.3 Gate Condition (SHOULD_WORK)
- PASS: high_conf_rate_difference < 0.15 OR conflation_score > 0.85
- FAIL: high_conf_rate_difference > 0.3 AND conflation_score < 0.7
- EXPLORE: Intermediate values suggest partial conflation

---

## 3. Functional Requirements

### FR-1: High-Confidence Task Analysis
Analyze H-M1 results to identify high-confidence responses across task types:
- Load H-M1 task results with confidence scores and type classifications
- Apply high-confidence threshold (0.7, also test 0.5, 0.8, 0.9)
- Count high-confidence tasks by Type A vs Type B

### FR-2: Rate Comparison
Compare high-confidence rates between task types:
- Rate A = high_conf_type_a / total_type_a
- Rate B = high_conf_type_b / total_type_b
- Rate difference = |Rate A - Rate B|
- Conflation score = 1 - rate_difference

### FR-3: Per-Feature Analysis
Break down high-confidence rates by individual features:
- `user_belief_reference` feature contribution
- `context_dependent` feature contribution
- `hedged_answer` feature contribution

### FR-4: Cross-Model Consistency
Verify conflation pattern holds across all 3 models:
- Llama-2-7B-Chat
- Llama-2-13B-Chat
- Mistral-7B-Instruct

### FR-5: Threshold Sensitivity Analysis
Test multiple high-confidence thresholds:
- Thresholds: [0.5, 0.6, 0.7, 0.8, 0.9]
- Report rate_difference at each threshold
- Generate sensitivity curve

### FR-6: Visualization Suite
Generate figures:
- Gate metrics comparison bar chart (high-conf rate Type A vs Type B)
- Confidence distribution histograms by task type (extend H-M1)
- Per-feature high-confidence rates heatmap
- Cross-model consistency scatter plot
- Threshold sensitivity curve (0.5-0.9 range)

---

## 4. Data Specification

### 4.1 Primary Input: H-M1 Results
| Source | Content | Path |
|--------|---------|------|
| H-M1 Results | Task classifications, confidence scores | `h-m1/code/outputs/results.json` |
| Task Count | 2212 total (1977 Type A, 235 Type B) | From H-M1 |

### 4.2 Datasets (Reuse from H-M1)
| Dataset | Tasks | Source | Auto-Download |
|---------|-------|--------|---------------|
| TruthfulQA | 817 | `truthful_qa` | Yes |
| MMLU moral_scenarios | ~895 | `cais/mmlu` | Yes |
| Anthropic HH-RLHF | ~500 | `Anthropic/hh-rlhf` | Yes |
| **Total** | **~2212** | - | - |

**Note:** H-M2 is an analysis experiment. Primary data comes from H-M1 outputs; original datasets only needed for re-classification if required.

### 4.3 Static Baselines
None - this is an analysis experiment extending H-M1, not a training experiment.

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Lightweight analysis: No model inference required
- Load existing H-M1 results
- Expected runtime: <5 minutes

### NFR-2: Reproducibility
- Deterministic analysis (no random components)
- Full logging of threshold effects
- Export intermediate calculations

### NFR-3: Statistical Validity
- Minimum 500+ samples (using full 2212 task dataset)
- Report confidence intervals where applicable
- Point-biserial correlation for binary associations

---

## 6. Success Criteria

### Primary Metrics
| Metric | Threshold | Gate |
|--------|-----------|------|
| High-Conf Rate Difference | < 0.15 | PASS |
| Conflation Score | > 0.85 | PASS |
| Cross-Model Consistency | Same pattern across 3 models | Supporting |

### Gate Logic
```python
gate_pass = (high_conf_rate_difference < 0.15) or (conflation_score > 0.85)
gate_fail = (high_conf_rate_difference > 0.3) and (conflation_score < 0.7)
gate_explore = not gate_pass and not gate_fail  # Partial conflation
```

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy
scipy
matplotlib
seaborn
pyyaml
```

### 7.2 Hardware
- CPU sufficient (no GPU required for analysis)

### 7.3 External References
- H-M1 code: `h-m1/code/` (task classification, confidence extraction)
- H-M1 results: `h-m1/code/outputs/results.json` (primary input)

---

## 8. Ablation Variants

### ABL-1: Threshold Sensitivity
Test high-confidence thresholds: [0.5, 0.6, 0.7, 0.8, 0.9]

### ABL-2: Per-Feature Isolation
Analyze high-confidence rates for tasks with each individual feature only.

### ABL-3: Per-Dataset Analysis
Compare conflation patterns within each benchmark (TruthfulQA, MMLU, HH-RLHF).

### ABL-4: Per-Model Analysis
Individual model conflation scores vs aggregate.

---

## 9. Traceability

| Requirement | Source |
|-------------|--------|
| High-confidence analysis | Phase 2C experiment brief |
| Task type classification | H-M1 implementation |
| Success criteria | Phase 2B verification plan |
| Rate comparison method | Phase 2C pseudo-code |

---

*Generated for Phase 3 Implementation Planning*
*Building on: H-M1 (PASS: mean_diff=0.018, overlap=0.647)*
*Next: Architecture Design*
