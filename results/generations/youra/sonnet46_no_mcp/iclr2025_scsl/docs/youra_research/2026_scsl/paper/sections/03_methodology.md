# 3. Methodology

## 3.1 Overview

Our measurement framework operationalizes the temporal competition between spurious and core feature learning during standard ERM training. The core tool is **checkpoint linear probing**: at regular intervals during training, we freeze the backbone and train separate linear classifiers (probes) for spurious labels and core labels on a held-out validation split. The difference in probe accuracies, δ(t) = spurious_probe_acc(t) − core_probe_acc(t), constitutes the temporal gap — a time series measuring which feature type dominates the model's representations at each training epoch.

This design choice follows directly from the key insight: if spurious features are simpler (measurably lower complexity) and receive higher gradient signal (gradient dominance), they should be encoded in the backbone's representations before core features. Checkpoint probing makes this encoding visible at each epoch without modifying the training procedure.

**Rationale for linear probing over other analysis tools:** Linear probes test for linear separability in the feature space — precisely what the Simplicity Bias predicts spurious features will achieve first. Nonlinear probes would conflate ease-of-encoding with ease-of-extraction. Gradient-weighted class activation maps (Grad-CAM) and attention analyses provide spatial attribution but not the scalar measurement needed for δ(t) time series. Linear probing with L2-regularized logistic regression provides a reproducible, computationally lightweight measurement that scales to the checkpoint frequency required (every 2 epochs over 30+ epoch training runs).

## 3.2 Formal Definitions

Let $f_\theta^{(t)}$ denote the backbone (ResNet-50) at training epoch $t$, with parameters $\theta^{(t)}$ obtained by standard ERM training. Let $\mathcal{V}$ be a held-out validation split with both spurious labels $y_s$ (e.g., background: ocean/land) and core labels $y_c$ (e.g., bird species: landbird/waterbird).

**Probe training:** For each checkpoint $t$, train two L2-regularized logistic regression probes on the frozen backbone representations $f_\theta^{(t)}(\mathcal{V})$:
- Spurious probe: $h_s^{(t)} = \arg\min_h \mathcal{L}(h(f_\theta^{(t)}(x)), y_s) + \lambda \|h\|_2^2$
- Core probe: $h_c^{(t)} = \arg\min_h \mathcal{L}(h(f_\theta^{(t)}(x)), y_c) + \lambda \|h\|_2^2$

**Temporal gap:** $\delta(t) = \text{acc}(h_s^{(t)}, \mathcal{V}) - \text{acc}(h_c^{(t)}, \mathcal{V})$

**Gap area:** $A = \sum_{t: \delta(t)>0} \delta(t) \cdot \Delta t$, where $\Delta t$ is the checkpoint interval (2 epochs). Measures the total spurious dominance accumulated over training.

**Transition epoch:** $t^* = \min\{t : \delta(\tau) < 0.02 \text{ for } \tau \in \{t, t+\Delta t, t+2\Delta t\}\}$. The first epoch where the temporal gap is consistently negligible for 3 consecutive checkpoints.

**Gradient Dominance Ratio (GDR):** To characterize the gradient mechanism, we instrument the model to track feature-aligned gradient norms. For each training batch, we compute the gradient of the loss with respect to neurons in the final convolutional layer that are most activated by spurious vs. core image regions (identified by spatial activation maps). GDR(t) = ||∇_spurious L||_2 / ||∇_core L||_2, averaged over the batch.

## 3.3 Feature Complexity Characterization

To establish the causal prerequisite — that spurious features ARE simpler than core features — we independently characterize feature complexity using three complementary metrics applied to image patches extracted from the Waterbirds dataset.

**Patch extraction:** Background patches (top 40% of image height, capturing ocean/land texture) are used as spurious feature representatives. Foreground patches (center 60% of image, capturing bird appearance) are used as core feature representatives. This fallback strategy (in lieu of COCO segmentation masks) provides sufficient patch purity given the Waterbirds dataset structure.

**Metric 1 — Spatial Frequency Content (FFT):** We compute the 2D Fast Fourier Transform of each grayscale patch and measure mean spatial frequency (weighted by power spectral density). Lower mean spatial frequency indicates simpler, more homogeneous texture. **Prediction:** spurious patches have lower mean spatial frequency than core patches.

**Metric 2 — Intra-class Variance:** We compute the pixel-level variance within each class's patches. Lower intra-class variance indicates more homogeneous, consistent appearance across instances. **Prediction:** spurious patches have lower intra-class variance than core patches.

**Metric 3 — Linear Separability (Sample Efficiency):** We measure the number of labeled samples required for an L2-regularized logistic regression probe to achieve 90% accuracy on held-out patches. Lower sample count indicates higher linear separability (simpler feature geometry). We report AUC across the full sample-size range as the primary metric, with sample efficiency (N_90%) as a secondary interpretive measure.

Statistical significance for all three metrics is assessed using one-sided t-tests (directional hypothesis: spurious simpler than core) with Bonferroni correction for 3 simultaneous tests (adjusted α = 0.0167 per metric).

## 3.4 Five-Hypothesis Verification Chain

We structure the verification as a sequential causal chain, where each sub-hypothesis is a necessary link in the causal mechanism:

```
H-E1 (Existence):    δ(t) > 0 exists in early training
     ↓ prerequisite
H-M1 (Mechanism 1): GDR > 1.0 in early training (gradient asymmetry)
     ↓ prerequisite
H-M2 (Mechanism 2): Spurious features simpler on ≥2/3 complexity metrics
     ↓ prerequisite
H-M3 (Mechanism 3): t* is reproducible across seeds (std < 10 epochs)
     ↓ prerequisite
H-M4 (Mechanism 4): DFR WGA improvement ∝ epochs trained past t*
```

This chain design ensures that if a later hypothesis fails, earlier confirmed links localize the failure. H-E1 is designated MUST_WORK (pipeline-critical); H-M1 and H-M3 are MUST_WORK; H-M2 and H-M4 are SHOULD_WORK (important but non-blocking).

## 3.5 Training Configuration

**Backbone:** ResNet-50 pretrained on ImageNet (torchvision pretrained weights). Pretraining provides a feature-rich initialization that is standard in the DFR literature.

**Optimizer:** SGD with learning rate 1e-3, momentum 0.9, weight decay 1e-4.

**Training:** Standard ERM on Waterbirds training split. Checkpoints saved every 2 epochs. Probe training at each checkpoint: L2-regularized logistic regression (sklearn, C=1.0) on the held-out validation split.

**Gradient instrumentation:** Per-batch gradient norms tracked for spurious-aligned and core-aligned neurons in the final ResNet-50 convolutional block (layer4), identified by spatial activation magnitude on spurious/core image regions.

**Seeds:** 3 random seeds for all experiments (training initialization + data shuffling). All primary claims verified across all seeds; paired t-tests across seeds for statistical significance.

**Scope:** Proof-of-concept 30-epoch training run on Waterbirds. Full 300-epoch runs are deferred to future work (Section 6.1). CelebA replication was planned but not executed due to network restrictions in the experimental environment (Section 6.2).

## 3.6 DFR Evaluation Protocol

To evaluate the relationship between temporal dynamics and DFR efficacy (H-M4), we train 5 ResNet-50 backbones to different epoch checkpoints: epochs {1, 2, 10, 20, 30}, representing conditions before, at, and after t* (mean t* = 2 epochs). For each checkpoint, we apply DFR: refit the last linear layer using a class-balanced subset of the validation split (50 samples per class, following Kirichenko et al. [2022]). We measure DFR WGA and DFR improvement (DFR WGA − ERM WGA) at each checkpoint. Pearson correlation between improvement and epochs-past-t* tests the hypothesized positive relationship.
