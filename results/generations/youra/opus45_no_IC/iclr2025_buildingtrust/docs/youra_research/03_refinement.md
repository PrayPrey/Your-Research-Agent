# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1
- **Gap Title**: Category-Specific Calibration Analysis Absent
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) met with genuine adversarial stress-testing

### Key Insights
- ECE already accounts for accuracy/difficulty — category calibration patterns are real calibration effects, not difficulty confounds
- Pre-registration of cluster assignments is essential to prevent post-hoc optimization and ensure scientific rigor
- Regularized cluster temperatures (penalized deviation from global T) balance flexibility with generalization
- Cross-benchmark transfer (TruthfulQA → FACTOR) provides the strongest evidence that category structure reflects real calibration patterns, not dataset-specific overfitting

### Breakthrough Moments
- Exchange 7: Dr. Nova proposed FACTOR as external validation dataset, enabling cross-benchmark generalization test
- Exchange 12: Prof. Rex demanded pre-registration and explicit null hypothesis statistical test
- Exchange 13: Prof. Vera proposed regularized temperature scaling to prevent overfitting while capturing real variation

---

## Final Hypothesis

### Title
Category-Specific Calibration for LLM Truthfulness

### Hypothesis ID
H-ClusterCal-v1

### Core Claim
Under evaluation on TruthfulQA benchmark with pre-registered semantic category clusters, if LLM predictions are calibrated using cluster-specific temperature scaling, then Expected Calibration Error will be significantly lower than global temperature scaling, because semantic category membership captures systematic variation in model confidence behavior.

### Mechanism
Different semantic categories evoke different confidence distributions in LLMs, potentially reflecting training data characteristics (confident rhetoric in misconception-prone topics vs. hedged language in scientific topics). Temperature scaling with separate parameters per cluster captures this variation, leading to better calibration than a single global temperature.

---

## Predictions

| ID | Primary | Statement | Success Criterion | Falsification |
|----|---------|-----------|-------------------|---------------|
| P1 | Yes | Cluster-specific T achieves lower ECE than global T | p<0.05 AND d>0.3 (paired t-test) | p>0.05 OR d<0.3 |
| P2 | No | Per-cluster ECE values differ significantly | ANOVA p<0.05 | p>0.05 |
| P3 | No | Calibration improvement transfers to FACTOR | ECE(cluster-T) < ECE(global-T) on FACTOR | No improvement |

---

## Novelty

**Key Innovation**: First systematic per-category calibration analysis on TruthfulQA with pre-registered semantic clusters

**Differentiation from Prior Work**:
- vs. Guo et al., 2017 (Temperature Scaling): They applied globally; we extend to per-cluster with regularization
- vs. Lin et al., 2022 (TruthfulQA): They evaluated truthfulness; we analyze calibration by category
- vs. Xiong et al., 2023 (LLM Uncertainty): They compared confidence types globally, not per-category

---

## Experimental Design

### Dataset
- **Primary**: TruthfulQA (~817 questions, 38 categories, 7 pre-registered clusters)
- **Validation**: FACTOR (cross-benchmark transfer test)

### Models
- Llama-2-7B (meta-llama/Llama-2-7b-hf)
- Mistral-7B (mistralai/Mistral-7B-v0.1)
- Llama-2-13B (meta-llama/Llama-2-13b-hf)

### Baselines
- Uncalibrated softmax probabilities
- Global temperature scaling [Guo et al., 2017]

### Method
- Cluster-specific temperature scaling with L2 regularization
- 5-fold cross-validation
- ECE with bootstrap 95% CI

### Pre-Registered Clusters (7)
1. Misconceptions: Misconceptions, Indexical errors, Confusion
2. Conspiracies & Paranormal: Conspiracies, Paranormal, Superstitions
3. Science & Health: Science, Health, Nutrition
4. History & Politics: History, Politics, Law
5. Culture & Society: Sociology, Psychology, Economics
6. Language & Logic: Language, Logical falsehoods, Proverbs
7. Other: Weather, Advertising, Fiction, etc.

---

## Limitations

- Small per-cluster sample sizes (~100-150 questions) limit statistical power
- Cluster assignment is domain-expert judgment, not empirically validated
- Temperature scaling is a simple linear calibration method
- Study detects patterns but does not explain *why* calibration varies
- Only open-weight models with logit access can be evaluated

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (addressed in discussion) |

---

*Phase 2A Complete — Ready for Phase 2B*
