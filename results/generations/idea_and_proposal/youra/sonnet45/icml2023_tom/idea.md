# Title
POMDP-Based Epistemic State Tracking for Interpretable Theory of Mind in Large Language Models

# Motivation
Current LLMs perform Theory of Mind (ToM) reasoning implicitly within opaque neural representations, limiting interpretability and controllability—critical for high-stakes applications like mental health support and education. While symbolic approaches offer transparency, they lack probabilistic uncertainty quantification. This creates a fundamental gap: we need ToM systems that are simultaneously accurate, interpretable, and capable of representing belief uncertainty. Bridging robotics' 30-year POMDP framework with modern NLP offers a principled solution to enable trustworthy human-AI collaboration.

# Main Idea
We propose integrating an explicit **Epistemic State Tracker (EST)** using Partially Observable Markov Decision Processes with fine-tuned LLMs. The EST maintains probabilistic belief distributions over others' mental states (beliefs, goals) via particle filtering, conditioned on dialogue observations from a learned neural observation model. This neuro-symbolic architecture enables the LLM to generate responses grounded in interpretable, calibrated probability distributions rather than implicit embeddings.

**Core mechanism**: EST provides human-readable belief states that condition LLM generation, combining symbolic transparency with neural flexibility.

**Methodology**: Train observation model on mental state annotations, deploy particle filter (500 particles) for belief tracking, fine-tune 7B LLM on EST-augmented dialogues.

**Expected impact**: ≥5% accuracy gain on ToMBench, 2× higher interpretability ratings, calibrated uncertainty (ECE≤0.15), enabling steerable AI collaboration with computational overhead ≤2×.