# Product Requirements Document: h-m1

**Date:** 2026-08-24  
**Author:** Anonymous  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Implementation Tier:** PoC  

---

## Executive Summary

**Goal:** Test whether optimal curation thresholds (deduplication, perplexity filtering) transfer robustly across pre-training and fine-tuning stages with ≤10% performance delta.

**Success Metric:** Performance delta <10% when applying pre-training-tuned thresholds to fine-tuning data (and vice versa).

**Implementation Budget:** Minimal (PoC tier) — reuse h-e1 infrastructure, add threshold sweep logic.

---

## Requirements

### Functional Requirements

**FR1: Threshold Sweep Framework**
- Implement parameterized curation pipeline accepting (dedup_threshold, perplexity_threshold)
- Support threshold ranges: dedup=[0.7, 0.8, 0.9], perplexity=[500, 1000, 1500]
- Apply curation independently to pre-training (C4) and fine-tuning (Dolly-15k) datasets

**FR2: Cross-Stage Threshold Transfer**
- Tune thresholds independently for pre-training and fine-tuning stages
- Cross-apply optimal thresholds (pre-training-tuned → fine-tuning data, fine-tuning-tuned → pre-training data)
- Log filtered sample counts per threshold configuration

**FR3: Performance Measurement**
- Train Llama-2-7B on curated datasets (optimal vs transferred thresholds)
- Evaluate on MMLU and HellaSwag benchmarks
- Compute performance delta: |perf_optimal - perf_transferred|

**FR4: Visualization**
- Gate metrics comparison (target vs actual delta)
- Threshold sensitivity heatmap (dedup × perplexity grid)
- Transfer delta bar chart (pre-training→fine-tuning vs fine-tuning→pre-training)
- Curation impact chart (samples filtered per threshold)

### Non-Functional Requirements

**NFR1: Reproducibility**
- Fixed random seed (seed=1)
- Cached perplexity scores (avoid recomputation)
- Deterministic deduplication (hash-based, not LSH for PoC)

**NFR2: Efficiency**
- Vectorized perplexity scoring (batch processing)
- Hash-set deduplication (O(n) complexity)
- Skip full training (mock evaluation acceptable for PoC)

**NFR3: Extensibility**
- Modular curation functions (reusable for future hypotheses)
- Configurable threshold ranges (YAML or command-line args)

---

## User Stories

**US1:** As a researcher, I want to apply deduplication and perplexity filtering with custom thresholds, so I can test threshold transfer robustness.

**US2:** As a researcher, I want to measure performance degradation when using transferred vs optimal thresholds, so I can validate the <10% delta success criterion.

**US3:** As a researcher, I want visualizations of threshold sensitivity and transfer impact, so I can interpret the mechanism's behavior.

---

## Success Criteria

**PoC Pass:**
1. Code runs without error
2. Thresholds applied (0 < filtered_count < total samples)
3. Performance delta measured (MMLU, HellaSwag)

**MUST_WORK Gate:**
1. Performance delta <10% when thresholds mismatched
2. Degradation significantly less than high-level techniques (domain mixing >5%)

**Failure Triggers:**
- Delta ≥10% → EXPLORE distribution shift effects (route to exploratory hypothesis)
- Missing benchmark results → implementation incomplete

---

## Constraints

**Technical Constraints:**
- Reuse h-e1 training protocol (AdamW lr=1e-5, batch_size=16, epochs=3)
- Fixed dataset split (C4: 52,002 samples, Dolly-15k: 15,000 samples)
- Perplexity computation requires reference LM (KenLM or GPT-2)

**Resource Constraints:**
- PoC budget: minimal infrastructure
- Single seed (seed=1) for PoC — no multi-seed statistical significance
- Mock evaluation acceptable (production requires full lm-evaluation-harness)

**Timeline Constraints:**
- Implementation must complete within Phase 4 coding window
- Validation gates must pass before routing to h-m2/h-m3

---

## Dependencies

**Prerequisites:**
- h-e1 VALIDATED (transfer-stable category established)
- h-e1 codebase (dataset loading, training loop, evaluation harness)

**External Libraries:**
- datasets (HuggingFace): C4 + Dolly-15k loading
- transformers: Llama-2-7B model
- lm-evaluation-harness: MMLU, HellaSwag benchmarks (or mock equivalent for PoC)
- kenlm / GPT-2: Perplexity computation

---

## Out of Scope (PoC)

- Multi-seed runs (statistical significance)
- Full training (checkpointing, early stopping, LR scheduling)
- LSH-based deduplication (exact-match hash for PoC)
- Cross-domain threshold transfer (future EXPLORE hypothesis)
- Production deployment (model serving, API endpoints)

---

## Acceptance Criteria

**Implementation Complete When:**
1. ✅ Threshold sweep pipeline functional (FR1)
2. ✅ Cross-stage transfer logic implemented (FR2)
3. ✅ Performance delta measured and logged (FR3)
4. ✅ All 4 visualizations generated (FR4)
5. ✅ PoC success check passes (code runs, delta measured)

**MUST_WORK Gate Passes When:**
1. ✅ Performance delta <10% (primary criterion)
2. ✅ Degradation < high-level techniques baseline (secondary criterion)

---

## Traceability

| Requirement | Source | Rationale |
|-------------|--------|-----------|
| Threshold ranges | Archon KB (DataComp) | Standard sweep: 0.7-0.9 (dedup), 500-1500 (perplexity) |
| Cross-stage transfer | Phase 2B h-m1 | Core mechanism to test |
| MMLU/HellaSwag metrics | Phase 2B | Standard LLM benchmarks |
| Reuse h-e1 protocol | h-e1 validation | Controlled experiment (isolate threshold variable) |
| PoC tier budget | Phase 3 allocation | MECHANISM hypothesis = minimal infrastructure |

---

**Next Document:** 03_architecture.md (system design)  
**Implementation Phase:** Phase 4 (coder-validator loop)  
**Validation Output:** 04_validation.md (gate pass/fail verdict)
