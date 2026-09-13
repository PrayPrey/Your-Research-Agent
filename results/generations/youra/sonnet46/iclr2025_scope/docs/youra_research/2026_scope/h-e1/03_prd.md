# Product Requirements Document: H-E1
# Activation Sparsity Existence Check for LLaMA-3-8B

**Hypothesis ID:** H-E1
**Hypothesis Type:** EXISTENCE
**Gate Type:** MUST_WORK
**Date:** 2026-05-08
**Phase:** 3 (Implementation Planning)
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

H-E1 is the foundational existence check for the SparsityLoRA pipeline. It verifies that LLaMA-3-8B MLP activation sparsity varies significantly across layers (CV > 0.3) and that the inter-layer sparsity ranking is stable across calibration distributions (Kendall's tau ≥ 0.6). This is a **measurement-only experiment** — no training occurs. Success unlocks all downstream hypotheses (H-M1 through H-M4).

**Core claim:** Pre-training drives MLP layers toward differentiated sparse activation attractors (Lazy Neuron Phenomenon), producing measurable and stable layer-wise sparsity variation.

---

## 2. Problem Statement

Before allocating LoRA ranks by layer-wise MLP activation sparsity, we must verify that such sparsity:
1. Varies meaningfully across LLaMA-3-8B's 32 MLP layers (high CV)
2. Produces a stable ranking across different calibration datasets (high Kendall's tau)
3. Remains stable across input sequence lengths

Without this foundation, the SparsityLoRA rank-allocation strategy has no valid signal to work with. Failure of H-E1 requires a pivot to alternative signals (gradient norm, activation magnitude).

---

## 3. Functional Requirements

### FR-1: Model Loading and Setup

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load LLaMA-3-8B (`meta-llama/Meta-Llama-3-8B`) in float16, eval mode, device_map="auto" | P0 |
| FR-1.2 | Disable gradient computation for all inference (torch.no_grad()) | P0 |
| FR-1.3 | Verify model has 32 MLP layers with accessible `gate_proj` modules | P0 |
| FR-1.4 | Seed reproducibility: dataset shuffling seed=42 | P0 |

### FR-2: Dataset Loading and Preprocessing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Load Alpaca dataset (`tatsu-lab/alpaca`, train split, first 512 samples shuffled with seed=42) | P0 |
| FR-2.2 | Load WikiText-103 dataset (`wikitext`, `wikitext-103-raw-v1`, test split, first 512 chunks) | P0 |
| FR-2.3 | Tokenize Alpaca `text` field with LLaMA-3-8B tokenizer | P0 |
| FR-2.4 | Truncate/pad to **128 tokens** (short condition) and **512 tokens** (long condition) separately | P0 |
| FR-2.5 | Concatenate WikiText-103 tokens into 512-token contiguous chunks | P0 |
| FR-2.6 | Batch size: 8 samples per forward pass | P0 |

### FR-3: Sparsity Measurement

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Register forward hooks on `gate_proj` of all 32 `model.model.layers[i].mlp` layers | P0 |
| FR-3.2 | For each forward pass, record sparsity fraction: `(output.abs() < epsilon).float().mean()` | P0 |
| FR-3.3 | Sweep epsilon ∈ {0.001, 0.01, 0.05, 0.1} independently | P0 |
| FR-3.4 | Compute per-layer mean sparsity across all 512 calibration samples | P0 |
| FR-3.5 | Remove all hooks after measurement (no lingering side effects) | P0 |
| FR-3.6 | Output: `layer_sparsity` array of shape (32,) for each (dataset, epsilon, length) condition | P0 |

### FR-4: Metric Computation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Compute CV: `sparsity.std() / sparsity.mean()` across 32 layers (primary: epsilon=0.01) | P0 |
| FR-4.2 | Compute Kendall's tau_calibration: `scipy.stats.kendalltau(alpaca_sparsity, wikitext_sparsity)` (primary: epsilon=0.01, length=512) | P0 |
| FR-4.3 | Compute Kendall's tau_length: `kendalltau(alpaca_128token_sparsity, alpaca_512token_sparsity)` | P1 |
| FR-4.4 | Compute CV and tau for all epsilon values ∈ {0.001, 0.01, 0.05, 0.1} | P1 |
| FR-4.5 | Report p-values for all Kendall's tau calculations | P1 |

### FR-5: Mechanism Verification

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Verify hooks fired for all 32 layers: `len(layer_sparsity) == 32` | P0 |
| FR-5.2 | Verify non-zero sparsity: `layer_sparsity.mean() > 0.0` | P0 |
| FR-5.3 | Verify layer variation: `layer_sparsity.std() > 0.01` | P0 |
| FR-5.4 | Log per-layer sparsity values to stdout for debugging | P1 |

### FR-6: Results Output

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Save per-layer sparsity arrays to JSON/CSV for all conditions | P0 |
| FR-6.2 | Print results table: CV and tau for each epsilon value | P0 |
| FR-6.3 | Save results summary to `results.json` | P0 |

### FR-7: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | **Gate Metrics Bar Chart**: CV value vs. 0.3 threshold, tau value vs. 0.6 threshold (mandatory) | P0 |
| FR-7.2 | **Sparsity Profile Plot**: per-layer mean sparsity (Alpaca vs. WikiText-103 overlaid, 32 layers) | P0 |
| FR-7.3 | **Epsilon Sensitivity Heatmap/Table**: CV and tau for each epsilon ∈ {0.001, 0.01, 0.05, 0.1} | P1 |
| FR-7.4 | **Length Sensitivity Plot**: sparsity profiles for 128-token vs. 512-token inputs with tau annotation | P1 |
| FR-7.5 | **Rank Correlation Scatter**: Alpaca vs. WikiText-103 layer sparsity ranks with tau annotation | P1 |
| FR-7.6 | Save all figures to `h-e1/figures/` directory | P0 |

---

## 4. Data Specification

### 4.1 Primary Dataset: Alpaca

| Field | Value |
|-------|-------|
| Source | HuggingFace: `tatsu-lab/alpaca` |
| Split | train |
| Sample count | 512 (first 512 after shuffle with seed=42) |
| Text field | `text` (instruction + input + output formatted) |
| Tokenization | LLaMA-3-8B tokenizer |
| Lengths | 128 tokens (short) AND 512 tokens (long) |
| Batch size | 8 |
| License | CC-BY-NC-4.0 |
| Download | Auto via HuggingFace Datasets |

### 4.2 Stability Check Dataset: WikiText-103

| Field | Value |
|-------|-------|
| Source | HuggingFace: `wikitext`, config `wikitext-103-raw-v1` |
| Split | test |
| Sample count | 512 (first 512 contiguous 512-token chunks) |
| Processing | Concatenate all text, split into 512-token chunks |
| Batch size | 8 |
| Download | Auto via HuggingFace Datasets |

**Note:** Both datasets are auto-downloadable via HuggingFace — NO manual download task required.

---

## 5. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Single GPU operation with CUDA_VISIBLE_DEVICES set before execution |
| NFR-2 | Float16 precision for LLaMA-3-8B (memory efficiency: ~16GB VRAM) |
| NFR-3 | Estimated runtime: 30-60 minutes (inference only, no training) |
| NFR-4 | All results reproducible with seed=42 |
| NFR-5 | No model weights modification (read-only measurement) |
| NFR-6 | Hook cleanup on completion and on exception (try/finally) |
| NFR-7 | Code must fail explicitly if model architecture is not LLaMA-3-8B or equivalent SiLU-gated transformer |

---

## 6. Success Criteria

### Primary Gate Conditions (MUST_WORK)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **CV > 0.3** | epsilon=0.01, Alpaca 512-token | `sparsity.std() / sparsity.mean() > 0.3` |
| **tau_calibration ≥ 0.6** | epsilon=0.01, Alpaca vs. WikiText-103 | `kendalltau(alpaca, wikitext).statistic >= 0.6` |

### Secondary Success Conditions

| Criterion | Threshold |
|-----------|-----------|
| tau_length ≥ 0.6 | 128-token vs. 512-token Alpaca ranking |
| CV > 0.3 for ≥ 3 of 4 epsilon values | Epsilon robustness |
| All 32 hooks fire successfully | Mechanism verified |

### Failure Actions

| Failure | Condition | Action |
|---------|-----------|--------|
| CV ≤ 0.3 | Sparsity not discriminating | PIVOT: explore gradient norm or activation magnitude |
| tau < 0.6 | Ranking unstable | EXPLORE: use task-specific calibration (GLUE val sets) |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.40.0
datasets>=2.18.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0  # (optional, for heatmaps)
peft>=0.10.0     # (informational, for downstream hypotheses)
```

### 7.2 Model Access

- HuggingFace Hub access for `meta-llama/Meta-Llama-3-8B`
- Valid HuggingFace token with LLaMA-3-8B access grant
- Minimum 20GB VRAM (float16) or 40GB+ (float32)

### 7.3 External Reference Repositories

| Repository | URL | Usage |
|------------|-----|-------|
| TEAL | https://github.com/FasterDecoding/TEAL | Hook pattern, calibration methodology |
| SparseGPT | https://github.com/IST-DASLab/sparsegpt | Layer-by-layer Catcher pattern |
| Activation-sparsity-benchmarking | https://github.com/fszatkowski/activation-sparsity-benchmarking | SparsificationManager pattern |

---

## 8. Constraints and Assumptions

- **No training**: H-E1 is pure inference-mode measurement
- **Single model**: Only LLaMA-3-8B (no other model variants)
- **Fixed architecture target**: `gate_proj` output is the hook target
- **No external baselines**: This is a measurement study, not a comparative experiment
- **Epsilon = 0.01 is primary**: All other epsilon values are robustness checks

---

## 9. Out of Scope

- LoRA fine-tuning or rank allocation (H-M3, H-M4 scope)
- Cross-distribution stability with >2 datasets (H-M1 scope)
- Threshold sensitivity beyond 4 epsilon values (H-M2 scope)
- Model comparison across different LLM architectures

---

*Generated by Phase 3 - Implementation Planning (inline PRD from 02c_experiment_brief.md)*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
