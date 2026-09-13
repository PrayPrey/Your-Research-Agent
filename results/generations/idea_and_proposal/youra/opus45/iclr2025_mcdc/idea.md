## Title
Geometric Mergeability Score: A Predictive Metric for Neural Network Model Merging Success

## Motivation
Current model merging approaches operate blindly—practitioners attempt to combine fine-tuned models without knowing beforehand whether the merge will succeed or catastrophically fail. This trial-and-error process wastes computational resources and hinders collaborative, modular deep learning development. While recent work shows that Linear Mode Connectivity enables successful merging of models sharing a pre-trained base, no unified metric exists to predict mergeability before attempting the merge.

## Main Idea
We propose the Geometric Mergeability Score (GMS), a predictive metric combining three complementary geometric properties: (1) gradient alignment (α) measuring task compatibility via cosine similarity, (2) singular value subspace overlap (β) quantifying shared representational structure, and (3) Fisher information distance (γ) capturing parameter importance similarity. The core hypothesis is that GMS estimates the loss barrier height between models in parameter space—the fundamental determinant of merge success.

**Methodology:** We validate GMS across 30+ model pairs from diverse task families, measuring Spearman correlation with actual merged performance. We test component complementarity through ablation and threshold generalization across domains.

**Expected Outcomes:** GMS achieving ρ > 0.7 correlation with merge success would enable practitioners to pre-screen model pairs, dramatically reducing failed merge attempts and enabling principled collaborative model development—a critical step toward truly modular deep learning systems.