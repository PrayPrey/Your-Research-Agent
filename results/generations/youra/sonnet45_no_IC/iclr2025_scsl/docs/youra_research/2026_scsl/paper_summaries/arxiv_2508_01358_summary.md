# An Empirical Validation of Open Source Repository Stability Metrics

## Key Metadata
- **Authors:** Adejumo & Johnson
- **Year:** 2025
- **Venue:** arXiv
- **Core Contribution:** First empirical validation of control-theoretic stability metrics for OSS health assessment

## Section Summaries

### Abstract
Validates Composite Stability Index (CSI) using control theory lens for 100 GitHub repositories. Findings: weekly (not daily) commit frequency sampling more feasible; median-based statistics improve issue/PR stability indices. Proposes data-driven recommendations for applying control theory to OSS health assessment.

### Introduction & Motivation
OSS sustainability critical as software depends on thousands of dependencies. Existing metrics (stars, forks) insufficient for maintenance status prediction. Control theory provides mathematical framework for system stability analysis. Gap: no empirical validation of control-theoretic metrics on real OSS repositories. Research questions: Can control theory metrics predict maintenance status? What sampling frequencies work? Which stability indicators most reliable?

### Methodology
**Control Theory Framework:** Stability = ability to return to equilibrium state after perturbation. Applies concepts: (1) Commit frequency as system output, (2) Issue resolution rate as feedback signal, (3) PR merge rate as control input, (4) Community engagement as external forcing.

**Composite Stability Index (CSI):** Combines 4 normalized sub-indices (0-1 scale): Commit Stability Index (CSI_C), Issue Stability Index (CSI_I), PR Stability Index (CSI_PR), Community Engagement Index (CSI_CE). Final CSI = weighted average with domain-specific weights.

**Dataset:** 100 highly-ranked GitHub repositories spanning multiple domains (web frameworks, ML libraries, DevOps tools). Criteria: >1000 stars, active >2 years, non-fork. Monthly data collection over 24-month observation window.

**Sampling Strategies:** Tested daily, weekly, monthly commit frequency sampling. Metric aggregation: mean vs median statistics for issue/PR resolution times.

### Experiments & Results
**Commit Frequency Stability:** Weekly sampling optimal balance between noise reduction and responsiveness. Daily sampling high variance (±40%), monthly sampling misses short-term fluctuations. CSI_C with weekly sampling: coefficient of variation 0.18 (stable) vs 0.45 (daily, unstable).

**Issue Resolution Stability:** Median resolution time more robust than mean (outliers from abandoned issues skew mean). Median-based CSI_I Spearman ρ = 0.67 with manual maintenance labels vs ρ = 0.42 for mean-based. Threshold: median <30 days indicates healthy issue management.

**PR Merge Rate:** Strong correlation with commit activity (ρ = 0.58). Weekly PR merge rate CSI_PR captures collaboration health. Threshold: >5 PRs/week for active repositories.

**Community Engagement:** Contributors, issue comments, discussion threads. Median monthly active contributors most predictive (ρ = 0.71 with repository health labels). CSI_CE based on contributor diversity (Gini coefficient) + engagement breadth (comment distribution).

**Validation:** Manual labels (maintained/stagnant/deprecated) for 100 repos. CSI binary classification (threshold=0.6): Precision 0.82, Recall 0.78, F1 0.80. Baseline (stars-based) F1 0.65. Statistical tests: Kruskal-Wallis H-test shows CSI significantly distinguishes groups (p < 0.001).

### Discussion & Conclusion
Control theory lens successfully models OSS stability. Weekly commit sampling practical middle ground. Median-based statistics essential for robustness against outliers. Future work: expand to 1000+ repos, incorporate network centrality (like HITS), test cross-platform (GitLab, Bitbucket).

## Key Contributions
- First empirical validation of control-theoretic stability metrics on real OSS data
- Data-driven sampling frequency recommendations (weekly > daily/monthly)
- Median-based metric formulations for outlier robustness
- Composite Stability Index achieving F1 0.80 for maintenance classification

## Potential Relevance
Provides validated framework for repository maintenance status definition using stability indices. Weekly commit frequency and median resolution times directly applicable to binary maintenance classification. CSI threshold approach offers alternative to timestamp-based definitions (6-month/1-year last commit).
