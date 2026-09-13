# Title: Phase Transitions in Simplicity Bias: Understanding the Competition Between Feature Learning Stages

## Motivation
Deep neural networks exhibit a well-documented simplicity bias, learning simple features before complex ones. However, the precise dynamics governing *when* and *how* networks transition between learning different feature complexities remain poorly understood. This transition appears to involve competition between structures at different complexity scales, potentially explaining phenomena like grokking, neural scaling laws plateaus, and the emergence of reasoning capabilities. Understanding these phase transitions is crucial for predicting training dynamics and designing more efficient learning curricula.

## Main Idea
I propose developing a mathematical framework analyzing the competition dynamics between feature learning stages in high-dimensional settings. The approach combines:

1. **Mean-field analysis** of networks learning hierarchical features (e.g., low-frequency vs. high-frequency components), deriving coupled ODEs that capture inter-stage competition as a function of width, depth, and data complexity.

2. **Phase diagram characterization** identifying critical points where networks transition from one dominant feature class to another, parameterized by learning rate, batch size, and architecture choices.

3. **Empirical validation** tracking feature complexity evolution in transformers during training, correlating identified phase transitions with emergent capabilities.

Expected outcomes include predictive equations for transition timing, principled methods for accelerating transitions (curriculum design), and explanations for why certain hyperparameter regimes produce staircase-like learning curves. This connects optimizer geometry to the sequential emergence of increasingly abstract representations, with direct implications for efficient training of reasoning-capable models.