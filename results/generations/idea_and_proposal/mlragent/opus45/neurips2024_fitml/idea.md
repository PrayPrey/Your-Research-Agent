# Title: Rank-Adaptive Fine-Tuning via Gradient-Based Importance Scoring

## Motivation
Low-rank adaptation (LoRA) has become the dominant paradigm for parameter-efficient fine-tuning, yet practitioners face a critical dilemma: selecting the rank hyperparameter. A fixed rank across all layers is suboptimal—different layers contribute unequally to task adaptation, and the optimal rank varies significantly across tasks and model architectures. Current approaches either require expensive grid search or rely on heuristics. This leads to either under-parameterization (poor performance) or over-parameterization (wasted computation and potential overfitting).

## Main Idea
We propose **GradRank**, a dynamic rank allocation method that adaptively determines layer-wise ranks during fine-tuning based on gradient importance scores. The key insight is that gradient magnitudes flowing through low-rank matrices indicate the layer's adaptation capacity needs.

**Methodology:**
1. Initialize all layers with minimal rank (r=1)
2. During training, compute importance scores using accumulated gradient norms for each layer's adaptation matrices
3. Periodically reallocate rank budget: expand high-importance layers by adding new singular vectors, prune low-importance layers
4. Use a global rank budget constraint to maintain efficiency

**Expected Outcomes:**
- Automatic rank selection eliminating hyperparameter tuning
- Better performance-efficiency trade-offs compared to uniform-rank LoRA
- Theoretical analysis connecting gradient importance to task-specific layer sensitivity

**Impact:** This work bridges the gap between theoretical understanding of low-rank representations and practical fine-tuning, enabling more accessible and efficient LLM adaptation.