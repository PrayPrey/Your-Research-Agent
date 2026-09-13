---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-25"
author: Anonymous
---

# Product Requirements Document: H-E1

## Executive Summary

H-E1 establishes the measurement infrastructure for the calibration research chain (H-E1 → H-M1 → H-M2 → H-M3). The experiment evaluates whether logit-based Expected Calibration Error (ECE) is computable for open-weight LLMs on adversarial NLP benchmarks (AdvGLUE, ANLI) and their clean counterparts (GLUE, MultiNLI). No training is performed; this is a pure inference and measurement feasibility study.

**Gate:** MUST_WORK — all 24 (model × task × split) cells must produce valid ECE values with ≥200 examples.

---

## Problem Statement

LLM calibration on clean benchmarks is well-studied (ECE ≈ 0.05–0.15; Kadavath 2022). Whether this calibration degrades on adversarial NLP splits (AdvGLUE, ANLI) is unmeasured. Before testing the magnitude or mechanism of degradation (H-M1 through H-M3), H-E1 must confirm that the measurement infrastructure — logit extraction via lm-evaluation-harness and 15-bin ECE computation — produces valid, non-degenerate results for all 4 target models and 3 task types across 2 splits (clean + adversarial).

---

## Functional Requirements

### FR-1: Dataset Loading

**FR-1.1 AdvGLUE Dataset Loading**
- Load AdvGLUE subtasks: `adv_qqp`, `adv_sst2`, `adv_mnli` from HuggingFace (`adv_glue`)
- Split: validation (only split available)
- Expected size: 800–1000 examples per subtask

**FR-1.2 ANLI Dataset Loading**
- Load ANLI rounds: `test_r1`, `test_r2`, `test_r3` from HuggingFace (`anli`)
- Expected size: ~1000 examples per round

**FR-1.3 GLUE Clean Baseline Loading**
- Load `glue/qqp` (validation), `glue/sst2` (validation)
- Subsample: 500 examples per split (random seed=1) for computational efficiency
- Clean counterpart to AdvGLUE QQP and SST-2

**FR-1.4 MultiNLI Clean Baseline Loading**
- Load `multi_nli` (`validation_matched`)
- Subsample: 500 examples (random seed=1)
- Clean counterpart to AdvGLUE MNLI and ANLI

**FR-1.5 Dataset Verification**
- Verify all 9 dataset splits load without error
- Assert minimum example counts after loading
- Save dataset manifest to `results/dataset_manifest.json`

### FR-2: Model Loading

**FR-2.1 Llama-2-7B-base Loading**
- HuggingFace ID: `meta-llama/Llama-2-7b-hf`
- Precision: bfloat16; device_map="auto"
- Record exact checkpoint hash in results metadata

**FR-2.2 Llama-2-7B-chat Loading**
- HuggingFace ID: `meta-llama/Llama-2-7b-chat-hf`
- Precision: bfloat16; device_map="auto"

**FR-2.3 Llama-2-13B-chat Loading**
- HuggingFace ID: `meta-llama/Llama-2-13b-chat-hf`
- Precision: bfloat16; 4-bit BitsAndBytes quantization if VRAM-constrained
- device_map="auto" (multi-GPU via accelerate if available)

**FR-2.4 Mistral-7B-instruct Loading**
- HuggingFace ID: `mistralai/Mistral-7B-Instruct-v0.1`
- Precision: bfloat16; device_map="auto"

**FR-2.5 Model Verification**
- Verify each model loads without OOM error
- Run forward pass on dummy input to confirm functionality
- Save model manifest (HF IDs + checkpoint hashes) to `results/model_manifest.json`

### FR-3: Logit Extraction

**FR-3.1 Multiple-Choice Logit Extraction**
- For each (context, answer_choices) pair, compute log-probability of each answer token
- Use `model.logits[0, -1, :]` for last-position logit; extract token_id for each choice letter (A/B/C/D)
- Apply softmax to convert log-probs to probabilities
- Return: `(probs, pred_label, confidence)` per example

**FR-3.2 Answer Token Tokenization**
- Tokenize answer choice labels (A, B, C, D) as single tokens
- Verify each answer choice maps to ≤2 tokens; warn if multi-token
- Use first token of multi-token choices as fallback

**FR-3.3 Prompt Formatting**
- Format MC prompts with letter labels: "A) {choice_A}\nB) {choice_B}\n..."
- Apply model-specific chat template for chat/instruct models (Llama-2-chat, Mistral-instruct)
- Use raw format for base models (Llama-2-7B-base)

**FR-3.4 Pre-validation Protocol (Risk R1 Mitigation)**
- Before full evaluation: run 10 examples per cell
- Assert: softmax probabilities sum to 1.0 ± 1e-4
- Flag cells where mean max confidence > 0.999 (degenerate — all-confident)
- Flag cells where mean max confidence < 0.40 (degenerate — near-uniform)
- Abort cell if pre-validation fails; log failure reason

### FR-4: ECE Computation

**FR-4.1 15-bin ECE (Primary)**
- Implement Guo 2017 equal-width ECE: `ECE = Σ_b |B_b|/n × |acc(B_b) - conf(B_b)|`
- n_bins=15, boundaries: `np.linspace(0, 1, 16)`
- Return ECE value per (model, task, split) cell

**FR-4.2 10-bin ECE (Sensitivity Check — Risk R5 Mitigation)**
- Same formula with n_bins=10
- Compute alongside primary metric; include in output CSV

**FR-4.3 Cell Validation (`verify_logit_extraction`)**
- For each cell, check:
  - `coverage_met`: `len(confidences) >= 200`
  - `non_degenerate`: `(confidences < 0.999).mean() > 0.90`
  - `non_uniform`: `confidences.mean() > 0.40`
  - `ece_plausible`: `0.0 <= ece_15 <= 0.5`
  - `probs_sum_to_one`: `abs(prob_sums.mean() - 1.0) < 1e-3`
- Return `(passed: bool, indicators: dict)` per cell

**FR-4.4 Clean-Split Sanity Check**
- After all clean-split evaluations, check: ECE ∈ [0.05, 0.15] for ≥2/4 models
- If all 4 models have clean ECE > 0.30, flag systematic deviation from Kadavath 2022 baseline
- Log sanity check result to `results/sanity_check.json`

### FR-5: Results Storage

**FR-5.1 Per-Cell Results CSV**
- Save `results/ece_results.csv` with columns: `model, task, split, n_examples, ece_15, ece_10, accuracy, mean_confidence, cell_passed`
- 24 rows (4 models × 3 tasks × 2 splits)

**FR-5.2 Per-Example Results (Optional)**
- Save `results/{model}_{task}_{split}_examples.jsonl` with per-example: `{confidence, pred_label, true_label, correct}`
- Required for reliability diagram generation

**FR-5.3 Gate Evaluation**
- Compute gate result: count cells where `cell_passed=True`
- Gate PASSES if: `passed_cells >= 20` AND `clean_sanity_passed`
- Save `results/gate_result.json`: `{passed: bool, passed_cells: int, failed_cells: list, gate_condition: str}`

### FR-6: Visualization

**FR-6.1 ECE Comparison Bar Chart (Required)**
- 2×2 subplot grid: 4 models × 3 tasks
- Each subplot: grouped bars for clean vs adversarial ECE
- Save to `docs/youra_research/h-e1/figures/fig1_ece_comparison.png`

**FR-6.2 Calibration Reliability Diagrams**
- 12 panels (4 models × 3 tasks), each with clean and adversarial overlaid
- Save to `docs/youra_research/h-e1/figures/fig2_reliability_diagrams.png`

**FR-6.3 Cell Coverage Heatmap**
- 4×6 grid (4 models × 6 dataset splits) showing example count per cell
- Save to `docs/youra_research/h-e1/figures/fig3_coverage_heatmap.png`

**FR-6.4 Confidence Distribution Boxplots**
- Per cell, max-softmax confidence distribution boxplots
- Save to `docs/youra_research/h-e1/figures/fig4_confidence_distribution.png`

**FR-6.5 ECE Sensitivity Scatter (10-bin vs 15-bin)**
- Scatter plot of ECE_10 vs ECE_15 across all 24 cells
- Save to `docs/youra_research/h-e1/figures/fig5_ece_sensitivity.png`

---

## Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed random seed = 1 for all subsampling operations
- Record exact HuggingFace checkpoint hashes in results metadata
- All results reproducible from seed + model IDs + dataset HF identifiers

**NFR-2: Compute Efficiency**
- Use `torch.no_grad()` for all inference
- Process examples in batches where possible (batch_size configurable, default=8)
- Total compute target: ≤20 A100-hours (4 models × ~4h each for 7B; ≤8h for 13B)

**NFR-3: Graceful Failure**
- Cell failures logged and skipped (not crashing the pipeline)
- Gate evaluation proceeds on available cells; flags missing cells
- Detailed error logging to `results/errors.log`

**NFR-4: GPU Memory**
- Unload each model before loading next (del model; torch.cuda.empty_cache())
- 4-bit quantization fallback for 13B model if VRAM < 40GB
- Assert VRAM availability before model loading

---

## Data Specification (Section 4)

### 4.1 Datasets

| Dataset | HF Identifier | Split | Size | Download Method |
|---------|--------------|-------|------|-----------------|
| AdvGLUE QQP | `adv_glue/adv_qqp` | validation | ~1000 | HF auto |
| AdvGLUE SST-2 | `adv_glue/adv_sst2` | validation | ~1000 | HF auto |
| AdvGLUE MNLI | `adv_glue/adv_mnli` | validation | ~1000 | HF auto |
| ANLI R1 | `anli` / `test_r1` | test_r1 | ~1000 | HF auto |
| ANLI R2 | `anli` / `test_r2` | test_r2 | ~1000 | HF auto |
| ANLI R3 | `anli` / `test_r3` | test_r3 | ~1000 | HF auto |
| GLUE QQP | `glue/qqp` | validation | 40k (→500) | HF auto |
| GLUE SST-2 | `glue/sst2` | validation | 872 (→500) | HF auto |
| MultiNLI | `multi_nli` | validation_matched | 9815 (→500) | HF auto |

**All datasets auto-download via HuggingFace `datasets` library — no manual download required.**

### 4.2 Evaluation Matrix

| Task | Clean Split | Adversarial Split | Task Type |
|------|-------------|-------------------|-----------|
| QQP (Paraphrase) | GLUE QQP | AdvGLUE QQP | Binary classification |
| SST-2 (Sentiment) | GLUE SST-2 | AdvGLUE SST-2 | Binary classification |
| NLI | MultiNLI | AdvGLUE MNLI + ANLI R1/R2/R3 | 3-way classification |

**Total cells:** 4 models × 3 task types × 2 splits = 24 evaluation cells

---

## Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Cell coverage | ≥200 valid examples per cell | MUST |
| ECE valid range | ECE ∈ [0.0, 0.5] for all 24 cells | MUST |
| Non-degenerate logits | `verify_logit_extraction()` passes ≥20/24 cells | MUST |
| Clean ECE sanity | ECE ∈ [0.05, 0.15] for ≥2/4 models on clean splits | MUST |
| All 5 figures generated | All required visualizations saved to figures/ | SHOULD |
| Per-example results | JSONL files for reliability diagram generation | SHOULD |

**Gate PASSES:** `passed_cells >= 20` AND `clean_sanity_passed`
**Gate FAILS → STOP:** Reassess measurement protocol; pivot to 2 models or BBH-MC only

---

## Dependencies (Section 7)

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
accelerate>=0.24.0
bitsandbytes>=0.41.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
tqdm>=4.65.0
jsonlines>=3.1.0
pyyaml>=6.0
```

### 7.2 External Repositories (Reference)

- EleutherAI/lm-evaluation-harness: Reference for logit extraction API pattern (not installed as dependency — we implement the logit extraction layer directly using `transformers`)
- HuggingFace model hub: `meta-llama/Llama-2-7b-hf`, `meta-llama/Llama-2-7b-chat-hf`, `meta-llama/Llama-2-13b-chat-hf`, `mistralai/Mistral-7B-Instruct-v0.1`

### 7.3 Hardware Requirements

- GPU: ≥1× NVIDIA A100-40GB (or equivalent ≥40GB VRAM for 13B model)
- For 13B with 4-bit quantization: ≥24GB VRAM
- Disk: ≥100GB for model weights (4 models)
- RAM: ≥32GB system RAM

---

## Out of Scope

- Model fine-tuning or training of any kind
- New model architectures
- ΔECE statistical testing (H-M1 through H-M3)
- Calibration improvement methods (H-M2, H-M3)
- Encoder-only models (BERT, RoBERTa) — incompatible architecture
- Closed-weight APIs (GPT-4, Claude) — no logit access
