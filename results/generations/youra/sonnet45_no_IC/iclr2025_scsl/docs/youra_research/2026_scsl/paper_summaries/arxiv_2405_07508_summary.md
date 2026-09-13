# Revealing the value of Repository Centrality in lifespan prediction of Open Source Software Projects

## Key Metadata
- **Authors:** He et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** Novel HITS-based repository centrality metric predicts OSS project deprecation via survival analysis

## Section Summaries

### Abstract
Proposes repository centrality metric using HITS (Hyperlink-Induced Topic Search) algorithm on user-repository star network to predict project deprecation. Dataset of 103,354 non-fork GitHub OSS projects (2011-2023). Gradient boosting + deep learning survival analysis models achieve satisfactory accuracy. Drop in HITS weights indicates increased deprecation risk. Repository centrality most significant feature among all predictors.

### Introduction & Motivation
91% of analyzed dependencies show no maintenance in 2 years. Repository deprecation triggers domino effect weakening software supply chain (e.g., left-pad incident). Existing techniques focus on static point-in-time features with limited effects. Need temporal dynamics capturing popularity shifts over continuous periods to predict deprecation and enable proactive measures.

### Methodology
**Data Collection:** 51,677 deprecated repos (archived OR deprecation keywords detected via SetFit classifier with 0.96 accuracy) + 51,677 comparison repos. Monthly statistics from GHArchive (2011-2023) stored in ClickHouse for efficient retrieval.

**Repository Centrality Metric:** HITS algorithm on bipartite user-repository star graph. Users = Hubs, Repositories = Authorities. Iterative weight aggregation: Auth(p) = Σ Hub(q), Hub(p) = Σ Auth(p). Composite metric: raw HITS weight + rank-normalized (percentile) + z-score normalized (log-transformed). Normalization handles long-tail distribution and temporal variance. Computed via Spark cluster (1000 core-hours for decade-long monthly HITS).

**Features:** 9 features across 3 dimensions: (1) Development (commits, tags), (2) Collaboration (issues, PRs, comments), (3) Community Attention (stars, HITS weight, Weight%, Weightz). Spearman correlation shows HITS weakly correlated with existing metrics (ρ < 0.4), capturing unique characteristics.

**Models:** (1) XGBoost AFT (Accelerated Failure Time) predicts survival time. Training: 80/20 split, nloglik loss, 50 iterations with early stopping. (2) DRSA (Deep Recurrent Survival Analysis) RNN predicts hazard rate from 10-month sequential features. Training: batch=64, lr=0.015, 1000 epochs.

### Experiments & Results
**AFT Model:** C-Index = 0.810 on test set (strong discriminatory power). Feature importance: HITS weight highest F-Score (600+), followed by stars (~460). SHAP values confirm HITS + Weightz strongest effect. Ablation: Full model C-Index 0.810, removing HITS → 0.755 (-6.8%), removing other features → <0.5% drop. HITS unique role confirmed.

**DRSA Model:** Accurate hazard rate predictions. Example: Stopwatch repo predicted 73% hazard rate 9 months ahead, actual archive within 1 month. mr4c predicted <50% hazard (safe), actually archived 5 years later. Full model C-Index improvement +9.3% vs baseline, removing HITS → -6.9% drop.

**Preliminary Analysis:** Top 10 repos by HITS (7/10 software projects: tensorflow, vue, vscode) vs Stars (9/10 non-software: tutorials, 996.ICU protest). Brackets case study: stars remained high despite decline, HITS steadily declined since 2015 matching deprecation trajectory. Δ