---
hypothesis_id: h-e1
generated_by: Phase 2C step-01 JIT generation
source: 02b_verification_plan.md
date: 2026-05-13
---

# Per-Hypothesis Context: H-E1

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Title:** Contamination Geometry Decomposition Exists
- **Gate:** MUST_WORK
- **Prerequisites:** None (root hypothesis)
- **Version:** 1

### Statement

Under contamination detection for MMLU/HellaSwag/GSM8K against The Pile/C4/RedPajama using open-weight models, if corpus-side geometric signals (max 13-gram overlap count, SBERT cosine similarity) are used to define geometry strata, then n-gram detectors will exhibit recall ≥ 0.80 in the lexical stratum and ≤ 0.40 in the semantic stratum, and Min-K%++ F1 variance across three corpora will be ≥ 0.15, because detector families operate on orthogonal signal types that align with different corpus overlap regimes.

### Rationale

This is the foundational existence claim: if geometry strata do not separate detector performance, the entire routing hypothesis collapses. Establishing that n-gram detectors strongly outperform in lexical regimes while failing in semantic regimes directly validates the core structural premise.

## Success Criteria

- **Primary:** N-gram recall ≥ 0.80 in lexical stratum AND ≤ 0.40 in semantic stratum
- **Secondary:** Min-K%++ F1 variance ≥ 0.15 across The Pile/C4/RedPajama for MMLU or HellaSwag
- **Tertiary:** Indeterminacy rate in [10%, 50%]

## Failure Response

IF fails (n-gram recall ≥ 0.60 in semantic stratum OR Min-K%++ variance < 0.10): STOP — H-GeomRoute-v1 does not hold; indeterminate zone finding still reportable as negative result

## Experimental Setup

### Dataset

- **Name:** MMLU + HellaSwag + GSM8K (benchmark test splits) × The Pile + C4 + RedPajama (pretraining corpora)
- **Type:** standard (real public benchmark datasets + real pretraining corpora)
- **Source:** HuggingFace datasets hub; EleutherAI/pile; allenai/c4; togethercomputer/RedPajama-Data-1T
- **Path:** Public — downloadable via HuggingFace hub
- **Hypothesis Fit:** Covers three reasoning modalities (knowledge, commonsense, math) × three corpus families (curated/web/deduplicated). 9 benchmark-corpus pairs; ~25K total benchmark items tractable (~48 GPU-hours).

### Models

- **Name:** Llama-2-7B, Mistral-7B, Pythia-7B (open-weight LLM, decoder-only)
- **Type:** Open-weight LLM (decoder-only, autoregressive)
- **Source:** HuggingFace model hub (all publicly available)
- **Hypothesis Fit:** White-box access required for per-token log probabilities (Min-K%++, DC-PDD). Three models provide cross-model robustness check. Pythia trained on The Pile provides known-corpus case.

### Detector Methods

5 detector families:
1. N-gram (EleutherAI/lm-evaluation-harness 13-gram decontamination pipeline)
2. Embedding similarity (ntunlp/LLMSanitize FAISS-based)
3. Min-K%++ (zjysteven/mink-plus-plus — ICLR'25 Spotlight)
4. DC-PDD (Zhang et al. 2024 [2409.14781])
5. ConStat/ConTAM (Singh et al. 2024)

## Verification Protocol (5 steps)

1. Build 13-gram inverted index (EleutherAI pipeline) and FAISS SBERT embedding index for The Pile, C4, RedPajama.
2. Compute geometry features (max 13-gram count, max SBERT cosine) for all ~25K benchmark items across 3 corpora; define strata using top-quartile thresholds.
3. Apply all 5 detector families to Approach A (known inclusion audit) and Approach B (simulated leakage, 3 injection regimes) labeled items.
4. Compute per-stratum recall/F1 with bootstrap 95% CIs (N=10,000); compute indeterminacy rate; compute Min-K%++ F1 variance across 3 corpora.
5. Generate 2D contamination phase diagram (13-gram × cosine) colored by dominant detector family; report indeterminacy rate as primary structural outcome.

## Dependencies

- **Source:** Phase 2A Section 1.6 Prediction P2; Section 5 SH1_existence
- **Required by:** H-M1, H-M2, H-M3, H-M4
