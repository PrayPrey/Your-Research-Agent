# Paper Summary: Distributionally Robust Neural Networks
**Authors:** Sagawa et al. (2020) | **arXiv:** 1911.08731 | **Citations:** ~1500

## Overview
Introduces Group DRO: minimax optimization over worst-group loss. Establishes Waterbirds and CelebA as canonical spurious correlation benchmarks with group annotations. Shows ERM dramatically underperforms on worst-group accuracy despite high average accuracy.

## Key Contributions
- Waterbirds benchmark: landbirds/waterbirds × land/water backgrounds; worst-group (landbirds on water) performance gap up to 40%
- CelebA benchmark: hair color × gender spurious correlation
- Group DRO training: up-weight loss from worst-performing group each step
- Regularization is critical: Group DRO without L2 regularization degrades

## Methodology
- ResNet-50 / BERT baselines
- Group annotations at training time
- Evaluation: average accuracy vs. worst-group accuracy

## Experiments & Results
- ERM: 97% avg / 72% worst-group on Waterbirds
- Group DRO: 91% avg / 91% worst-group on Waterbirds (with tuned regularization)
- Pattern: ERM exploits spurious background feature; Group DRO forces reliance on core feature

## Relevance to Gap 1
Provides the evaluation infrastructure and worst-group accuracy metric that any mechanistic intervention must demonstrate improvement on. The ERM baseline's poor worst-group performance is the downstream consequence of spurious feature acquisition. A mechanistic gradient-level intervention that alters the learning order should improve worst-group accuracy on these benchmarks without group labels.

## Limitations
Requires group labels for training (not annotation-free); no analysis of which training epochs spurious feature reliance is established; no gradient-level mechanistic account.
