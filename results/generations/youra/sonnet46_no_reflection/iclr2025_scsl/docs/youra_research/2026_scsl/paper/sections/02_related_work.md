# 2. Related Work

## 2.1 Robustification Methods with Group Annotations

The dominant paradigm for improving worst-group accuracy requires explicit group labels at training time. Distributionally Robust Optimization (DRO) [Ben-Tal et al., 2013] minimizes the worst-case expected loss over a family of distributions; GroupDRO [Sagawa et al., 2020] instantiates this by weighting training samples by group membership, achieving ~90% worst-group accuracy on Waterbirds when group labels are available. Deep Feature Reweighting (DFR) [Kirichenko et al., 2022] takes a different approach: train ERM to convergence, then retrain only the last linear layer on a small group-balanced labeled validation set, achieving ~97% worst-group on Waterbirds and ~92% on CelebA. DFR's success reveals that invariant features are richly encoded in pretrained ERM representations even when the linear head relies on shortcuts — a key observation that motivates our work.

These methods deliver strong performance but require group annotations that are often unavailable in practice. Annotating which samples belong to which spurious group requires either domain expertise (identifying that bird-on-water vs. bird-on-land is the spurious attribute in Waterbirds) or expensive human labeling. Our work specifically targets the annotation-free setting.

## 2.2 Annotation-Free Robustification Methods

Several methods approximate group labels without annotation. Just Train Twice (JTT) [Liu et al., 2021] trains an ERM model and upweights its misclassified examples — assuming that minority-group samples (which rely on spurious features) are disproportionately misclassified. JTT achieves ~82–86% worst-group accuracy on Waterbirds without group labels. Last-Layer Feature Reweighting (LFR) [Ghaznavi et al., 2023] uses a similar loss-based resampling approach and outperforms DFR in high-spuriosity settings. These methods are paradigm-specific (supervised cross-entropy) and use the training loss as a proxy for group membership — a proxy that has no natural extension to self-supervised or contrastive learning.

GEORGE [Bao et al., 2022] takes a representation-based approach: cluster penultimate-layer ERM embeddings at training convergence to discover spurious groups, then apply DRO with the cluster-derived pseudo-labels. PruSC [Kim et al., 2024] applies similar clustering to prune spurious shortcut neurons. AGRO [Yao et al., 2022] adversarially discovers error-prone groups and applies DRO. These methods are conceptually appealing because clustering operates on learned representations rather than loss values, making them paradigm-agnostic in principle.

However, none of these methods characterize the conditions under which the clustering step succeeds. They report results on benchmarks where the method works and treat the detection step as a solved problem. Our work shows this assumption is unjustified: the same clustering protocol that achieves near-perfect spurious group recovery on Waterbirds (purity=0.892) yields near-random performance on CelebA (purity=0.456). This silent failure mode is the central concern we address.

## 2.3 Shortcut Learning Mechanisms and Feature Learning

Shah et al. [2020] establish that SGD exhibits simplicity bias: it preferentially learns high signal-to-noise ratio features early in training, which in spurious-correlation settings corresponds to the spurious attribute. This provides the theoretical foundation for early-epoch probing — by epoch 5, ERM embeddings should already reflect the shortcut feature. Geirhos et al. [2020] document shortcut learning across multiple modalities, showing it is a general phenomenon not specific to any architecture or dataset.

Kirichenko et al. [2022] demonstrate that even fully trained ERM models richly encode invariant features in their representations — shortcuts dominate the linear head but invariant features remain present in the penultimate layer. Our experiment design builds on this: we extract epoch-5 penultimate embeddings specifically because this layer encodes the fullest feature picture, including the spurious attributes that shortcut learning targets early.

Robinson et al. [2023] show that self-supervised learning (SimCLR-style) also acquires spurious correlations through augmentation-invariant shortcuts, motivating cross-paradigm robustification. Our work targets the detection precondition for such robustification.

## 2.4 Gap: Conditionality of Annotation-Free Detection

The key gap our work addresses is the absence of any characterization of when clustering-based annotation-free detection works. The implicit assumption — that spurious features strong enough to degrade worst-group accuracy are also strong enough to produce cluster-separable representations — is never tested. We show this assumption fails for fine-grained texture-based spurious attributes (CelebA hair color) while holding for coarse scene-level spurious attributes (Waterbirds habitat background). The differentiating factor is not dataset spuriosity (both datasets degrade worst-group accuracy substantially under ERM) but the alignment of the spurious attribute with the ImageNet pretraining prior.

This distinction is absent from existing work and constitutes the primary contribution of our paper.
