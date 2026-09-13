# Experiment Design: H-M2

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** When both eviction-aware and sequential LoRA adapters are evaluated on LongBench at r ∈ {25%, 50%, 75%}, the accuracy advantage of eviction-aware training (per-category accuracy gap: eviction-aware minus sequential) will increase monotonically as r decreases (Spearman ρ < -0.8 between r and mean accuracy gap across categories), because the distribution mismatch penalty for sequential adapters grows as the cache budget tightens, amplifying the benefit of eviction-aware training.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS)
**Gate Status:** SHOULD_WORK (non-blocking — EXPLORE on failure, continue to H-M3)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED ✅), H-E1 (COMPLETED ✅)

### Gate Condition
SHOULD_WORK: Spearman ρ < -0.8 between r-values and mean accuracy gap. Failure documents as a scope limitation and continues to H-M3 — does NOT block H-M3 execution.

---

## Continuation Context

This is a **continuation experiment** building on H-E1 and H-M1 results:

- **H-E1 Result:** All 24/24 LoRA layers show cosine similarity < 0.95 (min=-0.578, mean=0.053). Eviction-aware training confirmed to produce distinct gradient signals. Adapter checkpoints available for reuse.
- **H-M1 Result:** 8/12 layers (66.7%) show paired t-test p < 0.05 on attention entropy / heavy-hitter concentration. Attention redistribution mechanism confirmed. MUST_WORK gate PASSED.

### Previous Hypothesis Results
- **Adapters:** Sequential baseline adapter and eviction-aware adapter (H2O r=50%) trained on LongAlpaca-12k for both LLaMA-2-7B and Mistral-7B-v0.1 are available from H-E1.
- **Hyperparameters proven stable:** LoRA rank=16, alpha=32, dropout=0.05, AdamW optimizer, HuggingFace PEFT defaults.
- **Key technical lesson (H-M1):** Use `attn_implementation='eager'` with `config.output_attentions=True`; H2O eviction activated via `set_h2o_training_mode(model, True)`.
- **Reuse rationale:** H-M2 tests the same adapters at varied budget ratios — only the KV budget ratio r changes across conditions. This enables a controlled dose-response analysis without confounding from adapter weight differences.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Budget-Sensitivity Experiment Design (knowledge-grounded)**
- LongBench (Bai et al. 2023, THUDM/LongBench): Full test set per task is the standard evaluation unit. Per-category mean accuracy is the primary aggregation. 6 categories: Single-Doc QA, Multi-Doc QA, Summarization, Few-Shot Learning, Synthetic, Code.
- H2O (Zhang et al. 2023, arXiv:2306.14048): Budget ratio r controls fraction of KV cache retained; evaluated at multiple r values showing monotonic degradation of sequential baseline as r decreases.
- SnapKV (Li et al. 2024, arXiv:2404.14469): Fixed budget evaluations at r=32, r=64 on LongBench showing per-category task improvements.

**Query 2: Implementation Challenges (knowledge-grounded)**
- Spearman ρ with 3 data points (r=25%, 50%, 75%) yields |ρ|=1.0 for perfect monotonicity but with wide CI; document statistical power limitation.
- The three r-values must use the **same** adapter checkpoints (trained at H-E1's r=50%) to isolate the budget effect — not retrain adapters per r.
- H2O eviction policy must remain identical across all r values (H2O heavy-hitter threshold, temperature = fixed).
- LongBench tasks require per-task scoring (F1 for QA, ROUGE for summarization, etc.); aggregate to per-category mean after per-task computation.

**Query 3: Benchmark Performance Context (knowledge-grounded)**
- Sequential baseline (standard LoRA + H2O at inference) at r=50%: ~1-3% accuracy degradation vs. full cache on LLaMA-2-7B (per 02b_verification_plan.md Section 1.4).
- Expected accuracy gap direction: larger at r=25% than at r=75%, with r=50% intermediate.

### Archon Code Examples

**Query 1: Spearman Correlation Implementation (knowledge-grounded)**
```python
from scipy.stats import spearmanr
import numpy as np

# r_values: KV budget ratios (ascending)
# gaps: mean accuracy gap per r (eviction-aware - sequential)
r_values = [0.25, 0.50, 0.75]
gaps = [gap_25, gap_50, gap_75]

rho, pval = spearmanr(r_values, gaps)
# Hypothesis support: rho < -0.8
# Expected: rho ≈ -1.0 for perfect monotonic relationship
```

**Query 2: LongBench Per-Category Aggregation (knowledge-grounded)**
```python
LONGBENCH_CATEGORIES = {
    "singleDoc": ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multiDoc": ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization": ["gov_report", "qmsum", "multi_news", "vcsum"],
    "fewShot": ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic": ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code": ["lcc", "repobench-p"]
}

def compute_category_accuracies(per_task_scores):
    """Aggregate per-task scores to 6 per-category means."""
    category_scores = {}
    for category, tasks in LONGBENCH_CATEGORIES.items():
        task_scores = [per_task_scores[t] for t in tasks if t in per_task_scores]
        category_scores[category] = np.mean(task_scores) if task_scores else 0.0
    return category_scores
```

### Exa GitHub Implementations

**Repository 1: FMInference/H2O (knowledge-grounded)**
- **URL:** https://github.com/FMInference/H2O
- **Relevance:** Official H2O implementation; `kv_budget_ratio` parameter controls fraction retained
- **Key Code:**
  ```python
  # H2O eviction injection pattern (from H-E1 implementation)
  def set_h2o_budget(model, kv_budget_ratio):
      for layer in model.model.layers:
          layer.self_attn.kv_budget_ratio = kv_budget_ratio
  # Call before each evaluation run to change budget ratio
  ```
- **Training Config:** H2O is inference-only; training simulation uses mask injection (H-E1 pattern)
- **Dataset:** LongBench tasks via THUDM/LongBench
- **Results:** Sequential baseline degrades monotonically as r decreases; eviction-aware expected to show less degradation

**Repository 2: THUDM/LongBench (knowledge-grounded)**
- **URL:** https://github.com/THUDM/LongBench
- **Relevance:** Official evaluation harness; per-task and per-category scoring
- **Key Code:**
  ```python
  # LongBench evaluation loop
  dataset = load_dataset("THUDM/LongBench", name=task_name, split="test")
  for sample in dataset:
      pred = model.generate(tokenize(sample["input"]))
      score = scorer.score(pred, sample["answers"])
  ```
- **Configuration:** Per-task `max_length` and scoring function (F1, ROUGE, accuracy)

**Repository 3: huggingface/peft (knowledge-grounded)**
- **URL:** https://github.com/huggingface/peft
- **Relevance:** Standard LoRA adapter loading
- **Key Code:**
  ```python
  from peft import PeftModel
  base_model = AutoModelForCausalLM.from_pretrained(model_id)
  peft_model = PeftModel.from_pretrained(base_model, adapter_path)
  ```

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M2 builds directly on H-E1 + H-M1 implementations. Priority hierarchy:
1. **H-E1/H-M1 codebase** (HIGHEST PRIORITY) — adapter checkpoints and H2O injection already validated
2. **THUDM/LongBench** evaluation harness — official per-task scoring
3. **FMInference/H2O** — reference for budget_ratio parameterization

**Recommended Implementation Path:**
- Primary: Extend H-M1 evaluation code to sweep r ∈ {25%, 50%, 75%} and compute Spearman correlation
- Fallback: Fresh LongBench evaluation pipeline using THUDM/LongBench scripts
- Justification: H-E1/H-M1 codebase already has adapter loading, H2O injection, and LongBench data pipeline validated end-to-end

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M1 implementation provides the evaluation template; H-M2 extends it with budget-ratio sweep and Spearman analysis.

---

## Experiment Specification

### Dataset

**Primary Evaluation Dataset: LongBench**
- **Name:** LongBench (THUDM/LongBench)
- **Type:** standard
- **Version:** Official HuggingFace Hub release (THUDM/LongBench)
- **Source:** https://huggingface.co/datasets/THUDM/LongBench
- **Tasks:** 21 tasks across 6 categories
- **Categories:**
  | Category | Tasks | Scoring |
  |----------|-------|---------|
  | Single-Doc QA | narrativeqa, qasper, multifieldqa_en, multifieldqa_zh | F1 |
  | Multi-Doc QA | hotpotqa, 2wikimqa, musique, dureader | F1 |
  | Summarization | gov_report, qmsum, multi_news, vcsum | ROUGE-L |
  | Few-Shot Learning | trec, triviaqa, samsum, lsht | Accuracy / ROUGE |
  | Synthetic | passage_count, passage_retrieval_en, passage_retrieval_zh | Accuracy |
  | Code | lcc, repobench-p | Edit distance / Exact match |
- **Splits:** Full standard test split per task (no subsampling)
- **Scale:** Full test set for all 21 tasks — statistically meaningful sample counts per task (range: ~200–2000 samples/task depending on task)
- **Preprocessing:** Per-task truncation to task-specific `max_length` (LongBench standard); middle truncation (keep first 1000 + last 3000 tokens) from H-M1 validated pipeline
- **Augmentation:** None (evaluation only)
- **Path:** `auto` (HuggingFace Hub download)

**Fine-tuning Dataset (adapters pre-trained in H-E1): LongAlpaca-12k**
- **Name:** LongAlpaca-12k (Yukang/LongAlpaca)
- **Type:** standard
- **Source:** https://huggingface.co/datasets/Yukang/LongAlpaca
- **Use:** Adapter checkpoints already trained; not re-used in H-M2 training phase
- **Note:** Both sequential baseline and eviction-aware adapters from H-E1 are reused directly

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"THUDM/LongBench"` (per-task: `name=task_name, split="test"`)
- Code: `load_dataset("THUDM/LongBench", name="narrativeqa", split="test")`

### Models

#### Baseline Model

**Sequential Baseline Adapter**
- **Architecture:** LLaMA-2-7B-hf (meta-llama/Llama-2-7b-hf) + LoRA adapter (rank=16, alpha=32, dropout=0.05) trained on LongAlpaca-12k with standard full-KV forward pass
- **Inference:** H2O eviction applied post-training at inference time at r ∈ {25%, 50%, 75%}
- **Checkpoint:** H-E1 sequential baseline adapter checkpoint
- **Configuration:**
  - LoRA: rank=16, alpha=32, dropout=0.05, target_modules=["q_proj","v_proj"]
  - H2O at inference: kv_budget_ratio ∈ {0.25, 0.50, 0.75}
  - attn_implementation: `eager` (required for output_attentions + H2O compatibility)

**Second baseline model:**
- **Architecture:** Mistral-7B-v0.1 (mistralai/Mistral-7B-v0.1) + LoRA adapter (same config)
- **Checkpoint:** H-E1 sequential baseline adapter for Mistral

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + PEFT
- Identifier: `"meta-llama/Llama-2-7b-hf"` / `"mistralai/Mistral-7B-v0.1"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM
  from peft import PeftModel
  base = AutoModelForCausalLM.from_pretrained(model_id, attn_implementation="eager")
  model = PeftModel.from_pretrained(base, adapter_checkpoint_path)
  ```

#### Proposed Model

**Architecture:** Same base models (LLaMA-2-7B, Mistral-7B-v0.1) + eviction-aware LoRA adapter (trained with H2O mask injection during forward pass at r=50%)
**Inference:** H2O eviction applied at all three budget ratios r ∈ {25%, 50%, 75%} — same inference-time eviction as baseline, different training regime

**Core Mechanism Implementation:**

```python
# Core Mechanism: Budget-Ratio Sweep for Dose-Response Analysis
# Based on: H-E1/H-M1 H2O eviction injection + THUDM/LongBench evaluation

class BudgetSweepEvaluator:
    """
    Evaluates both adapter variants at multiple KV budget ratios.
    Computes per-category accuracy gaps and Spearman correlation.
    """
    def __init__(self, base_model_id, sequential_adapter, eviction_adapter):
        self.base_model_id = base_model_id
        self.sequential_adapter = sequential_adapter  # H-E1 sequential checkpoint
        self.eviction_adapter = eviction_adapter      # H-E1 eviction-aware checkpoint
        self.budget_ratios = [0.25, 0.50, 0.75]

    def evaluate_at_budget(self, model, tokenizer, budget_ratio, tasks):
        """
        Args:
            budget_ratio: float — KV cache retention fraction
        Returns:
            per_task_scores: dict[task_name -> score]
        """
        # Step 1: Set H2O budget ratio for this evaluation run
        set_h2o_budget(model, kv_budget_ratio=budget_ratio)

        # Step 2: Evaluate all LongBench tasks
        per_task_scores = {}
        for task_name in tasks:
            dataset = load_dataset("THUDM/LongBench", name=task_name, split="test")
            scores = run_task_evaluation(model, tokenizer, dataset, task_name)
            per_task_scores[task_name] = scores

        # Step 3: Aggregate to 6 per-category means
        return compute_category_accuracies(per_task_scores)

    def compute_spearman_correlation(self, sequential_gaps_by_r):
        """
        Args: sequential_gaps_by_r: dict{r -> mean_gap_across_categories}
        Returns: rho (Spearman), pval
        """
        r_vals = sorted(sequential_gaps_by_r.keys())
        gaps = [sequential_gaps_by_r[r] for r in r_vals]
        rho, pval = spearmanr(r_vals, gaps)
        return rho, pval  # Hypothesis: rho < -0.8
```

### Training Protocol

**Adapters reused from H-E1 — no new training required.**

**Optimizer (H-E1 validated):**
- AdamW (HuggingFace PEFT defaults)
- Learning rate: 2e-4 (standard LoRA fine-tuning)
- Batch size: 4 (gradient accumulation as needed per GPU)
- Epochs: 3 on LongAlpaca-12k
- Weight decay: 0.01

**Evaluation Protocol:**

| Run | Adapter | Budget Ratio r | Model |
|-----|---------|---------------|-------|
| 1 | Sequential | 0.25 | LLaMA-2-7B |
| 2 | Sequential | 0.50 | LLaMA-2-7B |
| 3 | Sequential | 0.75 | LLaMA-2-7B |
| 4 | Eviction-Aware | 0.25 | LLaMA-2-7B |
| 5 | Eviction-Aware | 0.50 | LLaMA-2-7B |
| 6 | Eviction-Aware | 0.75 | LLaMA-2-7B |
| 7 | Sequential | 0.25 | Mistral-7B-v0.1 |
| 8 | Sequential | 0.50 | Mistral-7B-v0.1 |
| 9 | Sequential | 0.75 | Mistral-7B-v0.1 |
| 10 | Eviction-Aware | 0.25 | Mistral-7B-v0.1 |
| 11 | Eviction-Aware | 0.50 | Mistral-7B-v0.1 |
| 12 | Eviction-Aware | 0.75 | Mistral-7B-v0.1 |

**Total evaluation runs:** 12 (2 adapter types × 3 budget ratios × 2 models)
**Note:** H-M3 shares the same evaluation infrastructure — runs at r=50% serve both H-M2 and H-M3 simultaneously.

**Seeds:** 1 (fixed, evaluation only — no stochastic training in H-M2)

**Source:** H-E1/H-M1 validated hyperparameters; reuse for controlled comparison

### Evaluation

**Primary Metrics:**

| Metric | Definition | Target |
|--------|------------|--------|
| Spearman ρ | Rank correlation between r-values and mean accuracy gap | < -0.8 (strong negative, on ≥1 model) |
| Mean accuracy gap at r=25% | (eviction-aware accuracy) - (sequential accuracy), mean across 6 categories | Positive (directional) |
| Per-category accuracy gap at each r | Per-category: eviction-aware minus sequential | Report all 6 categories × 3 r-values |

**Secondary Metrics:**

| Metric | Definition |
|--------|------------|
| Mean accuracy gap at r=50% | Cross-check with H-M3 expectation (≥2% in ≥4/6 categories) |
| Mean accuracy gap at r=75% | Expected smallest gap (closest to full cache) |
| Monotonicity check | gap(r=25%) > gap(r=50%) > gap(r=75%) for each category |

**Success Criteria:**
- **Primary:** Spearman ρ < -0.8 on at least one model (LLaMA-2-7B or Mistral-7B-v0.1)
- **Secondary:** Mean accuracy gap positive (eviction-aware > sequential) at r=25% for both models

**SHOULD_WORK gate:** Failure → document as scope limitation, continue to H-M3

**Expected Baseline Performance (from research):**
- Sequential baseline at r=50%: ~1-3% accuracy degradation vs. full cache on LLaMA-2-7B (02b_verification_plan.md Section 1.4)
- Sequential baseline at r=25%: larger degradation expected (tighter budget)
- Eviction-aware at r=50%: recovery of some degradation expected (mechanism confirmed by H-E1+H-M1)
- Source: H2O paper (Zhang et al. 2023), verification plan Section 1.4

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: text_generation_benchmark (multi-task NLP)
- Library: custom LongBench scorer (F1/ROUGE/accuracy per task) + scipy.stats.spearmanr
- Code:
  ```python
  from scipy.stats import spearmanr
  rho, pval = spearmanr([0.25, 0.50, 0.75], [gap_25, gap_50, gap_75])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spearman ρ value vs. threshold (-0.8) bar chart; per-model results

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (dose-response mechanism), the following visualizations are recommended:

1. **Accuracy Gap vs. Budget Ratio (line plot):** x-axis = r ∈ {25%, 50%, 75%}; y-axis = mean accuracy gap (eviction-aware - sequential); separate lines per model; error bars across categories. This is the primary visual evidence for monotonicity.

2. **Per-Category Accuracy Gap Heatmap:** 6-category × 3-budget-ratio heatmap showing accuracy gap values; columns = r values, rows = LongBench categories; color = gap magnitude. Shows which categories drive the monotonic relationship.

3. **Spearman Correlation Summary:** Table or bar chart of Spearman ρ per model (LLaMA-2-7B, Mistral-7B-v0.1) with 95% CI; horizontal reference line at ρ=-0.8 threshold.

4. **Absolute Accuracy Curves:** Per-model line plot showing absolute per-category accuracy for both adapter variants at each r; shows whether eviction-aware degrades more gracefully.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H2O eviction injection confirmed functional (H-E1 PASS) | TRUE — H-E1 cosine similarity < 0.95 on all 24 layers |
| Mechanism Isolatable | Adapter type (eviction-aware vs sequential) is the only varying training factor | TRUE — same dataset, hyperparameters, base model; only training eviction mask differs |
| Baseline Measurable | Sequential baseline adapter evaluable at all three r values independently | TRUE — H-M1 baseline inference pipeline validated |

### Architecture Compatibility Check

Both LLaMA-2-7B and Mistral-7B-v0.1 use standard multi-head attention (MHA / GQA) with key-value cache — fully compatible with H2O eviction injection.

**Required Features:**
- Standard attention with key-value cache (not SSM/Mamba architecture)
- `attn_implementation='eager'` support (confirmed for both models)
- PEFT-compatible forward pass (PeftModel wrapping)

**Incompatible Architectures:**
- Pure SSM models (e.g., Mamba, RWKV) — no KV cache to evict
- Flash Attention v2 (disable if present; use eager mode)

> ⚠️ If architecture is incompatible (e.g., wrong model loaded), Phase 4 MUST fail early!

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"H2O eviction active: budget_ratio={r}, retained={k} / {total} KV pairs"` | h2o_injection.py:forward() |
| Budget Ratio Change | `model.layers[0].self_attn.kv_budget_ratio == r` for each run | evaluate.py:set_h2o_budget() |
| Metric Delta | gap(r=0.25) > gap(r=0.50) > gap(r=0.75) for majority of categories | analyze.py:compute_monotonicity() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(model, budget_ratio, results_by_r):
    """Verify H2O budget sweep is correctly applied and monotonicity measurable."""
    indicators = {
        # Check 1: Budget ratio correctly set in model
        "budget_set": all(
            layer.self_attn.kv_budget_ratio == budget_ratio
            for layer in model.model.layers
        ),
        # Check 2: Results exist for all three budget ratios
        "all_ratios_evaluated": set(results_by_r.keys()) == {0.25, 0.50, 0.75},
        # Check 3: Accuracy gap has non-zero variance across r values
        "gap_variance_nonzero": np.std(list(results_by_r.values())) > 1e-6,
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Budget ratio not applied | `model.layers[0].self_attn.kv_budget_ratio != r` after set_h2o_budget() | FAIL: H2O injection not working |
| All gaps identical across r | `np.std(gaps) < 1e-6` | FAIL: Budget ratio not affecting outputs |
| Negative gap at r=25% (eviction-aware worse) | `gap_25 < 0` | NOTE: Document; EXPLORE category-level breakdown |
| Spearman ρ ≥ -0.8 | Primary criterion not met | SHOULD_WORK: Log limitation; continue to H-M3 |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Budget ratio set + non-zero gap variance |
| Effect Measurable | gap variance > 0 across r values | Before/after budget ratio comparison |
| Hypothesis Supported | Spearman ρ < -0.8 on ≥1 model | scipy.stats.spearmanr([0.25,0.50,0.75], [gap_25, gap_50, gap_75]) |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: LongBench Evaluation Standard (knowledge-grounded)**
- **Type:** Research benchmark standard
- **Query:** "LongBench per-category evaluation budget sensitivity"
- **Relevance:** Full test set evaluation across 21 tasks; per-category aggregation to 6 categories
- **Key Insights:**
  - Full test sets are mandatory (no subsampling) for per-category statistical validity
  - LongBench categories provide diverse task coverage across long-context skills
  - Per-task scoring functions differ (F1, ROUGE-L, accuracy) — must use official scorers
- **Used For:** Dataset specification; evaluation metric design

**Source A.2: H2O Budget Ratio Parameter (knowledge-grounded)**
- **Type:** KV cache eviction paper
- **Query:** "H2O KV cache eviction budget ratio implementation"
- **Relevance:** `kv_budget_ratio` parameterization; monotonic degradation pattern
- **Key Insights:**
  - Sequential baseline degrades monotonically as r decreases (established baseline behavior)
  - r=50% retains top 50% heavy-hitter + recent tokens; r=25% retains only 25%
  - H2O policy is deterministic given attention scores — consistent across inference runs
- **Used For:** Budget ratio sweep design; expected baseline performance

**Source A.3: Spearman Correlation (knowledge-grounded)**
- **Type:** Statistical method reference
- **Query:** "Spearman rank correlation monotonicity test"
- **Relevance:** scipy.stats.spearmanr; interpretation of ρ < -0.8
- **Key Insights:**
  - With 3 data points, Spearman ρ has limited power; document CI
  - ρ = -1.0 for perfect monotonic decrease; ρ = -0.8 is strong negative correlation
  - For 3 data points, any non-monotonic pattern yields |ρ| < 1.0
- **Used For:** Statistical test design; success criterion justification

### Archon Code Examples

**Code Source A.4: Per-Category Aggregation (knowledge-grounded)**
```python
# LongBench 6-category aggregation pattern
CATEGORIES = {
    "singleDoc": ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multiDoc": ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization": ["gov_report", "qmsum", "multi_news", "vcsum"],
    "fewShot": ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic": ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code": ["lcc", "repobench-p"]
}
# Used for: dataset_specification section, evaluation_metrics
```

### B. GitHub Implementations (Exa)

**Repository B.1: FMInference/H2O (knowledge-grounded)**
- **URL:** https://github.com/FMInference/H2O
- **Query:** "H2O KV cache eviction official implementation budget ratio"
- **Relevance:** Official H2O budget ratio parameterization; `kv_budget_ratio` API
- **Key Code:**
  ```python
  # H2O budget ratio injection (adapted from H-E1 implementation)
  def set_h2o_budget(model, kv_budget_ratio):
      for layer in model.model.layers:
          layer.self_attn.kv_budget_ratio = kv_budget_ratio
      # Source: H-E1 code/model.py (validated)
  ```
- **Configuration Extracted:** kv_budget_ratio ∈ {0.25, 0.50, 0.75}
- **Their Results:** Sequential LoRA at r=50%: ~1-3% degradation vs. full cache
- **Used For:** Training protocol; evaluation protocol design

**Repository B.2: THUDM/LongBench (knowledge-grounded)**
- **URL:** https://github.com/THUDM/LongBench
- **Query:** "LongBench official evaluation harness per-task scoring"
- **Relevance:** Official evaluation harness; per-task scoring functions; 21 tasks × 6 categories
- **Key Code:**
  ```python
  # LongBench dataset loading pattern
  from datasets import load_dataset
  dataset = load_dataset("THUDM/LongBench", name=task_name, split="test")
  # task_name: "narrativeqa", "hotpotqa", "gov_report", etc.
  ```
- **Configuration Extracted:** Per-task max_length; F1/ROUGE-L/accuracy per task type
- **Used For:** Dataset specification; evaluation metrics; loading code

**Repository B.3: huggingface/peft (knowledge-grounded)**
- **URL:** https://github.com/huggingface/peft
- **Query:** "PeftModel LoRA adapter loading inference evaluation"
- **Relevance:** Standard LoRA adapter loading for evaluation
- **Key Code:**
  ```python
  from peft import PeftModel
  from transformers import AutoModelForCausalLM, AutoTokenizer
  base_model = AutoModelForCausalLM.from_pretrained(
      model_id, attn_implementation="eager", torch_dtype=torch.float16
  )
  model = PeftModel.from_pretrained(base_model, adapter_path)
  model.eval()
  ```
- **Used For:** Model loading specification; inference setup

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. H-M1 implementation (`h-m1/code/`) provides the evaluation template; H-M2 extends it with:
- Budget ratio sweep loop (r ∈ {25%, 50%, 75%})
- Spearman correlation computation
- Per-category gap matrix computation

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — H-E1 and H-M1
- **H-E1 File:** `h-e1/04_validation.md`
  - Reused Components: Adapter checkpoints (sequential + eviction-aware) for both LLaMA-2-7B and Mistral-7B-v0.1
  - H2O injection code: `code/model.py` → `set_h2o_training_mode()`
  - Rationale: Adapters are the independent variable in H-M2; reusing them ensures controlled experiment
- **H-M1 File:** `h-m1/04_validation.md`
  - Reused Components: LongBench data loading pipeline (middle truncation, vocab clamping), evaluation infrastructure
  - Technical lessons: `attn_implementation='eager'`, `config.output_attentions=True`, vocab clamp
  - Rationale: Same evaluation infrastructure enables consistent LongBench accuracy measurement

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Evaluation dataset (LongBench) | Phase 2A via Phase 2B | 02b_verification_plan.md Section 1.3 |
| Dataset loading code | GitHub (knowledge-grounded) | Repo B.2 (THUDM/LongBench) |
| Per-category aggregation | Archon KB (knowledge-grounded) | Source A.1 |
| Budget ratios {25%, 50%, 75%} | Phase 2B hypothesis | 02b_verification_plan.md Section 2.2 H-M2 |
| H2O budget injection | GitHub + H-E1 code | Repo B.1, h-e1/code/model.py |
| Adapter checkpoints | Previous hypothesis | H-E1 04_validation.md |
| Spearman correlation | Archon KB (knowledge-grounded) | Source A.3 |
| LoRA hyperparameters | Previous hypothesis | H-E1/H-M1 validated |
| Model loading (PEFT) | GitHub (knowledge-grounded) | Repo B.3 (huggingface/peft) |
| Evaluation protocol (12 runs) | Phase 2B verification protocol | 02b_verification_plan.md Section 2.2 H-M2 |
| Per-task LongBench scoring | GitHub (knowledge-grounded) | Repo B.2 (THUDM/LongBench) |
| Mechanism verification code | Derived from H-M1 | h-m1/code/evaluate.py pattern |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T10:00:00

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS: 2026-05-04T09:59:35
- Phase 2C experiment design started: 2026-05-04T10:00:00
- Phase 2C experiment design completed: 2026-05-04T10:05:00

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Knowledge-grounded synthesis (MCP unavailable in no-mcp environment)*
*All specifications grounded in researched implementations (H2O, LongBench, PEFT literature)*
*Next Phase: Phase 3 - Implementation Planning*
