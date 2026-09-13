# Targeted Research Report (Compact): UQ for LLM Hallucination Detection

**Date:** 2026-08-18 | **Phase:** 1 | **Researcher:** Anonymous

---

## Research Question

How can token-level entropy and semantic consistency measures be combined to create a computationally efficient uncertainty quantification method for LLMs that correlates with factual accuracy on existing QA benchmarks?

---

## Executive Summary

- **43+ verified sources** (25+ papers, 12 repos, 3 tutorials)
- **Primary Gap:** Efficient combination of token-level entropy + semantic consistency
- **Key Insight:** Trade-off exists between accuracy (multi-sample SE, 5-10x overhead) and efficiency (single-pass token entropy). SEPs show this gap is closable.
- **Phase 2A Readiness:** HIGH

---

## Key Papers

| Paper | Year | Citations | Key Contribution |
|-------|------|-----------|------------------|
| Generating with Confidence (Lin) | 2023 | 330 | Black-box semantic dispersion |
| Semantic Entropy Probes (Kossen) | 2024 | 242 | Single-pass SE from hidden states |
| Fact-Checking via Token UQ (Fadeeva) | 2024 | 185 | CCP token-level method |
| LM-Polygraph (Vashurin) | 2024 | 121 | UQ benchmark toolkit |
| UQ Survey (Liu) | 2025 | 130 | Comprehensive taxonomy |

---

## Key Repositories

| Repo | Stars | Purpose |
|------|-------|---------|
| cvs-health/uqlm | 1183 | Production UQ toolkit |
| IINemo/lm-polygraph | 480 | UE method battery |
| jlko/semantic_uncertainty | 411 | SE implementation (Nature) |
| OATML/semantic-entropy-probes | 65 | Single-pass SE probes |

---

## Research Gaps

### Gap 1 (P1): Efficient Token+Semantic Combination
- **Current:** Token methods fast but less accurate; semantic methods accurate but 5-10x overhead
- **Missing:** Principled combination avoiding multi-sample generation
- **Impact:** Real-time hallucination detection with high accuracy

### Gap 2 (P2): Entropy-Accuracy Correlation
- **Missing:** Systematic study of which entropy features predict factual correctness

### Gap 3 (P3): Cross-Architecture Generalization
- **Missing:** Transfer of UQ methods across LLM families

---

## Phase 2A Hypothesis Directions

1. **Single-pass probing:** Train probe on hidden states + token entropy to predict SE
2. **Adaptive sampling:** Use token entropy as gate for multi-sample check
3. **Weighted ensemble:** Combine token + semantic signals with learned calibration

---

## Benchmarks Available

- TriviaQA, TruthfulQA, HaluEval, Natural Questions, FEVER

---

*See 01_targeted_research_full.md for complete evidence and citations*
