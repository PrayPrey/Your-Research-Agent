# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-14
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v9.0.0
- **Gap ID**: gap-1
- **Gap Title**: Absence of Controlled Joint Analysis of Curation Hyperparameters on Both Performance and Fairness
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Pre-registered, falsifiable Path-Dependent Curation Fairness Hypothesis (PCFH) with explicit quantitative criteria: multivariate capability matching via Mahalanobis distance, conditional entropy H(occupation|demographic) mediation tests, benchmark decontamination protocol, shuffled-demographic negative control, and fastText bias diagnostic.

### Key Insights
1. Quality filtering (fastText percentile cutoff) and domain reweighting (DoReMi-style) are not fairness-neutral operations — they are implicit demographic selectors that reshape conditional probability structures in the training corpus
2. The critical mediating variable is conditional demographic association density H(occupation|demographic), not domain proportions or global token frequency
3. The DCLM benchmark infrastructure provides an unusually clean controlled experiment environment for extending performance-only ablations to joint performance+fairness measurement
4. A shuffled-demographic negative control corpus (random permutation of demographic tokens, preserving entropy, destroying conditional associations) is the critical experimental design element to isolate mechanism specificity

### Breakthrough Moments
- **Exchanges 3-4**: Prof. Rex and Prof. Pax identified that MMLU alone is insufficient for capability matching and domain-level mediation is too coarse — pivoted hypothesis from "tradeoff curve" to "causal identification problem"
- **Exchanges 8-9**: Prof. Rex's entropy compression mechanism + Dr. Nova's Curation-Entropy-Fairness Trilemma introduced conditional entropy as the precise mediator linking filtering to fairness
- **Exchange 12**: Prof. Vera's shuffled-demographic negative control formalized the experimental design to isolate conditional associative structure as causal mechanism

---

## Final Hypothesis

### Title
Path-Dependent Curation Fairness Hypothesis (PCFH)

### Hypothesis ID
H-PCFH-v1

### Core Claim
Under controlled pretraining conditions (Pythia-1B, DCLM recipe: decoder-only Transformer, LR 2e-5, batch size 256, cross-entropy loss, fixed 100B token budget), if different data curation paths (fastText quality percentile filtering vs. DoReMi-style domain reweighting) are applied to the same base corpus (Dolma/DCLM-POOL) and achieve matched downstream capability (MMLU ±1%, HellaSwag ±1%, perplexity ±0.1, ECE ≤0.5% via Mahalanobis distance criterion), then these models will produce statistically distinguishable fairness outcomes (BBQ accuracy gap Cohen's d ≥0.05, WinoBias consistency ratio divergence) that survive benchmark decontamination and are abolished in a shuffled-demographic negative control corpus, **because** different curation paths create differential conditional demographic association density H(occupation|demographic) in training corpora, which internalizes into differential model logit structures around demographic-occupation co-occurrences.

### Mechanism
Three-link causal chain:
1. **Curation → Corpus Demographics**: fastText filtering and domain reweighting alter H(occupation|demographic) in training data
2. **Corpus → Model Logits**: Cross-entropy training internalizes conditional structures; log-linear functional form (Spearman ρ > 0, p < 0.01)
3. **Model Logits → Fairness Benchmarks**: Differential logit structures produce measurable BBQ/WinoBias/StereoSet divergence that persists after capability matching and decontamination

---

## Predictions

### P1 (Primary)
**Statement**: Matched-capability models from different curation paths show BBQ accuracy gap Cohen's d ≥0.05
**Test Method**: ~10-12 Pythia-1B training runs; Mahalanobis matching; BBQ decontamination; paired t-test
**Success Criterion**: ≥1 matched pair with BBQ gap Cohen's d ≥0.05, p < 0.05, surviving decontamination
**Falsification**: All matched pairs show BBQ gap ≤0.01 after decontamination

### P2 (Secondary)
**Statement**: Corpus H(occupation|demographic) shifts ≥5% correlate with model logit margins (Spearman ρ > 0, p < 0.01)
**Test Method**: Corpus entropy audit + logit margin measurement; Spearman correlation
**Success Criterion**: Spearman ρ > 0, p < 0.01; shuffled-demographic control shows ≤0.01 logit margin change
**Falsification**: Spearman ρ ≈ 0 (p > 0.05), or shuffled-demographic control produces same logit margins as filtered corpus

### P3 (Diagnostic)
**Statement**: fastText quality scores are correlated with demographic features (R² > 0.05)
**Test Method**: OLS regression of fastText scores on demographic token features in 10M-document DCLM-POOL sample
**Success Criterion**: R² > 0.05 with p < 0.01 on ≥1 demographic feature
**Note**: This is a diagnostic — either outcome (R² high or low) is informative for mechanism interpretation

---

## Novelty
- **Primary**: First controlled experiment jointly measuring pretraining data curation effects on both performance AND fairness benchmarks from matched-capability model checkpoints
- **Key Differentiation**: DCLM/FineWeb/DoReMi all optimize for single-axis performance signals; this work adds the fairness axis with causal identification (not just correlation)
- **Theoretical Contribution**: Curation path effects on fairness are mediated by conditional demographic association density, not merely global token frequency or domain proportions

---

## Experimental Design

| Component | Choice | Justification |
|-----------|--------|---------------|
| **Model** | Pythia-1B (~10-12 runs) | Controlled pretraining, tractable scale, documented procedures |
| **Dataset** | Dolma/DCLM-POOL | Modular corpora, DCLM filtering infrastructure available |
| **Curation paths** | fastText 10%-90% + DoReMi | Contrast support-contraction vs. gradient-reweighting |
| **Capability matching** | Mahalanobis(MMLU, HellaSwag, ppl, ECE) | Multi-metric, pre-registered |
| **Fairness benchmarks** | BBQ (primary), WinoBias, StereoSet | Multi-dimensional fairness coverage |
| **Negative control** | Shuffled-demographic corpus | Isolates conditional structure as mechanism |

---

## Limitations
- English-language corpora only (Dolma); does not generalize to multilingual settings
- Pythia-1B at 100B tokens may not be sufficient scale for fairness effects to be clearly detectable
- BBQ/WinoBias/StereoSet capture US-centric demographic categories
- fastText classifier bias (demographic prior encoding) is a potential confound requiring diagnostic

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Pre-registered falsifiable PCFH with all major objections addressed |
| **Clarity Verified** | Yes |
| **Remaining Pre-Conditions** | fastText bias diagnostic + shuffled-demographic negative control design (Phase A) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
