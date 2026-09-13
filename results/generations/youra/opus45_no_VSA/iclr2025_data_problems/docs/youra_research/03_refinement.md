# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-08T03:05:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1-curation-contamination-attribution
- **Gap Title**: Curation-Contamination Attribution Link
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC core claim, MECHANISM explained, PREDICTIONS defined, NOVELTY articulated, FEASIBILITY established, OBJECTIONS addressed

### Key Insights
- CCR provides first operational definition linking curation to contamination
- IFR tests whether influence methods are valid for contamination forensics
- Influence Gini Coefficient (IGC) may reveal contamination structure without removal intervention
- Contaminated examples may be structurally irreplaceable (lower redundancy than general high-influence examples)

### Breakthrough Moments
- Prof. Pax distinguished semantic contamination from distributional overlap (Exchange 3)
- Prof. Vera formalized the removal intervention hypothesis with dose-response (Exchange 6)
- Dr. Nova proposed IFR metric and time-stratified clean benchmark approach (Exchange 9)
- Dr. Nova extended IGC as concentration measure enabling pre-training risk prediction (Exchange 15)

---

## Final Hypothesis

### Title
Curation-Driven Contamination Amplification (CDCA)

### Core Claim
**Under** controlled experiments with matched corpora and fixed model architecture (Pythia-1B/OLMo-1B), **if** a filtering strategy (e.g., perplexity-based selection) preferentially retains examples flagged as contaminated by membership inference (Min-K%++/CDD), **then** models trained on that strategy will show:
1. Higher Contamination Contribution Ratio (CCR) than random baseline
2. Larger accuracy drops when high-CCR examples are removed
3. Positive Amplification Index diverging contaminated vs. clean benchmark performance

**Because** filtering mechanisms that favor high-information-density examples inadvertently select benchmark-related content at higher rates, and these examples are structurally less redundant than general high-influence examples.

### Mechanism
1. Filtering strategy selects high-information-density examples
2. High-density examples include disproportionate benchmark-related content
3. Model learns benchmark answers from contaminated examples during training
4. Contaminated examples have low redundancy, making influence structurally necessary

---

## Predictions

| ID | Prediction | Success Criterion | Falsifier |
|----|------------|-------------------|-----------|
| P1 | CCR higher for perplexity than random | CCR difference > 0.1, p<0.05 | No significant difference |
| P2 | Removal shows causal effect | Degradation ≥1.5× random | Within seed variance |
| P3 | AI positive for perplexity | AI > 0, 95% CI excludes zero | AI ≈ 0 after audit |
| P4 | IFR reveals structure | IFR(contam) > IFR(non-contam), ρ < -0.5 | No difference |
| P5 | Synthetic validates stack | R² ≥ 0.9, F1 > 0.8 | Non-monotonic or F1 < 0.8 |

---

## Novelty
- **Key Innovation**: Three novel metrics (CCR, IFR, IGC) enabling quantification, causal validation, and structural characterization of contamination amplification
- **Differentiation**: First work connecting data attribution methods to contamination detection in curation context; prior work addressed each component in isolation

---

## Experimental Design

| Component | Specification |
|-----------|--------------|
| Corpus | RedPajama-1B subset (fixed) |
| Strategies | Perplexity top-30%, quality classifier, random |
| Model | Pythia-1B, 5 seeds per condition |
| Attribution | TRAK/LoGra |
| Contamination | Min-K%++ + CDD dual detection |
| Benchmarks | MMLU (contaminated), time-stratified MMLU 2024+ (clean) |
| Removal | 0.01%, 0.05%, 0.1% high-CCR removal |

---

## Limitations
- Results may not generalize to instruction-tuned or RLHF models
- Per-example contamination detection has inherent false positive rates
- Influence concentration may vary by benchmark type
- Methodology validated at 1B scale first; scaling requires additional validation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase: 2A - Hypothesis Generation via Dialogue*
*Ready for: Phase 2B - Verification Protocol Design*
