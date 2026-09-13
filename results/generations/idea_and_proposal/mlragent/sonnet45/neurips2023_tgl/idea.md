# Title
Causal Temporal Graph Neural Networks with Counterfactual Reasoning for Robust Event Forecasting

# Motivation
Current temporal graph learning methods excel at capturing correlations but often fail to distinguish genuine causal relationships from spurious correlations in evolving networks. This limitation becomes critical in high-stakes applications like fraud detection and financial forecasting, where models must understand *why* events occur, not just *when* they co-occur. Moreover, temporal graphs are susceptible to distribution shifts and adversarial perturbations, making causality-aware approaches essential for robust predictions. Existing methods lack mechanisms to perform counterfactual reasoning—asking "what would happen if a past interaction didn't occur?"—which is crucial for interpretability and intervention planning.

# Main Idea
We propose a novel framework integrating causal inference with temporal graph neural networks through three key components:

1. **Causal Structure Learning Module**: Automatically discover time-varying causal graphs from temporal interaction data using structural causal models and Granger causality tests, distinguishing causal edges from mere correlations.

2. **Counterfactual Graph Generator**: Generate counterfactual temporal graphs by intervening on learned causal structures, enabling "what-if" analysis and data augmentation for rare events.

3. **Causally-Informed Message Passing**: Design attention mechanisms that prioritize causal neighbors over correlated ones during temporal aggregation, improving robustness to distribution shifts.

Expected outcomes include improved prediction accuracy under domain shifts, enhanced interpretability through causal explanations, and superior performance in anomaly detection tasks. This approach bridges causal reasoning and temporal graph learning, advancing both theoretical understanding and practical applications.