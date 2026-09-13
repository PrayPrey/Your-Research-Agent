# Product Requirements Document: H-E1
# Epistemic Reliability as a Latent Dimension — Existence Proof

**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)
**Phase:** 3 — Implementation Planning
**Date:** 2026-04-30
**Author:** Anonymous
**Source:** h-e1/02c_experiment_brief.md

---

## Executive Summary

This experiment tests whether five LLM trustworthiness metrics (ECE, Brier score, TruthfulQA%, AdvGLUE drop, ANLI drop) share a common latent structure ("epistemic reliability") across a population of N=30 open-weight instruction-tuned LLMs. The study computes a partial Spearman correlation matrix controlling for MMLU accuracy and runs factor analysis to detect a stable latent factor. This is a **population-level empirical study**, not a model-training experiment.

**Success Gate (MUST_WORK):** Partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40 AND partial ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40, with BCa 95% CIs excluding zero.

---

## 1. Problem Statement

### 1.1 Research Gap

Prior work (DecodingTrust, TrustLLM) reports moderate cross-property correlations, but no study has:
1. Applied partial correlation controlling for capability (MMLU accuracy)
2. Tested factor stability across decoding regimes (greedy vs. T=0.7)
3. Evaluated whether a single latent dimension explains the cross-property covariance

### 1.2 Hypothesis to Test

> Under N≈30 instruction-tuned open-weight LLMs (7B–70B, ≥3 families), partial Spearman correlations across (ECE, Brier, TruthfulQA%, AdvGLUE drop, ANLI drop | MMLU acc) satisfy |ρ| ≥ 0.40 with BCa 95% CI excluding zero for ECE-TruthfulQA% and ECE-AdvGLUE drop pairs; and factor analysis extracts ≥1 stable factor (Tucker's congruence ≥ 0.85 across greedy vs. T=0.7).

---

## 2. Scope

### 2.1 In Scope
- Evaluation of N=30 LLMs on 5 benchmarks via lm-evaluation-harness v0.4.x
- ECE + Brier computation from MMLU logits (greedy + stochastic T=0.7)
- Partial Spearman correlation analysis with BCa bootstrap (10,000 resamples)
- Factor analysis (ML estimation, promax rotation) + Tucker's congruence
- LOO logistic regression for secondary predictive validity check
- Visualization: heatmap, loading plot, scatter plots

### 2.2 Out of Scope
- Model fine-tuning or training
- New benchmark creation
- Models not in the specified 30-model population
- Parameter-count regression analysis

---

## 3. Functional Requirements

### FR-1: Model Evaluation Pipeline

**FR-1.1:** Run lm-evaluation-harness v0.4.x on all 30 models for tasks: `mmlu`, `truthfulqa_mc1`, `adv_glue`, `anli_r3`, `humaneval`
- Greedy decoding: `temperature=0`, `seed=42`
- Stochastic: `temperature=0.7`, seeds 42, 123, 456 (3-run average)
- Flag `--log_samples` to save per-sample logits for ECE computation
- Output: `results/{model_name}/` JSON files per model

**FR-1.2:** Handle GPU memory constraints:
- 7B–13B models: float16, single GPU
- 30B–40B: float16 + tensor parallel or bitsandbytes 4-bit
- 70B: `load_in_4bit=True` via bitsandbytes

**FR-1.3:** All 30 models must be evaluated; partial results constitute failure.

### FR-2: Calibration Metric Computation

**FR-2.1:** Compute ECE from MMLU `--log_samples` output:
- Extract per-sample logits over 4 answer tokens
- Normalize to probabilities; confidence = max probability
- ECE via `netcal.metrics.ECE(n_bins=10).measure(confidences, correctness)`

**FR-2.2:** Compute Brier score:
- `brier = mean((confidence − correctness)²)` per model, averaged over MMLU questions

**FR-2.3:** Output: per-model ECE and Brier scalar values

### FR-3: Score Matrix Assembly

**FR-3.1:** Assemble N×6 pandas DataFrame with columns:
`[model_id, ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1]`

**FR-3.2:** AdvGLUE_drop = standard GLUE accuracy − adversarial AdvGLUE accuracy (per model)

**FR-3.3:** ANLI_drop = ANLI R1+R2 average accuracy − ANLI R3 accuracy (proxy for adversarial degradation)

**FR-3.4:** Stochastic metrics = average over 3 seeds (42, 123, 456) per model

### FR-4: Statistical Analysis — Partial Correlation

**FR-4.1:** Compute 5×5 partial Spearman correlation matrix controlling for MMLU_acc using `pingouin.partial_corr(data, x, y, covar='MMLU_acc', method='spearman')`

**FR-4.2:** BCa bootstrap CI (10,000 resamples) for each correlation pair
- Report: ρ, CI_low, CI_high, p_value

**FR-4.3:** Identify pairs satisfying gate condition: |ρ| ≥ 0.40 AND CI excludes zero

### FR-5: Statistical Analysis — Factor Analysis

**FR-5.1:** Run FactorAnalyzer on 5-indicator set (ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop):
- n_factors=1 (primary test), ML estimation, promax rotation
- Inputs: greedy score matrix, stochastic (averaged) score matrix separately

**FR-5.2:** Compute Tucker's congruence coefficient between greedy and stochastic factor loadings
- `factor_analyzer.utils.calculate_tucker_congruence(loadings_greedy, loadings_stochastic)`
- Gate: congruence ≥ 0.85

**FR-5.3:** Record: factor loadings, variance explained, KMO adequacy measure

### FR-6: Secondary Analysis — LOO Prediction

**FR-6.1:** LOO logistic regression: predict top-quartile AdvGLUE failure from (ECE, TruthfulQA_pct, Brier) composite
- sklearn `LogisticRegressionCV` with leave-one-out CV
- Report AUC; compare vs. MMLU-only baseline

### FR-7: Visualization

**FR-7.1 (Mandatory):** Gate metrics bar chart — partial ρ values vs. 0.40 threshold for all 10 pairs, with BCa CI error bars

**FR-7.2:** Partial correlation heatmap (5×5 with significance stars)

**FR-7.3:** Factor loadings bar chart (with HumanEval highlighted)

**FR-7.4:** Tucker's congruence side-by-side loading plot

**FR-7.5:** Model family scatter: ECE vs. TruthfulQA_pct colored by family

**FR-7.6:** Decoding invariance scatter: greedy vs. T=0.7 partial ρ values

All figures saved to `h-e1/figures/`.

### FR-8: Results Reporting

**FR-8.1:** Generate `h-e1/04_results.json` with:
- Per-model score matrix
- Full partial correlation matrix (ρ, CI, p-values)
- Factor analysis results (loadings, variance explained, congruence)
- Gate evaluation: PASS/FAIL with observed values

**FR-8.2:** Generate `h-e1/04_validation.md` summary report

---

## 4. Data Specification

### 4.1 Benchmarks (All via lm-evaluation-harness — Auto-Download)

| Benchmark | lm-eval Task | Questions | Split | Download |
|-----------|-------------|-----------|-------|----------|
| MMLU | `mmlu` | 14,042 | test (full) | Auto via HuggingFace |
| TruthfulQA | `truthfulqa_mc1` | 817 | test (full) | Auto via HuggingFace |
| AdvGLUE | `adv_glue` | ~1,000 | test (full) | Auto via HuggingFace |
| ANLI | `anli_r3` | 1,200 | test (full) | Auto via HuggingFace |
| HumanEval | `humaneval` | 164 | test (full) | Auto via HuggingFace |

**No manual dataset downloads required** — all auto-downloaded by lm-evaluation-harness.

### 4.2 Model Population (N=30)

All loaded via `lm_eval --model hf --model_args pretrained={hf_id},dtype=float16`:

| # | HuggingFace ID | Params | Family |
|---|----------------|--------|--------|
| 1 | meta-llama/Llama-2-7b-chat-hf | 7B | LLaMA-2 |
| 2 | meta-llama/Llama-2-13b-chat-hf | 13B | LLaMA-2 |
| 3 | meta-llama/Llama-2-70b-chat-hf | 70B | LLaMA-2 |
| 4 | mistralai/Mistral-7B-Instruct-v0.1 | 7B | Mistral |
| 5 | mistralai/Mistral-7B-Instruct-v0.2 | 7B | Mistral |
| 6 | mistralai/Mistral-7B-Instruct-v0.3 | 7B | Mistral |
| 7 | mistralai/Mixtral-8x7B-Instruct-v0.1 | 46.7B | Mistral |
| 8 | tiiuae/falcon-7b-instruct | 7B | Falcon |
| 9 | tiiuae/falcon-40b-instruct | 40B | Falcon |
| 10 | EleutherAI/pythia-6.9b-deduped | 6.9B | Pythia |
| 11 | EleutherAI/pythia-12b-deduped | 12B | Pythia |
| 12 | Qwen/Qwen-7B-Chat | 7B | Qwen |
| 13 | Qwen/Qwen-14B-Chat | 14B | Qwen |
| 14 | Qwen/Qwen1.5-7B-Chat | 7B | Qwen |
| 15 | 01-ai/Yi-6B-Chat | 6B | Yi |
| 16 | 01-ai/Yi-34B-Chat | 34B | Yi |
| 17 | allenai/OLMo-7B-Instruct | 7B | OLMo |
| 18 | google/gemma-2b-it | 2B | Gemma |
| 19 | google/gemma-7b-it | 7B | Gemma |
| 20 | microsoft/phi-2 | 2.7B | Phi |
| 21 | microsoft/Phi-3-mini-4k-instruct | 3.8B | Phi |
| 22 | mosaicml/mpt-7b-instruct | 7B | MPT |
| 23 | mosaicml/mpt-30b-instruct | 30B | MPT |
| 24 | HuggingFaceH4/zephyr-7b-beta | 7B | Zephyr |
| 25 | lmsys/vicuna-7b-v1.5 | 7B | LLaMA-2 |
| 26 | lmsys/vicuna-13b-v1.5 | 13B | LLaMA-2 |
| 27 | teknium/OpenHermes-2.5-Mistral-7B | 7B | Mistral |
| 28 | berkeley-nest/Starling-LM-7B-alpha | 7B | LLaMA-2 |
| 29 | upstage/SOLAR-10.7B-Instruct-v1.0 | 10.7B | LLaMA-2 |
| 30 | microsoft/Orca-2-13b | 13B | LLaMA-2 |

### 4.3 Preprocessing

- **MMLU:** 4-way MC; log-softmax over 4 answer tokens; normalize to probs; confidence = max prob
- **TruthfulQA MC1:** Binary correct/incorrect; top-1 log-prob as confidence
- **AdvGLUE:** Evaluate standard + adversarial; drop = std_acc − adv_acc
- **ANLI R3:** 3-way NLI accuracy on adversarial set
- **HumanEval:** Pass@1 via lm-eval (discriminant validity control)

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All evaluations use fixed seeds (greedy: seed=42; stochastic: seeds 42, 123, 456)
- lm-evaluation-harness v0.4.x pinned version
- Results saved to JSON with full configuration metadata

### NFR-2: Compute Efficiency
- Models evaluated sequentially per GPU slot to avoid memory conflicts
- 4-bit quantization for 40B+ models
- `--batch_size 8` for 7B–13B; `--batch_size 4` for 30B+; `--batch_size 1` for 70B

### NFR-3: Error Handling
- Failed model evaluations logged and flagged; pipeline continues with remaining models
- Minimum 25/30 models required for valid statistical analysis (N < 25 → stop and report)

### NFR-4: Storage
- Results per model: ~50–200MB JSON (log_samples enabled)
- Total: ~5–6GB for 30 models × 2 decoding conditions

---

## 6. Success Criteria

### 6.1 Primary Gate (MUST_WORK)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| partial ρ(ECE, TruthfulQA% \| MMLU) | ≥ 0.40 | pingouin.partial_corr, Spearman |
| partial ρ(ECE, AdvGLUE drop \| MMLU) | ≥ 0.40 | pingouin.partial_corr, Spearman |
| Both BCa 95% CIs | Exclude zero | 10,000 bootstrap resamples |

### 6.2 Secondary (Informative)

| Criterion | Threshold |
|-----------|-----------|
| Factor variance explained (1st factor) | ≥ 50% |
| Tucker's congruence (greedy vs. T=0.7) | ≥ 0.85 |
| HumanEval loading on epistemic factor | < 0.40 |
| LOO AUC vs. MMLU-only | ΔAUC > 0 |

### 6.3 Failure Gate

If partial ρ(ECE, TruthfulQA% | MMLU) < 0.20 AND partial ρ(ECE, AdvGLUE drop | MMLU) < 0.20: document as null result, STOP pipeline, do not proceed to H-M1/M2/M3.

---

## 7. Dependencies

### 7.1 Python Packages

```
lm_eval>=0.4.0
transformers>=4.36.0
torch>=2.0.0
accelerate>=0.24.0
bitsandbytes>=0.41.0
netcal>=1.3.0
pingouin>=0.5.3
factor_analyzer>=0.4.1
scipy>=1.11.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
```

### 7.2 External Repositories

- EleutherAI/lm-evaluation-harness v0.4.x (primary evaluation framework)
- HuggingFace model hub (model weights — downloaded on demand)
- HuggingFace datasets (benchmark data — auto-downloaded by lm-eval)

### 7.3 Hardware Requirements

- Minimum: 1× A100 40GB GPU (evaluates up to 13B float16)
- Recommended: 2–4× A100 40GB GPUs for parallel model evaluation
- Storage: ~50GB for model weights cache + ~10GB for results

---

## 8. Implementation Notes

### 8.1 No Model Training
This is a pure evaluation + statistical analysis study. No gradient computation, no optimizer, no training loop.

### 8.2 lm-eval as Primary Interface
All benchmark evaluation goes through lm-evaluation-harness. Custom code is only for:
1. ECE/Brier extraction from lm-eval `--log_samples` JSON output
2. Statistical analysis (partial correlation, factor analysis)
3. Visualization

### 8.3 Parallelization Strategy
- Sequential per-model evaluation on available GPUs
- Can parallelize: multiple models on separate GPUs simultaneously
- Stochastic runs (3 seeds) can run in parallel if 3+ GPUs available

---

## stepsCompleted
- [x] Executive Summary
- [x] Problem Statement
- [x] Functional Requirements (FR-1 through FR-8)
- [x] Data Specification (4 benchmarks, N=30 model population)
- [x] Non-Functional Requirements
- [x] Success Criteria (primary gate + secondary)
- [x] Dependencies
