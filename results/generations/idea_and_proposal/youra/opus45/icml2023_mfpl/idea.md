# Research Idea

## Title
Shapley-Weighted Direct Preference Optimization for Fair LLM Alignment

## Motivation
Large language models aligned via preference learning (DPO/RLHF) often exhibit demographic disparities—performing better for majority groups whose preferences dominate training data. Current fairness approaches use ad-hoc constraints lacking principled justification. Meanwhile, Shapley values from cooperative game theory uniquely satisfy fairness axioms (efficiency, symmetry, additivity) that guarantee proportional contribution-based representation. This creates an opportunity to bridge social choice theory with preference-based LLM alignment.

## Main Idea
We propose Shapley-Weighted DPO (SW-DPO), which reweights the DPO loss function using Shapley values computed per demographic group. The mechanism operates in three steps: (1) compute each group's marginal contribution to reward model accuracy via gradient-based Shapley approximation, (2) identify underrepresented groups with lower Shapley values, and (3) apply inverse-proportional weights to the loss function, ensuring groups contributing less receive amplified training signal.

**Core hypothesis:** SW-DPO will reduce demographic disparity (Gini coefficient) by ≥20% while maintaining ≥95% of baseline alignment accuracy, because Shapley axioms mathematically guarantee fair contribution attribution.

**Methodology:** Compare SW-DPO against standard DPO, FARO, and GRPO across demographic-labeled preference datasets using paired experiments (20 runs, 5 seeds × 4 demographic configurations).

**Expected impact:** A principled, axiomatically-grounded approach to fair preference learning applicable beyond LLMs to recommender systems and robotics.