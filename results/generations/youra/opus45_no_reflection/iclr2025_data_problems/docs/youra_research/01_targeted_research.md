# Targeted Research Report (Compact - Phase 2A Input)

**Research Question:** What is the trade-off between computational cost and attribution accuracy when applying gradient-based influence estimation methods to foundation models of varying scales?

**Date:** 2026-08-18 | **Phase:** 1 - Targeted Research | **Sources:** 36 (94.4% verified)

---

## Research Questions

**Primary:** Trade-off between computational cost and attribution accuracy for gradient-based influence estimation in FMs.

**Detailed:**
1. How does accuracy degrade with increased approximation?
2. Which FM architectures (encoder/decoder/encoder-decoder) have best trade-offs?
3. Can layer-wise attribution reduce compute 10x+ while maintaining accuracy?
4. How do benchmarks correlate across approximation settings?

---

## Key Sources (Compact)

### Academic Papers (Top 10)

| Title | Year | SS ID | arXiv | Citations | Key Insight |
|-------|------|-------|-------|-----------|-------------|
| Understanding Black-box Predictions via Influence Functions | 2017 | 08ad8fad21f6ec4cda4d56be1ca5e146b7c913a1 | 1703.04730 | 3752 | Foundational IHVP method |
| TracIn | 2020 | c94e49617f569204f989643e5462691b9b3a482b | 2002.08484 | 716 | First-order checkpoint approximation |
| Studying LLM Generalization with Influence Functions | 2023 | 04a96b66705858c988edfcb73191c1da7d54abfb | 2308.03296 | 350 | EK-FAC scales to 52B |
| TRAK | 2023 | 4f2ae5fa2dc74af9c36ee57b359a4b3241006a92 | 2303.14186 | 310 | Random projection attribution |
| Datamodels | 2022 | 2a7a6648563e6a09e6fea6dd96e68e0563216dcb | 2202.00622 | 216 | LOO benchmark methodology |
| Rethinking IF in Over-parameterized Regime | 2021 | ee2c7ae4f8c819eaba6427cb1beaccce6c154b40 | 2112.08297 | 34 | NTK-based bounds |
| LoRIF | 2026 | f8c4e28937666c556d8c1658dbb48fcdd2a552dc | 2601.21929 | 1 | 20x storage reduction, 70B scale |
| Bayesian Influence Functions | 2025 | 37ffadc006106a186b3de92d9d004493b638ba2c | 2509.26544 | 10 | Hessian-free MCMC |
| Generalized Group Data Attribution | 2024 | 6b7e8bcd5e60f037492d7731dc827200c6e566d2 | 2410.09940 | 5 | 10-50x speedup via grouping |
| Data Cleansing with Storage-efficient IF | 2021 | 0e69de37323d305abb2f689e64dc3896aad25b0a | 2103.11807 | 5 | 1/1563x cache reduction |

### Implementations (Top 5)

| Repo | URL | Stars | Key Feature |
|------|-----|-------|-------------|
| MadryLab/trak | https://github.com/MadryLab/trak | 243 | CUDA-optimized TRAK |
| pomonam/kronfluence | https://github.com/pomonam/kronfluence | 198 | EK-FAC for LLMs |
| frederick0329/TracIn | https://github.com/frederick0329/TracIn | 242 | Official TracIn |
| nimarb/pytorch_influence_functions | https://github.com/nimarb/pytorch_influence_functions | 345 | Classic IF baseline |
| pomonam/simple-influence | https://github.com/pomonam/simple-influence | 6 | Multi-method comparison |

---

## Research Evolution

```
Koh & Liang (2017) IHVP → TracIn (2020) First-order → EK-FAC/TRAK (2023) Scaling → LoRIF/BIF (2025-26) Hessian-free
```

**Efficiency Strategies:** Random projection (TRAK, LoRIF) | Curvature approximation (EK-FAC) | First-order (TracIn)

---

## Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: Systematic Architecture Comparison for Data Attribution

**Relevance:** 🎯 PRIMARY - Blocks answering research_question

**Connection:**
- ☑️ Addresses RQ: No systematic study compares trade-offs across encoder/decoder/encoder-decoder
- ☑️ Addresses DQ #2: "Which FM architectures show most favorable trade-offs?"

**Current State:** EK-FAC evaluates decoder-only (52B). TRAK evaluates BERT and CLIP separately. No unified comparison.

**Missing Piece:** Head-to-head comparison of same method across encoder-only (BERT), decoder-only (GPT), encoder-decoder (T5) at matched parameter counts.

**Impact:** HIGH

**Evidence:**

| Paper | SS ID | arXiv | Insight |
|-------|-------|-------|---------|
| Grosse et al. 2023 | 04a96b66705858c988edfcb73191c1da7d54abfb | 2308.03296 | Only decoder-only |
| TRAK 2023 | 4f2ae5fa2dc74af9c36ee57b359a4b3241006a92 | 2303.14186 | BERT/CLIP separate |

| Repo | URL | Stars | Feature |
|------|-----|-------|---------|
| MadryLab/trak | https://github.com/MadryLab/trak | 243 | Multi-architecture support |
| pomonam/kronfluence | https://github.com/pomonam/kronfluence | 198 | EK-FAC various architectures |

---

### Gap 2: Approximation Level Degradation Curves

**Relevance:** 🎯 PRIMARY - Blocks answering research_question

**Connection:**
- ☑️ Addresses RQ: Core trade-off requires quantified degradation curves
- ☑️ Addresses DQ #1: "How does accuracy degrade as approximation levels increase?"
- ☑️ Extends TracIn limitation: Mentions approximations but no systematic quantification

**Current State:** Papers report final accuracy at one approximation level. No systematic sweep showing curve shape.

**Missing Piece:** Empirical curves of attribution accuracy (LDS/LOO) vs. approximation parameters (projection dim, checkpoint count, Hessian rank).

**Impact:** HIGH

**Evidence:**

| Paper | SS ID | arXiv | Insight |
|-------|-------|-------|---------|
| LoRIF 2026 | f8c4e28937666c556d8c1658dbb48fcdd2a552dc | 2601.21929 | Storage vs quality, not full curve |
| Zhang 2021 | ee2c7ae4f8c819eaba6427cb1beaccce6c154b40 | 2112.08297 | Theoretical bounds only |
| TracIn 2020 | c94e49617f569204f989643e5462691b9b3a482b | 2002.08484 | Notes trade-off without quantifying |

| Repo | URL | Stars | Feature |
|------|-----|-------|---------|
| pomonam/simple-influence | https://github.com/pomonam/simple-influence | 6 | Multi-method ablation framework |
| frederick0329/TracIn | https://github.com/frederick0329/TracIn | 242 | Variable checkpoint count |

---

### Gap 3: Layer-Wise Attribution Accuracy Analysis

**Relevance:** 🎯 PRIMARY - Blocks answering research_question

**Connection:**
- ☑️ Addresses RQ: Layer selection is key efficiency lever
- ☑️ Addresses DQ #3: "Can layer-wise attribution reduce compute 10x+?"

**Current State:** TracIn mentions "cherry-picking layers." TRAK allows layer selection. No systematic layer importance analysis.

**Missing Piece:** Layer-by-layer attribution importance: (1) which layers contribute most, (2) minimum subset for 90% accuracy, (3) patterns across architectures.

**Impact:** HIGH

**Evidence:**

| Paper | SS ID | arXiv | Insight |
|-------|-------|-------|---------|
| TracIn 2020 | c94e49617f569204f989643e5462691b9b3a482b | 2002.08484 | Mentions layer selection, no study |
| Data Cleansing IF 2021 | 0e69de37323d305abb2f689e64dc3896aad25b0a | 2103.11807 | Uses final params only |

| Repo | URL | Stars | Feature |
|------|-----|-------|---------|
| MadryLab/trak | https://github.com/MadryLab/trak | 243 | Layer selection via projection targets |

---

## Gap Priority Matrix

| Gap | Title | Relevance | DQ | Impact | Priority |
|-----|-------|-----------|-----|--------|----------|
| 1 | Architecture Comparison | PRIMARY | #2 | High | Critical |
| 2 | Approximation Degradation Curves | PRIMARY | #1 | High | Critical |
| 3 | Layer-Wise Attribution Analysis | PRIMARY | #3 | High | Critical |

---

## Phase 2A Readiness

| Requirement | Status |
|-------------|--------|
| Research question | ✅ |
| Literature review | ✅ 18 papers |
| Implementations | ✅ 8 repos |
| Gaps identified | ✅ 3 PRIMARY |
| Evidence tables | ✅ |

**Ready for Phase 2A hypothesis generation.**

---

*Phase 1 Complete | Full report: 01_targeted_research_full.md*
