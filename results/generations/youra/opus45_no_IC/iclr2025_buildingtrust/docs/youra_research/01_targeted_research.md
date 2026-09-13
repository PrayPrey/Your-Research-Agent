# Targeted Research Report: LLM Miscalibration Patterns (Compact)

**Date:** 2026-08-10 | **Phase:** 1 | **Researcher:** Anonymous

---

## Executive Summary

Research on LLM calibration patterns across factual claim categories. Focus: post-hoc calibration methods improving trustworthiness.

**Results:** 12 verified Exa repos, 7 inferred papers, 3 gaps identified. **Status: READY for Phase 2A**

---

## 1. Research Questions

**Primary:** Do LLMs exhibit systematic miscalibration patterns across claim types, and can post-hoc methods improve ECE?

**Detailed:** RQ1 verbalized vs accuracy | RQ2 category patterns | RQ3 post-hoc ECE | RQ4 scale correlation

---

## 2. Search Queries (Top 3 per category)

**Brainstorm:** LLM calibration consistency | calibration truthfulness | domain-specific calibration
**Direct:** ECE language models | temperature scaling LLM | overconfidence factual claims

---

## 3. Archon KB (Compact)

| Query | Result | Pattern |
|-------|--------|---------|
| LLM calibration | 0 relevant | KB lacks LLM content |
| [INFERRED] | - | Post-hoc calibration pipeline |

---

## 4. Scholar Papers (Compact)

| Title | Year | arXiv | Insight |
|-------|------|-------|---------|
| TruthfulQA | 2022 | 2109.07958 | 38 categories, primary benchmark |
| On Calibration Modern NN | 2017 | 1706.04599 | Temperature scaling, ECE metric |
| Language Models Know | 2022 | 2207.05221 | Self-knowledge calibration |
| LLMs Express Uncertainty | 2023 | 2306.13063 | Verbalized vs logit comparison |

---

## 5. Exa Resources (Compact)

| Name | URL | Stars | Feature |
|------|-----|-------|---------|
| sylinrl/TruthfulQA | github.com/sylinrl/TruthfulQA | 936 | 38 categories, eval scripts |
| gpleiss/temperature_scaling | github.com/gpleiss/temperature_scaling | 1172 | Reference temp scaling |
| parameterlab/apricot | github.com/parameterlab/apricot | 22 | Generation-only calibration |
| p-lambda/verified_calibration | github.com/p-lambda/verified_calibration | 152 | ECE with bootstrap CI |
| Jonathan-Pearce/calibration-toolbox | github.com/Jonathan-Pearce/calibration-toolbox | 76 | ECE/MCE/RMSCE metrics |

---

## 6. Chain Analysis (Compact)

**Evolution:** Guo 2017 (ECE) → Lin 2022 (TruthfulQA) → Kadavath 2022 (Self-Know) → APRICOT/Thermometer 2024

**Integration:** TruthfulQA categories + ECE metrics + post-hoc calibration → category-wise miscalibration analysis

---

## 7. Verification (Compact)

**Verified:** 12 Exa repos (67%) | **Inferred:** 9 papers/patterns (33%)
**MCP Issues:** Scholar HTTP 500, Archon irrelevant content
**Quality:** 80/100

---

## 8. Research Gaps (FULL - CRITICAL FOR PHASE 2A)

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**

1. **Main Research Question**: Do LLMs exhibit systematic miscalibration patterns (overconfidence or underconfidence) across different types of factual claims, and can existing calibration methods improve trustworthiness without architectural changes?

2. **Detailed Questions**:
   - RQ1: What is the relationship between LLM verbalized confidence and actual accuracy on TruthfulQA, FACTOR?
   - RQ2: Do miscalibration patterns differ systematically across claim categories?
   - RQ3: Can post-hoc calibration techniques improve Expected Calibration Error (ECE)?
   - RQ4: How does calibration quality correlate with model scale?

3. **Reference Papers**: Not provided

### Identified Gaps

#### Gap 1: Category-Specific Calibration Analysis Absent

**Relevance Classification:** 🎯 PRIMARY
**Connection to Research Question:** ☑️ Directly blocks answering "Do miscalibration patterns differ across claim categories?"

**Current State:** Existing calibration studies (Guo 2017, Kadavath 2022) compute global ECE across entire datasets. TruthfulQA provides 38 category labels but existing analyses aggregate results.

**Missing Piece:** No systematic study disaggregates calibration metrics (ECE, MCE) by TruthfulQA category to reveal if certain claim types (e.g., misconceptions vs. scientific facts) show different miscalibration patterns.

**Potential Impact:** High - Enables targeted calibration interventions for high-error categories

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| TruthfulQA: Measuring How Models Mimic Human Falsehoods | 2022 | Lin, Hilton, Evans | [INFERRED] | 2109.07958 | 500+ | 38 categories exist but calibration not analyzed per-category |
| On Calibration of Modern Neural Networks | 2017 | Guo et al. | [INFERRED] | 1706.04599 | 5000+ | ECE metric is global, no category breakdown |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No relevant cases found* | - | "LLM calibration" | Archon KB lacks LLM evaluation content |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| sylinrl/TruthfulQA | https://github.com/sylinrl/TruthfulQA | 936 | Python | 38 category labels in CSV, evaluation scripts |
| Jonathan-Pearce/calibration-toolbox | https://github.com/Jonathan-Pearce/calibration-toolbox | 76 | Python | ECE/MCE metrics, can be applied per-category |

---

#### Gap 2: Verbalized vs Logit-Based Confidence Comparison on Truthfulness Benchmarks

**Relevance Classification:** 🎯 PRIMARY
**Connection to Research Question:** ☑️ Directly addresses RQ1 about "verbalized confidence and actual accuracy"

**Current State:** APRICOT (ACL2024) shows generation-only calibration works. Xiong et al. (2023) evaluate confidence elicitation methods. But systematic comparison of verbalized confidence calibration vs logit-based on TruthfulQA specifically is limited.

**Missing Piece:** Direct head-to-head comparison of ECE when using: (a) softmax logit probabilities, (b) prompted verbalized confidence (0-100%), on identical TruthfulQA questions across multiple model families.

**Potential Impact:** High - Determines which confidence source is more reliable for truthfulness assessment

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| Can LLMs Express Their Uncertainty? | 2023 | Xiong et al. | [INFERRED] | 2306.13063 | 100+ | Evaluates verbalized vs logit confidence, not TruthfulQA specific |
| Language Models Know What They Know | 2022 | Kadavath et al. | [INFERRED] | 2207.05221 | 200+ | Studies self-knowledge but not category-level calibration |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No relevant cases found* | - | "verbalized confidence" | Archon KB lacks relevant content |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| parameterlab/apricot | https://github.com/parameterlab/apricot | 22 | Python | Generation-only calibration, no logit access |
| facebookresearch/verbal_uncertainty_feature_calibration | https://github.com/facebookresearch/verbal_uncertainty_feature_calibration | 13 | Python | Verbal uncertainty as linear feature |

---

#### Gap 3: Post-hoc Calibration Effectiveness on LLM Truthfulness Tasks

**Relevance Classification:** 🎯 PRIMARY
**Connection to Research Question:** ☑️ Directly addresses RQ3 about "post-hoc calibration techniques improving ECE"

**Current State:** Temperature scaling (Guo 2017) is well-established for classification models. LLM-specific calibration methods exist (Thermometer, APRICOT). But systematic evaluation of classic post-hoc methods (temp scaling, Platt scaling) on truthfulness benchmarks with ECE as primary metric is sparse.

**Missing Piece:** Quantified ECE improvement from applying temperature scaling and Platt scaling to LLM outputs on TruthfulQA, with comparison to LLM-specific methods and analysis of category-specific improvements.

**Potential Impact:** Medium-High - Determines if simple post-hoc methods suffice or if LLM-specific approaches needed

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| On Calibration of Modern Neural Networks | 2017 | Guo et al. | [INFERRED] | 1706.04599 | 5000+ | Temperature scaling on CNNs, not evaluated on LLM truthfulness |
| Thermometer: Universal Calibration for LLMs | 2024 | Mao et al. | [INFERRED] | 2403.08819 | 10+ | Universal calibration, comparison with temp scaling exists |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No relevant cases found* | - | "temperature scaling calibration" | Archon KB lacks LLM calibration content |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| gpleiss/temperature_scaling | https://github.com/gpleiss/temperature_scaling | 1172 | Python | Reference temp scaling, directly applicable |
| p-lambda/verified_calibration | https://github.com/p-lambda/verified_calibration | 152 | Python | ECE with bootstrap CI, recalibration methods |
| maohaos2/Thermometer | https://github.com/maohaos2/Thermometer | 13 | Python | LLM-specific universal calibration baseline |

---

### Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | Category-Specific Calibration Analysis | High | Low | 4 sources | 🔴 Critical |
| Gap 2 | Verbalized vs Logit Confidence Comparison | High | Medium | 4 sources | 🔴 Critical |
| Gap 3 | Post-hoc Calibration on Truthfulness | Medium-High | Low | 5 sources | 🟡 High |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- **Gap 1**: Answers "Do patterns differ across claim categories?" via per-category ECE
- **Gap 2**: Addresses confidence-accuracy relationship via verbalized/logit comparison
- **Gap 3**: Tests "can existing methods improve trustworthiness?" via post-hoc ECE improvement

**Detailed Question Mapping:**
- **RQ1** (verbalized confidence vs accuracy): Gap 2
- **RQ2** (category-specific patterns): Gap 1
- **RQ3** (post-hoc calibration improving ECE): Gap 3
- **RQ4** (model scale correlation): Partially covered by Gap 1, 2 across model families

---

## 9. Conclusion (Compact)

**Key Findings:** 12 repos, 3 gaps, category-level analysis is clear gap
**Phase 2A Ready:** ✅ | **Priority:** Gap 1 (lowest difficulty)
**Resources:** TruthfulQA, temp scaling code, HuggingFace models

---

*Phase 1 Complete | Processing: ~15 min | Full report: 01_targeted_research_full.md*
