# Results

## Primary Finding: Alignment Signal Fails on Both Datasets

Within-batch gradient alignment achieves lower ROC-AUC than per-sample loss at every checkpoint epoch on both Waterbirds and CelebA. The existence test (H-E1) fails decisively. Table 1 presents the complete results.

**Table 1:** Gradient alignment ROC-AUC vs. per-sample loss ROC-AUC at checkpoint epochs on Waterbirds and CelebA. Higher ROC-AUC indicates better spurious-minority detection.

| Epoch | WB: alignment | WB: loss | WB: gap | CelebA: alignment | CelebA: loss | CelebA: gap |
|-------|--------------|----------|---------|-------------------|--------------|-------------|
| 1     | 0.150        | 0.930    | -0.780  | 0.246             | 0.975        | -0.729      |
| 5     | 0.301        | 0.854    | -0.554  | 0.484             | 0.949        | -0.465      |
| 10    | 0.340        | 0.821    | -0.481  | 0.523             | 0.939        | -0.416      |
| 25    | 0.340        | 0.801    | -0.461  | 0.407             | 0.910        | -0.503      |
| 50    | 0.349        | 0.775    | -0.426  | 0.632             | 0.905        | -0.273      |

*Figure 1 (roc\_auc\_vs\_epoch.png): ROC-AUC vs. training epoch for gradient alignment (blue) and per-sample loss (orange) on both datasets. Figure 2 (roc\_auc\_vs\_epoch\_waterbirds.png): Waterbirds detail. Figure 3 (roc\_auc\_vs\_epoch\_celeba.png): CelebA detail.*

## The Alignment Inversion Effect on Waterbirds

The most striking finding is at epoch 1 on Waterbirds: alignment ROC-AUC = **0.150**, substantially below chance (0.5). This is not merely a weak signal — it is an *inverted* signal. An alignment ROC-AUC of 0.15 means that for a randomly chosen minority–majority pair, the alignment score correctly identifies the minority sample only 15% of the time — worse than random assignment.

Equivalently, the raw (un-negated) cosine similarity of spurious-minority samples with the within-batch mean gradient is *higher* than that of majority samples (cosine similarity ROC-AUC ≈ 0.85). Spurious-minority samples appear **more aligned** with the batch mean gradient than majority samples — the direct opposite of the hypothesis.

The inversion is most extreme at epoch 1 (alignment ROC-AUC = 0.150) and partially recovers by epoch 50 (0.349), but alignment never approaches 0.5 on Waterbirds at any tested epoch. The gap between alignment and loss remains substantial throughout training (0.43–0.78).

**Why this matters:** The inversion is not consistent with a "gradient signal is too weak" failure — it reveals an active mechanism pushing the signal in the wrong direction. This is the primary empirical finding of the paper.

## Temporal Dynamics: Per-Sample Loss Degrades, Alignment Slowly Improves

On Waterbirds, per-sample loss ROC-AUC begins very high (0.930 at epoch 1) and monotonically degrades to 0.775 at epoch 50, as the model memorizes training samples and loss differences between minority and majority samples compress. This is consistent with JTT's observation that early-epoch ERM loss is the best minority proxy [Liu et al., 2021].

Gradient alignment on Waterbirds shows the opposite trend: it begins inverted (0.150) and slowly improves toward 0.35, but never exceeds loss. The two signals are on converging trajectories at epoch 50 — not because alignment improves to useful levels, but because loss degrades. Neither signal is useful at epoch 50.

**Interpretation:** The convergence pattern is consistent with the gradient collapse hypothesis: as training loss approaches near-zero (Waterbirds train loss → 0.0003 by epoch 50), all per-sample gradients collapse toward near-zero and become increasingly collinear. Both alignment discrimination and loss discrimination collapse, with loss starting from a much higher baseline.

## CelebA: Weak Positive Signal at Late Epochs

On CelebA, the alignment signal behaves differently: it begins inverted (0.246 at epoch 1), recovers through epoch 10 (0.523), dips at epoch 25 (0.407), then reaches its maximum at epoch 50 (0.632). This is a *weak positive* signal at late epochs — above chance, but still 0.27 below loss ROC-AUC (0.905).

**Why CelebA differs from Waterbirds:** The key distinction is minority prevalence. On CelebA, the spurious minority (blond male) comprises ~0.8% of training samples — far rarer than Waterbirds (~5% or ~18% depending on definition). With such extreme rarity, minority samples appear in fewer batches and with less frequency per batch. The batch contamination effect — minority gradient magnitude dominating the within-batch mean — is proportionally reduced, allowing a weak positive directional signal to emerge at late epochs.

This prevalence-dependent recovery is consistent with the batch contamination hypothesis: the contamination is a function of minority sample gradient magnitude relative to batch size and minority frequency. At 0.8% prevalence with B=32, expected minority samples per batch is 0.26 (minority appears in ~26% of batches), compared to Waterbirds where minority appears in nearly every batch.

*Figure 3 (roc\_auc\_vs\_epoch\_celeba.png): The non-monotonic CelebA alignment trajectory (rise → dip at epoch 25 → peak at epoch 50) reflects competing dynamics between gradient magnitude growth and batch contamination reduction as training progresses.*

## Score Distribution Analysis

At epoch 5, the alignment score distributions for minority and majority groups overlap substantially on both datasets (Figures 4–5, appendix). On Waterbirds, the minority distribution is shifted *toward higher cosine similarity* with the batch mean (confirming the inversion: minority appears more aligned, not less). On CelebA at epoch 5, distributions are near-identical with no useful separation.

The loss score distributions show clean separation at epoch 5 on both datasets: minority samples have noticeably higher loss, consistent with their higher loss ROC-AUC.

## ROC Curves at Best Alignment Epoch

Figures 6–7 (appendix) show full ROC curves at the epoch where alignment ROC-AUC is maximized for each dataset (epoch 50 for both). The alignment ROC curves are close to the diagonal (near-random discrimination), while loss ROC curves show substantial area above the diagonal. These curves confirm that at no operating point does gradient alignment provide useful minority detection — the failure is not threshold-sensitive.

## Summary of Evidence

The evidence consistently supports a single conclusion: **within-batch gradient cosine similarity with the per-batch mean gradient is not a viable spurious-minority detector under standard ERM training on Waterbirds or CelebA.** The failure is not marginal — the gap to per-sample loss ranges from 0.27 to 0.78 across all tested conditions. The inversion effect on Waterbirds at early epochs indicates an active mechanism (not merely noise) responsible for the failure, pointing to the batch contamination diagnosis explored in Section 6.
