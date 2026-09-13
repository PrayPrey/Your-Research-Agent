# Discussion

Our results provide strong evidence that data attribution trade-offs are structural properties of non-convex optimization landscapes. Here we discuss the key findings, their implications, honest limitations, and broader impact.

## Key Findings and Interpretation

### Why Same-Paradigm Methods Disagreed Most

Perhaps our most surprising finding is that TracIn and FastIF—both gradient-based methods—showed the lowest Jaccard agreement (0.0024), performing no better than cross-paradigm comparisons. This contradicts the intuition that methods from the same paradigm should produce more similar results.

**Our interpretation:** The "gradient-based" categorization is too coarse. TracIn computes gradient similarity across checkpoints, while FastIF uses Arnoldi iteration for Hessian-vector products. These different mechanisms navigate the non-convex landscape differently, emphasizing different regions of the training data manifold. The practical implication is that practitioners should not assume methods with similar-sounding descriptions will agree.

### The Geometry-Trade-off Connection

The dramatic contrast between convex and non-convex settings provides mechanistic insight. In logistic regression, the unique global minimum ensures all methods converge to the same closed-form influence function—hence metrics are coupled (corr $\geq$ 0.99). In ResNet-18, multiple local minima and the complex Hessian structure mean different approximation methods explore different regions, each "seeing" different influential examples.

This connection has theoretical implications: the search for a "universally best" attribution method may be fundamentally misguided in non-convex settings. The Pareto frontier is a structural property, not a deficiency to be overcome with better algorithms.

### Practical Guidance for Method Selection

Our findings translate directly to practitioner recommendations:

| Application | Priority Metric | Recommended Method |
|-------------|-----------------|-------------------|
| Data debugging (finding mislabeled examples) | Rank preservation ($\rho_r$) | IF, TRAK |
| Data valuation (marketplace pricing) | Magnitude fidelity ($\rho_m$) | FastIF, TracIn |
| Curriculum learning | Stability ($S$) | Empirical evaluation needed |
| ML auditing | Application-dependent | Match to audit goal |

The key insight is that method selection should be *application-driven*, not *accuracy-driven*. Asking "which method is most accurate?" is the wrong question; the right question is "which quality dimension matters for my use case?"

## Limitations

We acknowledge several limitations that bound the scope of our claims:

### Ground Truth Approximation

Our ground truth is computed via gradient-based proxies rather than true leave-one-out retraining (which would require 50,000 full training runs). While this is standard practice [Park et al., 2023; Koh and Liang, 2017], it may underestimate true LOO variability.

**Why acceptable:** Relative method comparisons remain valid even if absolute correlation values differ from true LOO. The key findings—trade-off existence and geometry-dependence—would persist.

**Future work:** Validate on a smaller dataset where true LOO is tractable.

### Single Architecture

Our non-convex experiments use ResNet-18 exclusively. Generalization to other architectures—particularly Transformers—is not validated.

**Why acceptable:** ResNet-18 exhibits canonical non-convex deep learning behavior. However, Transformer attention mechanisms may create different Hessian structures.

**Future work:** Extend validation to BERT-base on NLP tasks and vision Transformers.

### Dataset Scale

CIFAR-10 with 5,000 training samples is orders of magnitude smaller than production data attribution scenarios (millions of examples, billion-parameter models).

**Why acceptable:** Our focus is on characterizing *whether* trade-offs exist, not their exact values at scale. The geometric mechanism should transfer.

**Future work:** Develop scalable ground truth proxies for foundation model scale validation.

### Stability Metric

The normalized stability metric ($S$) was planned but not extensively validated in our experiments. Conclusions focus on $\rho_r$ and $\rho_m$.

**Why acceptable:** Rank preservation and magnitude fidelity cover the most common downstream applications. Stability analysis is deferred.

**Future work:** Extend H-M2 to include stability analysis with bootstrap variance estimation.

## Implications for Attribution Benchmarks

Our findings have implications for how the field evaluates attribution methods:

1. **Report Pareto fronts, not single numbers.** A single rank correlation value hides potential trade-offs. Future benchmarks should characterize the full quality profile.

2. **Standardize compute normalization.** Direct comparison across methods requires matched computational budgets via gradient-equivalent operations or similar normalization.

3. **Include geometry controls.** Convex baselines (as in H-M1) help isolate optimization effects from method deficiencies.

4. **Measure application-relevant metrics.** The "right" metric depends on the downstream application. Benchmarks should report metrics matched to common use cases.

## Broader Impact

### Positive Impacts

This work enables more informed method selection for data attribution applications:

- **Data debugging:** Practitioners can choose methods prioritizing rank preservation for identifying top-k problematic examples.
- **Data valuation:** Marketplace applications can select methods with higher magnitude fidelity for fair pricing.
- **ML safety:** Auditors can understand that different methods reveal different aspects of model behavior—neither is "wrong."

### Potential Concerns

We identify two potential concerns:

1. **False confidence in chosen method:** Practitioners might over-trust a single method after reading guidance, ignoring that *all* methods provide partial views. We emphasize that multi-method validation remains valuable.

2. **Misuse for data manipulation:** Understanding which examples methods identify could enable adversarial data injection that evades certain attribution methods. However, this concern applies to any attribution research and is not unique to our work.

### Mitigation

We recommend that practitioners:
- Use multiple methods when stakes are high
- Report which method was used and why
- Acknowledge that attribution results are method-dependent

## Comparison to Prior Work

Our findings complement rather than contradict prior work:

- **vs. Basu et al. [2020]:** They showed *when* IF fails; we show *trade-offs* when methods work but disagree.
- **vs. Park et al. [2023]:** They reported single-metric improvements; we reveal multi-metric trade-offs hidden by single-metric evaluation.
- **vs. Nguyen et al. [2023]:** They identified reliability concerns; we characterize the geometric structure underlying method disagreement.

The key contribution is shifting the conversation from "which method is best?" to "which quality dimension matters for this application?"
