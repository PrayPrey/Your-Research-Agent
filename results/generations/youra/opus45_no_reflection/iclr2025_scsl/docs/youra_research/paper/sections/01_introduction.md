# Introduction

We set out to detect spurious features by their emergence uniformity — and discovered why this elegant idea fails on pretrained models. The hypothesis was compelling: if spurious features are learned uniformly across training samples (because they correlate with labels regardless of subgroup), while core features emerge differentially, then the coefficient of variation (CV) of probe accuracy trajectories should distinguish them. Our experiments show this approach achieves AUC = 0.0 on Waterbirds using CLIP features — not merely weak, but entirely non-discriminative.

## The Problem

Deep neural networks achieve impressive average accuracy while failing catastrophically on minority groups. On Waterbirds, models learn that "water background" predicts "waterbird" with 95% training correlation, achieving ~95% average accuracy but only ~70% on the worst group (waterbirds on land). This reliance on spurious correlations — statistical patterns that don't reflect causal relationships — undermines model reliability in high-stakes applications.

Existing approaches to spurious correlation mitigation require either group annotations (Group DRO) or two-stage training (JTT, LfF). Group annotations are expensive and often unavailable. Two-stage methods, while effective, introduce computational overhead and hyperparameter sensitivity. A single-run, annotation-free method remains elusive.

## Our Approach

We proposed Emergence Uniformity Regularization (EUR), building on the observation that SGD exhibits simplicity bias — learning simple features before complex ones (Shah et al., 2020). We hypothesized that spurious features, being simpler, would not only emerge *earlier* but also *more uniformly* across sample subsets. Core features, relevant to specific subgroups, would emerge with higher variance.

The proposed detection mechanism: train linear probes on pretrained CLIP features across multiple sample subsets, compute the CV of accuracy improvement rates, and classify features with CV < 0.15 as spurious. The intervention: apply gradient regularization to suppress learning in low-CV directions.

## Key Finding

The detection mechanism fails completely. On Waterbirds with CLIP ViT-B/16 features:

- CV(background/spurious) = 0.0393
- CV(bird\_type/core) = 0.0360
- AUC for CV-based classification = 0.0

Both feature types show nearly identical CV values. The expected pattern (lower CV for spurious features) is absent — indeed, the direction is marginally reversed, though within noise.

## Why It Fails

The root cause is **feature saturation in pretrained models**. CLIP was trained on 400 million image-text pairs. Both "background" (land/water) and "bird type" are elementary visual concepts fully captured in CLIP's feature space. There are no emergence dynamics to measure — both concepts are already learned. Probes converge immediately at all regularization strengths, producing flat trajectories where CV captures only sampling noise.

This reveals a fundamental distinction: *emergence uniformity* is a training-time phenomenon, while *feature separability* is a representation property. C-sweep probing on frozen features measures the latter, not the former.

## Contributions

1. **Negative result with clear attribution**: CV-based spurious detection fails on frozen pretrained features, with AUC = 0.0 on Waterbirds/CLIP.

2. **Mechanistic explanation**: Feature saturation eliminates emergence dynamics; pretrained models are end-states, not windows into learning.

3. **Methodological clarification**: Emergence-based detection requires training-time measurement, not post-hoc probing on pretrained representations.

4. **Design principle**: For emergence uniformity to be measurable, features must be learned during probing, not pre-captured.
