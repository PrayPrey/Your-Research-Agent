# Title: Compositional Reasoning Probes: Detecting and Steering System-2 Emergence in Transformers

## Motivation
A critical challenge in developing System-2 reasoning is our inability to distinguish when models genuinely compose learned rules versus retrieve memorized patterns. Current benchmarks conflate these mechanisms, making it impossible to know if scaling truly yields systematic reasoning or just broader memorization. Without interpretable signals of compositional processing, we cannot reliably steer models toward genuine reasoning nor ensure AI safety through predictable, rule-following behavior.

## Main Idea
I propose developing **Compositional Reasoning Probes (CRPs)**—lightweight diagnostic classifiers trained on model internals to detect when transformers engage compositional versus retrieval-based processing. 

**Methodology:**
1. Construct controlled synthetic tasks with known compositional structure (e.g., function composition, nested logical operations) where we can definitively separate novel compositions from memorizable patterns
2. Train linear probes on attention patterns and hidden states to predict whether the model's solution path involves genuine composition (measured via held-out structural generalizations)
3. Use probe activations as reward signals for reinforcement learning, actively steering models toward compositional processing modes

**Expected Outcomes:**
- Quantitative metrics distinguishing memorization from rule-application in real-time
- Training procedures that explicitly incentivize System-2 mechanisms
- Interpretable evidence for whether scale genuinely induces compositional reasoning

**Impact:** This provides both a benchmarking solution avoiding contamination issues and a practical mechanism for implementing System-2 reasoning implicitly within models rather than through external scaffolding.