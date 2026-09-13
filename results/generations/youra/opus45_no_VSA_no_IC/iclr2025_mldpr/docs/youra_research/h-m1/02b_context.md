# Phase 2B Context: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Prerequisites:** H-E1 (VALIDATED)

## Hypothesis Statement

Benchmark Fingerprint Score (classifier confidence for true benchmark) correlates positively with cross-dataset performance gap (r>0.3, p<0.05)

## Success Criteria

- Primary: Pearson correlation r > 0.3 with p < 0.05
- Falsification: r ≤ 0 or p > 0.1

## Continuation Context

Building on H-E1 validation results:
- Linear probe achieved 99.51% accuracy (far exceeding 60% threshold)
- Cohen's d = 698.08 (massive effect size)
- Confirms fingerprints are highly detectable
- H-M1 now tests whether fingerprint strength predicts generalization gap

## Experimental Setup (from Phase 2B)

**Model:** ResNet-50 pretrained on ImageNet-1K
**Fine-tuning Datasets:** CUB-200-2011, Stanford Dogs, Oxford Flowers 102, Stanford Cars, FGVC Aircraft
**Cross-dataset Evaluation:** NABirds
**Seeds:** 3 per benchmark (15 models total)

## What H-M1 Must Measure

1. **Benchmark Fingerprint Score (BFS):** Classifier confidence for true benchmark
2. **Cross-dataset Gap:** In-domain accuracy - NABirds accuracy
3. **Correlation:** Pearson r between BFS and Gap across all 15 models

## Archon Task ID

d649e6b1-e3a6-418c-9c3a-46c1d7d81929
