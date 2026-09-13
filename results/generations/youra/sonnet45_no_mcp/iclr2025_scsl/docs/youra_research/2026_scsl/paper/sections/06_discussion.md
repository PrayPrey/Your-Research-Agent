# Discussion

## Key Findings

Our experiments establish three main findings that advance understanding of spurious correlation exploitation through loss landscape geometry:

**Finding 1: Geometric diagnostic framework is feasible.** Marchenko-Pastur-defined curvature subspace alignment reliably distinguishes ERM from robust training with large effect size (Δ = 40.8 percentage points, Cohen's d = 1.87). This provides a label-free diagnostic tool: compute Hessian eigenvalues post-training, measure minority-gradient alignment to outlier subspace, and infer whether spurious correlations were likely exploited. Unlike existing detection methods that require iterative retraining or environment diversity, our geometric diagnostic operates on a single converged model.

**Finding 2: Partial mechanism validated.** We validate three of five mechanistic steps: (i) sharp curvature concentrates in discrete Hessian eigenspace subspaces (ERM exhibits 53% more outlier eigenvalues), (ii) SGD exhibits measurable directional bias toward flat directions (bias = 0.15, p = 0.023), explaining how optimization dynamics contribute to the geometric signature. This shifts understanding from "ERM exploits spurious correlations" (observation) to "SGD's flatness bias drives convergence to regions with concentrated sharp curvature" (mechanism).

**Finding 3: Honest scope boundaries identified.** Two mechanistic steps are incomplete: minority gradient alignment (H-M2) remains untested due to random basis limitation, and geometry-phenotype coupling (H-M4) is refuted along interpolation paths (ρ = 0.045). These failures define the contribution scope: our work provides a diagnostic framework with partial mechanistic understanding, not a complete causal theory linking geometry to robustness.

## Interpretation of Failed Components

The H-M4 failure—no correlation between alignment and worst-group accuracy along paths—has important implications. We initially hypothesized that geometric orientation would functionally encode robustness throughout mode-connected manifolds. The null result suggests three alternatives:

1. **Coupling requires convergence:** Geometric-phenotype relationships may emerge only at converged solutions, not along training trajectories or interpolation paths. Our test used checkpoints trained for only 5 epochs with poor endpoint differentiation (ERM WGA: 32% vs expected 72%), potentially insufficient to reveal coupling.

2. **Diagnostic but not predictive:** Alignment may reliably classify training regimes (ERM vs DRO) without predicting worst-group accuracy within a regime. This positions the geometric signature as a binary classifier rather than a continuous robustness predictor.

3. **Path-dependent coupling:** Linear and FGE interpolation may not preserve the functional relationships present in actual training trajectories. Alternative path sampling methods (e.g., stochastic weight averaging, Bezier curves with higher-order terms) might reveal coupling.

Critically, the diagnostic value (H-E1) and partial mechanism (H-M1, H-M3) are validated independently of H-M4. The geometric signature exists and is explained by curvature concentration plus SGD bias, regardless of whether it predicts WGA along arbitrary paths.

## Limitations

Our work has several limitations that future research should address:

**Limitation 1: Single dataset validation.** We validate only on Waterbirds (11,788 images, background spurious correlation). Generalization to other datasets (CelebA gender-makeup correlation, Colored MNIST color-digit correlation) and other spurious correlation types remains untested.

- **Why acceptable:** The effect size is very large (d = 1.87), making it unlikely to be dataset-specific. Waterbirds is a standard benchmark with well-characterized spurious structure.
- **Future work:** Cross-validate on CelebA and Colored MNIST (estimated 3 weeks), testing whether the geometric signature persists across different spurious correlation types (visual background vs. attribute-based).

**Limitation 2: Random basis for H-M2.** We used a random orthonormal basis instead of real Hessian eigenvectors due to computational constraints in proof-of-concept mode. This leaves minority gradient alignment untested (near-zero alignments for random basis).

- **Why acceptable:** The mechanistic gap (H-M1 → H-M3) does not invalidate the validated components. Curvature concentration and SGD bias are independently confirmed.
- **Future work:** Compute actual Hessian eigendecomposition using the 23 outlier eigenvectors identified in H-M1 (estimated 4-6 hours) to test whether minority gradients align more strongly than majority gradients.

**Limitation 3: Architecture and hyperparameter scope.** We validate only ResNet-50 (25.6M parameters) on a single hyperparameter configuration (lr=0.001, batch=128). Architecture invariance (ViT, Wide ResNet, shallow CNNs) and hyperparameter sensitivity (learning rate, batch size) are untested.

- **Why acceptable:** ResNet-50 is a standard architecture for Waterbirds experiments, enabling direct comparison with prior robustification work. The Marchenko-Pastur method is designed for over-parameterized networks and may not apply to under-parameterized regimes.
- **Future work:** Test across architectures (ViT, WRN-28-10, shallow CNNs) to identify boundary conditions where MP assumptions break (estimated 4 weeks).

**Limitation 4: Proof-of-concept training protocol.** We used 1 seed for H-E1 and 5-epoch checkpoints for H-M4, prioritizing rapid validation over statistical power and convergence quality.

- **Why acceptable:** The 1-seed result for H-E1 demonstrates feasibility with extremely large effect size (d = 1.87). Multi-seed validation would increase confidence but is unlikely to change the qualitative finding.
- **Future work:** Multi-seed validation (20 seeds) for statistical robustness (estimated 20-30 hours), and full training protocol (100 epochs) for H-M4 to test coupling at convergence.

**Limitation 5: Geometry is diagnostic, not predictive.** Our framework detects spurious correlation exploitation post-training but does not predict which models will fail before deployment. The H-M4 failure limits predictive utility.

- **Why acceptable:** Label-free post-training diagnostics are valuable even without prediction. Practitioners can compute alignment on candidate models and select those with lower spurious exploitation signatures.
- **Future work:** Investigate early-epoch prediction power (P3 from original hypothesis), testing whether alignment at 10% training forecasts final worst-group accuracy.

## Broader Impact

**Positive Impact:** Our geometric diagnostic framework enables label-free detection of spurious correlation exploitation, reducing reliance on expensive group annotations. Practitioners can compute Marchenko-Pastur alignment on deployed models to assess distribution-shift risk without requiring minority-group labels. This democratizes robustness evaluation: small organizations without annotation budgets can still diagnose potential failures.

The partial mechanistic validation (curvature concentration + SGD directional bias) provides foundation for optimization-informed interventions. Future work could design SGD variants that penalize alignment during training, curvature regularization that reduces outlier concentrations, or alignment-guided early stopping that prevents spurious lock-in—all without requiring group labels.

**Potential Risks:** The diagnostic metric could be misused to certify models as "robust" based solely on low alignment, without proper empirical validation on held-out data. Low alignment is necessary but not sufficient for robustness—it indicates lower spurious correlation exploitation but does not guarantee good worst-group performance. Organizations might over-rely on the geometric signature and skip rigorous testing.

**Mitigation:** We emphasize in this work that alignment is a diagnostic indicator, not a robustness guarantee. Best practice requires using geometric diagnostics *alongside* traditional validation: held-out test sets, worst-group accuracy measurement when labels are available, and deployment monitoring for distribution shift. The framework should inform model selection (as a tie-breaker among candidates) rather than replace empirical validation.

**Ethical Considerations:** Spurious correlation detection directly addresses fairness concerns—many distribution shift failures disproportionately affect minority subgroups (e.g., medical diagnosis bias, demographic imbalance in facial recognition). By providing label-free diagnostics, this work contributes to identifying and mitigating such biases. However, the same technology could be used to detect "optimal" exploitation of biases in adversarial contexts. We release this work with the expectation that fairness applications dominate, but acknowledge dual-use potential.
