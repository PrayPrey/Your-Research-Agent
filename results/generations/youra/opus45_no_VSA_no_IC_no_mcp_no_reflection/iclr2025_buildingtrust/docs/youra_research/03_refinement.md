# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00Z
- **Workflow**: phase2a-dialogue (Self-Play Mode)
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: Gap1
- **Gap Title**: No Controlled Comparison Under Matched Computational Budget
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Semantic entropy and self-consistency target different failure modes despite both using sampling
- Benchmark characteristics serve as proxies for hallucination type distributions, avoiding need for annotation
- NLI overhead for semantic entropy should be reported as a finding, not eliminated as a confound

### Breakthrough Moments
- Exchange 7: Dr. Nova's insight to use benchmark as moderation proxy instead of requiring hallucination type annotation
- Exchange 8: Prof. Vera's precise operationalization of three testable predictions with clear success/failure criteria

---

## Final Hypothesis

### Title
Matched-Budget Comparison of Uncertainty-Based Hallucination Detection Methods

### Hypothesis ID
H-BudgetMatchedUQ-v1

### Core Claim
Under matched generation budgets (N samples), if semantic entropy and self-consistency methods are applied to the same hallucination detection task, then they will show different precision-recall tradeoffs with the pattern varying by benchmark, because semantic entropy captures semantic clustering of errors while self-consistency captures surface-level output inconsistency.

### Mechanism
1. Model generates N responses to each query under sampling (temperature > 0)
2. Semantic entropy clusters responses by semantic equivalence via bidirectional NLI, then computes entropy over clusters
3. Self-consistency measures surface-level agreement (e.g., BERTScore, n-gram overlap) without semantic grouping

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Methods show statistically different AUROC on at least one benchmark | p < 0.05 (Bonferroni-corrected) | p >= 0.05 on all benchmarks |
| P2 | Method × benchmark interaction exists | Significant interaction (p < 0.05) | No significant interaction |
| P3 | Both methods outperform calibration at N >= 10 | Both AUROC > baseline (p < 0.05) | Baseline matches or exceeds either |

---

## Novelty

**Key Innovation**: First controlled head-to-head comparison of semantic entropy vs self-consistency under matched computational budgets.

**Differentiation**: Prior work evaluates each method in isolation on different benchmarks with different sample counts. This study provides the first apples-to-apples comparison.

---

## Experimental Design

| Component | Selection | Rationale |
|-----------|-----------|-----------|
| Models | Llama-3-8B-Instruct, Mistral-7B-Instruct | Open-weight, sampling-capable, known to hallucinate |
| Benchmarks | TruthfulQA, HaluEval-QA, HaluEval-Summarization | Existing labels, different hallucination contexts |
| Sample counts | N = 5, 10, 20 | Spans typical range from prior work |
| Baselines | Contextual Calibration, Raw Confidence | Standard calibration approach |

---

## Limitations

- Comparison limited to two open-weight model families
- Does not address latency constraints in production settings
- NLI overhead for semantic entropy not parallelized in baseline implementation
- Effect sizes may be small if methods are more similar than hypothesized

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Full convergence after 10 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed with mitigation strategies) |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Both methods detect hallucinations with AUROC > 0.5
- **SH2 (Mechanism)**: Semantic clustering vs surface consistency capture different error patterns
- **SH3 (Comparison)**: Deferred to Phase 5 for baseline comparison

**Status**: READY for Phase 2B
