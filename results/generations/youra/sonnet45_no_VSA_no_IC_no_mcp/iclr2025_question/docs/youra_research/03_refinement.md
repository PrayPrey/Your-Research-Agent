# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: Systematic Methodology for Feasibility-First Research Design
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC claim (Pilot-Driven Viability Gates), MECHANISM (incremental empirical validation with Bayesian updates), PREDICTIONS (P1-P3 with measurable success criteria), NOVELTY (first formalized feasibility-first framework), FEASIBILITY (implementable with existing tools), OBJECTIONS (Prof. Rex's critiques addressed with mitigation strategies)

### Key Insights
- **Paradigm shift**: Feasibility-first research design (constraints → questions) vs. traditional hypothesis-first (questions → constraints)
- **Dual feasibility layers**: Scientific feasibility (Can we test it?) vs. deployment feasibility (Can we deploy it?). h-e1 passed the former, failed the latter.
- **Viability as incremental search**: Treat feasibility assessment as Bayesian search problem with viability gates at each scale (10 → 100 → full samples), not one-shot prediction

### Breakthrough Moments
- **Exchange 7 (Dr. Nova)**: Proposed concrete Pilot-Driven Viability Gates mechanism with three stages (Gate 0: Resource Inventory, Gate 1: 10-sample micro-pilot, Gate 2: 100-sample PoC, Gate 3: Full validation)
- **Exchange 8 (Prof. Vera)**: Operationalized P1 with precise accuracy metric (TP+TN/Total >80% vs. 50% null) and retrospective validation protocol using 30 past hypotheses from Papers with Code

---

## Final Hypothesis

### Title
Pilot-Driven Viability Gates for Early Identification of Non-Viable ML Hypotheses

### Hypothesis ID
H-PilotGates-v1

### Core Claim
Under ML research contexts where computational overhead thresholds exist (e.g., <10% for deployment), if researchers apply Pilot-Driven Viability Gates (incremental empirical validation at 10-sample, 100-sample, full-dataset scales), then non-viable hypotheses (overhead >threshold) will be identified at the micro-pilot stage (Gate 1, 10 samples, <1 hour) with >80% accuracy, because overhead scales predictably from micro-pilot to full implementation, and Bayesian updates refine predictions incrementally.

### Mechanism
**Three-stage incremental empirical validation:**

1. **Gate 1 (Micro-Pilot, 10 samples, <1 hour)**: Measure overhead O_10, extrapolate to full-scale O_full using scaling factor k. Decision: STOP if predicted O_full > user threshold, CONTINUE otherwise.

2. **Gate 2 (Proof-of-Concept, 100 samples)**: Measure O_100, apply Bayesian update combining Gate 1 prior P(O_full | O_10) with Gate 2 likelihood P(O_100 | O_full). Refine posterior prediction. Decision: STOP if still >threshold, CONTINUE to full validation.

3. **Gate 3 (Full Validation, complete dataset)**: Run full hypothesis test, report actual overhead and experimental results.

**Why h-e1 would have been caught**: h-e1 layer-wise logit extraction showed 68.65% overhead at full scale. A 10-sample micro-pilot would show ~60% overhead, triggering STOP at Gate 1 (threshold: 10%). This would save the day-long full implementation effort.

---

## Predictions

### P1 (Primary): Gate 1 Accuracy
**Statement**: Gate 1 micro-pilot (10 samples, <1 hour) identifies non-viable hypotheses (overhead >threshold) with >80% accuracy compared to full-scale ground truth.

**Test Method**: Retrospective validation using 30 past ML projects with published micro-pilot and full-scale overhead data. Apply Gate 1 prediction to micro-pilot results, compare to actual full overhead. Measure accuracy = (TP + TN) / 30.

**Success Criterion**: Accuracy >80% (24/30 correct predictions). Null hypothesis: 50% (random guessing). Statistical test: binomial test, p <0.05.

**Falsification**: If accuracy ≤60% across 20+ hypotheses, framework fails to beat random + small margin.

### P2: Filtering Rate
**Statement**: 60%+ of non-viable hypotheses (overhead >threshold) are filtered at Gate 1 (<1 hour investment) before reaching day-long full implementations.

**Test Method**: Track viability decisions across retrospective validation set. Count hypotheses stopped at Gate 1 vs. continuing to Gate 2/3. Measure filtering rate = (Stopped at G1) / (Total non-viable).

**Success Criterion**: Filtering rate ≥60%. If 10 non-viable hypotheses, ≥6 should stop at Gate 1.

**Falsification**: If <40% stop at Gate 1, framework provides minimal time savings.

### P3: Bayesian Update Accuracy Gain
**Statement**: Bayesian overhead updates between Gate 1 (10 samples) and Gate 2 (100 samples) reduce prediction error by >40% compared to Gate 1 alone.

**Test Method**: For hypotheses reaching Gate 2, compute prediction error at G1 and G2 after Bayesian update. Measure error reduction: (Error_G1 - Error_G2) / Error_G1.

**Success Criterion**: Mean error reduction >40% across ≥10 hypotheses. Paired t-test, p <0.05.

**Falsification**: If error reduction <20%, Bayesian updates add complexity without meaningful gain.

---

## Novelty

### What's New
First formalized feasibility-first framework in ML research methodology treating viability assessment as **incremental empirical validation** with Bayesian updates, rather than:
- One-shot constraint checking (hypothesis proposed → check resources → accept/reject)
- Post-hoc discovery (like h-e1: implement fully, then discover overhead issue)

### Differentiation from Prior Work

| Prior Work | Difference |
|------------|------------|
| Ablation studies | Test hypothesis VARIATIONS, not viability GATES. No formalized stop/continue decision |
| Hyperparameter early stopping | Optimizes hyperparams for accuracy, not feasibility. Different objective. |
| Complexity analysis (Big-O) | Theoretical, doesn't account for constant factors. h-e1 was O(n) but had 68.65% overhead constant |
| h-e1 post-hoc discovery | Discovered overhead AFTER full implementation. Framework discovers at micro-pilot BEFORE committing |

### Key Innovation
**Pilot-Driven Viability Gates with Bayesian updates**: Structured search through sample scales (10 → 100 → full) with probabilistic prediction refinement. Combines software engineering gating (fail-fast) with Bayesian inference (uncertainty reduction).

---

## Experimental Design

### Dataset
**Retrospective ML Projects Corpus**: 30 past ML hypotheses from Papers with Code leaderboards + conference papers (NeurIPS, ICML, ICLR) with published micro-pilot (10-sample) and full-scale overhead data. Stratified: 10 low-overhead (<20%), 10 mid (20-80%), 10 high (>80%).

**Fallback**: If <20 hypotheses available, run prospective validation with NEW hypotheses.

### Model
**Bayesian Overhead Predictor**: Statistical model (scipy.stats Gaussian priors/likelihoods). Takes O_10 as prior mean, updates with O_100 as likelihood, outputs posterior P(O_full).

### Baselines
1. **Random Guessing**: 50% accuracy (coin flip for viable/non-viable)
2. **Full Implementation First**: Current practice. 100% accuracy eventually (ground truth), but requires full time investment.
3. **Expert Intuition**: Researcher predicts viability without empirical micro-pilot. Estimated ~60-70% accuracy (h-e1 anecdote).

### Success Criteria
- P1: Accuracy >80% (vs. 50% null, binomial test p <0.05)
- P2: Filtering rate ≥60%
- P3: Error reduction >40% (paired t-test p <0.05)

---

## Limitations

### Known Constraints
1. **Scaling factor k variability**: May vary by hypothesis type (attention mechanisms vs. gradient methods). Framework may need type-specific calibration.
2. **Non-linear scaling**: Assumes overhead scales predictably. Memory bottlenecks or I/O bounds at 100 samples that don't appear at 10 could break predictions.
3. **Retrospective data availability**: Requires papers reporting micro-pilot data. If <20 available, statistical power drops.

### Scope Boundaries
- **Applies to**: ML hypotheses where overhead is critical constraint (real-time systems, resource-limited deployment), existing benchmarks exist, overhead measurable on small samples
- **Does NOT apply to**: Hypotheses where overhead irrelevant (unlimited compute), hypotheses requiring new datasets/human annotation, non-scalable operations (combinatorial search)

### Mitigation Strategies (Prof. Rex)
1. If <20 papers with micro-pilot data → run prospective validation with new hypotheses
2. Learn hypothesis-type-specific scaling factors (k_attention, k_gradient, etc.)
3. Add memory profiling at each gate to catch non-linear resource constraints

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (Prof. Rex concerns mitigated) |

---

## Phase 2B Readiness

**Status**: READY

**SH1 (Existence)**: Retrospective ML Projects Corpus must exist with ≥30 hypotheses. If Papers with Code insufficient, prospective validation alternative exists.

**SH2 (Mechanism)**: Core mechanism testable by correlating O_10 vs. O_full. If r >0.7, predictive scaling validated.

**SH3 (Comparison)**: Framework accuracy vs. baselines (random 50%, expert ~60-70%). Statistical tests: binomial (P1), paired t-test (P3).

**Open Questions**:
- Optimal micro-pilot sample size? (10 chosen heuristically, may need calibration)
- How to handle non-linear scaling? (May need memory profiling)
- Can scaling factor k be learned from data, or per-hypothesis tuning?

---

*Phase 2A Complete — Ready for Phase 2B Planning*
