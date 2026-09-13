# Title
EWHEST: Online Heavy-Tail Detection for Predicting Deep Learning Generalization

# Motivation
Heavy-tailed gradient distributions emerge naturally during neural network training and correlate with generalization performance, yet practitioners lack real-time tools to monitor this phenomenon. Existing tail-index estimation methods require offline batch analysis, making them impractical for guiding training decisions. This creates a critical gap: while theory links heavy-tail behavior (tail-index α) to optimization stability and generalization, we cannot measure it efficiently during training to enable early prediction or dynamic intervention.

# Main Idea
We propose EWHEST, an online tail-index estimator combining three techniques: the Hill estimator from extreme value theory, exponentially-weighted moving averages for handling non-stationarity, and CUSUM change-point detection for adaptive windowing across training regimes. The core hypothesis is that EWHEST can accurately estimate α from SGD gradient norms with <10% error and <2% computational overhead, while mid-training estimates (at 50% completion) significantly correlate (ρ>0.6) with final generalization performance.

The causal mechanism: heavy-tailed gradients (induced by learning rate/batch size ratio) enable escape from sharp minima through α-stable noise, with optimal α∈[1.5,2.5] balancing exploration and convergence. We test this across 180 experiments (5 architectures × 4 datasets × 3 hyperparameter regimes), measuring estimation accuracy against offline ground truth, learning rate dependence, and generalization prediction. Success enables practitioners to monitor optimization health in real-time and predict generalization before training completes.