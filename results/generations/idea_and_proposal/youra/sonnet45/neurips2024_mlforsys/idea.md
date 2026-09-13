# Title
Conformal-CVaR-MPC: Distribution-Free Carbon-Aware Scheduling with Probabilistic SLA Guarantees

# Motivation
Cloud datacenters face a critical challenge: reducing carbon emissions while maintaining strict service-level agreements (SLAs). Existing carbon-aware schedulers either lack formal uncertainty quantification (assuming perfect carbon forecasts) or provide no probabilistic SLA guarantees, leading to either conservative carbon savings or excessive latency violations. Recent work uses machine learning heuristics without theoretical guarantees or applies distributionally robust optimization requiring parametric assumptions. This research addresses the gap by integrating distribution-free uncertainty quantification with formal tail-risk constraints for interactive workloads.

# Main Idea
We propose integrating **conformal prediction** with **CVaR-constrained Model Predictive Control (MPC)** for carbon-aware request scheduling. The core mechanism operates through five causal steps: (1) conformal prediction generates distribution-free 90%-coverage carbon intensity forecast intervals from historical grid data, (2) Monte Carlo sampling converts these intervals into 50 optimization scenarios, (3) Conditional Value-at-Risk (CVaR) at the 95th percentile quantifies tail latency risk as convex constraints, (4) CVXPY+ECOS solver optimizes request delays (0-10s) and server assignments in <500ms, and (5) time-shifting requests to low-carbon windows achieves emissions reduction while CVaR bounds SLA violations.

**Methodology**: 24-hour randomized controlled trial comparing conformal-CVaR-MPC against deterministic and RL baselines using Google cluster traces with California grid data (WattTime API).

**Expected Impact**: 10-20% carbon reduction with <5% SLA violations (vs. 20% for aggressive optimization without guarantees), validated through formal approximation bounds and Pareto frontier analysis across multiple operating points.