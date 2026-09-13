# Title: BioDistill: Progressive Knowledge Distillation with Uncertainty-Aware Active Learning for Lab-Deployable Protein Foundation Models

## Motivation
Large protein foundation models (e.g., ESM-2, ProtTrans) achieve remarkable performance but require substantial computational resources beyond typical wet lab capabilities. Standard knowledge distillation produces smaller models with degraded performance, particularly on novel protein families. Meanwhile, biologists need models that not only run efficiently on modest hardware but also provide reliable uncertainty estimates to guide experimental prioritization. Current approaches treat compression and uncertainty quantification as separate problems, missing opportunities for synergy.

## Main Idea
We propose a progressive distillation framework that jointly optimizes for model compression and calibrated uncertainty estimation, specifically designed for lab-in-the-loop workflows. Our approach:

1. **Uncertainty-Guided Distillation**: Train student models using a multi-teacher ensemble, where disagreement between teachers naturally provides uncertainty signals. The student learns both predictions and calibrated confidence scores.

2. **Progressive Compression**: Iteratively distill through intermediate-sized models, preserving critical biological representations at each stage while reducing parameters by 10-50x.

3. **Active Refinement Protocol**: Deploy compressed models with uncertainty estimates to guide which experimental results should trigger model updates, enabling efficient adaptation with minimal wet lab iterations.

Expected outcomes include deployable models running on single GPUs with <8GB memory while maintaining >95% of original performance and well-calibrated uncertainties to prioritize experiments, directly bridging the ML-to-lab gap.