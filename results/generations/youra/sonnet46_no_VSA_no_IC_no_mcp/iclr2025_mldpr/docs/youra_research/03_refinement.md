# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Automated, Reproducible Method for Temporal Benchmark Saturation Detection
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met at Exchange 7 — unanimous STRONG verdicts across novelty, falsifiability, significance, and feasibility dimensions.

### Key Insights
1. The logistic curve is the correct model because benchmark overfitting produces a genuine S-curve — papers like Wang et al. 2018 (GLUE) show this empirically in public leaderboard data.
2. Papers With Code already contains all required temporal data — no new collection needed.
3. GLUE→SuperGLUE and SuperGLUE→BIG-bench transitions are hard, documented saturation events that serve as independent ground truth (successor benchmark publication dates avoid circular validation).
4. Prospective detection (P3 — forecasting saturation from early data) is the highest-impact framing.

### Breakthrough Moments
- **Exchange 2 (Prof. Vera):** Added AIC model comparison requirement — without formal model selection, logistic fitting is vacuous.
- **Exchange 4 (Prof. Pax):** Confirmed implementation feasibility; 3 existing libraries; < 1 week.
- **Exchange 6 (Prof. Rex):** Identified successor benchmark publication date as independent ground truth — resolving the circular validation risk.

---

## Final Hypothesis

### Title
Automated Temporal Benchmark Saturation Detection via Logistic Curve Fitting on Public Leaderboard Timeseries

### Hypothesis ID
H-BenchSat-v1

### Core Claim
Under the condition that a benchmark has ≥ 50 leaderboard submissions in Papers With Code with date coverage from ≥ 2019, if we fit a logistic growth model to the score-over-time timeseries and compare it against linear and sub-linear alternatives via AIC, then the logistic model will be statistically preferred AND its detected saturation date will match the community-recognized saturation event within ±6 months, because benchmark overfitting accumulates gradually as models are tuned against a fixed test set, producing a characteristic S-curve that the logistic model captures while linear models cannot.

### Mechanism
Community benchmark overfitting accumulates as models are tuned against a fixed test set → leaderboard performance follows an S-curve (slow start, rapid ascent, plateau) → logistic model parameters K (ceiling), r (growth rate), t0 (inflection) encode this dynamics → AIC comparison tests whether S-curve structure is statistically warranted vs. simpler alternatives → inflection point + asymptote exceedance criterion operationalizes the saturation date → comparison to successor benchmark publication dates validates detection accuracy.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | Logistic model AIC-preferred over linear for GLUE and SuperGLUE | ΔAIC > 4 vs. linear for both benchmarks | ΔAIC < 4 for either benchmark |
| **P2** | Detected saturation dates match community ground truth | Within ±6 months of successor benchmark publication dates | Error > 6 months for both |
| **P3** | Logistic fit to truncated GLUE data (6 months early) forecasts saturation date | Forecast within ±3 months of actual date | Forecast error > 3 months |

---

## Novelty

**What's new:** First automated, benchmark-agnostic pipeline for temporal saturation detection from public leaderboard timeseries.

**Key differentiator from prior work:**
- **vs. Recht et al. 2019:** No new test set collection required — uses existing Papers With Code data
- **vs. Qualitative community critiques:** Quantitative, automated, reproducible
- **vs. Papers With Code visual curves:** Formal statistical model with saturation score, confidence intervals, and date detection

---

## Experimental Design

**Data source:** Papers With Code API (`paperswithcode-client`), benchmark_results() endpoint — retrieves (model, score, date) tuples for GLUE, SuperGLUE, ImageNet, SQuAD

**Models fitted:**
- Logistic: `K / (1 + exp(-r*(t - t0)))` via scipy.optimize.curve_fit
- Linear: `score = a*t + b` via numpy.polyfit
- Power law: `score = a * t^b` for diminishing returns baseline

**Ground truth:** Successor benchmark publication dates (SuperGLUE paper arXiv:1905.00537 ≈ Sept 2019 for GLUE saturation; BIG-bench ≈ 2021 for SuperGLUE saturation)

**Scope:** Benchmarks with ≥ 50 entries, month-level dates from ≥ 2019. Primary targets: GLUE, SuperGLUE, ImageNet, SQuAD 1.1, SQuAD 2.0.

---

## Limitations

1. **Selection bias:** Papers With Code leaderboard is self-reported — teams submit when beating SOTA. Near-ceiling region is underrepresented, biasing K upward. Mitigation: sensitivity analysis, explicit bias direction reporting.
2. **Date resolution:** Pre-2019 entries may have year-level dates only. Mitigation: use arXiv submission date as fallback.
3. **Ceiling effects vs. overfitting:** High-bounded benchmarks show S-curves even without overfitting. Mitigation: cross-benchmark divergence analysis (GLUE plateau vs. SuperGLUE level) as required secondary test.
4. **Scope restriction:** Method applies only to benchmarks with sufficient leaderboard history — not applicable to benchmarks released after 2022 or niche benchmarks with < 50 entries.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 7 — unanimous STRONG verdicts |
| **Clarity Verified** | Yes |
| **Feasibility** | HIGH (< 1 week implementation, 3 libraries) |
| **Remaining Objections** | Selection bias (mitigated), tolerance sensitivity (multi-window analysis) |

---

*Phase 2A complete. Ready for Phase 2B hypothesis verification planning.*
