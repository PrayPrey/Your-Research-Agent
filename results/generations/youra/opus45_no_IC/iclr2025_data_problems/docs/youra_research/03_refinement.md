# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap1
- **Gap Title**: Quantitative Contamination-Performance Correlation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 19

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 19

**Convergence Reason**: All 6 criteria met at exchange 19 with full persona participation

### Key Insights
- Checkpoint-gradient methodology enables contamination-performance correlation without requiring clean baseline models
- OOD perplexity detrending (WikiText-103) separates capability gains from contamination-induced inflation
- Exact-match vs generation benchmark comparison tests the mechanism specificity hypothesis
- Pre-registration protocol eliminates multiple comparison and selection bias concerns

### Breakthrough Moments
- Exchange 7: Dr. Nova proposed using checkpoint gradient instead of clean baseline requirement
- Exchange 10: Dr. Ally synthesized the exposure-dependent vs convergence-dependent mechanism test
- Exchange 16: Prof. Rex identified OOD perplexity as critical improvement over Pile validation set

---

## Final Hypothesis

### Title
Contamination-Performance Transfer Function for LLM Benchmarks

### Core Claim
Under the condition of language models trained on documented corpora with measurable n-gram overlap, if we increase cumulative benchmark-relevant exposure during training, then benchmark scores will show positive inflation residuals after capability detrending, because progressive memorization encodes benchmark content proportionally to exposure frequency.

### Mechanism
1. Training corpus contains benchmark-relevant content as n-gram sequences
2. Repeated exposure during training leads to memorization of benchmark sequences
3. At inference, memorized content enables correct answers independent of generalization
4. This produces score inflation proportional to contamination level

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | Spearman r > 0.5 between cumulative 13-gram exposure and MMLU inflation residual | r > 0.5, p < 0.05 | r < 0.2, 95% CI upper < 0.35 |
| **P2** | Effect size ≥3% inflation at 10% contamination | Regression coefficient predicts ≥3% | Effect < 1% at 10% |
| **P3** | Exact-match benchmarks show higher inflation than generation | ARC > HellaSwag inflation | HellaSwag ≥ ARC |

---

## Novelty

**Key Innovation**: First empirically-validated contamination-to-inflation transfer function

**Differentiation**:
- **vs Sainz et al. (2023)**: Detects contamination but does not quantify performance impact
- **vs Dong et al. (2024) TED**: Proposes mitigation but does not model inflation magnitude
- **vs Choi et al. (2025) KDS**: Quantifies contamination presence but not score inflation

**Pipeline Position**: Completes detection → quantification → **impact modeling** → mitigation

---

## Experimental Design

### Models
- Pythia family: 410M, 1B, 1.4B, 2.8B, 6.9B, 12B
- 12 checkpoints per model (0%, 10%, ..., 100% + final)

### Datasets
- **Training corpus**: The Pile (documented, indexed)
- **Primary benchmark**: MMLU
- **Secondary**: ARC-Challenge, HellaSwag, WinoGrande
- **Capability detrending**: WikiText-103

### Baselines
- Capability-predicted scores via perplexity regression
- Shuffled checkpoint-contamination null baseline

---

## Limitations

1. **Single model family**: Pythia-only validation limits generalizability claims
2. **Verbatim contamination only**: 13-gram may miss paraphrased/semantic contamination
3. **Architecture-specific**: Transfer function may need recalibration for GPT/LLaMA families

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 19 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (concerns scoped as future work) |

---

## Phase 2B Readiness

- **H-E1 (Existence)**: Contamination-inflation correlation exists (r > 0.2)
- **H-M (Mechanism)**: Progressive memorization causes proportional inflation
- **H-C (Conditions)**: Verbatim contamination required; semantic may differ

**Status**: READY for Phase 2B verification protocol development
