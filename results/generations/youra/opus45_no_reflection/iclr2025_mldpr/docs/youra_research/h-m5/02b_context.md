# Phase 2B Context: H-M5 (Modality Divergence)

**Generated:** 2026-08-18
**Source:** 02b_verification_plan.md (JIT extraction)

## Hypothesis Information

- **ID:** H-M5
- **Type:** MECHANISM
- **Title:** Modality Divergence (Phase Transition Effect)
- **Statement:** Post-2021 Pearson correlation between CV and NLP Gini series drops below 0.4 from pre-2020 baseline of >0.6

**Rationale:** This is the key test of phase transition: unified concentration dynamics should fragment into modality-specific patterns.

## Variables

- **IV:** Modality (text, image, tabular, multimodal)
- **DV:** Rolling-window Pearson correlation between modality Gini series
- **CV:** Window size, temporal alignment

## Verification Protocol

1. Compute monthly Gini per modality (text, image, tabular, multimodal)
2. Calculate rolling-window Pearson correlations (6-month window)
3. Compare pre-2020 vs post-2021 correlation distributions
4. Apply Fisher z-test for significance

## Success Criteria (PoC: Direction-based)

- **Primary:** Pre-2020 r > 0.6; Post-2021 r < 0.4
- **Secondary:** Fisher z-test significant at α=0.05

## Failure Response

- IF fails: PIVOT to testing whether divergence is domain-pair specific (CV-NLP vs others)

## Gate Condition

- **Type:** SHOULD_WORK
- **Pass Condition:** Correlation drop >0.6 to <0.4
- **Fail Action:** Pivot to domain-pair analysis

## Prerequisites

- H-M4 (Traditional Benchmark Persistence with Reduced Dominance) - COMPLETED, PASS

## Previous Hypothesis Results

### H-M4 Validation Results
- **Status:** COMPLETED, PASS
- **Metrics:**
  - Traditional share: 11.70%
  - Emergent share: 4.01%
  - Traditional papers: 47,068
  - Emergent papers: 16,120
  - Dominance shift: 0.34
  - Chi-square: 16447.83, p-value: 0.0
- **Insight:** Traditional benchmarks persist with reduced dominance, confirming ecosystem fragmentation

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Historical Data | Contains task-dataset-metric triplets with modality classification |
| **Model** | Statistical Analysis Pipeline | Pearson correlation, Fisher z-test, rolling windows |

## Risks Affecting This Hypothesis

- **R1:** PWC data incomplete (High) - Mitigation: Semantic Scholar supplementation
- **R3:** Modality misclassification (Medium) - Mitigation: Manual audit sample
- **R5:** Volume confound inseparable (High) - Mitigation: Dual reporting (raw + normalized)
