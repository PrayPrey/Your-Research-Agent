# Research Idea

## Title
Curvature Homeostasis: A Self-Regulating Mechanism Linking Edge of Stability to Generalization in Deep Learning

## Motivation
Despite deep learning's empirical success, understanding why SGD finds generalizing solutions remains theoretically incomplete. The Edge of Stability (EoS) phenomenon—where loss curvature hovers near 2/η during training—has been observed but not mechanistically connected to generalization. Current theories treat sharpness-generalization correlations as coincidental rather than causal. This gap is critical: without understanding the underlying mechanism, practitioners cannot principally select hyperparameters for large-scale models where trial-and-error is prohibitively expensive.

## Main Idea
We hypothesize that SGD implements **curvature homeostasis**: the learning rate η acts as feedback gain in a self-regulating dynamical system that drives Batch Sharpness toward 2/η (Edge of Stochastic Stability). This self-regulation implicitly minimizes curvature complexity C(θ), causing convergence to flat minima with smaller generalization gaps.

**Methodology:** We test a 4-step causal chain: (1) large η exceeds stability threshold → (2) oscillations drive optimizer to low-curvature regions → (3) low curvature reduces PAC-Bayes complexity → (4) tighter generalization bounds. Using overparameterized CNNs on CIFAR-10 with constant learning rates, we measure Batch Sharpness via Hutchinson estimators across 20+ runs per condition.

**Expected Outcomes:** Batch Sharpness stabilizes within ±10% of 2/η, with strong correlations (r>0.7) between sharpness and complexity, and complexity and generalization gap. This provides principled guidance for learning rate selection in large models.