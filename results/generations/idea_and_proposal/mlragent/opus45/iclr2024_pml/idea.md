# Title: Adaptive Privacy Budget Allocation for Differentially Private Fine-tuning of Large Language Models

## Motivation
Fine-tuning large language models (LLMs) with differential privacy (DP) often results in significant utility degradation due to uniform privacy budget allocation across all model layers and training steps. Current DP-SGD implementations treat all parameters equally, ignoring that different layers contain varying amounts of sensitive information and contribute differently to model performance. This inefficiency makes privacy-preserving LLM deployment impractical for many real-world applications requiring strict GDPR compliance while maintaining acceptable model quality.

## Main Idea
We propose a dynamic privacy budget allocation framework that intelligently distributes the privacy budget (ε) across layers and training iterations based on gradient sensitivity analysis and layer-wise privacy leakage estimation. 

**Methodology:** (1) Develop a lightweight privacy risk estimator that quantifies per-layer memorization potential using gradient norms and attention patterns; (2) Design an adaptive noise calibration mechanism that injects less noise into layers with lower privacy risk while maintaining the overall privacy guarantee through composition theorems; (3) Implement temporal budget scheduling that allocates more budget to early training phases where gradients are more informative.

**Expected Outcomes:** We anticipate 15-25% improvement in downstream task performance under the same privacy budget compared to vanilla DP-SGD, validated on instruction-tuning benchmarks.

**Impact:** This approach bridges the gap between regulatory compliance and practical LLM deployment, enabling organizations to fine-tune models on sensitive data responsibly.