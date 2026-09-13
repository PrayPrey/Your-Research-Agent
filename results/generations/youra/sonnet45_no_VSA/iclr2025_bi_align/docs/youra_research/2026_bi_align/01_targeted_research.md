# Targeted Research Report: Dataset Training Accessibility Prediction via Combined MSI+SAT Profiling

**Date:** 2026-07-10
**Phase:** 1 - Targeted Research Gathering
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
**Mode:** ROUTE_TO_0 (Failure Recovery)

---

## Executive Summary

**Research Question:** Can a combined MSI+SAT predictor accurately classify datasets as training-accessible vs training-inaccessible using lightweight sample-based profiling?

**Key Findings:**
1. Pre-execution OOM prediction emerged 2025-2026 (VeritasEst: 84% error reduction, xMem, RTX-OOM-Guard)
2. All tools use single-metric (memory OR throughput), none combine MSI+SAT dual metrics
3. Sample-based profiling theory exists, no DL implementation for lightweight profiling
4. No public dataset with training accessibility labels (only internal H-E1/H-E3 ground truth)

**Research Gaps (3 Priority):**
- **P0 Gap 1:** No combined MSI+SAT dual-metric predictor
- **P1 Gap 2:** No lightweight sample-based profiling implementation
- **P1 Gap 3:** No validated ground truth dataset

**Phase 2 Readiness:** ✅ READY (61 items collected, 8 arXiv IDs, 3 gaps identified)

---

## Research Questions

### Primary
Can a combined structural predictor (MSI for memory stress + SAT for throughput variance) accurately classify datasets as training-accessible vs training-inaccessible, using lightweight sample-based profiling instead of full dataset loading?

### Detailed
1. Optimal MSI+SAT combination rule for OOM + throughput failure prediction?
2. Sample size needed for stable MSI/SAT estimation without full dataset streaming?
3. Do MSI+SAT predictions match REAL training outcomes (WildChat OOM, PersonaChat/DailyDialog success) better than SAT-only?
4. Does predictor generalize across dataset types (dialogue, QA, long-form)?
5. Can predictor save researcher time (identify inaccessible datasets BEFORE experiment setup)?

### Lessons from Previous Attempts (ROUTE_TO_0)

**H-E1 Failure (WildChat OOM):**
- Root Cause: Streaming timeout >10 min, training OOM from gradient memory
- Lesson: Data accessibility must be validated BEFORE hypothesis testing
- Avoidance: Use lightweight sample-based profiling (no full dataset loading)

**H-E3 Failure (SAT-only 50% accuracy):**
- Root Cause: Inference metrics (SAT) don't predict training memory (gradients + optimizer)
- Lesson: Need MSI (training memory) + SAT (throughput) orthogonal predictors
- Avoidance: Combine MSI (memory stress) + SAT (variance) dual metrics

---

## Top Research Findings

### Academic Literature (Scholar - 11 papers, 8 with arXiv)

**Directly Relevant:**

1. **VeritasEst (2025)** - arXiv:2504.03887
   - CPU-based offline OOM prediction (no GPU access)
   - 84% error reduction, 73% lower failure probability
   - **Relevance:** Pre-execution training accessibility prediction

2. **GPU Memory Prediction for Multimodal Models (2025)** - arXiv:2512.07853
   - Architecture-based memory estimation (8.7% MAPE)
   - **Relevance:** Validates factorization approach for MSI metric

3. **Profiling and Monitoring DL Training (2023)**
   - Survey of nvidia-smi, DCGM, framework-based profilers
   - **Relevance:** Tools for SAT metric collection (throughput variance)

### GitHub Implementations (Exa - 15 repos)

**OOM Prediction Tools:**

1. **xMem** (2 stars) - github.com/Stone-ResearchLife/xMem
   - CPU-based GPU memory estimator (matches VeritasEst approach)
   - **Relevance:** Offline prediction (pre-execution OOM prevention)

2. **RTX-OOM-Guard** (0 stars, 2026) - github.com/poojakira/Predictive-GPU-Memory-Defragmenter
   - Proactive OOM prediction, fragmentation modeling
   - **Relevance:** Training-time OOM prevention

3. **pytorch_memlab** (1078 stars) - github.com/Stonesjtu/pytorch_memlab
   - Line-profiler style CUDA memory management
   - **Relevance:** Memory profiling tool for MSI metric collection

4. **LLMem** (30 stars) - github.com/taehokim20/LLMem
   - Memory estimation for fine-tuning (distributed training methods)
   - **Relevance:** Training memory estimation (supports MSI concept)

---

## Research Gaps

### Gap 1: No Combined MSI+SAT Dual-Metric Predictor (P0 - CRITICAL)

**Current State:** Tools address EITHER memory (MSI) OR throughput (SAT), not both in unified predictor.

**Missing:**
- No academic paper on dual-metric (MSI + SAT) for orthogonal failure modes
- No GitHub implementation combining memory stress + throughput variance
- Existing tools focus single mode: OOM (xMem, VeritasEst) OR throughput (profilers)

**Impact:** H-E3 failure would repeat (SAT-only 50% accuracy), dual failures missed

**Evidence:**
- Scholar: VeritasEst (memory only), Profiling survey (throughput only)
- Exa: xMem (memory only), pytorch_memlab (memory only), stormlog (throughput only)
- **NO source combines MSI + SAT**

### Gap 2: No Lightweight Sample-Based Profiling (P1 - HIGH)

**Current State:** Tools require FULL dataset loading (defeats pre-execution prediction purpose).

**Missing:**
- No implementation of statistical sampling for MSI/SAT from N << dataset_size samples
- No validation of minimum sample size (N=100-500) for stable estimation

**Impact:** H-E1 failure would repeat (>10 min timeout for WildChat-1M 27GB streaming)

**Evidence:**
- Scholar: Sampling theory exists (Dagdoug 2026) - NO DL application
- Exa: pytorch_memlab requires FULL training run

### Gap 3: No Validated Ground Truth Dataset (P1 - HIGH)

**Current State:** No public dataset with labeled training accessibility outcomes.

**Missing:**
- No public dataset: accessible vs inaccessible labels
- Only internal: H-E1 (WildChat FAIL), H-E3 (PersonaChat/DailyDialog PASS)

**Impact:** Cannot validate MSI+SAT predictor accuracy, unknown generalization

**Evidence:**
- Scholar: VeritasEst validated on CNNs - NO binary classification dataset
- Exa: GPUMemNet synthetic data - NOT real training outcomes

---

## Preliminary Answers to Detailed Questions

**Q1: Optimal MSI+SAT combination rule?**
- A: Dual-threshold (MSI > 0.7 OR P95/Median > 3.0 → FAIL)
- Validation: ROC curve on ground truth (Gap 3)

**Q2: Sample size for stable estimation?**
- A: 100-500 samples (Central Limit Theorem)
- Validation: Empirical confidence interval study (Gap 2)

**Q3: MSI+SAT better than SAT-only?**
- A: YES (theoretical) - SAT-only missed H-E1 OOM
- Validation: Experimental comparison (Gap 3)

**Q4: Cross-domain generalization?**
- A: UNKNOWN - No cross-domain validation found
- Validation: Test on dialogue, QA, long-form

**Q5: Time savings?**
- A: YES (if profiling <1 min vs H-E1 >10 min timeout)
- Validation: Practical deployment (Gap 2)

---

## Next Steps (Phase 2A Inputs)

**Hypothesis Generation:**
1. Design MSI+SAT combined predictor (Gap 1)
2. Propose lightweight sample-based profiling protocol (Gap 2)
3. Create validation protocol using H-E1/H-E3 ground truth (Gap 3)

**Key References for Phase 2A:**
- VeritasEst (2025) - arXiv:2504.03887 (CPU-based OOM prediction)
- Statistical sampling (2026) - arXiv:2604.01160 (sample-based estimation)
- xMem (GitHub) - CPU-based memory estimator
- pytorch_memlab (GitHub) - Memory profiling tool

**Validation Targets:**
- WildChat: KNOWN FAIL (H-E1 OOM timeout)
- PersonaChat: KNOWN PASS (H-E3 success)
- DailyDialog: KNOWN PASS (H-E3 success)

---

*Full report: 01_targeted_research_full.md (1381 lines)*
*Compact report: 01_targeted_research.md (this file)*
*Processing time: ~8 minutes*
*Research items: 61 (11 Scholar + 15 Exa + 5 Archon verified + 7 inferred + 4 references + 19 tangential)*
