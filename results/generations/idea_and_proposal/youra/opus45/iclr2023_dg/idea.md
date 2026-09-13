# Research Idea

## Title
Gradient-Based Causal Feature Scoring for Domain Generalization via Cross-Domain Variance Analysis

## Motivation
Domain generalization (DG) methods have struggled to consistently outperform simple empirical risk minimization (ERM), suggesting that additional information is needed for robust out-of-distribution performance. While gradient-based invariance methods like IRM exist, they lack interpretability and fail when test domains differ significantly from training. A key gap exists: we need a principled, interpretable mechanism to identify which features represent stable causal relationships versus spurious domain-specific correlations.

## Main Idea
We propose Gradient-based Causal Feature Scoring (GCFS), which computes per-feature gradient variance across training domains to distinguish causal from spurious features. The core insight: causal features maintain stable gradient-to-label relationships across domains (low variance), while spurious features show high gradient variance due to domain-specific correlations.

**Methodology:** For each feature, compute CausalScore = 1/(1+Var), where Var measures gradient variance across domains. Features are then weighted by their CausalScores during inference.

**Causal Mechanism:** (1) Gradient computation captures feature-label relationships per domain → (2) Cross-domain variance identifies relationship stability → (3) Weighting emphasizes invariant features → improved OOD accuracy.

**Expected Outcomes:** OOD accuracy exceeding 72% on DomainBed benchmarks (vs. ~69% ERM baseline), with interpretable feature importance scores. Validation includes correlation analysis between CausalScores and ground-truth causal features on synthetic datasets (target ρ > 0.6).