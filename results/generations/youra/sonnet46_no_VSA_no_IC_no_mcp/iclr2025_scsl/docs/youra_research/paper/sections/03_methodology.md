# 3. Methodology

Our goal is to measure how strongly each pretraining paradigm encodes spurious attributes in frozen representations, holding backbone architecture constant. The methodology is designed around a specific concern: label correlation in supervised training could confound naive comparisons, so every design choice is motivated by the need to isolate the pretraining objective effect.

### 3.1 Pretraining Paradigms

We compare four ResNet-50 backbones pretrained on ImageNet-1k under different objectives:

- **Supervised ERM**: Standard cross-entropy classification on ImageNet-1k labels (torchvision `resnet50(pretrained=True)`).
- **MoCo-v3** (contrastive): Momentum-contrast contrastive SSL [He et al., 2020]; official `r-50-1000ep.pth.tar` checkpoint loaded directly.
- **DINO** (self-distillation): Self-distillation with knowledge distillation from a momentum teacher [Caron et al., 2021]; `dino_resnet50` via PyTorch Hub.
- **BarlowTwins** (non-contrastive SSL): Redundancy-reduction via cross-correlation matrix alignment [Zbontar et al., 2021]; official weights loaded from `facebookresearch/barlowtwins`.

All backbones output 2048-dimensional features via global average pooling; the final classification head is removed (`fc=Identity`). Backbones are frozen for all probe experiments — no fine-tuning is performed. This isolates the effect of the pretraining objective from downstream fine-tuning dynamics.

**Why this backbone?** ResNet-50 is used in the original DFR [Kirichenko et al., 2022], Group DRO [Sagawa et al., 2020], and WILDS [Koh et al., 2021] evaluations, providing a direct comparison baseline and ensuring that the same group annotations and evaluation splits apply.

### 3.2 Spurious/Task Probe Accuracy Ratio

For each frozen backbone, we train separate linear probes (logistic regression) to predict the *spurious attribute* and the *task label* from the 2048-dimensional features:

$$\text{ratio} = \frac{\text{spurious\_probe\_acc}}{\text{task\_probe\_acc}}$$

A ratio above 1.0 indicates that the representation encodes the spurious attribute *more strongly relative to the task* than random chance would predict. A higher ratio indicates stronger spurious feature encoding relative to task encoding.

**Why ratio?** Absolute probe accuracies vary across datasets due to difficulty and data quantity. The ratio is scale-free and dataset-agnostic: it captures how spurious encoding compares to task encoding within the same representation, regardless of overall feature quality.

**Why linear probes?** Nonlinear probes could fit spurious structure that is not linearly encoded, obscuring the paradigm effect. Linear probes are the standard in SSL evaluation [Chen et al., 2020; Caron et al., 2021] and provide a direct measure of linearly decodable feature content.

### 3.3 Group-Balanced Probe Protocol

A critical design choice: we train probes on a *group-balanced* subset of the validation split, not the training set.

The Waterbirds training split has 95% spurious correlation — 95% of landbirds appear on land backgrounds, 95% of waterbirds on water. Training a probe on this split would inflate the spurious probe accuracy artificially (the label correlation is spurious but the probe cannot distinguish encoded features from label signal). By using a group-balanced validation subset (equal examples per (task label × spurious attribute) group), we measure only what the frozen features encode, not what the training distribution implies.

Evaluation is performed on the full balanced test split (Waterbirds: 5,794 images, 50% spurious-correlated per class; CelebA: 720 images, 180 per group × 4 groups). Statistical analysis uses 5 random seeds per probe training run; means and standard deviations are reported.

### 3.4 Statistical Analysis

Pairwise comparisons between paradigms use two-sample t-tests across 5 seeds, with Bonferroni correction for 6 pairs (C(4,2)). A pair is considered gate-qualifying if Bonferroni-corrected p < 0.05 **and** mean difference ≥ 0.02 (2 percentage points). Cohen's d with pooled standard deviation quantifies effect size. A one-way ANOVA tests the joint significance of paradigm effects.

Bonferroni correction is conservative but appropriate given the confirmatory nature of the comparison: we pre-registered the paradigm pairs of primary interest (ERM vs MoCo-v3 as the theoretically motivated directional test; ANOVA as the omnibus existence test).

### 3.5 Background-Replacement Augmentation (Mechanism Test)

To directly test the role of augmentation in spurious feature encoding, we train SimCLR from scratch on Waterbirds under two conditions:

- **SimCLR-Original**: Standard augmentation (random crop, horizontal flip, color jitter, grayscale, Gaussian blur)
- **SimCLR-NoBackground**: Same as Original, plus random background replacement using a pool of 10,000 Places365 images

The `BackgroundReplacementTransform` uses CUB-200-2011 segmentation masks to identify foreground pixels and replaces background pixels with a randomly sampled Places365 image. This removes the instance-discriminative signal from background texture in contrastive views, directly testing whether augmentation-invariance over backgrounds reduces spurious probe accuracy.

Both conditions train for 50 epochs with matched hyperparameters (SGD, lr=0.03, batch=256, cosine annealing, NT-Xent temperature=0.5). Mechanism activation is verified by comparing pixel differences between views within and across conditions; the achieved pixel_diff=0.9656 (19× above the 0.05 threshold) confirms the background replacement is unambiguous.

### 3.6 Datasets

**Waterbirds** [Sagawa et al., 2020]: 4,795 training / 1,199 validation / 5,794 test images. Spurious attribute = background type (land vs. water); task = bird species (waterbird vs. landbird). Training set has 95% spurious correlation. Loaded via WILDS 2.0.

**CelebA** [Liu et al., 2015]: 162,770 training / 19,962 test images. Task = Blond_Hair; Spurious attribute = Male. Balanced test set: 720 images (180 per group). Loaded via WILDS format.

These datasets are standard benchmarks in spurious correlation research with publicly available group annotations, making our results directly comparable to Group DRO, DFR, and WILDS baselines.
