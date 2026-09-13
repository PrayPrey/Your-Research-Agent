# Phase 2B Context: H-M2

**Generated:** 2026-07-13T09:24:39+00:00
**Source:** 02b_verification_plan.md (Section 2.2)
**Hypothesis ID:** H-M2
**Type:** MECHANISM

---

## Hypothesis Information

### Statement
Aggregated benchmark results from literature provide sufficient training examples (50-60 datasets) to learn feature-method relationships.

### Rationale
Tests causal step 2 of 4. OGB+FedML+LEAF+pFL-Bench+Champneys+Zhou = 48-60 total benchmarks.

### Type
MECHANISM

---

## Variables

**Independent Variables:**
- Training set size (50-55 benchmarks in leave-5-out CV)

**Dependent Variables:**
- Meta-classifier cross-validation accuracy

**Controlled Variables:**
- Leave-5-out CV protocol
- Stratification by domain

---

## Experimental Setup

**Dataset:**
- Name: Aggregated Benchmark Collection
- Type: custom (reuse from H-E1)
- Source: Multi-source literature mining (OGB, FedML, LEAF, pFL-Bench, Papers with Code, Manual)
- Path: ../h-e1/code/output/benchmarks.json
- Hypothesis Fit: 63 benchmarks provide sufficient training examples (exceeds 50-60 target)

**Model:**
- Name: Random Forest Meta-Classifier
- Type: Ensemble tree-based classifier
- Source: scikit-learn RandomForestClassifier(n_estimators=100, max_depth=10)
- Hypothesis Fit: Robust to small sample sizes, interpretable feature importance, handles nonlinear relationships

---

## Verification Protocol

1. Run 10 rounds of leave-5-out CV on collected benchmarks
2. Train Random Forest on 50-55, test on 5 held-out
3. Measure accuracy: predicted method's actual ranking percentile

---

## Success Criteria (SHOULD_WORK Gate)

**Primary:**
- CV accuracy >45% (better than 40% domain folklore baseline)

**Secondary:**
- Accuracy stable across CV rounds (std < 10%)

---

## Failure Response

- IF accuracy <45%: PIVOT to collect more benchmarks or reduce method granularity

---

## Dependencies

**Prerequisites:** H-M1 (SHOULD_WORK gate)

**Falsifier:** If <30 benchmarks collectible or lack diversity

---

## Baseline Comparison Targets

**Baseline:** Random method selection (30% expected) and domain folklore (40% expected)

**Expected:** CV accuracy >45% demonstrates that 50-60 training examples provide sufficient signal for meta-learning

---

## Source Reference

Phase 2A Causal Step 2
Phase 2B Section 2.2: H-M2 specification
