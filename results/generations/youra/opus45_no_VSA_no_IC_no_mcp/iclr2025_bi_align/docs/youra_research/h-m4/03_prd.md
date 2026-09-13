# Product Requirements Document: H-M4 Differential Benchmark Profiles

**Hypothesis ID:** h-m4
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Generated:** 2026-08-26
**Phase 3 Document**

---

## 1. Executive Summary

Evaluate whether RLHF and DPO training methods produce measurably different alignment profiles across TruthfulQA, HHH-helpful, and HHH-harmless benchmarks. Test for differential (not uniform) performance: at least one benchmark showing significant difference while another shows equivalence.

**Prerequisite Context:** H-M3 (attractor hypothesis) returned PARTIAL — attractor mechanism not confirmed. H-M4 proceeds to test profile differences directly under SHOULD_WORK gate.

---

## 2. Problem Statement

### 2.1 Business Context

Understanding whether preference learning methods produce functionally equivalent models or distinct alignment profiles informs method selection for alignment training.

### 2.2 Core Question

Do DPO and RLHF produce different dimensional alignment signatures across truthfulness, helpfulness, and harmlessness benchmarks?

### 2.3 Success Definition

Primary criterion: At least one benchmark shows Cohen's d > 0.3 AND at least one shows d < 0.15 (differential profile).

---

## 3. Functional Requirements

### FR-1: Model Loading
- **Description:** Load 10 trained models from h-m3 checkpoints
- **Models:** 5 DPO (seeds: 42, 137, 256, 512, 1024), 5 RLHF (same seeds)
- **Source:** h-m3/checkpoints/
- **Acceptance:** All 10 models load without error, parameters match expected count

### FR-2: TruthfulQA Evaluation
- **Description:** Evaluate all models on TruthfulQA MC1
- **Dataset:** truthfulqa/truthful_qa (multiple_choice subset)
- **Size:** 817 questions (full test set)
- **Metric:** MC1 accuracy (highest log-probability answer selection)
- **Output:** Per-model, per-question scores

### FR-3: HHH-helpful Evaluation
- **Description:** Evaluate all models on HHH helpful preference
- **Dataset:** Anthropic/hh-rlhf (test split, helpful-base)
- **Size:** Full evaluation split (~8k samples)
- **Metric:** Preference accuracy (chosen vs rejected log-probability)
- **Output:** Per-model, per-sample scores

### FR-4: HHH-harmless Evaluation
- **Description:** Evaluate all models on HHH harmless preference
- **Dataset:** Anthropic/hh-rlhf (test split, harmless-base)
- **Size:** Full evaluation split (~8k samples)
- **Metric:** Preference accuracy (chosen vs rejected log-probability)
- **Output:** Per-model, per-sample scores

### FR-5: Differential Profile Analysis
- **Description:** Compute effect sizes and test differential criterion
- **Computation:**
  - Cohen's d for each benchmark (DPO vs RLHF)
  - t-tests for significance
  - Differential criterion: max(|d|) > 0.3 AND min(|d|) < 0.15
- **Output:** differential_analysis.json

### FR-6: Profile Shape Analysis
- **Description:** Compare normalized benchmark profiles
- **Computation:**
  - Mean accuracy per method per benchmark
  - Z-score normalization for profile shape
  - Profile correlation between methods
- **Output:** Profile vectors, correlation coefficient

### FR-7: Visualization
- **Description:** Generate radar chart comparing profiles
- **Format:** PNG, publication-quality
- **Output:** profile_comparison.png

### FR-8: Validation Report
- **Description:** Generate 04_validation.md with PASS/FAIL determination
- **Content:** Effect sizes, differential test result, limitations from h-m3

---

## 4. Non-Functional Requirements

### NFR-1: Compute Efficiency
- Batch inference within benchmarks
- Single GPU (A100 40GB) sufficient

### NFR-2: Reproducibility
- Fixed evaluation seeds
- Pinned dataset versions
- Deterministic inference

### NFR-3: Statistical Rigor
- Full test sets for >95% power at d=0.3
- Multiple seeds for variance estimation

---

## 5. Data Specifications

| Dataset | Source | Split | Size | Format |
|---------|--------|-------|------|--------|
| TruthfulQA | truthfulqa/truthful_qa | multiple_choice | 817 | HuggingFace |
| HHH-helpful | Anthropic/hh-rlhf | test/helpful-base | ~8k | HuggingFace |
| HHH-harmless | Anthropic/hh-rlhf | test/harmless-base | ~8k | HuggingFace |

---

## 6. Model Specifications

| Model Set | Training Method | Count | Source |
|-----------|-----------------|-------|--------|
| DPO models | DPO | 5 | h-m3/checkpoints/dpo_seed_* |
| RLHF models | RLHF | 5 | h-m3/checkpoints/rlhf_seed_* |

Base: meta-llama/Llama-2-7b-hf

---

## 7. Success Criteria

### Primary (Gate: SHOULD_WORK)
- [P1] At least one benchmark shows |Cohen's d| > 0.3
- [P2] At least one benchmark shows |Cohen's d| < 0.15
- [P3] P1 AND P2 satisfied (differential profile)

### Secondary
- [S1] Profile correlation < 0.8 (distinct shapes)
- [S2] Cross-benchmark correlation differences > 0.3 for at least one pair

### Failure Interpretation
- All d < 0.15: No detectable difference (H0)
- All d > 0.3 same direction: Uniform difference, not dimensional

---

## 8. Dependencies

### Input Dependencies
- h-m3 model checkpoints (5 DPO, 5 RLHF)
- HuggingFace datasets access

### Output Consumers
- Phase 4 validation
- Phase 4.5 synthesis
- Phase 6 paper writing

---

## 9. Estimated Timeline

| Phase | Duration |
|-------|----------|
| Model loading | 1 hour |
| TruthfulQA eval | 4 hours |
| HHH-helpful eval | 8 hours |
| HHH-harmless eval | 8 hours |
| Analysis | 2 hours |
| Reporting | 2 hours |
| **Total** | ~25 hours |

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| h-m3 checkpoints unavailable | Verify before starting |
| Evaluation inconsistency | Use lm-evaluation-harness |
| Statistical power | Full test sets ensure >95% power |

---

*Generated by Phase 3 Implementation Planning*
*Status: Complete*
