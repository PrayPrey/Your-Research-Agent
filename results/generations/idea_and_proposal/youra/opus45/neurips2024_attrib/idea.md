## Title
AttributionBench: A Unified Benchmark for Cross-Paradigm Model Behavior Attribution with Synthetic Ground Truth

## Motivation
Understanding how training data, internal circuits, and learned concepts contribute to model behavior remains fragmented across disconnected research paradigms. Data attribution, mechanistic interpretability, and concept-based methods each provide partial answers but cannot be directly compared—there is no shared evaluation framework with known ground truth. This gap prevents researchers from understanding which attribution approaches are most reliable and when different methods should be applied.

## Main Idea
We propose AttributionBench, a benchmark using synthetic learning tasks where ground truth attribution pathways are known by construction at three levels: which training examples contribute (data), which circuits implement behaviors (mechanistic), and which concepts mediate predictions (concept). The core insight is that synthetic task design can simultaneously control all three attribution dimensions, enabling objective fidelity measurement across heterogeneous methods.

The methodology employs tiered psychometric validation: Tier 1 tests basic identification, Tier 2 tests specificity, and Tier 3 tests counterfactual prediction accuracy. We will evaluate 6-10 attribution methods (TRAK, activation patching, TCAV, etc.) on 4-8 tasks across vision and language modalities using models ≤10B parameters.

Expected outcomes include: (1) validated ground truth achieving >95% inter-rater agreement, (2) meaningful performance differentiation across validation tiers, and (3) stable within-paradigm method rankings (Kendall's τ > 0.7). This enables the first standardized comparison of attribution methods across paradigms, advancing both theoretical understanding and practical method selection.