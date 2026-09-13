# Title
Adaptive Mixture-of-Relaxations: Hardware-Aware Dynamic Selection of Differentiable Proxies for Scalable Gradient-Based Learning

# Motivation
Differentiable relaxations enable gradient flow through discrete operations (sorting, ranking, rendering), but existing methods force a rigid trade-off: high-quality relaxations (e.g., permutahedron projection) provide accurate gradients but are computationally expensive at scale, while cheap approximations (e.g., straight-through estimators) are fast but yield poor gradients. Current approaches use static selection, ignoring that optimal relaxations vary by problem scale, hardware platform, and training phase. This creates inefficiencies in large-scale applications like neural architecture search and differentiable physics, where computational costs become prohibitive.

# Main Idea
We propose a Mixture-of-Relaxations (MoR) framework that dynamically selects and interpolates between differentiable relaxation methods during training. A meta-learned switching policy observes runtime profiling data (problem scale, hardware utilization, training phase) and adaptively weights relaxation methods to optimize the gradient quality-cost trade-off. The causal mechanism: contextual signals → policy decision → weighted relaxation combination → improved convergence efficiency.

We test across sorting, rendering, and ranking tasks at scales n=[100-100,000] on GPU/TPU hardware. Predictions: 20-40% training speedup versus always-high-quality baselines while maintaining <2% performance gap; automatic hardware-appropriate selection; phase-aware transitions from cheap (early training) to expensive (late training) relaxations.

Expected impact: 30% faster neural architecture search, scalable differentiable physics simulations, and reduced costs for web-scale learning-to-rank systems.