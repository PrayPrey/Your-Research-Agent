# Experimental Setup

We design experiments to answer three research questions that directly test our claims about attribution method fingerprints:

**RQ1 (Dissociation):** Do attribution methods produce statistically distinguishable mode profiles, with inter-method variance significantly exceeding intra-method variance?

**RQ2 (Stability):** Are mode profiles internally consistent within each method across different test points, exhibiting high split-half reliability?

**RQ3 (Transfer):** Do mode profiles transfer across model architectures, indicating that fingerprints are method-intrinsic rather than model-specific?

## Datasets

We evaluate on CIFAR-10, a standard image classification benchmark with 50,000 training and 10,000 test images across 10 classes. We construct contrastive probe sets isolating each influence mode:

| Probe Type | Construction | # Pairs |
|------------|--------------|---------|
| Memorization | Near-duplicate train-test pairs (high pixel similarity) | 100 |
| Feature Transfer | Same-class pairs with different visual features | 100 |
| Spurious Association | Pairs sharing background/context but different classes | 100 |

**Rationale:** CIFAR-10 provides well-understood visual features enabling controlled probe construction. The three probe types isolate modes that prior work has identified as distinct influence mechanisms.

## Models

We evaluate across three architectures representing distinct computational paradigms:

| Architecture | Parameters | Type | Rationale |
|--------------|------------|------|-----------|
| ResNet-18 | 11M | CNN | Standard convolutional baseline |
| ViT-Small | 22M | Transformer | Attention-based architecture |
| ConvNeXt-Tiny | 28M | Modern CNN | Contemporary design with depthwise separable convolutions |

**Training:** All models fine-tuned from ImageNet pretrained weights using SGD (momentum=0.9, weight decay=5e-4), learning rate 0.1 with cosine annealing, batch size 128. Due to computational constraints (CPU-only execution), we use 5 epochs for proof-of-concept validation.

## Attribution Methods

We compare three methods representing the major computational paradigms:

**TRAK** [Park et al., 2023]: Random projection of gradients using Johnson-Lindenstrauss dimensionality reduction. Projection dimension: 2048.

**TracIn** [Pruthi et al., 2020]: Checkpoint-weighted gradient dot products. We use final checkpoint (adaptation for limited compute).

**Kronfluence** [Grosse et al., 2023]: K-FAC approximated Fisher information inversion. Damping: 1e-4.

**Baseline:** Random attribution (uniform random scores) as null reference.

## Evaluation Metrics

**Primary (RQ1 - Dissociation):**
- F-ratio: Inter-method variance / intra-method variance (threshold: F > 4.0)
- Cohen's d: Maximum pairwise effect size (threshold: d > 0.5)
- p-value: Statistical significance (threshold: p < 0.05)

**Secondary (RQ2 - Stability):**
- Cronbach's α: Split-half reliability per method (threshold: α > 0.8)

**Secondary (RQ3 - Transfer):**
- Pearson r: Cross-architecture correlation per method (threshold: r > 0.7)

## Experimental Protocol

For RQ1, we run 10 independent trials per method with different random seeds, computing mode profiles for each trial. We then apply one-way ANOVA to test whether method identity explains variance beyond random seed variation.

For RQ2, we split probes into two halves and compute mode profiles on each half, measuring correlation to assess internal consistency.

For RQ3, we compute mode profiles for each method on each architecture and measure correlation across architecture pairs.
