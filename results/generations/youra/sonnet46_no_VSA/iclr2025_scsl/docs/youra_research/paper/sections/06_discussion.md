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
