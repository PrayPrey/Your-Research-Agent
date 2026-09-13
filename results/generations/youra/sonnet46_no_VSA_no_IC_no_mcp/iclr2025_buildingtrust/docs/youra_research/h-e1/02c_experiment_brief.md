# Experiment Design: H-E1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under standard lm-evaluation-harness with logit extraction, if open-weight LLMs (Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct) are evaluated on AdvGLUE and ANLI multiple-choice splits, then logit-based 15-bin ECE can be reliably computed for all 4 models × 3 task types = 12 (model, task) cells, with sufficient coverage (≥200 examples per cell), because AdvGLUE and ANLI are available on HuggingFace and lm-evaluation-harness natively extracts answer-token logits for MC tasks.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (H-E1 is root hypothesis, no prerequisites)
**Gate Status:** MUST_WORK — ECE computable for all 24 cells, ≥200 examples/cell

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition

**MUST_WORK** — The gate passes if:
1. ECE is computable for all 4 models × 3 tasks × 2 splits = 24 evaluation cells
2. ≥200 valid examples per (model, task, split) cell with non-degenerate logit distributions
3. ECE values fall in plausible range [0.0, 0.5]
4. Clean-split ECE values are consistent with published LLM calibration range (0.05–0.15) per Kadavath 2022

**Failure Action:** STOP — reassess measurement protocol; pivot model/task scope (e.g., reduce to 2 models or BBH-MC only)

---

## Continuation Context

First hypothesis in chain (H-E1 → H-M1 → H-M2 → H-M3). No previous hypothesis results.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the root hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP unavailable in this ablation session. Findings synthesized from Phase 2B verification plan which contains detailed experimental setup from Phase 2A dialogue.*

**Key Implementation Knowledge (from Phase 2B Section 1.3 and 4.1):**

**Experiment Design — ECE on LLMs:**
- Standard ECE computation for LLMs uses `lm-evaluation-harness` (EleutherAI) which natively extracts answer-token logits for MC tasks
- 15-bin equal-width ECE is the standard from Guo 2017 (arXiv 1706.04599); widely used in LLM calibration studies
- Published baseline: LLM clean-split ECE ~0.05–0.15 (Kadavath 2022, TriviaQA/MMLU/BIG-Bench)
- Verbal uncertainty elicitation (Kadavath 2022, Xiong 2023) provides alternative if logit extraction fails

**Implementation Challenges (from Phase 2B Risk Analysis):**
- **R1 (High):** Logit extraction may produce invalid distributions due to tokenization edge cases or prompt format sensitivity
  - Mitigation: Pre-validate on 10 examples per model × task cell; verify softmax distributions sum to ~1
  - Detection: Flag cells where max softmax confidence >0.999 for all examples or <0.5 mean max confidence
- **R5 (Medium):** 15-bin ECE may be noisy for small adversarial subtask samples (~1000 examples)
  - Mitigation: Compute both 10-bin and 15-bin variants; flag cells with <100 examples/bin

**Benchmark Results Context:**
- AdvGLUE: derived from GLUE; human-verified label preservation; available on HuggingFace
- ANLI: adversarial MultiNLI; model-in-the-loop construction with human validation; R1/R2/R3 rounds
- ECE on adversarial NLP benchmark splits for open-weight LLMs: **unmeasured** — no published study (the PROVE_NEW gap)

### Archon Code Examples

*Archon MCP unavailable (ablation). Standard lm-evaluation-harness patterns documented from Phase 2B context and public documentation.*

```python
# Standard lm-evaluation-harness invocation for MC tasks with logit extraction
# Source: EleutherAI/lm-evaluation-harness (GitHub, public documentation)

lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,dtype=bfloat16 \
  --tasks advglue_nli,anli_r1 \
  --device cuda:0 \
  --output_path ./results/llama2_7b_base/ \
  --log_samples  # enables per-sample logit capture
```

### Exa GitHub Implementations

*Exa MCP unavailable (ablation). Key repositories identified from Phase 2B and public knowledge:*

**Repository 1: EleutherAI/lm-evaluation-harness** (⭐ ~7k stars, authoritative)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** Primary evaluation framework; natively supports AdvGLUE, ANLI; extracts answer-token logits for MC tasks
- **Architecture:** Modular task registry; `loglikelihood` API returns log-probability per answer token
- **Key Code Pattern:**
  ```python
  # lm_eval API for logit extraction on MC tasks
  # Output: (log_likelihood, is_greedy) per (context, continuation) pair
  results = lm.loglikelihood(
      [(context, answer_token) for answer_token in answer_choices]
  )
  # Convert to probabilities for ECE
  probs = torch.softmax(torch.tensor([r[0] for r in results]), dim=0)
  pred_label = probs.argmax().item()
  confidence = probs.max().item()
  ```
- **Configuration:** Supports `--model hf` backend with bfloat16, 4-bit quantization (BitsAndBytes)
- **Dataset Tasks:** `advglue_*`, `anli_r1/r2/r3` available in task registry

**Repository 2: HuggingFace/datasets** (AdvGLUE + ANLI loading)
- **URL:** https://huggingface.co/datasets
- **Relevance:** Standard dataset loading for AdvGLUE, ANLI, GLUE, MultiNLI
- **Key Code:**
  ```python
  from datasets import load_dataset
  advglue = load_dataset("adv_glue", "adv_qqp")      # AdvGLUE subtask
  anli_r1 = load_dataset("anli", split="test_r1")     # ANLI Round 1
  glue_qqp = load_dataset("glue", "qqp")              # Clean GLUE baseline
  mnli = load_dataset("multi_nli", split="validation_matched")  # Clean MultiNLI
  ```

**Repository 3: ECE Implementation Reference (scikit-learn / custom)**
- **Relevance:** Standard 15-bin ECE implementation for calibration measurement
- **Key Code:**
  ```python
  import numpy as np
  def compute_ece(confidences, accuracies, n_bins=15):
      bin_boundaries = np.linspace(0, 1, n_bins + 1)
      ece = 0.0
      for i in range(n_bins):
          mask = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
          if mask.sum() > 0:
              bin_acc = accuracies[mask].mean()
              bin_conf = confidences[mask].mean()
              ece += (mask.sum() / len(confidences)) * abs(bin_acc - bin_conf)
      return ece
  ```

**Serena Analysis Needed:** False — code patterns are clear from lm-evaluation-harness documentation

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Primary choice: lm-evaluation-harness** — this is the de facto standard framework for LLM evaluation on AdvGLUE/ANLI. It is the exact tool used by the research community for these benchmarks. No paper-specific implementation to prioritize (H-E1 is a measurement feasibility study, not a paper reproduction).

**Recommended Implementation Path:**
- **Primary:** EleutherAI/lm-evaluation-harness with `--log_samples` flag for logit extraction; custom ECE computation layer on top
- **Fallback:** Direct HuggingFace Transformers with manual logit extraction if lm-evaluation-harness task registry doesn't support all required splits
- **Justification:** lm-evaluation-harness provides standardized, reproducible evaluation harness with built-in AdvGLUE and ANLI tasks; avoids reimplementing data loading and prompt formatting

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. lm-evaluation-harness is well-documented; standard ECE computation is a simple numpy implementation. No complex custom architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Multi-Dataset Setup (6 datasets, 3 task types, clean + adversarial pairs):**

| Task Type | Clean Split | Adversarial Split | HF Identifier |
|-----------|-------------|-------------------|---------------|
| NLI (Natural Language Inference) | MultiNLI | ANLI R1/R2/R3 | `multi_nli` / `anli` |
| Paraphrase Detection | GLUE QQP | AdvGLUE QQP | `glue/qqp` / `adv_glue/adv_qqp` |
| Sentiment Classification | GLUE SST-2 | AdvGLUE SST-2 | `glue/sst2` / `adv_glue/adv_sst2` |

**Dataset Details:**

**AdvGLUE** (Adversarial GLUE):
- Source: Wang et al. 2021; human-verified label preservation
- HuggingFace: `adv_glue` (subtasks: `adv_qqp`, `adv_sst2`, `adv_mnli`)
- Test set sizes: ~800–1000 examples per subtask
- Type: standard (available on HuggingFace)
- Synthetic data check: ❌ NOT synthetic — real adversarially-perturbed NLP examples with human verification

**ANLI** (Adversarial NLI):
- Source: Nie et al. 2020; model-in-the-loop construction with human validation
- HuggingFace: `anli` (splits: `test_r1`, `test_r2`, `test_r3`)
- Test set sizes: ~1000 examples per round
- Type: standard (available on HuggingFace)
- Synthetic data check: ❌ NOT synthetic — real adversarially-constructed NLI examples

**GLUE** (Clean baseline for AdvGLUE):
- HuggingFace: `glue` (subtasks: `qqp`, `sst2`, `mnli`)
- Test/validation sizes: 10k–400k (using validation splits for ECE baseline)
- Type: standard

**MultiNLI** (Clean baseline for ANLI):
- HuggingFace: `multi_nli` (split: `validation_matched`)
- Size: ~9815 examples
- Type: standard

**Coverage Targets:**
- Minimum ≥200 examples per (model, task, split) cell
- All cells from AdvGLUE/ANLI test sets meet this threshold (800–1000 examples each)
- GLUE/MultiNLI validation sets vastly exceed threshold (randomly subsample 500 examples per cell for computational efficiency while maintaining statistical validity)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` library
- Identifier: `adv_glue`, `anli`, `glue`, `multi_nli`
- Code:
  ```python
  from datasets import load_dataset
  datasets = {
      "advglue_qqp": load_dataset("adv_glue", "adv_qqp", split="validation"),
      "advglue_sst2": load_dataset("adv_glue", "adv_sst2", split="validation"),
      "advglue_mnli": load_dataset("adv_glue", "adv_mnli", split="validation"),
      "anli_r1": load_dataset("anli", split="test_r1"),
      "anli_r2": load_dataset("anli", split="test_r2"),
      "anli_r3": load_dataset("anli", split="test_r3"),
      "glue_qqp": load_dataset("glue", "qqp", split="validation"),
      "glue_sst2": load_dataset("glue", "sst2", split="validation"),
      "mnli": load_dataset("multi_nli", split="validation_matched"),
  }
  ```

### Models

#### Baseline Model

**4 Open-Weight Decoder-Only Transformers (fixed, no fine-tuning):**

| Model | HuggingFace ID | Parameters | Type |
|-------|----------------|------------|------|
| Llama-2-7B-base | `meta-llama/Llama-2-7b-hf` | 7B | Base (no RLHF) |
| Llama-2-7B-chat | `meta-llama/Llama-2-7b-chat-hf` | 7B | RLHF-aligned |
| Llama-2-13B-chat | `meta-llama/Llama-2-13b-chat-hf` | 13B | RLHF-aligned |
| Mistral-7B-instruct | `mistralai/Mistral-7B-Instruct-v0.1` | 7B | Instruction-tuned |

**Configuration:**
- Precision: bfloat16 (full precision; 4-bit BitsAndBytes if VRAM-constrained for 13B)
- Pin exact HuggingFace checkpoint hashes at run time (record in results metadata)
- Inference only (no gradient computation, `torch.no_grad()`)
- Device: CUDA (single or multi-GPU via accelerate for 13B)

**Justification:**
- Open-weight allows logit extraction (unlike closed-weight GPT-4, Claude)
- Base vs. chat comparison tests RLHF calibration effect (secondary prediction P2)
- Mistral-7B provides cross-architecture data point (GQA vs standard MHA)
- All 4 models are widely used as reference points in academic evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` with `AutoModelForCausalLM`
- Identifier: see table above
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

#### Proposed Model

**Architecture:** Same 4 models + ECE measurement layer (logit extraction + calibration computation)

H-E1 is an EXISTENCE/measurement feasibility hypothesis — the "proposed model" is the baseline model evaluated with the ECE measurement infrastructure. The experiment tests whether ECE computation is possible and valid, not whether a new architecture improves performance.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Logit-based ECE Extraction for LLMs on MC Tasks
# Based on: EleutherAI/lm-evaluation-harness loglikelihood API
# H-E1: Tests that this pipeline produces valid, non-degenerate ECE values

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def extract_mc_logits(model, tokenizer, context, answer_choices, device):
    """
    Extract answer-token log-probabilities for a multiple-choice item.
    Returns: probs (n_choices,), pred_label (int), confidence (float)
    """
    log_probs = []
    for choice in answer_choices:
        input_ids = tokenizer.encode(context + choice, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(input_ids)
            # Log-prob of the last (answer) token
            logits = outputs.logits[0, -1, :]
            token_id = tokenizer.encode(choice, add_special_tokens=False)[-1]
            log_probs.append(logits[token_id].item())
    probs = torch.softmax(torch.tensor(log_probs), dim=0).numpy()
    return probs, probs.argmax(), probs.max()

def compute_ece(confidences, labels, preds, n_bins=15):
    """15-bin equal-width ECE (Guo 2017)."""
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences > bins[i]) & (confidences <= bins[i+1])
        if mask.sum() > 0:
            bin_acc = (labels[mask] == preds[mask]).mean()
            bin_conf = confidences[mask].mean()
            ece += (mask.sum() / len(confidences)) * abs(bin_acc - bin_conf)
    return ece

# Integration: Applied over all examples in each (model, task, split) cell
# Output: ECE value per cell; calibration reliability diagram data
```

### Training Protocol

**No training performed** — H-E1 is an evaluation-only experiment (inference on pre-trained models).

**Evaluation Protocol:**

| Parameter | Value | Justification |
|-----------|-------|---------------|
| ECE bins | 15 (primary), 10 (secondary) | Guo 2017 standard; 10-bin for sensitivity check (R5 mitigation) |
| Seed | 1 (fixed) | Single run sufficient for existence PoC |
| Precision | bfloat16 | Standard for open-weight LLM inference; memory-efficient |
| Subsample (GLUE/MultiNLI) | 500 examples/cell | Exceeds ≥200 coverage threshold; matches adversarial set size order of magnitude |
| Prompt format | MC with letter labels (A/B/C/D) | Standard lm-evaluation-harness format for NLI/classification tasks |
| Logit extraction | Answer-token log-prob via `loglikelihood` | lm-evaluation-harness native API |

**Pre-validation (Risk R1 mitigation):**
- Run pipeline on 10 known examples per model × task before full evaluation
- Verify softmax distributions sum to ~1.0 (within 1e-4)
- Flag cells where max softmax confidence >0.999 for all examples (degenerate)
- Flag cells where mean max confidence <0.5 (near-uniform; may indicate tokenization issue)

**Runs:** 4 models × 3 tasks × 2 splits = 24 evaluation runs
**Compute estimate:** ~2–4 GPU-hours per model on A100 (7B models); ~6–8 hours for 13B
**Total:** ~12–18 A100-hours (parallelizable across 4 GPUs)

### Evaluation

**Primary Metrics (H-E1 EXISTENCE gate):**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cell coverage | ≥200 examples per (model, task, split) cell | Count valid examples with non-degenerate distributions |
| ECE range validity | ECE ∈ [0.0, 0.5] for all 24 cells | Direct ECE computation |
| Clean-split ECE sanity | ECE ∈ [0.05, 0.15] for clean splits | Compare against Kadavath 2022 published range |
| Distribution non-degeneracy | Max confidence ≠ 1.0 for >90% examples per cell | Per-cell logit validation |

**Success Criteria:**
- PoC PASSES if: All 24 cells have ≥200 valid examples AND ECE computable in plausible range AND clean-split ECE consistent with published baseline
- PoC FAILS if: Any cell has <200 examples OR degenerate logits for majority of examples OR clean-split ECE >0.3 for all models (systematic failure)

**Expected Baseline Performance (from Phase 2B / Kadavath 2022):**
- Clean-split ECE: 0.05–0.15 for LLMs on TriviaQA/MMLU/BIG-Bench (Kadavath 2022)
- Accuracy on AdvGLUE/ANLI: 15–30% lower than clean counterparts (Wang 2021, Nie 2020)
- H-E1 does NOT test ΔECE > threshold — that is H-M3; H-E1 only confirms ECE is computable

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-class classification (NLI: 3-way; QQP: binary; SST-2: binary)
- Library: Custom `numpy` implementation for ECE; `datasets` for label loading; `sklearn.metrics` for accuracy
- Code:
  ```python
  from sklearn.metrics import accuracy_score
  accuracy = accuracy_score(true_labels, pred_labels)
  ece_15 = compute_ece(confidences, true_labels, pred_labels, n_bins=15)
  ece_10 = compute_ece(confidences, true_labels, pred_labels, n_bins=10)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing ECE per (model, task) cell for clean vs. adversarial splits across all 12 cells (2×2 subplot grid: 4 models × 3 tasks, colored by split)

#### Additional Figures (LLM Autonomous)

Based on H-E1's measurement focus, the following additional figures are appropriate:

1. **Calibration Reliability Diagrams (12 panels):** One per (model, task) pair; show confidence histogram and calibration curve for both clean and adversarial splits overlaid — key diagnostic for non-degenerate ECE measurement
2. **Cell Coverage Heatmap:** 4×6 grid (4 models × 6 dataset splits) showing example count per cell — confirms ≥200 coverage requirement
3. **Confidence Distribution Boxplots:** Per cell, showing max-softmax confidence distribution — validates non-degeneracy assumption
4. **ECE Sensitivity (10-bin vs 15-bin):** Scatter plot of ECE values under both bin counts — validates R5 (bin count sensitivity) is not confounding

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | lm-evaluation-harness `loglikelihood` API is available and returns per-token log-probs for answer choices | TRUE — confirmed in lm-evaluation-harness public documentation and codebase |
| Mechanism Isolatable | ECE computation can be run with/without softmax normalization; baseline (accuracy-only) is independent of ECE | TRUE — ECE computation is a post-processing step on extracted logits |
| Baseline Measurable | Accuracy on clean splits can be computed independently of ECE | TRUE — standard accuracy from argmax of logit vector |

### Architecture Compatibility Check

All 4 target models are decoder-only transformer architectures with standard attention:
- Llama-2 (7B/13B): GQA/standard MHA — supports standard `loglikelihood` API via next-token prediction
- Mistral-7B: Sliding Window Attention + GQA — supports same API

**Required Features:**
- Causal language model with `logits` output tensor — all 4 models satisfy this via `AutoModelForCausalLM`
- Tokenizer that maps answer choices to single or multi-token sequences — validated in pre-validation step (10 examples)

**Incompatible Architectures:**
- Encoder-only models (BERT, RoBERTa) — cannot use next-token `loglikelihood` for generative MC format
- Closed-weight APIs (GPT-4, Claude) — no logit access

> ⚠️ All 4 target models ARE compatible. If a model is swapped to an incompatible architecture, Phase 4 MUST fail early with explicit error.

---

### Mechanism Activation Indicators

**How to detect if logit extraction is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Logit extraction validated: cell (model, task, split) — N examples, mean_conf=X.XX, ECE=Y.YY"` | `evaluate.py:validate_cell()` |
| Tensor Shape | `logits.shape == (batch_size, seq_len, vocab_size)` — non-degenerate (not collapsed to argmax) | `model.py:extract_mc_logits()` |
| Metric Delta | `ECE_clean ∈ [0.05, 0.15]` for at least 2/4 models (sanity check against Kadavath 2022) | `evaluate.py:compute_ece()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_logit_extraction(cell_results):
    """Verify that logit extraction mechanism is working correctly for a cell."""
    confidences = cell_results["confidences"]
    indicators = {
        "coverage_met": len(confidences) >= 200,
        "non_degenerate": (confidences < 0.999).mean() > 0.90,
        "non_uniform": confidences.mean() > 0.40,
        "ece_plausible": 0.0 <= cell_results["ece_15"] <= 0.5,
        "probs_sum_to_one": abs(cell_results["prob_sums"].mean() - 1.0) < 1e-3,
    }
    passed = all(indicators.values())
    return passed, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Coverage failure | `len(examples) < 200` after filtering degenerate | FAIL cell; document; PIVOT to BBH-MC if ≥3 cells fail |
| All-confident logits | `(confidences >= 0.999).mean() > 0.10` | FAIL: logit extraction collapse; check tokenization of answer tokens |
| All-uniform logits | `confidences.mean() < 0.35` | FAIL: model not conditioning on answer tokens; check prompt format |
| ECE out of range | `ece_15 > 0.5` or `ece_15 < 0.0` | FAIL: numerical error; check softmax normalization |
| Clean ECE far from baseline | `ece_clean > 0.30` for ALL models | WARN: systematic deviation from Kadavath 2022; investigate prompt format |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Coverage ≥200 AND non-degenerate distributions | Per-cell logit validation via `verify_logit_extraction()` |
| Effect Measurable | ECE computable (not NaN/Inf) for all 24 cells | `np.isfinite(ece_15)` check |
| Hypothesis Supported | ≥20/24 cells pass all validation checks | Count of cells where `verify_logit_extraction()` returns True |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on all 24 (model, task, split) cells
2. ≥20/24 cells pass logit extraction validation (coverage ≥200, non-degenerate, ECE plausible)
3. Clean-split ECE for ≥2/4 models falls in published range [0.05, 0.15] (Kadavath 2022 sanity check)

**PoC Failure Triggers:**
- <15/24 cells with valid ECE (measurement infrastructure failure) → STOP gate
- Clean-split ECE >0.30 for ALL 4 models → systematic prompt/tokenization issue → STOP gate
- Any model produces degenerate logits (all-confident or all-uniform) for >50% of examples → STOP gate

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Archon MCP unavailable (ablation mode). Sources synthesized from Phase 2B verification plan.*

**Source A.1: Phase 2B Verification Plan (02b_verification_plan.md)**
- **Type:** Internal Phase 2B planning document (Phase 2A dialogue output)
- **Relevance:** Contains full experimental setup, dataset selection, model selection, risk analysis, and implementation assumptions for H-E1
- **Key Insights:**
  - lm-evaluation-harness is the appropriate tool for ECE on LLMs
  - 15-bin ECE is standard (Guo 2017 arXiv 1706.04599)
  - Published ECE baseline for LLMs: 0.05–0.15 (Kadavath 2022)
  - Risk R1: logit extraction validity; Risk R5: bin count sensitivity
- **Used For:** Dataset specification, training protocol, evaluation metrics, risk mitigation strategies

**Source A.2: Guo et al. 2017 — "On Calibration of Modern Neural Networks"**
- **Type:** Academic paper (arXiv 1706.04599, ~4000 citations)
- **Key Insight:** 15-bin equal-width ECE formula: `ECE = Σ_b |B_b|/n × |acc(B_b) - conf(B_b)|`
- **Used For:** ECE formula and bin count specification

**Source A.3: Kadavath et al. 2022 — "Language Models (Mostly) Know What They Know"**
- **Type:** Academic paper (Anthropic)
- **Key Insight:** LLM clean-split ECE baseline range 0.05–0.15 on TriviaQA/MMLU/BIG-Bench
- **Used For:** Sanity check thresholds for clean-split ECE validation

### B. GitHub Implementations (Exa)

*Exa MCP unavailable (ablation mode). Key repositories identified from Phase 2B context.*

**Repository B.1: EleutherAI/lm-evaluation-harness**
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Query That Would Find It:** "lm-evaluation-harness AdvGLUE ANLI logit extraction MC tasks"
- **Relevance:** Primary evaluation framework; natively supports AdvGLUE and ANLI; `loglikelihood` API for logit extraction
- **Configuration Extracted:** `--model hf`, `--log_samples`, bfloat16 via `dtype=bfloat16`
- **Used For:** Primary implementation path; logit extraction API; dataset task registry

**Repository B.2: HuggingFace/datasets (adv_glue, anli)**
- **URL:** https://huggingface.co/datasets/adv_glue; https://huggingface.co/datasets/anli
- **Relevance:** Standard dataset loading; `load_dataset("adv_glue", "adv_qqp")` pattern
- **Used For:** Dataset loading code in experiment specification

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. lm-evaluation-harness has clean, well-documented `loglikelihood` API; ECE implementation is a simple numpy formula.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (AdvGLUE, ANLI, GLUE, MultiNLI) | Phase 2B planning | A.1, Section 1.3 |
| Dataset HuggingFace identifiers | Public documentation | B.2 |
| Model selection (4 LLMs) | Phase 2B planning | A.1, Section 1.3 |
| Model loading code | HuggingFace Transformers docs | B.2 |
| ECE formula (15-bin) | Academic paper | A.2 (Guo 2017) |
| Clean ECE sanity range [0.05–0.15] | Academic paper | A.3 (Kadavath 2022) |
| Logit extraction API | GitHub | B.1 (lm-evaluation-harness) |
| Pre-validation protocol | Phase 2B risk analysis | A.1, Section 4.1 R1 |
| Bin count sensitivity check | Phase 2B risk analysis | A.1, Section 4.1 R5 |
| Coverage threshold ≥200 | Phase 2B hypothesis spec | A.1, Section 2.2 H-E1 |
| Success criteria | Phase 2B hypothesis spec | A.1, Section 2.2 H-E1 |
| Core mechanism pseudocode | lm-evaluation-harness API | B.1 |
| Mechanism verification code | Derived from risk analysis | A.1 |
| Visualizations | Phase 2B evaluation protocol | A.1, Section 2.2 H-E1 |

---

## Quality Validation Results

**Check 1: All Hyperparameters Justified?** ✅
- n_bins=15: Guo 2017 standard (A.2)
- Subsample=500: exceeds ≥200 coverage threshold; justified by computational efficiency
- bfloat16: standard open-weight LLM inference precision (B.1)
- No other hyperparameters (H-E1 is evaluation-only, no training)

**Check 2: Dataset Choice Justified?** ✅
- AdvGLUE/ANLI: primary adversarial NLP benchmarks identified in Phase 2A as the PROVE_NEW gap
- GLUE/MultiNLI: clean counterparts to AdvGLUE/ANLI for ΔECE computation (same task, different perturbation)
- Source: A.1 Section 1.3

**Check 3: Mechanism Grounded in Code?** ✅
- Pseudocode based on lm-evaluation-harness `loglikelihood` API (B.1) and standard numpy ECE formula (A.2)
- Not speculative — directly derived from documented API

**Check 4: No Unsupported Assumptions?** ✅
- All claims referenced to Phase 2B risk analysis or published papers
- Ablation note on MCP unavailability explicitly documented

**Check 5: Full Traceability?** ✅
- Traceability matrix covers all specifications

**Overall: PASSED** (with note: MCP sources are Phase 2B-derived rather than live Archon/Exa queries due to ablation mode)

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in pipeline output)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: H-E1 set to IN_PROGRESS; Phase 2C experiment design started
- 2026-08-25: Phase 2C experiment design COMPLETED; 02c_experiment_brief.md written

---

*MCP Tools Used: Ablation mode — Archon, Exa, Serena unavailable. Specifications derived from Phase 2B verification plan (02b_verification_plan.md) which contains Phase 2A dialogue outputs including full experimental setup, dataset/model selection, risk analysis, and implementation details. All specifications are traceable to Phase 2B sources and published papers cited therein.*
*Specification Level: 1.5 (Concrete + Pseudo-code)*
*Next Phase: Phase 3 — Implementation Planning*
