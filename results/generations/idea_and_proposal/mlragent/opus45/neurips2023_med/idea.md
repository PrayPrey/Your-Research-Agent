# Title: Uncertainty-Aware Self-Training for Label-Efficient Medical Image Segmentation

## Motivation
Medical image annotation is extremely costly, requiring expert radiologists and significant time investment. While self-training with pseudo-labels has shown promise in leveraging unlabeled data, naive application to medical imaging often fails due to the high cost of errors—incorrect pseudo-labels can propagate confidently wrong predictions, particularly dangerous in clinical settings where reliability is paramount. Current methods lack principled approaches to quantify and utilize uncertainty when selecting which pseudo-labels to trust, leading to suboptimal performance and unreliable predictions.

## Main Idea
We propose an uncertainty-aware self-training framework that integrates Monte Carlo dropout-based epistemic uncertainty estimation directly into the pseudo-label selection and weighting process. Our method:

1. **Selective Pseudo-Labeling**: Generate pseudo-labels only for regions where predictive uncertainty falls below an adaptive threshold, computed from the distribution of uncertainties across the dataset.

2. **Uncertainty-Weighted Loss**: Weight the contribution of each pseudo-labeled pixel inversely proportional to its uncertainty, allowing the model to learn more from confident predictions.

3. **Curriculum Strategy**: Progressively lower uncertainty thresholds as training proceeds, expanding the pseudo-labeled set as the model improves.

We evaluate on cardiac MRI and chest X-ray segmentation tasks with only 5-10% labeled data. Expected outcomes include achieving 90%+ of fully-supervised performance while providing calibrated uncertainty maps for clinical decision support.