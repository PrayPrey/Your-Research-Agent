# Product Requirements Document: H-M1
# Attention Pattern Mechanistic Analysis for Eviction-Aware LoRA

**Hypothesis:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Date:** 2026-05-04
**Phase:** 3 — Implementation Planning
**Gate:** MUST_WORK (paired t-test p < 0.05 on attention entropy in ≥50% layers on ≥1 model)

---

## 1. Executive Summary

H-M1 investigates whether eviction-aware LoRA adapters (trained with H2O hard-mask injection) develop qualitatively different attention patterns compared to sequential baseline adapters evaluated under the same H2O eviction regime. This mechanistic analysis extends H-E1 (which confirmed adapter weight divergence) by measuring per-layer attention entropy and heavy-hitter concentration during LongBench inference.

**No new training.** H-E1 adapter checkpoints are reused. This experiment adds an attention extraction analysis layer on top of existing infrastructure.

---

## 2. Problem Statement

H-E1 confirmed that eviction-aware LoRA training produces significantly different adapter weight matrices (cosine similarity < 0.95, mean ≈ 0.053 — near-orthogonal). The mechanistic question is: *why* do these different weights matter? The token-scarcity regularization hypothesis predicts that adapters trained under eviction learn attention patterns more calibrated to the evicted-cache distribution — measurable as systematic differences in per-layer attention entropy and heavy-hitter concentration.

---

## 3. Functional Requirements

### FR-1: Adapter Loading (Base H-E1 Checkpoints)

**Reuse H-E1 trained adapters — no re-training.**

| Adapter | Base Model | Checkpoint Path |
|---------|-----------|-----------------|
| Eviction-Aware | LLaMA-2-7B | h-e1/code/outputs/h-e1/gpt2-eviction-aware/ (smoke test); full LLaMA-2-7B from H-E1 run |
| Sequential Baseline | LLaMA-2-7B | h-e1/code/outputs/h-e1/gpt2-baseline/ (smoke test); full from H-E1 run |
| Eviction-Aware | Mistral-7B-v0.1 | H-E1 Mistral eviction-aware checkpoint |
| Sequential Baseline | Mistral-7B-v0.1 | H-E1 Mistral baseline checkpoint |

- Load with `AutoModelForCausalLM.from_pretrained` + `PeftModel.from_pretrained`
- Inference precision: float16 (same as H-E1)
- Apply H2O eviction at r=0.5 at inference for both conditions

### FR-2: LongBench Dataset Loading

- **Source:** `load_dataset("THUDM/LongBench", task_name, split="test")`
- **Tasks:** All 21 tasks across 6 categories
- **Sample target:** ≥500 samples per category (aggregate across tasks within category)
- **Tasks with <500 samples:** Use full test set
- **Batch size:** 1 (required — long sequences + output_attentions=True)
- **Max sequence length:** 4096 tokens
- **Truncation:** Middle truncation — keep first 1000 + last 3000 tokens (LongBench standard)

### FR-3: Attention Extraction Module (AttentionAnalysisExtractor)

- Call `model(input_ids, attention_mask, output_attentions=True)`
- Returns tuple of tensors: `(B, H, S, S)` per layer, len = num_hidden_layers
- Compute per-layer:
  1. **Attention Entropy:** `H = -Σ p_i * log(p_i + eps)` over key dim, averaged over heads and query positions → scalar per layer
  2. **Heavy-Hitter Concentration:** ratio of top-20% key tokens' attention mass → scalar per layer
- Apply H2O eviction identically for both adapter conditions during inference

### FR-4: Statistical Analysis

- Collect per-layer entropy values across all samples (N ≥ 500 per category)
- Run **paired t-test** (`scipy.stats.ttest_rel`) per layer between eviction-aware and baseline
- Report: `p_value` per layer, `fraction_significant` = (#layers with p < 0.05) / total_layers
- Repeat for heavy-hitter concentration ratio

### FR-5: Visualization

| Figure | Type | Required |
|--------|------|----------|
| Gate metric: % layers with p < 0.05 | Bar chart | MANDATORY |
| Per-layer entropy comparison | Line plot with SE | Required |
| Per-layer HH concentration | Line plot | Required |
| p-value heatmap (-log10) | Heatmap | Required |
| Entropy by task category | Box plot | Required |

- Save all figures to `h-m1/figures/`

### FR-6: Smoke Test

- Short input (~512 tokens), verify `output_attentions=True` returns correct shapes
- Verify entropy values are non-NaN and row-sums of attention matrices ≈ 1
- Run before full experiment

---

## 4. Data Specification

| Dataset | Source | Split | Samples | Download |
|---------|--------|-------|---------|----------|
| LongBench | `THUDM/LongBench` (HuggingFace Hub) | test | Full (200–500/task, ≥500/category) | Auto (HuggingFace datasets) |
| LongAlpaca-12k | `Yukang/LongAlpaca-12k` | train | N/A — H-E1 already trained | Auto (training already done) |

**Note:** LongBench is auto-downloaded via HuggingFace datasets — **no manual download task needed.**

**H-E1 Adapter Checkpoints:** Must be accessible at H-E1 output paths. If full LLaMA/Mistral checkpoints were not saved (H-E1 used GPT-2 smoke test only), create placeholder loading logic with appropriate fallback.

---

## 5. Evaluation Metrics

### Primary (MUST_WORK Gate)

| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| Fraction of layers with p < 0.05 (attention entropy) | (#significant layers) / num_hidden_layers | ≥ 0.50 on ≥ 1 model |

### Secondary

| Metric | Definition | Target |
|--------|-----------|--------|
| Mean entropy difference | Mean(|eviction_aware_entropy - baseline_entropy|) across layers | > 0.1 nats |
| HH concentration difference | Mean(|eviction_aware_conc - baseline_conc|) across layers | > 0.05 |

---

## 6. Non-Functional Requirements

| Requirement | Value |
|-------------|-------|
| GPU Memory | Single GPU; batch_size=1 required for long sequences |
| Precision | float16 (matches H-E1) |
| Determinism | seed=1, fixed H2O eviction masks |
| Output format | CSV for per-layer metrics, JSON for summary, PNG for figures |
| Code reuse | Extend h-e1/code/model.py — do NOT copy/reimplement H2OEvictionAwareAttention |

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

- THUDM/LongBench: https://github.com/THUDM/LongBench (evaluation protocol reference)
- FMInference/H2O: https://github.com/FMInference/H2O (H2O eviction implementation reference)

### 7.3 H-E1 Dependencies (Code Reuse)

| Module | File | Purpose |
|--------|------|---------|
| H2OEvictionAwareAttention | h-e1/code/model.py | Eviction wrapper — reuse directly |
| inject_h2o_wrappers | h-e1/code/model.py | Inject H2O at inference |
| load_base_model | h-e1/code/model.py | Model loading |
| LoRAConfig, TrainingConfig | h-e1/code/config.py | Config dataclasses |

---

## 8. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| Primary Gate (MUST_WORK) | Paired t-test p < 0.05 on attention entropy in ≥50% of transformer layers on ≥1 model |
| Secondary | HH concentration differs by ≥5% mean across layers (directional) |
| PoC Pass | Code runs without error; gate condition met |
| Failure | p ≥ 0.05 in <50% layers on both models → PIVOT (examine deeper layers, task-specific) |

---

## 9. Scope Boundaries

**In Scope:**
- Attention entropy and HH concentration extraction during LongBench inference
- Statistical comparison (paired t-test) between eviction-aware and sequential baseline
- Visualization of per-layer attention differences

**Out of Scope:**
- Re-training adapters (H-E1 checkpoints reused)
- LongBench task-level accuracy evaluation (that is H-M3)
- Ablation over KV budget ratios (that is H-M2)
- New H2O eviction implementation (reuse from H-E1)

---

*Generated by Phase 3 Workflow (knowledge-grounded synthesis — MCP unavailable, consistent with H-E1 approach)*
*Source: h-m1/02c_experiment_brief.md*
*Next: 03_architecture.md (Architecture Agent)*
