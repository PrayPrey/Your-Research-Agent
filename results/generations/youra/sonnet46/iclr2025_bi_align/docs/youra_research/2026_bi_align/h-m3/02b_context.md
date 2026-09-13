# Phase 2B Context: h-m3

**Generated:** 2026-03-15 (JIT by Phase 2C step-01)
**Hypothesis ID:** h-m3
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**Statement:**
Within the same prompt (chosen/rejected pairs), human follow-up turns show higher semantic similarity to higher-PM-score AI responses (chosen) than to lower-PM-score responses (rejected): Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) > 0, surviving ≥ 2/3 length-control operationalizations (raw, length-matched truncation, prompt-projected), conditional on N_pairs ≥ 1000 per tier being verified empirically.

**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Prerequisites:** H-E1 (VALIDATED ✅), H-M1 (VALIDATED ✅)

**Rationale:**
This provides a within-prompt quasi-experimental quality probe, controlling for prompt content and conversation context — the strongest available causal test for the quality-accommodation link. The HH-RLHF chosen/rejected structure is a unique empirical asset. If confirmed, it isolates the PM-score quality signal from tier-level confounds. Conditional on Assumption A5 (N_pairs ≥ 1000 per tier).

**Variables:**
- IV: PM-score quality within same prompt (chosen vs. rejected, categorical)
- DV: Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) (continuous)
- CV: Response length (three operationalizations), prompt embedding (projection control), tier

---

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic/hh-rlhf (chosen/rejected pairs, helpfulness splits) (standard) | Chosen/rejected pair structure is the unique empirical asset for this hypothesis — same prompt, different PM-score responses; enables within-prompt quality probe |
| **Model** | all-MiniLM-L6-v2 (primary); paraphrase-MiniLM-L6-v2, all-mpnet-base-v2 (robustness) | SBERT models already validated in h-e1 and h-m1; consistent with prior hypotheses for controlled comparison |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: `datasets.load_dataset('Anthropic/hh-rlhf', data_dir='helpful-base|helpful-rejection-sampled|helpful-online')`
- Key property: Each conversation has a 'chosen' and 'rejected' field containing paired responses to the same prompt

**Model Details:**
- Type: sentence-transformers (pre-trained, inference-only)
- Source: HuggingFace model hub / sentence-transformers library
- Cache: Already cached from h-e1/h-m1 at ~/.cache/huggingface/hub/sentence-transformers

---

## Baseline & Comparison

**Baselines:**
- Function-word coordination (Danescu-Niculescu-Mizil et al. 2011): C_m(b,a) = P(E_m^u2|E_m^u1) - P(E_m^u2); p < 0.05 asymmetry in Wikipedia/Supreme Court
- H-E1 established: C_sem^H←A > 0 (existence proven, d=1.998 actual vs random)
- H-M1 established: Tier-monotonic C_sem scaling (J-T p=0.001 across 3 models)

**Proposed comparison:**
- Δ_raw = cos(H_next, A_chosen) - cos(H_next, A_rejected): raw cosine
- Δ_length = cos(H_next, A_chosen_truncated) - cos(H_next, A_rejected): length-matched truncation
- Δ_projected = cos(H_next, A_chosen - proj_prompt) - cos(H_next, A_rejected - proj_prompt): prompt-projected

---

## Dependencies & Gate Conditions

**Prerequisites:**
- H-E1: MUST_WORK PASSED ✅ (C_sem=0.3292, n=155,362 pairs)
- H-M1: MUST_WORK PASSED ✅ (J-T p=0.001 across all 3 SBERT models)

**Gate:** SHOULD_WORK
- Pass: E[Δ] > 0 with bootstrap CI lower bound > 0 in ≥ 2/3 operationalizations (conditional on N_pairs ≥ 1000)
- If N_pairs < 1000: auto-demote to exploratory, continue to H-M4

---

## Verification Protocol (from Phase 2B)

1. Filter HH-RLHF to paired conversations (same prompt, chosen + rejected response); count N_pairs per tier.
2. If N_pairs < 1000 per tier: demote H-M3 to exploratory; skip gate evaluation; continue to H-M4 with exploratory note.
3. Compute Δ via three operationalizations: (a) raw cosine, (b) length-matched truncation of chosen to rejected length, (c) projecting out prompt embedding from both A vectors.
4. Bootstrap CI (n=1000, seed=42) for each operationalization; test if lower bound > 0.
5. Run linear regression of Δ on PM-score proxy controlling for length, bullet structure, politeness markers.

**Success Criteria:**
- Primary: E[Δ] > 0 with bootstrap CI lower bound > 0 in ≥ 2/3 operationalizations (conditional on N_pairs ≥ 1000)
- Secondary: Δ magnitude consistent across tiers; length-matched operationalization > 0 (length confound controlled)

---

## Prior Hypothesis Context (h-e1, h-m1)

**From h-e1 (VALIDATED):**
- C_sem = 0.3292 (95% CI: [0.3280, 0.3304])
- n_pairs = 155,362
- Partner-specificity: cos_actual(0.3534) > cos_topic(0.2688) > cos_random(0.0241)
- Cache: /home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/.data_cache/datasets/hh-rlhf

**From h-m1 (VALIDATED):**
- Tier counts: helpful_base(43,835), helpful_rejection_sampled(52,421), helpful_online(22,007)
- J-T p=0.001 across all 3 models; Cohen d T1 vs T3: minilm=0.1826, paraphrase=0.2545, mpnet=0.2378
- IPW correction applied (KS triggered): base=0.307, RS=0.336, online=0.364

**Optimal hyperparameters (from h-e1/h-m1):**
- Batch size: 256 (SBERT encoding)
- KNN k: 5
- Bootstrap resamples: 1000
- Bootstrap seed: 42
- Significance level: 0.05

---

*JIT-generated by Phase 2C step-01 from 02b_verification_plan.md*
