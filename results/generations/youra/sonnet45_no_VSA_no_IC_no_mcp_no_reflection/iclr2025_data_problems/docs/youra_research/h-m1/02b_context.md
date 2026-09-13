# Phase 2B Context: H-M1

**Generated:** 2026-08-28T09:30:00Z  
**Source:** 02b_verification_plan.md  
**Hypothesis ID:** H-M1

---

## Hypothesis Information

**Type:** MECHANISM  
**Status:** NOT_STARTED (awaits H-E1)  
**Gate:** MUST_WORK

**Statement:**
Data curation (deduplication, filtering, domain mixing) increases information density per token, measured by entropy reduction and Fisher information increase.

**Rationale:**
Causal mechanism step 1-2 from refinement (Section 1.3). Proves Q(D) improvements create measurable information density gains. Required for compute multiplier claim.

---

## Success Criteria

- Entropy reduction >20% after aggressive deduplication (95% vs 0%)
- Fisher information matrix trace increases >15% with higher Q(D)
- Effect holds across 3 curation dimensions (dedup, filter, mix)

---

## Experimental Approach

1. Train small probe models (125M params) on curated vs uncurated C4 subsets
2. Measure gradient statistics (Fisher information) during training
3. Compute token-level entropy and perplexity distributions
4. Ablation study: vary one quality dimension at a time

---

## Controlled Variables (from Phase 2A)

**Dataset:** C4 (Colossal Clean Crawled Corpus)  
**Model:** GPT-2 architecture (decoder-only transformer)  
**Optimizer:** AdamW with fixed learning rate schedule  

**Hyperparameters:**
- Model size: 125M parameters (probe model for this hypothesis)
- Batch size: fixed per scale
- Learning rate: Chinchilla-optimal schedule
- Training seeds: 3 per condition

---

## Dependencies

**Prerequisites:** H-E1 (requires validated Q(D) metrics)

**Provides for:** H-M2 (proven information density mechanism)

---

## Gate Conditions

**MUST_WORK Gate:**
- Purpose: Foundation hypothesis; failure blocks Phase 5
- Action on PARTIAL: 1 modification attempt → Phase 2A-Dialogue if still fails
- Action on FAIL: Route to Phase 0 (fundamental flaw)

---

## Resource Budget

**Compute:** ~50 GPU-hours (125M models with gradient logging, ablation studies)  
**Dataset:** C4 subsets, 50GB with curation variations  
**Storage:** ~100GB with intermediate results

---

*Context extracted from 02b_verification_plan.md for hypothesis H-M1*
