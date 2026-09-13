# Research Idea

## Title
Multi-Signal Detection of Spurious Correlations via Training Dynamics and Augmentation Consistency

## Motivation
Deep learning models frequently exploit spurious correlations—superficial patterns that correlate with labels in training data but fail under distribution shift. Current detection methods require expensive group annotations that don't scale and miss unknown spurious features. This creates a critical gap: how can we identify spurious-reliant examples without prior knowledge of what spurious features exist? Understanding this would advance both robust model development and fundamental insights into how neural networks learn shortcuts.

## Main Idea
We propose Multi-Signal Detection (MSD), which identifies spurious-reliant examples by combining two behavioral signatures: (1) fast learning dynamics, measured via loss trajectory slopes and Prediction Depth (the network layer where correct predictions stabilize), and (2) prediction inconsistency under semantic-preserving augmentations. The causal mechanism leverages simplicity bias—spurious features are simpler, learned faster at shallower layers, and produce unstable predictions when augmentations alter superficial cues while preserving core semantics. Neither signal alone is specific: fast learning could indicate easy examples; inconsistency could indicate ambiguity. Their conjunction specifically flags spurious reliance.

We will validate on Waterbirds and CelebA benchmarks, targeting detection AUC >0.75 without group labels and >10% worst-group accuracy improvement after mitigation. Falsification occurs if AUC ≤0.60 or flagged examples show no significant Prediction Depth differences. This enables scalable robustness evaluation for foundation models across modalities.