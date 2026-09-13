# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-03T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-3
- **Gap Title**: Theoretical Direction of Diversity-Displacement Relationship (HR < 1 vs HR > 1)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 14
- **Pipeline Context**: ROUTE_TO_0 Attempt 11 — 10 prior failures

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 14

**Convergence Reason**: All 6 convergence criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) met at Exchange 14. 5-gate FAIL FAST protocol finalized with two protocol additions from Prof. Rex (direction-interpretation protocol, predictor collinearity failsafe).

### Key Insights
1. `paper_diversity_ratio = unique_paper_count / total_rows` is structurally an inverse HHI (Herfindahl-Hirschman Index) — connects benchmark lifecycle research to competition economics literature
2. The 5-gate FAIL FAST protocol prevents all 10 prior failure modes (time-proxy collapse from h-m1, variance flatness, join coverage failure, VIF multicollinearity)
3. Bidirectional test framing is scientifically stronger than pre-committed direction — both lock-in (HR<1) and saturation (HR>1) are literature-supported
4. Even a clean null result is publishable: rules out community-breadth class of predictors, narrows the predictor space for future attempts
5. The design template (5-gate FAIL FAST + bidirectional protocol + pre-specified effect threshold) is a methodological contribution beyond the empirical finding itself

### Breakthrough Moments
- **Exchange 6 (Prof. Rex)**: Added G3 variance gate — addressed underpowered-predictor risk absent from original design
- **Exchange 8 (Prof. Vera)**: Formalized complete 5-gate FAIL FAST protocol with explicit success/failure criteria for all gates
- **Exchange 12 (Prof. Rex)**: Added direction-interpretation protocol + predictor collinearity failsafe (r>0.95) — prevents HARKing and secondary predictor overclaiming
- **Exchange 13 (Dr. Nova)**: Inverse HHI analogy + template-as-contribution framing — elevates paper above single empirical test

---

## Final Hypothesis

### Title
**Benchmark Submitter Diversity Predicts Plurality Displacement Hazard (H-Diversity-v1)**

### Core Claim
Under the h-e2 panel (87 tasks, 345 plurality-benchmark displacement events, 2015–2023, Papers With Code), if `log_unique_paper_count_at_intro_z` (log-transformed, z-standardized count of distinct `paper_url` values per benchmark through plurality-introduction year from `pwc-archive/evaluation-tables`) passes a 5-gate FAIL FAST pre-validation protocol, then it significantly predicts plurality benchmark displacement hazard in `CoxPHFitter(penalizer=0.1)` with |HR−1| ≥ 0.10 and LRT p < 0.05.

Effect direction is determined empirically:
- **HR < 1** → Community lock-in mechanism (broad adoption → stakeholder network → slower displacement)
- **HR > 1** → Saturation pressure mechanism (diversity → overuse signal → faster community replacement)
- **LRT p > 0.05** → Null result (rules out community-breadth class of predictors)

### FAIL FAST Protocol (5 Gates)
| Gate | Criterion | Fail Action |
|------|-----------|-------------|
| G0 | ≥80% h-e2 benchmarks have non-null paper_url after join | ROUTE_TO_0 (Attempt 12) |
| G1 | partial_r²(log_unique_paper_count_z, [task_age, intro_year]) > 0.01 | ROUTE_TO_0 |
| G2 | partial_r²(paper_diversity_ratio_z, [task_age, intro_year]) > 0.01 | ROUTE_TO_0 |
| G3 | std(paper_diversity_ratio_at_intro) > 0.10 | ROUTE_TO_0 |
| G4 | VIF < 10 for all covariates | WARN + predictor exclusion |

### Mechanism

**H1 (Lock-in path):** High diversity at intro year → broad stakeholder community → teams continue submitting to incumbent → challenger cannot achieve plurality → slower displacement (HR < 1)

**H2 (Saturation path):** High diversity at intro year → widespread adoption → community perceives saturation → search for harder benchmarks → faster displacement (HR > 1)

Both mechanisms are grounded in literature: Ott et al. 2022 (breadth→longevity, 3765 benchmarks) supports H1; Koch et al. 2021 (concentration methodology) and ICLR 2025 workshop (overuse framing) support H2.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | log_unique_paper_count_at_intro_z significantly predicts displacement hazard | LRT p < 0.05 AND |HR-1| ≥ 0.10 | LRT p ≥ 0.05 OR |HR-1| < 0.10 |
| P2 | 95% CI of HR does not contain 1.0 | CI_upper < 1.0 (H1) OR CI_lower > 1.0 (H2) | CI spans 1.0 |
| P3 | KM curves Q1 vs Q4 diversity show separation | Log-rank p < 0.05 | Log-rank p ≥ 0.05 |

**Robustness Checks:**
- R1: paper_diversity_ratio_z as primary predictor — LRT p < 0.05
- R2: Interaction (diversity × task_age) added — primary HR remains significant
- R3: Koch 133 core subset only — LRT p < 0.10 (reduced power)

---

## Novelty

**What's New:** First empirical Cox test of community-structure diversity (submitter count/ratio at introduction year) as a time-independent predictor of plurality benchmark displacement hazard on Papers With Code. First 5-gate pre-validated survival analysis protocol for benchmark lifecycle research.

**Prior Work Differentiated:**
- Ott 2022: cross-benchmark population trends, no survival model, no displacement outcome
- Koch 2021: population-level concentration, no benchmark-level prediction
- h-m1 Runs 1-2: time-collinear (partial_r²=0.0011) or underpowered (22 events) prior attempts
- Paullada 2021: qualitative governance framework, no quantitative survival analysis

**Key Theoretical Anchor:** `paper_diversity_ratio` is an inverse HHI — high diversity (low HHI) = competitive market. Test: do benchmark markets follow economic stability-diversity pattern (HR<1) or inverted pattern (HR>1)?

---

## Experimental Design

**Data Sources:**
- `pwc-archive/evaluation-tables` — HuggingFace, CC-BY-SA-4.0, 326k rows, `paper_url` confirmed
- h-e2 survival panel — 87 tasks, 345 events, 2015–2023, validated across 10 prior attempts

**Model:** `CoxPHFitter(penalizer=0.1)` from lifelines (14/14 tests pass on h-e2 panel)

**Predictors:**
- Primary: `log_unique_paper_count_at_intro_z` = log1p(groupby('task_path')['paper_url'].nunique())_z
- Secondary: `paper_diversity_ratio_at_intro_z` = (unique_count / total_rows)_z [if r<0.95 with primary]

**Controls:** task_age, log_publication_volume, benchmark_introduction_year

**Implementation:**
```python
from datasets import load_dataset
import pandas as pd, numpy as np
from lifelines import CoxPHFitter

# Compute diversity metrics
ds = load_dataset("pwc-archive/evaluation-tables", split="train")
df = ds.to_pandas()
diversity_df = df.groupby('task_path')['paper_url'].agg(unique_paper_count=pd.Series.nunique)
total_rows = df.groupby('task_path').size().rename('total_rows')
diversity_df = diversity_df.join(total_rows, on='task_path')
diversity_df['paper_diversity_ratio'] = diversity_df['unique_paper_count'] / diversity_df['total_rows']
diversity_df['log_unique_paper_count_z'] = (
    np.log1p(diversity_df['unique_paper_count']).pipe(lambda x: (x - x.mean()) / x.std())
)

# FAIL FAST gates G0-G4 → then:
cph = CoxPHFitter(penalizer=0.1)
cph.fit(panel_df, duration_col='duration', event_col='event',
        formula='log_unique_paper_count_z + task_age + log_pub_vol + intro_year')
cph.print_summary()
```

---

## Limitations

1. **Join coverage unverified** — G0 gate handles this; if <80%, hypothesis routes to Attempt 12
2. **Association not causation** — Cox output cannot distinguish lock-in from saturation mechanism; direction is inferential, not mechanistic
3. **Secondary predictor redundancy** — if r(log_count_z, diversity_ratio_z) > 0.95, secondary predictor collapses into primary
4. **Temporal window** — 2015–2023 limits applicability to pre-LLM-saturation era of benchmark competition
5. **Saturation mechanism unobservable** — transmission path from "many submissions" to "community replacement" requires score-trajectory data (34.1% coverage ceiling); mechanism remains underdetermined

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-Diversity-v1 |
| **Discussion Convergence** | All 6 criteria met at Exchange 14 |
| **Clarity Verified** | Yes |
| **All Personas Participated** | Yes (6/6) |
| **FAIL FAST Protocol** | 5 gates (G0-G4) finalized |
| **Remaining Objections** | 3 (all mitigated by protocol design) |
| **Phase 2B Ready** | YES |

---

*Phase 2A Complete — Proceed to Phase 2B (Research Planning / Sub-hypothesis Decomposition)*
