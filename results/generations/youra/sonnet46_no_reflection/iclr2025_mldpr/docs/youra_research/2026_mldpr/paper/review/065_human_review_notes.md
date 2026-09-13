# Human Review Notes — R1 Round
**Paper**: BCBHS: Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Detection
**Date**: 2026-05-19
**Round**: R1 — Accuracy and Engagement
**Status**: MINOR issues collected for human reviewer decision — NOT fixed in `06_paper_r1.md`

These 6 MINOR issues were identified in the R1 adversarial review. They do not require immediate fix but should be addressed before camera-ready submission. Each entry includes the original review description and a recommended action.

---

## MINOR-001: Table 2 Rounding Inconsistency

**Type**: Numerical consistency
**Location**: Section 5.1, Table 2 (Effect Sizes by Lookback Window), 24-month row

**Issue**: Table 2 reports the 24-month values as NLP $|d|$ = 6.91 and Tabular $|d|$ = 6.52, while Table 1 and the contribution list in Section 1 use 6.910 and 6.515 respectively. The ground truth values are CV: 5.267, NLP: 6.910, Tabular: 6.515. Similarly, the h-e1 validation report shows CV 12-month = 3.42 and Tabular 12-month = 4.24, while Table 2 shows 3.40 and 4.22 — minor rounding differences.

**Recommended action**: Decide on a uniform decimal precision for effect size reporting throughout the paper. Either use 3 decimal places consistently (6.910, 6.515, 5.267) in both Table 1 and Table 2, or use 2 decimal places (6.91, 6.52, 5.27) consistently. The 3-decimal convention in Table 1 is more precise and aligns with ground truth values; recommend applying this to Table 2's 24-month row and harmonizing the 12-month values (3.40 → 3.42, 4.22 → 4.24) if high fidelity to the h-e1 validation report is desired.

---

## MINOR-002: Table 1 CV AUC Direction Inversion — Footnote Clarification

**Type**: Sign/absolute value clarity
**Location**: Section 1 (contribution #2), Table 1

**Issue**: The h-e1 validation report records Cohen's d = -5.267 for CV (negative because lower $H_d$ = saturated). The paper correctly uses absolute value notation $|d| = 5.267$. In `06_paper_r1.md`, the CV AUC cell has been updated to "0.000 (direction inverted; direction-corrected AUC = 1.000)" and an explanatory paragraph has been added in the main text (as part of MAJOR-002 fix). However, a dedicated Table 1 footnote (separate from the inline cell text) would improve readability for reviewers who skim tables:

**Recommended action**: Add a dedicated footnote below Table 1 such as: "*CV $H_d$ (score variance) is lower for saturated benchmarks, so the standard-direction AUC = 0.000 and the direction-corrected AUC = 1.000. The negative Cohen's d = -5.267 for CV reflects this inverted direction; $|d| = 5.267$ is reported throughout.*" This is distinct from the synthetic data footnote (†) already added.

---

## MINOR-003: "Granger causal validation" → "Granger causality test" in Section 2.5

**Type**: Grammar/style
**Location**: Section 2.5 (Related Work — Survival Analysis), last sentence of main text

**Issue**: The original paper contained "The Granger causal validation we provide establishes the temporal precedence required to justify this survival framing" — "Granger causal validation" is non-standard phrasing.

**Status**: This has been partially resolved in `06_paper_r1.md` as part of MAJOR-001, where the sentence was changed to "The Granger causality test we provide establishes the temporal precedence required to justify this survival framing." The human reviewer should confirm this specific instance reads naturally in context and that no other instances of "Granger causal validation" remain.

**Recommended action**: Search for any remaining instances of "Granger causal" (as opposed to "Granger causality" or "Granger-predictive") in the revised paper and replace with the appropriate standard terminology.

---

## MINOR-004: Baselines Described in Section 4.2 but Results Absent from Section 5

**Type**: Incomplete reporting
**Location**: Section 4.2 (Baselines), Section 5 (Results)

**Issue**: Section 4.2 describes four baselines:
1. Score variance + slope (naive)
2. Spearman correlation (contemporaneous)
3. Granger null (reverse direction)
4. S-index baseline (NLP only)

Of these, only Spearman $\rho = 0.052$ (Table 3) and Granger null (Table 3, "Reverse Granger $p > 0.05$") appear in the results. The "Score variance + slope (naive)" baseline and "S-index baseline (NLP only)" are described in Section 4.2 but their empirical results never appear in Section 5. ICML reviewers will note this discrepancy between promised and delivered comparisons.

**Recommended action**: Choose one of two resolutions before submission:
- **(Option A — Add results)**: Run the Score variance + slope baseline on the real panel and report its compression event detection accuracy vs. $H_d$ in a new table or as additions to Table 4. For the S-index baseline, report its NLP AUC or Cohen's d on the same dataset as $H_d^\text{NLP}$.
- **(Option B — Remove from Section 4.2)**: Remove the "Score variance + slope (naive)" and "S-index baseline (NLP only)" entries from Section 4.2 and note that these baselines are reserved for the full BCBHS validation pipeline (future work). This avoids the unfulfilled-promise issue.

Option B is lower effort and still scientifically honest given the paper's "empirical foundations" framing.

---

## MINOR-005: "approximately 6 months" Should Be "6 months (2 quarters)"

**Type**: Precision/clarity
**Location**: Section 1 (Introduction): "lag 2 (approximately 6 months)"; Section 5.2 header; Section 7

**Issue**: Lag = 2 quarters = 6 months exactly, not "approximately." The "approximately" qualifier is unnecessary and slightly imprecise. All instances in the paper use "approximately 6 months" when "6 months (2 quarters)" would be both more precise and more transparent about the quarterly resolution.

**Recommended action**: Replace all instances of "approximately 6 months" with "6 months (2 quarters)" throughout the paper. Specific locations to check:
- Section 1: "at lag 2 (approximately 6 months; $p = 1.854 \times 10^{-5}$)"
- Section 5.2 heading: "at lag 2 ($\approx$ 6 months)"
- Section 7: "at a 6-month lag"

Note: Section 7 already says "6-month lag" without "approximately" — this is correct. The Section 1 and Section 5.2 instances need updating.

---

## MINOR-006: Figure Placeholders Must Be Replaced with Actual Figures for Camera-Ready

**Type**: Formatting/presentation
**Location**: Sections 5.1 through 5.4 — Figures 1 through 9

**Issue**: All 9 figure references in the paper are formatted as italicized placeholder text, e.g.:
- `*[Figure 1: H_d value distributions...]*`
- `*[Figure 3: Quarterly panel heatmap...]*`
- `*[Figure 5: Granger p-values across lags 1–4...]*`
- `*[Figure 7: ROC curves per domain...]*`

These are appropriate working paper placeholders, but the camera-ready version requires actual embedded figures.

**Recommended action**: Before camera-ready submission, integrate figures from the pipeline output directories:
- **Figure 1** (H_d boxplots): `h-e1/figures/` — discriminability boxplots per domain
- **Figure 2** (Cohen's d by lookback): `h-e1/figures/` — temporal signal strength plot
- **Figure 3** (Panel heatmap): `h-m1/figures/` — compression events across 466 benchmarks × 7 years
- **Figure 4** (Time-series overlay): `h-m1/figures/` — representative benchmark cumcount vs. score_var
- **Figure 5** (Granger p-values by lag): `h-m1/figures/` — forward/reverse Granger lag profile
- **Figure 6** (Compression event distribution): `h-m1/figures/` — histogram of events per benchmark
- **Figure 7** (ROC curves): `h-m2/figures/` — per-domain ROC for compressed vs. non-compressed
- **Figure 8** (H_d magnitude boxplots): `h-m2/figures/` — compressed vs. non-compressed H_d distributions
- **Figure 9** (Signal emergence timeline): `h-m2/figures/` — the 1 detected collapse event signal lead

Verify that figures exist in these directories and are in ICML-compatible format (PDF or high-resolution PNG). If any figures are missing, they must be regenerated from the pipeline outputs before camera-ready submission.

---

## Summary Table

| Issue | Type | Location | Effort | Priority |
|-------|------|----------|--------|----------|
| MINOR-001 | Numerical consistency | Table 2 (Section 5.1) | Low | Medium |
| MINOR-002 | Sign/AUC clarity footnote | Table 1 (Section 5.1) | Low | Medium |
| MINOR-003 | Grammar/style | Section 2.5 | Very Low | Low |
| MINOR-004 | Missing baseline results | Section 4.2, Section 5 | Medium-High | High |
| MINOR-005 | Precision wording | Sections 1, 5.2 | Very Low | Low |
| MINOR-006 | Figure embedding | Sections 5.1–5.4 | Medium | High (camera-ready blocker) |

---

## Round 2 Issues
**Round**: R2 — Numerical Verification and Credibility Check
**Date**: 2026-05-19
**Status**: MINOR issues collected for human reviewer decision — NOT fixed in `06_paper_r2.md`

### R2-MINOR-001: "Spanning Seven Years" Overstates Per-Benchmark Coverage

**Type**: Precision/clarity
**Location**: Abstract ("spanning seven years of Papers With Code history"), Section 1, Section 6.1

**Issue**: The panel contains 6,938 observations across 466 benchmarks = 14.9 quarters average = ~3.7 years average per benchmark. The study period spans 7 years (2018–2025), but most benchmarks have less than half that coverage. "Spanning seven years" accurately describes the study *window* but may mislead readers into thinking all 466 benchmarks have 7-year histories.

**Recommended action**: Add a qualifier such as "covering up to seven years of leaderboard history" or "across a 7-year observation window (2018–2025)" in the abstract and first occurrence in Section 1. Optionally add to Section 3.2: "The study window covers 2018–2025 (7 years), with individual benchmarks having between 2 and 7 years of history (mean ~3.7 years, i.e., ~15 quarters)."

---

### R2-MINOR-002: Section 4.2 Baselines Promised but Results Absent from Section 5 (Inherited from R1 MINOR-004)

**Type**: Incomplete reporting (carried forward from R1)
**Location**: Section 4.2 (Baselines), Section 5 (Results)

**Issue**: Section 4.2 describes "Score variance + slope (naive)" and "S-index baseline (NLP only)" baselines but neither appears in Section 5 results. This unfulfilled promise was flagged in R1 MINOR-004 and remains unresolved. ICML reviewers will notice the discrepancy between described and reported baselines.

**Recommended action** (same as R1 MINOR-004):
- **(Option A — Add results)**: Run the Score variance + slope baseline on the real panel and report results in Table 4. Report S-index NLP AUC for comparison.
- **(Option B — Remove from Section 4.2)**: Remove these two entries from Section 4.2, noting they are reserved for the full BCBHS validation pipeline (future work).

Option B is lower effort and consistent with the paper's empirical foundations framing.
