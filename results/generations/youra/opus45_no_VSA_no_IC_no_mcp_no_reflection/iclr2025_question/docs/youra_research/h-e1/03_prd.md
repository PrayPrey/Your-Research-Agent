# Product Requirements Document: h-e1

**Hypothesis:** UQ methods produce discriminative uncertainty scores (AUROC > 0.55) for hallucination detection on TruthfulQA mc1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-29
**Status:** Draft

---

## Executive Summary

Validate that uncertainty quantification (UQ) methods can discriminate between correct and hallucinated LLM responses. This is a proof-of-concept experiment requiring no model training - only inference with pre-trained models and UQ score computation.

**Success Criterion:** At least one UQ method achieves AUROC > 0.55 on TruthfulQA mc1.

---

## Problem Statement

LLMs generate plausible-sounding but factually incorrect responses (hallucinations). Detecting hallucinations without ground truth labels requires uncertainty estimation. This experiment validates whether existing UQ methods provide discriminative signals for hallucination detection.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA mc1 split (817 questions) from HuggingFace
- Parse question + answer choices format
- Extract ground truth correct answer indices
- Cache processed dataset locally

### FR-2: Model Loading
- Load Llama-3-8B-Instruct from HuggingFace
- Configure bfloat16 precision with device_map="auto"
- Verify logit extraction capability
- Support temperature sampling (0.7)

### FR-3: UQ Method - Token Entropy
- Compute entropy from final-position logits
- Formula: H = -sum(p * log(p))
- Output: Single scalar per response

### FR-4: UQ Method - Semantic Entropy
- Generate N=10 samples per query at temperature=0.7
- Cluster samples using NLI-based semantic similarity
- Compute entropy over cluster distribution
- Requires: DeBERTa-v3-large for NLI

### FR-5: UQ Method - P(True)
- Generate response, then prompt "Is the above answer correct? (Yes/No)"
- Extract probability of "Yes" token
- Output: P(correct) score (invert for uncertainty)

### FR-6: UQ Method - SelfCheckGPT
- Generate main response + K=5 sample responses
- Use SelfCheckNLI to score consistency
- Output: Inconsistency score (higher = more hallucination)
- Requires: selfcheckgpt package

### FR-7: Evaluation Pipeline
- Compute AUROC for each method against ground truth
- Compute AUPRC as secondary metric
- Generate ROC curves and score distributions
- Apply 0.55 threshold for pass/fail

### FR-8: Results Logging
- Save per-question scores to CSV
- Save aggregate metrics to JSON
- Generate visualization figures
- Write summary to 04_validation.md

---

## Non-Functional Requirements

### NFR-1: Compute
- GPU: 1x A100 40GB (or 2x RTX 3090)
- Runtime: 2-4 hours total
- Memory: Peak ~35GB for model + NLI

### NFR-2: Reproducibility
- Fixed seed: 42
- Deterministic sampling where possible
- Log all hyperparameters

### NFR-3: Dependencies
- transformers >= 4.40
- torch >= 2.0
- selfcheckgpt
- sklearn
- datasets

---

## Success Criteria

| Criterion | Metric | Threshold |
|-----------|--------|-----------|
| Primary | max(AUROC across methods) | > 0.55 |
| Secondary | AUPRC | > baseline |
| Gate | MUST_WORK | Pipeline stops if all methods fail |

---

## Dependencies

- Phase 2C: 02c_experiment_brief.md (completed)
- External: HuggingFace model access (Llama-3 gated)
- External: selfcheckgpt package (pip install)

---

## Out of Scope

- Model fine-tuning
- Novel UQ method development
- Multi-dataset evaluation
- Ablation studies (deferred to mechanism hypotheses)

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Location |
|---------------|--------------|
| TruthfulQA mc1 | FR-1 |
| Llama-3-8B-Instruct | FR-2 |
| Token Entropy | FR-3 |
| Semantic Entropy | FR-4 |
| P(True) | FR-5 |
| SelfCheckGPT | FR-6 |
| AUROC > 0.55 | FR-7, Success Criteria |
