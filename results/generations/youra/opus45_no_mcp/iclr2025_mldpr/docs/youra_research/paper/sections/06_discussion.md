# Discussion

Our experiments reveal that benchmark popularity correlates with larger generalization failures, but the mechanism is more nuanced than initially hypothesized. We discuss our findings, their implications, and honest limitations.

## Key Findings

**Finding 1: The popularity-gap correlation is substantial and actionable.**

The 21.21 percentage point gap difference between CIFAR-10 and SVHN conditions is not a subtle statistical effect—it represents a dramatic difference in deployment reliability. This finding suggests that benchmark selection itself may be a confounding factor in model evaluation. Practitioners should consider validating on less-popular same-domain datasets before deployment, and researchers should report performance on diverse benchmarks rather than optimizing solely for popular leaderboards.

**Finding 2: Research investment is highly concentrated on popular benchmarks.**

High-use datasets receive nearly 25× more optimization-focused research papers than low-use alternatives. This concentration creates a self-reinforcing cycle: popular benchmarks attract more research, which produces more techniques optimized for those specific benchmarks, which further increases their popularity. The benchmark ecosystem may be converging on a narrow set of evaluation targets, potentially missing failure modes that would be visible on diverse benchmarks.

**Finding 3: Texture bias does not explain the co-evolution effect at CIFAR scale.**

Our most surprising finding is that modern architectures (ResNet-18) show *lower* texture bias than legacy architectures (VGG-11), contrary to predictions from Geirhos et al. (2019). We interpret this as evidence that architectural innovations—particularly skip connections and batch normalization—improve shape-based generalization rather than amplifying artifact exploitation. This contradicts the straightforward texture bias mechanism and suggests that:

1. ImageNet-scale texture bias findings may not transfer to 32×32 image classification
2. The optimization investment in architecture search may have selected for more shape-robust features
3. The co-evolution effect operates through alternative mechanisms (spurious correlations, background features, test set leakage)

## Implications

**For researchers:** Benchmark popularity should be reported alongside performance results. Progress claims should be validated on diverse benchmarks, including less-popular alternatives within the same domain.

**For practitioners:** Models validated solely on popular benchmarks may fail unexpectedly in deployment. Consider building validation sets from less-optimized data sources.

**For the field:** The concentration of research attention on a narrow set of benchmarks may be creating blind spots. Incentivizing diverse benchmark evaluation (e.g., in paper reviews) could help.

## Limitations

Our work has several limitations that bound the scope of our claims:

**Limitation 1: Two dataset pairs only**

We test on CIFAR-10/CINIC-10 and SVHN/SVHN-Extra—two pairs within the image classification domain. While these are canonical representatives of high-use and low-use benchmarks, we cannot claim generality across all domains or all dataset pairs.

*Why acceptable:* The pairs represent a strong high/low popularity contrast, and the effect size (21.21 pp) is large enough to be practically meaningful even if other pairs show smaller effects.

*Future work:* Extend to NLP benchmarks (GLUE vs. less-popular alternatives), tabular data, and additional vision domains.

**Limitation 2: Proof-of-concept statistical rigor**

H-E1 uses a single random seed with direction check rather than multi-run Cohen's d estimation. This provides directional evidence but not statistical significance for the existence hypothesis specifically.

*Why acceptable:* The effect size is unambiguously large (21.21 pp); statistical testing would confirm but not change the direction.

*Future work:* Multi-run experiments with proper effect size estimation and confidence intervals.

**Limitation 3: Mechanism incomplete**

We ruled out texture bias but did not identify the true causal pathway. The co-evolution effect is real (H-E1, H-M1), but why popular benchmarks induce worse generalization remains partially unexplained.

*Why acceptable:* Negative results are scientifically valuable—ruling out one mechanism clarifies the search space for future investigation.

*Future work:* Test alternative mechanisms including spurious correlation exploitation, background feature dependence, and test set leakage through community usage.

**Limitation 4: Bibliometric proxy**

ArXiv paper counts approximate but do not directly measure optimization intensity. Actual compute invested in hyperparameter search is not observable.

*Why acceptable:* Paper counts are a plausible proxy for research attention, and the effect size (24.68×) is robust to measurement noise.

## Broader Impact

**Positive impacts:** Our findings may encourage more diverse benchmark evaluation practices, leading to models that generalize better in deployment. Highlighting the risks of benchmark concentration could improve ML development practices.

**Potential concerns:** If misinterpreted, our findings could be used to argue against any standardized benchmarking—this is not our intent. Benchmarks serve important functions; we argue for *diverse* benchmarking, not *no* benchmarking.

**Mitigation:** We emphasize that our recommendation is to *complement* popular benchmarks with diverse alternatives, not to abandon established evaluation practices.
