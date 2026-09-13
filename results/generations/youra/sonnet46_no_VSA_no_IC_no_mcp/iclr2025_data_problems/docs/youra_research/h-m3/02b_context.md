# Phase 2B Context: H-M3

**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Status:** READY (prerequisites h-m1 PASS, h-m2 FAILED/SHOULD_WORK — continue with warning)

## Hypothesis Statement

Under the setting of Pythia dedup-Pile vs Pile benchmark accuracy differentials at token-count-matched checkpoints, if benchmarks vary in their estimated n-gram contamination overlap with the Pile corpus, then the per-benchmark accuracy differential (dedup-Pile minus Pile) will show positive correlation with contamination overlap estimate (Pearson r ≥ 0.5), because higher contamination means greater near-memorization advantage for Pile models and thus greater accuracy drop in dedup-Pile when that advantage is removed.

## Experimental Setup (from Phase 2A)

### Dataset
- **Name:** Pile vs dedup-Pile + MMLU, HellaSwag, ARC-Challenge, WinoGrande
- **Type:** standard (programmatic-api via lm-evaluation-harness + HuggingFace)
- **Source:** EleutherAI (Pythia checkpoints); benchmark test sets via lm-evaluation-harness
- **Path:** huggingface.co/EleutherAI/pythia-*; benchmarks via lm-evaluation-harness
- **Hypothesis Fit:** Provides exact contamination estimates (from H-M1 n-gram overlap) and exact accuracy differentials (from H-E1 evaluation), enabling direct correlation test

### Model
- **Name:** Pythia (160M, 410M, 1B, 6.9B) — Pile and dedup-Pile variants
- **Type:** Decoder-only GPT-NeoX
- **Source:** EleutherAI/pythia on HuggingFace
- **Hypothesis Fit:** Open checkpoints with controlled curation comparison; H-E1/H-M1 outputs already computed

## Variables
- **Independent:** Per-benchmark n-gram contamination overlap estimate (continuous, from H-M1)
- **Dependent:** Per-benchmark accuracy differential (dedup-Pile minus Pile) at token-count-matched checkpoints
- **Controlled:** Model sizes aggregated, token-count matching protocol, contamination estimators (dual: 13-gram + min-k%)

## Verification Protocol (from Phase 2B)
1. Collect contamination estimates from H-M1 (13-gram overlap per benchmark) and H-M2 (min-k% differential per benchmark)
2. Collect accuracy differentials from H-E1 (dedup-Pile minus Pile per benchmark)
3. Compute Pearson and Spearman correlation between contamination estimate vector (4 benchmarks) and accuracy differential vector (4 benchmarks), aggregated across model sizes
4. Test significance (p < 0.05) for both correlation estimators
5. Report correlation coefficients with confidence intervals; check directionality

## Success Criteria
- Primary: Pearson r ≥ 0.5 and Spearman ρ ≥ 0.5, p < 0.05, across both contamination estimators
- Secondary: High-contamination benchmarks show negative accuracy differentials

## Dependencies
- H-E1: Accuracy differentials (VALIDATED — PASS)
- H-M1: Contamination estimates (VALIDATED — PASS)
- H-M2: Memorization confirmation (FAILED — SHOULD_WORK, continue with warning)
