# Title: Semantic Entropy Decomposition for Efficient Hallucination Detection in LLMs

## Motivation
Current uncertainty quantification methods for LLMs either require expensive multiple sampling (e.g., semantic entropy) or fail to distinguish between *epistemic uncertainty* (what the model doesn't know) and *aleatoric uncertainty* (inherent ambiguity in the query). This distinction is crucial: epistemic uncertainty signals potential hallucinations requiring human oversight, while aleatoric uncertainty may simply reflect genuine ambiguity. Existing approaches also struggle with computational efficiency at scale, making real-time deployment impractical.

## Main Idea
I propose **Semantic Entropy Decomposition (SED)**, a method that decomposes uncertainty into epistemic and aleatoric components using a single forward pass augmented with lightweight probing. The approach involves:

1. **Training auxiliary probe networks** on intermediate layer representations to predict semantic consistency scores, calibrated against multi-sample semantic entropy ground truth
2. **Decomposition mechanism**: Using contrastive probes trained on questions with known ambiguity levels versus factual queries where the model lacks knowledge
3. **Efficient inference**: At deployment, probes provide real-time epistemic uncertainty estimates without multiple generations

**Expected outcomes**: (1) 10-50x speedup over sampling-based methods; (2) improved hallucination detection by isolating epistemic uncertainty; (3) actionable confidence scores that trigger retrieval augmentation or human review selectively.

**Impact**: Enables practical, real-time uncertainty-aware LLM deployment in high-stakes applications like medical diagnosis assistance.