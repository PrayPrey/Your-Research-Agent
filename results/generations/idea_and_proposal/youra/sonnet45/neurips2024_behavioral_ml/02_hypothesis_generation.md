# Phase 2A Extended: Hypothesis Summary (Phase 2B Input)

**Hypothesis ID:** H-PBFF-001
**Confidence:** 0.88 (HIGH)
**Date:** 2026-02-08
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Core Hypothesis Statement

**Main Hypothesis:**
If ML models that integrate behavioral science principles are evaluated using psychometric validation methods (construct validity, convergent validity, discriminant validity) with behavioral experiment test batteries, then the resulting fidelity metrics (CVS, DVS, CVI) will quantitatively distinguish models with high behavioral fidelity from those optimized only for task performance.

**Why:** Psychometric validity measures capture alignment between model outputs and human behavioral patterns across multiple constructs rather than single-task accuracy.

**Alternative (H0):** Psychometric metrics will NOT reliably distinguish behavioral-integrated from task-optimized models.

---

## Key Variables

| Type | Variable | Operationalization |
|------|----------|-------------------|
| **Independent** | Behavioral Integration Method | Type of behavioral principle (Prospect Theory, Cognitive Biases, Social Preferences, None) |
| **Dependent** | CVS (Convergent Validity Score) | Pearson r with human benchmark on construct-relevant tasks (threshold: r ≥ 0.70) |
| **Dependent** | DVS (Discriminant Validity Score) | Pearson r on construct-irrelevant tasks (threshold: r ≤ 0.30) |
| **Dependent** | CVI (Construct Validity Index) | (CVS_avg - DVS_avg) / (CVS_avg + DVS_avg), range [-1, 1] |

---

## Causal Mechanism (First Principles)

```
Behavioral Construct (e.g., Loss Aversion)
    ↓
Human Multi-Task Response Pattern (systematic co-variation)
    ↓
Psychometric Validation Detection:
    • CVS: Model correlates with construct-RELEVANT tasks
    • DVS: Model UNCORRELATED with construct-IRRELEVANT tasks
    ↓
CVI Composite: (CVS - DVS) / (CVS + DVS)
    ↓
DISTINGUISHES:
    • High CVI (>0.40): Genuine behavioral fidelity (pattern replication)
    • Low CVI (<0.20): Task optimization only (no construct alignment)
```

**Core Principle:** Psychometric metrics detect PATTERN-LEVEL similarity (multi-task correlation structure) vs. TASK-LEVEL accuracy (single-task performance).

---

## Testable Predictions

**P1 (Primary):** Behavioral-integrated models: CVS ≥ 0.70; Baseline models: CVS < 0.50 (ΔCVS ≥ 0.20)

**P2 (Discriminant):** Behavioral models with high CVS: DVS ≤ 0.30; Baseline: DVS > 0.30

**P3 (Composite):** Behavioral models: CVI > 0.40; Baseline: CVI < 0.20 (ΔCVI ≥ 0.20)

**P4 (Multi-Population):** CVS variance across 3 populations < 0.15 (consistent fidelity)

**P5 (Held-Out):** CVS_training - CVS_heldout < 0.10 (minimal overfitting)

**Falsification Criteria:**
- FC1: ΔCVS < 0.10 (no discrimination) → Framework fails
- FC2: CVS uncorrelated with expert ratings (r < 0.30) → Construct transfer fails
- FC3: DVS ≥ CVS → Metric invalidity
- FC4: Population variance > 0.30 → Overfitting
- FC5: CVS drop > 0.25 on held-out → Memorization

---

## Key Assumptions (Risk Assessment)

| Assumption | Risk | Mitigation |
|-----------|------|-----------|
| **A1:** Behavioral constructs measurable in ML outputs | MEDIUM | Empirical validation with expert ratings |
| **A2:** Correlation captures behavioral similarity | LOW | 60+ years psychometric evidence |
| **A3:** Human benchmark data valid ground truth | MEDIUM | Use meta-analyses (Many Labs, OSF) |
| **A4:** Psychometric principles transfer to ML | MEDIUM-HIGH | Novel transfer, requires validation |
| **A5:** Behavioral fidelity ⊥ task performance | MEDIUM | Empirically testable (correlation analysis) |

---

## Scope

**In Scope:**
ML models with behavioral integration, constructs from psychology/behavioral economics, post-hoc validation, comparison vs. baselines

**Out of Scope:**
Model development, task performance replacement, causal understanding, real-time behavior, neuroscience validation, safety-critical applications

**Boundary Conditions:**
≥100 participants per experiment, ≥3 constructs, ≥3 populations, ≥20 tasks

---

## Statistical Design

**Study:** Multi-model comparison (N=18: 12 behavioral + 6 baseline × 3 architectures)
**Constructs:** k=5 (loss aversion, confirmation bias, social reciprocity, temporal discounting, framing)
**Test Battery:** n=30 tasks (6 per construct)
**Populations:** p=3 (Western, East Asian, Middle Eastern)
**Split:** 80% training / 20% held-out

**Primary Test:** Independent t-test (behavioral vs. baseline CVS), α=0.05, power=0.80, detectable d=0.80
**Secondary Tests:** Paired t-test (CVS vs. DVS), Levene's test (population variance), ANOVA (CVI across types)

---

## Contributions

**Theoretical:**
- Construct validity framework for ML evaluation
- Behavioral fidelity as distinct from task performance
- Cross-domain transfer from psychometrics to ML

**Methodological:**
- Standardized behavioral validation protocol
- CVS/DVS/CVI metrics with thresholds
- Multi-population robustness framework

**Practical:**
- Verification of behavioral integration claims
- Model comparison benchmarking
- Reusable behavioral test battery
- Quality gate for behavioral AI applications

---

## Related Work (Key Papers)

**Foundations:**
1. Campbell & Fiske (1959) - Convergent/discriminant validity (FOUNDATIONAL)
2. Cronbach & Meehl (1955) - Construct validity (FOUNDATIONAL)
3. Messick (1995) - Unified validity framework

**Evidence Base:**
4. Chiu et al. (2016, 51 cites) - Measurement invariance demonstration
5. Aran et al. (2021, 13 cites) - Multi-group validation
6. Marsall et al. (2023, 8 cites) - Recent convergent/discriminant validation

**ML Context (Gap):**
7. Hsiao (2024, 7 cites) - Domain-specific behavioral measurement (no framework)
8. Cha & Lee (2021, 4 cites) - Small-sample behavioral inference (not systematic)
9. RLHF literature - Alignment without construct validation

**Novelty:** FIRST systematic application of psychometric construct validation to ML behavioral models.

---

## Phase 2B Sub-Hypothesis Seeds

**SH1 (Existence - Metric Validity):**
Do CVS/DVS/CVI metrics reliably measure behavioral fidelity with thresholds (r ≥ 0.70, r ≤ 0.30) distinguishing model types?

**SH2 (Mechanism - Construct Transfer):**
Do behavioral constructs from psychology transfer to ML such that models replicating human patterns show high CVS + low DVS?

**SH3 (Comparison - Orthogonality):**
Is behavioral fidelity (CVI) orthogonal to task performance (accuracy), demonstrating independent evaluation dimensions?

---

## Open Questions for Phase 2B

1. **Threshold Calibration:** Are r ≥ 0.70 / r ≤ 0.30 optimal for ML context?
2. **Construct Granularity:** Broad (social preferences) vs. fine-grained (reciprocity in trust games)?
3. **Temporal Stability:** How to operationalize test-retest for stochastic/evolving models?
4. **Adversarial Probes:** What defines edge case behavioral tests?
5. **Architecture Sensitivity:** Does PBFF effectiveness vary by architecture?
6. **Population Variance:** Is variance < 0.15 the right threshold for all constructs?
7. **Battery Standardization:** Single canonical battery vs. domain-specific?
8. **Computational Cost:** Minimum viable battery size?

---

**Full Documentation:** `02a_extended_hypothesis_full.md`
**Next Phase:** Phase 2B - Verification Planning (Sub-hypothesis decomposition)
**Command:** `/phase2b-planning`

---

*Generated: 2026-02-08 | Mode: YOLO Batch | Source: Round 1 FEASIBLE hypothesis*
