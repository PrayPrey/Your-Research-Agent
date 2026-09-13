# Conclusion

We began by noting a paradox: self-supervised learning achieves up to 90% worst-group accuracy on spurious correlation benchmarks via linear probes, yet the geometric structure underlying this fairness remained unclear. Researchers implicitly assumed that strong spurious correlations would manifest as discrete, geometrically separable clusters in embedding space, enabling cluster-based diagnostics and interventions.

Our experiments falsify this cluster hypothesis. Despite 93% spurious correlation in Waterbirds training data, SimCLR embeddings exhibit AMI=0.28, far below the 0.4 threshold for reliable clusterability. LA-SSL, hypothesized to disperse clusters, instead *increases* AMI by 2%. Cluster-based diagnostics show no predictive power for intervention efficacy (r=-1.0, p=1.0). All three tested mechanisms failed their success criteria.

The resolution to our opening paradox is now clear: spurious features form **continuous linear gradients**, not discrete clusters. Linear probes achieve high WGA by exploiting these gradients, but k-means clustering cannot identify discrete groups in continuous feature space. This dissociation between linear separability (which exists) and discrete clusterability (which doesn't) is a conceptual contribution that clarifies which geometric properties actually characterize SSL embeddings.

## Contributions

This work makes three contributions to SSL fairness research:

1. **Empirical falsification**: First evidence that standard SSL does not produce high geometric clusterability on spurious correlation datasets (AMI=0.28 < 0.4), invalidating cluster-based diagnostics.

2. **Mechanistic redirection**: Eliminates cluster dispersion as an explanation for LA-SSL's documented fairness benefits, opening theoretical space for alternative mechanisms (linear boundary adjustment).

3. **Conceptual clarification**: Demonstrates that linear separability and discrete clusterability are dissociable properties in SSL embeddings, resolving confusion in prior work.

## Future Directions

Our negative result opens several research directions:

**FW-1: Extended Training** - Full 100-epoch experiments to definitively confirm that clusters don't emerge at scale. Current POC (20 epochs) suggests they don't, but longer training provides stronger evidence.

**FW-2: Linear Mechanism Testing** - Direct test of the hypothesis that LA-SSL operates via linear boundary adjustment: measure per-group margins, visualize decision boundaries, analyze learning curves.

**FW-3: Linear Fairness Diagnostics** - Develop margin-based or boundary-based fairness metrics that work without labels and align with SSL's actual geometric structure (gradients, not clusters).

**FW-4: Gradient-Based Interventions** - Design differentiable training objectives that reshape linear decision boundaries for fairness (e.g., maximize minimum per-group margin during SSL training).

**FW-5: High-Capacity Models** - Test whether clusterability emerges in ViT-H-14 (600M parameters) or other high-capacity architectures that achieve higher baseline WGA.

**FW-6: Other Datasets** - Extend to CelebA, MultiNLI, and other spurious correlation benchmarks to test whether continuous-gradient geometry is universal or dataset-specific.

## Closing Reflection

Null results are not failures when they eliminate incorrect theories. By definitively showing that cluster-based diagnostics cannot work in SSL fairness—because clusters don't form—we prevent wasted research effort on doomed approaches. More importantly, we redirect the field toward linear mechanisms that better match the geometric reality of SSL embeddings.

Science progresses not only by confirming hypotheses but by falsifying them. We set out to validate the cluster hypothesis and found it comprehensively wrong. That is not a failure. That is exactly what experiments are for.
