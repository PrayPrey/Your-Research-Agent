# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-02T15:45:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap_1
- **Gap Title**: No Direct Benchmark of Consistency+Log-Prob Ensemble on TriviaQA/TruthfulQA with Open-Weight Models
- **Execution Mode**: UNATTENDED (#batch-mode)
- **Discussion Exchanges**: 15
- **Convergence**: Exchange 15 — all 6 criteria met

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed. Pre-registered quantitative success criteria established with explicit falsification conditions.

### Key Insights
- SE (entropy over semantic class masses) and min_logprob (minimum token probability on greedy path) are **algebraically distinct** — orthogonality is theoretically motivated, not speculative
- Length-bias-robust evaluation (LM-as-a-judge + length-matched AUROC) is essential per [Santilli et al. 2025] — lexical-only AUROC is insufficient
- The hypothesis is **meaningful regardless of sign**: positive = SE adds independent signal; negative = likelihood saturation on TriviaQA short-answer QA (equally publishable)
- Prior failure avoidance: all three prohibited approaches (hidden-state SVD from h-e1, POS filtering from h-m1, EM label OLS residualization from h-m2) are explicitly excluded
- Validated h-e1 infrastructure (SE pipeline, DeBERTa-MNLI backbone, fraction_degenerate=0.000) is directly reusable

### Breakthrough Moments
1. **Exchange 6** (Prof. Rex): Length-matched subset demand sharpened the causal control from "OLS residualization" to direct pair-matching within ±1 token — stronger protection against mutual bias
2. **Exchange 9** (Dr. Nova): Derived algebraic distinctness of SE from min_logprob from first principles (Kuhn 2023 Eq. 2-3) — the "orthogonality zone" (high confidence + high semantic disagreement) became the key mechanistic prediction
3. **Exchange 13** (Dr. Ally): Synthesized all quantitative criteria into a single pre-registered hypothesis statement with explicit success/falsification thresholds
4. **Exchange 14** (Prof. Vera): Identified circularity risk (ρ(SE, LM-judge)) as a pre-experiment diagnostic before ensemble fitting

---

## Final Hypothesis

### ID: H-SE-Ensemble-v1

### Title
Semantic Entropy Provides Conditionally Independent Uncertainty Signal Over Min Log-Probability on TriviaQA/TruthfulQA with Open-Weight LLMs

### Core Claim (Under-If-Then-Because)
**Under** Llama-3.1-8B (temperature=0.7, N=5 stochastic samples, greedy decode for log-prob features) on TriviaQA dev (2500 prompts, LM-as-a-judge correctness with a separate cross-model judge), **if** Semantic Entropy (SE_N5, bidirectional DeBERTa-MNLI NLI clustering per Kuhn et al. 2023) is added to a min_logprob baseline ensemble, **then** ΔAUROC ≥ 0.025 (95% CI lower bound > 0 on a length-matched subset of ~400-800 matched pairs), **because** SE captures semantic disagreement across stochastic samples that is conditionally independent of token-level minimum log-probability — as demonstrated by partial R² ≥ 0.02 for SE in a conditional logistic regression controlling for min_logprob, response length, and their interaction.

### Mechanism
1. **Step 1 (Algebraic Distinctness):** SE marginalizes over semantic class probability masses (NLI-cluster membership entropy), while min_logprob captures the weakest token-level prediction. These are different operations on different representations.
2. **Step 2 (Orthogonality Zone):** High min_logprob + high SE = prompts where the model is locally token-confident but globally semantically inconsistent across N=5 samples. This zone is enriched for factual hallucinations (≥10pp above base error rate).
3. **Step 3 (Ensemble Gain):** The LR ensemble exploits this complementarity, achieving ΔAUROC ≥ 0.025 under length-bias-robust evaluation (LM-as-a-judge, length-matched subset, cross-model replication without weight refitting).

### Null Hypothesis (H0)
There is no significant difference in AUROC between the min_logprob baseline and the [min_logprob + SE_N5] ensemble (ΔAUROC = 0, 95% CI overlapping zero on length-matched subset). SE does not provide conditionally independent signal (partial R² ≈ 0). Token likelihood already saturates epistemic uncertainty on TriviaQA short-answer factual QA.

---

## Predictions

| ID | Type | Statement | Success Criterion | Falsification |
|----|------|-----------|-------------------|---------------|
| P1 | PRIMARY | [min_logprob + SE_N5] achieves AUROC ≥ 0.85 on TriviaQA dev (LM-judge), ΔAUROC ≥ 0.025 (95% CI > 0, length-matched) | AUROC ≥ 0.85 AND ΔAUROC CI lower bound > 0 | AUROC < 0.85 OR CI overlaps 0 |
| P2 | Secondary | Partial R² ≥ 0.02 for SE in conditional LR; β₂ significant p < 0.05 | Partial R²(SE) ≥ 0.02 AND p < 0.05 | Partial R² < 0.01 or not significant |
| P3 | Secondary | Cross-model transfer: Llama weights on Qwen-2.5-7B TruthfulQA, AUROC gap < 0.05 | AUROC gap < 0.05, calibration slope ±0.1 | Gap > 0.05 = model-specific calibration |

---

## Novelty

**What's New:**
- First benchmark of consistency+log-prob ensemble on TriviaQA/TruthfulQA with open-weight LLMs (Llama-3.1-8B, Qwen-2.5-7B)
- First application of Santilli 2025-compliant length-bias-robust evaluation protocol (LM-as-a-judge, length-matched AUROC, correctness-function robustness sweep) on TriviaQA
- First mechanistic conditional independence test (partial R² in conditional LR) for SE vs min_logprob

**Differentiation from Prior Work:**
- vs Kuhn 2023 (SE standalone, OPT-30B, ROUGE-L): adds log-prob combination + LM-judge + open-weight models + length controls
- vs Manakul 2023 (SelfCheckGPT on WikiBio): uses factual QA benchmarks + log-prob ensemble
- vs Raghuvanshi 2025 (SQuAD2.0, no public code): TriviaQA/TruthfulQA, open-weight, public code
- vs UQLM 2025 (GPT-4o/Gemini, 6 benchmarks): provides open-weight equivalent + mechanistic analysis

---

## Experimental Design

**Dataset:** TriviaQA dev (2500 prompts, primary) + TruthfulQA (secondary/transfer)

**Model (generator):** Llama-3.1-8B (primary); Qwen-2.5-7B (cross-model transfer)

**Model (judge):** Cross-model judge (Qwen-2.5-7B or GPT-4o-mini) — separate from generator to avoid circularity

**Features:**
- Model A: `[min_logprob]` (greedy decode baseline)
- Model B: `[min_logprob, SE_N5]` (primary hypothesis, parsimony preference)
- Model C: `[min_logprob, SE_N5, SelfCheckNLI_N5]`
- Model D: `[min_logprob, SE_N5, SelfCheckNLI_N5, full_seq_var]` (full ensemble)

**Ensemble Training:** 5-fold nested CV (inner: L2 tuning; outer: AUROC); question-level bootstrap CIs (N=2000)

**Length Controls:** Length-matched subset (±1 token, correct vs incorrect pairs, ~400-800 pairs from TriviaQA dev); UQ-feature OLS residualization (Condition 2 from h-m2 — NOT correctness label residualization)

**Correctness Functions (robustness sweep):** LM-as-a-judge (primary), ROUGE-L(F1), BERTScore(F1) — sign-stability required

**Pre-Experiment Diagnostics:**
- Spearman correlation matrix (5 features × response_length × LM-judge_correctness)
- Orthogonality zone enrichment test (min_logprob ≥ 0.8 + SE top quartile)
- Circularity check: ρ(SE, LM-judge) < 0.4 required

---

## Limitations

- **Scope:** Short-answer factual QA (1-10 tokens) only; long-form generation excluded (SNNE limitations documented)
- **Models:** 7-8B scale; not validated for 70B+ scale
- **Likelihood saturation risk:** TPU AUROC=0.975 (h-e1) suggests log-prob may already capture most epistemic uncertainty; ΔAUROC may be < 0.025
- **Judge variability:** LM-as-a-judge still an estimator with its own failure modes; circularity risk if judge uses NLI-based reasoning
- **PROHIBITED approaches (from prior failures):** Hidden-state trajectory SVD (h-e1 FAIL), POS-filtered variance (h-m1 LIMITATION), OLS correctness label residualization (h-m2 SUPERSEDED)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Exchange 15 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Likelihood saturation (meaningful null if ΔAUROC < 0.025); circularity (pre-diagnostic required) |

---

*Phase 2A Complete — Ready for Phase 2B*
*Generated: 2026-08-02T15:45:00Z | Exchanges: 15 | Architecture: Self-Contained Tikitaka Loop | UNATTENDED*
