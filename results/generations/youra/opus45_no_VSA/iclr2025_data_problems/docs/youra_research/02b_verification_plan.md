# Phase 2B Verification Plan

**Main Hypothesis**: H-CDCA-v1 (Curation-Driven Contamination Amplification)
**Generated**: 2026-08-08
**Archon Project ID**: 1ae32675-caca-4ddf-a09d-b405b9efc978

## Executive Summary

This verification plan decomposes the CDCA hypothesis into 5 sub-hypotheses following the causal mechanism chain. The plan prioritizes **calibration first** (H-E1) to validate the metric stack before measuring strategy effects.

## Sub-Hypotheses

### H-E1: Synthetic Injection Calibration (MUST_WORK)
- **Statement**: Synthetic benchmark injection produces monotonic CCR scaling and validates detector precision
- **Prediction**: P5 - CCR scales monotonically with injection rate (R² ≥ 0.9); F1 > 0.8 at 0.1% injection
- **Falsification**: Non-monotonic scaling, saturation before 0.1%, or F1 < 0.8
- **Prerequisites**: None
- **Archon Task ID**: c352e49b-991a-4e7a-bfcd-cf4d04612f45

### H-M1: CCR Variation by Filtering Strategy (MUST_WORK)
- **Statement**: Perplexity filtering produces higher CCR than random sampling
- **Prediction**: P1 - CCR(perplexity) - CCR(random) > 0.1, p<0.05 under bootstrap
- **Falsification**: No significant CCR difference across strategies after controlling for confounds
- **Prerequisites**: H-E1
- **Archon Task ID**: 1db87e9d-95f3-4698-b360-6caeebb39756

### H-M2: Removal Intervention Causality (MUST_WORK)
- **Statement**: Removing high-CCR examples causes larger accuracy drop than random removal
- **Prediction**: P2 - Degradation from high-CCR removal ≥1.5× random removal, 95% CI excludes zero and random mean
- **Falsification**: Degradation ≤ random removal or within seed variance band
- **Prerequisites**: H-M1
- **Archon Task ID**: e6187af1-4954-47af-9172-2c5d9ad32a2c

### H-M3: Amplification Index Validation (SHOULD_WORK)
- **Statement**: Amplification Index is positive for perplexity filtering vs random
- **Prediction**: P3 - AI > 0 for perplexity vs. random, 95% CI excludes zero
- **Falsification**: AI ≈ 0 after overlap audit, or contaminated/clean performance track proportionally
- **Prerequisites**: H-M1
- **Archon Task ID**: 2bc8f4eb-c87e-479c-b184-ea518b25dc3b

### H-C1: IFR Sign Reversal and Redundancy (SHOULD_WORK)
- **Statement**: Contaminated high-influence examples have higher IFR than non-contaminated
- **Prediction**: P4 - IFR(contaminated) > IFR(non-contaminated) at p<0.05; ρ(IFR, redundancy) < -0.5
- **Falsification**: No IFR difference or no redundancy correlation
- **Prerequisites**: H-M2
- **Archon Task ID**: b712f568-3616-4290-adf1-3d7137a78226

## Dependency Graph

```
H-E1 ─────→ H-M1 ─────→ H-M2 ─────→ H-C1
              │
              └────────→ H-M3
```

**Critical Path**: H-E1 → H-M1 → H-M2 (all MUST_WORK)

## Risk Analysis

| ID | Hypothesis | Risk | Likelihood | Impact | Mitigation |
|----|------------|------|------------|--------|------------|
| R1 | H-E1 | CCR saturates before 0.1% injection | Medium | High | Extend injection range to 0.2%; use log-scale |
| R2 | H-M1 | CCR difference < 0.1 threshold | Medium | High | Adjust threshold based on H-E1 calibration variance |
| R3 | H-M2 | Removal effects within seed variance | Medium | High | Increase removal levels to 0.5%; use paired tests |
| R4 | H-M3 | Time-stratified MMLU fails overlap audit | Low | Medium | Prepare synthetic clean benchmark as fallback |
| R5 | H-C1 | Influence concentration below detectability | Medium | Low | Pre-compute Gini coefficient; skip if < 0.3 |

## Timeline (Gantt)

```
Week:        1    2    3    4    5    6    7    8    9
H-E1:       [====----]
H-M1:            [====--------====]
H-M2:                              [====----]
H-M3:                              [====]
H-C1:                                        [====]
```

**Total Estimated Duration**: 9 weeks
- H-E1: Weeks 1-2 (corpus prep, injection, metrics)
- H-M1: Weeks 2-5 (15 training runs + TRAK attribution)
- H-M2: Weeks 5-7 (removal + retraining)
- H-M3: Weeks 5-6 (benchmark comparison, parallel with H-M2)
- H-C1: Weeks 7-8 (IFR computation)

## Dialectical Analysis

### Thesis
Filtering strategies that select high-information-density examples inadvertently amplify benchmark contamination, quantifiable via CCR.

### Antithesis
- CCR differences may reflect general quality improvement, not contamination-specific amplification
- Attribution scores at 1B scale may be too noisy to distinguish contamination effects
- Removal intervention may conflate contamination with legitimate memorization

### Synthesis
The experimental design addresses each concern:
1. **Quality vs contamination**: Matched corpus isolates filtering effect; Amplification Index (H-M3) separates contaminated from clean benchmark performance
2. **Attribution noise**: Synthetic calibration (H-E1) validates TRAK precision before main experiments; 5 seeds with bootstrap tests
3. **Memorization conflation**: IFR/redundancy analysis (H-C1) distinguishes structurally necessary (contamination) from replaceable (memorization) influence

## Experimental Scale

| Hypothesis | Training Runs | Evaluation Samples | GPU Hours (est.) |
|------------|---------------|-------------------|------------------|
| H-E1 | 4 (injection levels) | Full MMLU (14,042) | 40 |
| H-M1 | 15 (3 strategies × 5 seeds) | Full MMLU (14,042) | 150 |
| H-M2 | 15 (3 removal × 5 seeds) | Full MMLU (14,042) | 150 |
| H-M3 | 0 (reuses H-M1 models) | MMLU + MMLU-2024 (28,084) | 10 |
| H-C1 | 0 (reuses H-M2 data) | Top 1% attribution (~10,000) | 20 |

**Total**: 34 training runs, ~370 GPU hours on A100

## Gate Logic

```
IF H-E1.FAIL → STOP (metric stack invalid)
IF H-M1.FAIL → STOP (no strategy effect)
IF H-M2.FAIL → STOP (no causal evidence)
IF H-M3.FAIL → CONTINUE (optional enhancement)
IF H-C1.FAIL → CONTINUE (optional characterization)
```

## Next Steps

1. **Phase 2C**: Generate detailed experiment design for H-E1
2. **Phase 3**: Create implementation plan with Archon task breakdown
3. **Phase 4**: Execute PoC validation for each sub-hypothesis in order
