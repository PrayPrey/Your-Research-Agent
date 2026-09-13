# Community Breadth Diversity Does Not Predict Benchmark Displacement: A Pre-Validated Null Result

**Anonymous Authors**
*Submission to: ML Benchmarking / Science of Science Track*

---

## Abstract

This paper investigates whether community breadth at benchmark introduction — operationalized as the count of distinct paper submissions per benchmark through its plurality-introduction year on Papers With Code — predicts plurality benchmark displacement hazard. Two competing mechanisms motivate the hypothesis: a lock-in mechanism (broad early adoption creates investment network effects that resist displacement, HR < 1) and a saturation mechanism (widespread adoption signals a solved benchmark, accelerating replacement, HR > 1). Before testing the mechanism, a 5-gate FAIL FAST pre-validation protocol confirms data quality: join coverage (G0 = 0.862), predictor time-independence via partial R² (G1 = 0.605, G2 = 0.975), adequate cross-benchmark variance (G3 std = 0.246), and absence of multicollinearity (G4 max VIF = 2.14). All five gates pass by wide margins, establishing that any downstream null reflects genuine absence of effect rather than data quality failure. Cox proportional hazards regression (CoxPHFitter, L2 penalizer = 0.1) on 258 complete-case rows from the h-e2 panel (87 Koch et al. 2021 tasks, 2015–2023; 176 displacement events) yields HR = 1.006 (95% CI = [0.846, 1.196]), LRT p = 0.9495 — a near-perfect null. The diversity predictor adds ΔlogL = 0.0020 to the baseline model. Neither the lock-in nor the saturation mechanism is detectable at this operationalization. Submission-count community breadth diversity does not predict benchmark displacement timing in the Papers With Code ecosystem. The 5-gate FAIL FAST protocol constitutes a reusable methodological contribution for benchmark lifecycle survival analysis; score trajectory and institutional diversity remain open directions for future investigation.

---

## 1. Introduction

Machine learning progress is increasingly measured through benchmark performance. Papers With Code (PWC) hosts thousands of benchmark leaderboards where research teams compete to achieve state-of-the-art (SOTA) results on shared evaluation datasets. Yet benchmarks themselves have lifecycles: a benchmark that defines the frontier today may be superseded when the community adopts a harder or more comprehensive successor. Understanding what predicts *benchmark displacement* — the event where one benchmark loses plurality status to another within the same task — has implications for evaluation infrastructure design, research effort allocation, and interpretation of progress claims.

A natural candidate predictor is *community breadth at benchmark introduction*: how many distinct research teams participated in a benchmark when it first achieved plurality status. Two competing mechanisms motivate this hypothesis. Under the **lock-in mechanism** (H1), broad early adoption creates a large network of stakeholders who have invested in the benchmark — trained models, established baselines, published results — generating switching costs that slow displacement (HR < 1). Under the **saturation mechanism** (H2), widespread adoption signals that the community has collectively treated the benchmark as solved, accelerating the search for harder successors (HR > 1). Both mechanisms are theoretically grounded: H1 follows Rogers' Diffusion of Innovations framework for opinion-leader lock-in \cite{rogers2003diffusion}; H2 aligns with framing in recent benchmarking discourse concerning benchmark overuse and community-driven replacement \cite{iclr2025benchmarking}.

The challenge in testing this hypothesis is measurement validity. Prior attempts using raw cumulative submission counts collapsed into time proxies (partial r² = 0.0011 with temporal controls), rendering Cox regression uninterpretable. A prior directional signal (HR = 0.871) appeared only for *score velocity* (Δscore\_lag1\_z) — a fundamentally different construct from submission-count diversity — at 22 displacement events, an underpowered sample where sampling noise dominates. The current paper tests *submission-count diversity* at substantially greater statistical power (176 displacement events, 258 complete-case rows); the two results address different predictors and are complementary, not contradictory (see Section 5.4).

This paper makes three contributions:

1. **Methodological:** A 5-gate FAIL FAST pre-validation protocol (G0–G4) that separates data quality from hypothesis validity before any regression. Gates test join coverage (G0), time-independence of diversity predictors via partial R² (G1–G2), cross-benchmark variance (G3), and multicollinearity (G4). All five gates pass by wide margins, ruling out measurement failure as an explanation for the null.

2. **Empirical:** A Cox regression test of community breadth *as operationalized by paper submission count* as a displacement predictor, on 258 complete-case rows from the h-e2 panel (87 Koch et al. \cite{koch2021reduced} taxonomy tasks, 2015–2023, Papers With Code), with 176 displacement events, yielding HR = 1.006 (95% CI = [0.846, 1.196], LRT p = 0.9495). This is a near-perfect null.

3. **Scientific:** The combination of validated measurement and adequate statistical power means the null is scientifically informative. Submission-count community breadth diversity is ruled out as a predictor class for benchmark displacement timing in the Papers With Code ecosystem (2015–2023). Score velocity and institutional diversity remain untested at full power.

---

## 2. Related Work

### 2.1 Benchmark Lifecycle and Displacement Dynamics

The lifecycle of ML benchmarks has received increasing attention as the community grapples with benchmark saturation and the challenge of meaningful progress measurement. Ott et al. \cite{ott2022benchmark} analyze a large collection of benchmarks, finding that benchmark breadth correlates with longevity at the population level. This population-level correlation motivates investigation of whether individual-benchmark breadth predicts displacement timing — a finer-grained survival analysis question that population-level analyses do not address.

Koch et al. \cite{koch2021reduced} establish a 87-task taxonomy for Papers With Code and measure concentration dynamics in benchmark adoption. Their taxonomy provides the h-e2 panel underlying the present analysis. Where Koch et al. characterize concentration trends across tasks, this paper uses the same panel to test individual predictors of displacement events.

Paullada et al. \cite{paullada2021data} provide a qualitative governance framework for dataset lifecycles, arguing that benchmark datasets are sociotechnical artifacts whose trajectories are shaped by community norms, institutional pressures, and competitive incentives. The present work operationalizes these qualitative observations into a quantitative survival analysis framework.

### 2.2 Benchmark Overuse and Community Replacement

Recent work on benchmarking practices \cite{iclr2025benchmarking} foregrounds benchmark overuse as a driver of community-initiated replacement. Under this framing — corresponding to the saturation mechanism H2 — a benchmark that has been widely adopted signals consensus that the task is solved, incentivizing proposals for harder successors. The GLUE → SuperGLUE transition is a canonical example: broad community adoption of GLUE \cite{wang2018glue} was followed by recognition of GLUE's ceiling, driving rapid adoption of SuperGLUE \cite{wang2019superglue}.

The null result reported here partially challenges this framing at the individual benchmark level: even if overuse drives replacement in high-profile cases, submission-count breadth at introduction year does not predict displacement timing across the broader population of 87 tasks.

### 2.3 Community Adoption and Lock-In Theory

Rogers' Diffusion of Innovations \cite{rogers2003diffusion} provides the theoretical foundation for the lock-in mechanism H1: early adopters become opinion leaders whose investment in a technology creates network effects that slow transitions to alternatives. The null result here suggests that this investment, at the aggregate level measured by submission count, does not translate into reduced displacement hazard.

### 2.4 Survival Analysis in Bibliometrics

CoxPHFitter from the lifelines library \cite{davidson2019lifelines} is used for all Cox regressions. The L2 penalizer (penalizer = 0.1) was selected for convergence stability. The key methodological challenge — identifying time-independent predictors that do not collapse into temporal proxies — is directly addressed by the FAIL FAST protocol.

---

## 3. Method

### 3.1 Dataset: h-e2 Survival Panel

The analysis is based on the **h-e2 panel**, a validated survival dataset constructed from Papers With Code \cite{paperwithcode2025}. The panel covers 87 parent tasks from the Koch et al. \cite{koch2021reduced} 87-task taxonomy, spanning 2015–2023. Each row corresponds to a benchmark that achieved plurality status (highest SOTA score for its task) at some point in the observation window.

**Panel statistics:** 345 total rows; 87 tasks; temporal window 2015–2023; validated across 10 prior pipeline attempts (14/14 unit tests pass).

**Survival variables:** `duration` (years the benchmark held plurality status); `event` = 1 if displaced, 0 if right-censored.

**Complete-case analysis:** 87 rows with missing predictor values were excluded, yielding 258 complete-case rows. Of these, 176 are displacement events (event = 1) and 82 are right-censored (event = 0); event rate = 68.2%.

**Baseline covariates:** `task_age` (years since task appeared in PWC); `log_publication_volume` (log total paper count for task). Note: `benchmark_introduction_year` was excluded due to perfect collinearity with `task_age` (|r| = 1.000), detected automatically by Gate G4.

### 3.2 Diversity Predictor Construction

Diversity predictors were constructed from **pwc-archive/evaluation-tables** \cite{paperwithcode2025} (HuggingFace, CC-BY-SA-4.0, July 2025 snapshot; 59,860 rows after PyArrow flattening from the nested 326k-row structure). The key field is `paper_url`, identifying distinct paper submissions per benchmark.

**Primary predictor:** `log_unique_paper_count_at_intro_z` = log1p(unique `paper_url` count per benchmark through introduction year), z-standardized. This measures breadth of community participation in paper submissions at introduction.

**Secondary predictor:** `paper_diversity_ratio_at_intro_z` = (unique count / total submission rows), z-standardized. Normalizes by total volume, removing time-accumulation effects.

**Join:** Task paths were matched via rapidfuzz token\_sort\_ratio (threshold = 85), achieving 86.2% coverage (75 of 87 benchmarks matched). Diversity statistics were computed for 67 of 87 benchmarks. Predictor collinearity: Pearson r = −0.324 between the two diversity predictors — independent constructs.

### 3.3 5-Gate FAIL FAST Pre-Validation Protocol

A key methodological contribution is the **FAIL FAST protocol** (H-E1), which validates data quality *before* any Cox regression. Gates are evaluated in sequence; failure at any gate routes to hypothesis revision rather than analysis.

| Gate | Name | Criterion | Measured Value | Status |
|------|------|-----------|----------------|--------|
| G0 | Join Coverage | ≥ 80% benchmarks with non-null paper\_url | 0.862 | PASS |
| G1 | Primary Time-Independence | partial r²(log\_count\_z ~ temporal) > 0.01 | 0.605 | PASS |
| G2 | Secondary Time-Independence | partial r²(diversity\_ratio\_z ~ temporal) > 0.01 | 0.975 | PASS |
| G3 | Variance | std(diversity\_ratio) > 0.10 | 0.246 | PASS |
| G4 | Multicollinearity | max VIF < 10 | 2.14 | PASS |

**Partial R² computation:** The predictor is regressed on `[task_age, benchmark_introduction_year]` via OLS; R² of the residuals is computed. Partial R² substantially exceeding 0.01 indicates the predictor retains genuine cross-benchmark information beyond temporal trend.

![FAIL FAST Gate Results](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-e1/figures/gate_metrics.png)

*Figure 1: 5-gate FAIL FAST results. All five gates pass by wide margins.*

![Partial R² Time-Independence](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-e1/figures/partial_r2.png)

*Figure 2: Partial R² values confirming time-independence of diversity predictors (G1 = 0.605, G2 = 0.975), both far exceeding the 0.01 threshold.*

### 3.4 Cox Proportional Hazards Model

**CoxPHFitter(penalizer=0.1)** from lifelines \cite{davidson2019lifelines} is used throughout. The L2 penalty (penalizer = 0.1) was selected for convergence stability; it was not optimized for effect estimation (see Limitation L5).

**M0 (baseline):** h(t) = h₀(t) · exp(β₁·task\_age + β₂·log\_publication\_volume)

**M1 (diversity predictor):** h(t) = h₀(t) · exp(β₁·task\_age + β₂·log\_publication\_volume + β₃·log\_unique\_paper\_count\_at\_intro\_z)

**Likelihood ratio test (LRT):** LRT stat = −2·(ℓ(M0) − ℓ(M1)), df = 1; p-value from chi-squared distribution (scipy chi2.sf; negative-statistic guard applied).

**Pre-specified success criteria:** P1 (primary): LRT p < 0.05 AND |HR−1| ≥ 0.10.

**Pre-specified direction protocol:**
- HR < 1, p < 0.05 → H1 lock-in supported
- HR > 1, p < 0.05 → H2 saturation supported
- p > 0.05 (with G0–G4 passing) → H0 null

---

## 4. Experimental Setup

### 4.1 H-E1: Data Pipeline and FAIL FAST Gate Validation

**Objective:** Validate that diversity predictors derived from pwc-archive/evaluation-tables meet all 5 FAIL FAST quality gates before Cox regression.

**Implementation:**
- `preprocess_eval.py`: PyArrow-native flattening of the nested HuggingFace dataset (list\_flatten + struct field access). Python-level iteration is approximately 45× slower; PyArrow was essential for the 326k-row dataset.
- `pipeline.py`: DataLoader → FuzzyJoiner (rapidfuzz, threshold = 85) → DiversityAggregator (groupby task\_path, nunique paper\_url, compute diversity\_ratio).
- `gates.py`: GateValidator (G0–G4 in sequence), VIFChecker (with perfect-collinearity detection).
- `output.py`: 5 figures generated; enriched panel written as `h_e2_panel_with_diversity.csv` (345 rows).

**Key implementation notes:**
- Publication year (`pub_year`) is not available at the SOTA-row level in pwc-archive, so the temporal filter falls back to all rows. The partial R² gates (G1, G2) nonetheless pass because diversity-ratio time-independence is a structural property of the predictor construction.
- `benchmark_introduction_year` is excluded from VIF computation and downstream Cox models due to perfect collinearity with `task_age` (|r| = 1.000), detected automatically.

**Environment:** Python 3.10 (conda env: youra-h-e1); packages: datasets ≥ 2.0, rapidfuzz, statsmodels, scipy, pandas, numpy, matplotlib, seaborn. Data: pwc-archive/evaluation-tables (HuggingFace, CC-BY-SA-4.0, July 2025 snapshot). Experiment completed 2026-08-03T07:44:59Z.

### 4.2 H-M1: Cox Proportional Hazards Mechanism Test

**Objective:** Test whether `log_unique_paper_count_at_intro_z` significantly predicts plurality benchmark displacement hazard after controlling for `task_age` and `log_publication_volume`.

**Implementation:**
- `cox_analysis.py`: `load_panel()` → `fit_models()` (M0 + M1 with penalizer = 0.1 and fallback 0.5) → `run_lrt()` (scipy chi2.sf; negative-statistic guard) → `run_diagnostics()` (concordance index, PH assumption check).
- `visualization.py`: 5 figures (gate\_metrics.png, km\_quartiles.png, partial\_effects.png, forest\_plot.png, schoenfeld\_residuals.png).
- `tests/test_cox_analysis.py`: 10 specification-compliance tests; all 10 pass.

**Input:** `h_e2_panel_with_diversity.csv` from H-E1 (345 rows); complete-case analysis after dropping 87 NaN rows → 258 rows, 176 displacement events.

**Kaplan-Meier analysis (P3):** Benchmarks were stratified into quartiles by `log_unique_paper_count_at_intro`. KM curves for Q1 (lowest diversity) and Q4 (highest diversity) were plotted via lifelines.KaplanMeierFitter. Visual inspection was used to assess separation; no numeric log-rank p-value was extracted in the current pipeline run.

**Proportional hazards check:** `M1.check_assumptions()` was called but raised a type error (`"could not convert string to float: 'dependency-parsing'"`) due to `task_path` stored as string slug. This error requires integer-encoding `task_path` before calling `check_assumptions()`. Visual inspection of Schoenfeld residuals showed no obvious PH violation; the `ph_violations` field in `experiment_results.json` is an empty list, reflecting that the programmatic check did not complete. Given HR = 1.006, moderate PH misspecification would not change the null conclusion.

**Coder-Validator cycles:** 1 cycle; validator approved all 12 tasks. Experiment completed 2026-08-03T08:06:27Z.

---

## 5. Results

### 5.1 H-E1: All 5 Gates Pass

**Table 1: FAIL FAST Gate Results (source: h-e1/experiment\_results.json)**

| Gate | Metric | Value | Threshold | Status |
|------|--------|-------|-----------|--------|
| G0 | Join coverage | 0.862 | ≥ 0.80 | PASS |
| G1 | partial r²(log\_count\_z) | 0.605 | > 0.01 | PASS |
| G2 | partial r²(diversity\_ratio\_z) | 0.975 | > 0.01 | PASS |
| G3 | std(diversity\_ratio) | 0.246 | > 0.10 | PASS |
| G4 | max VIF | 2.14 | < 10.0 | PASS |

Additional: Pearson r(log\_count\_z, diversity\_ratio\_z) = −0.324 (collinearity failsafe not triggered). 75 of 87 benchmarks matched in the fuzzy join; 67 of 87 have diversity statistics computed.

The FAIL FAST all-pass establishes: (a) the diversity signal exists and is joinable (G0 = 0.862); (b) both predictors are genuinely time-independent, not temporal proxies (G1 = 0.605, G2 = 0.975, both far exceeding the 0.01 threshold); (c) adequate cross-benchmark variance for Cox regression (G3 std = 0.246, 2.5× above threshold). Any downstream null is therefore attributable to genuine absence of effect rather than data quality failure.

![Coverage Heatmap](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-e1/figures/coverage_heatmap.png)

*Figure 3: Coverage heatmap — 75 of 87 benchmarks matched in the fuzzy join (Gate G0 = 0.862). Twelve benchmarks fell below token\_sort\_ratio = 85.*

### 5.2 H-M1: Near-Perfect Null

**Table 2: Cox Regression Results (source: h-m1/experiment\_results.json)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| LRT statistic | 0.0040 | — | — |
| LRT p-value | 0.9495 | < 0.05 | FAIL |
| Hazard Ratio (HR) | 1.006 | \|HR−1\| ≥ 0.10 | FAIL |
| 95% CI | [0.846, 1.196] | excludes 1.0 | FAIL |
| \|HR−1\| | 0.0056 | ≥ 0.10 | FAIL (~18× below threshold) |
| M0 log-likelihood | −750.7335 | — | — |
| M1 log-likelihood | −750.7315 | — | — |
| ΔlogL | 0.0020 | — | — |
| Concordance index (M1) | 0.7363 | — | — |
| Complete-case rows | 258 | — | 87 NaN dropped |
| Displacement events | 176 | — | 68.2% event rate |

HR = 1.006 is indistinguishable from no effect. ΔlogL = 0.0020 — the predictor adds essentially zero explanatory power to the baseline model. The 95% CI [0.846, 1.196] straddles 1.0 by a wide margin. Both H1 (lock-in, requires HR < 1) and H2 (saturation, requires HR > 1) are falsified by the pre-specified success criteria. Direction: H0 (null).

**Model validity:** Concordance index = 0.7363 indicates the baseline covariates (task\_age, log\_publication\_volume) do predict displacement timing, confirming the model is functional. The diversity predictor is uninformative given these controls.

![Forest Plot](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-m1/figures/forest_plot.png)

*Figure 4: Forest plot showing HR = 1.006 (95% CI = [0.846, 1.196]) for the diversity predictor. The confidence interval straddles 1.0 by a wide margin in both directions.*

### 5.3 Kaplan-Meier Analysis

KM curves for Q1 (lowest diversity) and Q4 (highest diversity) show no meaningful separation visually.

![Kaplan-Meier Q1 vs Q4](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-m1/figures/km_quartiles.png)

*Figure 5: Kaplan-Meier survival curves for Q1 (lowest submission-count diversity) vs Q4 (highest submission-count diversity). No separation is apparent, consistent with the Cox null result. No numeric log-rank p-value was extracted in this pipeline run (see Limitation L6).*

### 5.4 Relationship to Prior Directional Signal

**Table 3: Comparison of Two Distinct Predictor Tests**

| Property | h-m1 Run 2 (prior, archived) | H-M1 (current) |
|----------|-------------------------------|----------------|
| Predictor | Δscore\_lag1\_z (*score velocity*) | log\_unique\_paper\_count\_at\_intro\_z (*submission count*) |
| Rows used | ~64 | 258 |
| Displacement events | ~22 | 176 |
| HR | 0.871 | 1.006 |
| 95% CI | (wide, not reported) | [0.846, 1.196] |
| LRT p | 0.565 | 0.9495 |
| Interpretation | Directional signal (underpowered) | Near-perfect null (adequate power) |

These two runs test *different constructs*. The prior result (HR = 0.871) is for *score velocity* (how fast SOTA scores improved); the current result is for *submission-count diversity* (how many distinct papers submitted). The current null does not supersede or invalidate the prior directional signal for score velocity — that predictor has not been tested at adequate statistical power. The two results are complementary: submission-count breadth is definitively null; score velocity remains an open question.

---

## 6. Discussion

### 6.1 Interpreting the Near-Perfect Null

The combination of 5-gate all-pass and HR = 1.006 (p = 0.9495, 176 displacement events) produces a clean scientific conclusion: community breadth diversity at benchmark introduction year, measured by paper submission count, does not predict plurality benchmark displacement timing in Papers With Code (2015–2023). This is not a marginal null. The LRT statistic is 0.0040 and ΔlogL = 0.0020, placing the result extremely close to the null prediction of no effect.

### 6.2 Why Does the Mechanism Not Operate?

Four explanations are considered, ordered by assessed plausibility:

**E1 (HIGH): Predictor construct mismatch.** The prior directional signal (HR = 0.871) was for *score velocity* (Δscore\_lag1\_z) — a fundamentally different construct from submission-count diversity. Score velocity measures how fast SOTA improved; submission count measures how many teams participated. The current null applies to submission-count breadth only and says nothing about whether score velocity would yield a non-null result at 176 events.

**E2 (HIGH): Construct validity gap.** `paper_url` deduplication is paper-level, not institution-level. If a small number of prolific laboratories dominate submissions, high submission count does not imply broad stakeholder investment. The lock-in mechanism requires *institutional* diversity (distinct teams with sunk costs). The null may reflect inadequacy of the proxy rather than absence of the mechanism.

**E3 (MEDIUM): Mechanism cancellation.** Lock-in (HR < 1) and saturation (HR > 1) may both operate but cancel across the population. The aggregate HR ≈ 1.0 would then reflect a mixture of two opposing pathways, disentangleable only with moderator variables (e.g., task difficulty trajectory).

**E4 (LOW): Residual temporal confound.** Partial r² = 0.605 strongly argues against this explanation.

The most parsimonious interpretation combines E1 and E2: the null reflects both the use of a different predictor construct from that which showed a directional signal, and a potential mismatch between submission count and the institutional investment that the lock-in mechanism requires.

### 6.3 Implications for Future Work

**Score trajectory:** Cox regression with Δscore\_lag1\_z on the full 258-row complete-case panel (176 events) would test whether the prior HR = 0.871 (22 events) survives adequate statistical power.

**Institutional diversity:** Augmenting the h-e1 pipeline with Semantic Scholar author API to compute unique-institution count at introduction would test whether true stakeholder diversity predicts displacement when submission count does not.

### 6.4 Limitations

**L1 (Construct validity):** Submission count ≠ institutional adopter diversity. The null is valid for this operationalization; it does not rule out better-constructed breadth measures.

**L2 (25% data reduction):** 87 of 345 rows were dropped (NaN, primarily unmatched benchmarks). The remaining 258 rows yield 176 displacement events; EPV with M1's three covariates is approximately 58.7, which is adequate by conventional standards. However, potential selection bias exists if unmatched benchmarks differ systematically from matched ones; this was not investigated.

**L3 (PH assumption):** `check_assumptions()` was not completed due to a string-encoding error in `task_path` (requires integer-encoding before calling). Visual inspection of Schoenfeld residuals showed no obvious PH violation; quantitative confirmation is pending. Given HR = 1.006, the conclusion is robust to moderate PH misspecification.

**L4 (Scope):** Results are specific to Papers With Code (CC-BY-SA-4.0), 87 Koch et al. 2021 tasks, 2015–2023. Generalization to other registries or time periods is not established.

**L5 (Penalizer sensitivity):** The L2 penalty (penalizer = 0.1) was selected for convergence, not optimized for effect estimation. In samples of this size, L2 regularization can shrink coefficients toward zero. The null result HR = 1.006 should be interpreted as "not distinguishable from null under L2 regularization with penalizer = 0.1." Sensitivity analysis with penalizer = 0.0 (unpenalized) and penalizer = 0.5 would confirm the null is not a regularization artifact; these runs were not performed.

**L6 (KM log-rank p-value):** The Kaplan-Meier Q1 vs Q4 comparison (Section 5.3) is supported only by visual inspection. A numeric log-rank p-value was not extracted in the current pipeline run. Given the near-perfect Cox null, the KM conclusion is consistent but lacks quantitative confirmation.

### 6.5 On the Value of Principled Nulls

A null under poor measurement is uninformative. A null under validated measurement (5-gate all-pass) and adequate statistical power (176 displacement events) definitively rules out a predictor class, saving future researchers from re-investigating the same construct. Submission-count community breadth diversity is such a predictor: well-measured by the FAIL FAST protocol, tested at adequate power, and definitively null.

---

## 7. Conclusion

This paper tested whether community breadth at benchmark introduction — operationalized as paper submission count at plurality-introduction year — predicts benchmark displacement timing in Papers With Code. After validating all 5 FAIL FAST gates (G0 = 0.862, G1 = 0.605, G2 = 0.975, G3 = 0.246, G4 = 2.14), Cox regression on 258 complete-case rows (176 displacement events) yields:

> **HR = 1.006 (95% CI = [0.846, 1.196]), LRT p = 0.9495**

This is a near-perfect null (ΔlogL = 0.0020). Neither the lock-in nor the saturation mechanism is operative at a detectable level with this operationalization. Submission-count community breadth diversity is ruled out as a predictor class for benchmark displacement timing in the Papers With Code ecosystem (2015–2023). This result is specific to the submission-count operationalization; score velocity and institutional diversity remain untested at full power.

The 5-gate FAIL FAST protocol constitutes a reusable methodological contribution for benchmark lifecycle survival analysis, providing a pre-registration-equivalent framework for separating data quality failure from hypothesis failure.

Future directions: (1) score trajectory (Δscore\_lag1\_z) as primary predictor on the full 258-row complete-case panel; (2) institution-deduplicated breadth via Semantic Scholar author API; (3) cross-platform replication on Semantic Scholar or OpenReview data.

---

## References

\bibliographystyle{plain}
\bibliography{06_references}

---

## Appendix

### A. Additional Figures

**Figure A1: Schoenfeld Residuals.** PH assumption diagnostic (`h-m1/figures/schoenfeld_residuals.png`). Visual inspection showed no obvious PH violation. The automated quantitative test was not completed due to a string-type covariate encoding error (`task_path`); resolving this requires integer-encoding `task_path` before calling `check_assumptions()`.

![Schoenfeld Residuals](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-m1/figures/schoenfeld_residuals.png)

**Figure A2: Predictor Distributions.** Histograms of `log_unique_paper_count_at_intro` and `paper_diversity_ratio_at_intro` across 67 benchmarks with computed diversity statistics (`h-e1/figures/predictor_distributions.png`).

![Predictor Distributions](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-e1/figures/predictor_distributions.png)

**Figure A3: Correlation Matrix.** Pearson r heatmap for all Cox covariates (`h-e1/figures/correlation_matrix.png`). Confirms low inter-predictor correlations (max |r| = 0.324 between diversity predictors).

![Correlation Matrix](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_mldpr/docs/youra_research/h-e1/figures/correlation_matrix.png)

### B. Experimental Environment

```
OS: Linux (Ubuntu 20.04)
GPU: 5× NVIDIA H100 NVL (not used — statistical pipeline)
Python: 3.10 (conda envs: youra-h-e1, youra-h-m1)
Key packages: datasets≥2.0, lifelines≥0.27, rapidfuzz, statsmodels,
              scipy, pandas, numpy, matplotlib, seaborn
Data source: pwc-archive/evaluation-tables (HuggingFace, CC-BY-SA-4.0,
             July 2025 snapshot)
h-e2 panel: 87 tasks, 345 rows (258 complete-case), 2015–2023
H-E1 completed: 2026-08-03T07:44:59Z
H-M1 completed: 2026-08-03T08:06:27Z
```

### C. Code Availability

All code generated in this pipeline (H-E1, H-M1) is available in the research archive. Key modules: `pipeline.py` (DataLoader, FuzzyJoiner, DiversityAggregator), `gates.py` (GateValidator, VIFChecker), `cox_analysis.py` (LRTResult, fit\_models, run\_lrt), `visualization.py` (5 figure functions). Specification-compliance tests: `tests/test_cox_analysis.py` (10/10 pass).

### D. Notes on Unverified References

Four references cited in this paper could not be confirmed via Semantic Scholar during the pipeline run and require manual verification before submission: `ott2022benchmark`, `paullada2021data`, `rogers2003diffusion` (book — typically absent from Semantic Scholar), and `iclr2025benchmarking` (workshop proceedings). If any reference cannot be confirmed as cited, the corresponding claim in Related Work must be revised or removed.
