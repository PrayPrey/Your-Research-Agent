# Product Requirements Document: H-M2
# Budget-Ratio Dose-Response Analysis for Eviction-Aware LoRA

**Hypothesis:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-E1, H-M1)
**Date:** 2026-05-04
**Phase:** 3 — Implementation Planning
**Gate:** SHOULD_WORK (Spearman ρ < -0.8 between r-values and mean accuracy gap on ≥1 model)

---

## 1. Executive Summary

H-M2 quantifies how the accuracy advantage of eviction-aware LoRA adapters changes as the KV cache budget ratio r decreases from 75% to 25%. The core prediction is a strong negative monotonic relationship (Spearman ρ < -0.8) between budget ratio r and the mean per-category accuracy gap (eviction-aware minus sequential baseline) across LongBench categories. This is a dose-response analysis — the "dose" is the budget tightness (1/r) and the "response" is the performance gap.

**No new training.** H-E1 adapter checkpoints are reused directly for both LLaMA-2-7B and Mistral-7B-v0.1. This experiment sweeps the inference-time KV budget ratio across r ∈ {25%, 50%, 75%} and measures per-category LongBench accuracy at each operating point.

---

## 2. Problem Statement

H-E1 confirmed adapter weight divergence; H-M1 confirmed attention pattern redistribution. H-M2 asks: *does this mechanistic difference translate into a measurable, monotonically budget-sensitive accuracy advantage?* Sequential baseline adapters were trained without eviction masks, so their attention patterns are calibrated to full KV cache — the distribution mismatch penalty should grow as the cache budget tightens (lower r). If eviction-aware training genuinely internalizes token scarcity, the accuracy advantage should amplify as r decreases.

---

## 3. Functional Requirements

### FR-1: Adapter Loading (H-E1 Checkpoints — No Re-training)

| Adapter | Base Model | Source |
|---------|-----------|--------|
| Sequential Baseline | LLaMA-2-7B | H-E1 sequential baseline checkpoint |
| Eviction-Aware | LLaMA-2-7B | H-E1 eviction-aware checkpoint (trained with H2O r=50% mask) |
| Sequential Baseline | Mistral-7B-v0.1 | H-E1 sequential baseline checkpoint |
| Eviction-Aware | Mistral-7B-v0.1 | H-E1 eviction-aware checkpoint |

- Load with `AutoModelForCausalLM.from_pretrained(model_id, attn_implementation="eager", torch_dtype=torch.float16)`
- Wrap with `PeftModel.from_pretrained(base_model, adapter_path)`
- Inference precision: float16 (matches H-E1/H-M1)
- `attn_implementation="eager"` required for H2O compatibility (H-M1 lesson)

### FR-2: LongBench Dataset Loading

- **Source:** `load_dataset("THUDM/LongBench", name=task_name, split="test")`
- **Tasks:** All 21 tasks across 6 categories (full standard test sets — no subsampling)
- **Categories and tasks:**

| Category | Tasks | Scoring |
|----------|-------|---------|
| Single-Doc QA | narrativeqa, qasper, multifieldqa_en, multifieldqa_zh | F1 |
| Multi-Doc QA | hotpotqa, 2wikimqa, musique, dureader | F1 |
| Summarization | gov_report, qmsum, multi_news, vcsum | ROUGE-L |
| Few-Shot Learning | trec, triviaqa, samsum, lsht | Accuracy / ROUGE |
| Synthetic | passage_count, passage_retrieval_en, passage_retrieval_zh | Accuracy |
| Code | lcc, repobench-p | Edit distance / Exact match |

- **Truncation:** Middle truncation — keep first 1000 + last 3000 tokens (LongBench standard from H-M1)
- **Batch size:** 1 (required — long sequences)
- **Sample scale:** Full standard test split per task (statistically meaningful; range ~200–2000 samples/task)

### FR-3: Budget-Ratio Sweep Evaluator (BudgetSweepEvaluator)

- For each of 12 evaluation runs (2 adapter types × 3 budget ratios × 2 models):
  1. Load appropriate adapter checkpoint
  2. Call `set_h2o_budget(model, kv_budget_ratio=r)` to configure H2O eviction
  3. Run inference on all 21 LongBench tasks at this r value
  4. Score each task with per-task scoring function (F1 / ROUGE-L / Accuracy)
  5. Aggregate to 6 per-category means via `compute_category_accuracies(per_task_scores)`
- Store result matrix: `results[model][adapter_type][r]` → `{category: score}`

**Evaluation runs:**

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

**Note:** Runs 2, 5, 8, 11 (r=50%) are shared with H-M3 — reuse results directly.

### FR-4: Per-Category Gap Computation

- For each (model, r) pair: `gap[model][r][category] = eviction_aware_score - sequential_score`
- Compute `mean_gap[model][r] = mean(gap[model][r][c] for c in 6 categories)`
- Result: 2 models × 3 r-values = 6 (model, r) mean_gap values

### FR-5: Spearman Correlation Analysis

- For each model: `rho, pval = spearmanr([0.25, 0.50, 0.75], [mean_gap[r=0.25], mean_gap[r=0.50], mean_gap[r=0.75]])`
- Primary criterion: ρ < -0.8 on ≥1 model
- Report: ρ and p-value per model; confidence interval note (n=3 data points)
- Monotonicity check: verify `gap(r=0.25) > gap(r=0.50) > gap(r=0.75)` per category

### FR-6: Mechanism Verification

- Verify H2O budget correctly set: `all(layer.self_attn.kv_budget_ratio == r for layer in model.model.layers)`
- Verify gap variance non-zero across r-values: `np.std([mean_gap_25, mean_gap_50, mean_gap_75]) > 1e-6`
- Log activation indicator: `"H2O eviction active: budget_ratio={r}"` per run
- Fail fast if budget not applied (budget_ratio mismatch detected after `set_h2o_budget()`)

### FR-7: Visualization

| Figure | Type | Required |
|--------|------|----------|
| Accuracy gap vs. budget ratio (line plot) | x=r, y=mean gap, lines per model | MANDATORY (gate metric visual) |
| Spearman ρ per model vs. -0.8 threshold | Bar chart with reference line | MANDATORY |
| Per-category gap heatmap | 6-category × 3-r heatmap, color=gap | Required |
| Absolute accuracy curves | Per-model line plot, both adapters at each r | Required |

- Save all figures to `h-m2/figures/`

### FR-8: Smoke Test

- Load one adapter on short input (~512 tokens)
- Sweep r ∈ {0.25, 0.50, 0.75}: verify `set_h2o_budget()` changes model attribute
- Verify per-category aggregation returns 6 non-NaN values
- Run before full 12-run evaluation

---

## 4. Data Specification

| Dataset | Source | Split | Samples | Download |
|---------|--------|-------|---------|----------|
| LongBench | `THUDM/LongBench` (HuggingFace Hub) | test (per task) | Full test set, all 21 tasks | Auto (HuggingFace datasets) |
| LongAlpaca-12k | `Yukang/LongAlpaca-12k` | N/A | Not used — adapters pre-trained | N/A |

**Note:** LongBench is auto-downloaded via HuggingFace datasets — no manual download task needed.

**H-E1 Adapter Checkpoints:** Accessible at H-E1 output paths. If full LLaMA/Mistral checkpoints are GPT-2 proxies only (from H-E1 smoke test), create fallback loading with GPT-2 for CI validation; full models for production run.

---

## 5. Evaluation Metrics

### Primary (SHOULD_WORK Gate)

| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| Spearman ρ (r vs. mean accuracy gap) | scipy.stats.spearmanr([0.25,0.50,0.75], [gap_25, gap_50, gap_75]) | ρ < -0.8 on ≥1 model |

### Secondary

| Metric | Definition | Target |
|--------|-----------|--------|
| Mean accuracy gap at r=25% | Mean gap across 6 categories at tightest budget | Positive (eviction-aware > sequential) |
| Monotonicity fraction | Fraction of categories with gap(25%) > gap(50%) > gap(75%) | ≥ 4/6 categories |
| r=50% cross-check | Mean accuracy gap at r=50% | Expected ≥2% in ≥4/6 categories (H-M3 preview) |

---

## 6. Non-Functional Requirements

| Requirement | Value |
|-------------|-------|
| GPU Memory | Single GPU; batch_size=1 for long sequences |
| Precision | float16 (matches H-E1/H-M1) |
| Determinism | seed=1, fixed H2O policy (deterministic given attention scores) |
| Output format | CSV for per-run results, JSON for Spearman summary, PNG for figures |
| Code reuse | Extend h-m1/code/ evaluation infrastructure; import H2OEvictionAwareAttention from h-e1/code/model.py |
| attn_implementation | `eager` required (H-M1 lesson) |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
transformers>=4.35
peft>=0.6
datasets>=2.14
scipy>=1.10
numpy>=1.24
matplotlib>=3.7
pandas>=2.0
tqdm>=4.65
```

### 7.2 External Repositories (Reference)

- THUDM/LongBench: https://github.com/THUDM/LongBench (evaluation protocol)
- FMInference/H2O: https://github.com/FMInference/H2O (H2O budget_ratio parameterization)
- huggingface/peft: https://github.com/huggingface/peft (adapter loading)

### 7.3 H-E1 / H-M1 Dependencies (Code Reuse)

| Module | File | Purpose |
|--------|------|---------|
| H2OEvictionAwareAttention | h-e1/code/model.py | Eviction wrapper — reuse directly |
| set_h2o_budget / inject_h2o_wrappers | h-e1/code/model.py | Budget ratio injection |
| load_base_model | h-e1/code/model.py | Model + adapter loading |
| LongBench data pipeline | h-m1/code/dataset.py | Middle truncation, per-task loading |
| run_task_evaluation | h-m1/code/evaluate.py | Per-task scoring (F1/ROUGE/accuracy) |
| compute_category_accuracies | h-m1/code/evaluate.py | 6-category aggregation |

---

## 8. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| Primary Gate (SHOULD_WORK) | Spearman ρ < -0.8 on ≥1 model |
| Mechanism Activated | Budget ratio correctly set + non-zero gap variance across r-values |
| PoC Pass | Code completes all 12 evaluation runs without error |
| Failure (non-blocking) | ρ ≥ -0.8 on both models → document as scope limitation, continue to H-M3 |

---

## 9. Scope Boundaries

**In Scope:**
- LongBench accuracy evaluation at r ∈ {25%, 50%, 75%} for both adapter types
- Spearman correlation between budget ratio and mean accuracy gap
- Per-category gap heatmap and monotonicity analysis
- Visualization of dose-response relationship

**Out of Scope:**
- Re-training adapters (H-E1 checkpoints reused)
- Attention entropy / HH concentration analysis (that is H-M1)
- Statistical significance testing per category (that is H-M3)
- New H2O eviction implementation (reuse from H-E1)
- Budget ratios outside {25%, 50%, 75%}

---

*Generated by Phase 3 Workflow (knowledge-grounded synthesis — MCP unavailable, consistent with H-E1/H-M1 approach)*
*Source: h-m2/02c_experiment_brief.md*
*Next: 03_architecture.md (Architecture Agent)*
