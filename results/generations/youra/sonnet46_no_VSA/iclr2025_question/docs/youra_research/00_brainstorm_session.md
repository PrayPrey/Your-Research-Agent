---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Consistency-Based UQ for Hallucination Detection in LLMs"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-02
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Uncertainty quantification (UQ) and hallucination detection in large language models (LLMs) and multimodal foundation models for high-stakes domains

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Reflection 3)

**Session Duration:** < 1 minute (automated extraction with failure context integration from 3 Serena Memory records)

---

## Starting Context

How can we trust large language models (LLMs) when they generate text with confidence, but sometimes hallucinate or fail to recognize their own limitations? As foundation models like LLMs and multimodal systems become pervasive across high-stakes domains—from healthcare and law to autonomous systems—the need for uncertainty quantification (UQ) is more critical than ever. Uncertainty quantification provides a measure of how much confidence a model has in its predictions, allowing users to assess when to trust the outputs and when human oversight may be needed.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Uncertainty Quantification for Foundation Models)

Retrying after two previous failure/limitation cycles (h-e1 FAIL, h-e2 PARTIAL/h-m1 LIMITATION). New direction informed by cumulative failure diagnostics: both hidden-state geometry and token log-probability aggregation approaches have been explored. Pivoting to **consistency-based UQ** — a complementary signal class that measures disagreement across multiple model outputs.

---

## Lessons from Previous Attempts

### Attempt 1: h-e1 — Spectral Entropy of Hidden-State Trajectory

**What Was Tried:** Last-4-layer hidden-state trajectory SVD (H_spec = Shannon entropy of rank-64 singular values, trajectory shape k×T, d) predicting SNNE above median. Target: AUROC ≥ 0.85, partial Spearman ρ > 0.60 after length control.

**Why It Failed:** H_spec correlated 0.952 with token count. Matrix (k×T, d) is length-dominated — singular value structure encodes sequence length T, not semantic content. After OLS residualization: AUROC = 0.537 ≈ chance, partial ρ = -0.047. Root assumption invalidated: concatenating hidden layers along token dimension creates a length-dominated matrix.

**Key Finding:** TPU/log-prob AUROC = 0.975 on TriviaQA — SNNE IS predictable from log-probabilities.

---

### Attempt 2: h-e2 + h-m1 — Log-Probability Ensemble (Token-Level Statistics)

**What Was Tried:** Sequence-level aggregations of token log-probabilities (mean_token_entropy, mean_logprob, content_token_variance, min_logprob) as hallucination UQ signals. POS-filtered content-token variance (h-m1) as ablation.

**h-e2 Result (PARTIAL):** VIF gate passed (feature extraction validated), but mean_token_entropy ≈ −log_prob in greedy decoding — these are collinear features. Fallback ensemble: [min_logprob, content_token_variance]. Model: Llama-3.1-8B (3.3-70B inaccessible, 403).

**h-m1 Result (LIMITATION):** POS-filtered content-token variance AUROC = 0.8008 < full-sequence variance AUROC = 0.8250 (delta = -0.024). POS filtering removes uncertainty signal carried by function words. Sub-word alignment miss rate 16% above threshold. Full-sequence variance is superior.

**Key Finding:** Log-prob ensemble [min_logprob, full_sequence_variance] achieves AUROC ~0.82–0.83. Single-greedy-pass log-prob signals are strong but have a performance ceiling. Collinearity between entropy and log-prob under greedy decode is fundamental.

---

### How This New Direction Avoids Previous Pitfalls

**AVOID:**
- Trajectory concatenation along token dimension for SVD (h-e1 failure mode — always length-dominated)
- Hidden-state extraction (computationally expensive, architecture-specific)
- POS-based filtering of token-level signals on short-answer QA (h-m1 failure mode — removes real signal)
- Greedy-only log-prob features that saturate collinearity (entropy ≈ -log_prob in greedy decode)
- Any method requiring model internals beyond token probabilities

**NEW DIRECTION — Consistency-Based UQ:**
Previous attempts used **single-pass internal signals** (hidden states, log-probs from one forward pass). This reflection pivots to **multi-sample consistency** — measuring how much a model's outputs vary across multiple stochastic samples. This approach:
1. Captures a genuinely different signal class (output-level disagreement vs. single-pass probability statistics)
2. Is complementary to log-prob features — can be combined with [min_logprob, full_sequence_variance] ensemble
3. Is applicable to black-box models (only requires generation API, no log-prob access needed)
4. Has established baselines (SelfCheckGPT, semantic entropy) on the exact same benchmarks (TriviaQA, TruthfulQA)
5. Avoids ALL identified failure modes (no hidden states, no POS filtering, no single-pass collinearity)

---

## Session Plan

ROUTE_TO_0 Auto-extraction from structured input + failure context integration from 3 Serena Memory records (failure_h-e1_run1, h-e2/phase4-completion, limitation_h-m1_run1)

---

## Technique Sessions

ROUTE_TO_0 Mode - No interactive sessions. Failure context integrated from Serena Memory. Three failure/limitation records synthesized to identify unexplored signal class: consistency-based UQ via multi-sample generation disagreement.

---

## Research Question Development

### Initial Question

Can self-consistency metrics derived from multiple stochastic LLM generations — measuring lexical, semantic, and entailment-based disagreement across samples — provide reliable hallucination detection signals that outperform single-pass log-probability baselines on existing benchmarks?

### Refined Question

Do self-consistency uncertainty signals derived from N=5–10 stochastic samples (lexical consistency via ROUGE/BERTScore variance, semantic cluster entropy via NLI-based grouping, and entailment consistency via cross-sample contradiction detection) achieve AUROC ≥ 0.85 for hallucination detection on TriviaQA dev and TruthfulQA, outperforming the single-greedy-pass log-probability ensemble [min_logprob, full_sequence_variance] (AUROC ~0.82) established in h-e2/h-m1, using open-weight LLMs (Llama-3.1-8B, Qwen-2.5-7B) on existing benchmark splits without any fine-tuning or hidden-state extraction?

### Detailed Sub-Questions

1. Which self-consistency metric (lexical ROUGE variance, BERTScore pairwise variance, NLI-cluster entropy, cross-sample entailment contradiction rate) achieves highest AUROC for hallucination detection on TriviaQA dev using N=5 stochastic samples (temperature=0.7)?
2. Does NLI-cluster-based semantic entropy (Kuhn et al. 2023 approach) outperform lexical consistency metrics on TriviaQA and TruthfulQA when using the same N samples, controlling for computational cost?
3. Does combining consistency-based UQ signals with the validated log-prob ensemble [min_logprob, full_sequence_variance] (from h-e2/h-m1) via logistic regression achieve AUROC ≥ 0.87 on TriviaQA dev holdout — exceeding both single-source baselines?
4. How does performance degrade as N decreases from 10 to 3 samples, and is there a cost-efficiency frontier where N=3 consistency signals match N=10 performance?
5. Do consistency-based UQ signals transfer across model families (Llama-3.1-8B vs Qwen-2.5-7B) without model-specific recalibration, measured by AUROC delta < 0.05 across models on TriviaQA dev?

---

## Reference Papers

Not provided - will discover in Phase 1

Key papers to prioritize in Phase 1 search:
- Kuhn et al. (2023) "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation" (NeurIPS 2023) — primary semantic entropy baseline
- Manakul et al. (2023) "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models" — consistency-based hallucination detection
- Lin et al. (2022) "Teaching Models to Express Their Uncertainty in Words"
- Xiong et al. (2024) "Can LLMs Express Their Uncertainty?" — verbalized vs. behavioral UQ
- Fadeeva et al. (2023) "LM-Polygraph: Uncertainty Estimation for Language Models" — toolkit survey
- Wang et al. (2023) "Self-Consistency Improves Chain of Thought Reasoning" — consistency as reliability signal
- Azaria & Mitchell (2023) "The Internal State of an LLM Knows When It's Lying" — hidden-state baseline for comparison

---

## Validation Results

### So What Test

Input from ICLR 2025 Workshop on UQ for Foundation Models — significance pre-validated.

**Impact:** Self-consistency UQ is the most practically deployable uncertainty signal — requiring only generation API access (no log-probs, no hidden states). If consistency metrics achieve AUROC ≥ 0.85 and outperform the log-prob ensemble established in h-e2/h-m1, this demonstrates that output-level disagreement is a superior hallucination detector for black-box LLMs (GPT-4, Claude) deployed in high-stakes settings (healthcare QA, legal retrieval).

**Compounding value:** Testing whether combining consistency signals WITH the validated log-prob ensemble from h-e2/h-m1 achieves further improvement directly addresses the workshop's question about scalable, ensemble-based UQ methods for foundation models.

**Failure lessons applied:** h-e1 and h-e2/h-m1 exhausted single-pass internal signals. Consistency-based UQ is the natural complementary signal class that uses the same datasets/infrastructure but a genuinely different measurement modality.

### Feasibility Check

**Mandatory Feasibility Constraints — ALL SATISFIED:**
- ✅ No new benchmarks: TriviaQA dev (2500 prompts, h-e1 infrastructure reusable), TruthfulQA (817 MC questions, public) — all existing datasets
- ✅ No synthetic/generated data: Uses existing dataset splits with ground-truth labels; multi-sample generation from open-weight models is standard practice
- ✅ No human annotation: All evaluation uses automated metrics (AUROC, ROUGE, BERTScore, NLI via existing model e.g. DeBERTa-NLI, partial Spearman ρ)
- ✅ No new rubrics/scoring frameworks: AUROC, ROUGE-L, BERTScore, semantic entropy — all standard established metrics
- ✅ Immediately testable: HuggingFace models (Llama-3.1-8B, Qwen-2.5-7B) with temperature sampling; NLI via cross-encoder/deberta-v3-large-zeroshot-v2 (public)
- ✅ Avoids all previous failure modes: No hidden-state concatenation (h-e1), no POS filtering (h-m1), no greedy-only collinear features (h-e2)
- ✅ Reuses h-e1/h-e2 infrastructure: TriviaQA data loading, AUROC evaluation, OLS residualization for length control
- ✅ Builds on validated baseline: [min_logprob, full_sequence_variance] from h-e2/h-m1 serves as established comparison point (AUROC ~0.82)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Do self-consistency uncertainty signals derived from N=5–10 stochastic samples (lexical consistency via ROUGE/BERTScore variance, semantic cluster entropy via NLI-based grouping, and entailment consistency via cross-sample contradiction detection) achieve AUROC ≥ 0.85 for hallucination detection on TriviaQA dev and TruthfulQA, outperforming the single-greedy-pass log-probability ensemble [min_logprob, full_sequence_variance] (AUROC ~0.82) established in h-e2/h-m1, using open-weight LLMs (Llama-3.1-8B, Qwen-2.5-7B) on existing benchmark splits without any fine-tuning or hidden-state extraction?

### detailed_question
1. Which self-consistency metric (lexical ROUGE variance, BERTScore pairwise variance, NLI-cluster entropy, cross-sample entailment contradiction rate) achieves highest AUROC for hallucination detection on TriviaQA dev using N=5 stochastic samples (temperature=0.7)?
2. Does NLI-cluster-based semantic entropy (Kuhn et al. 2023 approach) outperform lexical consistency metrics on TriviaQA and TruthfulQA when using the same N samples, controlling for computational cost?
3. Does combining consistency-based UQ signals with the validated log-prob ensemble [min_logprob, full_sequence_variance] (from h-e2/h-m1) via logistic regression achieve AUROC ≥ 0.87 on TriviaQA dev holdout — exceeding both single-source baselines?
4. How does performance degrade as N decreases from 10 to 3 samples, and is there a cost-efficiency frontier where N=3 consistency signals match N=10 performance?
5. Do consistency-based UQ signals transfer across model families (Llama-3.1-8B vs Qwen-2.5-7B) without model-specific recalibration, measured by AUROC delta < 0.05 across models on TriviaQA dev?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Three failure/limitation records synthesized: h-e1 (hidden-state geometry FAIL), h-e2 (log-prob extraction PARTIAL/validated), h-m1 (POS-filtered variance LIMITATION). The signal space of single-pass internal model features has been explored.
- Consistency-based UQ is the natural next signal class — orthogonal to both failed approaches, uses same benchmarks, requires only generation API
- Validated h-e2/h-m1 ensemble [min_logprob, full_sequence_variance] (AUROC ~0.82) provides a concrete, internally-validated baseline for comparison
- NLI-cluster semantic entropy (Kuhn et al. 2023) is the most established consistency-based baseline on TriviaQA — Phase 1 should prioritize this paper
- SelfCheckGPT (Manakul et al. 2023) provides lexical + NLI consistency framework directly applicable to TriviaQA/TruthfulQA
- Combining consistency + log-prob signals is a novel ensemble not tested in prior work — potential for AUROC improvement beyond either signal alone

### Techniques Used

ROUTE_TO_0 Mode: Failure context integration from 3 Serena Memory records + structured input extraction. Signal class pivot from internal (hidden-state/log-prob) to external (consistency-based) UQ.

### Areas for Further Exploration

- Gram matrix approach K = H H^T / (1+log T): eigenspectrum entropy with explicit length normalization — if consistency approach also fails, this is the next hidden-state alternative
- Per-last-token hidden state SVD across layers (not trajectory concatenation) — avoids h-e1 length confound
- Conformal prediction coverage guarantees on top of consistency-based UQ
- Cross-lingual consistency UQ using multilingual TriviaQA or MKQA
- Verbalized uncertainty (model expresses own confidence in words) as complementary signal to consistency — Xiong et al. 2024

---

## Next Steps

Proceed to Phase 1 - Targeted Research (`/phase1-targeted`)

Focus areas for Phase 1 literature search:
1. Semantic entropy (Kuhn et al. 2023) — primary baseline for NLI-cluster consistency UQ on TriviaQA
2. SelfCheckGPT (Manakul et al. 2023) — lexical + NLI consistency-based hallucination detection framework
3. Self-consistency sampling methods (Wang et al. 2023) and relationship to UQ
4. Combining log-prob + consistency signals: prior ensemble work in UQ literature
5. N-sample efficiency: how many samples needed for reliable consistency estimates

**Failure lessons applied:**
- Do NOT revisit hidden-state trajectory concatenation (h-e1 failure mode)
- Do NOT use POS filtering on short-answer QA (h-m1 failure mode)
- Do NOT treat mean_token_entropy and mean_logprob as independent features in greedy decode (h-e2 collinearity finding)
- Use [min_logprob, full_sequence_variance] as the validated internal baseline for comparison (h-e2/h-m1 result)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
