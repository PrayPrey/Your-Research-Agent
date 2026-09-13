# Introduction

Consider the following experiment. Take a trained neural network and record its predicted test accuracy using a weight encoder. Now permute the neurons of a hidden layer — shuffle which neuron is labeled "channel 3", "channel 7", and so on — adjusting adjacent layers accordingly so the network computes exactly the same function. Re-encode and predict again. If you repeat this across K=50 such functionally equivalent rearrangements and average the predictions, what do you get?

For a correctly designed encoder, you should get the same prediction each time — the average should match any individual prediction. For CISE, a sinusoidal positional encoder widely used in weight-space learning, you get R² = −1.63. Averaging predictions over functionally equivalent networks produces accuracy *worse than predicting the mean* — a result that lands 2.63 R² units below the trivial baseline.

This is not a failure of robustness under noise. It is a precise measurement of a fundamental flaw: CISE encodes which channel occupies which position as a predictive signal. But channel positions in a neural network are arbitrary labels. Two networks with identical function can differ only in which neuron happens to be labeled "channel 3". An encoder that treats these networks as different is not modeling what a network *computes* — it is modeling an arbitrary administrative choice made during initialization.

The question this paper addresses is: does *architectural* permutation-invariance — building the encoder so that permuted inputs produce identical outputs by construction — causally improve model zoo performance prediction? And if so, *how* does it improve? Through what mechanism does the representational property (invariant encoder outputs) translate into the predictive property (lower prediction error)?

## The Weight-Space Symmetry Problem

Neural networks have a well-known symmetry: for networks with permutation-symmetric activation functions, permuting the neurons of a hidden layer and correspondingly adjusting adjacent layers produces a functionally identical network [Hecht-Nielsen, 1990]. This means the space of weight configurations is partitioned into *orbits* — equivalence classes under permutation — and any two configurations in the same orbit correspond to the same function.

Weight-space learning approaches — which train predictors directly on network weights — must therefore contend with this symmetry. A predictor trained on one configuration may encounter a functionally identical configuration with different raw weights, and if the encoder does not recognize these as equivalent, the predictor sees two different inputs that should produce the same output.

Prior work has attacked this problem from several angles. DeepSets [Zaheer et al., 2017] provides a theoretical foundation: any permutation-invariant function on sets can be decomposed as ρ(Σφ(xᵢ)), establishing sum pooling as the canonical architecture for invariant encoding. Neural Functional Networks (NFN) [Zhou et al., 2023] extend this to equivariant mappings over weight spaces, achieving strong Kendall's τ on generalization prediction tasks. DWSNet [Navon et al., 2023] derives the complete set of affine equivariant and invariant linear layers for weight spaces, formalizing the correct symmetry group — *coupled* row-column permutations across adjacent layers, not independent per-layer permutations.

Yet despite this theoretical progress, a critical empirical gap remains: no prior work has directly measured (1) how much non-invariant encoders vary in their representations of functionally equivalent networks (*OrbitVar*), (2) how much this representational variance propagates to prediction-space variance (*MSE_perm*), and (3) whether architectural invariance causally closes this gap in downstream prediction quality. The field has strong theoretical reasons to prefer invariant encoders, but no empirical closure of the causal chain.

## Our Approach: Measuring the Causal Chain

We address this gap with a three-step experimental design that directly measures each link in the causal chain:

**Step 1 — Architecture determines OrbitVar.** We measure within-orbit representational variance (OrbitVar = E_v[Var_π(encoder(π·v))]) for four encoders spanning the invariance spectrum: per-layer statistics (approximately invariant, C0), CISE sinusoidal PE (non-invariant, C1), DeepSets sum pooling (exactly invariant, C2), and NFN equivariant layers (near-invariant, C3), all on ModelZooDataset CIFAR10-GS [Unterthiner et al., 2020].

**Step 2 — OrbitVar propagates to prediction variance.** We apply the MSE bias-variance decomposition over permutation orbits — E[(y-ŷ)²] = MSE_res + MSE_perm — to directly measure how much of CISE's total prediction error is attributable to permutation-induced variance, and whether LightGBM trained on CISE embeddings can implicitly compensate.

**Step 3 — Eliminating MSE_perm improves R².** We compare LightGBM predictors trained on each encoder's embeddings, with DeepSets' zero MSE_perm as the treatment and CISE's high MSE_perm as the control.

This measurement framework allows us to go beyond the question of "does invariant encoding improve R²?" to ask "through exactly what mechanism, and by how much?"

## Contributions

This paper makes four contributions:

**1. First joint measurement of OrbitVar, MSE_perm, and R²** across the full invariance spectrum on ModelZooDataset CIFAR10-GS. DeepSets achieves OrbitVar = 1.002e-14 (machine precision), NFN achieves 8.905e-08, and CISE achieves 0.010333 — a gap of 5 to 12 orders of magnitude confirmed across 100 models with Wilcoxon p = 1.95e-18.

**2. A novel MSE bias-variance decomposition over permutation orbits** as a diagnostic tool for weight-space learning. For CISE, MSE_perm/MSE_total = 3.35 — permutation-induced variance contributes *more than 3× the total prediction error*, as confirmed by the orbit-averaged diagnostic R²(C1_avg) = −1.63.

**3. An empirical entanglement finding:** the additive decomposition MSE = MSE_res + MSE_perm assumes orthogonality — empirically violated (closure = 0.872). MSE_perm and MSE_res are entangled in CISE embedding space, revealing that LightGBM partially compensates for permutation sensitivity through non-linear feature interactions. This compensation changes both components simultaneously, opening a new line of inquiry into weight-space representation geometry.

**4. A practical encoder design result:** DeepSets doubly-invariant encoding achieves R² = 0.9148 on ModelZooDataset CIFAR10-GS, a +6.4 percentage-point improvement over CISE (R² = 0.851), with zero additional training supervision.

The remainder of the paper is organized as follows. Section 2 reviews weight-space learning and permutation-invariant encoding. Section 3 describes our measurement framework and encoder implementations. Section 4 presents the experimental setup. Section 5 reports results for each step of the causal chain. Section 6 discusses the entanglement finding and limitations. Section 7 concludes.
