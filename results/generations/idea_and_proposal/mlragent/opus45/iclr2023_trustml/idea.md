# Title: Data-Efficient Calibration via Selective Self-Training under Distribution Shift

## Motivation
Miscalibration—where model confidence poorly reflects actual correctness—poses severe risks in high-stakes domains like healthcare and autonomous systems. This problem is exacerbated under limited labeled data, as calibration methods typically require substantial held-out data for temperature scaling or histogram binning. Furthermore, when deployed models encounter distribution shifts, calibration degrades rapidly. Current self-supervised and semi-supervised approaches improve accuracy but often ignore or worsen calibration. Understanding and addressing the interplay between data scarcity, distribution shift, and calibration is critical for trustworthy deployment.

## Main Idea
We propose **Calibration-Aware Selective Self-Training (CASST)**, a framework that jointly optimizes for accuracy and calibration under limited labeled data and distribution shift. The key insight is that pseudo-labels in self-training should be selected not only based on confidence thresholds but also on their expected impact on calibration.

**Methodology:**
1. Train an initial model on limited labeled source data with focal loss to reduce overconfidence.
2. For unlabeled target data, compute both prediction confidence and calibration uncertainty (via MC dropout or ensemble disagreement).
3. Select pseudo-labels that maximize a calibration-accuracy trade-off objective, filtering samples that would increase expected calibration error (ECE).
4. Iteratively refine the model with calibration-regularized training.

**Expected Outcomes:** Improved ECE and accuracy under 5-10x data reduction compared to standard self-training, validated on medical imaging and autonomous driving benchmarks experiencing natural distribution shifts. This directly enables safer, more reliable ML deployment in resource-constrained settings.