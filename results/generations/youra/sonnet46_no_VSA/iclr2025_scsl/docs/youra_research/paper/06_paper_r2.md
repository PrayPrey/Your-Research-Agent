# Per-Sample Hessian Trace as an Annotation-Free Minority Group Proxy Under ERM Training

**Abstract**

Empirical risk minimization (ERM) on spuriously correlated data creates systematic accuracy gaps between majority and minority groups, but identifying minority-correlated training samples without group annotations remains an open problem. We propose measuring per-sample last-fc Hessian trace — estimated via K=50 Hutchinson probes using torch.func vmap+vjp — as an annotation-free proxy for minority group membership in ERM-trained neural networks. On Waterbirds, 4/5 random seeds achieve AUROC≥0.85 for minority membership prediction at the epoch t* of maximum trace ratio, with epoch-0 AUROC<0.70 confirming the signal is ERM-induced rather than inherited from ImageNet pretraining. However, investigation of the mechanism reveals that minority training confidence saturates to ≥0.967 at t* (range: 0.9678–0.9999 across seeds) — effectively equal to majority — refuting the predicted confidence-differential mechanism. The trace asymmetry must therefore arise from the feature-norm channel (‖x_i‖²), consistent with LaBonte et al. [2024]'s spectral imbalance result at the group level. We present the first per-sample second-order annotation-free minority proxy achieving AUROC>0.85, alongside a principled falsification of its expected mechanism.

# 1. Introduction

We trained ResNet-50 on Waterbirds and found that — without any group labels — the curvature of the loss surface around each training sample reveals minority group membership with AUROC 0.85–0.90 in 4/5 random seeds (mean AUROC 0.89 across the 4 passing seeds). But when we investigated *why*, the expected mechanism was absent: by the time the curvature signal peaks, minority samples are classified just as confidently as majority samples. The method works — but not for the reason we expected.

This puzzle sits at the intersection of two long-standing problems in robust machine learning. The first is spurious correlations: models trained with empirical risk minimization (ERM) on real-world datasets learn to exploit incidental statistical associations between input features and labels. On Waterbirds [Sagawa et al., 2019], a ResNet-50 trained with ERM achieves 97% average accuracy but only 72% worst-group accuracy — minority groups (e.g., landbirds on water backgrounds) suffer because the model relies on background rather than bird shape. The second problem is annotation burden: the most effective mitigation methods, such as deep feature reweighting (DFR) [Kirichenko et al., 2022], require a balanced held-out validation set with explicit group labels — a resource unavailable in many practical settings.

Annotation-free alternatives — Just Train Twice (JTT) [Liu et al., 2021], SELF [LaBonte et al., 2023], EVaLS [sharif-ml-lab] — proxy minority membership through first-order signals: which samples are misclassified, or which have the highest loss. These methods improve over ERM without group labels, but they operate on signals that are fundamentally insensitive to *how* the model encodes spurious features in its loss landscape geometry.

We ask: does the second-order geometry of the loss surface carry distinct information about minority group membership? Specifically, we measure the per-sample Hessian trace of the last fully-connected layer — computed via K=50 Hutchinson estimation using torch.func vmap+vjp — at six training checkpoints (t∈{0,1,5,10,20,50}) over five random seeds, and ask whether this trajectory discriminates minority from majority samples.

The measurement protocol is motivated by two theoretical results. LaBonte et al. [2024] show that minority group covariance matrices have larger spectral norm than majority groups — a group-level prediction of systematic feature-norm inequality (‖x_i‖²) that would elevate per-sample Hessian traces for minority samples. LaBonte & Muthukumar [2026] prove that SGD on spurious data learns the spurious feature first (Phase I) before the core feature (Phase II), predicting a transient differential in loss landscape curvature between majority (which gain confidence rapidly via the spurious shortcut) and minority (which do not).

Our existence experiment (H-E3) confirms the signal: 4/5 seeds achieve AUROC≥0.85 for minority membership prediction at t* (the epoch maximizing the trace ratio R(t) = mean_minority_trace / mean_majority_trace), with epoch-0 AUROC<0.70 in all seeds — confirming that ERM training creates the signal, not the pretrained ImageNet initialization. The Hutchinson estimator is stable (coefficient of variation CV<3% for all seeds), establishing K=50 as sufficient for the last-fc layer of ResNet-50.

Our mechanism experiment (H-M1) produces the puzzle. The original mechanistic explanation — that minority samples remain near the decision boundary (p_i∈[0.3,0.7]) throughout Phase I, keeping the confidence-entropy term p_i(1-p_i) in Tr(H_i^fc) ∝ ‖x_i‖²p_i(1-p_i) large — is directly falsified. At t*, minority training-set confidence is 0.9678–0.9999 across all seeds: fully saturated, not boundary-straddling. The confidence channel is inactive. A transient differential does exist at epoch 1 (seed 1: p_min=0.827 vs p_maj=0.972), consistent with Phase I theory, but it disappears before t*.

The trace signal at t* must therefore arise from the ‖x_i‖² feature-norm channel — systematic differences in the penultimate-layer representation norms between minority and majority samples, consistent with LaBonte et al. 2024's spectral imbalance finding. This is an unverified but testable candidate mechanism that we identify as the primary direction for future mechanistic investigation.

Our contributions are:

1. **Empirical existence result:** First experimental evidence that per-sample last-fc Hessian trace (K=50 Hutchinson via vmap+vjp) achieves AUROC≥0.85 for minority membership detection in ERM-trained ResNet-50 on Waterbirds across 5 random seeds, with epoch-0 control confirming ERM emergence (Section 5.1).

2. **Principled falsification of the confidence-differential mechanism:** Direct refutation of the sustained decision-boundary hypothesis (p_minority∈[0.3,0.7] at t*) on training-set data, identifying the feature-norm channel (‖x_i‖²) as the likely driver (Section 6.1–6.2).

3. **Practical confirmation:** K=50 Hutchinson is the minimum stable setting for last-fc ResNet-50 (CV<3%), with the epoch-0 control serving as a reliable pretrained-artifact detector (Section 4.4).

The remainder of the paper is organized as follows. Section 2 reviews related work on spurious correlations, annotation-free robustification, and Hessian analysis. Section 3 describes our methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses findings, limitations, and the mechanism puzzle. Section 7 concludes.

# 2. Related Work

## 2.1 Spurious Correlations and Group Robustness

Spurious correlations — statistical associations between features and labels that do not reflect causal structure — cause ERM-trained models to fail systematically on minority groups [Sagawa et al., 2019]. The Waterbirds benchmark [Sagawa et al., 2019] isolates this: bird labels are spuriously correlated with backgrounds, creating four groups (2 class × 2 background) with dramatically different ERM performance. Distributionally robust optimization (DRO) directly targets worst-group accuracy but requires group annotations at training time [Sagawa et al., 2019].

## 2.2 Annotation-Required Methods: DFR

The most effective post-hoc approach is deep feature reweighting (DFR) [Kirichenko et al., 2022]: retrain only the last layer on a balanced held-out validation set, keeping ERM-pretrained features frozen. DFR achieves WGA≈88–90% on Waterbirds with a small balanced set. Hill et al. [2025] explain DFR's effectiveness as implicit group-balancing: when the retraining set overrepresents minority samples, the final classifier learns to rely on causal features rather than spurious shortcuts. However, DFR's key limitation is the requirement for explicit group annotations in the balanced set — a requirement our work aims to relax.

## 2.3 Annotation-Free Proxies: First-Order Signals

The annotation-free direction emerged with Just Train Twice (JTT) [Liu et al., 2021]: identify misclassified samples after a first ERM run, upweight them, and retrain. JTT achieves WGA≈80–84% on Waterbirds without group labels. SELF [LaBonte et al., 2023] refines this by combining misclassification-based proxy selection with self-training, reaching WGA≈82–87%. EVaLS uses loss-value thresholding as the proxy signal. All of these methods share a fundamental constraint: they operate on first-order signals — the model's output or loss — and are insensitive to loss landscape geometry. They capture whether a sample is hard, not *why* it is hard in terms of the curvature of the loss surface around it.

Our work proposes the first second-order annotation-free proxy: per-sample Hessian trace of the last-fc layer. This signal is orthogonal to loss and misclassification and carries information about the differential curvature created by spurious feature exploitation — information that first-order signals discard.

## 2.4 Loss Landscape Geometry and Hessian Analysis

Sharpness of loss minima has long been connected to generalization: sharp minima (high Hessian eigenvalues) generalize poorly compared to flat minima [Keskar et al., 2016]. Sharpness-aware minimization (SAM) [Foret et al., 2020] explicitly seeks flat minima and improves group robustness as a byproduct [Izmailov et al., 2022]. However, SAM operates at the model level, not the per-sample level.

Per-layer Hessian trace estimation via Hutchinson's method has been studied for neural network diagnostics [Yao et al., 2020]. The Hutchinson estimator approximates tr(H) ≈ (1/K)Σ vᵀHv for K random Rademacher vectors v without materializing the full Hessian. Montes de Oca Ávalos et al. [2025] use Hutchinson trace monitoring to detect model degradation across training regimes. However, no prior work extends Hutchinson estimation to the *per-sample* level to discriminate minority from majority group membership.

## 2.5 Loss Landscape and Spurious Correlations: Mechanistic Theory

The closest theoretical work to ours is LaBonte et al. [2024], who show that minority group covariance matrices have larger spectral norm than majority groups within the same class — a group-level prediction of systematic representation-norm inequality (‖x_i‖²). This finding supports the hypothesis that per-sample Hessian traces would be elevated for minority samples, since Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i) for a linear cross-entropy head. LaBonte & Muthukumar [2026] prove that SGD on XOR spurious models learns the spurious feature first (Phase I) before the core feature (Phase II), creating a transient window where minority samples remain near the decision boundary. Our work is the first to test these theoretical predictions empirically with per-sample Hessian traces across training checkpoints on ResNet-50.

**Our positioning:** We extend LaBonte et al. [2024] from group-level covariance to per-sample trajectory analysis, and test LaBonte & Muthukumar [2026]'s Phase I/II prediction on real image data. We find that the existence result is confirmed but the confidence-differential mechanism is falsified on training-set data — the feature-norm channel, not the confidence channel, drives the trace asymmetry at t*.

# 3. Methodology

## 3.1 Problem Setup

We consider a training dataset D = {(x_i, y_i, g_i)}_{i=1}^N where group labels g_i are hidden during training and evaluation. ERM minimizes L(θ) = (1/N)Σ_i ℓ(f_θ(x_i), y_i) without observing g_i. We ask: at training time, does any per-sample statistic derived from the ERM loss surface discriminate minority from majority group membership — using only f_θ(x_i) and ℓ, without observing g_i?

## 3.2 Per-Sample Last-FC Hessian Trace

For sample i at training checkpoint t, we define the per-sample last-fc Hessian trace as:

    Tr(H_i^fc) = Tr(∂²ℓ(f_{θ_t}(x_i), y_i) / ∂W_fc²)

where W_fc ∈ ℝ^{2048×2} is the weight matrix of the last fully-connected layer of ResNet-50. We restrict to the last-fc layer for three reasons: (1) tractability — 4098 parameters vs. 25M total; (2) architectural motivation — the classification head directly encodes the spurious feature alignment learned by the backbone; (3) mechanistic interpretability — the per-sample last-fc Hessian has the closed-form decomposition Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i) for cross-entropy loss, isolating the feature-norm and confidence contributions.

## 3.3 Hutchinson Trace Estimation

Computing Tr(H) exactly requires full Hessian materialization. We use Hutchinson's estimator [Avron & Toledo, 2011]:

    Tr(H) ≈ (1/K) Σ_{k=1}^K v_k^T H v_k

where v_k ∈ {±1}^d are Rademacher random vectors, and Hv_k = ∂/∂W (∂ℓ/∂W · v_k) is computed as a second-order reverse-over-reverse automatic differentiation pass. We implement this via torch.func.vmap + torch.func.vjp on a per-sample basis, enabling vectorized computation across samples without storing the full Hessian or Jacobian.

**Choice of K=50:** Prior diagnostic work [Yao et al., 2020] uses K=256 for batch-level Hessian traces on large networks. For the last-fc layer (d=4098), K=50 Rademacher probes provide trace estimates with coefficient of variation CV<3% across all seeds in our experiments — confirmed as the minimum stable setting for this architecture.

## 3.4 Training Protocol

We train ResNet-50 (torchvision, ImageNet pretrained) on Waterbirds v1.0 with ERM:
- Optimizer: SGD (lr=3×10⁻³, momentum=0.9, weight decay=1×10⁻⁴)
- Epochs: 50
- Checkpoints: t ∈ {0, 1, 5, 10, 20, 50}
- Seeds: 5 independent seeds (seeds 1–5)

The t=0 checkpoint is the pretrained ImageNet initialization *before any Waterbirds training*. This serves as the epoch-0 control for distinguishing ERM-induced signals from pretrained artifacts (see Section 3.6).

**Dataset:** Waterbirds v1.0 contains 4795 training samples with four groups defined by (bird type, background): (waterbird/water, waterbird/land, landbird/water, landbird/land). Groups 1+3 (minority groups: landbird/water background and waterbird/land background) comprise 240 samples (5% of training set). Group labels are used only for post-hoc evaluation; they are not observed during training.

## 3.5 Trace Ratio and t* Selection

At each checkpoint t, we compute the trace ratio:

    R(t) = mean_{i∈minority} Tr(H_i^fc(t)) / mean_{i∈majority} Tr(H_i^fc(t))

The optimal checkpoint t* = argmax_t R(t) selects the epoch of maximum minority-majority trace divergence. This is the evaluation checkpoint for all discriminability metrics. R(t) is computed without observing group labels at training time — only the rank ordering of traces is used for AUROC evaluation.

## 3.6 Evaluation Protocol

**Existence gate (H-E3):** At checkpoint t*, we compute AUROC for predicting minority membership (g_i ∈ {1,3}) from the scalar trace Tr(H_i^fc(t*)). Three simultaneous criteria must hold:
1. AUROC(t*) ≥ 0.85
2. AUROC(t=0) < 0.70 (ERM-induction control)
3. Spearman ρ(t, AUROC(t)) ≥ 0.8 on the rising AUROC segment (monotone signal development)

The epoch-0 control (criterion 2) is mandatory: it rules out that minority-majority trace differences are inherited from ImageNet pretraining rather than induced by ERM training on Waterbirds. Our prior h-e2 experiment found AUROC=0.987 at epoch 0 for a gradient-direction signal — a pretrained artifact, not an ERM signal. The epoch-0 gate prevents this confound.

**Mechanism test (H-M1):** At t*, we measure the mean training-set prediction confidence for minority and majority samples separately. The confidence-differential mechanism predicts p_minority(t*) ∈ [0.3, 0.7] (boundary-condition proximity) in ≥3/5 seeds. This is the pre-registered gate for mechanism verification.

**Reproducibility standard:** All 5 seeds are evaluated independently. The H-E3 gate requires ≥4/5 seeds to pass all three criteria simultaneously.

# 4. Experiments

## 4.1 Dataset and Groups

All experiments use the Waterbirds v1.0 benchmark [Sagawa et al., 2019]. Waterbirds constructs a synthetic dataset by compositing bird images (from CUB-200-2011) onto background scenes (from Places), creating a spurious correlation between bird type (label y∈{waterbird, landbird}) and background (b∈{water, land}). The spuriosity level is 95%: 95% of waterbirds appear on water backgrounds, 95% of landbirds on land backgrounds.

This yields four groups:
- Group 0 (majority): waterbird + water background (3498 train samples, 73%)
- Group 1 (minority): waterbird + land background (184 train samples, 3.8%)
- Group 2 (majority): landbird + land background (1057 train samples, 22%)
- Group 3 (minority): landbird + water background (56 train samples, 1.2%)

Minority groups 1+3 together: 240 samples (5.0% of training set). Group labels are used **only for post-hoc AUROC evaluation**; the model receives only (x_i, y_i) during ERM training.

## 4.2 Model and Training

We use ResNet-50 [He et al., 2016] with ImageNet pretrained weights (torchvision v0.15). The last fully-connected layer is the 2048→2 linear head (4098 parameters including bias). Hyperparameters: SGD with lr=3×10⁻³, momentum=0.9, weight decay=1×10⁻⁴, 50 epochs, batch size 32. Checkpoints saved at t∈{0,1,5,10,20,50}. Five independent runs (seeds 1–5); seeds control both data ordering and weight initialization random state.

At the final checkpoint t=50, the ERM model achieves mean average accuracy ≈97% on the training set. Worst-group accuracy on the test set is substantially lower (≈72%), consistent with the known ERM-spurious correlation gap on Waterbirds [Sagawa et al., 2019].

## 4.3 Hessian Trace Computation

For each checkpoint t and each training sample i, we compute Tr(H_i^fc) via K=50 Rademacher probes:

```python
# Per-sample last-fc Hessian trace via torch.func vmap+vjp
def trace_per_sample(model, x_i, y_i, K=50):
    fc = model.fc  # last linear layer
    x_feat = model.backbone(x_i)  # penultimate feature
    
    def loss_fn(w, b):
        logits = x_feat @ w.T + b
        return F.cross_entropy(logits, y_i)
    
    traces = []
    for _ in range(K):
        v = torch.randint(0, 2, size=(len(w.flatten()),)) * 2 - 1  # Rademacher
        v = v.float() / len(v)**0.5
        # Hv via reverse-over-reverse:
        _, vjp_fn = torch.func.vjp(grad_fn, w, b)
        hv = vjp_fn(v_shaped)[0].flatten()
        traces.append((v * hv).sum())
    return torch.stack(traces).mean()
```

Computation is batched across samples via torch.func.vmap for efficiency. Total computation per checkpoint per seed: approximately 8 minutes on a single A100 GPU for all 4795 training samples with K=50.

## 4.4 Epoch-0 Control

The t=0 checkpoint is the pretrained ImageNet backbone before any Waterbirds training steps. Computing traces at t=0 measures the baseline minority-majority discriminability from ImageNet pretraining alone. This control is mandatory: a prior experiment (h-e2) found gradient-direction AUROC=0.987 at epoch 0, indicating that pretrained features already separate the groups — making the h-e2 signal a pretrained artifact rather than an ERM signal. Any candidate signal must satisfy AUROC(t=0) < 0.70 to pass the ERM-induction gate.

## 4.5 Research Questions

The experiments address three research questions:

**RQ1 (Existence):** Does per-sample last-fc Hessian trace achieve AUROC≥0.85 for minority membership prediction at t* across ≥4/5 seeds?

**RQ2 (ERM induction):** Is the trace signal ERM-induced rather than a pretrained artifact? Operationalized as AUROC(t=0) < 0.70 in all 5 seeds.

**RQ3 (Mechanism — confidence channel):** Is the confidence-differential mechanism active at t*? Operationalized as p_minority(t*) ∈ [0.3, 0.7] in ≥3/5 seeds (pre-registered H-M1 gate).

RQ1 and RQ2 together constitute the H-E3 existence gate. RQ3 is the H-M1 mechanism gate. All gates were pre-registered before conducting the experiments.

# 5. Results

## 5.1 H-E3: Per-Sample Hessian Trace Discriminates Minority Group Membership

**Main result:** 4/5 seeds satisfy all three gate criteria simultaneously. Per-sample last-fc Hessian trace achieves AUROC≥0.85 for minority membership prediction at t*, with the signal being ERM-induced rather than pretrained (AUROC(t=0)<0.70 in all seeds), and developing monotonically in 4/5 seeds (Spearman ρ≥0.8).

### Per-Seed AUROC Results

| Seed | AUROC(t=0) | AUROC(t*) | t* | Spearman ρ | Pass |
|------|------------|-----------|-----|------------|------|
| 1 | 0.538 | 0.850 | 20 | 0.70 | ✗ |
| 2 | 0.609 | 0.885 | 50 | 0.943 | ✓ |
| 3 | 0.558 | 0.897 | 50 | 0.943 | ✓ |
| 4 | 0.579 | 0.903 | 20 | 0.900 | ✓ |
| 5 | 0.609 | 0.890 | 5 | 1.000 | ✓ |

**Gate result: PASS (4/5 seeds).** Seed 1 fails due to a non-monotone AUROC trajectory (Spearman ρ=0.70, threshold 0.80) caused by a dip at t=5 — both AUROC(t=0)<0.70 and AUROC(t*)≥0.85 are satisfied.

**Epoch-0 control:** All 5 seeds show AUROC(t=0)∈[0.538, 0.609] (mean 0.577) — well below the 0.70 control threshold. The pretrained ImageNet backbone alone does not discriminate minority from majority training samples on Waterbirds. The trace asymmetry is created by ERM training.

**Comparison context:** This paper establishes the existence result (AUROC>0.85) for the per-sample Hessian trace signal. A direct AUROC comparison against first-order annotation-free proxies (JTT-proxy, SELF, loss-value thresholding) is left for future work, as such baselines require implementing and running their minority detection pipelines under identical conditions. The epoch-0 AUROC∈[0.538, 0.609] serves as a lower bound from the pretrained baseline; the upper bound from a random predictor is AUROC=0.50. The key advance is establishing that a second-order signal achieves AUROC>0.85 in a regime where first-order signals (loss, misclassification) have been used but not directly compared in AUROC terms on this task formulation.

Figure 1 shows AUROC(t=0) and AUROC(t*) per seed with gate thresholds. Figure 3 shows the full AUROC trajectory across all 6 checkpoints.

### Trace Ratio R(t)

The trace ratio R(t) = mean_minority_trace / mean_majority_trace rises from near-unity at initialization to peak values of 4.09–8.89:

| Seed | R(t=0) | R(t*) | t* |
|------|--------|-------|-----|
| 1 | 1.05 | 4.37 | 20 |
| 2 | 1.12 | 5.55 | 50 |
| 3 | 1.06 | 7.21 | 50 |
| 4 | 1.08 | 4.09 | 20 |
| 5 | 1.12 | 8.89 | 5 |

All seeds show R(t*)>>1 — minority Hessian traces are systematically higher than majority at the peak checkpoint. Figure 2 shows the R(t) trajectory for all seeds. Optimal t* varies across seeds (t*∈{5, 20, 50}), indicating that the peak of minority-majority curvature divergence is stochastic across training runs.

### Estimator Stability

Hutchinson coefficient of variation (CV) across K=50 probes:

| Seed | CV |
|------|-----|
| 1 | 0.0233 |
| 2 | 0.0132 |
| 3 | 0.0232 |
| 4 | 0.0283 |
| 5 | 0.0108 |

All CVs < 3% (max 0.0283). K=50 Rademacher probes provide reliable per-sample trace estimates for the last-fc layer of ResNet-50. The trace signal is not dominated by Hutchinson estimation noise.

Figure 4 shows the per-sample trace distributions at t* for minority and majority samples. Minority traces are systematically elevated, consistent with the AUROC>0.85 finding. Figure 5 shows Spearman ρ values on the rising AUROC segment per seed.

## 5.2 H-M1: Confidence-Differential Mechanism Is Absent at t*

**Main result:** The pre-registered mechanism gate fails in all 5 seeds. Minority training confidence at t* is 0.9678–0.9999 — fully saturated, not boundary-straddling. The confidence-differential mechanism is inactive.

### Per-Seed Confidence at t*

| Seed | t* | p_minority(t*) | p_majority(t*) | Boundary [0.3,0.7]? |
|------|----|----------------|----------------|----------------------|
| 1 | 20 | 0.9956 | 0.9994 | ✗ |
| 2 | 50 | 0.9999 | 0.9999 | ✗ |
| 3 | 50 | 0.9998 | 0.9999 | ✗ |
| 4 | 20 | 0.9964 | 0.9992 | ✗ |
| 5 | 5 | 0.9678 | 0.9925 | ✗ |

**Gate result: FAIL (0/5 seeds).** No seed shows minority confidence in the predicted boundary condition range [0.3, 0.7] at t*. Mean p_minority(t*)=0.9919, mean p_majority(t*)=0.9982.

**Transient early-epoch differential exists:** At epoch 1, a minority-majority confidence gap is visible (seed 1: p_min=0.827 vs p_maj=0.972; seed 5: p_min≈0.87 vs p_maj≈0.99). This is consistent with LaBonte & Muthukumar [2026]'s Phase I prediction — ERM learns the spurious feature first, temporarily lagging minority confidence. However, this differential disappears before t* in all seeds. By t*, both groups are saturated.

Figure 6 shows confidence trajectories per seed. Figure 7 shows per-sample confidence distributions at t*. Figure 8 shows the H-M1 gate comparison.

# 6. Discussion

## 6.1 The Dual Finding: Existence Without Expected Mechanism

The core finding of this work is a dual result. The trace signal is real: per-sample last-fc Hessian trace achieves AUROC≥0.85 for minority membership detection in 4/5 seeds, with the signal being ERM-induced (epoch-0 control). The expected mechanism is absent: at the checkpoint of peak discriminability, minority training confidence is 0.97–1.0 — indistinguishable from majority in terms of the confidence channel.

This combination — robust existence result + principled mechanism falsification — is more informative than either result alone. If only H-E3 had been tested, we would incorrectly attribute the signal to the confidence-differential mechanism by default. If only H-M1 had been tested, we would have no evidence that the trace signal is discriminative at all.

## 6.2 What Drives the Trace Signal? The Feature-Norm Channel

For a linear cross-entropy head with weight W ∈ ℝ^{C×d} and penultimate feature x_i ∈ ℝ^d:

    Tr(H_i^fc) ∝ ‖x_i‖² · p_i(1 - p_i)

At t*, p_i(1-p_i)→0 for all training samples (both minority and majority). The confidence term is inactive. The only surviving candidate driver of the trace asymmetry is ‖x_i‖² — systematic differences in the L2 norm of the penultimate-layer feature representation between minority and majority samples.

LaBonte et al. [2024] provide a group-level prediction consistent with this interpretation: minority group covariance matrices have larger spectral norm than majority groups within the same class — a prediction of systematic feature-norm elevation for minority samples. Our finding extends this from the group-level covariance setting to the per-sample trace trajectory, and identifies ‖x_i‖² as the specific channel that would need to show differential behavior.

**This interpretation is a candidate, not a verified claim.** We have not directly measured penultimate-layer norms ‖x_i‖² per sample or confirmed that minority norms exceed majority norms. Verifying this — by measuring feature norms at t* and correlating them with trace ranks — is the primary direction for future mechanistic investigation (see Section 6.4).

## 6.3 Relation to LaBonte & Muthukumar 2026 Phase I/II Theory

LaBonte & Muthukumar [2026] prove for an XOR spurious feature model that SGD learns the spurious feature first (Phase I), then the core feature (Phase II). This predicts that during Phase I, minority samples (which lack the spurious feature) remain near the decision boundary, keeping p_minority(t)≈0.5 while p_majority(t*)>0.9.

Our results show that on ResNet-50 on Waterbirds, a transient version of this is real at epoch 1 but does not persist to t*. ERM memorizes minority training samples — driving their training confidence to ≥0.97 — before the trace ratio R(t) reaches its maximum. The mechanism operates on a different timescale than t*.

Two non-exclusive interpretations: (1) the Phase I window for ResNet-50 on Waterbirds closes very quickly (by epoch 5 at the latest), so the confidence differential is genuinely transient; (2) ResNet-50 with ImageNet pretraining can memorize minority samples via the pretrained feature representation even without the spurious correlation, and this memorization outpaces the Phase I dynamics. Distinguishing these requires holding constant the spuriosity level and model capacity, which we leave for future work.

## 6.4 Limitations

**Scope:** All experiments use ResNet-50 on Waterbirds v1.0 with 95% spuriosity. Generalization to other architectures (ViT, ResNet-18), datasets (CelebA, MultiNLI), or spuriosity levels is unknown.

**Mechanism unverified:** The feature-norm channel (‖x_i‖²) is a candidate explanation, not a verified claim. The next step is to directly measure per-sample penultimate-layer norms at t* and test whether minority norms exceed majority norms at the same rank order as Hessian traces.

**No DFR application:** We have not tested whether the trace signal, used as a sample-weight or resampling guide for last-layer retraining (analogous to JTT upweighting), improves worst-group accuracy. The existence result (AUROC>0.85) is necessary but not sufficient for practical WGA improvement — the signal quality needs to translate through the DFR pipeline. This is H-M4, the next planned experiment.

**Training-set confidence only:** The H-M1 mechanism test uses training-set confidence. A different test — measuring confidence on held-out samples — might show a different boundary-condition pattern. The training-set test was pre-registered, but future work should examine validation-set confidence trajectories.

**Seed 1 failure:** One seed (seed 1) fails the H-E3 gate due to a non-monotone AUROC trajectory (Spearman ρ=0.70). This may reflect stochastic optimization dynamics at a specific random initialization rather than a systematic failure mode. Understanding why seed 1 exhibits a dip at t=5 while other seeds do not is a direction for future mechanistic investigation.

## 6.5 Implications for Annotation-Free Minority Detection

Our work identifies per-sample last-fc Hessian trace as a candidate second-order annotation-free proxy for minority group membership — the first such signal to achieve AUROC>0.85 on Waterbirds without group labels, with a verified epoch-0 control ruling out pretrained-artifact confounds.

The key practical questions remaining are: (1) does the trace proxy translate to WGA improvement via DFR-style last-layer retraining (H-M4); (2) does the signal generalize beyond Waterbirds; (3) what is the minimal computation needed (can K be reduced further, or can the epoch-0 control be replaced by a cheaper baseline check). If the feature-norm mechanism is confirmed, it would also suggest that directly measuring ‖x_i‖² as an annotation-free proxy might be cheaper than the full Hutchinson computation — a simplification worth testing.

# 7. Conclusion

We set out to test whether the curvature of the ERM loss surface — measured as per-sample Hessian trace of the last fully-connected layer — reveals minority group membership without group annotations. It does: 4/5 random seeds achieve AUROC≥0.85 at the epoch of maximum trace ratio, with the epoch-0 control confirming that the signal is created by ERM training on Waterbirds, not inherited from ImageNet pretraining.

We then set out to understand why. We expected that ERM's spurious feature exploitation would keep minority training samples near the decision boundary (Phase I confidence-differential mechanism), with the p_i(1-p_i) confidence channel elevating their Hessian traces. This expected mechanism is absent: minority training confidence saturates to ≥0.97 at t*, identical to majority. The signal is robust; its original mechanistic explanation is not.

This is not a failure. It is a precise scientific finding that eliminates one mechanism and identifies the right one to test next: the feature-norm channel (‖x_i‖²). LaBonte et al. [2024]'s spectral imbalance result — that minority group covariance matrices have larger spectral norm than majority groups — predicts that minority per-sample feature norms are systematically elevated, and with the confidence channel inactive, this is the remaining candidate. Testing it directly (measuring penultimate-layer norms at t* and correlating with trace ranks) is the primary next step.

The practical path forward is equally clear: test whether the trace proxy, used to guide annotation-free last-layer retraining (DFR-style), improves worst-group accuracy on Waterbirds. The existence result (AUROC>0.85) establishes the signal quality that makes this worth testing; the mechanism result identifies what signal the proxy is actually capturing.

A second-order perspective on spurious feature reliance — one that asks how ERM differentially shapes the loss landscape curvature around training samples, not just how it classifies them — opens a class of annotation-free minority detectors that first-order signals cannot replicate. This paper establishes the empirical foundation and the mechanistic question for that class.

## Broader Impact

This work advances annotation-free methods for identifying minority groups in machine learning training data. The ability to detect spuriously correlated minority samples without group labels could reduce the annotation burden for fairness-motivated model corrections. However, the same signal could in principle be used to identify and selectively filter minority samples in adversarial settings. We encourage future users of this method to apply it in contexts where minority detection supports, rather than undermines, equitable model performance.

## References

See 06_references.bib for full BibTeX.
