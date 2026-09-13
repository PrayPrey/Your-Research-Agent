# Research Idea

## Title
SGD-Driven Attractor Dynamics Explain Representation Convergence Across Neural Network Initializations

## Motivation
Neural networks trained on identical tasks with different random initializations consistently develop similar internal representations—a phenomenon observed across biological and artificial systems. Understanding *why* this convergence occurs remains an open question with significant implications for model merging, transfer learning, and modular deep learning. Current approaches measure similarity post-hoc without explaining the underlying mechanism, limiting our ability to predict or control representation alignment.

## Main Idea
We hypothesize that representation convergence emerges because SGD noise acts as an exploration mechanism guiding training trajectories into overlapping attractor basins, where basin structure is determined by task/data statistics. Our three-step causal mechanism proposes: (1) task statistics shape loss landscape geometry, creating task-optimal attractor basins; (2) SGD stochasticity enables different initializations to discover common low-loss regions; (3) convergence to shared basins produces high representation similarity (CKA > 0.8).

We will verify this by training networks (ResNet, ViT, MLP) across multiple seeds on standard benchmarks, measuring pairwise CKA at the penultimate layer. Key predictions include: mean CKA > 0.8 for same-task pairs, early-epoch CKA predicting final similarity (r > 0.6), and higher task complexity yielding greater CKA variance. Falsification occurs if CKA < 0.6 or high CKA fails to correlate with prediction agreement. This framework enables principled prediction of representation alignment, advancing model merging and cross-modal transfer applications.