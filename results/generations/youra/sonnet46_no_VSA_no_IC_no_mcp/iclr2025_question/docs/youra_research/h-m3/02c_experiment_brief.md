# Experiment Design: H-M3

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Llama-2-7B on TriviaQA dev, if SelfCheckGPT BERTScore consistency is computed across K=10 samples, then SCG achieves AUROC within 0.03 of SE (|SCG-SE| <= 0.03), because BERTScore agreement implicitly captures semantic consistency without requiring NLI inference — a different mechanism achieving the same discrimination.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests whether SCG (BERTScore-based) achieves practical equivalence to SE on hallucination detection AUROC.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (PASSED), H-M2 (FAILED — SHOULD_WORK, non-blocking)
**Gate Status:** SHOULD_WORK — failure does not block pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M1, H-M2

### Gate Condition

**Gate type:** SHOULD_WORK (non-blocking)
**Condition:** |SCG AUROC − SE AUROC| ≤ 0.03
**Rationale:** If SCG achieves equivalent discrimination to SE without NLI inference, practitioners at 7B scale can skip the NLI model entirely.

---

## Continuation Context

This is a continuation experiment in the causal chain H-E1 → H-M1 → H-M2 → H-M3.

**H-M2 failed** due to a structural experiment design error (ablated predictor was a monotone transform of SE — delta AUROC = 0 by construction). Secondary metrics confirmed NLI clustering is mechanically active (mean cluster count 7.31/10, 23% entropy savings). The SE mechanism remains plausible.

**Key continuation facts from H-M1/H-M2:**
- Same 98 TriviaQA questions with K=10 samples from h-e2-v2 cache
- SE AUROC ≈ 0.54–0.57 (from H-E1, confirmed active signal)
- TE AUROC ≈ 0.49–0.52 (from H-E1)
- Bootstrap AUROC with N=1000 iterations, seed=42, stratified resampling
- NLI model: cross-encoder/nli-deberta-v3-large, entailment threshold 0.5

### Previous Hypothesis Results (H-M2)
- Gate: FAIL (SHOULD_WORK — non-blocking)
- AUROC_clustered = 0.2136 [0.122, 0.304] — NOTE: this was inverted sign (uncertainty computed as within_cluster_fraction); actual SE AUROC from H-E1 is ~0.54
- Root cause: ablated predictor was monotone transform of SE
- Lesson: H-M3 uses an independent predictor (SCG via BERTScore) — no monotone transform issue

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon MCP not available in this session. Proceeding with web search findings.

**Query 1: SelfCheckGPT BERTScore experiment design**
- From Manakul et al. 2023 (SelfCheckGPT paper): BERTScore variant uses RoBERTa-large to compute pairwise F1 between each sentence in primary response and each stochastic sample
- Standard benchmark: WikiBio (original); TriviaQA adaptation is novel for this experiment
- SCG-BERTScore does NOT require access to model logits — pure black-box consistency method
- Computational cost: ~7 min CPU for 98 questions with K=10 samples (vs NLI model for SE)

**Query 2: Implementation challenges**
- BERTScore requires sentence segmentation of full-passage responses; for short QA answers (TriviaQA), treat entire answer as single sentence
- Rescale_with_baseline=True recommended for better absolute score calibration
- Higher BERTScore = more consistent = lower uncertainty; inversion needed for AUROC (high score = uncertain = likely wrong)
- `selfcheckgpt` PyPI package: `pip install selfcheckgpt`; imports `SelfCheckBERTScore` from `selfcheckgpt.modeling_selfcheck`

**Query 3: Benchmark / Expected performance**
- No direct SCG vs SE comparison on TriviaQA at 7B scale exists in literature (research gap confirmed in 02b_verification_plan.md Section 1.6)
- Systematic evaluation papers (arxiv 2510.20460) benchmark multiple UQ methods; confidence-based methods reach AUROC ~80 on Llama-3/Mistral-7B — but at larger scale / different datasets
- Xiong et al. 2023 on verbalized confidence at 7B: AUROC ~0.50-0.55 (comparison anchor)

### Archon Code Examples

Not available (Archon MCP offline). See Exa/Web findings below.

### Exa GitHub Implementations

**Query 1: Author's official implementation**

**Repository: potsawee/selfcheckgpt** (Official)
- **URL:** https://github.com/potsawee/selfcheckgpt
- **Relevance:** This is the exact library used in the Manakul et al. 2023 paper
- **Architecture:** Zero-resource black-box hallucination detection via sample consistency
- **Key Code:**
  ```python
  from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
  import torch

  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  selfcheck_bertscore = SelfCheckBERTScore(rescale_with_baseline=True)

  # sentences: list of sentences from primary response
  # sampled_passages: list of K stochastic sample strings
  sent_scores = selfcheck_bertscore.predict(
      sentences=sentences,              # list[str]
      sampled_passages=[s1, s2, ..., sK],  # list[str], K=10
  )
  # sent_scores: array of shape (len(sentences),), range [0,1]
  # Higher = more likely hallucinated (inconsistent across samples)
  ```
- **Training Config:** No training required — pure inference
- **Dataset:** WikiBio (original paper); adaptable to TriviaQA short-answer QA
- **Results:** Competitive with NLI variant on WikiBio; no TriviaQA numbers published

**Query 2: Dataset loading**

**Source: mandarjoshi/trivia_qa (HuggingFace)**
- **URL:** https://huggingface.co/datasets/mandarjoshi/trivia_qa
- Loaded via: `load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")`
- NOTE: H-M3 does NOT re-load TriviaQA — it reuses h-e2-v2 K=10 samples from the existing cache (same as H-E1 through H-M2)

**Serena Analysis Needed:** No — SelfCheckBERTScore implementation is straightforward from the official repo; no complex custom layers requiring semantic analysis.

### Code Analysis (Serena MCP)

*Skipped* — Code from official potsawee/selfcheckgpt repo and existing h-m2 codebase is sufficiently clear. SelfCheckBERTScore is a thin wrapper over bert_score package with a predict() API.

---

## Experiment Specification

### Dataset

**Name:** TriviaQA dev (N=98, from h-e2-v2 pilot cache)
**Type:** standard (programmatic-api — loaded from existing cache)
**Source:** `_archive/20260825T162535_routing_recovery/h-e2-v2/code/results/interim_cache.jsonl`
**HuggingFace identifier:** mandarjoshi/trivia_qa (rc config, validation split) — but H-M3 reuses cached samples, no re-download needed

**Statistics:**
- N = 98 questions (same as H-E1, H-M1, H-M2)
- K = 10 stochastic samples per question (temperature=0.7, Llama-2-7B)
- Labels: binary EM (exact match) correctness from h-e2-v2

**Preprocessing:**
- Load from h-e2-v2 cache via `h-e1/code/data.py:load_h_e2v2_samples()`
- Extract: `samples` (K=10 strings), `answer_aliases`, `is_correct` per question
- For SCG: each sample is a short QA answer → treat as single sentence (no segmentation needed)

**Continuation reuse rationale:** Identical dataset + samples enables controlled comparison. Only the uncertainty estimator changes (SCG vs SE vs TE from previous hypotheses).

**Loading Information** (for Phase 4 download):
- Method: local cache (no download required)
- Identifier: `_archive/20260825T162535_routing_recovery/h-e2-v2/code/results/interim_cache.jsonl`
- Code:
  ```python
  import sys
  sys.path.insert(0, "../../h-e1/code")
  from data import load_h_e2v2_samples
  samples_map = load_h_e2v2_samples()
  ```

### Models

#### Baseline Model

**Architecture:** Semantic Entropy (SE) — NLI-clustered entropy on K=10 samples
**Type:** Already computed — reuse SE scores from H-E1 results cache
**Source:** h-e1 results (se_scores per question already stored)

**Configuration:**
- NLI model: cross-encoder/nli-deberta-v3-large
- Entailment threshold: 0.5
- K: 10 samples, seed: 42
- SE score = -sum(p_c * log(p_c)) over NLI clusters where p_c = cluster_size / K

**Loading Information** (for Phase 4):
- Method: load from h-e1 results JSON or recompute via h-e1/code/compute_se.py
- Code:
  ```python
  import json
  with open("../../h-e1/results.json") as f:
      he1 = json.load(f)
  se_scores = he1["se_scores"]   # dict {question_id: float}
  em_labels = he1["em_labels"]   # dict {question_id: int}
  ```

#### Proposed Model

**Architecture:** SelfCheckGPT BERTScore (SCG) — pairwise BERTScore consistency across K=10 samples
**Mechanism:** For each question, compute SCG uncertainty as `1 - mean_pairwise_BERTScore(samples)`. No NLI model required.

**Core Mechanism Implementation:**

```python
# Core Mechanism: SelfCheckGPT BERTScore Consistency
# Based on: potsawee/selfcheckgpt (Manakul et al. 2023)
# Adapted for short QA answers (single-sentence per response)

from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore

selfcheck = SelfCheckBERTScore(rescale_with_baseline=True)

def compute_scg_uncertainty(samples: list[str]) -> float:
    """
    Args:
        samples: K=10 stochastic answer strings for one question
    Returns:
        scg_uncertainty: float in [0, 1], higher = more uncertain
    """
    # Use first sample as "primary response"
    primary = samples[0]
    others  = samples[1:]     # K-1 = 9 remaining samples

    # Treat each answer as a single sentence (short QA format)
    sentences = [primary]

    # Compute BERTScore consistency: shape (1,) per sentence
    sent_scores = selfcheck.predict(
        sentences=sentences,
        sampled_passages=others,  # list of 9 strings
    )

    # sent_scores[0] in [0,1]: high = hallucinated (inconsistent)
    # Average across sentences (here: just 1 sentence)
    scg_uncertainty = float(sent_scores.mean())
    return scg_uncertainty

# Integration: Compute for all 98 questions
scg_scores = {qid: compute_scg_uncertainty(data["samples"])
              for qid, data in samples_map.items()}
```

### Training Protocol

**No training required.** Both SE and SCG are inference-time uncertainty estimators.

**Optimizer:** N/A
**Learning Rate:** N/A
**Batch Size:** N/A (process one question at a time for BERTScore)
**Epochs:** N/A
**Loss:** N/A
**Seeds:** 42 (bootstrap AUROC only)

**Computation:**
- SCG BERTScore: ~7 min CPU per 98 questions (BERTScore uses RoBERTa-large; GPU optional)
- SE: loaded from h-e1 cache (no recomputation needed)
- TE: loaded from h-e1 cache (for secondary comparison)
- Bootstrap AUROC: N_boot=1000, seed=42, stratified (same as H-E1 through H-M2)

**Reuse from H-M2:** bootstrap_auroc() function in h-m2/code/evaluate.py — identical implementation inherited.

### Evaluation

**Primary Metric:** |SCG AUROC − SE AUROC| ≤ 0.03 (practical equivalence)
**Secondary Metric:** SCG AUROC > TE AUROC (confirms semantic-level advantage over token baseline)

**Gate condition:** SHOULD_WORK — |SCG_AUROC − SE_AUROC| ≤ 0.03

**Expected Baseline Performance (from research + H-E1):**
- SE AUROC ≈ 0.54–0.57 (established by H-E1)
- TE AUROC ≈ 0.49–0.52 (established by H-E1)
- SCG AUROC: unknown on TriviaQA at 7B — this is the experimental question
- Bootstrap 95% CI half-width at N=98: ≈ ±0.05

**Metrics Loading Information** (for Phase 4):
- Task Type: binary classification (hallucination detection via ranking)
- Library: sklearn.metrics (roc_auc_score) + numpy bootstrap — reuse h-m2/code/evaluate.py
- Code:
  ```python
  from evaluate import bootstrap_auroc
  auroc_scg, ci_lo, ci_hi = bootstrap_auroc(
      scores=list(scg_scores.values()),
      labels=list(em_labels.values()),
      n_boot=1000,
      seed=42,
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing SCG AUROC vs SE AUROC vs TE AUROC with 95% CI error bars

#### Additional Figures (LLM Autonomous)
- Distribution of SCG uncertainty scores per question, split by EM correct/incorrect
- Scatter plot: SCG score vs SE score per question (to show correlation/divergence)
- ROC curves for SCG, SE, TE on same axes

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | SelfCheckBERTScore is computable from K=10 samples without model internals | TRUE |
| Mechanism Isolatable | SCG score can be computed independently of SE; both produce per-question uncertainty float | TRUE |
| Baseline Measurable | SE AUROC from H-E1 is the baseline — loaded from cached results | TRUE |

### Architecture Compatibility Check

**Required:** K=10 stochastic text samples per question (already available from h-e2-v2 cache)
**Required:** `selfcheckgpt` package (`pip install selfcheckgpt`) — no GPU required (CPU viable)
**Required:** `bert_score` dependency (installed with selfcheckgpt)

**Compatible:** Any LLM output as strings — black-box method, no logit access needed
**Incompatible:** Nothing — SCG BERTScore works on raw text outputs only

> ⚠️ Verify h-e2-v2 samples have `samples` field (list of K strings) per question. Already confirmed in H-M1/M2 runs.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `"SCG uncertainty computed for question {qid}: {score:.4f}"` | run.py:main() |
| Score Distribution | scg_scores values in [0.0, 1.0] — not all identical, variance > 0 | run.py post-compute |
| Metric Delta | SCG AUROC within ±0.1 of SE AUROC (wider band for verification) | evaluate.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_scg_mechanism(scg_scores: dict, em_labels: dict, se_auroc: float) -> tuple:
    scores = list(scg_scores.values())
    labels = list(em_labels.values())
    indicators = {
        "scores_in_range":   all(0.0 <= s <= 1.0 for s in scores),
        "scores_have_variance": float(np.std(scores)) > 0.01,
        "auroc_computable":  len(set(labels)) == 2,  # both 0 and 1 present
        "auroc_not_random":  bootstrap_auroc(scores, labels)[0] > 0.45,
    }
    activated = all(indicators.values())
    scg_auroc = bootstrap_auroc(scores, labels)[0]
    delta = abs(scg_auroc - se_auroc)
    return activated, indicators, delta
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| All SCG scores identical | std(scg_scores) < 0.01 | FAIL: BERTScore degenerate — check selfcheckgpt install |
| SCG scores out of [0,1] | any score outside range | FAIL: rescale_with_baseline issue |
| AUROC non-computable | only one class in em_labels | FAIL: labels corrupted — reload from h-e2-v2 cache |
| SCG AUROC ≈ 0.5 (random) | auroc < 0.48 | INVESTIGATE: consistency signal absent at 7B for this dataset |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 4 indicators TRUE | verify_scg_mechanism() |
| Gate Passed | \|SCG AUROC − SE AUROC\| ≤ 0.03 | bootstrap_auroc() comparison |
| Semantic Advantage | SCG AUROC > TE AUROC | bootstrap_auroc() comparison |

**Hypothesis Support Threshold:** `|SCG_AUROC − SE_AUROC| <= 0.03`
**Hypothesis Support Metric:** AUROC (bootstrap, N=1000, seed=42, stratified) for SCG vs SE vs TE

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `|scg_auroc - se_auroc| <= 0.03`

**Gate type:** SHOULD_WORK — failure is logged and documented but does not stop H-M4.

**Failure response (from 02b_verification_plan.md):**
- IF SCG AUROC > SE AUROC + 0.03: Document — SCG outperforms SE at 7B; revise narrative
- IF SCG AUROC < SE AUROC − 0.05: Document limitation — BERTScore insufficient consistency proxy at 7B

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon MCP unavailable)

**Source 1:** Manakul et al. 2023 — SelfCheckGPT
- **Type:** Original paper + official implementation
- **Query Used:** "SelfCheckGPT BERTScore implementation TriviaQA uncertainty hallucination AUROC"
- **Relevance:** Defines SCG-BERTScore algorithm, provides official code
- **Key Insights:**
  - BERTScore F1 (RoBERTa-large) measures sentence-level consistency
  - Higher score = more consistent = lower uncertainty; must invert for AUROC
  - No logit access required — black-box method
  - `rescale_with_baseline=True` improves absolute calibration
- **Used For:** Core mechanism pseudo-code, implementation approach

**Source 2:** potsawee/selfcheckgpt (GitHub)
- **URL:** https://github.com/potsawee/selfcheckgpt
- **Query Used:** "SelfCheckGPT github potsawee BERTScore implementation code"
- **Key Code:**
  ```python
  from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
  selfcheck = SelfCheckBERTScore(rescale_with_baseline=True)
  sent_scores = selfcheck.predict(sentences=sentences, sampled_passages=other_samples)
  ```
- **Used For:** Core mechanism pseudo-code

**Source 3:** mandarjoshi/trivia_qa (HuggingFace)
- **URL:** https://huggingface.co/datasets/mandarjoshi/trivia_qa
- **Query Used:** "mandarjoshi trivia_qa huggingface datasets load TriviaQA dev split"
- **Used For:** Confirming dataset identifier (rc config, validation split); H-M3 uses cached samples

### B. Continuation Context (Previous Hypotheses)

**Source:** H-E1 — Validation Report
- SE AUROC established at ~0.54–0.57, TE AUROC ~0.49–0.52 on N=98 TriviaQA
- bootstrap_auroc() function (stratified, N=1000) confirmed stable
- **Reused:** se_scores, em_labels, bootstrap_auroc() — no recomputation

**Source:** H-M2 — Validation Report (FAIL, SHOULD_WORK)
- Key lesson: ablated predictor must be independent of primary predictor
- SCG is genuinely independent of SE (different algorithm, no shared computation)
- Secondary metrics confirm NLI clustering is active (mean cluster count 7.31/10)
- **Reused:** bootstrap_auroc() from h-m2/code/evaluate.py; same 98 questions

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TriviaQA N=98) | Continuation | H-E1, H-M1, H-M2 |
| K=10 samples (h-e2-v2) | Continuation | h-e2-v2 cache |
| SCG algorithm | Web/Paper | Manakul 2023, potsawee/selfcheckgpt |
| BERTScore implementation | Web/GitHub | potsawee/selfcheckgpt |
| SE baseline AUROC | Previous result | H-E1 validation report |
| TE baseline AUROC | Previous result | H-E1 validation report |
| bootstrap_auroc() | Codebase | h-m2/code/evaluate.py |
| Gate threshold (0.03) | Phase 2B | 02b_verification_plan.md H-M3 |
| Success criterion | Phase 2B | 02b_verification_plan.md H-M3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written directly)
**Date:** 2026-08-25

### Workflow History for This Hypothesis

- 2026-08-25: H-M2 completed (FAIL — SHOULD_WORK, non-blocking)
- 2026-08-25: H-M3 experiment design started (IN_PROGRESS)
- 2026-08-25: H-M3 experiment design completed (COMPLETED)

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable), existing codebase analysis*
*All specifications grounded in official SelfCheckGPT implementation + prior hypothesis results*
*Next Phase: Phase 3 - Implementation Planning*
