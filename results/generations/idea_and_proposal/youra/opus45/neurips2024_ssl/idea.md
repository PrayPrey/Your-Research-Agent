# Research Idea

## Title
Capacity-Matched Auxiliary Task Difficulty: A Theory-Driven Framework for Optimizing Self-Supervised Learning

## Motivation
Self-supervised learning (SSL) achieves remarkable empirical success, yet lacks theoretical guidance for selecting auxiliary tasks. A critical unanswered question is: why do certain tasks work better than others? Current SSL design relies on trial-and-error rather than principled selection. We hypothesize that the mismatch between task difficulty and model capacity explains performance variations—tasks too easy yield trivial solutions, while overly hard tasks produce noisy gradients. This gap between SSL theory and practice motivates a principled framework for task selection.

## Main Idea
We propose that optimal SSL performance occurs when auxiliary task difficulty matches model capacity. We introduce the **Training Dynamics Difficulty Index (TDDI)**—measuring normalized loss decrease rate over early epochs—and hypothesize an inverted-U relationship between TDDI/capacity ratio and downstream transfer accuracy.

**Causal mechanism:** Appropriately difficult tasks → meaningful gradient signals → higher effective rank (eRank) of representations → better downstream transfer.

**Methodology:** Test across 4 SSL methods (SimCLR, MoCo, MAE, DINO) and 4 architectures (ResNet/ViT variants) on ImageNet-1K, measuring TDDI, eRank, and linear probe accuracy. Validate via polynomial regression (quadratic vs. linear fit) and mediation analysis.

**Expected impact:** Theory-driven task selection guidelines, potentially improving SSL efficiency by identifying optimal difficulty-capacity configurations without exhaustive hyperparameter search.