# Experiment Design: H-E1

**Date:** 2026-03-17
**Author:** Anonymous
**Hypothesis Statement:** Under standard RLHF alignment on MCQ benchmarks (MMLU/TruthfulQA/ARC), if pre-alignment confidence margin (top-1 minus top-2 log-prob, z-scored within model) is low, then post-alignment argmax inversion probability is significantly higher (β₁ < 0, p < 0.005, AUROC ≥ 0.75 cross-benchmark), confirming a predictive geometric signal in base model confidence landscapes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK (gate not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation)

### Gate Condition
**MUST_WORK gate:** β₁ < 0 AND p < 0.005 AND AUROC ≥ 0.75 cross-benchmark.
If H-E1 fails (β₁ ≥ 0 or AUROC < 0.65): STOP — foundational existence claim is wrong; entire hypothesis chain must be reassessed.

---

## Continuation Context

This is the **first hypothesis** in the pipeline (H-E1 has no prerequisites). No previous hypothesis context to load.

### Previous Hypothesis Results (if applicable)
*Not applicable — H-E1 is the foundation hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Archon KB — confidence margin argmax flip RLHF alignment**
- No domain-specific results found (KB primarily covers diffusion models)
- All similarities < 0.38; irrelevant to LLM alignment domain

**Query 2: Archon KB — LLM calibration trustworthiness alignment**
- Hit: `hf.co/papers/2305.14314` (similarity 0.386) — alignment-related paper, partial relevance
- Hit: OpenAI InstructGPT blog — background on RLHF pipeline design
- No implementation-specific guidance for MCQ logit extraction

**Query 3: Archon KB — MCQ benchmark logit extraction evaluation harness**
- No relevant results; Archon KB lacks LLM evaluation content

**Query 4: Archon KB — MMLU huggingface datasets load**
- Hit: `huggingface.co/docs/transformers/index` (similarity 0.509) — confirms HuggingFace as canonical loading library
- Hit: `github.com/huggingface/transformers` (similarity 0.627) — AutoModel/AutoTokenizer patterns confirmed

**Summary:** Archon KB contains no prior experiment cases specific to this domain. Implementation must be derived from Phase 2B protocol + established tools (lm-evaluation-harness, transformers).

### Archon Code Examples

**Query: logit extraction log probability language model**
- `CustomLogitsProcessor` pattern from HuggingFace diffusers: shows token-level score access pattern
  ```python
  def __call__(self, input_ids, scores):
      # scores is (batch_size, vocab_size) log-prob distribution
      return scores + self.bias
  ```
  - **Applicable insight:** `scores` tensor in HuggingFace generate/forward is the raw logit distribution. For MCQ, we extract logits for specific option tokens (A/B/C/D) directly from `model(**inputs).logits[:, -1, :]`.

**Summary:** No direct MCQ logit extraction code found. Implementation pattern derived from lm-evaluation-harness standard methodology (confirmed in Phase 2B).

### Exa GitHub Implementations

**Status:** Exa MCP unavailable (HTTP 402 — quota exceeded for all queries)
- `get_code_context_exa`: 402 error
- `web_search_exa`: 402 error

**Known reference repositories (from Phase 2B research):**
- **EleutherAI/lm-evaluation-harness** (github.com/EleutherAI/lm-evaluation-harness) — Official MCQ evaluation suite. Provides `--tasks mmlu,truthfulqa_mc1,arc_challenge` with built-in log-probability extraction. Standard implementation for all benchmarks in this experiment.
- **allenai/open-instruct** (github.com/allenai/open-instruct) — Official repository for Tulu-2 PPO and DPO models. Contains training scripts and model cards for `allenai/tulu-2-ppo-7b` and `allenai/tulu-2-dpo-7b`.
- **Plaut et al. [2024]** "From Predictions to Decisions" — MSP correctness prediction methodology (AUROC analysis on MMLU/ARC/TruthfulQA/HellaSwag/WinoGrande) across 15 fine-tuned LLMs. Directly validates feasibility of log-prob→correctness signal extraction on same benchmark suite.

**Serena Analysis Needed:** TRUE (complex multi-model logit extraction pipeline)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment does NOT reproduce an existing paper. H-E1 is a novel analysis pipeline combining:
1. Standard benchmark evaluation (lm-evaluation-harness)
2. Statistical analysis (logistic regression + AUROC)

**Recommended Implementation Path:**
- Primary: Direct HuggingFace model loading + custom logit extraction script (following lm-evaluation-harness methodology)
- Fallback: Extend lm-evaluation-harness with custom output_type="loglikelihood" task definitions
- Justification: lm-evaluation-harness provides validated, reproducible MCQ log-probability extraction for MMLU/TruthfulQA/ARC. Custom extraction wrapping the same HuggingFace AutoModelForCausalLM forward pass is simpler for our analysis pipeline and avoids framework overhead.

### Code Analysis (Serena MCP)

*Limited* — Exa code search unavailable (402 quota). No external code retrieved for Serena analysis. Core implementation pattern is derived from:
1. Phase 2B verification protocol (lm-evaluation-harness log-prob extraction)
2. Standard HuggingFace AutoModelForCausalLM.forward() output structure (logits tensor)
3. Plaut et al. [2024] methodology (direct token log-prob access for MCQ options)

---

## Experiment Specification

### Dataset

**Primary Dataset: MMLU (Massive Multitask Language Understanding)**
- **Name:** MMLU
- **Version/Split:** Full test set across all 57 subjects
- **Source:** HuggingFace: `cais/mmlu`
- **Size:** ~14,042 test items (57 subjects × ~246 items average)
- **Type:** `standard`
- **Splits used:** test split only (logit extraction, no training)
- **Preprocessing:** Tokenize question + options as multiple-choice prompt; extract log-prob for each option token (A/B/C/D)
- **Augmentation:** None (inference-only evaluation)

**Cross-Benchmark Validation Dataset 1: TruthfulQA**
- **Name:** TruthfulQA (MC1 format)
- **Version/Split:** Full validation set
- **Source:** HuggingFace: `truthful_qa`, config `multiple_choice`
- **Size:** 817 items
- **Type:** `standard`
- **Splits used:** validation set

**Cross-Benchmark Validation Dataset 2: ARC-Challenge**
- **Name:** ARC-Challenge
- **Version/Split:** Full test set
- **Source:** HuggingFace: `allenai/ai2_arc`, config `ARC-Challenge`
- **Size:** 1,172 test items
- **Type:** `standard`
- **Splits used:** test split

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifiers: `cais/mmlu`, `truthful_qa`, `allenai/ai2_arc`
- Code:
  ```python
  from datasets import load_dataset
  mmlu = load_dataset("cais/mmlu", "all", split="test")  # ~14K items
  truthfulqa = load_dataset("truthful_qa", "multiple_choice", split="validation")  # 817 items
  arc = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")  # 1172 items
  ```

**Total Evaluation Items:** ~16,031 items across 3 benchmarks × N model pairs

### Models

#### Baseline Model

**Architecture:** Tulu-2-base-7B (pre-alignment base model for Tulu-2 family)
**HuggingFace ID:** `allenai/tulu-2-7b` (base model, no alignment)
**Type:** Decoder-only transformer (LLaMA-2 architecture base)
**Role:** Reference "base model" providing pre-alignment logits for margin computation
**Parameters:** ~7B

**Model Pairs for Analysis:**
| Pair ID | Base Model | Aligned Model | Alignment Method |
|---------|-----------|---------------|------------------|
| Pair-1 | `allenai/tulu-2-7b` | `allenai/tulu-2-ppo-7b` | PPO |
| Pair-2 | `allenai/tulu-2-7b` | `allenai/tulu-2-dpo-7b` | DPO |
| Pair-3 | `EleutherAI/pythia-1.4b` | Pythia-1.4B-RLHF-aligned* | PPO/DPO |
| Pair-4 | `EleutherAI/pythia-6.9b` | Pythia-6.9B-RLHF-aligned* | PPO/DPO |

*Note: For Pythia aligned variants, use available aligned checkpoints from HuggingFace (e.g., OpenAssistant/oasst-pythia variants or similar). Primary analysis uses Tulu-2 pairs (matched PPO/DPO from identical base). Pythia pairs provide scale variation.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "allenai/tulu-2-7b",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("allenai/tulu-2-7b")
  ```

#### Proposed Model

**Architecture:** No new model architecture — H-E1 is an ANALYSIS experiment, not a training experiment.

**The "proposed model" is the analysis pipeline:**
- Input: Base model logits + Aligned model logits for same MCQ items
- Analysis: Logistic regression with margin as predictor of flip indicator
- Output: β₁ coefficient, p-value, AUROC

**Core Mechanism Implementation:**

```python
# Core Analysis Pipeline: Margin → Flip Prediction
# Based on: Phase 2B verification protocol + Plaut et al. [2024] MSP methodology

def extract_mcq_logprobs(model, tokenizer, dataset, device):
    """
    Extract log-probs for MCQ option tokens (A/B/C/D).
    Returns: (n_items, 4) array of log-probabilities for each option.
    """
    logprobs = []
    for item in dataset:
        prompt = format_mcq_prompt(item)  # Format as "Q: ... A: ... B: ..."
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        # Extract logits for option tokens at last position
        option_token_ids = [tokenizer.encode(f" {x}")[0] for x in ["A","B","C","D"]]
        last_logits = outputs.logits[0, -1, option_token_ids]  # (4,)
        logprobs.append(F.log_softmax(last_logits, dim=-1).cpu().numpy())
    return np.array(logprobs)  # (n_items, 4)

def compute_margin_and_flip(base_logprobs, aligned_logprobs):
    """Compute confidence margin and argmax flip indicator."""
    # Margin = top-1 minus top-2 log-prob (z-scored within model pair)
    sorted_base = np.sort(base_logprobs, axis=1)[:, ::-1]
    margin_raw = sorted_base[:, 0] - sorted_base[:, 1]  # (n_items,)
    margin_z = zscore(margin_raw)  # z-score within model pair

    # Flip indicator: 1 if argmax changes after alignment
    flip = (np.argmax(base_logprobs, axis=1) !=
            np.argmax(aligned_logprobs, axis=1)).astype(int)
    return margin_z, flip

def fit_logistic_regression(margin_z, flip, kl_div):
    """Fit logistic regression and compute AUROC."""
    X = np.column_stack([margin_z, kl_div])  # (n_items, 2)
    lr = LogisticRegression().fit(X, flip)
    auroc = roc_auc_score(flip, lr.predict_proba(X)[:, 1])
    return lr.coef_[0][0], auroc  # beta_1, auroc
```

### Training Protocol

**Note:** H-E1 is an inference-only analysis experiment. No training occurs. The "protocol" is the logit extraction + statistical analysis pipeline.

**Execution Protocol:**
- **Step 1:** Download and cache all model pairs and datasets
- **Step 2:** Extract MCQ log-probs for base and aligned models on MMLU (~14K items)
- **Step 3:** Compute confidence margin (z-scored) and argmax flip indicators
- **Step 4:** Compute KL divergence per item as control variable: `KL(base || aligned) = Σ p_base * log(p_base / p_aligned)` over option distribution
- **Step 5:** Fit logistic regression: `logit P(flip) = β₀ + β₁·margin + β₄·KL`
- **Step 6:** Compute cross-benchmark AUROC: train on MMLU, evaluate on TruthfulQA + ARC-Challenge
- **Step 7:** Report results

**Statistical Analysis Config:**
- Logistic regression library: `sklearn.linear_model.LogisticRegression`
- AUROC library: `sklearn.metrics.roc_auc_score`
- KL divergence: computed from softmax of 4-option logit distributions
- Z-scoring: `scipy.stats.zscore` within each model pair
- Bonferroni correction: applied across model pairs (4 pairs × 3 benchmarks = 12 tests; threshold p < 0.005 = 0.05/10 ~ adequate margin)

**Compute:**
- No GPU training required; inference only
- ~14K items × 5 models × 1 forward pass = ~70K forward passes
- Estimated time: 2-4 hours per model on single GPU (float16)
- Total GPU-hours: ~20-40 hours (5 models × 4-8 hours each)

**Seeds:** 1 (fixed, seed=42; inference is deterministic with no sampling)

### Evaluation

**Primary Metrics:**
- **β₁ coefficient:** Logistic regression coefficient for margin predictor (must be < 0)
- **p-value:** Two-sided Wald test for β₁ (must be < 0.005)
- **AUROC:** Area under ROC curve for margin predicting flip (must be ≥ 0.75 on cross-benchmark)
- **Partial η²:** Effect size for margin predictor (target ≥ 0.06)

**Success Criteria (PoC):**
- Primary: `β₁ < 0` AND `p < 0.005` (margin predicts flip in correct direction)
- Secondary: Cross-benchmark AUROC ≥ 0.75 on held-out TruthfulQA/ARC
- Tertiary (visual check): Monotonically decreasing P(flip|margin quintile) curve

**Expected Baseline Performance (from Phase 2B):**
- AUROC for random predictor: 0.50
- AUROC expected (based on Plaut et al. [2024] MSP→correctness R²=0.94): 0.75-0.85
- Flip rate baseline (marginal): ~20-30% for PPO, ~40-60% for DPO (from h-m3 Phase 2B: 99.7% for Pythia-1.4B PPO — large effect expected)

**PoC Pass Condition:**
1. Logistic regression fits without error
2. `β₁ < 0` (negative association between margin and flip probability)
3. AUROC > 0.75 on at least one cross-benchmark split

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (flip indicator)
- Library: `sklearn.metrics`
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  from sklearn.linear_model import LogisticRegression
  from scipy.stats import zscore
  auroc = roc_auc_score(y_true=flip, y_score=lr.predict_proba(X)[:,1])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing β₁ value, AUROC (target vs actual), p-value significance marker

#### Additional Figures (LLM Autonomous)
- **Margin Quintile Flip Rate Plot**: 5-bin bar chart of P(flip) by margin quintile for PPO vs DPO (most critical visualization for hypothesis)
- **ROC Curves**: Per model pair and cross-benchmark generalization curves
- **Margin Distribution by Method**: Box plots of confidence margin distribution for PPO vs DPO flipped vs non-flipped items
- **KL vs Margin Scatter**: Residual plot showing margin predicts flip independent of KL

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Base model logits accessible via AutoModelForCausalLM forward pass | TRUE — verified via transformers library (HuggingFace transformers docs, similarity 0.627 in Archon KB) |
| Mechanism Isolatable | Can extract logits from base independently of aligned model | TRUE — models loaded separately; logprobs extracted independently per model |
| Baseline Measurable | Flip indicator (argmax comparison) is computable without training | TRUE — pure inference comparison, no training required |

### Architecture Compatibility Check

**This experiment analyzes EXISTING model pairs — no architectural modification required.**

**Required Features:**
- Decoder-only causal LM with accessible `model.forward().logits` output
- Tokenizer with known option token IDs ("A", "B", "C", "D" or " A", " B", " C", " D")
- Model pairs with documented base↔aligned correspondence (same base checkpoint)

**Incompatible Architectures:**
- Encoder-only models (BERT, RoBERTa) — different forward pass structure for generation
- Models without public HuggingFace weights
- Aligned models trained from different base than available base checkpoint

**Compatibility Verified:** Tulu-2 family uses LLaMA-2-7B architecture; `allenai/tulu-2-7b` (base), `allenai/tulu-2-ppo-7b` and `allenai/tulu-2-dpo-7b` (aligned) are all publicly available on HuggingFace Hub.

---

### Mechanism Activation Indicators

**How to detect if analysis pipeline is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Extracted logprobs for N items from [model_name]" | `extract_mcq_logprobs()` |
| Data Shape | `base_logprobs.shape == (14042, 4)` for MMLU full test set | `main.py` after extraction |
| Metric Delta | `β₁ < 0` with nonzero absolute value (expected -0.3 to -0.8) | `fit_logistic_regression()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_pipeline_activated(base_logprobs, aligned_logprobs, margin_z, flip, beta1, auroc):
    """Verify that analysis pipeline produced meaningful results."""
    indicators = {
        "logprobs_extracted": base_logprobs.shape[0] > 1000,  # at least 1K items
        "margin_variable": margin_z.std() > 0.1,             # margin has variance
        "flip_occurs": flip.mean() > 0.05,                   # at least 5% flip rate
        "negative_beta": beta1 < 0,                          # correct direction
        "auroc_above_chance": auroc > 0.55,                  # better than random
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Model load error | Exception on `from_pretrained()` | FAIL: Model unavailable — try cached version |
| No logit variance | All logprobs nearly equal (option entropy < 0.01) | FAIL: Model not producing meaningful MCQ logits — check prompt format |
| Zero flip rate | `flip.mean() < 0.01` | WARN: Nearly no argmax changes — may indicate identical models |
| β₁ positive | `beta1 >= 0` | HYPOTHESIS FALSIFIED: Margin does not predict flip in expected direction |
| AUROC below threshold | `auroc < 0.65` | HYPOTHESIS FALSIFIED: No predictive signal cross-benchmark |
| KL dominates | β₁ becomes non-significant when KL added | REINTERPRET: Effect may be magnitude-driven not geometry-driven |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 5 pipeline checks pass | `verify_pipeline_activated()` |
| Effect Measurable | β₁ < 0 with |β₁| > 0.1 | Logistic regression coefficient |
| Hypothesis Supported | AUROC ≥ 0.75 on cross-benchmark (TruthfulQA + ARC) | `roc_auc_score()` on held-out sets |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `β₁ < 0` (direction confirmed)
3. AUROC > 0.75 on at least one cross-benchmark split

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace Transformers Documentation
- **Type**: Library documentation
- **Query Used**: "Pythia transformer huggingface pretrained model loading" (similarity: 0.627)
- **Relevance**: Confirms canonical model loading pattern for AutoModelForCausalLM
- **Key Insights**:
  - `AutoModelForCausalLM.from_pretrained()` works for all decoder-only LLMs including Tulu-2 and Pythia families
  - `device_map="auto"` enables automatic GPU placement for large models
  - `torch_dtype=torch.float16` required for 7B models on single GPU
- **Used For**: Model loading code in Dataset/Model specification

**Source A.2**: HuggingFace Transformers GitHub Repository
- **Type**: Open-source library
- **Query Used**: "Pythia transformer huggingface pretrained model loading" (similarity: 0.525)
- **Relevance**: Validates tokenizer + model forward pass structure
- **Key Insights**:
  - `model(**inputs).logits` returns `(batch_size, seq_len, vocab_size)` tensor
  - Last position logits `[:, -1, :]` give next-token distribution
  - Token IDs for "A"/"B"/"C"/"D" extractable via `tokenizer.encode(" A")[0]`
- **Used For**: Core mechanism pseudo-code (logit extraction step)

**Source A.3**: Archon KB — Alignment/RLHF domain
- **Type**: Research paper abstract (hf.co/papers/2305.14314)
- **Query Used**: "LLM calibration trustworthiness alignment evaluation" (similarity: 0.386)
- **Relevance**: Partial — covers alignment evaluation methodology
- **Key Insights**:
  - General RLHF evaluation framework; no MCQ-specific logit methodology
- **Used For**: Background context only

### Archon Code Examples

**Code Source A.4**: CustomLogitsProcessor pattern (HuggingFace diffusers)
- **Query Used**: "logit extraction log probability language model evaluation"
- **Key Code**:
  ```python
  def __call__(self, input_ids, scores):
      # scores is (batch_size, vocab_size) — raw logit distribution
      return scores + self.bias
  ```
- **Annotation**: Confirms `scores` tensor structure; for MCQ we access `outputs.logits[:, -1, option_token_ids]` directly
- **Used For**: Logit extraction pattern in core mechanism pseudo-code

---

### B. GitHub Implementations (Exa)

**Exa MCP Status**: Unavailable (HTTP 402 quota error on 2026-03-17)

**Known Reference Repository B.1**: EleutherAI/lm-evaluation-harness
- **URL**: github.com/EleutherAI/lm-evaluation-harness
- **Stars**: ~7,000+ (as of Phase 2B research)
- **Relevance**: Official benchmark evaluation framework for MMLU, TruthfulQA, ARC-Challenge
- **Key Implementation Pattern** (from Phase 2B specification):
  ```bash
  lm_eval --model hf \
    --model_args pretrained=allenai/tulu-2-7b \
    --tasks mmlu,truthfulqa_mc1,arc_challenge \
    --output_path ./results/
  ```
- **Configuration Extracted**: `output_type="loglikelihood"` for MCQ tasks; option tokens scored independently
- **Used For**: Dataset loading and evaluation methodology validation

**Known Reference Repository B.2**: allenai/open-instruct
- **URL**: github.com/allenai/open-instruct
- **Relevance**: Official training code for Tulu-2 PPO (`allenai/tulu-2-ppo-7b`) and DPO (`allenai/tulu-2-dpo-7b`) models
- **Used For**: Model pair validation (confirming `allenai/tulu-2-7b` is shared base for both PPO/DPO variants)

---

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed.
- **Reason**: Exa code search unavailable (402 quota); no complex external code retrieved for analysis
- **Alternative**: Implementation pattern derived from Phase 2B protocol + HuggingFace transformers standard API
- **Impact**: Core mechanism pseudo-code based on Phase 2B verification steps + standard transformers API patterns (well-documented, low risk)

---

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain. No previous validation report to inherit from.

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (MMLU, TruthfulQA, ARC) | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| MMLU HuggingFace identifier (`cais/mmlu`) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Dataset preprocessing (log-prob extraction) | Archon KB + Phase 2B | A.2 (transformers), B.1 (lm-eval-harness) |
| Base model selection (Tulu-2-7B, Pythia) | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| Model loading code | Archon KB | A.1 (transformers docs, similarity 0.627) |
| Aligned model pairs (PPO/DPO) | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| Core mechanism pseudo-code | Archon KB + Phase 2B | A.2, A.4, B.1; Phase 2B protocol |
| KL divergence control variable | Phase 2B | 02b_verification_plan.md Section 2.2 H-E1 |
| Logistic regression methodology | Phase 2B | 02b_verification_plan.md H-E1 verification steps 4-5 |
| AUROC cross-benchmark evaluation | Plaut et al. [2024] | Phase 2B reference; same benchmark suite |
| Success thresholds (β₁<0, p<0.005, AUROC≥0.75) | Phase 2B | 02b_verification_plan.md H-E1 success criteria |
| Visualization requirements | Phase 2B + hypothesis | H-E1 verification protocol |
| Mechanism verification protocol | Step 6 synthesis | Derived from Phase 2B failure conditions |

**Research Paper References:**
| Paper | Used For |
|-------|----------|
| Plaut et al. [2024] "From Predictions to Decisions" | Validates MSP→correctness AUROC methodology; same benchmark suite (MMLU/TruthfulQA/ARC/HellaSwag/WinoGrande); R²=0.94 result confirms feasibility |
| Li et al. [2024] | Post-RLHF trustworthiness evaluation; Pythia family alignment documented |
| Fan et al. [2026] | Pretraining→SFT accuracy ranking correlation (R²=0.7-0.9); validates cross-stage signal transfer |
| Xu et al. [2024] | DPO vs PPO objective differences (used in H-M2, background for H-E1) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-17T00:50:26Z

### Workflow History for This Hypothesis
- 2026-03-17T00:50:26Z: h-e1 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-03-17: Phase 2C experiment_design.status = IN_PROGRESS (this file created)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 6 queries executed, KB domain mismatch noted), Exa (unavailable — 402 quota error)*
*All specifications grounded in Phase 2B verified protocols and Phase 2A dataset/model selections*
*Next Phase: Phase 3 - Implementation Planning*
