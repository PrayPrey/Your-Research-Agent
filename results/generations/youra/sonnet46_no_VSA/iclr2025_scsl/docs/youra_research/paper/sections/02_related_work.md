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
