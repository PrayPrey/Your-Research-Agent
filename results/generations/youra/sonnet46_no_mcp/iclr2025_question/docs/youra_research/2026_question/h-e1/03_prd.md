# Product Requirements Document: H-E1
# Semantic Entropy UQ Comparison — EXISTENCE PoC

**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK gate)
**Generated:** 2026-05-11
**Phase:** 3 - Implementation Planning
**Tier:** LIGHT (15-task budget)
**Author:** Anonymous
---

## 1. Executive Summary

This PRD specifies implementation requirements for H-E1, the foundational existence hypothesis in the Semantic Entropy UQ Comparison pipeline. The experiment validates that at least one pairwise AUROC difference ≥ 0.05 (non-overlapping 95% bootstrap CIs) exists between three UQ methods — token-level entropy (token_entropy_mean), semantic entropy (semantic_entropy), and SelfCheckGPT-BERTScore (selfcheckgpt_bertscore_n5) — applied to LLaMA-2-7B-chat on a 2,000-example stratified HaluEval-QA sample.

**MUST_WORK gate:** The discrimination gap must be statistically confirmed before downstream mechanism hypotheses (H-M1, H-M2, H-M3) can proceed.

---

## 2. Problem Statement

### 2.1 Research Question
Does a statistically meaningful discrimination gap exist between entropy-based UQ signals for binary hallucination detection on HaluEval-QA?

### 2.2 Hypothesis Statement
Under fixed-budget inference conditions, if token_entropy_mean, semantic_entropy, and selfcheckgpt_bertscore_n5 (N=5) are applied to LLaMA-2-7B-chat on 2,000 stratified HaluEval-QA examples, then semantic entropy will achieve statistically significantly higher AUROC (≥ 0.05 difference, non-overlapping 95% bootstrap CIs) than at least one baseline UQ method, because a discrimination gap between UQ methods must exist for the comparative hypothesis to be meaningful.

### 2.3 Scope
- **In scope:** Single model (LLaMA-2-7B-chat), single dataset (HaluEval-QA 2K), three UQ methods, AUROC evaluation
- **Out of scope:** Multi-model comparison (H-M3), causal mechanism analysis (H-M1, H-M2), training

---

## 3. Functional Requirements

### FR-1: Dataset Loading and Preprocessing
- **FR-1.1:** Load HaluEval-QA from HuggingFace `pminervini/HaluEval`, split `qa_samples`
- **FR-1.2:** Stratified sampling: 1,000 hallucinated + 1,000 factual examples, seed=42
- **FR-1.3:** Output: list of 2,000 dicts with `{question, answer, hallucination_label}` fields
- **FR-1.4:** Save dataset sample to disk for reproducibility: `data/halueval_qa_2k.json`

### FR-2: LLM Inference — Greedy Pass
- **FR-2.1:** Load LLaMA-2-7B-chat (`meta-llama/Llama-2-7b-chat-hf`) in float16 on single GPU
- **FR-2.2:** Greedy inference: temperature=0.0, do_sample=False, output_scores=True, max_new_tokens=256
- **FR-2.3:** Save per-example: greedy response text + stacked logit tensor (seq_len, vocab_size)
- **FR-2.4:** Persist to: `outputs/greedy_responses.jsonl` + `outputs/greedy_logits/example_{id}.pt`

### FR-3: LLM Inference — Stochastic Sampling (N=5)
- **FR-3.1:** Stochastic inference: temperature=1.0, do_sample=True, N=5 samples per example
- **FR-3.2:** For SelfCheckGPT: save stochastic samples as plain text passages
- **FR-3.3:** For Semantic Entropy: save stochastic samples as text strings
- **FR-3.4:** Persist to: `outputs/stochastic_samples.jsonl` (list of 5 strings per example)

### FR-4: UQ Signal Computation — token_entropy_mean (Baseline)
- **FR-4.1:** Compute mean token-level Shannon entropy from greedy pass logits
- **FR-4.2:** Formula: `H = mean(-sum(p * log(p+1e-9), dim=-1))` over generated tokens
- **FR-4.3:** Output: one float scalar per example (higher = more uncertain)
- **FR-4.4:** Persist to: `outputs/uq_scores/token_entropy_mean.json`

### FR-5: UQ Signal Computation — semantic_entropy (Proposed)
- **FR-5.1:** Load NLI model: `microsoft/deberta-large-mnli` via HuggingFace pipeline
- **FR-5.2:** Cluster N=5 stochastic samples via bidirectional NLI entailment (Kuhn 2023)
- **FR-5.3:** Compute Shannon entropy over cluster frequency distribution
- **FR-5.4:** Batch NLI inference at batch_size=16 for efficiency
- **FR-5.5:** Output: one float scalar per example
- **FR-5.6:** Persist to: `outputs/uq_scores/semantic_entropy.json`

### FR-6: UQ Signal Computation — selfcheckgpt_bertscore_n5 (Baseline)
- **FR-6.1:** Use official `selfcheckgpt` package (`pip install selfcheckgpt`)
- **FR-6.2:** API: `SelfCheckBERTScore(rescale_with_baseline=True).predict(sentences, sampled_passages)`
- **FR-6.3:** Segment greedy response into sentences; aggregate per-sentence scores by mean
- **FR-6.4:** Output: one float scalar per example (higher = more hallucinated)
- **FR-6.5:** Persist to: `outputs/uq_scores/selfcheckgpt_bertscore_n5.json`

### FR-7: AUROC Evaluation
- **FR-7.1:** Compute AUROC per UQ method vs. HaluEval binary hallucination label
- **FR-7.2:** For token_entropy_mean and semantic_entropy: positive label = higher score = more hallucinated
- **FR-7.3:** For selfcheckgpt_bertscore_n5: positive label = higher inconsistency score
- **FR-7.4:** Use `sklearn.metrics.roc_auc_score`
- **FR-7.5:** Compute 95% bootstrap CI: 1,000 resamples, numpy-based

### FR-8: Statistical Testing
- **FR-8.1:** Compute all 3 pairwise AUROC differences: (SE vs. TE), (SE vs. SCG), (TE vs. SCG)
- **FR-8.2:** Apply Bonferroni correction: α_corrected = 0.05/3 ≈ 0.0167
- **FR-8.3:** Determine CI overlap: non-overlapping 95% CI ↔ significant at corrected level
- **FR-8.4:** MUST_WORK gate check: ≥ 1 pair shows Δ AUROC ≥ 0.05 with non-overlapping CIs

### FR-9: Results Reporting
- **FR-9.1:** Save `results/h_e1_results.json` with per-method AUROC, CI, pairwise differences
- **FR-9.2:** Save `results/h_e1_gate_check.json` with MUST_WORK gate evaluation
- **FR-9.3:** Generate visualizations (see Section 6)

### FR-10: Figure Generation
- **FR-10.1:** Required: Bar chart of AUROC per UQ method with 95% CI error bars (gate metrics)
- **FR-10.2:** Required: ROC Curves Overlay (all 3 methods on same plot with AUC annotation)
- **FR-10.3:** Optional: Bootstrap distribution violin plot per method
- **FR-10.4:** Optional: Score distribution KDE (hallucinated vs. factual, per method)
- **FR-10.5:** Save to: `figures/` directory within hypothesis folder

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | HaluEval-QA (QA Subset) |
| Source | Li et al. 2023 (arXiv:2305.11747) |
| HuggingFace ID | `pminervini/HaluEval` |
| Split | `qa_samples` |
| Total Available | ~10,000 examples |
| Experiment Sample | 2,000 (stratified: 1K hallucinated + 1K factual) |
| Label Type | Binary: True (hallucinated), False (factual) |
| Download Method | `datasets.load_dataset("pminervini/HaluEval", "qa_samples")` |
| Manual Download | NOT required (HuggingFace auto-download) |
| Seed | 42 |

### 4.2 Static Baselines (Reference Datasets)
None — this is an inference-only comparison experiment, no training datasets needed.

### 4.3 Preprocessing Steps
1. Load dataset via HuggingFace `datasets` library
2. Separate by hallucination label
3. Random sample 1,000 from each class with seed=42
4. Shuffle combined sample with seed=42
5. Save to `data/halueval_qa_2k.json`

---

## 5. Model Specifications

### 5.1 Primary LLM: LLaMA-2-7B-chat
- **HuggingFace ID:** `meta-llama/Llama-2-7b-chat-hf`
- **Type:** Decoder-only causal LM, 7B parameters
- **Precision:** float16 (bfloat16 on A100)
- **Device:** Single GPU (CUDA_VISIBLE_DEVICES → empty GPU)
- **Access:** Requires HuggingFace token + Meta access approval

### 5.2 NLI Model: DeBERTa-large-MNLI
- **HuggingFace ID:** `microsoft/deberta-large-mnli`
- **Type:** Sequence classification (3-class NLI)
- **Purpose:** Bidirectional entailment for semantic clustering
- **Usage:** `pipeline("text-classification", model="microsoft/deberta-large-mnli")`

### 5.3 SelfCheckGPT BERTScore
- **Package:** `selfcheckgpt` (pip install)
- **Class:** `SelfCheckBERTScore(rescale_with_baseline=True)`
- **Dependency:** `bert-score` package (auto-installed with selfcheckgpt)

---

## 6. Evaluation Metrics

### 6.1 Primary Metric
- **AUROC** (Area Under ROC Curve) for binary hallucination detection
- Computed for each UQ method independently
- Higher = better discriminator between hallucinated and factual responses

### 6.2 Statistical Metrics
- **95% Bootstrap CI:** N=1,000 resamples using numpy
- **Pairwise AUROC differences:** All 3 pairs with CI bounds
- **Bonferroni-corrected threshold:** α = 0.0167

### 6.3 Gate Metric (MUST_WORK)
- At least 1 pair: Δ AUROC ≥ 0.05 with non-overlapping 95% CIs
- Direction check: semantic_entropy AUROC > token_entropy_mean AUROC

### 6.4 Expected Performance (from literature)
- Semantic entropy on TriviaQA: AUROC ~0.78 (Kuhn 2023)
- Token entropy on factual QA: AUROC ~0.60–0.70 (estimated)
- Expected gap: 0.05–0.15 AUROC units

---

## 7. Non-Functional Requirements

### 7.1 Reproducibility
- **Seed:** 42 for all stochastic operations
- **Persistence:** Save all intermediate outputs (logits, samples, UQ scores)
- **Version pinning:** Exact package versions in `requirements.txt`

### 7.2 Performance
- **Inference budget:** ~4–8 hours on single A100 (2K examples × 6 passes × 7B model)
- **Memory:** LLaMA-2-7B in float16 requires ~14GB VRAM minimum
- **Batching:** NLI inference batch_size=16; LLM batch_size=1 (memory constraint)

### 7.3 Code Quality
- Python 3.9+
- Type hints on all public functions
- Minimum 3 test methods per module with real assertions (no mocks)

---

## 8. Dependencies

### 8.1 Python Packages
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
selfcheckgpt>=0.1.0
bert-score>=0.3.13
scikit-learn>=1.3.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
```

### 8.2 External Repositories (Reference)
- `lorenzkuhn/semantic_uncertainty` — Semantic entropy reference implementation
- `potsawee/selfcheckgpt` — SelfCheckGPT reference implementation (also pip-installable)

### 8.3 HuggingFace Models (Download Required)
- `meta-llama/Llama-2-7b-chat-hf` (requires access token + Meta approval)
- `microsoft/deberta-large-mnli` (public)

---

## 9. Success Criteria

### 9.1 MUST_WORK Gate (Phase 4 Validation)
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Code runs without error | 100% | No uncaught exceptions |
| AUROC comparison computed | All 3 methods | roc_auc_score outputs |
| Pairwise gap exists | Δ AUROC ≥ 0.05 | At least 1 pair |
| Statistical significance | Non-overlapping 95% CI | Bootstrap CI check |

### 9.2 Direction Check
- semantic_entropy AUROC > token_entropy_mean AUROC

---

## 10. Implementation Constraints

- **Single GPU only:** CUDA_VISIBLE_DEVICES must be set to one empty GPU
- **Sequential LLM inference:** batch_size=1 for LLM (7B model memory constraint)
- **Checkpoint strategy:** Save all intermediate outputs to disk; resume from checkpoint if interrupted
- **EXISTENCE scope:** Single model (LLaMA-2-7B-chat) only — multi-model expansion in H-M3

---

*Generated by Phase 3 Implementation Planning (Step 2)*
*Source: h-e1/02c_experiment_brief.md*
*Grounded in: Kuhn 2023 (arXiv:2302.09664), Manakul 2023 (arXiv:2303.08896), Li 2023 (arXiv:2305.11747)*
