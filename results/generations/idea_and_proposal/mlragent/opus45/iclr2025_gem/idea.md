# Title: Uncertainty-Guided Adaptive Experimental Design for Protein Engineering

## Motivation
A critical bottleneck in ML-driven protein engineering is the inefficient allocation of expensive wet lab resources. Current generative models propose many candidates, but experimentalists lack principled methods to select which designs to validate. This disconnect leads to wasted experimental cycles on redundant or low-confidence predictions. By explicitly modeling and propagating uncertainty from generative models to experimental selection, we can dramatically improve the hit rate of designed proteins while minimizing costly wet lab iterations.

## Main Idea
We propose an adaptive experimental design framework that integrates epistemic uncertainty quantification from generative protein models into a Bayesian optimization loop for wet lab validation. 

**Methodology:** (1) Train an ensemble of structure-conditioned sequence generators with calibrated uncertainty estimates using deep ensembles or MC dropout. (2) Develop an acquisition function that balances exploitation (high predicted fitness) with exploration (high model uncertainty and sequence diversity). (3) Implement a batch selection algorithm accounting for experimental constraints (synthesis cost, assay throughput). (4) Update the generative model with experimental feedback in successive rounds.

**Expected Outcomes:** We will validate this framework on enzyme engineering tasks, demonstrating 2-3x improvement in identifying functional variants within fixed experimental budgets compared to random or greedy selection.

**Impact:** This directly bridges ML and experimental biology by providing actionable, resource-aware recommendations that experimentalists can immediately implement, accelerating the design-build-test-learn cycle.