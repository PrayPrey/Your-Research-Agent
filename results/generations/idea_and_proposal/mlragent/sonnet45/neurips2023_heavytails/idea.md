# Title
Heavy-Tailed Momentum: Leveraging α-Stable Processes for Adaptive Gradient Accumulation

## Motivation
Current optimization algorithms use exponential moving averages for momentum, which implicitly assume light-tailed gradient distributions. However, recent evidence shows that gradients in deep learning naturally exhibit heavy-tailed behavior, especially near critical points and during phase transitions. This mismatch between algorithm design and empirical reality suggests that explicitly modeling heavy tails in momentum could improve optimization dynamics and generalization.

## Main Idea
We propose replacing traditional momentum's exponential smoothing with α-stable Lévy processes, which naturally accommodate heavy tails through their stability parameter α ∈ (0,2]. The key innovation is an adaptive mechanism that:

1. **Estimates tail index**: Use Hill estimator or quantile-based methods to dynamically measure the heavy-tailedness of recent gradient distributions
2. **Adjusts α parameter**: Modulate between Gaussian (α=2, light tails) and Cauchy (α=1, heavy tails) behavior based on measured tail indices
3. **Selective amplification**: Allow occasional large gradient updates during exploration phases while maintaining stability during convergence

**Expected outcomes**: Enhanced escape from sharp minima (improving generalization), faster traversal of flat loss regions, and principled framework connecting heavy-tailed dynamics to implicit regularization. This naturally bridges "edge of stability" phenomena with optimization algorithm design.

**Impact**: Provides theoretically-grounded heavy-tail-aware optimizers that embrace rather than resist the natural heavy-tailed structure of deep learning.