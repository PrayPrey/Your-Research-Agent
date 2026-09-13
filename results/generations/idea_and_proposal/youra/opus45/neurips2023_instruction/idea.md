# Title
Hierarchical Decomposition Representation Learning (HDRL) for Compositional Generalization in Instruction-Following LLMs

# Motivation
Large language models struggle with compositional generalization—executing novel combinations of known instructions—despite advances in instruction tuning. Current approaches like Chain-of-Thought prompting achieve strong results through explicit decomposition at inference time, but this requires verbose prompting and doesn't address the underlying representation problem. Recent theoretical work (Li, 2025) proves that models must have computational graphs matching compositional structure to generalize. This suggests that supervising internal representations to encode hierarchical task structure could fundamentally improve compositional abilities.

# Main Idea
We propose HDRL, a training objective that supervises hidden states to encode hierarchical sub-task structure derived from Chain-of-Thought annotations. The core mechanism operates through three causal steps: (1) contrastive loss clusters related sub-task representations while separating unrelated ones, (2) this creates decomposition-aware internal processing, and (3) aligned computational graphs enable compositional generalization per theoretical requirements.

**Methodology:** Train LLaMA-7B with auxiliary contrastive loss on hidden states using auto-parsed CoT decomposition annotations (~100K examples). Evaluate on SCAN length splits and novel instruction chains.

**Expected Outcomes:** >90% SCAN accuracy (vs. ~16% baseline), >70% probing accuracy for sub-task identification, and 50-70% inference token reduction versus prompting-based methods.

**Impact:** Establishes representation-level supervision as a principled approach to compositional generalization, complementing inference-time techniques.