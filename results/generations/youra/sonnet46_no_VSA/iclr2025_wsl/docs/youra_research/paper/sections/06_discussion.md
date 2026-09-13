# Discussion

## 6.1 Key Findings

Our results confirm three of the four predictions in the causal chain and surface an unexpected entanglement phenomenon that opens new questions about weight-space representation geometry.

**Finding 1: Architectural invariance produces machine-precision zero OrbitVar.** DeepSets achieves OrbitVar = 1.002e-14, not merely small but at the precision floor of float32 arithmetic. This is not a quantitative improvement over CISE — it is a qualitative regime change. Once OrbitVar is at machine precision, there is no residual symmetry violation for downstream predictors to compensate for; the encoder's output is *definitionally* the same for all functionally equivalent models.

The 5.1 OOM gap for NFN (8.905e-08) is less decisive — non-negligible within float32 precision, though far below CISE. This suggests that NFN's HNPPool aggregation introduces small but real imprecision from spatial interaction terms in the CNN permutation group. Whether this residual variance matters for downstream prediction is a direct target for follow-up work.

**Finding 2: CISE's non-invariance is not a noise problem — it is a signal problem.** MSE_perm/MSE_total = 3.35 reveals that CISE's permutation sensitivity does not add small noise on top of a clean signal; it contributes error larger than the total prediction error budget. The R²(C1_avg) = −1.63 result is the clearest demonstration: channel-position information is not a minor artifact that averaging can remove — it is a primary predictive feature in CISE embeddings, and removing it by averaging destroys the predictor entirely.

**Finding 3: The entanglement result is a new empirical finding, not a failure.** The additive closure criterion (ΔMSE ≈ MSE_perm^C1 ± 10%) was pre-registered as the quantitative test of the causal mechanism. It fails decisively (closure = 0.872). This is an honest result, and we present it as such. But the closure failure is *informative*: it tells us that MSE_perm and MSE_res in CISE embedding space are not orthogonal components — they are correlated through LightGBM's non-linear feature interactions.

The most likely mechanism is as follows: LightGBM, trained on CISE embeddings, implicitly learns to suppress the most permutation-sensitive embedding dimensions in favor of more stable ones. This implicit compensation reduces effective MSE_perm at training time below its naive (all-dimensions-equal) estimate. Simultaneously, this non-linear suppression changes MSE_res — the residual error after accounting for permutation sensitivity — because the predictor is no longer using an optimal linear combination of all features. When C2 removes channel-position encoding entirely, LightGBM faces a different geometric landscape and re-optimizes, changing MSE_res in a direction that partially offsets the MSE_perm elimination.

This interpretation predicts that simpler predictors (e.g., linear regression, where no implicit suppression is possible) would show less entanglement. The h-m3 linear head ablation result (Ridge R²(C2) = −6.42) rules out linear heads as a viable comparison — the embedding is not linearly separable — but an MLP predictor (non-linear but less expressive than LightGBM) would be a more controlled test.

## 6.2 Limitations

**Additive closure not achieved (closure = 0.872).** The pre-registered quantitative prediction — that eliminating MSE_perm would reduce total MSE by approximately MSE_perm^C1 — fails empirically. While the direction of effect is confirmed, the magnitude is not predictable from MSE_perm alone. Future work should establish whether the additive assumption can be recovered under specific conditions (matched predictor capacity, orthogonalized embedding spaces) or whether entanglement is a general feature of non-linear predictors on non-invariant encodings.

**NFN downstream comparison unavailable.** NFN achieves near-invariance (OrbitVar = 8.905e-08) at the representational level, but downstream R² comparison against DeepSets is limited by library installation failure. NFN Kendall's τ = 0.934 on generalization prediction (from Zhou et al. [2023]) uses a different evaluation protocol and cannot be directly compared to our R² results. This comparison is the primary open empirical question from our work.

**Single dataset and architecture.** All experiments use ModelZooDataset CIFAR10-GS: 100 CNNs with a fixed 3-layer structure (S₈ × S₆ × S₄ permutation group). Generalization to wider networks (ResNets, ViTs), larger model zoos, or different prediction tasks requires separate experiments. The MSE decomposition diagnostic is theoretically architecture-agnostic and should transfer, but the specific magnitude of OrbitVar and MSE_perm will depend on the dataset and architecture.

**R² reference point sensitivity.** Unterthiner et al. [2020] report R²(C0) = 0.984 from 5-fold training CV on the full dataset; our testset evaluation yields R²(C0) = 0.731. Matched evaluation protocol (using the same 5-fold CV setup) would enable direct comparison with the published baseline. We report testset R² throughout for consistency and supplement with Kendall's τ, which is less sensitive to evaluation protocol differences.

## 6.3 Broader Impact

This work establishes that weight-space encoders must be evaluated not only on downstream performance but on their permutation sensitivity (OrbitVar) and its propagation to prediction error (MSE_perm). We introduce the MSE bias-variance decomposition over permutation orbits as a reusable diagnostic that can be computed for any encoder-predictor pair with access to functional permutations.

For practitioners building model zoo applications — performance prediction, model selection, hyperparameter transfer — the practical recommendation is clear: architectural invariance (DeepSets sum pooling) provides a +6.4pp R² improvement at zero additional training cost over CISE, and eliminates the fundamental incompatibility between non-invariant encoding and the permutation symmetries of neural network weights.

We do not anticipate negative societal impacts from this work. The methodology — measuring weight-space encoder quality — is a tool for improving the reliability of model zoo analysis. It does not enable new capabilities for harmful applications.
