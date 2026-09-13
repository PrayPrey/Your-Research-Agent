# Product Requirements Document: H-E1
## Token-Level Log-Probability Aggregation Function Ablation

**stepsCompleted:** prd-v1.0
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis:** H-E1 (EXISTENCE / LIGHT)
**Phase:** 3 - Implementation Planning
**Gate:** MUST_WORK

---

## 1. Executive Summary

This experiment measures whether the choice of token-level log-probability aggregation function (min, mean, raw-sum) produces measurably different AUROC for hallucination detection. We run frozen LLaMA-2-7B and Mistral-7B-v0.1 on three factual QA benchmarks (TriviaQA ~7,000 samples, NQ ~3,600 samples, TruthfulQA 817 samples) using Farquhar 2023 splits. A single greedy forward pass per question extracts per-token log-probabilities; three aggregation functions reduce them to a scalar confidence score; AUROC evaluates each score against binary correctness labels. H-E1 passes if any pairwise AUROC difference ≥ 0.02 with bootstrap 95% CI lower bound > 0.

---

## 2. Problem Statement

Prior hallucination detection literature uses different aggregation functions (min, mean, sum) inconsistently. No systematic within-study comparison exists under identical inference conditions. Establishing whether aggregation choice matters is a prerequisite for downstream mechanism hypotheses (H-M1–H-M3). This is a pure measurement study requiring no training.

---

## 3. Scope

**In scope:**
- Greedy inference pipeline for 2 frozen models × 3 benchmarks (6 combinations)
- Three aggregation functions per (model, question): min, mean, sum
- AUROC, AUPRC, ECE (15-bin) per (model × dataset × aggregation) — 18 primary cells
- Bootstrap 95% CI on all pairwise AUROC differences
- Answer length stratification ablation (T ≤ 5 vs. T > 5 tokens)
- Score distribution histograms and ROC curve visualizations

**Out of scope:**
- Model fine-tuning or gradient computation
- Sampling-based methods (only greedy decoding)
- Models other than LLaMA-2-7B and Mistral-7B-v0.1

---

## 4. Functional Requirements

### FR-1: Dataset Loading

Load all three benchmarks with Farquhar 2023 splits:

| Dataset | Source | Split | Min Samples |
|---------|--------|-------|-------------|
| TriviaQA | `jlko/semantic_uncertainty` `data/trivia_qa_val.jsonl` | test | ~7,000 |
| NQ-Open | `jlko/semantic_uncertainty` `data/nq_open_val.jsonl` | dev | ~3,600 |
| TruthfulQA | `truthful_qa` HF `generation` config | full validation | 817 |

Preprocessing:
- Prompt: `"Q: {question}\nA:"` (zero-shot, no system prompt)
- Answer extraction: greedy decoded tokens until first newline or max 50 tokens; strip whitespace
- TriviaQA/NQ labels: binary exact-match/F1 via Farquhar 2023 reference answers
- TruthfulQA labels: ROUGE-L ≥ 0.3 vs. reference best answer → correct (1), else hallucinated (0)
- Exclusion: questions with no reference answer in Farquhar splits

### FR-2: Model Loading

| Model | HF Identifier | Precision |
|-------|--------------|-----------|
| LLaMA-2-7B | `meta-llama/Llama-2-7b-hf` | fp16 |
| Mistral-7B-v0.1 | `mistralai/Mistral-7B-v0.1` | fp16 |

Settings: frozen (no gradient), single GPU ≥16 GB VRAM, `torch_dtype=torch.float16`, Flash Attention 2 if available.

### FR-3: Log-Probability Extraction

Single forward pass greedy decoding via `model.generate()`:
- `do_sample=False`, `temperature=1.0`, `max_new_tokens=50`
- `return_dict_in_generate=True`, `output_scores=True`
- Token log-probs: `log_softmax(scores[t], dim=-1)[0, token_ids[t]]` for each generated step t
- Batch size: 1 (avoids padding artifacts)
- Exclusion: answers with T < 1 generated token (empty generation)

### FR-4: Aggregation Functions (Core Ablation)

Three scalar confidence scores from token log-prob sequence `[lp_1, ..., lp_T]`:

| Method | Formula | Notes |
|--------|---------|-------|
| `min` | `min(lp_1...lp_T)` | Most uncertain single token |
| `mean` | `mean(lp_1...lp_T)` | Average token log-prob (avg NLL negated) |
| `sum` | `sum(lp_1...lp_T)` | Raw sequence log-prob (length-biased) |

Scores are negated before AUROC (higher negated score = more uncertain = predicted hallucinated).

### FR-5: Primary Metrics

Per (model × dataset × aggregation) cell — 18 cells total:

| Metric | Implementation |
|--------|---------------|
| AUROC | `sklearn.metrics.roc_auc_score(labels, scores)` |
| AUPRC | `sklearn.metrics.average_precision_score(labels, scores)` |
| ECE (15-bin) | `sklearn.calibration.calibration_curve` after Platt scaling |

### FR-6: Pairwise AUROC Differences + Bootstrap CI

For each (model × dataset) pair, compute 3 pairwise differences:
- AUROC(min) − AUROC(mean)
- AUROC(min) − AUROC(sum)
- AUROC(mean) − AUROC(sum)

Bootstrap: percentile method, n=1000 resamples, 95% CI via `scipy.stats.bootstrap`.

### FR-7: Ablation — Answer Length Stratification

Split answers into short (T ≤ 5 tokens) and long (T > 5 tokens). Recompute AUROC per aggregation function per stratum. Controls for `sum` length bias.

### FR-8: Visualizations

- ROC curves per (model × dataset) with all 3 aggregation methods overlaid
- Score histograms per (model × dataset × aggregation) split by correctness label

Saved to `docs/youra_research/h-e1/figures/`.

### FR-9: Results Persistence

| Artifact | Path |
|----------|------|
| Raw scores | `h-e1/results/scores_{model}_{dataset}.npz` |
| AUROC table | `h-e1/results/auroc_table.csv` |
| CI table | `h-e1/results/bootstrap_ci_table.csv` |
| Gate decision | `h-e1/results/gate_decision_h-e1.md` |

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Fixed seed=42; record HF model commit hashes |
| Performance | Full TriviaQA+NQ inference per model ≤ 2h on single A100/H100 |
| Memory | ≤14 GB VRAM per model (fp16 7B) |
| Correctness | All 18 AUROC cells populated; bootstrap CI for all 9 pairwise differences per model |

---

## 6. Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| H-E1 pass | ≥1 pairwise AUROC diff ≥ 0.02 with CI lower bound > 0 | MUST_WORK |
| Absolute floor | ≥1 method AUROC > 0.55 on ≥1 dataset for ≥1 model | Sanity check |

**Failure protocol:** If gate fails → run N=5 sampling entropy sanity check on 10% TriviaQA; check for implementation bugs via 10-sample dry run; route to Phase 2A redesign.

---

## 7. Data Specification

### 7.1 Python Packages

```
transformers>=4.40.0
datasets>=2.18.0
torch>=2.2.0
scikit-learn>=1.4.0
scipy>=1.11.0
numpy>=1.26.0
rouge-score>=0.1.2
matplotlib>=3.8.0
accelerate>=0.29.0
```

### 7.2 External Repositories

| Repository | Usage |
|------------|-------|
| `jlko/semantic_uncertainty` | Farquhar 2023 TriviaQA/NQ splits with binary labels |

Download: `git clone https://github.com/jlko/semantic_uncertainty` and read `data/trivia_qa_val.jsonl` and `data/nq_open_val.jsonl`.

---

## 8. Constraints

- HF token required for LLaMA-2-7B (gated model)
- Batch size = 1 mandatory (log-prob extraction correctness)
- No internet during GPU compute (pre-download all models and data)
- TruthfulQA loaded from HF hub standard split (no Farquhar split needed)
