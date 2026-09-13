# Per-Hypothesis Context: H-M4

**Generated:** 2026-08-03 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Prerequisites:** H-M3 (VALIDATED)

---

## Hypothesis Statement

Cross-model contract-satisfaction rate across 5 LLM families is orthogonal to pass@1⋆ (Kendall τ ≤ 0.6, partial ΔR² ≥ 0.10) and contract-strength gap varies ≥ 0.10 absolute between best/worst model families controlling for pass@k.

## Rationale

Tests whether contract-strength measurement is a novel axis of model evaluation. If τ ≥ 0.8, contracts simply replicate pass@k rankings. Low τ and high ΔR² establish that contract evaluation complements existing benchmarks.

## Variables

- **IV:** LLM model family (GPT-4o-mini, Claude-3-haiku, DeepSeek-Coder-V2-Lite, CodeLlama-13B, CodeLlama-34B)
- **DV:** Per-model contract-satisfaction rate; Kendall τ vs. pass@1⋆; partial ΔR²; cross-model gap range
- **CV:** ContractEval 364 tasks, n=10 samples per model per task, Experiment B adaptive PBT results

## Success Criteria

- **Primary:** Kendall τ ≤ 0.6 (permutation p < 0.05) AND partial ΔR² ≥ 0.10
- **Secondary:** Cross-model contract-strength gap range ≥ 0.10 absolute, model family coefficient p < 0.05

## Failure Response

IF fails (τ ≥ 0.8 or ΔR² < 0.05) → EXPLORE: contracts replicate pass@k; reframe as negative result showing redundancy; still publishable.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

- **Name:** ContractEval (HumanEval+/MBPP+ subset)
- **Type:** standard
- **Source:** github.com/suhanmen/ContractEval (ACL 2026)
- **Path:** 364 tasks with Python pre/post-condition contracts
- **Hypothesis Fit:** Primary benchmark containing all required contract annotations; enables direct EvalPlus integration; covers both HumanEval+ and MBPP+ for cross-task generalization

### Model

- **Name:** Multi-model evaluation (5 LLM families)
- **Type:** Mixed (API closed + vLLM/HuggingFace open)
- **Source:** evalplus/evalplus (1789★, NeurIPS 2023) with OpenAI/Anthropic/HuggingFace backends
- **Models:**
  - GPT-4o-mini (closed, OpenAI API)
  - Claude-3-haiku (closed, Anthropic API)
  - DeepSeek-Coder-V2-Lite (open, vLLM/HuggingFace)
  - CodeLlama-13B (open, vLLM/HuggingFace)
  - CodeLlama-34B (open, vLLM/HuggingFace)
- **Hypothesis Fit:** Required for cross-model τ/ΔR² computation; mix of open+closed tests generalization

## Verification Protocol

1. Compute per-model mean contract-satisfaction rate from Experiment B (Hypothesis PBT results from H-M3).
2. Compute Kendall τ and Spearman ρ between contract-satisfaction and HUMANEVAL+ pass@1⋆ rankings.
3. Fit regression: `contract_rate ~ pass@1⋆ + log(model_size) + model_type`; compute partial ΔR² for model identity.
4. Fit mixed-effects model: model family coefficient controlling for task difficulty (random effect).
5. Permutation test for τ significance; report range = max_model_gap − min_model_gap.

## Dependencies

- **H-M3 (VALIDATED):** Experiment B adaptive PBT results needed — provides per-model contract-satisfaction rates
- Also reuses Experiment A static oracle results from H-M1 (VALIDATED) for baseline comparison

## Previous Hypothesis Results (from H-M3)

- Mean adaptive contribution = 0.0999 (> 0 threshold)
- Wilcoxon p = 2.64e-22 (one-sided); bootstrap 95% CI [0.0651, 0.1325]
- Tasks with positive contribution: 257/354 (72.6%)
- Consistent across all 5 models (range 0.099–0.103)
- Data coverage: 17,226 joined triples from 18,200 total (94.6%)

## Gate Status

- **Gate:** SHOULD_WORK
- **H-M3 prerequisite:** SATISFIED (VALIDATED)
- **Status:** READY to proceed
