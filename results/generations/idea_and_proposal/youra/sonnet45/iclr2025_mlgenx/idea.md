# Research Idea: Reinforcement Learning from Biological Feedback for Genomics Foundation Models

## Title
Reinforcement Learning from Biological Feedback (RLBF): Aligning Genomics Foundation Models with Experimental Outcomes for Perturbation Prediction

## Motivation
Drug discovery suffers from high clinical trial failure rates partly because computational models fail to predict real-world biological outcomes. While genomics foundation models like scGPT show promise for perturbation prediction, they rely on supervised fine-tuning that cannot directly optimize for experimental success. Existing methods lack mechanisms to align predictions with actual biological validity and experimental outcomes, limiting their practical utility in target identification and drug design.

## Main Idea
We propose adapting reinforcement learning from human feedback (RLHF) to genomics by training foundation models with **biological feedback** from experimental outcomes. Using scGPT fine-tuned on LINCS L1000 perturbation data (1.3M profiles), we construct pairwise comparisons of successful versus failed perturbations to train an ensemble of five Bradley-Terry reward models. These models learn to predict biological validity by combining experimental outcomes with validated computational metrics (QED, docking scores, synthetic accessibility). 

Through Proximal Policy Optimization (PPO) with KL-divergence regularization, the model iteratively improves perturbation predictions while preserving pretrained biological knowledge. We hypothesize this reward-based optimization will achieve ≥5% higher prediction accuracy and ≥10% better experimental validation rates versus supervised fine-tuning baselines, because policy optimization directly aligns model outputs with experimental success signals rather than merely fitting labeled data. Validation includes 130K held-out predictions and 200 experimental tests, establishing whether RL mechanisms can bridge the gap between computational predictions and biological reality.