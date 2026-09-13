# Research Idea

## Title
Hierarchical Explainable Multi-Agent Reinforcement Learning for Regulatory-Compliant Financial Trading via Active Inference

## Motivation
Financial AI systems face a critical tension: multi-agent trading algorithms achieve strong performance but lack the transparent decision trails required by regulations like EU AI Act and MiFID II. Current post-hoc explanation methods (SHAP/LIME) provide feature importance but cannot trace causal decision processes, achieving only ~30% audit completeness. This gap threatens both regulatory compliance and operator trust in automated trading systems.

## Main Idea
We propose replacing standard RL agents with Active Inference-based agents whose decisions naturally decompose via expected free energy minimization. The core mechanism: free energy mathematically separates into interpretable pragmatic (exploitation/reward-seeking) and epistemic (exploration/uncertainty-reduction) components, creating inherent audit trails without post-hoc approximation.

The approach enables three-level hierarchical explanations: (1) agent-level free energy decomposition, (2) interaction-level belief propagation traces between agents, and (3) system-level collective behavior landscapes. We will validate using multi-agent market simulations with 10-50 agents on public limit order book data.

**Expected outcomes:** >90% audit trail completeness (vs. <30% baseline), ≥50% compliance officer trust improvement, while maintaining trading performance within ±5% of standard MARL. **Falsification criteria:** completeness ≤50% or Sharpe ratio degradation >10% rejects the hypothesis.

This bridges the explainability-performance gap for regulatory-compliant financial AI.