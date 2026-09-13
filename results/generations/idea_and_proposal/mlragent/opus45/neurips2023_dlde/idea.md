# Title: Adaptive Neural ODE Solvers via Meta-Learned Step Size Controllers

## Motivation
Neural ODEs have become fundamental building blocks in modern deep learning, yet their training and inference efficiency remains bottlenecked by numerical integration costs. Current adaptive solvers (e.g., Dormand-Prince) use hand-crafted error controllers that are agnostic to the learned dynamics, often taking unnecessarily small steps in smooth regions or failing to anticipate stiffness. This mismatch between classical numerical heuristics and learned neural dynamics leads to computational waste during both training and deployment, particularly problematic for real-time applications in robotics and time-series forecasting.

## Main Idea
We propose **MetaStep**, a meta-learned step size controller that replaces traditional PI/PID error controllers in adaptive ODE solvers with a small neural network trained across diverse Neural ODE tasks. The controller takes as input local features (current error estimates, Jacobian approximations, step history) and predicts optimal step sizes that minimize total function evaluations while maintaining accuracy guarantees.

**Methodology**: (1) Create a diverse meta-training set of Neural ODE problems spanning different stiffness regimes and dynamics; (2) Train the controller via reinforcement learning to minimize NFEs subject to error constraints; (3) Provide theoretical analysis connecting learned policies to classical stability regions.

**Expected Outcomes**: 30-50% reduction in neural function evaluations with equivalent accuracy, particularly for stiff or multi-scale dynamics common in scientific applications. The controller generalizes across architectures, enabling plug-and-play acceleration for existing Neural ODE models.