# Targeted Research Report (Compact): Uncertainty Estimation for Hallucination Detection in LLMs

**Date:** 2026-08-24
**Phase:** 1 - Targeted Research Gathering
**Researcher:** Anonymous

---

## Executive Summary

Investigated UQ methods for LLM hallucination detection. Collected 26 verified sources: 11 papers (Scholar), 13 GitHub repos (Exa), 2 KB entries (Archon).

**Key Finding:** Field evolved from multi-sample semantic entropy (Nature 2024) to efficient single-pass methods (SEPs). Toolkits available (UQLM 1183 stars, LM-Polygraph 480 stars).

**Phase 2A Readiness:** HIGH

---

## Research Question

How can we leverage existing uncertainty estimation techniques (ensemble disagreement, token-level entropy, semantic consistency) to detect hallucinations in LLM outputs, and evaluate effectiveness using established QA benchmarks?

---

## Key Papers (Semantic Scholar)

| Paper | Year | Citations | Key Contribution |
|-------|------|-----------|------------------|
| Detecting hallucinations using semantic entropy (Nature) | 2024 | 1615 | Semantic entropy - meaning-level uncertainty |
| Semantic Entropy Probes | 2024 | 247 | Single-pass efficiency via hidden state probes |
| Token-Level UQ Fact-Checking (CCP) | 2024 | 186 | Fine-grained token-level fact-checking |
| Hallucination Survey | 2023 | 3590 | Comprehensive taxonomy and benchmarks |
| Conformal Prediction for NLP Survey | 2024 | 70 | CP framework with coverage guarantees |
| Pre-trained UQ Heads | 2025 | 29 | SOTA claim-level detection |
| UQLM Framework | 2025 | 22 | Ensemble black/white-box scorers |

---

## Key Implementations (Exa)

| Repository | Stars | Key Feature |
|------------|-------|-------------|
| cvs-health/uqlm | 1183 | Comprehensive UQ toolkit |
| IINemo/lm-polygraph | 480 | UE method battery |
| jlko/semantic_uncertainty | 411 | Nature paper code |
| sylinrl/TruthfulQA | 927 | Benchmark (817 questions) |
| OATML/semantic-entropy-probes | 65 | Single-pass SEPs |
| XavierZhang2002/ICR_Probe | 18 | Cross-layer dynamics (ACL 2025) |

---

## Research Gaps

### Gap 1: Single-Pass vs Multi-Sample Parity (P1)
- **Current:** SE requires 5-10 samples; SEPs claim near-parity with single-pass
- **Missing:** Systematic comparison across LLM families on standard benchmarks
- **Impact:** Enables practical deployment

### Gap 2: Token vs Sequence Uncertainty Correlation (P2)
- **Current:** Token and sequence entropy used independently
- **Missing:** Which token positions most predictive of sequence correctness?
- **Impact:** Focused computation on critical tokens

### Gap 3: Probe Cross-Model Generalization (P3)
- **Current:** Probes trained on specific models
- **Missing:** Transfer across Llama/Mistral/Qwen families
- **Impact:** Reusable detectors without per-model training

---

## Preliminary Answer

Yes, UQ techniques detect hallucinations effectively:
- Token entropy: AUROC ~0.52-0.65 (baseline)
- Semantic entropy: AUROC ~0.75-0.90 (SOTA, expensive)
- SEPs: Competitive AUROC, 5-20x speedup
- Ensembles (UQLM): Best overall performance

**Trade-off:** Multi-sample for accuracy, single-pass for deployment.

---

## Benchmarks Available

- **TruthfulQA:** 817 questions across 38 categories
- **TriviaQA:** ~11K questions with answer aliases
- **HaluEval:** Hallucination evaluation benchmark

All have ground truth - no human evaluation needed.

---

## Next Steps

1. **Phase 2A:** Generate hypotheses from Gap 1 (recommended: single-pass efficiency)
2. **Phase 2B:** Design verification protocol using TruthfulQA
3. **Phase 2C:** Create experiment spec with AUROC threshold (>0.75 gate)

---

*Phase: 1 - Targeted Research Gathering*
*Full report: 01_targeted_research_full.md*
