# Related Work

We position our work at the intersection of efficient attention mechanisms and mechanism validation in deep learning. While numerous efficient attention variants exist, systematic testing of their proposed mechanisms remains rare.

## Efficient Attention Mechanisms

Standard transformer attention computes pairwise interactions across all positions, yielding O(n²) complexity [Vaswani et al., 2017]. This cost has motivated substantial work on efficient variants.

**Linear attention** methods replace softmax with kernel approximations, achieving O(n) complexity [Katharopoulos et al., 2020; Choromanski et al., 2021]. Random Feature Attention and Performers demonstrate competitive performance on certain tasks, though with accuracy trade-offs on long-range dependencies. These methods reduce complexity through mathematical approximation rather than iterative refinement.

**Sparse attention** restricts the attention pattern to predefined or learned subsets of positions. Longformer [Beltagy et al., 2020] combines local windowed attention with global tokens. BigBird [Zaheer et al., 2020] adds random attention for theoretical expressiveness guarantees. These methods achieve efficiency through reduced attention computation, not through dynamic evolution of attention patterns.

**Low-rank attention** approximates attention matrices via factorization [Wang et al., 2020]. Linformer projects key-value pairs to lower dimensions. These approaches assume attention matrices have low effective rank—an assumption that may not hold across all layers and tasks.

Our work differs from these approaches: we focus not on proposing a new efficiency mechanism, but on *validating* whether proposed mechanisms operate as claimed.

## Iterative and Recurrent Attention

Several works explore attention that evolves over internal steps, drawing inspiration from biological attention systems.

**Recurrent attention** uses RNN-like dynamics within attention computation [Graves, 2016]. Universal Transformers [Dehghani et al., 2019] apply transformer blocks iteratively with shared parameters. These works propose that iterative processing allows refinement toward task-relevant patterns.

**Equilibrium models** solve for fixed points in attention computation [Bai et al., 2019; Bai et al., 2020]. Deep Equilibrium Models frame forward passes as root-finding problems. The biological plausibility of iterative refinement motivates these architectures.

However, we observe a gap: these works demonstrate efficiency or accuracy improvements without testing whether the *proposed* iterative refinement mechanism actually operates. Do attention patterns converge across steps? Does the convergence correlate with task performance? Our work directly tests these mechanism-level questions.

## Mechanism Validation in Deep Learning

The broader deep learning literature increasingly calls for mechanistic understanding beyond end-to-end benchmarks.

**Interpretability research** seeks to understand what networks learn [Olah et al., 2020; Elhage et al., 2021]. Circuit analysis identifies human-interpretable components. However, interpretability and mechanism validation are distinct: a method can be interpretable without its efficiency mechanism being validated.

**Ablation studies** test component contributions but rarely decompose claims into orthogonal sub-hypotheses with falsification criteria. A typical ablation shows that removing component X degrades performance Y; it does not test whether X operates *through the proposed mechanism*.

**Negative results** are underreported in machine learning [Henderson et al., 2018; Dodge et al., 2019]. Our work demonstrates that negative mechanism results (H-M2 FAIL: no convergence) coexist with positive efficiency results (H-M1 PASS: 10.2% reduction)—a finding that would be invisible without explicit mechanism testing.

## Our Contribution

We contribute a methodology for mechanism validation:

1. **Sub-hypothesis decomposition:** Break efficiency claims into testable components (existence, mechanism, conditions).
2. **Gate hierarchy:** Distinguish MUST_WORK gates (core feasibility) from SHOULD_WORK gates (proposed mechanism).
3. **Explicit falsification:** Define what would refute each sub-hypothesis before running experiments.

This framework revealed that temporal dynamic attention achieves efficiency through reduced iteration count—a simpler explanation than the convergence hypothesis. We demonstrate that proposed mechanisms and observed outcomes can diverge, motivating mechanism-level testing in efficiency research.
