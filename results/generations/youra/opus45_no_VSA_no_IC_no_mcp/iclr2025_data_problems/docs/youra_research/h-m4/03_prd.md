# Product Requirements Document: H-M4

**Date:** 2026-08-28
**Hypothesis:** Scale Transfer Validation
**Statement:** Under optimal curation parameters identified at 125M scale, the same parameters at 1B scale preserve relative performance rankings

---

## 1. Executive Summary

H-M4 validates whether the optimal perplexity threshold (p44.5) identified at 125M scale transfers to 1B scale while preserving relative performance rankings. This tests the scale-invariant optima hypothesis critical for practical data curation.

### Success Criteria
1. Optimal threshold at 1B within ±20% of 125M optimum
2. CPDR-optimized outperforms defaults at both scales
3. Relative rankings preserved (same sign improvement at both scales)

---

## 2. Scope

### In Scope
- Train GPT-2 125M from scratch on RedPajama-v2 with optimal (p44.5) and default thresholds
- Train GPT-2 1B from scratch on same filtered datasets
- Evaluate on HellaSwag, ARC-Easy, PIQA, WinoGrande
- Compare relative improvements across scales
- Generate scale transfer analysis figures

### Out of Scope
- Full threshold sweep at 1B (only mini-sweep if rankings diverge)
- Scales beyond 1B
- Non-perplexity quality metrics
- Production deployment

---

## 3. Technical Requirements

### 3.1 Data Pipeline
| Requirement | Specification |
|-------------|---------------|
| Source Dataset | RedPajama-Data-v2 (English) |
| Filtering | KenLM 5-gram perplexity |
| Optimal Threshold | p44.5 (from H-M3) |
| Default Threshold | RedPajama default |
| Token Budget (125M) | 10B tokens |
| Token Budget (1B) | 20B tokens (compute-matched) |

### 3.2 Models
| Model | Parameters | Config |
|-------|------------|--------|
| GPT-2 Small | 125M | n_embd=768, n_layer=12, n_head=12 |
| GPT-2 1B | 1B | n_embd=1600, n_layer=48, n_head=25 |

### 3.3 Training
| Parameter | 125M | 1B |
|-----------|------|-----|
| Learning Rate | 6e-4 | 2e-4 |
| Batch Size | 512K tokens | 2M tokens |
| Optimizer | AdamW (β1=0.9, β2=0.95) | AdamW |
| Warmup | 2000 steps | 2000 steps |
| Seeds | 3 | 3 |
| Precision | FP16 | BF16 |

### 3.4 Evaluation
- Library: lm-eval-harness
- Tasks: hellaswag, arc_easy, piqa, winogrande
- Metric: Mean accuracy (ensemble) or PC1
- Success: Same-sign improvement at both scales

---

## 4. Deliverables

1. **Code**: Training and evaluation pipeline
2. **Checkpoints**: 125M and 1B models (3 seeds each, 2 thresholds)
3. **Results**: JSON with per-benchmark and ensemble scores
4. **Figures**: Scale transfer comparison plots
5. **Analysis**: Threshold transfer validation report

---

## 5. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| 1B training OOM | Use gradient checkpointing, BF16, batch accumulation |
| Compute budget exceeded | Start with 125M validation, proceed to 1B if successful |
| Rankings don't transfer | Document as finding; run mini-sweep to find 1B optimum |

---

## 6. Dependencies

- H-M3 PASS (optimal threshold p44.5)
- GPU compute (minimum 4x A100 for 1B training)
- RedPajama-v2 access
- lm-eval-harness installed

---

## 7. Timeline Estimate

| Phase | Duration |
|-------|----------|
| Data preparation | 1 day |
| 125M training (2 thresholds × 3 seeds) | 2 days |
| 1B training (2 thresholds × 3 seeds) | 5 days |
| Evaluation and analysis | 1 day |
| **Total** | 9 days |
