# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan (JIT by Phase 2C Step 1)
**Date:** 2026-03-14
**Main Hypothesis:** Human Semantic Accommodation Sensitivity to RLHF Alignment Quality
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under HH-RLHF helpfulness conversations, if SBERT cosine similarity is computed between human follow-up turns and AI partner turns with matched-shuffle baseline subtraction, then C_sem^H←A = E[cos(SBERT(H_{t+1}), SBERT(A_t))] - E[cos(SBERT(H_{t+1}), SBERT(A_t^matched-shuffle))] > 0 AND partner-specificity gap holds (cos(H_next, A_actual) > cos(H_next, A_topic-matched) > cos(H_next, A_random), d ≥ 0.1 between adjacent levels), because semantic accommodation to a specific interlocutor produces interaction-specific alignment beyond topical coherence.

### Type
EXISTENCE

### Rationale
This is the foundational existence proof for the entire study. Without C_sem > 0 with partner-specificity, neither tier-level monotonicity nor directional asymmetry can be interpreted as evidence of accommodation. This establishes that SBERT captures accommodation-relevant semantic variation, not merely topical persistence, via the three-level control hierarchy.

---

## Verification Protocol

### Conceptual Test
1. Encode all HH-RLHF helpful splits with all-MiniLM-L6-v2 (batch size 256, CPU); build K=5 KNN topic-matched control by prompt embedding from different conversations in same tier.
2. Compute C_sem with true random shuffle baseline for all tiers combined (pooled over tiers for existence test).
3. Compute three-level partner-specificity: cos(H_next, A_actual), cos(H_next, A_topic-matched), cos(H_next, A_random).
4. Test pairwise Mann-Whitney U + bootstrap Cohen's d (n=1000, seed=42) for each adjacent level contrast.
5. Report bootstrap CI for C_sem; check if lower bound > 0; confirm d ≥ 0.1 between actual and topic-matched.

### Success Criteria
- Primary: C_sem^H←A > 0 with bootstrap CI lower bound > 0
- Secondary: d ≥ 0.1 between cos(H_next, A_actual) and cos(H_next, A_topic-matched), with three-way inequality holding

### Variables
- **Independent Variable:** Actual vs. topic-matched vs. random AI turn (three-level control)
- **Dependent Variable:** C_sem = E[cos(SBERT(H_{t+1}), SBERT(A_t))] - shuffle baseline; cos(H_next, A_actual); cos(H_next, A_topic-matched)
- **Controlled Variables:** Response length (residualized), lexical overlap (residualized), prompt embedding distribution (KS test)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Anthropic/hh-rlhf (helpfulness splits: helpful-base, helpful-rejection-sampled, helpful-online)
- **Type:** standard
- **Source:** HuggingFace datasets
- **Path:** `datasets.load_dataset('Anthropic/hh-rlhf', data_dir='helpful-base')` etc.
- **Hypothesis Fit:** Three-tier RLHF quality gradient directly operationalizes the IV; chosen/rejected structure provides within-tier quality control; ~273,617 conversation turns provides sufficient N for d ≥ 0.1 detection

### Selected Model
- **Name:** all-MiniLM-L6-v2 (primary); paraphrase-MiniLM-L6-v2, all-mpnet-base-v2 (robustness)
- **Type:** sentence-transformers (pre-trained, inference-only)
- **Source:** HuggingFace model hub / sentence-transformers library
- **Hypothesis Fit:** SBERT validated for semantic similarity measurement; CPU-capable (14K sentences/sec); no fine-tuning required; multi-model robustness test rules out geometry artifacts

---

## Baseline & Comparison Targets

### Baseline Methods
- Function-word coordination (Danescu-Niculescu-Mizil et al. 2011): C_m(b,a) = P(E_m^u2|E_m^u1) - P(E_m^u2); p < 0.05 asymmetry in Wikipedia and Supreme Court
- Word-level LLM-human bidirectional adaptation (Chang & Wang 2025): Word-level style matching confirmed in LLM-human dialog across cultures
- PM-grounded feature analysis on HH-RLHF (h-e1 Attempt 2): Max d=0.136; keyword proxies insufficient; placebo features (length d=0.735) dominated
- Human turn lexical features on HH-RLHF (h-e1 Attempt 3): d_human=0.036; CI includes zero; hapax anti-monotonic

### Baseline Performance
Three prior attempts on HH-RLHF using surface lexical features (word_count, hapax_ratio, PM-grounded keywords) all failed (d ∈ [0.036, 0.136]), suggesting the effect exists at the semantic embedding level.

### Gap Analysis
Surface-level features consistently fail (d < 0.1); SBERT semantic embedding approach is the novel fourth attempt targeting meaning-level accommodation.

---

## Dependencies and Gate Conditions

### Prerequisites
None — this is the first hypothesis in the verification chain.

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** STOP pipeline; report null result for semantic accommodation existence; write Serena failure memory; ROUTE_TO_0 for new direction

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** Moderate (SBERT encoding ~273K turns, KNN construction, bootstrap statistics)

---

## Dependency Context

### Relationship to Other Hypotheses
- H-E1 is foundational: H-M1, H-M2 (via H-M1), H-M3 (via H-E1, H-M1), H-M4 (via H-M1, H-M2, H-M3) all depend on H-E1 passing.
- This is the first hypothesis in the verification chain.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
