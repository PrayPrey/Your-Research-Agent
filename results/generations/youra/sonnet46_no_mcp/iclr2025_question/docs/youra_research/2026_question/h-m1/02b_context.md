# H-M1: Per-Hypothesis Context (Phase 2B → Phase 2C)

**Generated:** 2026-05-11 (JIT by Phase 2C step-01)
**Source:** 02b_verification_plan.md
**Hypothesis ID:** H-M1

---

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM (Causal Step 1)
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (VALIDATED ✅)

**Statement:**
Under fixed-budget inference conditions on HaluEval-QA, if token-level entropy (mean aggregation) and semantic entropy are computed on the same LLaMA-2-7B-chat responses, then their Pearson correlation will be significantly below 1.0 (r < 0.9 across all 2,000 examples), because LLM token probability distributions simultaneously encode surface-form variation (word choice, phrasing) and semantic variation (factual uncertainty), and these two sources contribute differentially to total token entropy on factual QA tasks where lexical diversity is high.

**Rationale:**
This hypothesis tests the first causal step: that token entropy and semantic entropy diverge because they capture different variance sources. If r > 0.9, token entropy and semantic entropy are essentially measuring the same thing, invalidating the mechanism explanation for semantic entropy's claimed superiority. The correlation threshold (r < 0.9) is a necessary (not sufficient) condition for the mechanism to hold.

---

## Variables

- **Independent:** UQ Signal Type (token_entropy_mean vs. semantic_entropy) computed on identical responses
- **Dependent:** Pearson correlation r between token_entropy_mean and semantic_entropy scores across 2,000 examples; distribution of score divergence by example
- **Controlled:** Same LLM (LLaMA-2-7B-chat), same 2,000-example sample, same NLI model (deberta-large-mnli)

---

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HaluEval-QA (standard, 2,000 stratified examples — reuse H-E1 outputs) | Outputs already computed in H-E1; no new inference needed; same sample ensures controlled comparison |
| **Model** | LLaMA-2-7B-chat (reuse H-E1 cached outputs) | All greedy logits + 5 stochastic samples per example already generated |
| **NLI Model** | microsoft/deberta-large-mnli | Used in H-E1 semantic entropy computation |

**Dataset Details:**
- Source: pminervini/HaluEval (qa_samples)
- Cache path: h-e1/code/data/halueval_qa_2k.json (verified, 2000 examples: 1000 hallucinated + 1000 factual, seed=42)
- Pre-computed UQ scores: h-e1/code/outputs/uq_scores/token_entropy_mean.json, semantic_entropy.json

**Model Details:**
- LLM: meta-llama/Llama-2-7b-chat-hf (inference outputs cached, no re-generation needed)
- NLI: microsoft/deberta-large-mnli (used for semantic entropy clustering in H-E1)

---

## Verification Protocol (from 02b_verification_plan.md)

1. Use the 2,000-example responses and logits generated in H-E1 (no additional generation needed).
2. Compute token_entropy_mean and semantic_entropy for each of the 2,000 examples.
3. Compute Pearson r between the two score vectors; compute Spearman ρ as robustness check.
4. Identify examples with largest divergence (|token_entropy - semantic_entropy| > 1 SD); analyze their lexical diversity (type-token ratio of 5 stochastic samples).
5. Report r, ρ, and divergence distribution; confirm r < 0.9 as evidence of surface/semantic conflation.

---

## Success Criteria

- **Primary:** Pearson r < 0.9 between token_entropy_mean and semantic_entropy score vectors (p < 0.05, bootstrap CI)
- **Secondary:** High-divergence examples show high lexical diversity (many distinct surface forms with same factual answer)

## Failure Response

- IF r ≥ 0.9: PIVOT — document that surface-form filtering is not the mechanism; explore whether semantic entropy advantage arises from a different source

---

## Baseline & Comparison Targets

- **Baseline metric:** r = 1.0 (perfect correlation — null hypothesis: no difference in what signals capture)
- **Target threshold:** r < 0.9 (significant divergence between signal types)
- **Gate:** MUST_WORK — if r ≥ 0.9, mechanism is not supported

---

## Dependencies & Gate Conditions

- **H-E1 MUST_WORK gate:** SATISFIED ✅ (2 qualifying pairs with Δ≥0.05 AUROC non-overlapping CIs)
- **H-E1 key finding:** SE AUROC=0.5000 (degenerate CI), TE AUROC=0.4829 — NLI clustering behavior needs investigation
- **Continuation context:** All H-E1 inference outputs are cached and reusable

---

## Notes from H-E1 Validation (Phase 2C Handoff)

- Semantic entropy AUROC=0.5 with degenerate CI [0.5, 0.5] — likely constant scores across 2000 examples
- Token entropy AUROC=0.4829 — near random
- H-M1 should first diagnose whether NLI clustering produced meaningful cluster count variation
- If semantic entropy scores are constant (0 entropy for all examples), Pearson r may be undefined or degenerate
- All code infrastructure reusable: data.py, uq_signals.py, evaluate.py from h-e1/code/
