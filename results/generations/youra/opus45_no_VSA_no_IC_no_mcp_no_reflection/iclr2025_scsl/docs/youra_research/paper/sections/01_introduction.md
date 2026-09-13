# Introduction

Gradient-based interventions for spurious correlation robustness promise single-run training without group labels—but our experiments reveal a critical measurement challenge: naive gradient subspace accumulation produces representations too low-rank to distinguish spurious from core feature directions. When we expected clear separation (>70% spurious alignment vs <30% core alignment based on simplicity bias theory), we observed both at approximately 5%—essentially indistinguishable from random projection.

This finding matters because methods claiming to exploit training dynamics for robustness may be measuring noise rather than meaningful signal. Without understanding minimum requirements for gradient subspace analysis, researchers risk investing effort in fundamentally flawed approaches that cannot be validated.

## The Problem

Deep neural networks trained with empirical risk minimization (ERM) reliably learn spurious correlations—shortcuts that achieve low training loss but fail on minority groups. On the Waterbirds benchmark, ERM models learn to associate waterbirds with water backgrounds (95% correlation in training data), achieving only 60% worst-group accuracy when waterbirds appear on land backgrounds.

Existing solutions require resources unavailable in many practical settings. Group DRO needs group annotations during training. Just Train Twice (JTT) requires two complete training runs. Deep Feature Reweighting (DFR) needs held-out data with group labels for last-layer retraining. The promise of training dynamics exploitation—intervening on gradients during a single training run without any labels—remains unrealized.

The deeper problem is that we do not know whether gradient subspace methods can even distinguish spurious from core feature directions. Simplicity bias theory predicts that early training gradients should point toward spurious (simpler) features, but this has been assumed rather than measured. Before designing gradient orthogonalization methods, we need validated measurement apparatus.

## Our Investigation

We tested the foundational assumption underlying Progressive Gradient Orthogonalization (PGO): that early gradient subspaces primarily capture spurious feature directions. We trained ResNet-50 on Waterbirds, accumulated gradients during epochs 1-10, computed a top-50 SVD subspace, and measured alignment with spurious (background-varying) and core (bird-type-varying) gradient directions.

The result was unexpected. Both alignments registered at approximately 0.05—far below the 0.70 and 0.30 thresholds predicted by simplicity bias theory, and statistically indistinguishable from each other. Investigation revealed the cause: accumulating only one gradient per epoch produced a 10-dimensional subspace in a 25-million-parameter space. This is insufficient to capture meaningful variance in any direction. The measurement apparatus failed before the hypothesis could be tested.

## Contributions

This investigation yields a methodological constraint rather than a positive result:

1. We demonstrate that gradient subspace analysis in high-dimensional parameter spaces requires sufficient sample density—single gradients per epoch produce subspaces too low-rank for meaningful directional analysis.

2. We document the minimum requirements for valid gradient subspace measurement: multi-batch accumulation within early epochs, not single-batch per epoch sampling.

3. We provide a template for future gradient-based robustification work to validate measurement apparatus before testing hypotheses.

The Progressive Gradient Orthogonalization hypothesis remains unverified. What we establish is what valid testing requires. Future work should accumulate gradients across all batches during early epochs using streaming SVD before attempting to measure spurious-core separation.
