# PRD: h-m3 — P(True) Confidence Elicitation via Logprob Extraction

**Hypothesis ID:** h-m3
**Type:** MECHANISM (Step 3 of 4)
**Gate:** MUST_WORK — std(c) > 0.05 for ALL 3 models
**Date:** 2026-03-18
**Author:** Anonymous
**Phase 2C Source:** h-m3/02c_experiment_brief.md

---

## 1. Executive Summary

This PRD defines implementation requirements for h-m3: zero-shot P(True) confidence elicitation for each (problem, solution) pair using logprob extraction. The system extracts logprob(True) and logprob(False) from the first generated token and normalizes them as c = logprob(True)/(logprob(True)+logprob(False)). Gate condition: std(c) > 0.05 for ALL 3 models, confirming non-degenerate confidence distribution.

This hypothesis is INCREMENTAL, building on h-m1 (solutions + pass@1 values) and h-m2 (tier assignments). No model training is required — inference-only experiment.

---

## 2. Problem Statement

**Research Question:** Can LLMs produce non-degenerate confidence signals via zero-shot P(True) prompting?

**Mechanism Under Test:** For each (problem, solution) pair, append a zero-shot correctness question and extract the logit distribution over "True"/"False" tokens at the first generated position. Normalize to obtain confidence score c ∈ [0,1].

**Why Needed:** h-m4 requires per-pair confidence scores to compute tier-stratified ECE. This step validates that P(True) produces meaningful (non-degenerate) signal before investing in ECE computation.

**Failure Mode:** If c values cluster at 0.5 (pure uncertainty) or 1.0 (overconfidence), std(c) ≤ 0.05, the mechanism fails and an alternative prompt must be tried.

---

## 3. Hypothesis Context

- **Prerequisite:** h-m2 COMPLETED (SHOULD_WORK gate PASS — all 3/3 Jaccard pairs > 0.3)
- **Reused from h-m1:** k=5 solutions per (problem, model), pass@1 values, correctness labels
- **Reused from h-m2:** tier_assignments.csv (542 rows × [model, problem_id, tier, pass@1])
- **Expected confidence range from Run 3:** P(True) values 0.57–0.91 across 3 model families

---

## 4. Data Specification

### 4.1 Primary Dataset

| Property | Value |
|----------|-------|
| Name | EvalPlus (HumanEval+ + MBPP+) |
| Size | 542 problems (164 HumanEval+ + 378 MBPP+) |
| Source | Liu et al. NeurIPS 2023; evalplus Python package |
| Access | `from evalplus.data import get_human_eval_plus, get_mbpp_plus` |
| Cache | `~/.cache/evalplus/` (pre-populated from h-m1) |
| Download Required | NO — auto-load via evalplus package |

### 4.2 Dependency Input Files (From Previous Hypotheses)

| File | Source Hypothesis | Content | Path |
|------|------------------|---------|------|
| tier_assignments.csv | h-m2 | 542 × [model, problem_id, tier, pass@1] | `../h-m2/results/tier_assignments.csv` |
| pass_at_1_hm1_verified.json | h-m1 | pass@1 per (problem, model) | `../h-m1/results/pass_at_1_hm1_verified.json` |
| solutions_{model}.jsonl | h-m1 | k=5 solutions per (problem, model) | `../h-m1/results/solutions_{model}.jsonl` |
| Correctness labels | h-m1 | binary correct/incorrect per solution | embedded in solutions JSONL |

**NOTE:** No manual data download required. All data reused from h-m1/h-m2.

### 4.3 Data Scope

- **Pairs processed:** All (problem, solution) pairs in hard+easy tiers from tier_assignments.csv
- **Estimated pairs:** hard_n × 5 + easy_n × 5 per model (h-e1: n_hard ~68–199, n_easy ~24–176)
- **Total across 3 models:** ~3,000–5,000 (problem, solution) pairs

### 4.4 P(True) Prompt Template

```
{problem_description}

```python
{solution_code}
```

Is this solution correct? Answer True or False.
Answer:
```

---

## 5. Functional Requirements

### FR-1: P(True) Logprob Extraction (CRITICAL)

**Description:** For each (problem, solution) pair in hard+easy tiers, extract normalized confidence c using model.generate() with output_logits=True.

**Implementation:**
```python
def extract_ptrue_confidence(model, tokenizer, problem_prompt, solution_code, device) -> float:
    """
    Returns c in [0,1]: normalized P(True)/(P(True)+P(False))
    """
    prompt = f"{problem_prompt}\n\n```python\n{solution_code}\n```\n\nIs this solution correct? Answer True or False.\nAnswer:"
    true_id  = tokenizer.encode(" True",  add_special_tokens=False)[0]
    false_id = tokenizer.encode(" False", add_special_tokens=False)[0]
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=1, return_dict_in_generate=True, output_logits=True)
    logits = out.logits[0][0]  # shape: (vocab_size,)
    log_probs = F.log_softmax(logits, dim=-1)
    c = torch.softmax(torch.tensor([log_probs[true_id].item(), log_probs[false_id].item()]), dim=0)[0].item()
    return c
```

**Reference:** Kadavath et al. 2022; HuggingFace Transformers PR #28667 (merged 2024-02-19)

### FR-2: Tier Filtering

**Description:** Load tier_assignments.csv from h-m2 results. Filter to rows where tier ∈ {hard, easy} per model. Iterate over (problem_id, model, tier) tuples.

**Input:** `../h-m2/results/tier_assignments.csv`
**Output:** Filtered DataFrame with columns [problem_id, model, tier, pass@1]

### FR-3: Solution Loading

**Description:** For each (problem_id, model) in filtered tier assignments, retrieve the k=5 solutions from h-m1 solutions JSONL files.

**Input:** `../h-m1/results/solutions_{model_shortname}.jsonl`
**Output:** List of k=5 solution strings per (problem, model)

### FR-4: Confidence Score Storage

**Description:** Store extracted confidence scores in structured format:
```python
{
  "model_name": {
    "problem_id": {
      "tier": "hard"|"easy",
      "pass_at_1": float,
      "confidence_scores": [c1, c2, c3, c4, c5],  # k=5 solutions
      "correctness_labels": [0|1, ...]
    }
  }
}
```

Save as: `h-m3/results/ptrue_confidence_scores.json`

### FR-5: Gate Metrics Computation

**Description:** Compute std(c) and mean(c) per model across ALL (problem, solution) pairs in hard+easy tiers.

```python
std_c_per_model = {model: np.std(all_confidence_scores[model]) for model in models}
mean_c_per_model = {model: np.mean(all_confidence_scores[model]) for model in models}
```

**Gate check:** std(c) > 0.05 for ALL 3 models.

### FR-6: Secondary Metrics

**Description:** Compute additional diagnostic metrics:
- min(c)/max(c) per model
- 20-bin histogram of c values per model
- mean(c) and std(c) by tier (hard vs. easy)
- Point-biserial correlation between c and binary correctness label

### FR-7: Visualization (5 Figures)

| Figure | Description | Filename |
|--------|-------------|----------|
| Fig 1 | Bar chart: std(c) per model vs. threshold 0.05 | `fig1_gate_check.png` |
| Fig 2 | Histogram: c distribution per model (3 subplots, 20 bins) | `fig2_c_histograms.png` |
| Fig 3 | Scatter: c vs. pass@1 per model | `fig3_c_vs_pass_at_1.png` |
| Fig 4 | Box plots: c by model × tier (hard vs. easy) | `fig4_c_by_tier.png` |
| Fig 5 | CDF: c values per model | `fig5_c_cdf.png` |

All figures saved to `h-m3/figures/`.

### FR-8: Mechanism Verification

**Description:** At startup, verify P(True) mechanism is operational:
```python
def verify_ptrue_mechanism(confidence_scores_by_model, out_logits_sample) -> tuple[bool, dict]:
    indicators = {
        "logits_extracted": out_logits_sample is not None and len(out_logits_sample) > 0,
        "vocab_size_correct": out_logits_sample[0][0].shape[0] > 30000,
        "c_values_in_range": all(0.0 <= c <= 1.0 for c in confidence_scores_by_model["llama3"]),
        "non_degenerate": all(np.std(scores) > 0.05 for scores in confidence_scores_by_model.values())
    }
    return all(indicators.values()), indicators
```

### FR-9: Fallback Prompt (If Degenerate)

If std(c) ≤ 0.05 for any model, retry with alternative prompt:
```
{problem_description}

```python
{solution_code}
```

Does this solution pass all tests? Answer True or False.
Answer:
```

### FR-10: Results Persistence

Save validated results file: `h-m3/results/ptrue_hm3_verified.json` with schema:
```yaml
schema_version: "FR-10.1"
hypothesis_id: "h-m3"
gate:
  type: "MUST_WORK"
  condition: "std(c) > 0.05 for ALL 3 models"
  satisfied: true|false
models:
  llama3_8b:
    std_c: float
    mean_c: float
    n_pairs: int
    gate_pass: bool
  codellama_7b:
    std_c: float
    mean_c: float
    n_pairs: int
    gate_pass: bool
  deepseek_6.7b:
    std_c: float
    mean_c: float
    n_pairs: int
    gate_pass: bool
```

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| **Precision** | float16 (consistent with h-m1/h-m2) |
| **Reproducibility** | seed=42, greedy decoding (temperature=0) |
| **GPU** | Single GPU (CUDA_VISIBLE_DEVICES=<empty_gpu>) |
| **max_new_tokens** | 1 (extract only first token logit) |
| **Batch Size** | 1 per call (sequential logprob extraction) |
| **transformers version** | ≥ 4.38 (output_logits=True requires PR #28667) |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
transformers>=4.38.0    # Required: output_logits=True (PR #28667)
evalplus>=0.1.0
numpy>=1.24
scipy>=1.10             # pointbiserialr
matplotlib>=3.7
pandas>=2.0             # tier_assignments.csv loading
tqdm>=4.65              # progress bars
```

### 7.2 Input Files (From Previous Hypotheses)

```
../h-m2/results/tier_assignments.csv
../h-m1/results/pass_at_1_hm1_verified.json
../h-m1/results/solutions_llama3_8b.jsonl
../h-m1/results/solutions_codellama_7b.jsonl
../h-m1/results/solutions_deepseek_6.7b.jsonl
```

### 7.3 Model Checkpoints (Pre-cached)

```
~/.cache/huggingface/  # Pre-populated from h-m1/h-m2
  NousResearch/Meta-Llama-3-8B
  codellama/CodeLlama-7b-hf
  deepseek-ai/deepseek-coder-6.7b-base
```

---

## 8. Success Criteria

### 8.1 Gate Condition (MUST_WORK)

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| std(c) for Llama3-8B | > 0.05 | TBD |
| std(c) for CodeLlama-7b | > 0.05 | TBD |
| std(c) for DeepSeek-6.7b | > 0.05 | TBD |

**ALL 3 must pass.** If any fails, try alternative prompt (FR-9); if still degenerate, report as mechanism failure.

### 8.2 Secondary Checks

| Check | Expected |
|-------|----------|
| mean(c) per model | 0.6–0.8 (Run 3 prior: 0.57–0.91) |
| Range of c | spans at least [0.2, 0.9] |
| Point-biserial correlation c vs. correctness | positive (c higher for correct solutions) |

---

## 9. Output Artifacts

| Artifact | Path |
|----------|------|
| Confidence scores JSON | `h-m3/results/ptrue_confidence_scores.json` |
| Verified results | `h-m3/results/ptrue_hm3_verified.json` |
| Figure 1 (gate check) | `h-m3/figures/fig1_gate_check.png` |
| Figure 2 (histograms) | `h-m3/figures/fig2_c_histograms.png` |
| Figure 3 (scatter) | `h-m3/figures/fig3_c_vs_pass_at_1.png` |
| Figure 4 (box plots) | `h-m3/figures/fig4_c_by_tier.png` |
| Figure 5 (CDF) | `h-m3/figures/fig5_c_cdf.png` |

---

## 10. Phase 4 Guidance

- Load models in float16 with device_map="auto"
- Set CUDA_VISIBLE_DEVICES before any Python invocation
- Verify `output_logits=True` works with `max_new_tokens=1` on first test pair before full loop
- Implement progress saving (checkpoint every 100 pairs) to allow resume
- Log true_id and false_id at startup to verify correct tokenization
- For h-m4 consumption: output must include per-pair c values with tier labels
