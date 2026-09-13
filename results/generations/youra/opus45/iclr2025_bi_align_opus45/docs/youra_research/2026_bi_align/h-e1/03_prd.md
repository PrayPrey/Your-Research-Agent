# Product Requirements Document: H-E1

**Hypothesis:** Structural Enumeration Preference in RLHF-Trained Reward Models
**Type:** EXISTENCE (PoC Validation)
**Date:** 2026-03-24
**Author:** Anonymous
**Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for validating whether RLHF-trained reward models exhibit a consistent preference for enumerated response structures across multiple architecturally distinct models. The experiment tests the existence of an enumeration preference effect (Cohen's d >= 0.3) as a foundation for subsequent mechanism investigations.

**Key Deliverables:**
1. Custom stimulus generation pipeline (600 factorial stimulus pairs)
2. Multi-RM inference infrastructure (4 architecturally distinct models)
3. Statistical analysis pipeline for effect size computation
4. Visualization suite for result presentation

---

## Problem Statement

### Background

Prior research identified a strong enumeration preference (d=0.634) in ArmoRM during a composite agency experiment. However, this finding was confounded with other factors (deliberation markers, verbosity). This experiment isolates the enumeration factor to validate whether the preference is:
1. Real and replicable (not measurement artifact)
2. Cross-model robust (not ArmoRM-specific)
3. Independent of confounding factors (controlled via factorial design)

### Goal

Determine whether RLHF-trained reward models systematically prefer enumerated responses over semantically equivalent synthesized responses, across multiple architecturally distinct models.

### Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Primary | Cohen's d >= 0.3 in >= 2 architecturally distinct RMs | MUST_WORK |
| Secondary | >= 75% (3/4) RMs show positive effect (d > 0) | SHOULD_WORK |

---

## Functional Requirements

### FR-1: Stimulus Generation Pipeline

**Purpose:** Generate controlled stimulus pairs with 2x2x2 factorial design

**Requirements:**
- FR-1.1: Generate 75 diverse base prompts across domains (general knowledge, advice, explanation)
- FR-1.2: Create 8 response variants per prompt (2x2x2: Structure × Correctness × Completeness)
- FR-1.3: Match response length within ±2% across structure conditions
- FR-1.4: Implement regex-based enumeration classifier (>95% accuracy target)
- FR-1.5: Validate cross-factor contamination (require |d| < 0.2)

**Output:** `stimuli.json` with 600 stimulus pairs (75 prompts × 8 variants)

**Acceptance Criteria:**
- Enumeration classifier achieves >95% agreement with human labels
- Length matching within ±2% verified programmatically
- Cross-factor contamination validated via pilot human ratings

### FR-2: Multi-RM Inference Infrastructure

**Purpose:** Score stimuli across 4 architecturally distinct reward models

**Models:**
| Model | HuggingFace ID | Architecture | Size |
|-------|----------------|--------------|------|
| ArmoRM | `RLHFlow/ArmoRM-Llama3-8B-v0.1` | Llama-3 + MoE gating | 8B |
| UltraRM | `openbmb/UltraRM-13b` | Llama + regression head | 13B |
| Starling-RM | `berkeley-nest/Starling-RM-7B-alpha` | Llama2-7B-Chat | 7B |
| PairRM | `llm-blender/PairRM` | DeBERTa-v3-large | 0.4B |

**Requirements:**
- FR-2.1: Implement unified RM interface supporting all 4 models
- FR-2.2: Handle model-specific loading (trust_remote_code, custom wrappers)
- FR-2.3: Support batch inference (batch_size=16) for efficiency
- FR-2.4: Normalize scores to [0, 1] range for cross-model comparison
- FR-2.5: Implement PairRM pairwise comparison mode

**Acceptance Criteria:**
- All 4 models load and produce scores without error
- Inference completes for full stimulus set within reasonable time (<2 hours total)
- Score normalization verified via spot checks

### FR-3: Statistical Analysis Pipeline

**Purpose:** Compute effect sizes and statistical significance

**Requirements:**
- FR-3.1: Compute Cohen's d for structure main effect per RM
- FR-3.2: Compute 95% confidence intervals for effect sizes
- FR-3.3: Implement paired t-test for significance testing
- FR-3.4: Compute pooled effect size across RMs (with heterogeneity test)
- FR-3.5: Generate per-RM and aggregate summary statistics

**Acceptance Criteria:**
- Effect sizes match manual calculation on subset
- CI coverage verified via bootstrap validation
- Results exportable to structured format (JSON/CSV)

### FR-4: Visualization Suite

**Purpose:** Generate publication-quality figures for results

**Required Figures:**
- FR-4.1: Per-RM effect size forest plot with 95% CI
- FR-4.2: Score distribution violin plot (enumerated vs. synthesized per RM)
- FR-4.3: Factorial interaction plot (Structure × Correctness × Completeness)
- FR-4.4: Gate metrics comparison (target vs. actual bar chart)

**Acceptance Criteria:**
- All figures saved as PNG and PDF formats
- Font sizes appropriate for publication (minimum 12pt)
- Color scheme accessible (colorblind-friendly palette)

---

## Non-Functional Requirements

### NFR-1: Performance

- Inference throughput: Complete full experiment in <2 hours on single GPU
- Memory efficiency: Support 13B model loading with 4-bit quantization if needed
- Batch processing: Minimize GPU idle time via efficient batching

### NFR-2: Reproducibility

- Fixed random seed (42) for stimulus generation
- Deterministic model inference (disable dropout, use eval mode)
- Complete logging of all hyperparameters and configurations
- Checkpointing of intermediate results

### NFR-3: Reliability

- Graceful error handling for model loading failures
- Resume capability from checkpoints
- Validation assertions at each pipeline stage

### NFR-4: Maintainability

- Modular code structure (separate modules for stimulus, inference, analysis, visualization)
- Configuration via YAML files (not hardcoded)
- Type hints and docstrings for all public functions

---

## Data Requirements

### Input Data

| Data | Source | Format | Size |
|------|--------|--------|------|
| Base prompts | LLM-generated | JSON | 75 prompts |
| Response variants | LLM-generated | JSON | 600 pairs |
| Human validation (pilot) | Manual annotation | CSV | 50 samples |

### Output Data

| Data | Format | Location |
|------|--------|----------|
| Raw scores | JSON | `data/raw_scores.json` |
| Effect sizes | JSON | `data/effect_sizes.json` |
| Summary statistics | CSV | `data/summary_stats.csv` |
| Figures | PNG/PDF | `figures/` |
| Validation report | Markdown | `04_validation.md` |

---

## Technical Constraints

### Hardware Requirements
- GPU: Single CUDA-capable GPU with ≥16GB VRAM (for UltraRM-13b)
- Fallback: 4-bit quantization if VRAM insufficient

### Software Dependencies
- Python 3.10+
- PyTorch 2.0+
- Transformers 4.30+
- bitsandbytes (for quantization)
- scipy, numpy, pandas (analysis)
- matplotlib, seaborn (visualization)
- llm-blender (for PairRM)

### Environment Variables
- `CUDA_VISIBLE_DEVICES`: Set to single available GPU
- `HF_HOME`: HuggingFace cache directory

---

## Dependencies

### Internal Dependencies
- Phase 2C Experiment Brief: `02c_experiment_brief.md` (input specification)
- Phase 2B Context: `02b_context.md` (hypothesis context)

### External Dependencies
- HuggingFace Model Hub (model downloads)
- No external APIs required (all inference is local)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Model loading failure | Low | High | Implement fallback quantization, verify model availability |
| OOM during inference | Medium | Medium | Use batch size 8, implement gradient checkpointing |
| Effect size < threshold | Unknown | High | This is the experimental question - no mitigation needed |
| Cross-factor contamination | Low | Medium | Validate via pilot human ratings before full run |

---

## Acceptance Criteria Summary

### Gate Condition (MUST_WORK)

```
IF Cohen's d >= 0.3 in >= 2 architecturally distinct RMs:
    PASS → Proceed to mechanism hypotheses (H-M1, H-M2)
ELSE:
    FAIL → ABANDON main hypothesis (enumeration preference not robust)
```

### Quality Criteria

- [ ] All 4 models produce valid scores
- [ ] Effect sizes computed with confidence intervals
- [ ] All required figures generated
- [ ] Results reproducible with same random seed
- [ ] Validation report documents all findings

---

## Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Success Criteria | Gate Condition section |
| FR-1 | Dataset section |
| FR-2 | Models section |
| FR-3 | Evaluation section |
| FR-4 | Visualization Requirements section |
| Technical Constraints | Training Protocol / Inference Protocol |

---

*Generated for Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Architecture Design (03_architecture.md)*
