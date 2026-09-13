# Targeted Research Report: Classical Variance Measurement in Neural Network Training

**Generated:** 2026-03-20 23:23:19
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
---

## Executive Summary

**Research Question:** Does reproducible accuracy variance exist and remain measurable for 1-hidden-layer MLP on MNIST using classical statistics with N≥30 seeds?

**Search Strategy:** ROUTE_TO_0 mode - Failure-aware queries prioritizing alternatives to 7 previous failures (theoretical complexity, computational infeasibility, sample size inadequacy).

**Sources Collected:** 48 verified sources (23 Archon KB + 25 Semantic Scholar papers, 0-313 citations)

**Key Finding:** **LITERATURE GAP CONFIRMED** - No published classical variance baseline for MNIST MLP exists, despite:
- Complex variance methods available (quantum NNs, mean-variance estimation networks)
- Seed effect studies on CIFAR-10, ImageNet, LLMs
- Theoretical foundations (N≥30 criterion, PyTorch seed control)

**Critical Gaps Identified:**
1. **Gap 1 (P0)**: Validated classical σ²=Var[accuracy] baseline for simple NNs
2. **Gap 2 (P1)**: Empirical validation of N≥30 sample size threshold
3. **Gap 3 (P2)**: Computational feasibility benchmarks (<10min constraint)

**Phase 2A Readiness:** ✅ READY - Clear gap, theoretical foundations, implementation guidance, 25 papers with arXiv IDs available for download

---

## Key Papers for Phase 2A Download

1. **Picard 2021** - "Torch.manual_seed(3407) is all you need..." (arXiv:2109.08203, 123 cit)
   - Random seed variance on CIFAR-10, scanned 10^4 seeds

2. **Rajput 2023** - "Evaluation of decided sample size in ML" (DOI:10.1186/s12859-023-05156-9, 313 cit)
   - N≥30 criterion, effect size ≥0.5, accuracy ≥80%

3. **Ghasemzadeh 2023** - "Generalizable ML Models" (arXiv:2308.11197, 29 cit)
   - Nested k-fold reduces required N by 50%

4. **Zhou 2025** - "Random Seeds on Fine-Tuning LLMs" (arXiv:2503.07329, 5 cit)
   - Macro + micro variance metrics

5. **Sluijterman 2023** - "Optimal Training of MVE Networks" (arXiv:2302.08875, 39 cit)
   - Mean-variance estimation optimization

---

## Research Gaps (CRITICAL for Phase 2A)

### Gap 1: Validated Classical Variance Baseline for Simple Neural Networks (P0 - CRITICAL)

**Current State:** Literature contains complex variance methods but NO simple, validated baseline for classical σ²=Var[accuracy] on foundational tasks like MNIST MLP.

**Missing Piece:**
- Published protocol for measuring test accuracy variance on MNIST MLP
- Classical statistical variance (no novel frameworks)
- Validates N≥30 empirically
- Demonstrates <10min computational feasibility
- Baseline values for comparison (mean accuracy, σ², CI width)

**Evidence:**
- PyTorch docs provide seed control but no experimental validation
- Picard 2021 uses CIFAR-10, not MNIST baselines
- Rajput 2023 provides theory, not specific baseline experiments
- Archon KB: No MNIST MLP variance baseline repos found

**Impact:** Establishes foundational measurement infrastructure before complex UQ methods, prevents Runs 1-7 type failures

### Gap 2: Empirical Validation of N≥30 Sample Size Threshold (P1 - HIGH)

**Missing:** Empirical demonstration that N=30 seeds produces stable variance estimate (CI width <50%) on MNIST MLP

**Evidence:** Rajput 2023 theory, Ghasemzadeh 2023 k-fold method, but no MNIST validation

### Gap 3: Computational Feasibility Benchmarks (P2 - MEDIUM)

**Missing:** Published timing data for N=30 seed experiments on standard hardware (single GPU)

**Evidence:** Phase 0 identified "10-20h experiments never executed" as failure mode

---

## Implementation Guidance from Research

**From Archon (PyTorch Documentation):**
```python
import torch
torch.manual_seed(seed)  # Control RNG
torch.backends.cudnn.deterministic = True  # CUDA determinism
torch.use_deterministic_algorithms(True)  # Force deterministic ops

# For DataLoader
def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    numpy.random.seed(worker_seed)
    random.seed(worker_seed)

g = torch.Generator()
g.manual_seed(0)
DataLoader(dataset, worker_init_fn=seed_worker, generator=g)
```

**From Scholar Papers:**
- N≥30 seeds (Rajput 2023 criterion)
- Nested k-fold validation (Ghasemzadeh 2023 recommendation)
- Track both macro (accuracy variance) and micro (prediction consistency) metrics (Zhou 2025)

**Recommended Protocol:**
1. Use PyTorch `torch.manual_seed()` for RNG control
2. Implement N=30 independent runs with seeds 0-29
3. Apply nested k-fold validation
4. MLP architecture: 1 hidden layer, MNIST dataset, 10 epochs
5. Measure variance: `σ² = np.var(test_accuracies)`
6. Verify CI width <50%, timing <10min

---

## Answer to Research Question (Preliminary)

**Q1: Can we measure σ² across N≥30 runs?**
✅ YES - PyTorch provides seed control, literature confirms feasibility

**Q2: Is σ² statistically distinguishable from zero?**
⚠️ LIKELY YES - Picard 2021 found variance even with controlled seeds, needs MNIST validation

**Q3: Does variance estimate stabilize (CI width <50%)?**
⚠️ EXPECTED YES - Rajput 2023 criteria suggest N≥30 sufficient, needs empirical confirmation

**Q4: Can protocol execute in <10 minutes?**
✅ HIGHLY LIKELY - MNIST MLP is lightweight

**Q5: Do multiple runs produce consistent estimates?**
⚠️ UNKNOWN - No literature data, requires experimental validation

**Overall:** Research question is **feasible and addresses documented gap**

---

## Phase 2A Next Steps

1. Download 5 key papers (arXiv IDs provided above)
2. Formulate testable hypotheses addressing Gaps 1-3
3. Design experiments: N=30 seeds, MNIST MLP, <10min constraint
4. Specify success criteria: σ²>0, CI width <50%, timing <10min

---

*Report generated by YouRA Deep Learning Research Analyst*
*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~12 minutes*
