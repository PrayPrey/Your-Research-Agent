# Paper Summary: Shortcut Learning in Deep Neural Networks
**Authors:** Geirhos et al. (2020) | **arXiv:** 2004.07780 | **Citations:** ~2000

## Overview
Defines and taxonomizes shortcut learning: DNNs exploit predictive features that are spuriously correlated with labels in training data but do not generalize causally. The paper establishes the phenomenology without mechanistic gradient-level account.

## Key Contributions
- Taxonomy: textures vs. shapes in ImageNet models; spurious correlations in NLP; contextual biases in vision
- Demonstrates shortcuts arise even when models achieve high training accuracy
- Proposes "out-of-distribution generalization" as the evaluation criterion

## Methodology
- Controlled texture/shape conflict stimuli (Stylized-ImageNet)
- Evaluation on multiple OOD test sets
- Human comparison studies

## Experiments & Results
- ResNet-50 trained on ImageNet shows >90% texture bias; humans show >95% shape bias
- Style transfer training reduces texture bias and improves OOD performance
- Shortcut reliance is not an artifact of small models — scales to large architectures

## Relevance to Gap 1
Establishes that shortcut learning is a systematic property of ERM/SGD but does NOT explain the gradient-level mechanism by which spurious features are acquired first. The temporal ordering (spurious early, core late) is observed but not mechanistically explained.

## Limitations
No gradient trajectory analysis; no per-epoch feature learning order characterization on controlled spurious correlation benchmarks (Waterbirds, CelebA).
