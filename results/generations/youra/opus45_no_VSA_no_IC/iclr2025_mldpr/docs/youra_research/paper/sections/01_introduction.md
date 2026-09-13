# Introduction

A simple linear classifier can identify which benchmark was used to fine-tune a vision model with 99.5% accuracy — yet this powerful fingerprint tells us nothing about how well the model will generalize. This paper investigates this paradox: benchmark-specific signatures are massively detectable in model representations, but their relationship to cross-dataset performance degradation is far more complex than previously assumed.

## The Benchmark Concentration Problem

The machine learning community's reliance on a small set of popular benchmarks has raised concerns about whether strong benchmark performance translates to real-world deployment success. Recht et al. (2019) demonstrated that ImageNet-trained classifiers experience 11-14% accuracy drops on carefully replicated test sets, suggesting systematic gaps between benchmark and deployment performance. D'Amour et al. (2020) attributed such failures to underspecification: models with equivalent benchmark performance can diverge dramatically under distribution shift. Wang et al. (2025) showed that ImageNet classifiers learn frequency shortcuts, encoding texture biases rather than shape information.

These findings share a common thread: fine-tuning on narrow benchmark distributions may cause models to encode spurious, benchmark-specific features rather than task-general visual concepts. However, prior work has measured generalization gaps through external evaluation alone. No model-internal metric exists to detect or quantify benchmark-specific encoding before deployment.

## Benchmark Fingerprints: A Representation-Level Analysis

We hypothesize that fine-tuning creates detectable "benchmark fingerprints" in model representations — systematic patterns that reveal training dataset origin. If such fingerprints exist, they could provide a diagnostic tool for identifying models at risk of benchmark overfitting before deployment failure occurs.

To test this hypothesis, we propose a simple methodology: train a linear classifier on penultimate layer representations to predict which benchmark was used for fine-tuning. If benchmark-specific features are encoded, the classifier should achieve above-chance accuracy. We further propose the Benchmark Fingerprint Score (BFS) — the classifier's confidence for the true benchmark — as a candidate metric for fingerprint strength.

## Contributions and Findings

Our investigation yields both a striking positive finding and an important negative result:

1. **Fingerprints are massively detectable.** A logistic regression classifier achieves 99.51% accuracy distinguishing models fine-tuned on Flowers102 versus CIFAR-100, with an effect size of Cohen's d = 698. This far exceeds our 60% threshold and establishes that benchmark fingerprints are not subtle artifacts but dominant signals in representation space.

2. **BFS does not predict generalization gap.** Despite near-perfect fingerprint detection, the correlation between BFS and cross-dataset performance gap is r = 0.022 (p = 0.967). The proposed mechanism linking fingerprint strength to generalization degradation is not supported.

3. **The paradox opens new questions.** Why are fingerprints so detectable yet so uninformative about generalization? We analyze potential explanations including BFS saturation, domain shift confounding, and the possibility that fingerprints are binary rather than graded phenomena.

These findings establish benchmark fingerprints as a measurable phenomenon while highlighting that the mechanistic link between fingerprints and deployment failure remains an open problem. We discuss implications for representation learning evaluation and future directions toward fingerprint-aware training.
