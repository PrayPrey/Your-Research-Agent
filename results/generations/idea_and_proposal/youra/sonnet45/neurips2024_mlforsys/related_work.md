## Related Work

**Related Papers**

1. **Title**: Algorithmic Learning in a Random World (Vovk 2005 - Conformal Prediction)
   - **Authors**: Not specified
   - **Summary**: Introduced distribution-free prediction intervals with finite-sample coverage guarantees, providing the theoretical foundation for conformal prediction methods.
   - **Year**: 2005

2. **Title**: The scenario approach to robust control design (Calafiore 2006 - Scenario Approach)
   - **Authors**: Not specified
   - **Summary**: Developed scenario-based approximation of chance constraints with probabilistic feasibility guarantees and error bound ε ≤ 0.05 for N=50 scenarios.
   - **Year**: 2006

3. **Title**: Optimization of conditional value-at-risk (Rockafellar 2000 - Conditional Value-at-Risk)
   - **Authors**: Not specified
   - **Summary**: Defined CVaR properties and optimization formulations for financial risk management, providing the theoretical basis for tail risk quantification.
   - **Year**: 2000

4. **Title**: Constrained model predictive control: Stability and optimality (Mayne 2000 - Model Predictive Control)
   - **Authors**: Not specified
   - **Summary**: Established MPC theory including stability, optimality, and receding horizon formulation for control systems.
   - **Year**: 2000

5. **Title**: Carbon-Aware Distributionally Robust Optimization Scheduling (Ruparel 2025)
   - **Authors**: Not specified
   - **Summary**: Proposed distributionally robust optimization with CVaR for carbon scheduling, achieving 10% worst-case carbon reduction by using CVaR for carbon risk quantification.
   - **Year**: 2025

6. **Title**: MPC for Quantum Datacenter Cooling (Heidary 2025)
   - **Authors**: Not specified
   - **Summary**: Applied MPC-based cooling control to reduce facility energy by 9%, demonstrating MPC feasibility in carbon-aware datacenter management systems.
   - **Year**: 2025

7. **Title**: SLIT Multi-Objective LLM Scheduling (Moore 2025)
   - **Authors**: Not specified
   - **Summary**: Co-optimized LLM quality-of-service, carbon emissions, water usage, and energy consumption using ML-based metaheuristic approaches.
   - **Year**: 2025

8. **Title**: The Sunk Carbon Fallacy: Rethinking Carbon Footprint Metrics in Technology (Bashir 2024)
   - **Authors**: Not specified
   - **Summary**: Demonstrated that including embodied carbon in operational decisions can increase total footprint, advocating for operational-only carbon accounting approaches.
   - **Year**: 2024

9. **Title**: AI-Driven Carbon-Aware Scheduling (Siddique 2025)
   - **Authors**: Not specified
   - **Summary**: Combined time-series forecasting (LSTM) with reinforcement learning (PPO) for carbon scheduling, achieving 40% emission reduction with marginal SLA impact.
   - **Year**: 2025

**Key Challenges**

1. **Uncertainty Quantification in Carbon Forecasting**: Existing approaches like Ruparel 2025 use distributional robustness, but lack distribution-free uncertainty quantification methods that don't rely on parametric assumptions for non-parametric carbon intensity data.

2. **Formal SLA Guarantees**: Works like Moore 2025 and Siddique 2025 lack probabilistic guarantees for service-level agreements, making it difficult to provide formal bounds on tail latency violations.

3. **Carbon-Latency Trade-off Framework**: No existing work provides formal Pareto characterization with theoretical bounds for the carbon-latency trade-off space in scheduling systems.

4. **Interactive Workload Focus**: Existing work like Heidary 2025 targets batch cooling systems, leaving a gap for interactive scheduling with real-time constraints (<500ms decision latency).

5. **CVaR Application Domain**: Ruparel 2025 uses CVaR for carbon risk minimization, but CVaR application to SLA tail risk (latency violations) remains unexplored.

6. **Exchangeability in Non-Stationary Carbon Data**: Conformal prediction assumes exchangeability, but carbon intensity data may exhibit non-stationary behavior during grid events (blackouts, extreme weather), potentially violating this assumption.

7. **Computational Tractability**: Real-time scheduling requires <500ms optimization solver latency for interactive workloads, but CVaR-constrained MPC with scenario-based formulations may face scalability challenges.

8. **Generalization Across Grid Types**: Carbon-aware scheduling effectiveness depends on carbon intensity variability, but different power grids (renewable-heavy vs. baseload) have vastly different variability characteristics.
