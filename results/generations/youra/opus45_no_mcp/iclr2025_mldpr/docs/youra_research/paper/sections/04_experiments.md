# Experimental Setup

We design experiments to answer three research questions that directly test the benchmark co-evolution hypothesis:

**RQ1:** Do models trained on high-popularity datasets exhibit larger generalization gaps than those trained on low-popularity same-domain datasets?

**RQ2:** Do popular benchmarks attract disproportionate research investment in architecture and hyperparameter optimization?

**RQ3:** Does texture bias explain the mechanism by which optimization intensity leads to generalization failure?

## Datasets

We evaluate on two dataset pairs selected to isolate the effect of popularity within the same domain:

| High-Use | Held-Out | Domain | Popularity Ratio | Selection Rationale |
|----------|----------|--------|------------------|---------------------|
| CIFAR-10 | CINIC-10 | 32×32 natural images | High | Most-studied image classification benchmark; CINIC-10 designed as held-out test |
| SVHN | SVHN-Extra | 32×32 street digits | Low | Lower research attention; SVHN-Extra less optimized |

**CIFAR-10** (60,000 images, 10 classes): Created in 2009, CIFAR-10 has become the canonical benchmark for image classification research. Its extensive use makes it ideal for testing the co-evolution hypothesis.

**CINIC-10** (270,000 images, 10 classes): Combines downsampled ImageNet images with CIFAR-10, using only images not in the original CIFAR-10 training set. Serves as our held-out test for CIFAR-trained models.

**SVHN** (73,257 training, 26,032 test images): Street View House Numbers from Google Street View. Lower popularity than CIFAR-10 despite comparable difficulty.

**SVHN-Extra** (531,131 images): Extended SVHN set with less optimization attention. Serves as held-out test for SVHN-trained models.

## Baselines and Comparisons

### Experiment 1 (H-E1): Generalization Gap
We compare ResNet-18 trained on high-use (CIFAR-10) versus low-use (SVHN) datasets, measuring generalization to respective held-out sets.

### Experiment 2 (H-M1): Research Investment
We compare arXiv paper counts for 10 high-use datasets (by OpenML run-rate) versus 10 low-use datasets from the same repository.

### Experiment 3 (H-M2): Texture Bias Mechanism
We compare texture bias in ResNet-18 (modern architecture, 2015) versus VGG-11 (legacy architecture, 2014) on CIFAR-10.

## Implementation Details

**Framework:** PyTorch 1.13, trained on NVIDIA GPU

**Training Configuration:**
- Optimizer: SGD with momentum 0.9, weight decay 5×10⁻⁴
- Learning rate: 0.1 with cosine annealing to 0.001
- Batch size: 128
- Training epochs: 200 (H-E1), 30 (H-M2)
- Data augmentation: RandomCrop(32, padding=4), RandomHorizontalFlip
- Random seed: 42

**Texture Bias Measurement (H-M2):**
- Style transfer: AdaIN (Adaptive Instance Normalization)
- Texture source: Describable Textures Dataset (DTD), 47 categories
- Conflict stimuli: 10,000 Stylized-CIFAR-10 images with shape-texture conflicts
- Texture bias ratio: proportion of predictions aligned with texture rather than shape

## Evaluation Metrics

**Generalization Gap (H-E1):**
$$\text{gap} = \text{accuracy}_{\text{in-domain}} - \text{accuracy}_{\text{held-out}}$$

A positive gap indicates performance degradation on held-out data. Our hypothesis predicts larger gaps for high-popularity datasets.

**Optimization Paper Ratio (H-M1):**
$$\text{ratio} = \frac{\text{papers}_{\text{high-use}}}{\text{papers}_{\text{low-use}}}$$

Papers retrieved via arXiv API with query: `"{dataset}" AND (architecture OR NAS OR hyperparameter OR optimization)`. Statistical significance via Mann-Whitney U test.

**Texture Bias Ratio (H-M2):**
$$\text{texture\_bias} = \frac{\text{texture\_aligned\_predictions}}{\text{total\_conflict\_stimuli}}$$

On conflict stimuli where shape suggests class A and texture suggests class B, this ratio measures the proportion of texture-driven predictions.

## Success Criteria

| Experiment | Metric | Threshold | Interpretation |
|------------|--------|-----------|----------------|
| H-E1 | Gap difference | > 0 (direction check) | CIFAR gap > SVHN gap supports hypothesis |
| H-M1 | Paper ratio | ≥ 3:1, p < 0.05 | Research investment differential |
| H-M2 | Texture bias diff | ResNet > VGG by 0.05 | Optimization amplifies texture exploitation |
