# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play Mode)
- **Gap ID**: Gap-1
- **Gap Title**: Causal Link Between Curation Strategy and Benchmark Score
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 personas approved hypothesis after refinement cycle

### Key Insights
- Dose-response framing (borrowed from pharmacology) provides rigorous experimental design
- Cross-scale transfer should be TESTED not ASSUMED (demoted from core claim to testable prediction)
- Fixed-token design is cleaner than efficiency normalization for confound control
- Benchmark ensemble (HellaSwag, ARC-Easy, PIQA, WinoGrande) reduces noise while measuring general reasoning

### Breakthrough Moments
- **Exchange 5**: Dr. Ally proposed benchmark ensemble to address Prof. Pax's noise concerns
- **Exchange 6-7**: Prof. Rex's critique led to demoting cross-scale transfer to testable hypothesis (P3)
- **Exchange 8**: Prof. Vera formalized experimental protocol with clear falsification criteria

---

## Final Hypothesis

### Title
Curation Parameter Dose-Response (H-CPDR)

### Hypothesis ID
H-CPDR-v1

### Core Claim
Under LLM pretraining on English web text corpora, if data curation parameters (perplexity filtering threshold, deduplication stringency) are systematically varied in controlled ablation, then quantifiable dose-response relationships with downstream benchmark performance will emerge, because there exists an optimal balance between data quality (strict filtering) and data diversity (permissive filtering).

### Mechanism
1. Low perplexity thresholds include noisy/irrelevant data that dilutes learning signal
2. High perplexity thresholds exclude too much data, reducing coverage and diversity
3. An optimal range exists that balances quality and diversity
4. This optimal range can be determined empirically through systematic sweep

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | At least one curation parameter shows non-monotonic dose-response with measurable peak | Quadratic model selected over linear via AIC/BIC | R² > 0.9 for monotonic fit |
| **P2** (Primary) | CPDR-optimized parameters outperform RedPajama defaults by >1% | Mean difference > 1%, p < 0.05 | No config beats RedPajama by >1% |
| **P3** (Secondary) | Optimal values at 125M scale transfer within ±20% to 1B scale | Optima within ±2 percentile points | Optima differ by >20% |

---

## Novelty

**Key Innovation**: First controlled dose-response study for LLM curation parameters with proper confound control (fixed-token design)

**Differentiation from Prior Work**:
- DataComp: Focused on vision; this extends to LLM pretraining
- How to Train Data-Efficient LLMs (arXiv:2402.09668): Varied multiple factors; this isolates each parameter
- RedPajama, Dolma: Report configurations without systematic ablation

---

## Experimental Design

### Dataset
RedPajama-v2 (English web text subset)

### Models
- GPT-2 125M (full sweep)
- GPT-2 350M (validation)
- GPT-2 1B (validation)

### Parameters
- **Perplexity Threshold**: 10 levels (none, p10, p20...p90)
- **Deduplication**: 5 levels (none, fuzzy_0.7, fuzzy_0.85, exact, exact+fuzzy)
- **Seeds**: 3 per configuration

### Baselines
1. No filtering (raw corpus)
2. RedPajama defaults
3. CPDR-optimized

### Controls
- Fixed 10B tokens per configuration
- Fixed hyperparameters
- Min-K%++ contamination verification

---

## Limitations

- **Scope**: English web text only; results may not transfer to code, multilingual, or specialized domains
- **Scale**: Primary sweep at 125M; cross-scale transfer (→7B+) remains to be fully validated
- **Parameters**: Focuses on perplexity and deduplication; interaction effects and other parameters (domain mixing, quality classifiers) are future work
- **Corpus**: Uses RedPajama-v2; results may vary with other corpora (Dolma, C4)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas approved |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (blocking) |

---

## Phase 2B Readiness

| Criterion | Status |
|-----------|--------|
| Core hypothesis defined | ✅ |
| Testable predictions specified | ✅ (3 predictions with falsification criteria) |
| Experimental setup outlined | ✅ |
| Baselines identified | ✅ |
| Confound controls specified | ✅ |
| Novelty justified | ✅ |
| Scope bounded | ✅ |

**Status**: READY for Phase 2B experimental design
