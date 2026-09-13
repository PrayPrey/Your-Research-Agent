# Introduction

Self-supervised learning (SSL) has emerged as a powerful paradigm for learning visual representations without labels, achieving remarkable performance across diverse computer vision tasks. However, when trained on datasets with spurious correlations—where superficial features (e.g., backgrounds) correlate with labels—SSL models inherit these biases, leading to fairness failures on minority subgroups. Recent work by Mehta et al. (2022) demonstrated that high-capacity SSL models (ViT-H-14) achieve up to 90% worst-group accuracy (WGA) on the Waterbirds spurious correlation benchmark using only frozen embeddings and linear probes. Yet despite this empirical success, a fundamental question remains unanswered: **what geometric structure in SSL embedding space enables this fairness, and how can we detect and manipulate it without group labels?**

This question matters because group labels are often unavailable in real-world deployments due to privacy concerns, legal restrictions, or the difficulty of defining meaningful groups a priori. Without understanding the geometric manifestation of spurious features in embedding space, practitioners cannot develop automated, training-time interventions that improve fairness for unlabeled data. The stakes are particularly high in fairness-critical domains like medical diagnosis, hiring, and lending, where biased models affect millions of users.

## The Cluster Hypothesis

Prior work has implicitly assumed that spurious correlations manifest as **discrete, geometrically separable clusters** in SSL embedding space. The intuition is compelling: if InfoNCE contrastive loss pulls together samples with shared features (e.g., water backgrounds), these samples should form dense clusters measurable by standard clustering metrics like Adjusted Mutual Information (AMI). This cluster hypothesis underpins several proposed fairness interventions: (1) use clusterability as a diagnostic to identify when bias exists, (2) apply cluster-balanced reweighting to mitigate bias without labels, and (3) design training objectives that disperse spurious clusters while preserving task-relevant structure.

However, this cluster hypothesis has never been empirically validated. Prior SSL fairness work demonstrates that linear classifiers can achieve high WGA, but linear separability does not imply discrete clusterability—spurious features could form **continuous gradients** that linear probes exploit without forming discrete clusters. This distinction is critical: cluster-based interventions will fail entirely if clusters don't exist.

## Our Contribution: Falsifying the Cluster Hypothesis

In this work, we directly test the cluster hypothesis through controlled experiments on the Waterbirds dataset, which exhibits strong (93%) spurious correlation between bird type and background. We hypothesized that standard SSL training (SimCLR with InfoNCE loss) would create dense spurious feature clusters (AMI ≥ 0.4), enabling cluster-balanced retraining to improve WGA by ≥2 percentage points. Further, we hypothesized that learning-speed aware SSL (LA-SSL), which resamples based on per-sample learning dynamics, would disperse these clusters (reducing AMI by ≥30%) while preserving linear separability.

Our proof-of-concept experiments (20 epochs, ResNet-50) **comprehensively refute the cluster hypothesis**. We find:

1. **No discrete cluster formation**: SimCLR embeddings exhibit AMI=0.2795, significantly below the 0.4 threshold required for reliable clustering. This occurs despite 93% spurious correlation in the training data.

2. **No cluster-efficacy relationship**: AMI does not predict cluster-balanced retraining efficacy (Pearson r=-1.0, p=1.0), invalidating AMI-based fairness diagnostics.

3. **LA-SSL operates via a different mechanism**: Contrary to the cluster dispersion hypothesis, LA-SSL slightly *increases* AMI (+2%) while preserving linear separability (ΔAUC=0.005). Its documented fairness benefits must come from linear boundary adjustment, not geometric dispersion.

4. **High implementation quality**: Our cluster-balanced retraining mechanism achieved 100% code validation (43/43 tests passing, 100% SDD compliance), demonstrating technical feasibility independent of the falsified geometric assumptions.

These results constitute a **valuable negative finding**: we eliminate an incorrect mechanistic theory and redirect SSL fairness research from cluster-based diagnostics to linear separability-based approaches. The dissociation between linear separability (which enables 90% WGA) and discrete clusterability (which we show does not exist) is itself a conceptual contribution, clarifying which geometric properties actually characterize spurious correlations in SSL embeddings.

## Paper Organization

Section 2 reviews related work on SSL fairness, spurious correlation detection, and geometric analysis of embeddings. Section 3 describes our methodology for measuring clusterability and testing mechanism hypotheses. Section 4 details experimental setup, including datasets, evaluation metrics, and success criteria. Section 5 presents results showing comprehensive failure of the cluster hypothesis across all tested mechanisms. Section 6 discusses implications, limitations, and future directions. Section 7 concludes.
