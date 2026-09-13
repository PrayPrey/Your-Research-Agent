# Introduction

When practitioners ask "which training examples most influenced this prediction?", different attribution methods give answers that agree on less than 1% of the identified examples. This striking finding emerges from our systematic comparison of four widely-used data attribution methods—TRAK, TracIn, Influence Functions (IF), and FastIF—under controlled computational budgets. A data scientist debugging a model's gender bias could identify completely different problematic training examples depending on their choice of method, potentially addressing the wrong data entirely.

Data attribution has become critical infrastructure for machine learning: it enables model debugging by identifying training examples causing failures [Koh and Liang, 2017], data valuation for marketplace applications [Ghorbani and Zou, 2019], curriculum learning optimization [Katharopoulos and Fleuret, 2018], and ML safety auditing through influence tracing [Park et al., 2023]. Yet despite significant methodological advances—from the foundational influence functions [Koh and Liang, 2017] to efficient approximations like TRAK [Park et al., 2023] and DataInf [Kwon et al., 2023]—practitioners lack principled guidance for selecting among these methods.

## The Multi-Objective Nature of Attribution Quality

The conventional approach treats data attribution as a single well-posed problem: given a model and a test example, identify the most influential training points. Methods are typically evaluated on a single metric—usually rank correlation with leave-one-out (LOO) retraining—and "better" methods achieve higher correlation. This framing implicitly assumes that improving one quality dimension improves all others.

We challenge this assumption. Our analysis reveals that attribution quality is inherently multi-dimensional, encompassing at least three distinct aspects:
- **Rank preservation** ($\rho_r$): How well does the method preserve the ordering of influential examples?
- **Magnitude fidelity** ($\rho_m$): How accurately does the method estimate the magnitude of influence?
- **Normalized stability** ($S$): How consistent are the estimates across random seeds?

These dimensions serve different downstream applications—rank preservation matters for identifying "top-k" influential examples, magnitude fidelity matters for data pricing, and stability matters for reproducible auditing—yet prior work has not systematically characterized their relationships.

## From Single-Metric to Multi-Objective Evaluation

The deeper problem is that methods face fundamental trade-offs between these quality dimensions. We observe that Influence Functions achieve higher rank preservation while FastIF achieves higher magnitude fidelity at matched computational budgets—they cannot both be "correct" in an absolute sense. This pattern persists across all five tested compute budgets, suggesting these trade-offs are not finite-sample artifacts but structural properties of the attribution problem.

What causes this structural decoupling? We hypothesize that the answer lies in the geometry of deep learning optimization. In convex settings like logistic regression, the loss landscape has a unique global minimum, and the Hessian structure ensures all quality metrics move together—they are functions of a single approximation error. But in non-convex deep networks, the landscape has multiple local minima, and different approximation methods (random projections for TRAK, HVP iterations for IF, gradient similarity for TracIn) navigate this landscape differently, each "seeing" different influential training examples.

## Our Key Insight

**Attribution metric trade-offs are structural properties of non-convex optimization landscapes, not artifacts of approximation quality.** In convex settings, we prove that all metrics remain perfectly coupled (correlation $\geq 0.99$). But in non-convex deep networks, this coupling completely breaks down (R² = 0.034), revealing that different methods explore fundamentally different regions of the loss landscape. The question is not "which method is best?" but rather "which quality dimension matters for my application?"

## Contributions

Building on this insight, we make the following contributions:

1. **First rigorous Pareto characterization of data attribution methods.** We demonstrate that finite-compute attribution exhibits non-degenerate Pareto trade-offs across quality dimensions, with IF vs FastIF showing metric crossings at all five tested compute budgets (10, 25, 50, 75, 100 gradient-equivalent operations).

2. **Mechanistic explanation rooted in optimization geometry.** We establish that metric coupling persists in convex settings (partial correlation $\geq 0.99$) but breaks down in deep networks (R² drops 84%), proving that trade-offs arise from non-convex geometry rather than approximation quality.

3. **Quantitative evidence of practical impact.** We show that different attribution methods identify fundamentally different influential training examples, with top-50 Jaccard similarity as low as 0.0024 (<1% overlap). This finding has immediate implications for practitioners: method selection determines which data you would actually modify.

4. **Unified evaluation framework.** We introduce compute-normalized comparison via gradient-equivalent operations, enabling fair cross-method evaluation and reproducible Pareto frontier characterization.

Our findings fundamentally change how practitioners should approach method selection: rather than seeking the "best" attribution method, they should identify which quality dimension matters for their use case and select accordingly.

## Paper Organization

Section 2 reviews related work in data attribution, positioning our multi-objective contribution. Section 3 presents our methodology, including quality metric definitions and the unified evaluation framework. Section 4 describes experimental setup, and Section 5 presents results from our four-hypothesis validation. Section 6 discusses implications, limitations, and future directions. Section 7 concludes with practical recommendations.
