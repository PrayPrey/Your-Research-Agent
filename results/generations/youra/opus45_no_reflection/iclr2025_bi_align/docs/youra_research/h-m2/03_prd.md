# Product Requirements Document: H-M2

**Hypothesis:** BiDPO models generate responses with higher collaboration scores than DPO
**Type:** MECHANISM
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This PRD specifies implementation requirements for validating that BiDPO-trained models generate responses with statistically higher collaboration scores than standard DPO baselines. The experiment compares response generation quality between the BiDPO checkpoint (from H-M1) and Mistral-7B-Instruct baseline on 500 held-out prompts from HH-RLHF.

**Gate Condition:** BiDPO mean collaboration score > DPO mean AND paired t-test p < 0.05.

---

## 2. Problem Statement

H-M1 demonstrated that BiDPO training with L_agency loss is stable (loss decreased 0.929 → 0.918). The next validation step tests whether this training translates to measurably higher agency-preservation signals in generated responses.

**Success Criteria:**
- BiDPO responses show higher mean collaboration scores
- Statistical significance at p < 0.05 (one-sided paired t-test)
- Cohen's d effect size > 0.2 (small effect threshold)

---

## 3. Functional Requirements

### FR-1: Prompt Extraction
**Priority:** P0 (Critical)
- Load HH-RLHF test split from HuggingFace
- Extract 500 unique prompts from Human turns
- Format prompts with Mistral chat template `[INST] ... [/INST]`

### FR-2: Baseline Model Loading
**Priority:** P0 (Critical)
- Load Mistral-7B-Instruct-v0.2 from HuggingFace Hub
- Configure bfloat16 dtype with auto device_map
- Set pad_token = eos_token

### FR-3: BiDPO Model Loading
**Priority:** P0 (Critical)
- Load base Mistral-7B-Instruct-v0.2 architecture
- Load H-M1 trained weights from `../h-m1/code/outputs/final.pt`
- Apply state_dict with strict=False for compatibility

### FR-4: Response Generation
**Priority:** P0 (Critical)
- Generate responses for all 500 prompts from both models
- Parameters: max_new_tokens=256, temperature=0.7, top_p=0.9
- Use deterministic seed=42 for reproducibility
- Track generation time for both models

### FR-5: Collaboration Score Computation
**Priority:** P0 (Critical)
- Implement compute_collab_score_v2() function (from H-E1)
- Score all 1000 responses (500 BiDPO + 500 DPO)
- Length-normalize scores by sqrt(word_count)

### FR-6: Statistical Analysis
**Priority:** P0 (Critical)
- Compute paired t-test (same prompts)
- Calculate one-sided p-value (BiDPO > DPO)
- Compute Cohen's d effect size
- Generate comparison statistics

### FR-7: Visualization
**Priority:** P1 (High)
- Required: Bar chart comparing mean scores with error bars
- Additional: Score distribution histograms
- Additional: Per-prompt scatter plot (DPO vs BiDPO)
- Save all figures to `figures/` directory

### FR-8: Gate Evaluation
**Priority:** P0 (Critical)
- Evaluate gate condition: BiDPO_mean > DPO_mean AND p_onesided < 0.05
- Output structured results for verification_state.yaml update
- Generate 04_validation.md report

---

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | HH-RLHF Test Split |
| Source | HuggingFace Hub |
| Identifier | Anthropic/hh-rlhf (helpful-base) |
| Split | test |
| Sample Size | 500 unique prompts |
| Auto-download | Yes (HuggingFace datasets) |

### 4.2 Model Checkpoints

| Model | Source | Path |
|-------|--------|------|
| Baseline (DPO) | HuggingFace | mistralai/Mistral-7B-Instruct-v0.2 |
| Proposed (BiDPO) | Local | ../h-m1/code/outputs/final.pt |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Generation should complete within 60 minutes for both models
- GPU memory usage < 24GB (single A100 or equivalent)

### NFR-2: Reproducibility
- Random seed fixed at 42
- All generation parameters logged
- Results include confidence intervals

### NFR-3: Compatibility
- Python 3.10+
- PyTorch 2.0+
- transformers 4.40+

---

## 6. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Gate Pass | BiDPO > DPO AND p < 0.05 | Paired t-test |
| Effect Size | Cohen's d > 0.2 | Pooled std calculation |
| Sample Size | 500 prompts | Full extraction |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.40.0
datasets>=2.14.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| H-M1 Checkpoint | ../h-m1/code/outputs/final.pt | BiDPO trained weights |
| compute_collab_score_v2 | ../h-e1/code/ | Reuse scoring function |

### 7.3 Hardware Requirements

- GPU: NVIDIA A100 40GB (or equivalent)
- RAM: 32GB minimum
- Storage: 50GB for model weights + outputs

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| H-M1 checkpoint missing | Blocker | Verify file exists at start |
| Memory overflow | High | Use bfloat16, batch generation |
| Statistical power | Medium | 500 samples provides >95% power for d=0.2 |

---

## 9. Appendix: Phase 2C Reference

- Experiment Brief: 02c_experiment_brief.md
- Gate Type: SHOULD_WORK
- Prerequisite: H-M1 (PASSED)
