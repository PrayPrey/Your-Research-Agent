# Research Idea

## Title
Privacy-Aware Synthetic Tabular Data Generation via LLM-Guided Differential Privacy Budget Allocation

## Motivation
While Large Language Models (LLMs) show remarkable capabilities in generating synthetic tabular data, naively applying differential privacy (DP) mechanisms often results in significant utility degradation, particularly for rare subgroups that are already underrepresented. Current approaches apply uniform privacy budgets across all features and samples, ignoring the heterogeneous sensitivity of different columns and the varying privacy risks across demographic groups. This leads to a critical trade-off conflict: protecting privacy while maintaining fairness for minority groups in the synthetic data.

## Main Idea
We propose an LLM-guided adaptive differential privacy framework for synthetic tabular data generation. The key innovation is using LLMs' semantic understanding to intelligently allocate privacy budgets across features and subgroups.

**Methodology:**
1. Leverage LLMs to analyze feature semantics and identify sensitivity levels (e.g., "income" vs. "zip code")
2. Design a fairness-aware budget allocation mechanism that reserves higher utility budgets for underrepresented groups while maintaining overall DP guarantees
3. Use LLMs to generate realistic synthetic samples conditioned on protected attributes, with group-specific noise calibration

**Expected Outcomes:**
- Improved utility-privacy trade-off compared to uniform DP baselines
- Better demographic parity in synthetic data quality across subgroups
- Validated on healthcare and financial benchmark datasets

**Impact:** This work bridges the gap between privacy preservation and fairness in synthetic data, enabling trustworthy ML in sensitive domains.