# Experiment Design: H-E1

**Date:** 2026-08-02
**Author:** Anonymous
**Hypothesis Statement:** SE_N5 (bidirectional DeBERTa-MNLI NLI clustering, N=5, temp=0.7) and min_logprob (greedy decode minimum token log-probability) are empirically conditionally independent uncertainty signals on TriviaQA dev with Llama-3.1-8B: Pearson |r|(SE, min_logprob) < 0.7, and SE contributes partial R² ≥ 0.02 in conditional logistic regression [logit(h=1) ~ min_logprob + SE + L + SE×min_logprob] predicting correctness under LM-as-a-judge labels.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (H-E1 is root hypothesis — no prerequisites)
**Gate Status:** MUST_WORK — Pearson |r|(SE, min_logprob) < 0.7 AND partial R²(SE) ≥ 0.02

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

MUST_WORK gate: Both conditions must pass —
1. Pearson |r|(SE_N5, min_logprob) < 0.7
2. Partial R²(SE) ≥ 0.02 in conditional LR [logit(h=1) ~ min_logprob + SE + L + SE×min_logprob] (LRT p < 0.05)

If |r| > 0.85 → ABANDON (SE is a reparameterization of log-prob; entire chain blocked).
If 0.7 < |r| < 0.85 OR partial R² < 0.02 → EXPLORE (N=10 ablation).

---

## Continuation Context

H-E1 is the root hypothesis with no prior hypothesis results. This is a fresh experiment.

### Previous Hypothesis Results (if applicable)

None — H-E1 is the first hypothesis in the verification chain.

**Established facts to build on (DO NOT RE-VERIFY):**
- SE pipeline non-degenerate: fraction_degenerate=0.000, SE_variance=0.1522 on TriviaQA dev with Llama-3.1-8B at temp=0.7 (h-e1 snapshot 2026-08-02, 90 prompts)
- full_seq_log_prob AUROC ~0.825 on TriviaQA dev (Llama-3.1-8B) — from h-m1 limitation record, 300/2500 samples
- Hidden-state trajectory SVD PROHIBITED (AUROC=0.537 after length control) — h-e1 FAIL record

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Semantic entropy NLI clustering experiment design**
- Archon KB returned low-relevance results (similarity ~0.40) — KB primarily contains diffusion model literature, not LLM uncertainty quantification.
- **Key insight from available results:** HuggingFace Transformers library is the standard tool for loading DeBERTa-MNLI models used in semantic entropy clustering (confirmed via hf.co/papers/2305.14314 reference).
- **Applied:** Use `cross-encoder/nli-deberta-v3-small` or `microsoft/deberta-large-mnli` for NLI entailment classification in SE pipeline.

**Query 2: Log probability uncertainty calibration best practices**
- Archon KB: Low relevance (similarity ~0.49) — returned diffusion model training configs.
- **Applied:** min_logprob implementation derived from Exa/paper sources (see below).

**Query 3: TriviaQA dataset AUROC benchmark**
- Archon KB: Low relevance — returned video generation dataset docs.
- **Applied:** Dataset loading details derived from HuggingFace dataset card (Exa search, see below).

**Assessment:** Archon KB does not contain LLM uncertainty quantification literature for this research domain. All implementation grounding comes from Exa GitHub search and paper sources.

### Archon Code Examples

**Query: semantic entropy logprob conditional logistic regression**
- Archon code search returned diffusion model and image generation code (similarity < 0.35).
- No relevant LLM UQ code found in Archon KB.
- **Applied:** Code patterns from jlko/semantic_uncertainty (Exa, official implementation) used as primary reference.

### Exa GitHub Implementations

**Query 1: jlko/semantic_uncertainty — Official Implementation (HIGHEST PRIORITY)**

**Repository 1**: jlko/semantic_uncertainty
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Relevance:** Official author implementation of Kuhn et al. 2023/2024 Nature paper — exact codebase for SE_N5 computation
- **Architecture:** Three-stage pipeline: `generate_answers.py` → `compute_uncertainty_measures.py` → `analyze_results.py`
- **Key Code (SE clustering):**
  ```python
  def get_semantic_ids(strings_list, model, strict_entailment=False, example=None):
      """Group list of predictions into semantic meaning."""
      def are_equivalent(text1, text2):
          implication_1 = model.check_implication(text1, text2, example=example)
          implication_2 = model.check_implication(text2, text1, example=example)
          # Non-strict: no contradiction AND not both neutral
          semantically_equivalent = (0 not in [implication_1, implication_2]) and \
                                     ([1, 1] != [implication_1, implication_2])
          return semantically_equivalent
      # Assign cluster IDs via transitive closure
      ...

  def cluster_assignment_entropy(semantic_ids):
      """SE from cluster assignment frequencies — no token likelihoods."""
      n_generations = len(semantic_ids)
      counts = np.bincount(semantic_ids)
      probabilities = counts / n_generations
      entropy = -(probabilities * np.log(probabilities)).sum()
      return entropy
  ```
- **Dataset:** TriviaQA supported natively (`--dataset=trivia_qa`)
- **NLI Model:** DeBERTa-large via HuggingFace transformers; `strict_entailment=False` (bidirectional, non-strict)
- **N=5 samples:** Configurable via `--num_few_shot` and generation params

**Repository 2**: BuffaloTechRider/zero-shot-llm-confidence-estimation
- **URL:** https://github.com/BuffaloTechRider/zero-shot-llm-confidence-estimation
- **Relevance:** Directly benchmarks average token log-probability on Llama-3.1-8B and TriviaQA
- **Architecture:** `datasets.py` (TriviaQA loader), `labeling.py` (LLM-judge + regex), `ablation_experiment.py` (AUROC)
- **Key Results:** logprob AUROC 0.650 (Llama-3.1-8B MMLU-Pro), 0.782 avg TriviaQA — confirms logprob is a strong signal
- **Training Config:** Zero-shot (no training); AUROC evaluation via sklearn
- **Dataset:** TriviaQA n=500 queries per model

**Query 2: UQLM min_token_negentropy / min_probability**
- **Source:** cvs-health/uqlm, JMLR 2025 paper
- **Key insight:** min_token_probability (Manakul et al. 2023) = minimum token probability across greedy decode; used as "weakest link" detector
- **Implementation:**
  ```python
  # min_logprob = min of per-token log probabilities across greedy decode
  min_logprob = min(token_logprobs_from_greedy_decode)
  ```
- **Note:** Our `min_logprob` uses log-probability (not negentropy), directly from greedy forward pass token scores

**Query 3: First-Token Confidence paper (Exa)**
- **Source:** arxiv 2605.05166 — "The First Token Knows"
- **Key finding:** Pearson r(first_token_confidence, semantic_agreement) = 0.54–0.76 on TriviaQA/PopQA with Llama-3.1-8B — **directly relevant**: shows that single-decode logprob signals ARE correlated with SE-family signals at r=0.54–0.76, but below |r|=0.85 threshold; suggests our |r|(SE_N5, min_logprob) < 0.7 threshold is plausible but tight.
- **Key Numbers:** mean AUROC φ_first = 0.820, semantic agreement = 0.793; logistic ensemble = +0.02 over φ_first alone

**Serena Analysis Needed:** FALSE — code from jlko/semantic_uncertainty is clear and self-contained. No complex unfamiliar architecture requiring semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: Paper reproduction experiments prioritize author's official implementation**

- SE_N5: Use jlko/semantic_uncertainty as primary reference; adapt `get_semantic_ids` + `cluster_assignment_entropy` for N=5 samples with DeBERTa-MNLI
- min_logprob: Implement as `min(token_log_probs)` from greedy decode — simple Python expression; no external library needed

**Recommended Implementation Path:**
- Primary: jlko/semantic_uncertainty (official SE implementation, TriviaQA-tested)
- Fallback: UQLM WhiteBoxUQ for min_logprob if HuggingFace tokenizer logprob extraction is complex
- Justification: Official implementation matches paper protocol exactly; avoids reimplementation risk

### Code Analysis (Serena MCP)

*Skipped* — Code from jlko/semantic_uncertainty is sufficiently clear. SE clustering logic is <30 lines and fully readable from Exa results. No Serena analysis required.

---

## Experiment Specification

### Dataset

**Primary Dataset: TriviaQA dev (rc.nocontext split)**

| Field | Value |
|-------|-------|
| Name | TriviaQA |
| Version | HuggingFace `mandarjoshi/trivia_qa`, config `rc.nocontext` |
| Split | `validation` (11,313 examples total; use first 2500) |
| Task | Closed-book short-answer QA |
| Answer format | Aliases list (`answer.aliases`, `answer.normalized_aliases`) |
| Type | standard |

**Preprocessing:**
- Load `rc.nocontext` (no document context — closed-book setting)
- Use `question` field as prompt; `answer.aliases` for correctness checking
- No special tokenization preprocessing needed — raw question text fed to LLM
- Shuffle with fixed seed=42, take first 2500 for consistency with h-m1 baseline

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"mandarjoshi/trivia_qa"`, config `"rc.nocontext"`, split `"validation"`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")
  dataset = dataset.shuffle(seed=42).select(range(2500))
  ```

### Models

#### Baseline Model

**Llama-3.1-8B-Instruct as primary generator**

| Field | Value |
|-------|-------|
| Architecture | Llama-3.1 (decoder-only transformer, 8B params) |
| Role | Primary response generator (stochastic N=5 + greedy×1) |
| Source | HuggingFace `meta-llama/Llama-3.1-8B-Instruct` |
| Validated | SE_variance=0.1522 at temp=0.7 N=5 (h-e1 snapshot) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-3.1-8B-Instruct"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-3.1-8B-Instruct",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
  ```

**NLI Judge Model (for SE clustering):**
- Identifier: `"cross-encoder/nli-deberta-v3-small"` (lightweight) or `"microsoft/deberta-large-mnli"` (paper-exact)
- Code:
  ```python
  from transformers import pipeline
  nli_pipeline = pipeline("zero-shot-classification",
                          model="cross-encoder/nli-deberta-v3-small")
  ```

#### Proposed Model

**Architecture:** Same Llama-3.1-8B-Instruct + SE_N5 signal extraction (no model modification — SE is a post-hoc computation over N=5 stochastic samples)

**Core Mechanism Implementation:**

```python
# Core Mechanism: SE_N5 + min_logprob Conditional Independence Test
# Based on: jlko/semantic_uncertainty (official Kuhn et al. 2023/2024 implementation)

import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

def compute_se_n5(responses: list[str], nli_model) -> float:
    """SE from cluster assignment entropy over N=5 samples."""
    semantic_ids = get_semantic_ids(responses, nli_model)
    counts = np.bincount(semantic_ids)
    probs = counts / len(semantic_ids)
    return -(probs * np.log(probs + 1e-10)).sum()

def compute_min_logprob(token_logprobs: list[float]) -> float:
    """Minimum token log-probability from greedy decode."""
    return min(token_logprobs)  # weakest link = most uncertain token

def run_conditional_independence_test(
    se_scores: np.ndarray,          # shape (N_prompts,)
    min_logprob_scores: np.ndarray, # shape (N_prompts,)
    response_lengths: np.ndarray,   # shape (N_prompts,) — char/token count
    correctness_labels: np.ndarray  # shape (N_prompts,) — binary {0,1}
) -> dict:
    # Step 1: Pearson correlation (raw)
    r, p_r = pearsonr(se_scores, min_logprob_scores)

    # Step 2: Circularity check
    rho_se_judge, _ = spearmanr(se_scores, correctness_labels)

    # Step 3: Conditional LR — full model
    X_full = np.column_stack([
        min_logprob_scores, se_scores,
        response_lengths, se_scores * min_logprob_scores
    ])
    # Step 4: Reduced model (without SE)
    X_reduced = np.column_stack([min_logprob_scores, response_lengths])

    lr_full = LogisticRegression(max_iter=1000).fit(X_full, correctness_labels)
    lr_reduced = LogisticRegression(max_iter=1000).fit(X_reduced, correctness_labels)

    # Step 5: Partial R² via McFadden (likelihood ratio)
    ll_full = lr_full.score(X_full, correctness_labels)
    ll_reduced = lr_reduced.score(X_reduced, correctness_labels)
    partial_r2_se = 1 - (ll_full / ll_reduced)  # approx LRT-based

    return {
        "pearson_r": r, "pearson_p": p_r,
        "partial_r2_se": partial_r2_se,
        "rho_se_judge": rho_se_judge,
        "gate_pass": abs(r) < 0.7 and partial_r2_se >= 0.02
    }
```

### Training Protocol

This is a **diagnostic experiment** — no model training occurs. The "training protocol" describes the inference and statistical testing procedure.

**Generation Protocol (Stochastic, N=5):**
- Model: Llama-3.1-8B-Instruct
- Temperature: 0.7
- N samples: 5 per prompt (for SE clustering)
- Max new tokens: 50 (short-answer QA)
- Top-p: 0.95
- Source: jlko/semantic_uncertainty default params for short-phrase experiments

**Generation Protocol (Greedy, ×1):**
- Temperature: 0.0 (greedy)
- Purpose: Extract per-token log-probabilities for min_logprob computation
- Return: `output_scores` from HuggingFace `generate()` call

**Statistical Test:**
- Pearson r: `scipy.stats.pearsonr(se_scores, min_logprob_scores)`
- Conditional LR: `sklearn.linear_model.LogisticRegression` with L2 penalty (C=1.0)
- Partial R²: McFadden-style likelihood ratio (full model vs. model without SE term)
- Circularity check: `scipy.stats.spearmanr(se_scores, lm_judge_labels)`

**Seeds:** 1 (fixed, seed=42 for dataset shuffle and generation if using sampling)

**Correctness Labels:**
- LM-as-a-judge: Cross-model judge (Qwen-2.5-7B or GPT-4o-mini) evaluating Llama-3.1-8B greedy answer against TriviaQA answer aliases
- Judge prompt: "Is the following answer correct for the question? Answer YES or NO."

> ⚠️ **EXISTENCE (PoC):** Single seed sufficient. No hyperparameter search. No multiple seeds.

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Pearson \|r\|(SE, min_logprob) | Absolute Pearson correlation between SE_N5 and min_logprob across 2500 prompts | < 0.7 |
| Partial R²(SE) in conditional LR | McFadden partial R² for SE term in [logit(h=1) ~ min_logprob + SE + L + SE×min_logprob] | ≥ 0.02 |
| ρ(SE, LM-judge) | Spearman correlation between SE and cross-model judge correctness | < 0.4 (circularity check) |

**Success Criteria:**
- proposed_outcome > baseline_threshold: Pearson |r| < 0.7 AND partial R²(SE) ≥ 0.02 (both must pass)
- Secondary: ρ(SE, LM-judge) < 0.4

**Expected Baseline Performance (from research):**
- First-Token Confidence vs SE correlation: r = 0.54–0.76 (arxiv 2605.05166, Llama-3.1-8B, TriviaQA)
- This suggests min_logprob vs SE_N5 correlation is likely in 0.4–0.7 range — plausible to pass |r| < 0.7 gate
- Source: "The First Token Knows" (arxiv 2605.05166)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (correctness prediction) + correlation analysis
- Library: `scipy.stats` (pearsonr, spearmanr), `sklearn.linear_model` (LogisticRegression), `sklearn.metrics` (roc_auc_score)
- Code:
  ```python
  from scipy.stats import pearsonr, spearmanr
  from sklearn.linear_model import LogisticRegression
  from sklearn.metrics import roc_auc_score
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing |r|(SE, min_logprob) vs threshold 0.7; partial R²(SE) vs threshold 0.02

#### Additional Figures (LLM Autonomous)

Based on the experiment:
1. **Scatter plot:** SE_N5 vs min_logprob (2500 points), colored by correctness label — visually demonstrates correlation structure
2. **Correlation matrix heatmap:** [SE_N5, min_logprob, response_length, LM-judge_correctness] — full feature correlation overview
3. **Conditional LR coefficients bar chart:** β coefficients with 95% CI for [min_logprob, SE, L, SE×min_logprob]

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Pearson |r|(SE_N5, min_logprob) < 0.7 AND partial R²(SE) ≥ 0.02

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | SE_N5 and min_logprob are algebraically distinct computations (SE: cluster entropy over N=5 samples; min_logprob: min token log-prob from greedy decode) | TRUE — by construction |
| Mechanism Isolatable | Can compute SE_N5 alone, min_logprob alone, or together — independent computations | TRUE |
| Baseline Measurable | Pearson r and partial R² can be computed with or without SE term | TRUE |

### Architecture Compatibility Check

**No model architecture modification required.** H-E1 is a diagnostic experiment:
- SE_N5: Post-hoc computation over N=5 stochastic generations from Llama-3.1-8B-Instruct
- min_logprob: Extracted from `output.scores` of HuggingFace `generate()` greedy decode

**Required Features:**
- Llama-3.1-8B-Instruct: Must expose `output_scores=True` in `generate()` for log-prob access
- DeBERTa-MNLI: Must be loadable via HuggingFace transformers pipeline

**Incompatible Architectures:**
- Black-box APIs that do not expose token log-probabilities (cannot compute min_logprob)
- Tokenizer configurations that do not produce per-token scores

> ⚠️ If Llama-3.1-8B does not expose `output_scores`, Phase 4 MUST fail early with explicit error.

### Mechanism Activation Indicators

**How to detect if mechanism (independence test) is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "SE_N5 computed for N=2500 prompts; variance={val}" (val > 0.05) | generate.py logging |
| Tensor Shape | SE scores shape: (2500,); min_logprob shape: (2500,) | compute_signals.py assertions |
| Metric Delta | Pearson r computed and printed; partial R² computed and printed | stats_analysis.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(se_scores, min_logprob_scores, results):
    indicators = {
        "se_nondegenerate": np.var(se_scores) > 0.01,          # SE has discriminative variance
        "minlogprob_valid": np.all(min_logprob_scores < 0),    # all log-probs are negative
        "n_samples_correct": len(se_scores) == len(min_logprob_scores),
        "correlation_computed": "pearson_r" in results,
        "partial_r2_computed": "partial_r2_se" in results
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| SE all-zero | np.var(se_scores) < 0.001 | FAIL: SE degenerate (all prompts in 1 cluster) |
| min_logprob all-zero | np.all(min_logprob == 0) | FAIL: log-prob extraction failed |
| N < 2500 | len(se_scores) != 2500 | WARN: Insufficient samples, recheck dataset loading |
| NLI model unavailable | ImportError or model download failure | FAIL: Cannot compute SE without NLI model |
| Judge not cross-model | Same model family as generator | FAIL: Circularity risk — use different judge |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (all indicators pass) | verify_mechanism_activated() |
| Effect Measurable | Pearson r computed without NaN | pearsonr() returns finite value |
| Hypothesis Supported | |r| < 0.7 AND partial R² ≥ 0.02 | results["gate_pass"] == True |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB did not contain relevant LLM uncertainty quantification literature. All Archon queries returned diffusion model / image generation content (similarity < 0.50). Three queries executed; zero relevant results.

- Query 1: "semantic entropy NLI clustering uncertainty quantification experiment design" → similarity 0.40, diffusion model results
- Query 2: "log probability uncertainty calibration LLM implementation best practices" → similarity 0.50, diffusion model configs
- Query 3: "TriviaQA dataset loading HuggingFace evaluation AUROC QA benchmark" → similarity 0.49, video generation datasets

**Used For:** Archon did not contribute implementation guidance. All grounding from Exa GitHub sources.

---

### B. GitHub Implementations (Exa)

**Repository 1**: jlko/semantic_uncertainty
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Query Used:** "jlko semantic_uncertainty semantic entropy Kuhn 2023 TriviaQA implementation GitHub"
- **Relevance:** Official author implementation for Nature 2024 paper — ground truth for SE_N5 computation
- **Key Code** (annotated):
  ```python
  # get_semantic_ids: assigns cluster IDs via bidirectional NLI entailment check
  # Non-strict mode: equivalent if no contradiction AND not both neutral
  # cluster_assignment_entropy: SE = entropy of cluster frequency distribution
  # Does NOT use token likelihoods — purely sampling-based signal
  ```
- **Configuration Extracted:** N=5-10 samples; DeBERTa-large-mnli; TriviaQA rc.nocontext; strict_entailment=False
- **Their Results:** SE AUROC > normalized entropy and predictive entropy on TriviaQA (OPT-30B)
- **Used For:** SE_N5 computation implementation (clustering logic + entropy formula)

**Repository 2**: BuffaloTechRider/zero-shot-llm-confidence-estimation
- **URL:** https://github.com/BuffaloTechRider/zero-shot-llm-confidence-estimation
- **Query Used:** "min_logprob minimum token log probability uncertainty LLM Python implementation TriviaQA AUROC"
- **Relevance:** Benchmarks average token log-prob on Llama-3.1-8B + TriviaQA — provides AUROC reference numbers
- **Configuration Extracted:** `datasets.py` TriviaQA loader; `labeling.py` LLM-judge; n=500 queries per model
- **Their Results:** avg logprob AUROC 0.650 (Llama-3.1-8B MMLU-Pro), 0.782 avg TriviaQA
- **Used For:** min_logprob implementation pattern; LLM-judge labeling approach reference

**Repository 3**: UQLM (cvs-health/uqlm) + arxiv 2605.05166
- **URL:** https://cvs-health.github.io/uqlm; https://arxiv.org/html/2605.05166v1
- **Query Used:** "min_logprob minimum token log probability uncertainty LLM Python implementation"
- **Relevance:** Formal definition of min_token_probability scorer; Pearson r between first-token confidence and semantic agreement
- **Key Finding:** Pearson r(first_token_confidence, semantic_agreement) = 0.54–0.76 on Llama-3.1-8B TriviaQA — calibrates expected |r|(SE_N5, min_logprob)
- **Used For:** min_logprob definition; |r| < 0.7 threshold plausibility assessment

---

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from jlko/semantic_uncertainty was sufficiently clear from Exa results. SE clustering logic is ~25 lines and fully readable. No Serena MCP call required.

---

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

**Infrastructure reuse from prior h-e1 snapshot:**
- Prior h-e1 snapshot (2026-08-02, 90 prompts) validated SE pipeline non-degeneracy
- Can reuse `generate.py` and `compute_signals.py` infrastructure if available in codebase
- If not, implement fresh based on jlko/semantic_uncertainty reference

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: TriviaQA rc.nocontext, validation split | HuggingFace dataset card | Exa: mandarjoshi/trivia_qa HF page |
| Dataset loading code | HuggingFace datasets API | Exa: TriviaQA dataset card README |
| SE_N5 clustering logic | GitHub | Exa: jlko/semantic_uncertainty (B.1) |
| SE entropy formula | GitHub + Paper | Exa: jlko/semantic_uncertainty cluster_assignment_entropy |
| min_logprob definition | UQLM paper + arxiv | Exa: UQLM min_token_probability (B.3) |
| Expected |r| range (0.54–0.76) | Arxiv paper | Exa: arxiv 2605.05166 "The First Token Knows" (B.3) |
| Conditional LR partial R² method | Statistical standard | Phase 2B hypothesis spec |
| NLI model: DeBERTa-MNLI | GitHub | Exa: jlko/semantic_uncertainty README (B.1) |
| LLM-judge approach | GitHub | Exa: BuffaloTechRider (B.2) |
| Success thresholds (|r|<0.7, R²≥0.02) | Phase 2B gate spec | 02b_verification_plan.md H-E1 section |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-02

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| h-e1 set to IN_PROGRESS | 2026-08-02T15:50:06 | Hypothesis Loop |
| Phase 2C experiment_design.status = COMPLETED | 2026-08-02 | Phase 2C |

---

*MCP Tools Used: Archon (Knowledge + Code — low relevance, LLM UQ not in KB), Exa (GitHub — jlko/semantic_uncertainty, BuffaloTechRider, UQLM, arxiv 2605.05166), Serena (Skipped — code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
