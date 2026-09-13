# 7. Conclusion

We began by asking why a symmetry-enforcing architecture fails at the very scale where its inductive bias should matter most. Our answer: it does not fail because the structural inductive bias is flawed — it fails because the bias requires data to activate. Below approximately 150–250 training models on the CIFAR-10 CNN zoo, the GNN-NFN graph encoder lacks sufficient topological diversity in its training set to benefit from permutation equivariance. Above this threshold, the structural constraint reduces the effective hypothesis space and produces a sample efficiency advantage of 6.8× over a plain flat-MLP.

## Summary

In this work, we addressed the absence of a controlled, shared-split comparison of equivariant and plain weight-space encoders under data constraints. Our main contributions are:

1. **A 6.8× sample efficiency advantage.** GNN-NFN reaches 90% of peak R² at N≈147 training models; flat-MLP requires N=1000. This is the first quantitative measurement of the efficiency ratio on shared ModelZooDataset splits, far exceeding the 2× gate criterion and establishing a strong baseline for future encoder designs.

2. **A novel data-regime crossover.** At N=100, permutation augmentation of a plain MLP (R²=0.138) outperforms structural equivariance (GNN-NFN R²=−0.016). At N=250, the ordering reverses decisively (GNN-NFN R²=0.767 vs. PermAug R²=0.532). This crossover — absent from all prior weight-space learning studies — reveals a minimum-data threshold of approximately 150–250 models for equivariant graph encoders, and shows that structural and data-level symmetry enforcement are distinguishable strategies with qualitatively different data-regime dependencies.

3. **Mechanistic grounding.** Permutation equivariance is verified to floating-point precision for GNN-NFN (max_diff=1.80×10⁻⁶ across 10,000 checks) and DWSNets (max_diff=7.45×10⁻⁹), providing a structural basis for the efficiency advantage. The full-scale convergence (Δ=0.008 R² at N=full) is consistent with Dayan et al. [2026]'s expressivity equivalence theorem.

4. **A reusable evaluation protocol.** Shared-split learning curves at {100, 250, 500, 1000, full} training sizes, 90%-peak efficiency ratio, bootstrap CI, and equivariance verification form a complete protocol that can be applied to new encoders without redesigning experiments.

## Future Directions

The N=100 crossover raises three questions that directly follow from our results:

**From untested alternatives.** Does GNN-NFN's N=100 failure arise from architecture complexity (underfitting), or from a more fundamental minimum-data limit of structural equivariance? Varying GNN-NFN hidden dimension ∈ {16, 32, 64, 128} at N=100 with 10 seeds would distinguish these explanations: if smaller GNN-NFN achieves positive R² at N=100, the issue is capacity-data mismatch, not structural equivariance per se.

**From unverified assumptions.** Is the efficiency advantage specific to the CIFAR-10 CNN zoo, or does it generalize to MLP zoos (where DWSNets is architecturally appropriate)? Downloading the MNIST MLP zoo from Zenodo and running the full comparison with DWSNets — the highest-impact single extension — would answer whether the 6.8× ratio and the crossover point are consistent across zoo types.

**From scope extension.** Multi-seed replication of the N=100 crossover (10 seeds, approximately 10× H-M3 compute) would confirm or refute the most novel finding at low cost. Until confidence intervals are available, the crossover should be treated as a preliminary observation, not a confirmed result.

## Closing

As model zoos grow and equivariant encoder designs mature, the minimum-data threshold we identify may shrink — but until it does, practitioners with small zoos should start with augmented simplicity, not equivariant complexity. The question of when structural inductive bias pays off is not merely architectural; it is fundamentally a question about data.
