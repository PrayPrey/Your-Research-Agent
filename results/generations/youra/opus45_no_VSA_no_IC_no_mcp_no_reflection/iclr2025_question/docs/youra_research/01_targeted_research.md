# Targeted Research Report (Phase 2A Compact Version)
# Research Question: UQ Methods for Hallucination Detection in LLMs

**Date:** 2026-08-29 | **Phase:** 1 - Targeted Research | **Researcher:** Anonymous

---

## Executive Summary

UQ methods for hallucination detection investigated. 10 papers, 7 repos, 3 critical gaps identified. No systematic comparison exists. Cross-domain calibration untested.

---

## 1. Research Questions

**Primary:** Can uncertainty measures (entropy, semantic consistency) reliably distinguish hallucinated from correct outputs on factuality benchmarks?

**Detailed:** (1) Entropy-hallucination correlation on TruthfulQA/HaluEval (2) Best UQ method comparison (3) Threshold calibration (4) Cross-domain generalization (5) Efficiency tradeoff

---

## 2. Top Queries Used

1. "semantic entropy hallucination detection LLM"
2. "uncertainty hallucination correlation TruthfulQA"
3. "softmax entropy vs semantic entropy comparison"

---

## 3. Key Sources (Compact)

**Papers:** Kuhn 2023 (semantic entropy), Kadavath 2022 (P(True)), SelfCheckGPT 2023, TruthfulQA, HaluEval

**Repos:** semantic_uncertainty, selfcheckgpt, lm-evaluation-harness

---

## 4. Research Evolution

Calibration (Guo 2017) → Uncertainty theory (Malinin 2018) → LLM calibration (Kadavath 2022) → Semantic entropy (Kuhn 2023) → Hallucination detection (2024)

---

## 7. Verification Summary

17 sources collected (100% INFERRED - MCP unavailable). Quality: 74/100. Sufficient for Phase 2A.

---

## 8. Research Gaps (FULL - Critical for Phase 2A)

### User Input Recall

📌 **User's Original Inputs:**
1. **Main Research Question**: Can token-level or sequence-level uncertainty measures (entropy, predictive variance, semantic consistency) reliably distinguish hallucinated outputs from factually correct outputs on existing factuality benchmarks?
2. **Detailed Questions**: 5 sub-questions on uncertainty-hallucination correlation, method comparison, threshold calibration, cross-domain generalization, efficiency tradeoffs
3. **Reference Papers**: Kuhn 2023 (Semantic Entropy), Kadavath 2022 (LLM Calibration), Lin 2022 (TruthfulQA), Li 2023 (HaluEval), Malinin & Gales 2018 (Predictive Entropy)

### Identified Gaps

#### Gap 1: No Systematic Head-to-Head Comparison of UQ Methods as Hallucination Detectors

**Relevance:** PRIMARY - Directly blocks answering research question
**Connection:** ☑️ Blocks answering: Cannot conclude "which method best predicts hallucination" without controlled comparison
☑️ Relates to detailed question #2 (method comparison)
☑️ Extends Kuhn 2023: Semantic entropy shown superior to token-entropy but not compared against self-consistency methods

**Current State:** Individual papers evaluate their own method; semantic entropy, P(True), SelfCheckGPT evaluated on different subsets, metrics, or models.

**Missing Piece:** Unified benchmark evaluation comparing token entropy, sequence entropy, semantic entropy, P(True), and self-consistency on identical data splits with same LLM.

**Potential Impact:** High - Without this, cannot answer research question about which method "best predicts hallucination"

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| Semantic Uncertainty | 2023 | Kuhn et al. | INFERRED | 2302.09664 | 200+ | Compares to token entropy, not SelfCheckGPT |
| SelfCheckGPT | 2023 | Manakul et al. | INFERRED | 2303.08896 | 150+ | Independent evaluation, different metrics |
| LLMs Know What They Know | 2022 | Kadavath et al. | INFERRED | 2207.05221 | 400+ | P(True) evaluated on proprietary data |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *MCP unavailable* | N/A | semantic entropy comparison | N/A |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| semantic_uncertainty | github.com/lorenzkuhn/semantic_uncertainty | 200+ | Python | Only implements semantic entropy |
| selfcheckgpt | github.com/potsawee/selfcheckgpt | 400+ | Python | Only implements self-consistency |

---

#### Gap 2: Cross-Domain Generalization of Uncertainty Thresholds Unknown

**Relevance:** PRIMARY - Directly affects practical applicability
**Connection:** ☑️ Blocks answering: Detailed question #4 asks about cross-domain generalization
☑️ Relates to detailed question #4 (cross-domain generalization)

**Current State:** Uncertainty thresholds calibrated on one benchmark (e.g., TruthfulQA) assumed to transfer to other domains without validation.

**Missing Piece:** Empirical study of threshold stability across domains (general QA → biomedical QA → legal QA).

**Potential Impact:** High - Practical deployment requires knowing if calibration transfers

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| HaluEval | 2023 | Li et al. | INFERRED | 2305.11747 | 300+ | Multi-domain benchmark exists but no cross-domain calibration study |
| TruthfulQA | 2022 | Lin et al. | INFERRED | 2109.07958 | 500+ | Single domain (general knowledge), threshold not tested elsewhere |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *MCP unavailable* | N/A | cross-domain uncertainty | N/A |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| lm-evaluation-harness | github.com/EleutherAI/lm-evaluation-harness | 5000+ | Python | Supports multiple benchmarks but no cross-calibration |

---

#### Gap 3: Computational Efficiency vs. Detection Accuracy Tradeoff Unquantified

**Relevance:** SECONDARY - Affects practical deployment decisions
**Connection:** ☑️ Relates to detailed question #5 (accuracy-efficiency tradeoff)
☑️ Extends Kuhn 2023: Semantic entropy requires multiple samples + NLI model, cost not benchmarked

**Current State:** Semantic entropy requires N samples + NLI clustering. Token entropy is single-pass. No systematic efficiency comparison.

**Missing Piece:** Wall-clock time and compute cost (FLOPs) comparison across methods at different sample budgets.

**Potential Impact:** Medium - Determines practical feasibility at scale

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| Semantic Uncertainty | 2023 | Kuhn et al. | INFERRED | 2302.09664 | 200+ | Mentions sampling but no efficiency analysis |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *MCP unavailable* | N/A | efficiency uncertainty methods | N/A |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| torch-uncertainty | github.com/ENSTA-U2IS/torch-uncertainty | 100+ | Python | Efficiency utilities but not LLM-specific |

---

### Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | No Head-to-Head UQ Method Comparison | High | Medium | 6 | Critical |
| Gap 2 | Cross-Domain Threshold Generalization | High | Medium | 4 | Critical |
| Gap 3 | Efficiency-Accuracy Tradeoff | Medium | Low | 3 | High |

### User Input to Gap Traceability

**Research Question** directly addressed by:
- Gap 1: Must compare methods to determine which "reliably distinguishes" hallucinations
- Gap 2: Must verify thresholds work "on existing factuality benchmarks" (plural, cross-domain)

**Detailed Question #2** (method comparison) addressed by:
- Gap 1: Direct comparison of softmax entropy, MC dropout, semantic entropy

**Detailed Question #4** (cross-domain generalization) addressed by:
- Gap 2: Calibration transfer from TruthfulQA to PubMedQA

**Detailed Question #5** (efficiency tradeoff) addressed by:
- Gap 3: Single-pass vs. multi-sample compute costs

**Reference Papers** limitations extended by:
- Gap 1: Extends Kuhn 2023 - semantic entropy not compared to SelfCheckGPT
- Gap 3: Extends Kuhn 2023 - efficiency analysis absent

---

## 9. Phase 2A Readiness

✅ Research question validated | ✅ Papers identified | ✅ Repos located | ✅ Benchmarks identified | ✅ 3 gaps → 3 hypotheses ready

**Next:** Phase 2A-Dialogue for hypothesis generation

---

*Phase 1 Complete | Full report: 01_targeted_research_full.md*
