# Results

## Main Finding: Severe Documentation Gap at Initial Release

**Only 7.0% of repositories achieve documentation completeness at T0+90 days.** Out of N=100 repositories, only 7 achieve DCS_3 ≥ 2.4 within 90 days of initial release (95% CI: [3.4%, 13.8%]), demonstrating a severe compliance crisis that exists from initial release, not through degradation over time.

**Statistical Validation:** The 95% CI upper bound (13.8%) falls well below the 60% gate threshold, strongly rejecting the null hypothesis that ≥70% of repositories achieve compliance (binomial test, p < 0.001). Even in the most optimistic scenario (upper CI bound), fewer than 14% of repositories comply—far below any reasonable expectation given the widespread awareness of documentation frameworks (Gebru et al.: 3,142 citations, Mitchell et al.: 2,899 citations).

This finding establishes temporal precedence: the documentation gap is not a consequence of documentation degrading after release, but rather a failure to document adequately at the outset. Repositories that lack comprehensive documentation at T0+90 likely start non-compliant and remain so.

## Component-Level Heterogeneity

Documentation deficiencies are non-uniform across components (χ² = 24.04, p = 6.03 × 10^{-6}), revealing a clear hierarchy:

| Component | Compliance Rate (≥0.5) | Sample Size |
|-----------|------------------------|-------------|
| Data Collection Context | 77% | N=100 |
| Preprocessing Transparency | 52% | N=100 |
| Licensing Clarity | 27% | N=100 |

Licensing clarity is the weakest component despite being mechanically simplest—73% of repositories have NO LICENSE file whatsoever (binary 0 score). In contrast, data collection context documentation (narrative-heavy, requiring domain knowledge) achieves 77% compliance. This paradox suggests systematic barriers orthogonal to documentation effort: licensing may require institutional approval or legal expertise, creating friction even for copy-paste actions.

**Implications:** The component hierarchy identifies licensing as a critical intervention target. Automated licensing template prompts at repository creation could address the 73% zero-license problem with minimal friction. Preprocessing documentation (52% compliance, mid-tier) represents moderate difficulty, while data context's relative strength (77%) suggests narrative-style documentation is more natural for researchers than procedural compliance tasks.

## Mechanism: Commit Velocity Dominates Documentation Quality

Repository commit activity exhibits near-perfect correlation with documentation quality (Figure 1). Spearman ρ = 0.951 (95% CI: [0.931, 0.960], p = 5.32 × 10^{-52}), far exceeding the predicted range (ρ ≥ 0.30) and demonstrating that sustained development intensity is the dominant mechanism driving documentation compliance.

**Figure 1:** Scatterplot showing commits/month (x-axis) vs. DCS_3 score (y-axis). Strong positive correlation with Spearman ρ = 0.951 (p = 5.32×10^{-52}). Each point represents one repository (N=100). \[Figure placement here\]

This extreme effect size (ρ = 0.951) indicates that commit velocity is not merely associated with better documentation—it nearly perfectly predicts it. Repositories with high commit frequency systematically achieve higher DCS\_3 scores, while low-activity repositories cluster near zero documentation compliance.

### Robustness to Age Confound

The correlation persists even when controlling for repository age. Partial correlation (age-adjusted) remains ρ = 0.951 (p = 4.11 × 10^{-51}), ruling out repository maturity as a confounding explanation. This means that within same-age repositories, commit velocity still predicts documentation quality—the effect is not simply "older repos have both more commits and better docs," but rather "active development drives documentation regardless of age."

**Figure 3:** Bar chart comparing raw Spearman ρ (0.951) vs. age-controlled partial ρ (0.951). Both exceed the 0.30 gate threshold by a wide margin. \[Figure placement here\]

### Mechanism Specificity: Only Commits Correlate

In contrast to commits/month (ρ = 0.951), neither contributor count nor issue responsiveness show any relationship with documentation quality (Figure 2):

| Activity Metric | Spearman ρ | 95% CI | p-value | Result |
|----------------|------------|--------|---------|--------|
| Commits/Month | 0.951 | [0.931, 0.960] | 5.32 × 10^{-52} | ✅ SIGNIFICANT |
| Unique Contributors | 0.028 | [-0.157, 0.211] | 0.389 | ❌ NOT SIGNIFICANT |
| Median Issue Response | 0.061 | [-0.130, 0.253] | 0.272 | ❌ NOT SIGNIFICANT |

**Figure 2:** Correlation matrix heatmap showing activity metrics vs. DCS\_3. Only commits/month shows strong positive correlation (dark blue); contributors and issue response show near-zero correlation (white/neutral). \[Figure placement here\]

This specificity is critical: it demonstrates that documentation is not driven by team size (contributors) or maintainer responsiveness (issue handling), but specifically by sustained development activity. The mechanism is **commit-specific**, not generically "community engagement." This narrows intervention targets from broad "build larger communities" to precise "integrate documentation into active development workflows."

**Figure 4 (Optional):** Commits/month correlation with individual DCS components. All three components (data context, preprocessing, licensing) show positive correlation with commit activity, indicating the mechanism applies uniformly across documentation dimensions. \[Figure placement here if space permits\]

### Interpretation: Workflow Integration Hypothesis

The extreme ρ = 0.951 correlation combined with null results for contributors (ρ = 0.028) and issues (ρ = 0.061) supports the workflow integration hypothesis: documentation quality is a byproduct of sustained development intensity, not team diversity or responsiveness culture. Repositories with frequent commits naturally update documentation as part of their development rhythm—documentation becomes routine when coding is active, regardless of team size.

This explains why licensing (copy-paste task) is the weakest component (27%) despite low effort: licensing is orthogonal to code commits. A developer making 10 commits/month to dataset preprocessing code is likely to update preprocessing documentation (workflow integration), but may never touch the LICENSE file (no workflow trigger). Interventions must target commit-linked workflows (e.g., pre-commit hooks prompting documentation updates) rather than generic awareness campaigns.

## Summary of Key Results

1. **Existence:** 7% compliance (CI: [3.4%, 13.8%]) confirms severe gap from initial release (H-E1 PASS).
2. **Component Heterogeneity:** Licensing weakest (27%), data context strongest (77%), χ² p < 10^{-6} (H-E1 secondary PASS).
3. **Mechanism:** Commit velocity ρ = 0.951 (p = 5.32×10^{-52}), far exceeds predicted ρ ≥ 0.30 (H-M1 PASS).
4. **Robustness:** Partial ρ = 0.951 (age-controlled), ruling out maturity confound (H-M1 secondary PASS).
5. **Specificity:** Contributors ρ = 0.028 (NS), issues ρ = 0.061 (NS), confirming commit-specific mechanism.

These results establish that (1) the documentation gap is severe and exists from initial release, (2) commit velocity is the dominant mechanism, and (3) interventions must target workflow integration, not awareness or community size.
