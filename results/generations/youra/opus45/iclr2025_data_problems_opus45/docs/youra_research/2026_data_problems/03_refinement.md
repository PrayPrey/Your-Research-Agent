# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-24T16:26:00+00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1-pareto-frontier
- **Gap Title**: Systematic Pareto Frontier Characterization Across Methods
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met - formulated precise, falsifiable hypothesis with formal metrics, dominance criteria, convex vs. deep control tests, and mechanistic predictions

### Key Insights
- Multi-objective framing reframes attribution from "which method is best" to "best for what"
- Convex baseline provides falsification backbone - if coupling fails there, hypothesis is ill-posed
- Stability inflation ratio distinguishes estimator variance from target stochasticity
- Decision-level impact test ensures practical relevance, not just statistical significance

### Breakthrough Moments
- **Exchange 5 (Dr. Ally)**: Reframing as "practical finite-compute heterogeneity" not asymptotic impossibility
- **Exchange 8 (Prof. Rex)**: Demanding variance-as-signal be normalized by sigma_LOO
- **Exchange 10 (Prof. Pax)**: Single-error-axis regression test as mechanistic falsification

---

## Final Hypothesis

### Title
Multi-Objective Pareto Trade-offs in Finite-Compute Data Attribution

### Core Claim
Under finite-compute constraints (<=100 gradient-equivalent operations), if we compare multiple data attribution methods (TRAK, TracIn, IF, FastIF) across standardized quality dimensions, then non-degenerate Pareto trade-offs emerge across rank preservation, magnitude fidelity, and normalized stability, because non-convex deep learning geometry creates structural metric decoupling that does not exist in convex settings.

### Mechanism
1. In convex settings, all attribution metrics are monotone functions of a single approximation error norm
2. In non-convex deep networks, the loss landscape geometry creates multiple paths to approximate influence
3. Different method designs (random projection vs HVP iteration) inherently prioritize different quality dimensions
4. This creates irreducible trade-offs that persist even as compute increases

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | In convex settings, cross-metric partial correlations >= 0.95 at all compute levels | corr(rho_r, rho_m \| b) >= 0.95 | If < 0.90, metrics definitionally inconsistent |
| **P2** | In deep networks, at least one method pair shows metric crossings with non-overlapping 95% CIs | >=1 pair with CI-separated crossings | If no crossings or universal dominance |
| **P3** | R^2 from single-axis regression drops from ~1.0 (convex) to <0.8 (deep) | R^2_convex >= 0.95, R^2_deep < 0.80 | If R^2 remains >= 0.95 in deep |
| **P4** | Top-k disagreement >30% with significant downstream accuracy differences | Jaccard < 0.70, p < 0.05 | If Jaccard >= 0.90 or p >= 0.05 |

---

## Novelty

**Key Innovation**: First rigorous multi-objective Pareto characterization of data attribution methods connecting method design choices (random projections vs. HVP) to downstream use case requirements (debugging vs. valuation vs. auditing).

**Differentiation from Prior Work**:
- **TRAK (Park et al. 2023)**: Reports single-metric (LDS); we characterize multi-metric Pareto structure
- **Basu et al. (2020)**: Shows when IF fails; we characterize trade-offs across methods at fixed compute
- **DataInf (Kwon et al. 2023)**: Optimizes for LoRA efficiency; we compare all methods under unified framework

---

## Experimental Design

### Datasets
- **CIFAR-10** (Track A - Vision)
- **MNLI** (Track A - NLP)

### Models
- **Logistic Regression** (Convex baseline)
- **ResNet-18** (Deep vision)
- **BERT-base** (Deep NLP)

### Attribution Methods
- Exact Influence Functions (gold standard)
- TRAK (random projection)
- TracIn (gradient similarity)
- FastIF (approximate HVP)

### Compute Range
- 10, 25, 50, 75, 100 gradient-equivalent operations

### Ground Truth
- 1000 stratified examples x 10 retrains for sigma_LOO estimation

---

## Limitations

- **Scale**: Results may not transfer to FM scale (7B+ params) where LOO is infeasible
- **Method scope**: Excludes Data Shapley and non-gradient-based methods
- **Ground truth cost**: 10,000 training runs required for sigma_LOO estimation
- **LoRA caveat**: Track B may show metric recoupling due to low-rank parameterization

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

## Persona Verdicts Summary

| Persona | Dimension | Verdict |
|---------|-----------|---------|
| Dr. Nova | Novelty | STRONG |
| Prof. Vera | Falsifiability | STRONG |
| Dr. Sage | Significance | STRONG |
| Prof. Pax | Feasibility | STRONG |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Ready for Phase 2B: Research Planning*
