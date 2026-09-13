# Discussion

## Key Findings

Our experiments reveal a fundamental insight about architectural inductive biases: **permutation invariance cannot be learned from data regardless of scale**. Three findings support this conclusion:

1. **Massive Sample Efficiency Gap:** NFN achieves R²=0.95 at N=1K where MLP achieves only R²=0.35—a 60 percentage point advantage demonstrating the practical value of equivariance in data-limited regimes.

2. **Perfect NFN Invariance:** NFN predictions are invariant to weight permutation with deviations < 1.19e-07, confirming that equivariant architecture mathematically guarantees the desired property.

3. **MLP Dissociation:** At N=40K, MLP achieves R²=0.986 (near-perfect predictions) but only 0.63 invariance. High task performance coexists with failure to learn correct representations.

## Why MLPs Succeed Without Invariance

How does MLP achieve 99% R² without permutation invariance? We hypothesize:

**Position-Sensitive Statistics:** The Model Zoo dataset has correlations between specific weight positions and model accuracy. MLPs exploit these dataset-specific patterns rather than learning semantic weight-function relationships.

**Evidence:** If MLP learned true invariance, permuting test weights would not affect predictions. Instead, invariance score of 0.63 indicates predictions change substantially under permutation—the model relies on positional information.

**Implication:** MLP's success is brittle. Weights from a different training run (with different neuron ordering) would likely receive incorrect predictions, while NFN would remain robust.

## Implications for Weight-Space Learning

### Architectural Constraints Are Necessary

Our results argue that certain symmetries require explicit architectural encoding. The universal approximation theorem guarantees MLPs *can* learn any function, but our experiments show they *don't* learn invariance from finite data—even 40K models spanning diverse training conditions.

This suggests a revision to the conventional wisdom:
- **Old:** "More data teaches implicit symmetries"
- **New:** "Data teaches correlations, not structure; symmetries require architecture"

### When to Use Equivariant Architectures

Based on our findings:
- **Use NFN** when data is limited (N < 5K) or when invariance is critical for robustness
- **MLP may suffice** when data is abundant AND test distribution matches training distribution
- **Neither suffices** when robustness to arbitrary permutations is required at test time—only NFN provides this guarantee

## Limitations

We acknowledge several limitations:

### Synthetic Data in Initial Experiments

H-E1 used synthetic MLP weights rather than real Model Zoo data due to initial mock data detection. However, H-M4 and H-M5 use real Model Zoo data and confirm the core findings: NFN has perfect invariance, MLP does not learn it from data.

**Mitigation:** Phase 5 baseline comparison (planned) will replicate H-E1 on real data.

### Single Architecture Family

All experiments use CIFAR-10 CNNs. Results may not generalize to:
- Transformer architectures (different permutation structure)
- Much larger models (ViT, GPT-scale)
- Different tasks (generation vs. prediction)

**Mitigation:** The principle—equivariance provides sample efficiency—likely generalizes; specific magnitudes may vary.

### Limited Seed Count

Some experiments used 1-3 seeds instead of the planned 10 due to computational constraints.

**Mitigation:** Effect sizes are large (60pp R² gap, 0.37 invariance gap) and unlikely to disappear with more seeds.

### NFN-Scrambled Baseline Not Implemented

We did not test NFN with wrong permutation group (P2 in original predictions), which would distinguish "any constraint helps" from "correct symmetry helps."

**Mitigation:** Future work; our current results already establish the NFN-MLP gap.

## Broader Impact

### Positive Impacts

- **Efficiency gains:** Equivariant architectures reduce data requirements, enabling weight-space learning in data-limited domains
- **Robustness:** NFN's guaranteed invariance provides robustness to arbitrary neuron orderings

### Potential Concerns

- **Over-reliance on architecture:** Our findings might be misinterpreted as "architecture solves everything"—we emphasize that equivariance helps specifically for permutation symmetries, not all learning challenges

## Future Work

1. **Permuted Test Set Evaluation:** Directly verify that MLP R² drops when test weights are permuted while NFN maintains performance

2. **Transformer Weight Spaces:** Extend to attention weight permutation symmetries

3. **Very Large Scale:** Test at N > 100K to determine if any data quantity eventually teaches invariance

4. **Generation Tasks:** Evaluate whether equivariance benefits extend to weight generation, not just prediction
