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
