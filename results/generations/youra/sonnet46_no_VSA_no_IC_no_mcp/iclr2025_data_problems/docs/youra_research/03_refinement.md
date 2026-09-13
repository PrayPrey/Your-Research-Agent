# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap_1
- **Gap Title**: Controlled Cross-Family Curation Comparison on Standard Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8
- **Hypothesis ID**: H-ContaminationCorrectionSignature-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met at Exchange 8 (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Within-family comparison (Pile vs dedup-Pile, same GPT-NeoX architecture) is the only clean causal design; cross-family is observational
- Deduplication produces profile **reordering**, not uniform improvement — high-contamination benchmarks may score **lower** in dedup models
- Token-count matching via Pythia's 154 intermediate checkpoints is essential to control for data volume confound (~15% fewer tokens in dedup-Pile)
- The contamination-correction framework unifies deduplication effects and contamination detection into a single mechanistic prediction

### Breakthrough Moments
- **Exchange 6 (Prof. Rex)**: Identified mechanism direction confusion (dedup → lower scores on contaminated benchmarks, not higher) and data volume confound (dedup-Pile has ~15% fewer tokens)
- **Exchange 7 (Dr. Ally)**: Corrected mechanism to profile reordering; proposed token-count matching as confound solution; precisified null hypothesis with Bonferroni correction
- **Exchange 8 (Prof. Vera)**: Formally verified all 6 convergence criteria; declared convergence

---

## Final Hypothesis

### Title
Contamination-Correction Signature of Deduplication in Pretraining Benchmark Profiles

### Core Claim
Under the setting of existing open pretrained language model families (Pythia suite) trained on corpora with and without deduplication (Pile vs dedup-Pile), **if training data deduplication removes repeated near-duplicate documents that overlap with standard benchmark test patterns, then the resulting benchmark performance profile will show a characteristic contamination-correction signature**: benchmarks with higher Pile n-gram contamination will score lower in dedup-Pile models (memorization inflation removed), while benchmarks with lower contamination will show relatively stable or improved performance, **because** deduplication selectively removes the near-memorization advantage conferred by repeated training examples that partially overlap with benchmark test content.

**Null hypothesis**: At token-count-matched checkpoints, Pythia dedup-Pile and Pile models show no statistically significant difference in few-shot performance on any of {MMLU, HellaSwag, ARC, WinoGrande} (Bonferroni-corrected α=0.0125), and per-benchmark changes show no significant correlation with estimated n-gram overlap.

### Mechanism
1. **Pile contains repeated near-duplicate documents** that partially overlap with benchmark test patterns (~15% removed by deduplication)
2. **Pile-trained models develop near-memorization** of repeated training patterns that overlap with benchmark test content → inflated scores on high-contamination benchmarks
3. **Dedup-Pile removes this advantage** → lower scores on high-contamination benchmarks, stable/improved on low-contamination benchmarks
4. **Profile reordering** (not uniform shift) is the contamination-correction signature

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|------------------|
| P1 | ✅ | Pythia dedup-Pile vs Pile at token-count-matched checkpoints shows Bonferroni-significant difference on ≥1 benchmark | p < 0.0125 on ≥1 benchmark at ≥2 model sizes |
| P2 | — | Per-benchmark accuracy differential correlates with n-gram contamination overlap | Pearson r ≥ 0.5, p < 0.05 |
| P3 | — | Dolma shows lower contamination overlap than Pile for 4 target benchmarks (exploratory) | Dolma mean contamination < Pile, p < 0.05 |

**P1 falsification**: All 4 benchmarks show p > 0.0125 → null hypothesis supported, mechanism unsupported
**P2 falsification**: r < 0.3 → contamination is not the mechanism driving the signature

---

## Novelty

**Key Innovation**: Contamination-correction signature as a mechanistic framework — predicts per-benchmark directional changes from first principles using contamination estimates, rather than reporting aggregate effects post-hoc.

**Differentiation**:
- Lee et al. 2022: report aggregate dedup improvements → we predict per-benchmark directions tied to contamination
- Biderman et al. 2023: tabulate Pile vs dedup-Pile results → we use those results to test a specific mechanistic prediction
- Shi et al. 2023: detect training data presence → we use contamination estimates to predict performance direction

---

## Experimental Design

**Models**: Pythia 160M, 410M, 1B, 6.9B — Pile and dedup-Pile variants (8 models total)

**Benchmarks**: MMLU (knowledge), HellaSwag (commonsense), ARC-Challenge (science), WinoGrande (pronoun)

**Evaluation**: lm-evaluation-harness few-shot at token-count-matched checkpoints

**Contamination estimation**: 13-gram overlap (n-gram tools) + min-k% probability (Shi et al. 2023)

**Primary comparison**: Pythia dedup-Pile vs Pile at token-count-matched checkpoints

**Secondary (exploratory)**: OLMo-1B vs Pythia-1B contamination profile comparison

**All tools are publicly available. No new training, no human annotation, no new benchmarks.**

---

## Limitations

- Architecture confound in cross-family comparison (GPT-NeoX vs OLMo architecture) — labeled exploratory
- Token-count matching is approximate given checkpoint granularity
- Only 4 benchmarks — may not generalize across all benchmark categories
- Contamination estimates are proxies (n-gram overlap), not ground truth
- Results may not generalize to instruction-tuned models or non-English benchmarks

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 8 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Token-count matching granularity (mitigated); P2 statistical power (mitigated) |
| **Phase 2B Ready** | READY |
| **Feasibility** | Fully executable with existing open-source artifacts |
