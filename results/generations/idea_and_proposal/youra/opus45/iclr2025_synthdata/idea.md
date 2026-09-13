## Title
Synthetic-Guided Adaptive Data Mixing: Closed-Loop Feedback Control for Preventing Model Collapse in Mixed Synthetic-Real Training

## Motivation
Synthetic data offers a promising solution to data access challenges in machine learning, yet training on synthetic-real mixtures risks model collapse—where performance degrades as models overfit to synthetic artifacts. Current approaches use fixed mixing ratios or static curricula, but these cannot adapt to evolving training dynamics. Recent theoretical work proves collapse is inevitable with pure synthetic data, while empirical studies show adaptive curricula outperform fixed approaches by 2-4%. This gap motivates a principled, feedback-driven solution.

## Main Idea
We propose SGADM (Synthetic-Guided Adaptive Data Mixing), a closed-loop controller that dynamically adjusts synthetic-to-real data ratios based on real-time model state signals. The core mechanism uses three feedback signals—loss divergence between synthetic/real data, Expected Calibration Error (ECE), and Maximum Mean Discrepancy (MMD)—to detect distribution drift before collapse onset. A PID-style controller translates these signals into ratio adjustments, reducing synthetic data when divergence exceeds thresholds.

**Key methodology:** Compare SGADM against fixed-ratio baselines and static curricula (DisCL) on ImageNet-LT and iWildCam, measuring downstream accuracy, tail-class preservation, and collapse indicators across 20+ runs.

**Expected outcomes:** 2-5% accuracy improvement over fixed ratios, maintained tail-class accuracy >15%, with <5% computational overhead. This establishes feedback-driven mixing as a principled framework for safe synthetic data utilization.