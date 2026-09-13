# Title
Bias Competition Dynamics: Tracking Phase Transitions in Deep Learning via Multi-Axis Order Parameters

# Motivation
Deep neural networks exhibit complex learning dynamics including phenomena like grokking, double descent, and simplicity bias, yet we lack unified frameworks to predict when and why networks transition between different learning regimes. Current approaches analyze single biases (frequency or complexity) in isolation, missing the competitive dynamics that govern real training. Understanding these transitions would enable better training diagnostics, hyperparameter selection, and architectural choices.

# Main Idea
We hypothesize that training dynamics can be characterized by tracking two coupled order parameters: Spectral Smoothness Ratio (SSR, measuring frequency bias) and Linear Region Density (LRD, measuring complexity bias). Under gradient flow, these parameters follow predictable trajectories in phase space, with detectable crossings corresponding to behavioral phase transitions (e.g., memorization-to-generalization shifts).

**Core mechanism:** Architecture and data determine initial (SSR, LRD) positions; SGD/Adam induces coupled dynamics where different function classes experience varying gradient pressures at different stages, causing systematic bias switches at trajectory crossings.

**Methodology:** Track SSR via Fourier analysis and LRD via linear region counting across MLPs/CNNs on modular arithmetic and vision tasks, varying weight decay to test coupling predictions.

**Expected outcomes:** ≥70% of detected phase transitions correspond to observable behavioral changes; framework predicts dominant bias and transition timing within ±10% accuracy. This would provide the first multi-axis dynamical framework for understanding bias competition in deep learning.