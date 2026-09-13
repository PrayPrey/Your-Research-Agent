# Methodology

## Overview

Building on our observation that practitioners need budget-aware UQ selection, we design a systematic benchmark to map the cost-performance space. Rather than declaring a single "best" method, we construct the **Pareto frontier** of UQ methods—the set of methods where no alternative achieves both higher AUROC and equal-or-lower cost.

Our approach evaluates 6 UQ method variants on TruthfulQA selective prediction, measuring both uncertainty quality (AUROC) and computational cost (FLOPs normalized to baseline). This reveals which methods are Pareto-optimal across different budget constraints (1×, 3×, 5×, 10× cost zones).

## UQ Methods

We evaluate three classes of single-forward-pass UQ methods:

### Temperature Scaling

**What it does:** Learns a single scalar parameter T that rescales logits before softmax:

$$p(y|x) = \text{softmax}(\mathbf{z}/T)$$

where $\mathbf{z}$ are the model's logits. T is optimized on a held-out calibration set to minimize negative log-likelihood.

**Rationale:** Zero inference overhead (T applied post-training) provides a baseline for cost-performance trade-offs. Tests whether post-hoc calibration suffices for selective prediction.

**Cost:** 1.0× (same as baseline single forward pass)

**Uncertainty score:** Predictive entropy $H[p(y|x)]$

### Conformal Prediction

**What it does:** Computes nonconformity scores on a calibration set, then constructs prediction sets with coverage guarantee $1-\alpha$. Following Su et al. (2024), we use:

$$\text{nonconformity}(x) = \text{sample\_freq}(x) \times \text{semantic\_sim}(x, \text{calib})$$

**Rationale:** Distribution-free guarantees complement parametric methods. Tests cross-dataset transfer (HaluEval calibration → TruthfulQA test).

**Cost:** 1.0× (calibration is one-time, per-query cost is single forward pass)

**Uncertainty score:** Nonconformity score (higher = more uncertain)

### MC Dropout (k=1, 3, 5, 10)

**What it does:** Enables dropout at inference time, samples k predictions, computes variance:

$$\text{Var}[y] \approx \frac{1}{k}\sum_{i=1}^{k} (f_{\theta_i}(x) - \bar{f}(x))^2$$

where $\theta_i$ are stochastic dropout masks.

**Rationale:** Approximates Bayesian posterior via variational inference, capturing epistemic uncertainty. k-variants test cost-quality trade-offs across budget zones.

**Cost:** k× (k forward passes)

**Uncertainty score:** Predictive variance

**k=1 variant:** Deterministic (no dropout), serves as degenerate baseline to test if stochasticity is necessary.

## Dataset

**TruthfulQA** (Lin et al., 2021): 817 adversarially-designed questions testing model truthfulness. Questions target common misconceptions ("What happens if you crack your knuckles?"). Human annotations provide ground-truth correctness labels.

**Rationale:** Adversarial design challenges UQ methods more than standard QA benchmarks (MMLU, Natural Questions). 817 samples provide sufficient power for statistical significance testing.

**Calibration split:** 40% (326 questions) for temperature scaling and conformal prediction calibration. We use HaluEval (~10k samples) for conformal calibration to test cross-dataset transfer, matching Su et al. (2024) protocol.

**Test split:** 60% (491 questions) for AUROC evaluation, never touched during calibration.

## Evaluation Metrics

**AUROC (Area Under ROC Curve):** Measures how well uncertainty scores discriminate correct vs incorrect predictions. AUROC = 0.5 is random, 1.0 is perfect. We set threshold ≥ 0.70 for viable selective prediction based on prior work.

**Inference Cost (FLOPs):** Normalized to single forward pass = 1.0×. MC dropout k=N measured as N.0× ± 0.1×. Temperature scaling and conformal prediction are 1.0× (post-hoc, excludes one-time calibration).

**Rationale for FLOPs over wall-clock time:** FLOPs is hardware-agnostic and deterministic. Wall-clock time varies with GPU type, batch size, memory bandwidth—unsuitable for cross-study comparison.

## Pareto Frontier Construction

For each method $i$, compute $(cost_i, AUROC_i)$ averaged over 3 random seeds (seeds: 42, 123, 456). Method $i$ is **Pareto-optimal** if:

$$\forall j \neq i: \neg(cost_j \leq cost_i \land AUROC_j > AUROC_i \text{ with } p < 0.05)$$

where statistical significance is assessed via paired t-test (two-tailed, $\alpha = 0.05$). A method is dominated if another method achieves both equal-or-lower cost AND statistically higher AUROC.

**Rationale:** Pareto frontier captures the complete trade-off space. If only 1 method is Pareto-optimal, budget-aware selection collapses to "always use that method." If ≥2 methods are Pareto-optimal, practitioners choose based on budget constraints.

## Implementation Details

**Model:** Llama-3.1-8B-Instruct (meta-llama/Llama-3.1-8B-Instruct from HuggingFace)

**Hardware:** 5× NVIDIA H100 NVL GPUs

**Temperature scaling:** Optimized via LBFGS on calibration split, minimizing NLL

**Conformal prediction:** 90th percentile nonconformity threshold ($\alpha = 0.1$), calibrated on HaluEval

**MC dropout:** Dropout rate p=0.1 (default Llama architecture), k samples per query

**Random seeds:** 42, 123, 456 for reproducibility

**Evaluation:** Official TruthfulQA evaluation script (sylinrl/TruthfulQA repo), human-annotated labels as ground truth (not GPT-judge metrics)
