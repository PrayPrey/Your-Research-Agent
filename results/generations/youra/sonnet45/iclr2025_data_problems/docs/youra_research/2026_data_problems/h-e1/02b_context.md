# Phase 2B Context: H-E1 — Registry Construction Feasibility

**Generated:** 2026-03-17 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None (foundation hypothesis)

---

## Hypothesis Statement

Under the Open LLM Leaderboard v1 snapshot, if model cards are publicly accessible on HuggingFace for a sufficient fraction of evaluated models, then a dataset of ≥200 models with non-missing binary curation documentation features, ≥4/6 benchmark scores, and recoverable parameter count can be assembled, because major open-weight model families (LLaMA, Falcon, Mistral, Pythia) consistently publish detailed model cards with the required feature information.

---

## Variables

- **Independent:** Presence/absence of HuggingFace model card with ≥1 documented curation feature
- **Dependent:** Number of models with complete feature set (n_complete); doc_score distribution (0-4)
- **Controlled:** Benchmark score availability threshold (≥4/6 benchmarks)

---

## Success Criteria

- **Primary:** n_analyzable ≥ 200 models with complete feature set
- **Secondary:** doc_score variance > 0 in at least 3 of 4 features; n with training tokens D recoverable ≥ 100

---

## Failure Response

- IF n < 200: PIVOT — expand to v1+v2 snapshot or relax to ≥3/6 benchmarks; document as limitation
- IF doc_score uniformly 0 or 4: EXPLORE — manual review of feature extraction rules; consider annotation revision

---

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Open LLM Leaderboard v1 Snapshot + HuggingFace Model Cards (standard) | Natural observational corpus with ~3000+ model evaluations; Thrush et al. (2024) used same source for perplexity-benchmark correlations; static v1 snapshot eliminates temporal confounds |
| **Model** | N/A (OLS regression — statsmodels/scipy/pandas) | Standard OLS regression sufficient for correlational observational study; no deep learning infrastructure required |

**Dataset Details:**
- Source: HuggingFace Datasets API (`open-llm-leaderboard/results`)
- Type: standard (public API)
- Path: Public — downloadable via HuggingFace Hub API (`huggingface_hub`) and `datasets` library

**Model Details:**
- Type: OLS regression / partial correlation
- Source: statsmodels, scipy, pandas (Python)
- No GPU required — pure statistical analysis

---

## Verification Protocol

1. Download Open LLM Leaderboard v1 static snapshot via HuggingFace Datasets API or direct scrape.
2. For each model, attempt model card retrieval via HuggingFace Hub API and extract 4 binary features using pre-registered keyword rules.
3. Filter to models with ≥4/6 benchmark scores AND recoverable parameter count (N); record dropout rate.
4. Compute doc_score distribution and verify non-trivial variance (not >90% at 0 or >90% at 4).
5. Report final n_analyzable; confirm ≥200 with all required fields.

---

## Gate Condition

**Type:** MUST_WORK
**Meaning:** If H-E1 fails, the entire pipeline STOPS — all mechanism hypotheses (H-M1, H-M2, H-M3) require an assembled registry to proceed.

---

## Dependencies

- None — This is the foundation hypothesis; no prerequisites.

---

## Source

Phase 2A Section 5 (sh1_existence), Prediction P1 data requirements; 02b_verification_plan.md Section 2.2 H-E1.
