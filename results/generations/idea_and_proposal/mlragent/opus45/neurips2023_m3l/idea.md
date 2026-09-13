# Title: Understanding Grokking Through the Lens of Representation Learning Dynamics

## Motivation
Grokking—the phenomenon where neural networks suddenly generalize long after memorizing training data—remains one of the most puzzling observations in deep learning. While recent work has connected grokking to weight norm regularization and representation quality, we lack a unified theoretical framework explaining *when* and *why* this delayed generalization occurs. Understanding grokking is crucial because it reveals fundamental principles about how neural networks transition from memorization to generalization, which could inform more efficient training strategies for large models where prolonged training is prohibitively expensive.

## Main Idea
We propose analyzing grokking through the dynamics of learned representations rather than weight-space metrics. Our key hypothesis is that grokking occurs when the network's internal representations undergo a phase transition from "memorization-compatible" (high-dimensional, sample-specific) to "generalization-compatible" (low-dimensional, structure-aligned) configurations.

**Methodology:** (1) Develop a theoretical framework using representation geometry metrics (e.g., intrinsic dimensionality, class separation) to characterize representation quality during training. (2) Derive conditions under which gradient descent induces representation compression, connecting to implicit regularization theory. (3) Predict grokking timing based on data structure and architecture properties.

**Expected Outcomes:** A predictive theory identifying when grokking will occur based on task complexity, model capacity, and regularization strength—potentially enabling early detection of imminent generalization without extended training.

**Impact:** Practical guidelines for accelerating generalization in foundation model training by engineering favorable representation dynamics.