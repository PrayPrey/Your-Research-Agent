# Research Idea

## Title
Active Inference-Inspired Hierarchical Abstraction for Learning PDDL Domain Models from Experience Traces

## Motivation
A fundamental gap exists between data-driven deep reinforcement learning (strong short-horizon reasoning but poor generalization) and classical AI planning (robust generalization but requiring hand-crafted domain models). Learning symbolic planning representations automatically from experience would bridge this divide, enabling sample-efficient transfer to novel problems. Current approaches either lack differentiability for end-to-end learning or fail to produce interpretable, planner-compatible outputs.

## Main Idea
We propose a hierarchical architecture inspired by active inference that learns PDDL action schemas directly from planning traces. The core mechanism operates through four stages: (1) sparse-attention GNNs encode object-centric state representations with O(n log n) complexity; (2) a three-level active inference hierarchy abstracts these into state predicates, action parameters, and action schemas; (3) Gumbel-Softmax relaxation enables differentiable learning of discrete symbolic structures through temperature annealing; (4) the resulting soft predicates discretize into valid PDDL compatible with classical planners.

The key insight is that active inference's principled uncertainty propagation naturally bridges continuous neural encodings and discrete symbolic representations. We predict >70% planning success on in-distribution problems and >50% on out-of-distribution instances (2-3x larger). Falsification occurs if success drops below 40% or generated PDDL fails parser validation. This approach would enable automated domain model acquisition, dramatically reducing the expertise barrier for deploying classical planning systems.