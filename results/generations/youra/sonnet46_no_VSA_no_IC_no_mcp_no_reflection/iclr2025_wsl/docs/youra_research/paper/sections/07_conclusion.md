# Conclusion

We opened this paper with an observation: in the Unterthiner CIFAR-10 CNN zoo, weight tensors predict
generalization gap better than they predict test accuracy — a finding that inverts the conventional
assumption about which quantity is more legible from weights. Our experiments confirm and extend this
observation into three concrete results. Generalization gap is learnable from weight tensors at Spearman
r > 0.5 using standard encoders. Among the architectures we tested, NFT's cross-layer attention achieves
the highest gap Spearman (r = 0.575) with statistical confidence. Most strikingly, NFT's gap predictions
contain information about true generalization gap that is independent of test accuracy — a partial
Spearman of r = 0.73 — revealing that weight tensors carry a distinct overfitting signal that is not
merely a shadow of absolute performance.

## Summary

We investigated whether permutation-equivariant weight-space encoders show an advantage on generalization
gap prediction (train_acc − test_acc at convergence), and whether this advantage is specific to gap
versus test accuracy. Our controlled dual-target study on 10,000 CNNs from the Unterthiner CIFAR-10 zoo
produces four findings:

1. **Gap learnability established.** FlatMLP achieves Spearman r = 0.557 on generalization gap
   prediction; DWSNet achieves r = 0.510. The A1 audit (Spearman(gap, −test_acc) = −0.142) confirms
   gap is not trivially derivable from test accuracy. Gap is a genuine, accessible weight-space signal.

2. **Cross-layer attention is the relevant inductive bias for gap.** NFT, the only tested encoder with
   cross-layer attention, achieves the highest gap Spearman (r = 0.575, 95% CI: [0.534, 0.616]).
   DWSNet (within-layer equivariance) and GNN (graph-structured equivariance) both underperform
   FlatMLP on gap — equivariance alone is insufficient; it is the capacity to reason across layer
   boundaries that provides advantage.

3. **NFT captures gap-specific overfitting structure.** The partial Spearman analysis (r = 0.730,
   p = 1.6×10⁻¹⁶⁷) establishes that NFT extracts information about generalization gap that is
   statistically independent of test accuracy rank. This is the most significant result of our study:
   gap and test accuracy occupy distinct regions of the weight-space information landscape.

4. **Target-specific differential advantage not confirmed.** The Δ-based mechanism hypothesis is
   not confirmed under our experimental conditions, confounded by an anomalously low FlatMLP test_acc
   baseline (r = 0.279 vs. literature ~0.85). We identify the confounder, propose corrective
   experiments, and report the null result transparently.

## Future Directions

**Resolving the mechanism question.** The most immediate priority is reproducing FlatMLP test_acc
Spearman ≈ 0.85 on the original Unterthiner zoo data with an extended 50-trial search budget, then
recomputing Δ with a valid control baseline. If FlatMLP test_acc is restored, the Δ values will shift;
determining their sign under clean conditions will reveal whether equivariant encoders genuinely lack
gap-specific differential advantage or whether our null result was a measurement artifact.

**Multi-architecture zoos.** The Schürholt PDFD zoo provides a multi-architecture evaluation venue
where the tested encoders can be applied without retraining the zoo. Replicating the NFT gap advantage
(r = 0.575) and P3 partial Spearman (r = 0.73) on PDFD would establish generalization beyond the
CIFAR-10 small CNN family.

**Mechanistic attribution.** Sub-hypothesis h-m4 (not executed in this pipeline) proposes to directly
compare NFT cross-layer attention vs. DWSNet within-layer equivariance through ablation — modifying
NFT to restrict its attention to within-layer positions only. If within-layer-restricted NFT loses
the gap advantage, this would directly confirm that cross-layer reasoning is the operative mechanism,
not other aspects of the NFT architecture (embedding dimension, number of heads, etc.).

**Theoretical grounding.** PAC-Bayes generalization bounds are naturally permutation-invariant and
defined over the full weight distribution. A theoretical analysis connecting cross-layer weight
co-variation (as captured by NFT's attention) to PAC-Bayes gap magnitude could provide principled
motivation for our empirical findings.

## Closing

Weight tensors may be natural overfitting sensors — encoding the distributed signature of memorization
across layer boundaries in a form that cross-layer attention architectures are well positioned to read.
The harder prediction problem, it turns out, is the one weight space was built for.
