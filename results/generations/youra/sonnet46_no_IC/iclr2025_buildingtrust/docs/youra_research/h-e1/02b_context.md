---
hypothesis_id: h-e1
generated_by: Phase 2C step-01 JIT generation
source: 02b_verification_plan.md
generated_at: 2026-08-04
---

# H-E1 Per-Hypothesis Context

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Gate:** MUST_WORK
- **Prerequisites:** None (foundation hypothesis)

### Statement

Under the TrustLLM 16-model × 6-dimension evaluation setting, if we compute partial Spearman rank correlations for all 15 dimension pairs controlling for log(param_count) and RLHF status, then at least one correlation will be statistically significant (|ρ_partial| > 0.5, p < 0.0033 Bonferroni-corrected), because LLM trustworthiness dimensions are not statistically independent — RLHF optimization systematically co-moves related dimensions.

### Rationale

This is the foundation hypothesis testing whether any correlation structure exists at all. It directly verifies PROVE_NEW claim 2 (2-cluster RLHF-driven structure). Without passing H-E1, no mechanism testing makes sense.

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

- **Name:** TrustLLM Published Score Tables
- **Type:** standard
- **Source:** https://github.com/HowieHwong/TrustLLM (results/ folder)
- **Path:** HowieHwong/TrustLLM repository / results/*.json
- **Description:** 16-model × 6-dimension score matrix. Scores are pre-computed and publicly available. 6 dimensions: truthfulness, safety, fairness, robustness, privacy, machine ethics.
- **Hypothesis Fit:** Provides the exact 16-model × 6-dimension score matrix needed for the primary partial Spearman correlation analysis. Scores are pre-computed, satisfying the existing-data constraint.

### Model

- **Name:** TrustLLM 16-model evaluation set
- **Type:** convenience sample (published evaluation results)
- **Source:** TrustLLM paper (Sun et al., 2024), ICML 2024
- **Models included:** LLaMA-2 7B/13B/70B base+chat, Mistral-7B, Falcon-7B, GPT-3.5-turbo, GPT-4, Claude-2, Vicuna variants, and others spanning ~7B to ~175B+ parameters
- **Hypothesis Fit:** Spans sufficient variation in scale (log param count) and RLHF alignment status for partial correlation estimation. Includes both RLHF-tuned (Chat/Instruct) and base models.

## Variables

- **Independent:** Trustworthiness dimension pair (15 combinations of 6 dimensions)
- **Dependent:** Partial Spearman ρ_partial (after OLS residualization on [log_params, is_RLHF])
- **Controlled:** Benchmark operationalization (TrustLLM fixed), model population (16-model set)

## Success Criteria (PoC)

- **Primary (MUST_WORK gate):** At least 1 of 15 |ρ_partial| > 0.5 AND p < 0.0033 (Bonferroni-corrected for 15 tests)
- **Secondary:** Silhouette score > 0.3 for k=2 hierarchical Ward clustering solution

## Verification Protocol

1. Download HowieHwong/TrustLLM results/*.json and extract per-model per-dimension scores into 16×6 matrix
2. Annotate each model with log10(param_count) and is_RLHF binary flag
3. For each of 15 dimension pairs: OLS-residualize both dimensions on [log_params, is_RLHF], compute Spearman ρ on residuals, test H0: ρ=0 using t-distribution (df=13)
4. Apply Bonferroni correction (α=0.0033 for 15 tests); flag significant pairs
5. Perform Ward hierarchical clustering on 6×6 ρ_partial matrix; compute silhouette score for k=2

## Failure Response

- IF primary fails: PIVOT — investigate whether score files have sufficient granularity (A1 check); run lm-eval-harness as fallback

## Key Risks

- **R1 (Critical):** TrustLLM JSON may contain only aggregate rankings, not per-dimension float scores → verify data format first
- **R2 (High):** n=16 may be insufficient power after Bonferroni; Pythia expansion partially mitigates
