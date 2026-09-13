# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: GAP-1
- **Gap Title**: No Quantitative Measurement of Benchmark Dataset Concentration
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 18

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 18

**Convergence Reason**: All 6 convergence criteria satisfied at Exchange 18

### Key Insights

1. HHI (Herfindahl-Hirschman Index) from economics provides a ready-to-use concentration metric for benchmark usage
2. Epistemic lock-in theory explains WHY concentration matters: it reduces evaluation diversity and prevents discovery of benchmark-specific overfitting
3. Papers With Code provides the necessary data at scale (80%+ coverage for major venues)
4. Lagged panel regression design enables causal interpretation beyond correlation

### Breakthrough Moments

- **Exchange 8-9**: Pivoted from H1 (OOD gaps, infeasible) to H2 (evaluation diversity, feasible)
- **Exchange 13-14**: Within-venue longitudinal design solved the intervention definition problem
- **Exchange 15**: Confirmed Papers With Code data availability at 15K+ papers

---

## Final Hypothesis

### Title
Benchmark Concentration and Epistemic Lock-in in ML Research

### Core Claim
Under conditions of high benchmark dataset concentration (HHI > venue median) in major ML venues (NeurIPS, ICML, ICLR), if HHI increases year-over-year, then evaluation diversity (normalized entropy) decreases in the subsequent year, because researchers collectively optimize for established benchmarks and reduce exploration of alternative evaluation paths.

### Mechanism
1. High HHI indicates community convergence on few datasets
2. Convergence creates implicit standards for "acceptable" evaluation
3. New papers follow existing standards to ensure comparability
4. Reduced diversity prevents discovery of benchmark-specific overfitting
5. The cycle reinforces itself (positive feedback loop)

---

## Predictions

| ID | Statement | Test Method | Success Criterion |
|----|-----------|-------------|-------------------|
| P1 | ΔHHI_t predicts ΔEntropy_{t+1} negatively | Panel regression with lagged IV | β < 0, p < 0.05 |
| P2 | HHI Granger-causes entropy | Granger causality test | HHI → Entropy sig., reverse not sig. |
| P3 | High-HHI papers use fewer evaluation datasets | Paper-level regression | Negative coefficient, p < 0.05 |

---

## Novelty

- **First quantitative application** of economic concentration metrics (HHI) to ML benchmark usage
- **Epistemic lock-in theory** applied to ML research practices
- **Temporal-causal design** with lagged panel regression advances beyond cross-sectional correlation

### Differentiation from Prior Work

| Prior Work | Difference |
|------------|------------|
| Engdahl (2024) "Agreements in the wild" | Qualitative ethnographic vs quantitative longitudinal |
| Olszewski et al. (2023) "Get in Researchers" | Reproducibility measurement vs concentration mechanism |
| HPO-B (2021) | Created benchmark vs analyzed benchmark usage patterns |

---

## Experimental Design

- **Data Source**: Papers With Code API/CSV export
- **Sample**: ~15K papers from NeurIPS, ICML, ICLR (2018-2024)
- **Unit of Analysis**: Venue-year (21 observations) + paper-level (15K observations)
- **Primary Analysis**: Panel regression with lagged IV and venue/year fixed effects
- **Secondary Analysis**: Granger causality test, paper-level regression

---

## Limitations

1. Tests upstream mechanism (concentration → diversity), not final reproducibility outcome
2. Observational data cannot establish experimental causation
3. Publication bias may hide diversity attempts (acknowledged as part of mechanism)
4. Papers With Code coverage is ~80%, not complete
5. Scope limited to major general-purpose venues (NeurIPS/ICML/ICLR)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria satisfied at Exchange 18 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Reverse causality (mitigated), positive concentration interpretation (addressed) |

---

*Phase: 2A - Research Dialogue*
*Architecture: Self-Play Loop (Claude-only, IC-ablation)*
*Ready for: Phase 2B - Hypothesis Verification Planning*
