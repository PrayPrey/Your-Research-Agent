# Phase 1: Research Summary — h-m-pareto

**Date:** 2026-08-20
**Research Question:** Do different UQ methods exhibit cost-performance trade-offs in selective prediction tasks?
**Hypothesis ID:** h-m-pareto

---

## Research Context

Building on h-m-integrated validation (all UQ methods produce valid uncertainty rankings), investigating whether cost-performance Pareto frontiers exist across 6 UQ methods.

---

## Key Findings

### 1. Pareto Frontier for UQ Methods

**Source:** Archon Knowledge Base + Exa GitHub search
**Key Insight:** No direct UQ-specific Pareto frontier analysis found, but domain-general multi-objective optimization applies

**Evidence:**
- Pareto frontier construction is standard practice in cost-performance analysis
- Limited results for "Pareto frontier + UQ" combination
- Implementation relies on dominance checking (cost_j ≤ cost_i AND metric_j > metric_i)

### 2. UQ Method Implementations

**Source:** TorchCP (https://github.com/atzamis/TorchCP), retinal-selective-prediction (https://github.com/ShahnawazKakarh/retinal-selective-prediction)

**Key Findings:**
- **MC Dropout (T=30)**: Best AURC (0.0756) in retinal benchmark
- **Temperature Scaling**: ECE 0.146→0.055 (62% calibration improvement)
- **Conformal Prediction**: 90.2% coverage @ α=0.10, avg set size 1.35
- **No universal dominance**: "Three different methods, three different wins"

**Trade-off Evidence:**
- TS4CP paper: Non-monotonic trend between temperature and prediction set size
- MC dropout cost scales linearly with k (k forward passes)
- Temperature scaling / conformal prediction are post-hoc (1× cost)

### 3. Implementation Patterns

**Cost Measurement:**
- Time multiple runs, average over N passes
- Normalize to baseline (1.0× for single forward pass)
- MC dropout: k× baseline for k passes

**AUROC Computation:**
- sklearn.metrics.roc_auc_score(y_true=correctness, y_score=uncertainty)
- Correctness binary label from ground truth comparison

**Pareto Frontier Construction:**
- Collect (cost, AUROC) pairs for all methods
- Dominance check: Method j dominates i if cost_j ≤ cost_i AND auroc_j > auroc_i (statistically significant)
- Pareto set: All non-dominated methods

---

## Reference Papers

### Primary References

1. **"On Temperature Scaling and Conformal Prediction of Deep Classifiers"** (ICML)
   - Authors: Lahav Dabah et al.
   - Repository: https://github.com/lahavdabah/TS4CP
   - Key Finding: Non-monotonic trade-off between temperature and prediction set size

2. **Retinal Selective Prediction Benchmark**
   - Repository: https://github.com/ShahnawazKakarh/retinal-selective-prediction
   - Methods Compared: Softmax, MC dropout, ensembles, temperature scaling, conformal, evidential
   - Key Result: MC dropout T=30 best AURC, but no method universally dominates

3. **TorchCP Library**
   - Repository: https://github.com/atzamis/TorchCP
   - Implementation: GPU-accelerated conformal prediction (90% ImageNet inference reduction)
   - Methods: LAC, APS, SAPS, RAPS score functions

---

## Gap Analysis

**What's Missing:**
- No prior work applies Pareto frontier analysis to UQ methods specifically
- Most benchmarks report single metric (AUROC or calibration), not multi-objective trade-offs

**Research Opportunity:**
- Novel contribution: Characterize cost-performance Pareto frontier for 6 UQ methods on TruthfulQA
- Expected insight: Different methods occupy different efficiency zones (low-cost calibration vs high-cost accuracy)

---

## Dataset Selection

**Primary:** TruthfulQA (817 questions, adversarial QA)
**Calibration:** HaluEval (~10k samples for temperature scaling / conformal prediction)

**Rationale:**
- TruthfulQA provides correctness ground truth (correct_answers field)
- Selective prediction task aligns with AUROC evaluation
- HaluEval enables calibration without test set leakage

---

## Hypothesis Formation

**Testable Claim:** At least 2 methods are Pareto-optimal (no method strictly dominates with p < 0.05)

**Predictions:**
- H1: MC dropout k=5 achieves highest AUROC (per retinal benchmark)
- H2: Temperature scaling competitive with MC k=5 (|AUROC difference| ≤ 0.05)
- H3: Cost-performance trade-off exists (|Pareto_set| ≥ 2)

**Mechanistic Explanation:**
- MC dropout: High computational cost (k× passes) → high uncertainty quality (averaging reduces variance)
- Temperature scaling: Low cost (post-hoc) → competitive calibration (rescales logits without extra inference)
- Conformal prediction: Low cost (post-hoc) → different efficiency zone (set-valued predictions)

---

*Next Phase: 02a_hypotheses.md — Formalize competing hypotheses and prerequisites*
