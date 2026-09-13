# PRD: H-E1 — Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17
**Phase 2C Source:** `h-e1/02c_experiment_brief.md`
**Gate:** MUST_WORK — β₁ < 0, p < 0.005, AUROC ≥ 0.75 cross-benchmark

---

## 1. Executive Summary

This PoC experiment validates whether pre-alignment confidence margin (top-1 minus top-2 log-probability, z-scored) in base LLMs predicts post-alignment argmax inversion probability. It is a pure inference + statistical analysis pipeline — no training. Success confirms the foundational existence claim required by downstream hypotheses H-M1 through H-M4.

**Scope:** Inference-only analysis on existing model pairs. ~16K MCQ items × 5 models.

---

## 2. Problem Statement

**Question:** Does a low pre-alignment confidence margin causally correlate with higher post-alignment argmax flip probability?

**Current State:** No published work directly measures this margin→flip relationship with statistical rigor across multiple benchmarks and model families.

**Success Condition:** Logistic regression β₁ < 0 (p < 0.005) and cross-benchmark AUROC ≥ 0.75.

---

## 3. Goals and Non-Goals

### Goals
- Extract MCQ log-probabilities from base and aligned model pairs
- Compute confidence margin (z-scored within model pair) and argmax flip indicators
- Fit logistic regression: `logit P(flip) = β₀ + β₁·margin + β₄·KL`
- Report β₁, p-value, AUROC on primary (MMLU) and cross-benchmark (TruthfulQA, ARC)
- Generate figures: margin quintile flip rates, ROC curves, margin distribution by method

### Non-Goals
- No model training or fine-tuning
- No hyperparameter search
- No ablation variants (EXISTENCE PoC only)
- No comparison between PPO vs DPO (that is H-M2–H-M4)

---

## 4. Functional Requirements

### FR-1: Data Loading
- Load MMLU full test set (14,042 items) from `cais/mmlu` — all 57 subjects
- Load TruthfulQA MC1 validation set (817 items) from `truthful_qa`
- Load ARC-Challenge test set (1,172 items) from `allenai/ai2_arc`
- Format each item as MCQ prompt: `"Question: {q}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer:"`
- Extract log-probabilities for option tokens A/B/C/D at final token position

### FR-2: Model Inference
- Load model pairs via `AutoModelForCausalLM.from_pretrained()` with `torch_dtype=torch.float16, device_map="auto"`
- Model pairs:
  - Pair-1: `allenai/tulu-2-7b` (base) → `allenai/tulu-2-ppo-7b` (aligned, PPO)
  - Pair-2: `allenai/tulu-2-7b` (base) → `allenai/tulu-2-dpo-7b` (aligned, DPO)
  - Pair-3: `EleutherAI/pythia-1.4b` (base) → aligned Pythia-1.4B variant
  - Pair-4: `EleutherAI/pythia-6.9b` (base) → aligned Pythia-6.9B variant
- Extract `outputs.logits[0, -1, option_token_ids]` for each MCQ item
- Apply `log_softmax` over 4 option tokens

### FR-3: Metric Computation
- Confidence margin: `margin_raw = sorted_logprobs[:,0] - sorted_logprobs[:,1]`, then z-score within model pair using `scipy.stats.zscore`
- Flip indicator: `flip = (argmax(base_logprobs) != argmax(aligned_logprobs)).astype(int)`
- KL divergence control: `KL(base||aligned) = sum(softmax(base_4) * log(softmax(base_4)/softmax(aligned_4)))`

### FR-4: Statistical Analysis
- Fit logistic regression: `LogisticRegression().fit(X=[margin_z, kl_div], y=flip)`
- Compute AUROC: `roc_auc_score(flip, lr.predict_proba(X)[:,1])`
- Cross-benchmark evaluation: train on MMLU, evaluate on TruthfulQA + ARC-Challenge
- Apply Bonferroni correction: threshold p < 0.005 (adequate for 4 pairs × 3 benchmarks)
- Report per model pair: β₁, β₁ p-value (Wald test), AUROC, 95% CI

### FR-5: Visualization
- **Figure 1 (Gate Metrics):** Bar chart — β₁ value, AUROC (target vs actual), p-value marker
- **Figure 2 (Quintile Flip Rate):** 5-bin bar chart of P(flip|margin quintile) for each model pair
- **Figure 3 (ROC Curves):** Per model pair + cross-benchmark generalization
- **Figure 4 (Margin Distribution):** Box plots margin dist for flipped vs non-flipped items
- Save to: `h-e1/figures/`

### FR-6: Pipeline Verification
- Implement `verify_pipeline_activated()` checking:
  - `logprobs_extracted`: shape[0] > 1,000
  - `margin_variable`: std > 0.1
  - `flip_occurs`: mean > 0.05
  - `negative_beta`: β₁ < 0
  - `auroc_above_chance`: AUROC > 0.55

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: `seed=42`; inference is deterministic (no sampling)
- All models loaded in float16; no quantization

### NFR-2: Performance
- Single GPU (float16); ~70K forward passes total
- Estimated: 2–4 hours per model; 20–40 GPU-hours total
- Batch size: 1 (simplest, deterministic)

### NFR-3: Storage
- Cache models locally in `~/.cache/huggingface/` (auto-default)
- Output logprobs as `.npy` files: `h-e1/cache/{model_id}_logprobs.npy`
- Figures as `.pdf` and `.png`

---

## 6. Success Criteria (Gate Conditions)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Direction | β₁ < 0 | Logistic regression coefficient |
| Significance | p < 0.005 | Two-sided Wald test |
| Predictive power | AUROC ≥ 0.75 | Cross-benchmark (TruthfulQA or ARC) |
| Effect size | Partial η² ≥ 0.06 | From logistic regression |

**PoC Pass:** All 3 primary criteria satisfied on at least one aligned model pair.

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
pyyaml>=6.0
statsmodels>=0.14.0
```

### 7.2 External Reference Repositories

- **EleutherAI/lm-evaluation-harness** — reference for MCQ log-prob extraction methodology
- **allenai/open-instruct** — reference for Tulu-2 PPO/DPO model cards and base checkpoint info

### 7.3 HuggingFace Model IDs

| Model | HuggingFace ID |
|-------|----------------|
| Tulu-2 Base | `allenai/tulu-2-7b` |
| Tulu-2 PPO | `allenai/tulu-2-ppo-7b` |
| Tulu-2 DPO | `allenai/tulu-2-dpo-7b` |
| Pythia-1.4B | `EleutherAI/pythia-1.4b` |
| Pythia-6.9B | `EleutherAI/pythia-6.9b` |

### 7.4 HuggingFace Dataset IDs

| Dataset | HuggingFace ID | Config | Split |
|---------|----------------|--------|-------|
| MMLU | `cais/mmlu` | `all` | `test` |
| TruthfulQA | `truthful_qa` | `multiple_choice` | `validation` |
| ARC-Challenge | `allenai/ai2_arc` | `ARC-Challenge` | `test` |

---

## 8. Traceability

| Requirement | Source |
|-------------|--------|
| Datasets + sizes | Phase 2C §Dataset |
| Model pairs | Phase 2C §Models |
| Margin formula | Phase 2C §Core Mechanism |
| Logistic regression + AUROC | Phase 2C §Statistical Analysis Config |
| Success thresholds | Phase 2C §Success Criteria |
| Figures | Phase 2C §Visualization Requirements |
