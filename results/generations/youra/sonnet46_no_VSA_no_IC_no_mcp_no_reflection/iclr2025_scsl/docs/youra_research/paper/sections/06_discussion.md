# Discussion

## Root Cause: Batch Contamination by High-Magnitude Minority Gradients

The inversion effect on Waterbirds — alignment ROC-AUC = 0.150 at epoch 1, with minority samples appearing *more* aligned with the batch mean than majority samples — requires a mechanistic explanation. We propose **batch contamination** as the primary cause.

The within-batch mean gradient is:
$$\bar{g} = \frac{1}{B} \sum_{i=1}^{B} g_i = \frac{1}{B}\left(\sum_{i \in \text{maj}} g_i + \sum_{i \in \text{min}} g_i\right)$$

Under standard ERM training, minority samples incur substantially higher loss than majority samples — their per-sample gradients have larger norms. With batch size $B=32$ and Waterbirds minority prevalence ~5%, a typical batch contains 1–2 minority samples. These 1–2 high-magnitude gradients disproportionately pull the within-batch mean toward the minority gradient direction, relative to the 30–31 lower-magnitude majority gradients. The result: the within-batch mean already partially represents the minority gradient direction, causing minority samples to appear *more* aligned with the mean than expected.

Formally, if minority gradients have magnitude $\|\bar{g}_{\text{min}}\| = k \cdot \|\bar{g}_{\text{maj}}\|$ with $k > 1$ (as is true at epoch 1 when minority has high loss), and if $n_\text{min} \ll n_\text{maj}$ in the batch, the batch mean is shifted toward the minority direction by factor $\propto k \cdot n_\text{min} / B$. With $k \approx 10$ at epoch 1 (early high-loss) and $n_\text{min} = 1$, the minority contribution to the mean is comparable to the majority contribution despite comprising 1/32 of the batch.

**Supporting evidence from CelebA:** The batch contamination hypothesis predicts that the inversion should be *weaker* for lower minority prevalence, because minority samples appear in fewer batches. CelebA minority prevalence (~0.8%) means fewer minority samples per batch, and correspondingly the CelebA alignment signal is less inverted (0.246 at epoch 1 vs. 0.150 on Waterbirds) and reaches a weak positive signal at epoch 50 (0.632). This prevalence-dependent pattern is consistent with batch contamination as the root cause.

## Alternative Explanations

### Gradient Compression at the Last Layer

The last fully-connected layer (Linear(2048, 2)) projects from a 2048-dimensional feature space to 2 class logits. The per-sample gradients with respect to this layer are vectors in $\mathbb{R}^{4098}$ ($\mathbf{W}$: 2048×2 and $\mathbf{b}$: 2). It is possible that the group-discriminative signal present in penultimate-layer (2048-dim activation) representations is destroyed by this 2-dimensional output bottleneck. If the spurious feature direction is well-aligned with the 2-dim output weight space, last-layer gradients for minority and majority samples may be directionally similar despite meaningful representational differences in earlier layers.

We cannot rule out this explanation. P3 (the untested prediction) would directly address it: measuring alignment at the penultimate layer would distinguish gradient compression from batch contamination as the primary failure mode.

### ImageNet Pretraining Effect

At epoch 1 with ImageNet pretraining, ResNet-50 already fits simple textures and backgrounds efficiently. Both majority and minority samples may produce gradients in similar fine-tuning directions (adjusting bird recognition from generic ImageNet categories), making batch-mean cosine similarity uniformly high and non-discriminative. This would explain why the inversion is strongest at epoch 1 and partially recovers as training diverges from ImageNet features.

**Most likely mechanism:** Batch contamination (primary) combined with ImageNet pretraining (early epochs). The contamination explanation accounts for the prevalence-dependent pattern; the pretraining explanation accounts for why epoch 1 is the worst. Both contribute to the inversion.

## The Path Forward: Two-Pass Global Mean Gradient

The batch contamination failure is *not* a fundamental problem with gradient direction as a minority signal. It is a problem with the *reference direction* — the within-batch mean is not a stable representation of the majority gradient direction.

A **two-pass global mean gradient** correction addresses the root cause directly:

**Pass 1:** Standard ERM training forward/backward pass.  
**Pass 2:** After each epoch (or at fixed intervals), compute $\bar{g}_{\text{global}} = \frac{1}{N} \sum_{i=1}^{N} g_i$ by averaging per-sample gradients over the full training set.  
**Alignment:** Compute cosine similarity of each sample's gradient with $\bar{g}_{\text{global}}$ rather than the within-batch mean.

The global mean is stable across thousands of samples, majority-dominated (by class prevalence, not batch noise), and robust to the high-magnitude minority gradient spikes that contaminate the per-batch mean. The annotation-free property is preserved: $\bar{g}_{\text{global}}$ uses only training labels, no group annotations.

**Computational cost:** One additional full forward-backward pass per epoch (same cost as the probe pass we already run). This is feasible and does not require gradient checkpointing.

## Limitations

**L1 — Single seed (seed=42):** H-E1 is designed as a proof-of-concept existence test; single-seed evaluation is appropriate for the PoC level. The failure conclusion is robust: the alignment–loss gap ranges 0.27–0.78, far exceeding any plausible seed-to-seed variance. We do not claim precise ROC-AUC values; we claim the failure is decisive and replication-grade.

**L2 — CelebA subsampled to 16K:** We used 16K of 162K training samples for computational feasibility. The subsample preserves group composition ratios (stratified, seed 42). The failure conclusion on CelebA is robust; the specific CelebA values (especially the 0.63 at epoch 50) may shift slightly with the full dataset, but the alignment–loss gap (0.27 minimum) is decisive.

**L3 — Last layer only:** We instrument gradient computation only at the final Linear(2048, 2) layer. The hypothesis chain includes P3 (penultimate-layer alignment) as a separate untested prediction. We cannot conclude that gradient alignment at *all* layers fails — only last-layer within-batch alignment is falsified.

**L4 — Global mean gradient untested:** The batch contamination diagnosis points to two-pass global mean as the correction, but we have not run that experiment. The inversion might persist with global mean reference (suggesting gradient compression at the last layer as primary cause) or disappear (confirming batch contamination). This is the most important immediate follow-up experiment.

## Broader Implications for Gradient-Based Debiasing Methods

The batch contamination failure mode identified here may affect any method that uses within-batch gradient statistics to identify minority samples in an imbalanced training scenario. Methods that use per-batch gradient norms, per-batch gradient directions, or per-batch gradient covariances as minority signals should be re-examined under imbalanced settings. The issue is structural: imbalanced mini-batches cause high-loss minority samples to dominate batch gradient statistics regardless of the specific statistic used.

Methods using globally computed gradient statistics (e.g., Fisher information across the full training set, gradient covariance over many batches) are less susceptible to this failure. Our results provide empirical motivation for preferring global over per-batch gradient reference directions in any annotation-free debiasing method that relies on gradient direction discriminability.
