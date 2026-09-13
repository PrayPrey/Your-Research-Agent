# Research Idea

## Title
Physics-Constrained Flow Matching with Extreme Value Theory for Physically Consistent Climate Extreme Generation

## Motivation
Climate projections critically depend on accurately simulating extreme events (heat waves, precipitation extremes), yet current AI-based climate models face a fundamental tension: they either satisfy physical conservation laws OR capture statistical tail distributions, but rarely both. Unconstrained generative models produce physically implausible extremes (energy/mass violations ~10⁻²), while physics-constrained approaches underrepresent rare event statistics. This gap limits trustworthy climate risk assessment for adaptation planning.

## Main Idea
We propose EVT-CFM, combining Physics-Constrained Flow Matching (PCFM) with Extreme Value Theory guidance for climate extreme generation. The core mechanism operates through a 4-step causal chain: (1) PCFM projects flow trajectories onto constraint manifolds via Newton iterations during ODE integration, achieving conservation law satisfaction to numerical precision (<10⁻⁶); (2) these physically valid intermediate states enable (3) EVT-parameterized tail guidance using fitted Generalized Pareto Distribution parameters to steer sampling toward statistically correct extremes; (4) the combined mechanism produces events that are simultaneously physically consistent AND statistically accurate.

We will validate on ERA5/CMIP6 data using pretrained climate flow models, measuring conservation violations (<10⁻⁶ target), tail accuracy (QQ-plot R²>0.95), and spatial coherence. Falsification occurs if conservation exceeds 10⁻³ or R²<0.8. This enables trustworthy extreme event generation for climate risk assessment without model retraining.