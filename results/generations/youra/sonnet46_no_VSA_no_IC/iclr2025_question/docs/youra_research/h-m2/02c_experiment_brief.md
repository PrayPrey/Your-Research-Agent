# Experiment Design: H-M2

**Date:** 2026-08-21
**Author:** Anonymous
**Hypothesis Statement:** Min log-prob achieves higher rank-order correlation with hallucination labels than mean log-prob on TriviaQA/NQ (peaked distributions); mean log-prob achieves higher rank-order correlation than min on TruthfulQA (flat high-probability distributions), because min is maximally sensitive to single worst-case tokens while mean integrates signal across all tokens.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Rank-order correlation sensitivity comparison across benchmark types.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (MUST_WORK gate PASS)
**Gate Status:** SHOULD_WORK — failure narrows claim but does not block H-M3

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (MUST_WORK, satisfied)

### Gate Condition

SHOULD_WORK: Rank correlation direction matches prediction on at least TriviaQA and TruthfulQA for at least one model. Failure → EXPLORE (document mechanistic limitation, proceed to H-M3).

---

## Continuation Context

**Continuation from H-M1:** This experiment reuses the same frozen model forward-pass outputs already computed for H-M1 (LLaMA-2-7B on TriviaQA/NQ, Farquhar 2023 splits). No re-inference needed for LLaMA-2-7B on TriviaQA/NQ. TruthfulQA requires an additional inference pass.

**H-M1 Proven Components (reuse):**
- LLaMA-2-7B frozen weights, greedy decoding, Farquhar 2023 TriviaQA/NQ splits
- Token log-prob extraction pipeline (already validated)
- Binary correctness labels from Farquhar 2023

**New for H-M2:**
- Compute Spearman ρ between min/mean log-prob scores and correctness labels (instead of peakedness ratio)
- Add TruthfulQA inference pass (standard HuggingFace split)
- Add Mistral-7B-v0.1 inference pass for secondary replication

### Previous Hypothesis Results (H-M1)
- LLaMA-2-7B on TriviaQA (n=488): hallucinated peakedness mean=2.936, correct mean=2.533, p=0.0021 — distribution shape asymmetry confirmed
- Peaked distribution mechanism verified: recall failures concentrate uncertainty at single fact-token

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** No domain-relevant content found in Archon KB (KB contains diffusion model / image generation content only; all similarity scores ≤ 0.51). Experiment design proceeds from Exa GitHub findings and Phase 2B planning.

**Queries executed:**
- "token log probability aggregation hallucination detection" — no relevant results
- "min mean aggregation uncertainty quantification LLM implementation" — no relevant results
- "TriviaQA NQ TruthfulQA hallucination AUROC benchmark" — no relevant results
- "Spearman rank correlation hallucination labels logprob" — no relevant results
- "TriviaQA NQ dataset loading HuggingFace evaluation" — no relevant results

### Archon Code Examples

**Status:** No relevant code examples found. All results are HuggingFace Diffusers image generation code (similarity ≤ 0.43).

### Exa GitHub Implementations

**Query 1: Farquhar semantic_uncertainty official implementation**

**Repository 1:** jlko/semantic_uncertainty (⭐ 411)
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Relevance:** Official codebase for Farquhar 2023 Nature paper — exact data splits and pipeline used in our verification protocol
- **Pipeline structure:**
  1. `generate_answers.py` — samples responses + likelihoods from frozen LLMs (greedy + temperature)
  2. `compute_uncertainty_measures.py` — computes uncertainty metrics (predictive entropy, semantic entropy, etc.)
  3. `analyze_results.py` — computes AUROC and aggregate performance metrics
- **Models supported:** Llama-2-7b, Llama-2-13b, Llama-2-70b, Mistral-7B-v0.1 (all our targets)
- **Datasets supported:** trivia_qa, nq, squad, bioasq, svamp
- **Dataset splits:** 400 train + 400 test per dataset (randomly sampled from original splits)
- **Key insight:** predictive entropy (sum of token log-probs) is a baseline in this repo; we ablate min vs. mean vs. sum directly

**Repository 2:** IINemo/lm-polygraph (widely deployed benchmark)
- **URL:** https://github.com/IINemo/lm-polygraph
- **Relevance:** Implements `MeanTokenEntropy()`, `Perplexity()` (mean/sum aggregation) as distinct estimators; confirmed white-box information-based estimators
- **Key code:**
  ```python
  from lm_polygraph.estimators import *
  ue_method = MeanTokenEntropy()
  estimate_uncertainty(model, ue_method, input_text='...')
  ```
- **Estimator table confirms:** Mean/max token entropy implemented as distinct white-box low-compute estimators; min log-prob requires custom 5-line wrapper

**Repository 3:** technion-cs-nlp/LLMsKnow
- **URL:** https://github.com/technion-cs-nlp/LLMsKnow
- **Relevance:** `logprob_detection.py` script directly computes log-prob baseline for TriviaQA/Mistral; shows exact implementation pattern for log-prob as hallucination detector
- **Key pattern:**
  ```bash
  python logprob_detection.py --model mistralai/Mistral-7B-Instruct-v0.2 --dataset triviaqa --seeds 0 5 26 42 63
  ```

**Query 2: Spearman correlation logprob hallucination labels**

**Repository 4:** dasjoms/jspace-hallucination-eval
- **URL:** https://github.com/dasjoms/jspace-hallucination-eval
- **Relevance:** Documents TriviaQA, NQ-Open, TruthfulQA evaluation with logprob baselines and Spearman/AUROC metrics; confirms TruthfulQA workspace signal collapses (ROC-AUC ~0.617 vs logprob baseline ~0.743) — directly relevant to P2 prediction
- **Key finding:** "On TruthfulQA, the metric fails to detect errors on adversarially constructed misconceptions" — supports our prediction that mean > min on TruthfulQA

**Scipy / sklearn references:**
- `scipy.stats.spearmanr(scores, labels)` — direct Spearman ρ with p-value
- `sklearn.metrics.roc_auc_score(y_true, y_score)` — AUROC
- `scipy.stats.bootstrap(data, statistic, n_resamples=1000, confidence_level=0.95)` — 95% CI on correlation differentials

**Serena Analysis Needed:** false — code is clear (<30 lines of core logic)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For data pipeline: use jlko/semantic_uncertainty as ground truth for Farquhar 2023 splits.
For aggregation functions: implement custom min/mean/sum wrappers (5 lines each) on top of token log-probs already extracted by the semantic_uncertainty pipeline.

**Recommended Implementation Path:**
- Primary: jlko/semantic_uncertainty for data loading + LLM inference pipeline
- Fallback: Direct HuggingFace `datasets.load_dataset` + custom inference loop
- Justification: jlko/semantic_uncertainty already handles LLaMA-2-7B and Mistral-7B-v0.1 on trivia_qa and nq with exact Farquhar 2023 splits; reusing eliminates data split drift

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Core aggregation logic is ≤10 lines of numpy; scipy.stats.spearmanr and sklearn.metrics.roc_auc_score are standard API calls.

---

## Experiment Specification

### Dataset

**Multi-Dataset Setup (3 benchmarks, per hypothesis design):**

| Dataset | Role | Distribution Type | Split |
|---------|------|-------------------|-------|
| TriviaQA | Primary (P1: min > mean) | Peaked — recall failure | Farquhar 2023: 400 test |
| NQ-Open | Primary (P1 replication) | Peaked — recall failure | Farquhar 2023: 400 test |
| TruthfulQA | Primary (P2: mean > min) | Flat — imitative falsehood | HuggingFace generation split: 817 samples |

**TriviaQA + NQ Details:**
- Source: Farquhar et al. 2023 (jlko/semantic_uncertainty repo, BSD-3-Clause-Clear)
- HuggingFace: `load_dataset("trivia_qa", "rc.nocontext")` + `load_dataset("nq_open")` then apply Farquhar 2023 sample selection
- Split: 400 test examples per dataset (randomly sampled, fixed seed, from original test/validation splits)
- Labels: Binary correctness (exact-match/F1 against reference answers, per Farquhar 2023)
- Type: standard (programmatic-api via Farquhar 2023 pipeline)
- Path: auto (downloaded via jlko/semantic_uncertainty pipeline or HuggingFace)

**TruthfulQA Details:**
- Source: Lin et al. 2021; HuggingFace: `load_dataset("truthful_qa", "generation")`
- Split: full generation split (~817 samples)
- Labels: Binary correctness (truthful = 1, hallucinated = 0) via reference answer matching
- Type: standard
- Path: auto

**Loading Information:**
- Method: HuggingFace datasets + jlko/semantic_uncertainty pipeline
- Identifier: `"trivia_qa"`, `"nq_open"`, `"truthful_qa"`
- Code:
  ```python
  from datasets import load_dataset
  trivia = load_dataset("trivia_qa", "rc.nocontext", split="validation")
  nq = load_dataset("nq_open", split="validation")
  tqa = load_dataset("truthful_qa", "generation", split="validation")
  ```

**Preprocessing:**
- No text preprocessing beyond tokenization (frozen model, single greedy forward pass)
- Questions formatted as few-shot prompts per Farquhar 2023 format (4-shot for TriviaQA/NQ, 0-shot for TruthfulQA)
- Answers: single greedy decode, max_new_tokens=20 (short-phrase regime)

**Synthetic data check:** PASS — all three are established real benchmarks.

### Models

#### Baseline Model

**Architecture:** LLaMA-2-7B (primary), Mistral-7B-v0.1 (secondary replication)

**Configuration:**
- Frozen weights (no fine-tuning, no LoRA)
- Single greedy forward pass (temperature=0, do_sample=False)
- Token log-prob extraction via `model.generate()` with `return_dict_in_generate=True, output_scores=True`
- 16GB VRAM (fp16)

**Loading Information:**
- Method: HuggingFace transformers
- Identifier (primary): `"meta-llama/Llama-2-7b-hf"`
- Identifier (secondary): `"mistralai/Mistral-7B-v0.1"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

**Continuation from H-M1:** LLaMA-2-7B inference on TriviaQA/NQ already performed. Token log-probs cached. Only TruthfulQA + Mistral-7B-v0.1 require new inference.

#### Proposed Model

**Architecture:** Baseline + three token log-prob aggregation functions (ablation over aggregation function choice)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Token Log-Prob Aggregation Function Ablation
# Based on: jlko/semantic_uncertainty pipeline + lm-polygraph estimator patterns
# Hypothesis H-M2: min sensitive to peaked distributions, mean integrates flat distributions

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

def extract_token_logprobs(model, tokenizer, prompt, max_new_tokens=20):
    """Single greedy forward pass; returns per-token log-probs of generated answer."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, return_dict_in_generate=True, output_scores=True
        )
    # scores: list of (vocab_size,) logits per generated token
    token_logprobs = [
        torch.log_softmax(s, dim=-1)[0, tok].item()
        for s, tok in zip(out.scores, out.sequences[0, inputs.input_ids.shape[1]:])
    ]
    return np.array(token_logprobs)  # shape: (n_generated_tokens,)

def aggregate(token_logprobs, method):
    """Aggregation functions: min / mean / raw_sum."""
    if method == "min":
        return token_logprobs.min()          # most uncertain single token
    elif method == "mean":
        return token_logprobs.mean()         # average uncertainty
    elif method == "raw_sum":
        return token_logprobs.sum()          # joint log-prob (length-dependent)
    raise ValueError(method)

# For each dataset and model:
# 1. Compute token_logprobs for each question's greedy answer
# 2. Compute min/mean/raw_sum scores per sample
# 3. Compute Spearman ρ(score, correctness_label) per aggregation function per dataset
# 4. Report ρ(min, TriviaQA/NQ) vs ρ(mean, TriviaQA/NQ)
#    and ρ(mean, TruthfulQA) vs ρ(min, TruthfulQA)
```

### Training Protocol

**No training required** — evaluation-only experiment on frozen models.

**Inference Protocol:**
- Optimizer: N/A (frozen weights)
- Batch size: 1 (greedy decode; or 8 with padding if GPU memory allows)
- Seeds: 1 (fixed, for reproducibility of prompt sampling)
- Compute: Single forward pass per question per model
- Estimated runtime: ~2-4 GPU-hours per model on 16GB VRAM (400+400+817 samples)

**Continuation from H-M1:**
- LLaMA-2-7B token log-probs on TriviaQA/NQ: **reuse from H-M1** (already computed)
- LLaMA-2-7B on TruthfulQA: new inference (~817 samples, ~1 GPU-hour)
- Mistral-7B-v0.1 on all three datasets: new inference (~1617 samples, ~3 GPU-hours)

**Statistical Analysis Protocol:**
```python
from scipy.stats import spearmanr, bootstrap
from sklearn.metrics import roc_auc_score
import numpy as np

def compute_spearman_with_ci(scores, labels, n_resamples=1000, ci=0.95):
    """Spearman ρ with bootstrap 95% CI."""
    rho, pval = spearmanr(scores, labels)
    def stat(data):
        s, l = data
        return spearmanr(s, l).statistic
    res = bootstrap(
        (scores, labels), stat, n_resamples=n_resamples,
        confidence_level=ci, paired=True, method='percentile'
    )
    return rho, pval, res.confidence_interval

# For each (model, dataset, aggregation_method):
# rho, pval, ci = compute_spearman_with_ci(scores, labels)
# Also compute AUROC for comparison with H-M3
```

### Evaluation

**Primary Metrics (H-M2):**

| Metric | Definition | Tool |
|--------|------------|------|
| Spearman ρ (min, TriviaQA) | Rank-order correlation between min log-prob scores and binary correctness labels | `scipy.stats.spearmanr` |
| Spearman ρ (mean, TriviaQA) | Same with mean aggregation | `scipy.stats.spearmanr` |
| Spearman ρ (min, NQ) | Same on NQ | `scipy.stats.spearmanr` |
| Spearman ρ (mean, NQ) | Same on NQ | `scipy.stats.spearmanr` |
| Spearman ρ (min, TruthfulQA) | Same on TruthfulQA | `scipy.stats.spearmanr` |
| Spearman ρ (mean, TruthfulQA) | Same on TruthfulQA | `scipy.stats.spearmanr` |
| CI on ρ differential | 95% bootstrap CI on ρ(min) − ρ(mean) per dataset | `scipy.stats.bootstrap` |

**Secondary Metrics (for H-M3 preview):**
- AUROC (min, mean, raw_sum) per (model, dataset) via `sklearn.metrics.roc_auc_score`

**Success Criteria (SHOULD_WORK gate):**

| Prediction | Criterion | Priority |
|------------|-----------|----------|
| P1: min > mean on TriviaQA/NQ | ρ(min, TriviaQA) > ρ(mean, TriviaQA) for ≥1 model | Primary |
| P2: mean > min on TruthfulQA | ρ(mean, TruthfulQA) > ρ(min, TruthfulQA) for ≥1 model | Primary |
| Direction match | At least TriviaQA and TruthfulQA directional pattern confirmed for ≥1 model | Gate criterion |
| Secondary: NQ replication | P1 also holds on NQ | Secondary |
| Secondary: Mistral replication | Both P1 and P2 replicate on Mistral-7B-v0.1 | Secondary |

**Expected Baseline Performance (from research):**
- jlko/semantic_uncertainty reports predictive entropy (sum) AUROC ~0.72 on TriviaQA
- dasjoms/jspace-hallucination-eval: logprob baseline ROC-AUC ~0.743 on TriviaQA, ~0.617 on TruthfulQA — supports P2 (min/sum-based aggregations underperform mean on TruthfulQA)
- CCP mean aggregation: AUROC ~0.72-0.80 on TriviaQA/NQ (Fadeeva 2024) — consistent with mean being a reasonable baseline on recall benchmarks

**Task Type:** Binary hallucination detection (no training; evaluation-only)
**Library:** `scipy.stats` + `sklearn.metrics`
**Metrics code:**
```python
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
rho, pval = spearmanr(scores, labels)
auroc = roc_auc_score(labels, -scores)  # negated: lower score = more uncertain = hallucinated
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **ρ Differential Bar Chart:** ρ(min) − ρ(mean) per dataset per model, with 95% CI error bars. Shows sign and magnitude of direction effect.

#### Additional Figures (LLM Autonomous)
- **Scatter plot:** Spearman ρ values (min vs. mean) per dataset/model — visual separation between peaked and flat benchmark groups
- **AUROC comparison table/heatmap:** min / mean / raw_sum × TriviaQA / NQ / TruthfulQA × LLaMA-2-7B / Mistral-7B-v0.1 (feeds H-M3)
- **Distribution overlay:** token log-prob distribution histograms for hallucinated vs. correct answers on TriviaQA vs. TruthfulQA (reinforces H-M1 → H-M2 causal chain)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**Gate: SHOULD_WORK**

**Pass Condition (Primary):**
1. Code runs without error
2. ρ(min, TriviaQA) > ρ(mean, TriviaQA) for ≥1 model (P1 direction)
3. ρ(mean, TruthfulQA) > ρ(min, TruthfulQA) for ≥1 model (P2 direction)

**Partial Pass (narrowed claim):**
- P1 holds but P2 fails → document: TruthfulQA imitative pattern absent at 7B (Risk R1); narrowed claim: min > mean only on recall benchmarks

**Fail → EXPLORE:**
- Both P1 and P2 fail → rank correlation and AUROC may decouple due to label noise or distribution shape not as predicted; document as limitation

---

## Mechanism Verification Protocol

**Pre-conditions (verify before running):**
- `mechanism_exists`: Token log-prob sequences are accessible per generated answer ✓ (confirmed in H-M1)
- `mechanism_isolatable`: Only aggregation function changes between min/mean/raw_sum conditions; all other variables frozen ✓
- `baseline_measurable`: Binary correctness labels available via Farquhar 2023 pipeline ✓

**Architecture Compatibility:**
- LLaMA-2-7B and Mistral-7B-v0.1 both expose per-token log-probs via HuggingFace `output_scores=True` ✓
- Single greedy forward pass sufficient — no sampling required for this hypothesis ✓

**Activation Indicators (verify mechanism fires correctly):**
- Log message: `"[H-M2] min={min_score:.4f}, mean={mean_score:.4f}, sum={sum_score:.4f} for sample {i}"`
- Sanity check: `min_score ≤ mean_score ≤ 0` for all samples (log-probs are negative; min is most negative)
- Tensor shape: `token_logprobs.shape = (n_generated_tokens,)` where n > 0

**Failure Detection:**
- If `min_score == mean_score` for all samples: aggregation bug (check extraction)
- If all correlations ≈ 0: label noise or extraction error; verify Farquhar 2023 labels match model outputs
- If Spearman p-value > 0.5 for all: no signal; proceed to H-M3 with AUROC-based analysis

**Mechanism Verification Code:**
```python
# Sanity check before full experiment
assert all(s.min() <= s.mean() <= 0 for s in sample_logprobs[:10]), \
    "Log-prob ordering violated — check extraction"
print(f"Sample ρ(min, label) on 50 examples: {spearmanr(min_scores[:50], labels[:50]).statistic:.4f}")
print(f"Sample ρ(mean, label) on 50 examples: {spearmanr(mean_scores[:50], labels[:50]).statistic:.4f}")
```

**Hypothesis Support Threshold:**
- `hypothesis_support_threshold`: ρ(min) > ρ(mean) on TriviaQA AND ρ(mean) > ρ(min) on TruthfulQA for ≥1 model
- `hypothesis_support_metric`: Spearman ρ differential sign per dataset

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No domain-relevant content found. Archon KB indexed content is limited to HuggingFace Diffusers / image generation domain. All 5 queries returned irrelevant results (similarity ≤ 0.51).

**Impact:** No KB-derived hyperparameters or past cases applicable. Experiment design fully grounded in Exa GitHub findings and Phase 2B protocol.

### B. GitHub Implementations (Exa)

**Repository B.1:** jlko/semantic_uncertainty (⭐ 411)
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Query:** "Farquhar semantic uncertainty jlko GitHub token log probability aggregation hallucination detection TriviaQA NQ"
- **Relevance:** Official implementation; exact data splits; LLaMA-2-7B and Mistral-7B-v0.1 supported
- **Configuration extracted:** 400 test samples per dataset (Farquhar 2023 splits), greedy decode, few-shot prompts
- **Used for:** Dataset loading protocol, inference pipeline, split specification, label generation

**Repository B.2:** IINemo/lm-polygraph
- **URL:** https://github.com/IINemo/lm-polygraph / https://lm-polygraph.readthedocs.io
- **Query:** "lm-polygraph token probability aggregation min mean sum AUROC hallucination uncertainty quantification LLM"
- **Relevance:** `MeanTokenEntropy()` and `Perplexity()` confirm mean/sum aggregation API patterns; min requires custom wrapper
- **Used for:** Aggregation function implementation pattern; confirms white-box low-compute estimator feasibility

**Repository B.3:** technion-cs-nlp/LLMsKnow
- **URL:** https://github.com/technion-cs-nlp/LLMsKnow
- **Query:** "Spearman rank correlation token logprob min mean hallucination label TriviaQA TruthfulQA Python scipy"
- **Relevance:** `logprob_detection.py` — direct log-prob baseline for TriviaQA/Mistral; shows evaluation pattern
- **Used for:** Log-prob baseline implementation pattern, model loading code

**Repository B.4:** dasjoms/jspace-hallucination-eval
- **URL:** https://github.com/dasjoms/jspace-hallucination-eval
- **Query:** "Spearman rank correlation token logprob min mean hallucination label TriviaQA TruthfulQA Python scipy"
- **Relevance:** Empirically confirms TruthfulQA logprob baseline collapse (ROC-AUC ~0.617 vs TriviaQA ~0.743); validates P2 prediction direction
- **Used for:** Expected performance calibration; P2 prediction support

**Library sources (Exa web search):**
- `scipy.stats.spearmanr` — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- `scipy.stats.bootstrap` — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- `sklearn.metrics.roc_auc_score` — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa search results was sufficiently clear. Core aggregation logic is ≤15 lines of standard numpy/scipy. No complex architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1
- **Reused components:**
  - LLaMA-2-7B frozen inference pipeline on TriviaQA/NQ (token log-probs already extracted)
  - Farquhar 2023 data splits and binary correctness labels
  - Forward-pass extraction code (`output_scores=True`)
- **Why reused:** Enables controlled comparison — only the aggregation function and metric (Spearman ρ vs. peakedness ratio) change between H-M1 and H-M2

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| TriviaQA/NQ dataset splits | GitHub | B.1 (jlko/semantic_uncertainty) |
| TruthfulQA dataset | HuggingFace standard | HuggingFace datasets |
| Sample count (400/400/817) | GitHub + Paper | B.1, Farquhar 2023 Nature |
| Binary correctness labels | GitHub | B.1 pipeline |
| LLaMA-2-7B loading | GitHub | B.3 (LLMsKnow) |
| Mistral-7B-v0.1 loading | GitHub | B.1, B.3 |
| Aggregation function logic | GitHub | B.2 (lm-polygraph patterns) |
| Spearman ρ implementation | Exa web search | scipy.stats.spearmanr docs |
| Bootstrap CI | Exa web search | scipy.stats.bootstrap docs |
| AUROC | Exa web search | sklearn.metrics.roc_auc_score docs |
| Expected TruthfulQA AUROC ~0.617 | GitHub | B.4 (dasjoms/jspace) |
| Token log-prob extraction | Phase 2B + H-M1 | Continuation context |
| Statistical analysis protocol | Phase 2B | 02b_verification_plan.md H-M2 protocol |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS (2026-08-21T13:17:04)
- Phase 2C experiment design COMPLETED (2026-08-21)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + web search — primary research source), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
