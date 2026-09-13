# Experiment Brief: H-E1 — Token-Level Log-Probability Aggregation Function Ablation

**Date:** 2026-08-21  
**Hypothesis ID:** H-E1 (sub-hypothesis of H-TokenAgg-v1)  
**Gate Type:** MUST_WORK  
**Phase:** 2C — Experiment Design  

---

## 1. Hypothesis Statement

**H-E1:** Under frozen open-weight LLMs (LLaMA-2-7B, Mistral-7B-v0.1) with single greedy forward pass, if we vary only the token-level log-probability aggregation function (min, mean, raw-sum) on factual QA benchmarks (TriviaQA, NQ, TruthfulQA; Farquhar 2023 splits), then AUROC for hallucination detection will differ by ≥ 0.02 between at least one pair of aggregation functions on at least one benchmark, because different aggregation functions have different mathematical sensitivities to token-level uncertainty distributions.

**Gate:** MUST_WORK — if H-E1 fails, stop pipeline; investigate assumptions A3/A4/A5.

---

## 2. Dataset Specification

All datasets are real, public benchmarks. No synthetic data is used.

### 2.1 TriviaQA

| Property | Value |
|----------|-------|
| Source | Farquhar et al. 2023 splits (`jlko/semantic_uncertainty` repository) |
| Split | Test split (Farquhar 2023 selection) |
| Size | ~7,000 samples |
| Labels | Binary correctness via exact-match/F1 against reference answers |
| HuggingFace ID | `trivia_qa` (filtered by Farquhar splits) |
| Hallucination definition | Exact-match = 0 → hallucinated; = 1 → correct |
| Answer type | Short factual entities (recall-failure hallucination type) |

### 2.2 Natural Questions (NQ)

| Property | Value |
|----------|-------|
| Source | Farquhar et al. 2023 splits (`jlko/semantic_uncertainty` repository) |
| Split | Dev split (Farquhar 2023 selection) |
| Size | ~3,600 samples |
| Labels | Binary correctness via exact-match/F1 |
| HuggingFace ID | `nq_open` (filtered by Farquhar splits) |
| Hallucination definition | Same as TriviaQA |
| Answer type | Short factual entities (recall-failure hallucination type) |

### 2.3 TruthfulQA

| Property | Value |
|----------|-------|
| Source | Standard HuggingFace hub |
| Split | Generation subset (full) |
| Size | 817 questions |
| Labels | Binary correctness from reference best/correct answers via ROUGE-L ≥ 0.3 (following standard evaluation) |
| HuggingFace ID | `truthful_qa` config `generation` |
| Hallucination definition | ROUGE-L < 0.3 vs. reference best answer → hallucinated |
| Answer type | Imitative falsehoods (flat high-confidence wrong answers) |

### 2.4 Preprocessing

- **Prompt format:** Standard zero-shot QA prompt: `"Q: {question}\nA:"` (no system prompt, no few-shot)
- **Tokenization:** Each model's native tokenizer; no truncation of questions (all fit within 512 tokens)
- **Answer extraction:** Greedy decoded tokens until first newline or max 50 tokens; strip leading/trailing whitespace
- **Exclusions:** Questions with no reference answer in the Farquhar 2023 split are excluded

**Minimum sample counts (all met):**
- TriviaQA: ~7,000 ≥ 500 ✓
- NQ: ~3,600 ≥ 500 ✓
- TruthfulQA: 817 ≥ 500 ✓

---

## 3. Model Architecture

### 3.1 Models

| Model | Source | Parameters | VRAM Required |
|-------|--------|------------|---------------|
| LLaMA-2-7B-hf | `meta-llama/Llama-2-7b-hf` | 7B | ~14 GB (fp16) |
| Mistral-7B-v0.1 | `mistralai/Mistral-7B-v0.1` | 7B | ~14 GB (fp16) |

Both models are used **frozen** (no gradient updates, no fine-tuning).

### 3.2 Log-Probability Extraction

- **Inference mode:** Single forward pass, greedy decoding (`do_sample=False`, `temperature=1.0`)
- **Log-prob source:** `scores` output from `model.generate(..., return_dict_in_generate=True, output_scores=True)`
- **Token log-probs:** `log_softmax(scores[t], dim=-1)[generated_token_id]` at each generation step `t`
- **Sequence:** A sequence of `T` log-probs `[lp_1, lp_2, ..., lp_T]` where `T` = answer length in tokens
- **Minimum length filter:** Exclude answers with T < 1 token (empty generation)

---

## 4. Core Mechanism Pseudo-Code

```python
import torch
import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.stats import bootstrap

def extract_token_logprobs(model, tokenizer, prompt, max_new_tokens=50):
    """Single forward pass; returns list of log-probs for generated tokens."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
        )
    token_ids = out.sequences[0, inputs.input_ids.shape[1]:]  # generated only
    logprobs = [
        torch.log_softmax(out.scores[t], dim=-1)[0, token_ids[t]].item()
        for t in range(len(out.scores))
    ]
    return logprobs  # list of floats, all <= 0


def aggregate(logprobs, method):
    """Three aggregation functions under comparison."""
    lp = np.array(logprobs)
    if method == "min":
        return float(np.min(lp))       # most uncertain single token
    elif method == "mean":
        return float(np.mean(lp))      # average token log-prob (= avg NLL negated)
    elif method == "sum":
        return float(np.sum(lp))       # raw sequence log-prob (length-biased)
    raise ValueError(f"Unknown method: {method}")


def run_evaluation(samples, model, tokenizer, method):
    """Returns scores and binary labels for AUROC computation."""
    scores, labels = [], []
    for q, ref_answer, correct in samples:
        prompt = f"Q: {q}\nA:"
        lp = extract_token_logprobs(model, tokenizer, prompt)
        if len(lp) == 0:
            continue
        # Negate: higher score = more confident = less likely hallucination
        scores.append(-aggregate(lp, method))
        labels.append(int(correct))
    return np.array(scores), np.array(labels)


def bootstrap_auroc_diff(scores_a, scores_b, labels, n_resamples=1000):
    """Bootstrap 95% CI on AUROC(a) - AUROC(b)."""
    def diff_stat(idx):
        idx = idx.astype(int)
        return (roc_auc_score(labels[idx], scores_a[idx])
                - roc_auc_score(labels[idx], scores_b[idx]))
    res = bootstrap((np.arange(len(labels)),), diff_stat,
                    n_resamples=n_resamples, confidence_level=0.95,
                    method="percentile")
    return res.confidence_interval
```

**Key design decisions:**
- Scores are negated before AUROC: lower (more negative) log-prob = higher uncertainty = more likely hallucinated → after negation, higher score = more hallucinated (AUROC convention)
- `sum` is length-biased; this is intentional — it is the raw sequence log-prob used as baseline by Farquhar 2023's predictive entropy (before semantic clustering)
- Bootstrap uses percentile method, n=1000 resamples

---

## 5. Training Protocol (Inference Only)

No training is performed. All models are loaded frozen from HuggingFace hub.

### 5.1 Forward Pass Details

| Setting | Value |
|---------|-------|
| Decoding | Greedy (`do_sample=False`) |
| Temperature | 1.0 (no scaling applied to logits before log-softmax) |
| Max new tokens | 50 |
| Batch size | 1 (to avoid padding artifacts in log-prob extraction) |
| Precision | fp16 (`torch_dtype=torch.float16`) |
| Device | CUDA (single GPU, ≥16 GB VRAM) |
| Attention | Flash Attention 2 if available (speed only; no effect on log-probs) |

### 5.2 Compute Estimate

| Task | Samples | Time/sample (est.) | Total |
|------|---------|-------------------|-------|
| TriviaQA × 2 models | 14,000 | ~0.3s | ~1.2h |
| NQ × 2 models | 7,200 | ~0.3s | ~0.6h |
| TruthfulQA × 2 models | 1,634 | ~0.3s | ~0.15h |
| **Total** | **22,834** | | **~2h** |

---

## 6. Evaluation Metrics

### 6.1 Primary Metric: AUROC

- **Definition:** Area under the ROC curve treating "hallucinated" as positive class
- **Score direction:** Higher aggregation score (negated log-prob) = predicted hallucinated
- **Implementation:** `sklearn.metrics.roc_auc_score(labels, scores)`
- **Reported per:** (model × dataset × aggregation_function) → 2 × 3 × 3 = 18 AUROC values

### 6.2 Secondary Metrics

| Metric | Purpose | Implementation |
|--------|---------|----------------|
| AUPRC | Handles class imbalance (TruthfulQA may be ~50/50; TriviaQA/NQ may be ~40-60% wrong) | `sklearn.metrics.average_precision_score` |
| ECE (15 bins) | Calibration quality of the aggregated scores after Platt scaling | `sklearn.calibration.calibration_curve` |
| Bootstrap 95% CI | Statistical significance of pairwise AUROC differences | Percentile bootstrap, n=1000 |

### 6.3 Pairwise Comparisons

For each (model, dataset) pair, compute all 3 pairwise AUROC differences:
- AUROC(min) − AUROC(mean)
- AUROC(min) − AUROC(sum)
- AUROC(mean) − AUROC(sum)

Report bootstrap 95% CI lower bound for each. H-E1 passes if any CI lower bound > 0 with |difference| ≥ 0.02.

---

## 7. Ablation Studies

### 7.1 Aggregation Function × Dataset

Primary ablation — the core of H-E1:

| Aggregation | TriviaQA AUROC | NQ AUROC | TruthfulQA AUROC |
|-------------|---------------|----------|------------------|
| min | ? | ? | ? |
| mean | ? | ? | ? |
| sum | ? | ? | ? |

Report for each model separately; then averaged across models.

### 7.2 Per-Model Breakdown

Compare LLaMA-2-7B vs. Mistral-7B-v0.1 for each (aggregation × dataset) cell. Replication across model families strengthens the existence claim.

### 7.3 Answer Length Stratification

Split answers into short (T ≤ 5 tokens) vs. long (T > 5 tokens) and recompute AUROC per aggregation function. This controls for length bias in `sum` aggregation and verifies that `min` advantage (if observed) is not an artifact of short answers.

### 7.4 Score Distribution Visualization

For each (model, dataset, aggregation), plot:
- Score histogram split by correct/hallucinated groups
- ROC curve with CI band

---

## 8. Success Criteria

### 8.1 H-E1 Gate Condition (MUST_WORK)

**Pass if:** At least one pairwise AUROC difference ≥ 0.02 with bootstrap 95% CI lower bound > 0, across any (aggregation pair × dataset × model) combination.

**Interpretation:** Existence of meaningful differences in aggregation function AUROC is established. Downstream mechanism hypotheses (H-M1–H-M3) proceed.

**Fail if:** All 18 pairwise differences have CI including 0 or |difference| < 0.02.

**On failure:** STOP — investigate:
1. A3 (greedy log-probs uninformative): run N=5 sample-based entropy as sanity check on 10% of TriviaQA
2. A4 (label noise): check if best AUROC across all methods < 0.65
3. A5 (implementation bug): verify 10-sample dry-run of all three aggregation variants produce distinct scores
4. Route to Phase 2A-Dialogue for hypothesis redesign

### 8.2 Directional Predictions (H-M3 Preview — Secondary for H-E1)

| Prediction | Condition | Threshold |
|-----------|-----------|-----------|
| P1 | AUROC(min) > AUROC(mean) on TriviaQA and NQ | Δ ≥ 0.02, CI lower > 0 |
| P2 | AUROC(mean) > AUROC(min) on TruthfulQA | Δ ≥ 0.02, CI lower > 0 |
| P3 | AUROC(sum) < both min and mean on all datasets | Directional, no threshold |

P1–P3 are not required for H-E1 gate; they are tracked here for H-M3 evidence accumulation.

### 8.3 Absolute Performance Floor

For interpretability, also verify that at least one aggregation function achieves AUROC > 0.55 on at least one dataset for at least one model (confirming log-prob signal is non-trivial vs. random).

---

## 9. Implementation Plan

### 9.1 Software Stack

| Component | Library | Version |
|-----------|---------|---------|
| LLM inference | `transformers` | ≥4.40 |
| AUROC | `scikit-learn` | ≥1.4 |
| Bootstrap | `scipy.stats.bootstrap` | ≥1.11 |
| Datasets | `datasets` (HuggingFace) | ≥2.18 |
| Numerics | `numpy` | ≥1.26 |

### 9.2 lm-polygraph Note (Risk R5 Mitigation)

lm-polygraph implements `TokenSAR` (token-level sensitivity-weighted average) and entropy-based estimators, but may not expose standalone `min` log-prob aggregation as a named estimator. The pseudo-code in Section 4 implements all three aggregation functions directly from `model.generate(..., output_scores=True)` — no dependency on lm-polygraph for the core aggregation comparison. lm-polygraph can be used as a cross-check for `mean` (equivalent to negative sequence NLL / length).

### 9.3 Farquhar 2023 Data Splits

Load Farquhar 2023 splits from `jlko/semantic_uncertainty` GitHub repository:
- `data/trivia_qa_val.jsonl` — TriviaQA samples with binary labels
- `data/nq_open_val.jsonl` — NQ samples with binary labels
- These provide consistent Q/A pairs and exact-match labels used in the AUROC ~0.72 baseline (predictive entropy)

---

## 10. Failure Response Protocol

| Failure Mode | Diagnostic | Response |
|-------------|------------|----------|
| All AUROCs cluster within 0.01 | Greedy log-probs uninformative (A3) | Sanity check: run N=5 sampling entropy on 10% TriviaQA; if SE AUROC >> our best, confirm A3 violation |
| Best AUROC < 0.55 on all datasets | Label noise ceiling (A4) | Use full splits (already planned); report as label noise limitation; relative comparisons still valid |
| Three variants give identical scores | Implementation bug (A5) | Verify 10-sample dry run; check tokenizer alignment between question and answer tokens |
| AUROC > 0.55 but no pair Δ ≥ 0.02 | H0 supported | ABANDON H-E1; reframe as negative result; report that aggregation function is not a critical design choice at this scale |

---

## 11. References

### Primary Literature (from Phase 2B Verification Plan)

- Farquhar et al. (2023). "Detecting Hallucinations in Large Language Models Using Semantic Entropy." *Nature*. — Provides TriviaQA/NQ splits, binary labels, predictive entropy (sum) AUROC ~0.72 baseline
- Fadeeva et al. (2024). "LM-Polygraph: Uncertainty Estimation for Language Models." *EMNLP 2024*. — CCP mean aggregation AUROC ~0.72–0.80 on TriviaQA/NQ
- Lin et al. (2021). "TruthfulQA: Measuring How Models Mimic Human Falsehoods." *ACL 2022*. — TruthfulQA dataset, inverse scaling phenomenon
- Manakul et al. (2023). "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models." *EMNLP 2023*. — AUROC ~0.72–0.78 on WikiBio

### Related Implementations Found (Exa Search, 2026-08-21)

- Hima-Mehta/LLM-Uncertainity (GitHub, 2026): Implements token-level uncertainty (entropy, max prob gap), sentence-level uncertainty (avg NLL, sequence confidence), and AUROC evaluation — directly parallel to this experiment's aggregation comparison
- Hert4/LLM-Certainty-Consistency (GitHub, 2026): PCC method using token logprobs for hallucination detection; one-forward-pass certainty signal (τ = log-prob margin on yes/no verdict)
- Heman10x-NGU/hallucination-sentinel (GitHub, 2026): CES entropy scoring from per-token log-probs; single-pass; relevant to calibration analysis
- Rivas-AI/HalluDetect (GitHub, 2024): Token probability features for hallucination classification; uses LR/MLP on extracted features — confirms viability of token-prob approaches

### Archon KB Search

Archon KB search for "log probability hallucination detection AUROC" and "log probability scoring hallucination detection" returned no relevant results (KB contains diffusion model content, not LLM uncertainty estimation). No prior implementation found in KB.

---

## 12. Output Artifacts

| Artifact | Path | Description |
|---------|------|-------------|
| Raw scores | `h-e1/results/scores_{model}_{dataset}.npz` | Per-sample scores for all 3 aggregation functions |
| AUROC table | `h-e1/results/auroc_table.csv` | 18-cell AUROC table (2 models × 3 datasets × 3 methods) |
| CI table | `h-e1/results/bootstrap_ci_table.csv` | Pairwise AUROC differences with 95% CI bounds |
| ROC curves | `h-e1/figures/roc_{model}_{dataset}.png` | ROC curves per (model, dataset) with all 3 aggregation methods |
| Score histograms | `h-e1/figures/hist_{model}_{dataset}_{method}.png` | Score distributions split by correctness |
| Gate decision log | `h-e1/results/gate_decision_h-e1.md` | Pass/fail verdict with justification |
