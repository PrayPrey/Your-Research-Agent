# Abstract

Reinforcement learning from execution feedback for code generation suffers from sparse rewards: binary test pass/fail signals provide no gradient for partial progress, and all tokens receive uniform credit regardless of their contribution to the outcome. Fine-Grained Optimization (FGO) addresses this by masking non-executed tokens from gradient updates, but prior work conflates FGO with other components (curriculum learning, feedback content), making it impossible to isolate the mechanism's contribution.

We present the first controlled mechanism validation study of FGO. We decompose the technique into three testable components: (1) execution trace collection, (2) gradient exclusion via token masking, and (3) credit assignment to executed tokens. For each component, we establish explicit falsification criteria and verify the mechanism empirically.

Our experiments on HumanEval and MBPP demonstrate that: trace collection achieves 100% capture rate using Python's `sys.settrace`; gradient exclusion is correct, with masked tokens receiving exactly zero gradient in all verification checks; and FGO improves final pass@1 by 10% (0.244 vs. 0.222), with executed tokens receiving 1.78x signal concentration.

The key finding is that FGO's benefit comes from gradient exclusion: non-executed tokens receive exactly zero gradient, while executed tokens receive concentrated learning signal. This mechanism validation approach—decomposing techniques into independently testable components with falsification criteria—provides a template for rigorous evaluation of credit assignment methods in code RL.
