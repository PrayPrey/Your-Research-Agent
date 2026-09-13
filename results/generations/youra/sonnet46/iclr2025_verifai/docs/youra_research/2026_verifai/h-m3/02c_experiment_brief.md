# Experiment Design: h-m3

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under zero-shot P(True) prompting for each (problem, solution) pair, if logprob(True) and logprob(False) are extracted and normalized as confidence c = logprob(True)/(logprob(True)+logprob(False)), then confidence values are non-degenerate (std(c) > 0.05 for all 3 models), because Run 3 validated P(True) values of 0.57–0.91 for all 3 model families.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates P(True) logprob elicitation produces non-degenerate confidence signals.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m2 ✅ PASS (SHOULD_WORK, all 3/3 Jaccard pairs > 0.3; max=0.5462)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM (Step 3 of 4)
- **Prerequisites:** h-m2 (COMPLETED, PASS)

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** std(c) > 0.05 for ALL 3 models (non-degenerate confidence distribution)
**Secondary:** c values span range 0.2–0.9 (not collapsing to extremes)
**Fail Action:** Try alternative prompt format ("Does this solution pass all tests?"); if still degenerate, report as mechanism failure and PIVOT

---

## Continuation Context

**Previous Hypothesis:** h-m2 (COMPLETED, PASS)
- h-m2 validated that difficulty tier assignments are meaningful (Jaccard > 0.3 across all 3 model pairs)
- tier_assignments.csv generated with 542-row tier assignments per model
- Consensus hard set: 133/542 problems (24.5%)
- Hard tier problem sets available for all 3 models

**Previous Hypothesis Proven Components:**
- Pass@1 values from h-m1 (pass_at_1_hm1_verified.json) are valid and reusable
- Tier assignments from h-m2 (tier_assignments.csv) are meaningful and ready
- All 3 model checkpoints validated and cached at ~/.cache/huggingface/
- EvalPlus dataset cached at ~/.cache/evalplus/

**Reuse Strategy:** Load tier_assignments.csv from h-m2 results. Iterate over all (problem, solution) pairs in hard+easy tiers to elicit P(True) confidence scores.

### Previous Hypothesis Results (if applicable)
**h-m2 key findings:**
- Jaccard similarity (all 3 pairs): llama3-codellama=0.5462, llama3-deepseek=0.5305, codellama-deepseek=0.4561
- All above 0.3 threshold (SHOULD_WORK gate: PASS)
- tier_assignments.csv: 542 rows × [model, problem_id, tier, pass@1]
- Consensus hard (all 3 hard): 133/542 problems
- h-m3 explicitly UNBLOCKED in h-m2 validation

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: P(True) logprob confidence calibration LLM**
- Result 1: [HF Papers 2305.14314] — Discusses P(True) uncertainty estimation approaches for LLMs
  - Key insight: Token-level probability elicitation for True/False tokens captures calibration signal
  - Similarity score: 0.44 (top match in KB)

- Result 2: [NeurIPS 2024] "Large Language Models Must Be Taught to Know What They Don't Know" (Kapoor et al.)
  - Key insight: Fine-tuning on correct/incorrect examples improves calibration; P(True) prompting on its own produces partially calibrated outputs. Key finding: *"prompting on its own is insufficient to achieve good calibration"* — relevant as baseline expectation for zero-shot P(True)
  - Hyperparameters from referenced work: AdamW, lr=1e-4, cosine schedule, batch=32, 10K steps, LoRA
  - ECE reported for LLaMA-2 7B/13B, Mistral 7B with zero-shot classifier vs. LoRA approaches

- Result 3: [TruthTorchLM] Comprehensive library (30+ truth methods) including P(True) method
  - Includes PTrue as a supported method with HuggingFace and LiteLLM integration
  - AUROC scores reported: PTrue achieves 0.727–0.833 AUROC range across benchmarks
  - Integration pattern: `output = ttlm.generate_with_truth_value(model, tokenizer, messages, truth_methods=[ttlm.PTrue()])`

**Query 2: ECE implementation challenges best practices**
- Result 1: [openreview.net/forum?id=gU58d5QeGv] — LLM calibration paper with ECE implementation
  - Key insight: Bin count sensitivity (M=10/15/20) affects ECE; standard practice uses M=15
  - Challenge: Hard tier has lower base accuracy → ECE numerically higher even without calibration failure

**Query 3: logprob elicitation code verification EvalPlus**
- Result 1: [openreview.net] LLM Output Signatures paper — references Kadavath et al. 2022 for P(True) approach
  - Confirms: logprob(True)/(logprob(True)+logprob(False)) is a standard normalization formula
  - Cites this as "Actual Token Probabilities (ATP)" pattern used in multiple papers

### Archon Code Examples

**Query: P(True) logprob extraction HuggingFace output_scores**
- Code Source 1: Custom LogitsProcessor pattern (HuggingFace diffusers)
  ```python
  class CustomLogitsProcessor(LogitsProcessor):
      def __call__(self, input_ids, scores):
          # scores = raw logits at each generation step
          return scores + self.bias
  ```
  Pattern: LogitsProcessor gives access to per-token logits during generation
  Insight: `output_logits=True` in `model.generate()` returns raw unprocessed logits

### Exa GitHub Implementations

**Query 1: P(True) logprob elicitation LLM code verification PyTorch HuggingFace**

**Repository 1**: justinchiu/openlogprobs
- **URL**: https://github.com/justinchiu/openlogprobs
- **Relevance**: Python API for extracting log-probabilities from language model APIs; exact use case
- **Key Insight**: Demonstrates binary search approach for logprob extraction from APIs
- **Note**: For local HuggingFace models, `output_logits=True` or `output_scores=True` is simpler

**Repository 2**: Pwicke/logprobs_for_CausalLMs (HuggingFace)
- **URL**: https://huggingface.co/Pwicke/logprobs_for_CausalLMs
- **Relevance**: Exact pattern for CausalLM logprob extraction
- **Key Code**:
  ```python
  def logprobs_from_prompt(prompt, tokenizer, model):
      encoded = tokenizer(prompt, return_tensors="pt")
      input_ids = encoded["input_ids"]
      output = model(input_ids=input_ids)
      shift_logits = output.logits[..., :-1, :].contiguous()
      log_probs = F.log_softmax(logit, dim=0).tolist()[label_id]
      return log_probs
  ```
- **Insight**: Forward pass on prompt+answer appended gives logits for answer tokens

**Repository 3**: parea-ai/parea-sdk-py — self_check.py
- **URL**: https://github.com/parea-ai/parea-sdk-py/blob/main/parea/evals/general/self_check.py
- **Relevance**: SelfCheckGPT approach to confidence via multiple generations
- **Note**: For P(True) we use single forward pass logprob, not multiple generations

**Query 2: Kadavath P(True) self-evaluation LLM logprob True False token extraction**

**Paper Reference**: Kadavath et al. 2022 "Know What You Don't Know" — described in multiple found sources
- **Method**: Append "Is the above code correct? (True/False)" to prompt+solution, extract P(True) and P(False) from first generated token's logit distribution
- **Normalization**: c = softmax([logprob(True), logprob(False)])[0]
- **Confirmed by**: NeurIPS 2024 paper (Kapoor et al.) which validates this approach for code tasks

**HuggingFace Transformers output_logits=True** (PR #28667)
- Merged 2024-02-19, `output_logits=True` in `model.generate()` returns raw unprocessed logits
- Key quote from PR: *"Query your language model with: 'Is the {statement} correct? Answer yes or no:', take the raw logit scores and softmax them, and calculate the score: prob(yes) / (prob(yes) + prob(no)) to get a useful classification score"* — exact H-M3 approach
- Method: `generation_output = model.generate(**inputs, return_dict_in_generate=True, output_logits=True, max_new_tokens=1)`

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL:** This is NOT a paper reproduction experiment — it is a new empirical study using P(True) prompting. Implementation is based on the Kadavath et al. 2022 approach, validated in Run 3.

**Recommended Implementation Path:**
- Primary: Custom implementation using HuggingFace `model.generate(output_logits=True, max_new_tokens=1)` — exact pattern described in PR #28667 and confirmed by Run 3
- Fallback: Forward pass approach (model(input_ids) to get logits directly, no generation loop)
- Justification: `output_logits=True` with `max_new_tokens=1` is the cleanest approach for single-token classification. Reuses h-m1/h-m2 infrastructure (models already loaded, EvalPlus already cached).

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The P(True) extraction pattern is well-documented via HuggingFace `output_logits=True` with `max_new_tokens=1`, confirmed by Kadavath et al. 2022 approach and Run 3 prior validation.

---

## Experiment Specification

### Dataset

**Name:** EvalPlus (HumanEval+ 164 + MBPP+ 378) — reused from h-m1/h-m2
**Type:** programmatic-api (real benchmark data via evalplus Python package)
**Source:** Liu et al. NeurIPS 2023; https://github.com/evalplus/evalplus
**Total Problems:** 542 (164 HumanEval+ + 378 MBPP+)
**Scope for h-m3:** All (problem, solution) pairs in hard and easy tiers from h-m2's tier_assignments.csv
**Estimated pairs:** ~3×542×5 = ~8,130 (problem, solution) pairs, filtered to hard+easy tiers only

**Tier Data Source:**
- tier_assignments.csv from h-m2 results (542 problems × 3 models × tier assignment)
- pass_at_1_hm1_verified.json from h-m1 results (used to reconstruct solutions if needed)
- Solutions: k=5 per (problem, model) generated by h-m1 pipeline

**Preprocessing:**
- Load tier_assignments.csv → filter to hard (pass@1=0.0) and easy (pass@1≥0.6) rows per model
- For each (problem, model, tier) row: retrieve the k=5 solutions from h-m1 outputs
- Construct P(True) prompt: `{problem_description}\n\n{solution_code}\n\nIs this solution correct? Answer True or False.\nAnswer:`
- No augmentation required (inference-only, no training)

**Synthetic Data Check:** NOT synthetic — uses real EvalPlus benchmark problems with real model-generated solutions from h-m1. Type: programmatic-api ✅

**Loading Information** (for Phase 4 download):
- Method: evalplus Python package (already installed from h-m1/h-m2)
- Identifier: `from evalplus.data import get_human_eval_plus, get_mbpp_plus`
- Code:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  humaneval_data = get_human_eval_plus()   # dict: task_id -> {prompt, canonical_solution, ...}
  mbpp_data = get_mbpp_plus()              # dict: task_id -> {prompt, canonical_solution, ...}
  ```
- Tier assignments: `pd.read_csv("../h-m2/results/tier_assignments.csv")`
- Solutions: load from `../h-m1/results/solutions_{model_name}.jsonl`

### Models

#### Baseline Model

**Architecture:** No training baseline — this is a logprob extraction experiment (inference-only).
**Baseline Measurement:** Degenerate confidence distribution: c ≈ 0.5 for all pairs (pure uncertainty) OR c ≈ 1.0 for all pairs (overconfidence). std(c) ≤ 0.05.
**Purpose:** Verify h-m3 gate: std(c) > 0.05 confirms non-degeneracy.

**Models Used (all 3, inference-only):**
1. NousResearch/Meta-Llama-3-8B (general-purpose LLM)
2. codellama/CodeLlama-7b-hf (code-adapted LLM)
3. deepseek-ai/deepseek-coder-6.7b-base (code-specialized LLM)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (already cached from h-m1/h-m2)
- Identifier: model IDs above
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  ```
- Cache path: ~/.cache/huggingface/ (already populated from h-m1)

#### Proposed Model

**Architecture:** Same 3 models + P(True) zero-shot prompting with logprob extraction

**Core Mechanism Implementation:**

```python
# Core Mechanism: P(True) Logprob Confidence Elicitation
# Based on: Kadavath et al. 2022, HuggingFace PR #28667, Run 3 validation
# Reference: https://github.com/huggingface/transformers/pull/28667

import torch
import torch.nn.functional as F

def extract_ptrue_confidence(model, tokenizer, problem_prompt, solution_code, device):
    """
    Extract P(True) confidence score for a (problem, solution) pair.

    Args:
        problem_prompt: str — problem description from EvalPlus
        solution_code:  str — one of k=5 generated solutions from h-m1
    Returns:
        c: float in [0,1] — normalized confidence = P(True)/(P(True)+P(False))
    """
    # Step 1: Construct zero-shot P(True) prompt
    prompt = (
        f"{problem_prompt}\n\n"
        f"```python\n{solution_code}\n```\n\n"
        f"Is this solution correct? Answer True or False.\nAnswer:"
    )

    # Step 2: Tokenize and get token IDs for "True" and "False"
    true_id  = tokenizer.encode(" True",  add_special_tokens=False)[0]
    false_id = tokenizer.encode(" False", add_special_tokens=False)[0]

    # Step 3: Run model.generate with output_logits=True, max_new_tokens=1
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=1,
            return_dict_in_generate=True,
            output_logits=True        # returns raw logits at each step (PR #28667)
        )

    # Step 4: Extract logits for first generated token
    logits_step0 = out.logits[0][0]   # shape: (vocab_size,)

    # Step 5: Extract logprob(True) and logprob(False) and normalize
    log_probs = F.log_softmax(logits_step0, dim=-1)
    logp_true  = log_probs[true_id].item()
    logp_false = log_probs[false_id].item()

    # Step 6: Normalize: c = exp(logp_true) / (exp(logp_true) + exp(logp_false))
    # Equivalent to softmax over [logp_true, logp_false]
    c = torch.softmax(torch.tensor([logp_true, logp_false]), dim=0)[0].item()

    return c  # c in [0,1]; c>0.5 means model "believes" solution is correct
```

### Training Protocol

**N/A — Inference-only experiment.** No training, no optimizer, no learning rate, no epochs.

**Inference Configuration:**
- **Temperature:** 0 (greedy decoding for deterministic logprob extraction)
- **max_new_tokens:** 1 (extract only first token's logit distribution)
- **Precision:** float16 (consistent with h-m1/h-m2)
- **Batch size:** 1 per call (logprob extraction is sequential per pair)
- **Seed:** fixed=42 (consistent with h-m1/h-m2)
- **Device:** Single GPU (CUDA_VISIBLE_DEVICES set to empty GPU)

**Execution Scope:**
- For each model (3 total):
  - For each problem in hard+easy tiers (estimated ~200–300 problems per model per tier):
    - For each of k=5 solutions (from h-m1 outputs):
      - Extract c = P(True) confidence score
  - Total pairs per model: hard_n × 5 + easy_n × 5 (h-e1 confirmed: n_hard ~68–199, n_easy ~24–176)

**Source:** HuggingFace `output_logits=True` (PR #28667, merged 2024-02-19); Kadavath et al. 2022

### Evaluation

**Primary Metrics:**
- **std(c) per model:** Standard deviation of normalized P(True) confidence across all (problem, solution) pairs in hard+easy tiers
  - Gate threshold: std(c) > 0.05 for ALL 3 models
  - Expected from Run 3: std(c) in range 0.15–0.30 (non-degenerate; P(True) values 0.57–0.91 in Run 3)

**Secondary Metrics:**
- **mean(c) per model:** Mean confidence (expected: ~0.6–0.8 based on Run 3)
- **min(c) / max(c) per model:** Range check (expected: range spanning at least 0.2–0.9)
- **c distribution histograms:** 20-bin histogram of c values per model (detect degeneracy patterns)
- **c by tier:** mean(c) and std(c) separately for hard vs. easy tiers (preview for h-m4 ECE analysis)
- **Correlation c vs. pass@1:** Point-biserial correlation between c and binary correctness label per (problem, solution)

**Success Criteria (Gate):**
- **Primary (MUST_WORK):** std(c) > 0.05 for ALL 3 models
- **Secondary:** c value range spans at least [0.2, 0.9] (not collapsing to extremes)
- **Fail trigger:** Any model with std(c) ≤ 0.05 → try alternative prompt; if still degenerate → PIVOT

**Expected Baseline Performance:**
- Run 3 P(True) results: llama3-8b: ~0.71–0.82, codellama-7b: ~0.57–0.73, deepseek-coder: ~0.68–0.91
- std(c) expected: ~0.15–0.25 per model (well above 0.05 threshold)
- **Source:** Phase 2B Section 6.1 (Run 3 validation, pre-registered prior evidence)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: confidence_distribution_analysis (not classification — no labels needed for gate check)
- Library: numpy, scipy.stats, matplotlib
- Code:
  ```python
  import numpy as np
  std_c = np.std(confidence_scores_per_model)   # gate check: std_c > 0.05
  mean_c = np.mean(confidence_scores_per_model)
  from scipy.stats import pointbiserialr
  corr, pval = pointbiserialr(correctness_labels, confidence_scores)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of std(c) per model vs. threshold (0.05 line). Title: "P(True) Confidence Std by Model — H-M3 Gate Check"

#### Additional Figures (LLM Autonomous)
- **Figure 2:** Histogram of c distribution per model (3 subplots, 20 bins, overlaid with hard/easy tier color coding)
- **Figure 3:** Scatter plot of c vs. pass@1 per model (x=correctness binary, y=c value, with jitter)
- **Figure 4:** Box plots of c distributions per model × tier (hard vs. easy side-by-side)
- **Figure 5:** CDF of c values per model — diagnose degeneracy (flat CDF = degenerate)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 3 models
2. std(c) > 0.05 for all 3 models (gate condition satisfied)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | model.generate(output_logits=True) is supported in transformers ≥ 4.38 | TRUE — PR #28667 merged 2024-02-19 |
| Mechanism Isolatable | P(True) can be enabled/disabled (trivial: just run vs. don't run the prompt variant) | TRUE |
| Baseline Measurable | Can measure degenerate baseline: std(c)≤0.05 is detectable | TRUE |

### Architecture Compatibility Check

All 3 models are HuggingFace CausalLM models (AutoModelForCausalLM):
- NousResearch/Meta-Llama-3-8B: LlamaForCausalLM ✅
- codellama/CodeLlama-7b-hf: LlamaForCausalLM ✅
- deepseek-ai/deepseek-coder-6.7b-base: MistralForCausalLM ✅

**Required Features:** `output_logits=True` in `model.generate()` (available in transformers ≥ 4.38)
**Incompatible Architectures:** None for these 3 models; all are standard CausalLM

> ⚠️ If `output_logits` unavailable, fallback: use `model(**inputs).logits` direct forward pass on prompt+answer tokens.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"P(True) extraction: True_id={}, False_id={}"` printed at startup | extract_ptrue_confidence() |
| Tensor Shape | `out.logits[0][0].shape == (vocab_size,)` — confirms logit extraction worked | h_m3_ptrue.py:forward() |
| Metric Delta | std(c) > 0.05 per model — confirms non-degenerate distribution | evaluate.py:compute_stats() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_ptrue_mechanism(confidence_scores_by_model, out_logits_sample):
    indicators = {
        "logits_extracted": out_logits_sample is not None and len(out_logits_sample) > 0,
        "vocab_size_correct": out_logits_sample[0][0].shape[0] > 30000,  # vocab > 30K
        "c_values_in_range": all(0.0 <= c <= 1.0 for c in confidence_scores_by_model["llama3"]),
        "non_degenerate": all(
            np.std(scores) > 0.05
            for scores in confidence_scores_by_model.values()
        )
    }
    return all(indicators.values()), indicators
```

**Failure Detection:**

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Degenerate c≈0.5 | std(c) ≤ 0.05, all values ~0.5 | Try alternative prompt format |
| Degenerate c≈1.0 | mean(c) > 0.95, std(c) ≤ 0.05 | Check tokenization of "True"/"False" |
| Empty logits | out.logits is None or empty | Switch to direct forward pass |
| Wrong token ID | true_id == false_id or id not in vocab | Debug tokenizer encoding |

**Success Criteria (Mechanism Level):**

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Logit tensor extracted for ≥1 pair |
| Effect Measurable | std(c) > 0 | Distribution is non-constant |
| Hypothesis Supported | std(c) > 0.05 for ALL 3 models | numpy.std(confidence_scores) per model |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HF Papers 2305.14314 — P(True) self-evaluation approach
- **Type:** Research paper reference
- **Query:** "P(True) logprob confidence calibration LLM"
- **Key Insight:** Token-level P(True) confidence elicitation is a validated approach for LLM self-evaluation
- **Used For:** Confirmation of approach validity; baseline calibration expectation

**Source A.2:** NeurIPS 2024 "LLMs Must Be Taught to Know What They Don't Know" (Kapoor et al.)
- **Type:** Research paper with ECE results
- **Query:** "P(True) logprob confidence calibration LLM"
- **Key Insight:** Zero-shot P(True) produces partially calibrated but non-degenerate confidence; fine-tuning improves calibration. Training hyperparameters: AdamW, lr=1e-4, cosine, batch=32.
- **Used For:** Expected baseline ECE range; confirmation that zero-shot P(True) produces non-degenerate outputs

**Source A.3:** TruthTorchLM Library (Ybakman/TruthTorchLM)
- **Type:** Open-source library implementing P(True) and 30+ truth methods
- **Query:** "P(True) logprob confidence calibration LLM"
- **Key Insight:** PTrue achieves AUROC 0.727–0.833 across QA benchmarks; integrates with HuggingFace
- **Used For:** Validation that P(True) produces meaningful signal; reference implementation pattern

**Source A.4:** OpenReview LLM Output Signatures paper
- **Type:** Research paper
- **Query:** "logprob elicitation code verification EvalPlus HumanEval"
- **Key Insight:** P(True) / ATP (Actual Token Probabilities) cited alongside Kadavath et al. 2022 for correctness self-evaluation
- **Used For:** Confirmation of P(True) for code correctness specifically

### B. GitHub Implementations (Exa)

**Repository B.1:** justinchiu/openlogprobs
- **URL:** https://github.com/justinchiu/openlogprobs
- **Query:** "P(True) logprob elicitation LLM code verification PyTorch HuggingFace"
- **Relevance:** Demonstrates logprob extraction from LM APIs; binary search approach for APIs without native logprob support
- **Used For:** Reference for logprob extraction concept; for local models, `output_logits=True` is simpler

**Repository B.2:** Pwicke/logprobs_for_CausalLMs
- **URL:** https://huggingface.co/Pwicke/logprobs_for_CausalLMs
- **Query:** "P(True) logprob elicitation LLM code verification PyTorch HuggingFace"
- **Key Code:**
  ```python
  # CausalLM logprob from forward pass
  output = model(input_ids=input_ids)
  log_probs = F.log_softmax(logit, dim=0).tolist()[label_id]
  ```
- **Used For:** Basis for core mechanism pseudo-code (Step 3 of forward pass approach)

**Repository B.3:** HuggingFace Transformers PR #28667 (output_logits=True)
- **URL:** https://github.com/huggingface/transformers/pull/28667
- **Relevance:** Merged 2024-02-19; provides `output_logits=True` in `model.generate()` for classification tasks
- **Key Quote:** *"Query your language model with: 'Is the {statement} correct? Answer yes or no:', take the raw logit scores and softmax them, calculate prob(yes) / (prob(yes) + prob(no))"* — exact H-M3 formula
- **Used For:** Primary implementation approach; `max_new_tokens=1` + `output_logits=True` pattern

**Repository B.4:** EvalPlus (evalplus/evalplus, ⭐1698)
- **URL:** https://github.com/evalplus/evalplus
- **Query:** "EvalPlus pass@1 tier stratification P(True) confidence calibration ECE"
- **Key Code:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  # Returns dict of task_id -> {prompt, canonical_solution, base_input, plus_input}
  ```
- **Dataset:** 164 HumanEval+ + 378 MBPP+ = 542 problems
- **Used For:** Dataset loading specification; problem prompt extraction for P(True) construction

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. The P(True) extraction pattern is fully documented in HuggingFace PR #28667 and confirmed by Run 3 prior validation. No complex custom architecture to analyze.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — h-m1 and h-m2

**h-m1 Reused Components:**
- Solutions: k=5 per (problem, model) generated by h-m1 pipeline (results/solutions_{model}.jsonl)
- pass_at_1_hm1_verified.json: pass@1 values for all 542 problems × 3 models
- Correctness labels: individual solution correctness (needed for c vs. correctness correlation)

**h-m2 Reused Components:**
- tier_assignments.csv: 542 × 3 model hard/easy tier assignments
- Consensus hard set: 133/542 problems
- Model-specific tier sizes: ~68–199 hard per model, ~24–176 easy per model

**Why Reused:** Enables controlled experiment — only P(True) logprob extraction changes; all prior data (solutions, correctness, tiers) is fixed.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B + h-m1/h-m2 reuse | Phase 2B Section 1.3; h-m1 results |
| P(True) prompt format | Research paper + Exa | Kadavath 2022; PR #28667 |
| logprob extraction method | GitHub | Repo B.3 (HF PR #28667) |
| Normalization formula | Research + GitHub | Kadavath 2022; Repo B.2 |
| Gate threshold std(c)>0.05 | Phase 2B | Verification plan H-M3 success criteria |
| Model loading | h-m1 reuse | h-m1 implementation |
| Secondary metrics | Phase 2B + Archon | A.2, B.4; Phase 2B H-M3 verification protocol |
| Expected confidence range | Phase 2B (Run 3) | Section 6.1: P(True) values 0.57–0.91 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T13:05:00+00:00

### Workflow History for This Hypothesis
- 2026-03-18T10:05:41: h-m3 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-03-18T13:05:00: Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web), Serena (skipped — not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
