# Methodology

Our methodology tests the benchmark co-evolution hypothesis through three complementary experiments: (1) measuring the popularity-gap correlation across dataset pairs, (2) quantifying research investment differentials, and (3) testing the texture bias mechanism. Each experiment addresses a specific claim in our causal chain.

## Overview

Building on our observation that popular benchmarks may induce benchmark-specific learning, we design experiments that isolate the effect of popularity from confounds such as dataset difficulty, domain differences, and model capacity. Our approach uses naturally occurring variation in dataset popularity within the same domain to test whether higher popularity predicts larger generalization gaps.

## Dataset Popularity Measurement

**Rationale:** Raw download or run counts confound popularity with dataset age. We use *run-rate*—runs per year since dataset creation—as our popularity metric, following OpenML conventions.

**Operationalization:** We query the OpenML API for dataset metadata including `number_of_runs` and `upload_date`, computing run-rate as:

$$\text{run\_rate} = \frac{\text{number\_of\_runs}}{\text{years\_since\_upload}}$$

Datasets are stratified into high-use (top quartile) and low-use (bottom quartile) categories within each domain.

## Dataset Pair Selection

**Rationale:** Testing the popularity hypothesis requires held-out same-domain datasets that were not used for model optimization. We select pairs where one member is heavily used (high run-rate) and the other is less used or specifically designed as a held-out test set.

**Selected Pairs:**

| High-Use | Held-Out | Domain | Design |
|----------|----------|--------|--------|
| CIFAR-10 | CINIC-10 | Natural images (32×32) | CINIC-10 combines ImageNet downsampled + CIFAR; distinct from CIFAR training |
| SVHN | SVHN-Extra | Street digits (32×32) | SVHN-Extra is official extended set; less optimized |

CIFAR-10 represents a high-popularity benchmark (extensively studied since 2009), while SVHN represents a lower-popularity alternative in the same modality.

## Experiment 1: Generalization Gap Measurement (H-E1)

**Hypothesis:** Models trained on high-popularity datasets show larger generalization gaps to held-out same-domain datasets compared to low-popularity datasets.

**Protocol:**
1. Train ResNet-18 on CIFAR-10 for 200 epochs (SGD, lr=0.1, cosine decay)
2. Train identical ResNet-18 on SVHN using same hyperparameters
3. Evaluate CIFAR-10 model on CIFAR-10 test set and CINIC-10
4. Evaluate SVHN model on SVHN test set and SVHN-Extra
5. Compute generalization gap: $\text{gap} = \text{acc}_{\text{in-domain}} - \text{acc}_{\text{held-out}}$

**Success Criterion:** Gap difference > 0 (direction check); full study would require Cohen's d > 0.3, p < 0.05.

## Experiment 2: Research Investment Quantification (H-M1)

**Hypothesis:** Popular benchmarks attract disproportionate optimization research investment.

**Rationale:** If the co-evolution effect operates through research ecosystem dynamics, high-use datasets should have more papers focused on architecture search, hyperparameter optimization, and model design.

**Protocol:**
1. Select 10 high-use and 10 low-use datasets by run-rate
2. Query arXiv via API for optimization-focused papers: `"{dataset}" AND (architecture OR NAS OR hyperparameter OR optimization)`
3. Count papers per dataset over the past 5 years
4. Compare distributions using Mann-Whitney U test

**Success Criterion:** High-use datasets have ≥3:1 more optimization papers (p < 0.05).

## Experiment 3: Texture Bias Mechanism Test (H-M2)

**Hypothesis:** Modern architectures show higher texture bias on popular datasets than legacy architectures, indicating that optimization amplifies artifact exploitation.

**Rationale:** If the co-evolution mechanism operates through texture bias (following Geirhos et al., 2019), then architectures that received more optimization attention should exhibit higher texture reliance.

**Protocol:**
1. Train ResNet-18 (modern, 2015) and VGG-11 (legacy, 2014) on CIFAR-10
2. Create Stylized-CIFAR-10: apply AdaIN style transfer using DTD textures
3. Generate conflict stimuli: images with shape of class A and texture of class B
4. Measure texture bias ratio: proportion of texture-aligned predictions on conflict stimuli

**Success Criterion:** ResNet-18 texture bias > VGG-11 texture bias by at least 0.05.

## Architecture Details

**ResNet-18:** 11.7M parameters, skip connections, batch normalization. Represents modern architecture benefiting from intensive optimization on ImageNet and CIFAR.

**VGG-11:** 9.7M parameters, purely sequential convolutions. Represents pre-ResNet era with less optimization investment.

We match architectures approximately by parameter count to control for capacity differences.

## Training Configuration

All models trained with:
- Optimizer: SGD with momentum 0.9, weight decay 5e-4
- Learning rate: 0.1 with cosine annealing to 0.001
- Batch size: 128
- Data augmentation: RandomCrop(32, padding=4), RandomHorizontalFlip
- Seeds: 42 (single run for proof-of-concept)

## Statistical Analysis

- **H-E1:** Direction check (CIFAR gap > SVHN gap) for PoC; full study would use paired t-test
- **H-M1:** Mann-Whitney U test for paper count distributions
- **H-M2:** Direct comparison of texture bias ratios

## Limitations of Methodology

Our proof-of-concept design prioritizes hypothesis testing over statistical power. Key limitations:

1. **Single run:** H-E1 uses one random seed; effect size estimation requires multiple runs
2. **Two dataset pairs:** Generality claims require more domain coverage
3. **Bibliometric proxy:** Paper counts approximate but do not directly measure optimization intensity

These limitations are acceptable for establishing directional evidence; we discuss required extensions in the Discussion section.
