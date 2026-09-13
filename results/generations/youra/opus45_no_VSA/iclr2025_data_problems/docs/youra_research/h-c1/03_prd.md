# Product Requirements Document: H-C1

**Date:** 2026-08-08
**Hypothesis:** IFR(contaminated) > IFR(non-contaminated) at p<0.05 and IFR correlates negatively with redundancy (ρ < -0.5)
**Type:** CONDITION
**Gate:** SHOULD_WORK

---

## Overview

H-C1 tests the mechanistic explanation for H-M2's findings. H-M2 validated that high-CCR examples cause disproportionate accuracy drops when removed (degradation ratio 1.969). H-C1 investigates *why* through Influence Fragility Ratio (IFR) — contaminated examples should have higher IFR because they cannot be substituted by similar training examples.

## Objectives

1. Compute IFR for top 1% attribution examples from H-M2
2. Compare IFR between contaminated and non-contaminated examples
3. Measure IFR-redundancy correlation

## Success Criteria

| Metric | Gate Threshold | Measurement |
|--------|---------------|-------------|
| IFR Difference | IFR(contaminated) > IFR(non-contaminated) | Mann-Whitney U, p<0.05 |
| IFR-Redundancy Correlation | ρ < -0.5 | Spearman correlation |

## Data Requirements

### Input Data (from H-M1/H-M2)
- TRAK attribution scores: `h-m2/trak_attribution_scores.npy`
- CCR scores: `h-m1/ccr_scores.npy`
- Pythia-1B checkpoint: `h-m2/checkpoint-final`

### Analysis Set
- Top 1% by absolute TRAK score (~10,000 examples)
- Split by CCR median into contaminated/non-contaminated

### Evaluation Set
- MMLU (14,042 samples) for consistency with H-M2

## Computational Requirements

- GPU Hours: 20
- Memory: 4GB (model) + 1GB (embeddings/indices)
- Storage: ~5GB

## Deliverables

1. `h-c1/experiment.py` — Main experiment script
2. `h-c1/ifr_computer.py` — IFR computation module
3. `h-c1/figures/` — Required visualizations
4. `h-c1/04_validation.md` — Results report

## Dependencies

- H-M2 outputs (TRAK scores, trained model)
- H-M1 outputs (CCR scores)
- PyTorch, transformers, scikit-learn, scipy

## Risks

| Risk | Mitigation |
|------|-----------|
| H-M2 artifacts missing | Simulate with synthetic data for PoC |
| IFR definition ambiguity | Use normalized influence/redundancy ratio |
| Correlation threshold arbitrary | Report full correlation with CI |

---

*Phase 3 Step 01: PRD Generation Complete*
