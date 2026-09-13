# Experimental Setup

We test temporal ordering (P1), layer-wise mechanism (h-m1), forgetting stability (h-e2), and gradient-aware intervention (h-c1) through controlled ablation experiments on CMNIST benchmark. Multi-dataset validation (Waterbirds, CelebA, NICO++) is planned future work due to manual setup requirements.

## Datasets

**CMNIST (Colored MNIST):** Canonical spurious correlation benchmark with controlled color-label bias. Training set: 60,000 images, color biased with label (75% correlation—digit 0 → red, digit 1 → green). Test set: 10,000 images with reversed bias (25% correlation) to measure worst-group accuracy. Spurious feature: digit color (low-level visual). Core feature: digit shape (edges, stroke patterns).

**Preprocessing:** Resize to 224×224 for ResNet compatibility, normalize to ImageNet statistics. Ablation variants: (1) Spurious-only—Gaussian blur σ=3 removes shape edges, preserves color. (2) Core-only—grayscale conversion removes color, preserves shape. (3) Baseline—original colored sharp digits.

**Why CMNIST:** Ablation training cleanly separates color from shape (blur destroys edges, grayscale removes color). Global color corruption tests convergence measurement without spatial attribution ambiguity (unlike Waterbirds where background is spatially localized, requiring segmentation masks).

## Models and Training

**Architecture:** ResNet-18 (pretrained ImageNet weights), final FC layer replaced with 10-class classification head. Total parameters: 11.2M.

**Optimizer:** SGD with momentum 0.9, learning rate 0.01 (constant for PoC, no schedule), weight decay $10^{-4}$, batch size 256.

**Training:** 30 epochs per variant (spurious-only, core-only, baseline) to observe post-convergence behavior. Convergence tracked via per-epoch gradient norm (L2 norm of all parameter gradients, averaged over epoch). Convergence criterion: gradient norm < 10% of peak for 3 consecutive epochs.

**Statistical validation:** 10 random seeds (seeds 0-9) per experiment for paired t-tests. PoC results (reported below) use seed 0 only; full 10-seed validation launched but not completed by paper submission deadline.

## Experimental Questions

**Q1 (h-e1):** Do spurious features converge ≥2 epochs earlier than core features?  
**Method:** Train spurious-only, core-only, baseline variants on CMNIST. Measure $E_s$, $E_c$ (convergence epochs), compute temporal gap $\Delta = E_c - E_s$.  
**Success:** $\Delta \geq 2$ epochs, $p < 0.05$ via paired t-test across 10 seeds.

**Q2 (h-m1):** Is temporal gap driven by layer-wise feature hierarchy?  
**Method:** Compute neuron-spurious correlation $\rho_j$ per neuron from ablation training activations. Aggregate by layer, test early > late layers.  
**Success:** $\bar{\rho}_{\text{early}} > \bar{\rho}_{\text{late}}$, $p < 0.05$ via independent t-test.

**Q3 (h-e2):** Do spurious features exhibit lower forgetting rate?  
**Method:** Track prediction flips per training example across 30 epochs. Compute forgetting rate $F$ (events/sample) for spurious-only vs core-only.  
**Success:** $F_{\text{spurious}} < F_{\text{core}}$, $p < 0.05$ via paired t-test.

**Q4 (h-c1):** Can gradient-aware training match JTT worst-group accuracy?  
**Method:** Use CMNIST $\rho_j$ values to modulate per-neuron learning rates ($\text{lr}_j = \text{lr}_{\text{base}} \times (1 - \rho_j)$) on Waterbirds. Compare worst-group accuracy to JTT baseline (86%).  
**Success:** WG-Acc $\geq 86\% - 1\% = 85\%$ (competitive with JTT).

## Baselines

**ERM (Empirical Risk Minimization):** Standard training without debiasing. Expected worst-group accuracy ~40% on Waterbirds, ~60% on CMNIST.

**JTT (Just Train Twice):** State-of-the-art reweighting method. Train biased ERM model for $T_{\text{up}}$ epochs, identify hard examples (those ERM misclassifies), retrain with hard examples upweighted $\lambda_{\text{up}}=10\times$. Expected worst-group accuracy ~86% on Waterbirds (from Nam et al. 2020).

**Layer-wise Regularization:** Falsification baseline for h-c1. Apply stronger weight decay to early layers, weaker to late layers (opposite of gradient-aware modulation). Tests whether h-c1 improvement comes from feature-specific modulation vs generic early-layer regularization.

## Evaluation Metrics

**Temporal gap $\Delta$:** $E_c - E_s$ in epochs. Primary metric for P1 (h-e1).

**Layer-wise $\rho_j$ gradient:** Mean neuron-spurious correlation difference between early (conv1, layer1) and late (layer3, layer4) layers. Mechanism validation for h-m1.

**Forgetting rate $F$:** Average forgetting events per training example. Stability metric for h-e2.

**Worst-group accuracy (WG-Acc):** Accuracy on minority group (lowest of 4 groups: spurious-aligned majority, spurious-aligned minority, spurious-misaligned majority, spurious-misaligned minority). Intervention metric for h-c1. Standard fairness metric for spurious correlation benchmarks.

## Computational Resources

**Hardware:** NVIDIA A100 40GB GPUs (10 GPUs for parallel seed execution).

**Wallclock time:** CMNIST PoC (3 variants × 30 epochs × 1 seed) = 6 hours. Full 10-seed validation = 60 hours parallelized to 6 hours across 10 GPUs.

**Storage:** Gradient norms + activations + forgetting logs = ~500MB per seed × 10 seeds = 5GB total.
