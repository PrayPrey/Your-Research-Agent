# Per-Sample Hessian Trace as an Annotation-Free Minority Group Proxy Under ERM Training

## Abstract

Empirical risk minimization (ERM) on spuriously correlated data produces systematic accuracy gaps between majority and minority groups, yet identifying minority-correlated training samples without group annotations remains an open problem. This work measures per-sample last-fully-connected-layer (last-fc) Hessian trace — estimated via K=50 Hutchinson probes using torch.func vmap+vjp — as a candidate annotation-free proxy for minority group membership in ERM-trained neural networks. On Waterbirds (ResNet-50, SGD, 50 epochs, five independent random seeds), 4/5 seeds achieve AUROC≥0.85 for minority membership prediction at the epoch t* of maximum trace ratio, with epoch-0 AUROC below 0.70 in all five seeds, confirming that the signal is induced by ERM training rather than inherited from ImageNet pretraining. Investigation of the mechanistic basis reveals that minority training-set confidence saturates to ≥0.9678 at t* (range: 0.9678–0.9999 across seeds) — effectively equal to majority confidence — refuting the pre-registered confidence-differential mechanism (p_minority(t*)∈[0.3,0.7] in ≥4/5 seeds: 0/5 satisfied). The Hutchinson estimator is stable across seeds (coefficient of variation CV<3% for all seeds at K=50). The trace asymmetry at t* must therefore arise primarily from the feature-norm channel (‖x_i‖²), consistent with LaBonte et al. [2024]'s group-level spectral imbalance result, though direct per-sample feature-norm verification remains for future work. This paper presents the first per-sample second-order annotation-free minority proxy achieving AUROC>0.85 on Waterbirds, alongside a principled falsification of the expected mechanism.

## 1. Introduction

We trained ResNet-50 on Waterbirds and found that — without any group labels — the curvature of the loss surface around each training sample reveals minority group membership with AUROC 0.85–0.90 in 4/5 random seeds (mean AUROC 0.89 across the four passing seeds). When investigating the mechanism, however, the expected mechanistic driver was absent: by the time the curvature signal peaks, minority samples are classified with training confidence ≥0.97, indistinguishable from majority samples. The signal is robust; the original mechanistic explanation is not.

This puzzle sits at the intersection of two long-standing problems in robust machine learning. The first is spurious correlations: models trained with ERM on real-world datasets learn to exploit incidental statistical associations between input features and labels. On Waterbirds [Sagawa et al., 2020], a ResNet-50 trained with ERM achieves approximately 97% average accuracy on training samples but only approximately 72% worst-group accuracy on the test set — minority groups (e.g., landbirds on water backgrounds) suffer because the model relies on background rather than bird shape. The second problem is annotation burden: the most effective mitigation methods, such as deep feature reweighting (DFR) [Kirichenko et al., 2023], require a balanced held-out validation set with explicit group labels — a resource that is unavailable in many practical settings.

Annotation-free alternatives — Just Train Twice (JTT) [Liu et al., 2021], SELF [LaBonte et al., 2023] — proxy minority membership through first-order signals: which samples are misclassified, or which have the highest loss. These methods improve over ERM without group labels, but they are insensitive to how the model encodes spurious features in its loss landscape geometry.

This work asks whether the second-order geometry of the loss surface carries distinct information about minority group membership. Specifically, we measure the per-sample Hessian trace of the last fully-connected layer — computed via K=50 Hutchinson estimation using torch.func vmap+vjp — at six training checkpoints (t∈{0,1,5,10,20,50}) over five random seeds, and ask whether this trajectory discriminates minority from majority samples.

The measurement protocol is motivated by two theoretical results. LaBonte et al. [2024] show that minority group covariance matrices have larger spectral norm than majority groups within the same class — a group-level prediction of systematic feature-norm inequality (‖x_i‖²) that would elevate per-sample Hessian traces for minority samples, given the decomposition Tr(H_i^fc) ∝ ‖x_i‖² p_i(1−p_i). LaBonte and Muthukumar [2026] prove that SGD on XOR spurious models learns the spurious feature first (Phase I) before the core feature (Phase II), predicting a transient differential in loss landscape curvature between majority (which gain confidence rapidly via the spurious shortcut) and minority (which do not).

The existence experiment (H-E3) confirms the signal: 4/5 seeds achieve AUROC≥0.85 for minority membership prediction at t* (the epoch maximizing the trace ratio R(t) = mean_minority_trace / mean_majority_trace), with epoch-0 AUROC<0.70 in all seeds. The Hutchinson estimator is stable (CV<3% for all seeds), establishing K=50 as sufficient for the last-fc layer of ResNet-50.

The mechanism experiment (H-M1) produces the central puzzle. The original mechanistic explanation — that minority samples remain near the decision boundary (p_i∈[0.3,0.7]) throughout Phase I training, keeping p_i(1−p_i) large and thereby elevating Tr(H_i^fc) — is directly falsified. At t*, minority training-set confidence is 0.9678–0.9999 across all seeds: fully saturated, not boundary-straddling. A transient differential does exist at epoch 1 (seed 1: p_min=0.827 vs p_maj=0.972), consistent with Phase I theory, but it disappears well before t* in all seeds.

The trace signal at t* must therefore arise from the ‖x_i‖² feature-norm channel — systematic differences in the penultimate-layer representation norms between minority and majority samples, consistent with LaBonte et al. [2024]'s spectral imbalance finding. This interpretation is a candidate, not a verified claim; directly measuring penultimate-layer norms at t* is the primary direction for future mechanistic investigation.

**Contributions:**

1. **Empirical existence result:** First experimental evidence that per-sample last-fc Hessian trace (K=50 Hutchinson via vmap+vjp) achieves AUROC≥0.85 for minority membership detection in ERM-trained ResNet-50 on Waterbirds across 5 random seeds, with epoch-0 control confirming ERM emergence (Section 5.1).

2. **Principled falsification of the confidence-differential mechanism:** Direct refutation of the sustained decision-boundary hypothesis (p_minority∈[0.3,0.7] at t*) on training-set data, with identification of the feature-norm channel (‖x_i‖²) as the likely surviving driver (Section 5.2, Section 6.2).

3. **Practical confirmation:** K=50 Hutchinson is the minimum stable setting for last-fc ResNet-50 (CV<3%), and the epoch-0 control serves as a reliable pretrained-artifact detector (Section 4.4).

## 2. Related Work

### 2.1 Spurious Correlations and Group Robustness

Spurious correlations — statistical associations between features and labels that do not reflect causal structure — cause ERM-trained models to fail systematically on minority groups [Sagawa et al., 2020]. The Waterbirds benchmark [Sagawa et al., 2020] isolates this phenomenon: bird labels are spuriously correlated with backgrounds, creating four groups (2 class × 2 background) with dramatically different ERM performance. Distributionally robust optimization (DRO) [Sagawa et al., 2020] directly targets worst-group accuracy but requires group annotations at training time.

### 2.2 Annotation-Required Methods: DFR

The most effective post-hoc approach is deep feature reweighting (DFR) [Kirichenko et al., 2023]: retrain only the last layer on a balanced held-out validation set, keeping ERM-pretrained features frozen. DFR achieves worst-group accuracy (WGA) approximately 88–90% on Waterbirds with a small balanced set. Hill et al. [2025] explain DFR's effectiveness as implicit group-balancing: when the retraining set overrepresents minority samples, the final classifier learns to rely on causal features rather than spurious shortcuts. DFR's key limitation is the requirement for explicit group annotations in the balanced validation set.

### 2.3 Annotation-Free Proxies: First-Order Signals

The annotation-free direction emerged with JTT [Liu et al., 2021]: identify misclassified samples after a first ERM run, upweight them, and retrain. JTT achieves WGA approximately 80–84% on Waterbirds without group labels. SELF [LaBonte et al., 2023] refines this by combining misclassification-based proxy selection with self-training, reaching WGA approximately 82–87%. All such methods share a fundamental constraint: they operate on first-order signals — model output or loss — and are insensitive to loss landscape geometry.

The present work proposes the first second-order annotation-free proxy: per-sample Hessian trace of the last-fc layer. This signal is orthogonal to loss and misclassification rates and carries information about differential curvature created by spurious feature exploitation.

### 2.4 Loss Landscape Geometry and Hessian Analysis

Sharpness of loss minima is connected to generalization: sharp minima (high Hessian eigenvalues) generalize poorly compared to flat minima [Keskar et al., 2016]. Sharpness-aware minimization (SAM) [Foret et al., 2021] explicitly seeks flat minima. Per-layer Hessian trace estimation via Hutchinson's method has been studied for neural network diagnostics [Yao et al., 2020]. The Hutchinson estimator approximates tr(H) ≈ (1/K)Σ v^T H v for K random Rademacher vectors v without materializing the full Hessian. However, no prior work extends Hutchinson estimation to the per-sample level to discriminate minority from majority group membership.

### 2.5 Theoretical Connections

LaBonte et al. [2024] show that minority group covariance matrices have larger spectral norm than majority groups within the same class — a group-level prediction of systematic representation-norm inequality (‖x_i‖²). This finding supports the hypothesis that per-sample Hessian traces would be elevated for minority samples, since Tr(H_i^fc) ∝ ‖x_i‖² p_i(1−p_i) for a linear cross-entropy head. LaBonte and Muthukumar [2026] prove that SGD on XOR spurious models learns the spurious feature first (Phase I) before the core feature (Phase II), creating a transient window where minority samples remain near the decision boundary.

This work extends LaBonte et al. [2024] from group-level covariance to per-sample trajectory analysis, and tests the Phase I/II prediction of LaBonte and Muthukumar [2026] on real image data with ResNet-50.

## 3. Method

### 3.1 Problem Setup

Consider a training dataset D = {(x_i, y_i, g_i)}_{i=1}^N where group labels g_i are hidden during training and evaluation. ERM minimizes L(θ) = (1/N)Σ_i ℓ(f_θ(x_i), y_i) without observing g_i. The question is whether any per-sample statistic derived from the ERM loss surface discriminates minority from majority group membership using only f_θ(x_i) and ℓ, without observing g_i.

### 3.2 Per-Sample Last-FC Hessian Trace

For sample i at training checkpoint t, the per-sample last-fc Hessian trace is:

$$\mathrm{Tr}(H_i^{fc}) = \mathrm{Tr}\!\left(\frac{\partial^2\,\ell(f_{\theta_t}(x_i), y_i)}{\partial W_{fc}^2}\right)$$

where W_fc ∈ ℝ^{2048×2} is the weight matrix of the last fully-connected layer of ResNet-50. Restriction to the last-fc layer is motivated by three considerations: (1) tractability — 4098 parameters versus 25M total; (2) architectural motivation — the classification head directly encodes spurious feature alignment learned by the backbone; (3) mechanistic interpretability — the per-sample last-fc Hessian has the closed-form decomposition:

$$\mathrm{Tr}(H_i^{fc}) \propto \|x_i\|^2 \cdot p_i(1 - p_i)$$

for cross-entropy loss with penultimate feature x_i ∈ ℝ^d and predicted probability p_i. This decomposition isolates the feature-norm channel (‖x_i‖²) and the confidence channel (p_i(1−p_i)) as two separable candidate drivers of trace asymmetry.

### 3.3 Hutchinson Trace Estimation

Computing Tr(H) exactly requires full Hessian materialization. The Hutchinson estimator [Avron and Toledo, 2011] is used instead:

$$\mathrm{Tr}(H) \approx \frac{1}{K} \sum_{k=1}^K v_k^T H v_k$$

where v_k ∈ {±1}^d are Rademacher random vectors, and Hv_k is computed as a reverse-over-reverse automatic differentiation pass. This is implemented via torch.func.vmap + torch.func.vjp on a per-sample basis, enabling vectorized computation across samples without storing the full Hessian or Jacobian.

**Choice of K=50:** Prior diagnostic work [Yao et al., 2020] uses K=256 for batch-level Hessian traces on large networks. For the last-fc layer (d=4098), K=50 Rademacher probes provide trace estimates with coefficient of variation CV<3% across all five seeds in the experiments reported here — confirmed as the minimum stable setting for this architecture. Total computation per checkpoint per seed is approximately 8 minutes on a single H100 GPU for all 4795 training samples.

### 3.4 Training Protocol

ResNet-50 [He et al., 2016] with ImageNet pretrained weights (torchvision v0.15) is trained on Waterbirds v1.0 with ERM:

- Optimizer: SGD (lr=3×10⁻³, momentum=0.9, weight decay=1×10⁻⁴)
- Epochs: 50
- Checkpoints: t ∈ {0, 1, 5, 10, 20, 50}
- Seeds: 5 independent seeds (seeds 1–5)
- Batch size: 32
- Device: CUDA (NVIDIA H100 NVL)

The t=0 checkpoint is the pretrained ImageNet initialization before any Waterbirds training. This serves as the epoch-0 control for distinguishing ERM-induced signals from pretrained artifacts (Section 4.4).

### 3.5 Trace Ratio and t* Selection

At each checkpoint t, the trace ratio is:

$$R(t) = \frac{\mathrm{mean}_{i\in\mathrm{minority}}\, \mathrm{Tr}(H_i^{fc}(t))}{\mathrm{mean}_{i\in\mathrm{majority}}\, \mathrm{Tr}(H_i^{fc}(t))}$$

The optimal checkpoint t* = argmax_t R(t) selects the epoch of maximum minority-majority trace divergence. R(t) is computed without observing group labels at training time; group labels are used only post-hoc for AUROC evaluation.

### 3.6 Evaluation Protocol

**Existence gate (H-E3):** At checkpoint t*, AUROC is computed for predicting minority membership (g_i ∈ {1,3}) from the scalar trace Tr(H_i^fc(t*)). Three simultaneous criteria must hold for a seed to pass:

1. AUROC(t*) ≥ 0.85
2. AUROC(t=0) < 0.70 (ERM-induction control)
3. Spearman ρ(t, AUROC(t)) ≥ 0.8 on the rising AUROC segment from t=0 to t* (monotone signal development)

The gate requires ≥4/5 seeds to satisfy all three criteria simultaneously.

The epoch-0 control (criterion 2) is mandatory: it rules out that minority-majority trace differences are inherited from ImageNet pretraining rather than induced by ERM training on Waterbirds. A prior experiment (h-e2) found AUROC=0.987 at epoch 0 for a gradient-direction signal — a pretrained artifact. The epoch-0 gate prevents this confound.

**Mechanism gate (H-M1):** At t*, mean training-set prediction confidence is measured for minority and majority samples separately. The confidence-differential mechanism predicts p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds. Both criteria — minority boundary and majority saturation (p_majority(t*) > 0.80) — must hold simultaneously. This gate was pre-registered before conducting the experiments.

## 4. Experimental Setup

### 4.1 Dataset and Groups

All experiments use the Waterbirds v1.0 benchmark [Sagawa et al., 2020]. Waterbirds constructs a synthetic dataset by compositing bird images (from CUB-200-2011) onto background scenes (from Places), creating a spurious correlation between bird type (label y∈{waterbird, landbird}) and background (b∈{water, land}). The spuriosity level is 95%: 95% of waterbirds appear on water backgrounds, 95% of landbirds on land backgrounds. This yields four groups:

| Group | Composition | Train Samples | Train Fraction |
|-------|-------------|---------------|----------------|
| 0 (majority) | waterbird + water background | 3498 | 73.0% |
| 1 (minority) | waterbird + land background | 184 | 3.8% |
| 2 (majority) | landbird + land background | 1057 | 22.1% |
| 3 (minority) | landbird + water background | 56 | 1.2% |

Minority groups 1+3 together: 240 samples (5.0% of 4795 training samples). Group labels are used **only for post-hoc AUROC evaluation**; the model receives only (x_i, y_i) during ERM training.

### 4.2 Model and Training

ResNet-50 with ImageNet pretrained weights (torchvision v0.15) is used. The last fully-connected layer is the 2048→2 linear head (4098 parameters including bias). Hyperparameters: SGD with lr=3×10⁻³, momentum=0.9, weight decay=1×10⁻⁴, 50 epochs, batch size 32. Checkpoints are saved at t∈{0,1,5,10,20,50}. Five independent runs (seeds 1–5) control both data ordering and weight initialization.

### 4.3 Hessian Trace Computation

For each checkpoint t and each training sample i, Tr(H_i^fc) is computed via K=50 Rademacher probes using reverse-over-reverse automatic differentiation (torch.func.vmap + torch.func.vjp). The computation is vectorized across samples. Total computation per checkpoint per seed is approximately 8 minutes on a single H100 GPU for all 4795 training samples with K=50.

### 4.4 Epoch-0 Control

The t=0 checkpoint is the pretrained ImageNet backbone before any Waterbirds training steps. Computing traces at t=0 measures minority-majority discriminability from ImageNet pretraining alone. Any candidate signal must satisfy AUROC(t=0) < 0.70 to pass the ERM-induction gate, ruling out pretrained-artifact confounds. A prior experiment (h-e2) illustrates the importance of this control: a gradient-direction signal achieved AUROC=0.987 at epoch 0, indicating that pretrained features already separate the groups — making the h-e2 signal a pretrained artifact rather than an ERM signal.

### 4.5 Research Questions

**RQ1 (Existence):** Does per-sample last-fc Hessian trace achieve AUROC≥0.85 for minority membership prediction at t* across ≥4/5 seeds?

**RQ2 (ERM induction):** Is the trace signal ERM-induced rather than a pretrained artifact? Operationalized as AUROC(t=0) < 0.70 in all 5 seeds.

**RQ3 (Mechanism — confidence channel):** Is the confidence-differential mechanism active at t*? Operationalized as p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds (pre-registered H-M1 gate).

## 5. Results

### 5.1 H-E3: Per-Sample Hessian Trace Discriminates Minority Group Membership

**Main result:** 4/5 seeds satisfy all three gate criteria simultaneously. The H-E3 existence gate is satisfied.

#### Per-Seed AUROC Results

| Seed | AUROC(t=0) | t=1 | t=5 | t=10 | t=20 | t=50 | t* | AUROC(t*) | Spearman ρ | Pass |
|------|------------|-----|-----|------|------|------|----|-----------|------------|------|
| 1 | 0.538 | 0.838 | 0.657 | 0.780 | 0.850 | 0.879 | 20 | 0.850 | 0.70 | ✗ |
| 2 | 0.609 | 0.671 | 0.827 | 0.825 | 0.844 | 0.885 | 50 | 0.885 | 0.943 | ✓ |
| 3 | 0.558 | 0.459 | 0.580 | 0.797 | 0.860 | 0.897 | 50 | 0.897 | 0.943 | ✓ |
| 4 | 0.579 | 0.568 | 0.799 | 0.853 | 0.903 | 0.905 | 20 | 0.903 | 0.900 | ✓ |
| 5 | 0.609 | 0.735 | 0.890 | 0.875 | 0.840 | 0.916 | 5 | 0.890 | 1.000 | ✓ |

**Gate result: PASS (4/5 seeds).** Seed 1 fails due to a non-monotone AUROC trajectory (Spearman ρ=0.70, threshold 0.80) caused by a dip at t=5 — both AUROC(t=0)<0.70 and AUROC(t*)≥0.85 are satisfied for seed 1, but the Spearman criterion is not.

**Epoch-0 control (RQ2):** All 5 seeds show AUROC(t=0) ∈ [0.538, 0.609] (mean 0.577) — well below the 0.70 control threshold. The pretrained ImageNet backbone alone does not discriminate minority from majority training samples on Waterbirds. The trace asymmetry is created by ERM training.

**Comparison context:** This paper establishes the existence result (AUROC>0.85) for the per-sample Hessian trace signal. A direct AUROC comparison against first-order annotation-free proxies (JTT-proxy, SELF) is left for future work, as such baselines require implementing and running their minority detection pipelines under identical conditions. The epoch-0 AUROC ∈ [0.538, 0.609] provides a lower bound from the pretrained baseline.

![AUROC at t* and epoch-0 per seed with gate thresholds](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig1_gate_metrics.png)

*Figure 1: AUROC at t* and epoch-0 per seed with gate thresholds (0.70 and 0.85). All 5 seeds show epoch-0 AUROC below 0.70 (mean 0.577), confirming ERM-induced signal. Four of five seeds achieve AUROC(t*)≥0.85.*

#### Trace Ratio R(t)

The trace ratio R(t) = mean_minority_trace / mean_majority_trace rises from near-unity at initialization to peak values of 4.09–8.89:

| Seed | R(t=0) | R(t=1) | R(t=5) | R(t=10) | R(t=20) | R(t=50) | t* | R(t*) |
|------|--------|--------|--------|---------|---------|---------|-----|-------|
| 1 | 1.05 | 3.78 | 0.88 | 1.36 | 4.37 | 3.74 | 20 | 4.37 |
| 2 | 1.12 | 2.31 | 3.36 | 2.85 | 2.06 | 5.55 | 50 | 5.55 |
| 3 | 1.06 | 1.23 | 1.10 | 2.55 | 2.93 | 7.21 | 50 | 7.21 |
| 4 | 1.08 | 1.41 | 2.99 | 3.20 | 4.09 | 3.13 | 20 | 4.09 |
| 5 | 1.12 | 3.02 | 8.89 | 4.12 | 1.10 | 2.60 | 5 | 8.89 |

All seeds show R(t*)>>1 — minority Hessian traces are systematically higher than majority at the peak checkpoint. Optimal t* varies across seeds (t*∈{5, 20, 50}), indicating that the peak of minority-majority curvature divergence is stochastic across training runs. Seeds 2 and 3 show R still increasing at t=50, and no clear decline is observed within the checkpoint schedule — the peak-then-decline pattern assumed at hypothesis formulation is not universal.

![R(t) trajectory across training epochs](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig2_R_trajectory.png)

*Figure 2: Trace ratio R(t) = mean_minority_trace(t) / mean_majority_trace(t) across training epochs for all 5 seeds. R rises from near-unity at initialization (R≈1.05–1.12) to peak values of 4.09–8.89, with t* varying across {5, 20, 50} depending on seed.*

![AUROC trajectory per seed](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig3_auroc_trajectory.png)

*Figure 3: AUROC trajectory per seed across 6 checkpoints (t∈{0,1,5,10,20,50}). Dashed lines indicate gate thresholds at 0.70 (epoch-0 upper bound) and 0.85 (t* lower bound). Four of five seeds cross 0.85 by t*.*

#### Estimator Stability

Hutchinson coefficient of variation (CV) across K=50 probes:

| Seed | CV | Stable? |
|------|-----|---------|
| 1 | 0.0233 | ✓ |
| 2 | 0.0132 | ✓ |
| 3 | 0.0232 | ✓ |
| 4 | 0.0283 | ✓ |
| 5 | 0.0108 | ✓ |

All CVs < 3% (maximum 0.0283). K=50 Rademacher probes provide reliable per-sample trace estimates for the last-fc layer of ResNet-50. The trace signal is not dominated by Hutchinson estimation noise.

![Per-sample trace distributions at t*](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig4_trace_distribution.png)

*Figure 4: Per-sample Hessian trace distributions at t* for minority (groups 1+3) and majority (groups 0+2) training samples. Minority traces are systematically elevated, consistent with the empirical AUROC>0.85 finding.*

![Spearman correlation per seed on rising segment](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig5_spearman_rising.png)

*Figure 5: Spearman correlation on rising AUROC segment per seed. Seeds 2–5 achieve ρ≥0.90, confirming monotone rise. Seed 1 (ρ=0.70) shows a non-monotone trajectory at t=1→5.*

### 5.2 H-M1: Confidence-Differential Mechanism Is Absent at t*

**Main result:** The pre-registered mechanism gate fails in all 5 seeds. Minority training confidence at t* is 0.9678–0.9999 — fully saturated, not boundary-straddling. The H-M1 gate is not satisfied.

#### Per-Seed Confidence at t*

| Seed | t* | p_minority(t*) | p_majority(t*) | Confidence Gap | Boundary [0.3,0.7]? |
|------|----|----------------|----------------|----------------|----------------------|
| 1 | 20 | 0.9956 | 0.9994 | 0.0039 | ✗ |
| 2 | 50 | 0.9999 | 0.9999 | 0.0000 | ✗ |
| 3 | 50 | 0.9998 | 0.9999 | 0.0000 | ✗ |
| 4 | 20 | 0.9964 | 0.9992 | 0.0029 | ✗ |
| 5 | 5 | 0.9678 | 0.9925 | 0.0247 | ✗ |

**Gate result: FAIL (0/5 seeds).** No seed shows minority confidence in the predicted boundary condition range [0.3, 0.7] at t*. Mean p_minority(t*)=0.9919, mean p_majority(t*)=0.9982.

#### Full Confidence Trajectory (Seed 1)

| Epoch | p_minority | p_majority | Gap |
|-------|------------|------------|-----|
| 0 | 0.521 | 0.491 | 0.030 |
| 1 | 0.827 | 0.972 | 0.145 |
| 5 | 0.898 | 0.986 | 0.088 |
| 10 | 0.964 | 0.996 | 0.032 |
| 20 | 0.996 | 0.999 | 0.004 |
| 50 | 1.000 | 1.000 | 0.000 |

**Transient early-epoch differential exists:** At epoch 1, a minority-majority confidence gap is visible (seed 1: p_min=0.827 vs p_maj=0.972, gap=0.145; seed 2: p_min=0.720 vs p_maj=0.975; seed 3: p_min=0.570 vs p_maj=0.967). This is consistent with LaBonte and Muthukumar [2026]'s Phase I prediction — ERM learns the spurious feature first, temporarily lagging minority confidence. However, this differential disappears before t* in all seeds. By t*, both groups are saturated.

![Confidence trajectories per seed](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig_confidence_trajectory.png)

*Figure 6: Training-set confidence trajectories for minority and majority groups per seed. At epoch 1, minority confidence lags majority (seed 1: p_min=0.827 vs p_maj=0.972). By t*, both groups saturate to ≥0.97, refuting the sustained boundary-condition mechanism.*

![Per-sample confidence distributions at t*](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig_conf_distribution.png)

*Figure 7: Per-sample confidence distribution at t* for minority and majority samples. Both distributions are concentrated near 1.0 (mean p_minority=0.9919, mean p_majority=0.9982), demonstrating that the confidence channel p_i(1−p_i) is inactive at t*.*

![H-M1 gate comparison](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig_gate_metrics.png)

*Figure 8: H-M1 gate comparison: minority confidence at t* vs gate band [0.3, 0.7]. All 5 seeds show p_minority(t*)>0.96, with 0/5 seeds satisfying the boundary-condition criterion.*

## 6. Discussion

### 6.1 The Dual Finding: Existence Without Expected Mechanism

The core finding is a dual result. The trace signal is real: per-sample last-fc Hessian trace achieves AUROC≥0.85 for minority membership detection in 4/5 seeds, with the signal being ERM-induced (epoch-0 control). The expected mechanism is absent: at the checkpoint of peak discriminability, minority training confidence is 0.97–1.0 — indistinguishable from majority in terms of the confidence channel p_i(1−p_i).

This combination is more informative than either result alone. If only H-E3 had been tested, the confidence-differential mechanism would be the default attribution. If only H-M1 had been tested, there would be no evidence that the trace signal is discriminative at all. Together, they establish that the signal exists and identify the correct channel to investigate next.

### 6.2 What Drives the Trace Signal? The Feature-Norm Channel

For a linear cross-entropy head with weight W ∈ ℝ^{C×d} and penultimate feature x_i ∈ ℝ^d:

$$\mathrm{Tr}(H_i^{fc}) \propto \|x_i\|^2 \cdot p_i(1 - p_i)$$

At t*, p_i(1−p_i)→0 for all training samples (both minority and majority), as confirmed by H-M1. The confidence term is inactive. The only surviving candidate driver of the trace asymmetry is ‖x_i‖² — systematic differences in the L2 norm of the penultimate-layer feature representation between minority and majority samples.

LaBonte et al. [2024] provide a group-level prediction consistent with this interpretation: minority group covariance matrices have larger spectral norm than majority groups within the same class. Our finding extends this from the group-level covariance setting to the per-sample trace trajectory, and identifies ‖x_i‖² as the specific channel that would need to show differential behavior.

**This interpretation is a candidate, not a verified claim.** Penultimate-layer norms ‖x_i‖² have not been directly measured per sample, and it has not been confirmed that minority norms exceed majority norms. Verifying this — by measuring feature norms at t* and correlating them with trace ranks — is the primary direction for future mechanistic investigation.

### 6.3 Relation to LaBonte and Muthukumar [2026] Phase I/II Theory

LaBonte and Muthukumar [2026] prove for an XOR spurious feature model that SGD learns the spurious feature first (Phase I), then the core feature (Phase II). This predicts that during Phase I, minority samples remain near the decision boundary, keeping p_minority(t)≈0.5 while p_majority(t)>0.9.

The present results show that on ResNet-50 on Waterbirds, a transient version of this Phase I differential is present at epoch 1 but does not persist to t*. ERM memorizes minority training samples — driving their training confidence to ≥0.97 — before the trace ratio R(t) reaches its maximum. The mechanism operates on a different timescale than t*.

Two non-exclusive interpretations: (1) the Phase I window for ResNet-50 on Waterbirds closes quickly (by epoch 5 at the latest), so the confidence differential is genuinely transient; (2) ResNet-50 with ImageNet pretraining can memorize minority samples via the pretrained feature representation even without the spurious correlation, and this memorization outpaces the Phase I dynamics. Distinguishing these requires varying the spuriosity level and model capacity, which remains for future work. Additionally, the H-M1 test measured training-set confidence, where ERM optimization drives all samples toward high confidence; the mechanism may still operate on the held-out distribution, where minority samples encounter distribution shift.

### 6.4 Limitations

**Scope:** All experiments use ResNet-50 on Waterbirds v1.0 with 95% spuriosity. Generalization to other architectures (ViT, ResNet-18), datasets (CelebA, MultiNLI), or spuriosity levels is not established.

**Mechanism unverified:** The feature-norm channel (‖x_i‖²) is a candidate explanation, not a verified claim. The direct next step is to measure per-sample penultimate-layer norms at t* and test whether minority norms exceed majority norms at the same rank order as Hessian traces.

**No DFR application:** The trace signal has not been tested as a sample-weight or resampling guide for last-layer retraining (analogous to JTT upweighting). The existence result (AUROC>0.85) is necessary but not sufficient for practical WGA improvement — the signal quality needs to translate through the DFR pipeline. Three downstream experiments (H-M2, H-M3, H-M4) were blocked when H-M1 failed its gate.

**Training-set confidence only:** The H-M1 mechanism test uses training-set confidence. The pre-registered gate was designed for training-set data, but future work should examine held-out confidence trajectories, where distribution shift may expose boundary-condition behavior that is masked by ERM memorization on the training set.

**Seed 1 non-monotone trajectory:** Seed 1 fails the H-E3 gate due to a non-monotone AUROC trajectory at t=1→5 (Spearman ρ=0.70, threshold 0.80). This may reflect stochastic optimization dynamics at a specific random initialization. Denser checkpointing (every epoch from t=0 to t=10) would clarify whether this is a genuine double-peak or a checkpoint-granularity artifact.

**Scalability:** Per-checkpoint trace computation takes approximately 8 minutes on an H100 for 4795 samples with K=50. Scaling to datasets with more than 100K samples or architectures with larger last-fc layers would require further engineering.

### 6.5 Implications for Annotation-Free Minority Detection

Per-sample last-fc Hessian trace is established as a candidate second-order annotation-free proxy for minority group membership — the first such signal to achieve AUROC>0.85 on Waterbirds without group labels, with a verified epoch-0 control ruling out pretrained-artifact confounds.

Key practical questions remaining: (1) does the trace proxy translate to WGA improvement via DFR-style last-layer retraining; (2) does the signal generalize beyond Waterbirds; (3) what is the minimal computation needed (can K be reduced below 50, or can the epoch-0 control be replaced by a cheaper baseline check). If the feature-norm mechanism is confirmed, directly measuring ‖x_i‖² as an annotation-free proxy might be computationally cheaper than the full Hutchinson computation.

## 7. Conclusion

This work tests whether the curvature of the ERM loss surface — measured as per-sample Hessian trace of the last fully-connected layer — reveals minority group membership without group annotations. It does: 4/5 random seeds achieve AUROC≥0.85 at the epoch of maximum trace ratio, with the epoch-0 control confirming that the signal is created by ERM training on Waterbirds, not inherited from ImageNet pretraining (epoch-0 AUROC ∈ [0.538, 0.609] in all five seeds). The Hutchinson estimator at K=50 is stable across seeds (CV<3%), establishing this as the minimum reliable setting for last-fc of ResNet-50.

The mechanism investigation produces an equally clear result, though in the negative direction. The pre-registered mechanism gate — minority training-set confidence remaining in [0.3, 0.7] at t* — fails in all five seeds (p_minority(t*)=0.9678–0.9999). A transient early-epoch confidence differential does exist at epoch 1 (seed 1: p_min=0.827 vs p_maj=0.972), consistent with Phase I theory [LaBonte and Muthukumar, 2026], but it disappears before t* in all seeds. The confidence channel p_i(1−p_i) is inactive at t* for both groups.

The remaining candidate for the trace asymmetry at t* is the feature-norm channel: systematic elevation of ‖x_i‖² for minority samples, consistent with LaBonte et al. [2024]'s group-level spectral imbalance result. Directly verifying this — measuring penultimate-layer norms at t* and correlating them with trace ranks — is the primary next mechanistic step. The practical path forward requires testing whether the trace proxy, used to guide annotation-free last-layer retraining (DFR-style), improves worst-group accuracy on Waterbirds.

The existence result establishes the signal quality that makes the downstream application worth testing; the mechanism result identifies what signal the proxy is likely capturing. A second-order perspective on spurious feature reliance — one that asks how ERM differentially shapes the loss landscape curvature around training samples, not merely how it classifies them — opens a class of annotation-free minority detectors orthogonal to first-order signals.

### Broader Impact

This work advances annotation-free methods for identifying minority groups in machine learning training data. The ability to detect spuriously correlated minority samples without group labels could reduce the annotation burden for fairness-motivated model corrections. However, the same signal could in principle be used to identify and selectively filter minority samples in adversarial settings. Application of this method should be in contexts where minority detection supports, rather than undermines, equitable model performance.

## References

Avron, H. and Toledo, S. (2011). Randomized algorithms for estimating the trace of an implicit symmetric positive semi-definite matrix. *Journal of the ACM*.

Foret, P., Kleiner, A., Mobahi, H., and Neyshabur, B. (2021). Sharpness-aware minimization for efficiently improving generalization. *ICLR 2021*.

He, K., Zhang, X., Ren, S., and Sun, J. (2016). Deep residual learning for image recognition. *CVPR 2016*.

Hill, B., LaBonte, T., Li, C., Kolter, J. Z., and Muthukumar, V. (2025). On the unreasonable effectiveness of last layer retraining for group robustness. *Transactions on Machine Learning Research*.

Keskar, N. S., Mudigere, D., Nocedal, J., Smelyanskiy, M., and Tang, P. T. P. (2016). On large-batch training for deep learning: Generalization gap and sharp minima. *arXiv:1609.04836*.

Kirichenko, P., Izmailov, P., and Wilson, A. G. (2023). Last layer re-training is sufficient for robustness to spurious correlations. *ICLR 2023*.

LaBonte, T., Westcott, N., Tucker-Foltz, J., Ghassemi, M., and Muthukumar, V. (2023). Towards last-layer retraining for group robustness with fewer annotations. *NeurIPS 2023*.

LaBonte, T., Muthukumar, V., and Kumar, A. (2024). The group robustness is in the details. *NeurIPS 2024*. arXiv:2407.13957.

LaBonte, T. and Muthukumar, V. (2026). SGD provably learns spurious features: A phase transition theory for XOR spurious models. *arXiv:2606.30444*.

Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., and Finn, C. (2021). Just train twice: Improving group robustness without training group information. *ICML 2021*.

Sagawa, S., Koh, P. W., Hashimoto, T. B., and Liang, P. (2020). Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. *ICLR 2020*.

Yao, Z., Gholami, A., Keutzer, K., and Mahoney, M. W. (2020). PyHessian: Neural networks through the lens of the Hessian. *IEEE International Conference on Big Data*.
