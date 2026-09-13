# Targeted Research Report (Compact - Phase 2A Input)

**Research Question:** Can weight space learning methods effectively predict model properties or enable model operations using only weight tensors?
**Date:** 2026-08-12

---

## 1. Research Questions

**Primary:** Can weight space learning methods (embeddings, hypernetworks, equivariant architectures) effectively predict model properties or enable model operations using only weight tensors, validated on existing model zoo benchmarks?

**Detailed:**
1. Can weight embeddings predict accuracy/robustness without inference?
2. Do permutation-equivariant architectures outperform MLP baselines?
3. Can weight features predict model merging success?
4. Do weight representations transfer across architectures?
5. Can weights alone detect backdoored models?

---

## 2. Key Papers (Semantic Scholar)

| Title | Year | arXiv | Citations | Key Insight |
|-------|------|-------|-----------|-------------|
| WSL Survey | 2026 | 2603.10090 | 13 | Unified taxonomy |
| Hyper-Representations (Generative) | 2022 | 2209.14733 | 74 | Layer-wise loss normalization |
| Self-Supervised on NN Weights | 2021 | 2110.15288 | 64 | Foundation for property prediction |
| Model Zoos Dataset | 2022 | 2209.14764 | 45 | 50K model benchmark |
| NFN | 2023 | 2302.14040 | - | Permutation equivariant layers |

---

## 3. Key Implementations (Exa)

| Repo | Stars | Key Feature |
|------|-------|-------------|
| AllanYangZhou/nfn | 93 | Permutation equivariant layers (pip install) |
| ModelZoos/ModelZooDataset | 60 | 50K models benchmark |
| HSG-AIML/SANE | 33 | Scalable WSL (ICML 2024) |

---

## 4. Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: Permutation Equivariance vs Non-Equivariant Baselines

**Classification:** PRIMARY | **Addresses:** Q2
**Current State:** NFN provides equivariant layers but systematic comparison against matched-capacity non-equivariant baselines limited.
**Missing:** Rigorous ablation: NFN vs MLP-Matched vs NFN-Scrambled with statistical tests.
**Impact:** HIGH

| Paper | arXiv | Key Insight |
|-------|-------|-------------|
| NFN | 2302.14040 | Introduces NFN but focuses on generation |
| Hyper-Rep | 2110.15288 | Uses attention, not equivariant |

| Repo | URL | Key Feature |
|------|-----|-------------|
| nfn | github.com/AllanYangZhou/nfn | NPLinear, HNPPool |

---

### Gap 2: Simple Baselines for Weight-to-Property Prediction

**Classification:** PRIMARY | **Addresses:** Q1
**Current State:** Complex methods exist but unclear if simple layer statistics achieve comparable R².
**Missing:** Baseline study: what R² do simple stats (mean, std, norm) achieve on Model Zoo?
**Impact:** HIGH

| Paper | arXiv | Key Insight |
|-------|-------|-------------|
| Model Zoos | 2209.14764 | 50K models but no simple baselines |
| Phase Transitions | 2504.18072 | Loss landscape metrics |

| Repo | URL | Key Feature |
|------|-----|-------------|
| ModelZooDataset | github.com/ModelZoos/ModelZooDataset | 50K models with labels |

---

### Gap 3: Cross-Architecture Weight Representation Transfer

**Classification:** SECONDARY | **Addresses:** Q4
**Current State:** Most methods require homogeneous zoos. MultiZoo-SANE limited to similar families.
**Missing:** Transfer study: CNN representations predicting MLP properties.
**Impact:** MEDIUM

| Paper | arXiv | Key Insight |
|-------|-------|-------------|
| MultiZoo Impact | 2504.10141 | Heterogeneous but same family |
| WSL Survey | 2603.10090 | Identifies as open problem |

---

## 5. Gap Priority Matrix

| Gap | Impact | Difficulty | Priority |
|-----|--------|------------|----------|
| Gap 1 (Equivariance ablation) | HIGH | Medium | Critical |
| Gap 2 (Simple baselines) | HIGH | Low | Critical |
| Gap 3 (Cross-architecture) | MEDIUM | High | Secondary |

---

## 6. Phase 2A Readiness

| Criterion | Status |
|-----------|--------|
| Research question | Ready |
| Gaps identified | 3 (2 critical) |
| Benchmarks | ModelZoo 50K+ |
| Implementations | NFN (pip), SANE |

**Next:** Phase 2A-Dialogue for hypothesis generation from Gap 1 and Gap 2.

---

*Compact version for Phase 2A input. Full report: 01_targeted_research_full.md*
