# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: gap-1-cross-benchmark-correlation
- **Gap Title**: No Systematic Cross-Benchmark Correlation Study
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Truthfulness benchmarks may measure distinct failure modes, not a single trait
- Divergence patterns could be more informative than correlation strength alone
- Factor analysis can reveal latent structure of "truthfulness" as measured
- Either outcome (multi-factor or single-factor) advances the field

### Breakthrough Moments
- Exchange 1: Dr. Nova reframed the question from "do benchmarks correlate?" to "what latent structure explains divergence?"
- Exchange 4: Prof. Pax confirmed computational tractability (~400 GPU-hours)
- Exchange 7: Dr. Nova solved arbitrary threshold problem via baseline-relative comparisons
- Exchange 11: Dr. Ally synthesized final hypothesis addressing all concerns

---

## Final Hypothesis

### Title
Multi-Dimensional Truthfulness: Correlation Structure of LLM Reliability Benchmarks

### Core Claim
Under evaluation of N≥30 diverse LLMs (varied architecture, scale, training) on truthfulness benchmarks, if TruthfulQA, HaluEval, and FactScore measure partially independent reliability dimensions, then inter-benchmark correlations will be moderate (r between unrelated-benchmark baseline and 0.7) while intra-benchmark correlations remain high (r > 0.7), and factor analysis will reveal 2-3 components rather than a single factor, because these benchmarks target distinct failure modes: misconception resistance, generation coherence, and factual precision respectively.

### Mechanism
1. TruthfulQA tests resistance to popular misconceptions → requires knowledge retrieval + misconception detection
2. HaluEval tests generation coherence → requires generation control + consistency maintenance
3. FactScore tests atomic factual precision → requires fact verification + retrieval accuracy
4. Different benchmarks tap different capabilities → partial independence in performance

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | Inter-benchmark correlations will be moderate | r > baseline AND r < 0.7 | All inter-benchmark r > 0.7 |
| P2 | Intra-benchmark correlations will be high | r > 0.7 | Intra-benchmark r < 0.5 |
| P3 | Factor analysis reveals 2-3 components | No single component >80% variance | Single factor >80% variance |
| P4 | Error clustering distinguishes patterns | Different errors for different profiles | Same errors regardless |

---

## Novelty

**Key Innovation**: First empirical correlation and factor structure study for truthfulness benchmarks specifically.

**Differentiation from Prior Work**:
- BenchBench (2024): Meta-benchmark methodology → We apply to truthfulness specifically
- Ailem et al. (2024): Prompt-level correlations → We do model-level cross-benchmark correlations
- Moving Target (2026): Score drift → We do snapshot correlation structure

---

## Experimental Design

**Model Population**: N≥30 diverse models
- 10 base models (Llama, Mistral, Falcon, Phi, Qwen)
- 10 instruction-tuned variants
- 10 scaled variants (7B, 13B, 70B)

**Benchmarks**:
- TruthfulQA (MC1, MC2, Generation)
- HaluEval (QA, Summarization subsets)
- FactScore (generation + retrieval)
- MMLU, HellaSwag (controls)

**Analysis**:
- Spearman correlation matrix
- PCA with oblique rotation
- IRT models (robustness check)
- Error type clustering

**Compute**: ~400 GPU-hours total (~16 GPU-days)

---

## Limitations

- FactScore depends on retrieval quality (mitigated: fixed Wikipedia snapshot)
- Model count limits statistical power for detecting small correlations
- Results apply to decoder-only transformers only
- English-language evaluation only

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

## Phase 2B Readiness

| Sub-Hypothesis | Content |
|----------------|---------|
| SH-1 (Existence) | Moderate inter-benchmark correlations exist |
| SH-2 (Mechanism) | Different failure modes underlie different benchmarks |
| SH-3 (Comparison) | Multi-factor vs single-factor (deferred to Phase 5) |

**Status**: READY for Phase 2B verification protocol design

---

*Phase: 2A - Research Dialogue*
*Architecture: Self-Play Tikitaka Loop*
*Ready for: Phase 2B - Verification Protocol Design*
