# Product Requirements Document: H-M1
# Base Calibration Verification — Pythia Pretrained Models ECE Measurement

---

**Frontmatter:**
```yaml
hypothesis_id: h-m1
hypothesis_type: MECHANISM
tier: FULL
phase: Phase 3
generated_at: 2026-03-15
based_on: h-m1/02c_experiment_brief.md
prerequisites_satisfied: h-e1 (MUST_WORK PASS)
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Goals and Non-Goals
  - Functional Requirements
  - Data Specification
  - Evaluation Metrics
  - Non-Functional Requirements
  - Dependencies
  - Success Criteria
```

---

## 1. Executive Summary

H-M1 is a **causal baseline verification** experiment that confirms Pythia pretrained base models exhibit low Expected Calibration Error (ECE < 0.15) before any alignment training. This is the mechanistic foundation for the broader RLHF alignment vs. calibration trade-off pipeline: if base models are already miscalibrated, the causal interpretation of H-E1's alignment-induced calibration degradation would be invalid.

**Primary Implementation Path (PREFERRED — Zero Compute):** Read ECE_base values directly from `h-e1/04_validation.md`, which already computed base model calibration during H-E1 Phase 4.

**Fallback Path:** Re-run lm-eval v0.4.11 on 3 Pythia base models only (vs. 12 models in H-E1), computing ECE from log-probability outputs.

**Gate:** MUST_WORK — ECE_base < 0.15 for ALL 3 Pythia base model sizes (1.4B, 2.8B, 6.9B).

---

## 2. Problem Statement

### Background

H-E1 demonstrated that alignment training (SFT, DPO, PPO) increases Brier reliability (overconfidence) in Pythia LLMs. H-M1 establishes the **causal baseline**: that pretraining alone yields well-calibrated logit distributions, making alignment the necessary and sufficient cause of observed calibration degradation.

### Research Question

Do Pythia pretrained base models (1.4B, 2.8B, 6.9B) satisfy ECE < 0.15 under greedy-decoded log-probability evaluation on MMLU?

### Causal Importance

Without confirmed base calibration (ECE_base < 0.15), the alignment-calibration degradation observed in H-E1 could be attributed to pre-existing miscalibration rather than alignment training. H-M1 eliminates this alternative explanation.

---

## 3. Goals and Non-Goals

### Goals

1. **Verify ECE_base < 0.15** for all 3 Pythia base model sizes on MMLU (15-bin ECE)
2. **Extract base model ECE values** from H-E1 outputs (primary) or recompute via lm-eval (fallback)
3. **Confirm calibration ordering**: ECE_base < ECE_SFT < ECE_DPO ≤ ECE_PPO (secondary, informative)
4. **Generate 4 required figures** including gate metrics bar chart
5. **Produce 04_validation.md** report with PASS/FAIL gate result

### Non-Goals

- Evaluating aligned models (H-M1 is base-only)
- Training any models
- Collecting new datasets
- Modifying lm-eval harness
- Comparing to non-Pythia models

---

## 4. Functional Requirements

### FR-1: Data Extraction from H-E1 (Primary Path)

**Priority:** MUST HAVE
**Source:** h-m1/02c_experiment_brief.md §Dataset

The system SHALL implement Path A (primary):
- Read `h-e1/04_validation.md` to extract ECE_base values for pythia-{1.4b|2.8b|6.9b}-base
- Parse key_metrics section using regex patterns for `ece_base_{size}` fields
- Fall back to Path B if ECE_base keys not found in H-E1 validation report
- Return structured dict: `{model_id: ece_value}` for all 3 base models

```python
# FR-1 Interface
def load_h_e1_ece_base(validation_file: str = "h-e1/04_validation.md") -> dict[str, float]:
    """
    Extract ECE_base values for Pythia base models from H-E1 validation report.
    Returns: {"pythia-1.4b-base": float, "pythia-2.8b-base": float, "pythia-6.9b-base": float}
    """
```

### FR-2: Fallback lm-eval Execution (Path B)

**Priority:** MUST HAVE (fallback)
**Source:** h-m1/02c_experiment_brief.md §Training Protocol

The system SHALL implement Path B (fallback) when H-E1 outputs are not parseable:
- Execute lm-eval v0.4.11 for EleutherAI/pythia-{1.4b|2.8b|6.9b} on MMLU (0-shot, greedy)
- Use `--log_samples` to capture per-item log-probability vectors
- Save outputs to `h-m1/results/pythia-{size}-base/`
- Execute one model at a time (sequential to manage GPU memory)

```bash
# FR-2 Execution Template
lm_eval --model hf \
  --model_args "pretrained=EleutherAI/pythia-{SIZE}" \
  --tasks mmlu \
  --num_fewshot 0 \
  --output_path ./h-m1/results/pythia-{SIZE}-base/ \
  --log_samples \
  --device cuda:0
```

### FR-3: ECE Computation

**Priority:** MUST HAVE
**Source:** h-m1/02c_experiment_brief.md §Evaluation

The system SHALL compute 15-bin ECE (Guo et al. 2017) for each base model:
- Inherit `compute_ece()` from `h-e1/code/calibration_analysis.py` (no reimplementation)
- Input: (N, 4) log-probability array + (N,) integer labels
- Output: scalar ECE value in [0, 1]
- Apply softmax to convert log-probs to probabilities before ECE computation

```python
# FR-3 Interface — reuse from h-e1
import sys
sys.path.append("h-e1/code/")
from calibration_analysis import compute_ece, compute_brier_decomposition
```

### FR-4: MUST_WORK Gate Evaluation

**Priority:** MUST HAVE
**Source:** h-m1/02c_experiment_brief.md §Gate Condition

The system SHALL implement gate evaluation:
- Check ECE_base < 0.15 for ALL 3 model sizes (1.4B, 2.8B, 6.9B)
- Return: gate_result ∈ {"PASS", "FAIL"}
- If ANY size has ECE_base ≥ 0.15 → FAIL
- Document which sizes passed/failed in validation report

```python
# FR-4 Interface
def evaluate_must_work_gate(ece_base: dict[str, float]) -> tuple[str, list[str]]:
    """
    Returns: (gate_result, failed_checks)
    gate_result: "PASS" if all ECE_base < 0.15, else "FAIL"
    failed_checks: list of model_ids where ECE ≥ 0.15
    """
```

### FR-5: Secondary Calibration Ordering Check

**Priority:** SHOULD HAVE
**Source:** h-m1/02c_experiment_brief.md §Evaluation (Secondary Metrics)

The system SHALL verify calibration ordering (informative only, non-gating):
- Load ECE values for SFT, DPO, PPO models from H-E1 validation report
- Check ECE_base < ECE_SFT for each model size
- Report ordering compliance: count of sizes where ordering holds

### FR-6: Figure Generation

**Priority:** MUST HAVE (mandatory) + SHOULD HAVE (additional)
**Source:** h-m1/02c_experiment_brief.md §Visualization Requirements

The system SHALL generate:

**Mandatory Figure:**
- **Figure 1:** Bar chart of ECE_base for 1.4B / 2.8B / 6.9B Pythia base models
  - Horizontal dashed line at ECE = 0.15 (gate threshold)
  - Color coding: green if < 0.15, red if ≥ 0.15
  - Save to: `h-m1/figures/figure_01_ece_gate.png`

**Additional Figures (Strongly Recommended):**
- **Figure 2:** Base vs Aligned ECE comparison (3 sizes × 4 conditions bar chart)
  - Save to: `h-m1/figures/figure_02_base_vs_aligned_ece.png`
- **Figure 3:** Calibration reliability diagrams (3 panels, one per Pythia size)
  - Save to: `h-m1/figures/figure_03_calibration_curves.png`
- **Figure 4:** ECE by MMLU Subject (box plot, 57 subjects × 3 base models)
  - Save to: `h-m1/figures/figure_04_ece_by_subject.png`
- **Figure 5:** Brier Decomposition (reliability vs resolution vs uncertainty)
  - Save to: `h-m1/figures/figure_05_brier_decomposition.png`

### FR-7: Validation Report Generation

**Priority:** MUST HAVE
**Source:** Phase 4 pipeline requirements

The system SHALL generate `h-m1/04_validation.md` containing:
- Experiment metadata (hypothesis ID, type, date)
- Gate result: PASS/FAIL with gate type (MUST_WORK)
- ECE_base values for all 3 model sizes
- Size-specific gate check results
- Secondary metrics (calibration ordering)
- Figure paths and descriptions
- Key findings list (≥3 findings)
- Execution path used (Path A or Path B)

### FR-8: Mechanism Activation Verification

**Priority:** MUST HAVE
**Source:** h-m1/02c_experiment_brief.md §Mechanism Activation Indicators

The system SHALL verify mechanism activation before accepting results:
- Confirm ECE_base values are non-null floats in range [0, 1]
- Confirm all 3 model sizes produced valid ECE values
- Log verification status to stdout during execution

---

## 5. Data Specification

### Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | MMLU (Massive Multitask Language Understanding) |
| Version | Full test set (cais/mmlu, HuggingFace) |
| Size | ~14,042 items across 57 subjects |
| Format | 4-option multiple-choice (log-probability evaluation) |
| Cache | `~/.cache/huggingface/datasets/cais___mmlu` |
| Download | NOT required — already cached from H-E1 |
| Preprocessing | None — lm-eval handles via `--tasks mmlu` |

### Data Sources

| Source | Usage |
|--------|-------|
| `h-e1/04_validation.md` | **Primary (Path A):** ECE_base values already computed |
| `h-e1/results/pythia-{size}-base/` | **Primary (Path A):** lm-eval log-probability outputs |
| HuggingFace Hub (EleutherAI/pythia-*) | **Fallback (Path B):** Model weights for re-evaluation |
| `~/.cache/huggingface/datasets/cais___mmlu` | **Fallback (Path B):** Cached MMLU dataset |

### Data Priority

1. **Path A (PREFERRED):** Read ECE_base from `h-e1/04_validation.md` — 0 new GPU-hours
2. **Path A (Extended):** Load log-probs from `h-e1/results/pythia-{size}-base/` and recompute
3. **Path B (FALLBACK):** Re-run lm-eval for 3 base models only

---

## 6. Evaluation Metrics

### Primary Metrics (Gate-Determining)

| Metric | Definition | Threshold | Gate |
|--------|-----------|-----------|------|
| ECE_base (1.4B) | 15-bin Guo 2017 ECE on MMLU | < 0.15 | MUST_WORK |
| ECE_base (2.8B) | 15-bin Guo 2017 ECE on MMLU | < 0.15 | MUST_WORK |
| ECE_base (6.9B) | 15-bin Guo 2017 ECE on MMLU | < 0.15 | MUST_WORK |

**Gate Logic:** ALL 3 sizes must satisfy ECE_base < 0.15 for PASS.

### Secondary Metrics (Informative Only)

| Metric | Definition | Expected | Non-gating |
|--------|-----------|----------|-----------|
| ECE ordering | ECE_base < ECE_SFT for each size | True for ≥2/3 sizes | ✓ |
| Brier_rel_base | Murphy 1973 reliability component | Low (near 0) | ✓ |
| Per-subject ECE | ECE computed per MMLU subject | Consistent ≈ aggregate | ✓ |

### Expected Values (from literature)

- Pythia base ECE: < 0.15 on MMLU (Xie et al. 2024)
- Reference: LLaMA-2 base ECE ≈ 0.08; LLaMA-2-Chat ECE = 0.298 (post-RLHF)
- H-E1 context: PPO 1.4B ΔBrier_rel = +0.0406 → base ECE is the reference point

---

## 7. Non-Functional Requirements

### NFR-1: Computational Efficiency
- Path A execution: < 5 minutes (data reading only)
- Path B execution (if needed): < 2 hours for 3 base models on single GPU
- Memory: ≤ 24 GB VRAM for 6.9B model (float16)

### NFR-2: Reproducibility
- All random seeds fixed (seed=42)
- Greedy decoding (temperature=1.0, no sampling)
- Identical lm-eval v0.4.11 configuration as H-E1
- Single GPU execution only

### NFR-3: Code Reuse
- MUST inherit h-e1/code/calibration_analysis.py (no reimplementation of ECE)
- MUST use lm-eval v0.4.11 (same version as H-E1) if Path B needed
- Import path: `sys.path.append("h-e1/code/")`

### NFR-4: Error Handling
- FileNotFoundError on H-E1 outputs → activate Path B automatically
- Model loading error → fail with descriptive error message
- ECE out of range [0, 1] → raise ValueError (data integrity check)

### NFR-5: Output Organization
- Results: `h-m1/results/` (if Path B)
- Figures: `h-m1/figures/`
- Code: `h-m1/code/`
- Report: `h-m1/04_validation.md`

---

## 8. Dependencies

### 8.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| lm-eval | v0.4.11 | MMLU log-probability extraction (Path B only) |
| torch | ≥2.0 | Model inference (Path B) |
| transformers | ≥4.35 | Pythia model loading (Path B) |
| numpy | ≥1.24 | ECE computation, array operations |
| scipy | ≥1.10 | softmax for probability conversion |
| matplotlib | ≥3.7 | Figure generation |
| seaborn | ≥0.12 | Statistical visualization |
| pyyaml | ≥6.0 | YAML parsing for verification_state.yaml |
| accelerate | ≥0.24 | Multi-GPU support if needed |

### 8.2 External References (Non-Installable)

| Resource | Location | Purpose |
|----------|----------|---------|
| H-E1 Validation Report | `h-e1/04_validation.md` | Primary ECE_base source (Path A) |
| H-E1 lm-eval outputs | `h-e1/results/pythia-{size}-base/` | Log-probability files (Path A extended) |
| H-E1 Code | `h-e1/code/calibration_analysis.py` | compute_ece, compute_brier_decomposition |
| EleutherAI/pythia-1.4b | HuggingFace Hub | Base model (Path B fallback) |
| EleutherAI/pythia-2.8b | HuggingFace Hub | Base model (Path B fallback) |
| EleutherAI/pythia-6.9b | HuggingFace Hub | Base model (Path B fallback) |
| MMLU | `cais/mmlu` HuggingFace Hub | Dataset (cached from H-E1) |

### 8.3 Hardware Requirements

| Resource | Requirement |
|----------|------------|
| GPU | 1× CUDA GPU (≥16 GB VRAM for 6.9B model) |
| RAM | ≥32 GB system RAM |
| Storage | ≥50 GB for lm-eval outputs (Path B) |

---

## 9. Success Criteria

### Primary (MUST_WORK Gate)

```
PASS condition:
  ECE_base(pythia-1.4b) < 0.15  AND
  ECE_base(pythia-2.8b) < 0.15  AND
  ECE_base(pythia-6.9b) < 0.15

FAIL condition: ANY of the above thresholds NOT met
FAIL consequence: Reassess base calibration assumption; mechanistic chain H-M2→M3→M4 at risk
```

### Secondary (Informative)

```
EXPECTED:
  ECE_base < ECE_SFT for ≥ 2/3 model sizes
  Brier_rel_base near 0 for all 3 sizes
  Per-subject ECE consistent across 57 MMLU subjects
```

### Deliverables

| Deliverable | Required |
|-------------|---------|
| `h-m1/04_validation.md` | ✅ MUST |
| `h-m1/figures/figure_01_ece_gate.png` | ✅ MUST |
| `h-m1/figures/figure_0[2-5]_*.png` | ✅ STRONGLY RECOMMENDED |
| Gate result written to verification_state.yaml | ✅ MUST |
| ECE_base values logged for H-M2/M3/M4 context | ✅ MUST |

---

## 10. Phase 2C → Phase 3 Completeness Check

| Phase 2C Item | Present in PRD |
|---------------|----------------|
| Dataset: MMLU (cais/mmlu, 14,042 items) | ✅ FR-2, §5 |
| Base models: pythia-1.4b, 2.8b, 6.9b | ✅ FR-2, §5 |
| Path A (H-E1 data reuse) | ✅ FR-1, §5 |
| Path B fallback (lm-eval re-run) | ✅ FR-2 |
| ECE computation (15-bin Guo 2017) | ✅ FR-3 |
| MUST_WORK gate: ECE_base < 0.15 (all 3) | ✅ FR-4, §9 |
| Secondary: ordering check | ✅ FR-5 |
| Mandatory figure (bar chart + threshold line) | ✅ FR-6 |
| Additional figures (4 recommended) | ✅ FR-6 |
| Code inheritance from h-e1 | ✅ FR-3, §7 NFR-3 |
| Mechanism activation verification | ✅ FR-8 |

---

*Generated by Phase 3: Implementation Planning*
*Hypothesis: H-M1 | Type: MECHANISM | Tier: FULL | Base: H-E1*
