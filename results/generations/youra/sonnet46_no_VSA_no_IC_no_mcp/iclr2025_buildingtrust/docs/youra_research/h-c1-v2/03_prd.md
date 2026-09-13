# Product Requirements Document: h-c1-v2
# RLHF Calibration Moderation — Task-Type-Conditional ΔΔECE Analysis

**Hypothesis ID:** h-c1-v2
**Hypothesis Type:** CONDITION (INCREMENTAL — extends h-e1, h-m1, h-c1)
**Date:** 2026-08-25
**Phase:** 3 — Implementation Planning
**stepsCompleted:** [prd]

---

## 1. Executive Summary

This experiment validates that RLHF alignment (Llama-2-7B-chat vs. Llama-2-7B-base) moderates ECE degradation under adversarial perturbation **conditionally on benchmark type**: moderation is expected on model-in-the-loop adversarial benchmarks (ANLI R1/R2/R3) but may reverse on static human-crafted adversarial benchmarks (AdvGLUE MNLI). The hypothesis refines h-c1 (which FAILED by averaging across benchmark types), separating ANLI moderation (3/3 rounds confirmed in h-c1) from AdvGLUE reversal (documented as boundary condition). The primary contribution is: (1) formal benchmark-type × RLHF interaction analysis, (2) cross-size validation with Llama-2-13B-chat on ANLI, and (3) calibration reliability diagrams for all conditions. All 7B ECE values are pre-computed from h-c1; only 13B-chat requires new inference.

**Gate Type:** SHOULD_WORK
**Success Criterion:** ΔΔECE > 0.01 for ≥60% of ANLI cells (Llama-2-7B-chat vs. base)

---

## 2. Problem Statement

### 2.1 Research Question

Does RLHF alignment moderate calibration degradation under adversarial perturbation, and is this moderation conditional on the adversarial benchmark construction method (model-in-the-loop vs. static human-crafted)?

### 2.2 Context from Prior Hypotheses

| Hypothesis | Finding | Status |
|-----------|---------|--------|
| h-e1 | ECE_adv > ECE_clean for NLI × Llama-2-7B | PASS |
| h-m1 | Confidence-accuracy decoupling drives ΔECE; label-preservation ≥80% confirmed | PASS |
| h-c1 | ΔΔECE_NLI (aggregate) = -0.0256 → gate FAILED; ANLI 3/4 cells moderated | FAILED |
| h-c1-v2 | Separates ANLI (moderation) from AdvGLUE (reversal boundary) | IN_PROGRESS |

### 2.3 Pre-computed Results from h-c1

| Cell | ΔECE_base | ΔECE_chat | ΔΔECE | Moderation? |
|------|-----------|-----------|-------|-------------|
| NLI-ANLI-R1 | -0.0165 | -0.1314 | **+0.1149** | True |
| NLI-ANLI-R2 | +0.0017 | -0.1458 | **+0.1474** | True |
| NLI-ANLI-R3 | -0.0112 | -0.0537 | **+0.0425** | True |
| NLI-AdvGLUE | +0.0648 | +0.0904 | **-0.0256** | False (reversal) |

**V2 interpretation:** 3/3 ANLI cells show ΔΔECE > 0.01. AdvGLUE reversal is benchmark-type-specific boundary condition (Minderer et al. calibration-shift amplification).

---

## 3. Functional Requirements

### FR-1: Data Loading and Preprocessing

**FR-1.1: ANLI Dataset Loading**
- Load ANLI test splits: `test_r1`, `test_r2`, `test_r3` from `allenai/anli`
- Coverage: ≥200 examples per split (confirmed h-e1)
- Labels: {0: entailment, 1: neutral, 2: contradiction}
- Auto-download via HuggingFace datasets

**FR-1.2: AdvGLUE MNLI Loading**
- Load AdvGLUE adversarial MNLI: `adv_glue` → `adv_mnli` → `validation` split
- Load clean counterpart: `glue` → `mnli` → `validation_matched`
- Load MultiNLI: `multi_nli` → `validation_matched`
- Auto-download via HuggingFace datasets

**FR-1.3: Label-Preservation Filter (from h-m1)**
- Apply h-m1 label-preservation mask (≥80% confirmed) to AdvGLUE examples
- High-preservation mask (≥0.9) used for boundary characterization
- Reuse h-m1 filter logic; no new computation

**FR-1.4: H-C1 Cache Loading**
- Load pre-computed logit caches from h-c1 results:
  - `h-c1/results/llama2_7b_base_anli_r1.json` (and r2, r3, adv_glue)
  - `h-c1/results/llama2_7b_chat_anli_r1.json` (and r2, r3, adv_glue)
- Validate cache structure: must contain `logits`, `labels`, `split_id`

### FR-2: Model Evaluation (New Inference — 13B-chat only)

**FR-2.1: Llama-2-13B-chat Evaluation**
- Model: `meta-llama/Llama-2-13b-chat-hf`
- Tasks: ANLI R1, R2, R3 + AdvGLUE MNLI (4 evaluation runs)
- Tool: lm-evaluation-harness with `--log_samples` flag
- Output: JSON logit files per task to `results/h-c1-v2/13b_chat/`
- Compute estimate: ~2 hours on A100 (30 min/run × 4 runs)
- Seed: 1 (fixed, matches h-e1)

**FR-2.2: lm-evaluation-harness Integration**
- Use EleutherAI/lm-evaluation-harness (already installed from h-e1)
- Command:
  ```bash
  python main.py --model hf \
    --model_args pretrained=meta-llama/Llama-2-13b-chat-hf \
    --tasks anli_r1,anli_r2,anli_r3,adv_glue_mnli \
    --log_samples --output_path results/h-c1-v2/13b_chat/
  ```
- Extract answer token logits: 3-class NLI (entailment/neutral/contradiction)

### FR-3: ECE Computation

**FR-3.1: 15-bin Equal-Width ECE**
- Protocol identical to h-e1 (validated, reuse `compute_ece()`)
- Input: confidences `(N,)` = max softmax prob, accuracies `(N,)` = 0/1 correct
- Output: scalar ECE ∈ [0, 1]

**FR-3.2: ΔECE Computation**
- ΔECE = ECE(adversarial) − ECE(clean)
- Computed for all (model, benchmark_type, round) combinations
- Clean counterparts: MultiNLI for ANLI, GLUE MNLI for AdvGLUE

**FR-3.3: ΔΔECE Moderation Metric**
- ΔΔECE = ΔECE(base) − ΔECE(chat)
- Positive = moderation (chat shows less calibration degradation)
- Threshold: ΔΔECE > 0.01 = moderation confirmed (from h-c1 gate criterion)
- Computed per cell: (model_pair, benchmark_type, round)

### FR-4: Task-Type-Conditional Moderation Analysis

**FR-4.1: ANLI Moderation Analysis**
- Compute ΔΔECE for 3 ANLI rounds × 2 model pairs (7B-base vs 7B-chat, 7B-base vs 13B-chat)
- Report moderation rate per model pair: fraction of rounds with ΔΔECE > 0.01
- Gate: ≥60% moderation rate on 7B pair (primary)

**FR-4.2: AdvGLUE Boundary Characterization**
- Compute ΔΔECE for AdvGLUE MNLI (expected reversal: ΔΔECE < 0)
- Document as boundary condition, not gate failure
- Apply label-preservation filter (h-m1) to validate reversal on clean-label examples

**FR-4.3: Benchmark-Type Interaction**
- Separate moderation statistics by benchmark_type ∈ {ANLI, AdvGLUE}
- Test: Moderation_rate(ANLI) > Moderation_rate(AdvGLUE) (expected)
- Document Perez (2022) explanation: RLHF models better calibrated to model-in-the-loop adversarial construction

**FR-4.4: Cross-Size Validation (13B-chat)**
- Compute ΔΔECE for 13B-chat vs 7B-base on ANLI rounds
- Secondary gate: ≥60% moderation rate (smaller dataset, corroborating evidence)

### FR-5: Visualization

**FR-5.1: ΔΔECE Comparison Bar Chart (MANDATORY)**
- Per-cell ΔΔECE for all cells: ANLI-R1, ANLI-R2, ANLI-R3, AdvGLUE-MNLI
- Color-coded: green = ΔΔECE > 0.01 (moderation), red = ΔΔECE < 0 (reversal), gray = |ΔΔECE| ≤ 0.01
- Separate panels per model pair (7B-base vs 7B-chat, 7B-base vs 13B-chat)
- Save to: `figures/ddece_comparison_bar.png`

**FR-5.2: Calibration Reliability Diagrams**
- Side-by-side: base vs. chat on ANLI-R3 (peak moderation) and AdvGLUE MNLI (reversal)
- 15-bin, x=confidence, y=accuracy, diagonal=perfect calibration
- Save to: `figures/reliability_diagram_{split}.png`

**FR-5.3: Confidence Distribution Histogram**
- base vs. chat on adversarial ANLI misclassifications
- Shows RLHF logit distribution shift toward lower max confidence
- Save to: `figures/confidence_distribution_adv.png`

**FR-5.4: Benchmark-Type Moderation Heatmap**
- Rows = model (7B-base, 7B-chat, 13B-chat), columns = (ANLI-R1, ANLI-R2, ANLI-R3, AdvGLUE)
- Values = ΔECE per cell; color scale: red (high degradation) to green (low/negative ΔECE)
- Save to: `figures/moderation_heatmap.png`

**FR-5.5: ΔΔECE vs. Adversarial Difficulty Scatter**
- x = ANLI round difficulty (R1=1, R2=2, R3=3), y = ΔΔECE
- Tests if moderation strength scales with adversarial difficulty
- Save to: `figures/ddece_vs_difficulty.png`

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | HuggingFace ID | Split | Source |
|---------|---------------|-------|--------|
| ANLI R1 | `allenai/anli` | `test_r1` | Auto-download |
| ANLI R2 | `allenai/anli` | `test_r2` | Auto-download |
| ANLI R3 | `allenai/anli` | `test_r3` | Auto-download |
| AdvGLUE MNLI | `adv_glue` → `adv_mnli` | `validation` | Auto-download |
| GLUE MNLI (clean) | `glue` → `mnli` | `validation_matched` | Auto-download |
| MultiNLI (clean) | `multi_nli` | `validation_matched` | Auto-download |

### 4.2 Pre-computed Cache (from h-c1)

| Cache File | Contents | Reuse |
|-----------|----------|-------|
| `h-c1/results/llama2_7b_base_anli_*.json` | Logits + labels for base model on ANLI R1/R2/R3 | Full reuse |
| `h-c1/results/llama2_7b_chat_anli_*.json` | Logits + labels for chat model on ANLI R1/R2/R3 | Full reuse |
| `h-c1/results/llama2_7b_*_adv_glue.json` | Logits + labels for both models on AdvGLUE | Full reuse |
| `h-m1/results/label_preservation_mask.npy` | Label-preservation filter for AdvGLUE | Full reuse |

### 4.3 New Data (13B-chat only)

| Data | Generation | Output Path |
|------|-----------|-------------|
| 13B-chat ANLI R1/R2/R3 logits | lm-eval-harness run | `results/h-c1-v2/13b_chat/` |
| 13B-chat AdvGLUE MNLI logits | lm-eval-harness run | `results/h-c1-v2/13b_chat/` |

---

## 5. Evaluation Metrics

| Metric | Formula | Threshold | Type |
|--------|---------|-----------|------|
| ECE | 15-bin equal-width | — | primary |
| ΔECE | ECE(adv) − ECE(clean) | — | primary |
| ΔΔECE | ΔECE(base) − ΔECE(chat) | > 0.01 = moderation | primary |
| Moderation rate (ANLI) | fraction(ΔΔECE > 0.01) / 3 ANLI rounds | ≥ 0.60 | gate |
| Moderation rate (13B) | fraction(ΔΔECE > 0.01) / 3 ANLI rounds | ≥ 0.60 | secondary |
| AdvGLUE reversal | ΔΔECE < 0 documented | — | boundary |

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Seed fixed at 1 for all new runs (matches h-e1)
- Cache loading deterministic (hash-checked)
- All results stored as JSON with logit arrays for reproducibility

### NFR-2: Performance
- 7B model evaluation: cached (0 new inference)
- 13B-chat: ~2 hours on single A100 (4 runs × ~30 min)
- ECE computation: <1 min (vectorized numpy)

### NFR-3: Compatibility
- lm-evaluation-harness version: same as h-e1 (pinned)
- HuggingFace transformers: same as h-e1
- Python 3.10+, PyTorch 2.0+

### NFR-4: Output Format
- All ECE values: float64 (4 decimal places in reports)
- Results saved to: `docs/youra_research/h-c1-v2/results/`
- Figures saved to: `docs/youra_research/h-c1-v2/figures/`
- All figures: PNG, 300 DPI, 12pt font

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `transformers` | ≥4.35 | Model loading |
| `datasets` | ≥2.14 | Dataset loading |
| `torch` | ≥2.0 | Inference |
| `numpy` | ≥1.24 | ECE computation |
| `matplotlib` | ≥3.7 | Visualization |
| `seaborn` | ≥0.12 | Heatmap |
| `torchmetrics` | ≥1.0 | ECE cross-check |
| `scipy` | ≥1.10 | Statistical tests |
| `pyyaml` | ≥6.0 | Config/results |

### 7.2 External Repositories

| Repository | URL | Purpose |
|-----------|-----|---------|
| lm-evaluation-harness | EleutherAI/lm-evaluation-harness | 13B-chat evaluation |
| facebookresearch/llama | facebookresearch/llama | Architecture reference |

### 7.3 Model Checkpoints

| Model | HuggingFace ID | Status |
|-------|---------------|--------|
| Llama-2-7B-base | `meta-llama/Llama-2-7b-hf` | Cached (h-e1) |
| Llama-2-7B-chat | `meta-llama/Llama-2-7b-chat-hf` | Cached (h-c1) |
| Llama-2-13B-chat | `meta-llama/Llama-2-13b-chat-hf` | **Download required** |

---

## 8. Success Criteria

### Primary Gate (SHOULD_WORK)

| Criterion | Threshold | Expected Value |
|-----------|-----------|----------------|
| ANLI moderation rate (7B pair) | ≥ 60% | 100% (3/3 rounds) from h-c1 |
| ΔΔECE(ANLI-R1) | > 0.01 | +0.1149 |
| ΔΔECE(ANLI-R2) | > 0.01 | +0.1474 |
| ΔΔECE(ANLI-R3) | > 0.01 | +0.0425 |

### Secondary Gate

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| 13B-chat moderation rate (ANLI) | ≥ 60% | Cross-size validation |
| AdvGLUE reversal documented | ΔΔECE < 0 | Boundary condition, not failure |

### Failure Mode

If SHOULD_WORK fails: document as EXPLORE finding. Investigate whether alignment affects logit scale independently of calibration. Characterize AdvGLUE reversal as task-specific boundary. Report as contextual finding on RLHF calibration moderation limits.

---

*PRD generated for Phase 3 implementation planning of h-c1-v2*
*Based on: 02c_experiment_brief.md + h-c1 validated results*
*Extends: h-e1 (ECE infrastructure), h-m1 (label-preservation filter), h-c1 (ECE cache)*
