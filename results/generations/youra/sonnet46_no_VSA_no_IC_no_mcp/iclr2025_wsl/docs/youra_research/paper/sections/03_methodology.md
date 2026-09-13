# Methodology

Our methodology is organized around four interconnected experimental questions, each with a distinct measurement protocol. The central design principle is **oracle orbit construction**: rather than inferring symmetry structure from natural variation in the zoo, we directly construct ground-truth functional equivalents by applying explicit symmetry transforms. This provides controlled probes unavailable from zoo statistics alone.

## 3.1 Setting and Data

**Model Zoo.** We use the Schürholt MNIST model zoo [Schürholt et al., 2022], a collection of 2-layer MLPs trained on MNIST with architecture 784→64→10 (ReLU activations, no bias in the final layer). Models vary in learning rate, weight decay, and random initialization seed. We use a locally archived subset of N=500 models with ground-truth property labels: test accuracy, generalization gap (train − test accuracy), and learning rate recovery. Weights are stored as flat tensors of dimension D=51,850 (784×64 + 64×10).

**Why this zoo.** The M=2 architecture makes scaling and sign-flip canonicalization well-defined: for a single hidden layer with h=64 neurons, scaling orbits have dimension 64 (one free scale per neuron), and sign-flip orbits have discrete order 2^64. The majority-sign algorithm for sign-flip canonicalization is unambiguous in theory for M=2 (only one consecutive layer pair exists). As we show, this theoretical unambiguity does not hold in practice for even d_in — a structural finding of independent interest.

## 3.2 Symmetry Orbit Construction

**Scaling orbits.** For a 2-layer ReLU MLP with weight matrices W₁ ∈ ℝ^{d_in × h} and W₂ ∈ ℝ^{h × d_out}, the scaling symmetry transform applies per-neuron positive rescaling:

$$W_1[:, i] \leftarrow \alpha_i W_1[:, i], \quad W_2[i, :] \leftarrow W_2[i, :] / \alpha_i$$

for any α_i > 0. The resulting network computes the same function as the original for any input (ReLU preserves sign under positive scaling). We sample scaling factors log-uniformly: log α_i ~ Uniform(log 0.1, log 10), covering a 100× dynamic range per neuron.

**Sign-flip orbits.** The sign-flip symmetry transform applies per-neuron sign changes:

$$W_1[:, i] \leftarrow s_i W_1[:, i], \quad W_2[i, :] \leftarrow s_i W_2[i, :]$$

for s_i ∈ {-1, +1}. For ReLU activations, f(s_i x) = s_i f(x) when s_i = -1... actually: ReLU(-x) ≠ -ReLU(x). The functional equivalence holds when both pre- and post-activation weights are flipped for each neuron simultaneously, since the ReLU's range restriction means the overall function is preserved only when the incoming and outgoing sign cancels through the linearity of the downstream layer. We sample signs uniformly: s_i ~ Bernoulli(0.5) mapped to {-1,+1}.

**Oracle construction.** For each base model b in the zoo, we construct an oracle orbit member b' by applying the transform with randomly sampled parameters (α or s). This yields N oracle orbit pairs (b, b') where b and b' are verifiably functionally identical by construction. We construct N=500 pairs for each symmetry type (limited by zoo size), with all random seeds fixed for reproducibility.

## 3.3 NFT Invariance Probe

**Encoder.** We use NFT [Zhou et al., 2023] with d_model=256, 4 attention layers, 8 heads, and CLS-token pooling. CLS pooling is critical — we empirically verified that mean pooling collapses embeddings and destroys discrimination. NFT was trained on Condition A (raw weights) for property prediction, then frozen. Weights are tokenized row-by-row from each weight matrix; the CLS token's final-layer representation serves as the model embedding.

**Within-orbit vs. cross-orbit similarity.** For each oracle orbit pair (b, b'), we extract embeddings e(b) and e(b'). Within-orbit similarity is cos(e(b), e(b')). We also sample a cross-orbit comparison: for each base model b, we select a different model c from the zoo with the same test accuracy decile (same functional equivalence class in property space, but different orbit). Cross-orbit similarity is cos(e(b), e(c)). 

**Invariance gap.** We define the invariance gap as:

$$\text{gap} = \overline{\text{within-orbit similarity}} - \overline{\text{cross-orbit same-property similarity}}$$

A negative gap indicates the encoder treats orbit members as more similar to each other than to functionally similar models from different orbits — i.e., the encoder is *more* invariant than random. A positive gap indicates the encoder distinguishes orbit members, wasting capacity on symmetry-induced variation. We compute bootstrap 95% confidence intervals (n_boot=1,000) on the gap.

**Gate criterion (H-M1).** The MUST_WORK gate requires the scaling gap CI to lie entirely above 0 — i.e., NFT is detectably non-invariant to scaling. The sign-flip result is evaluated separately (EXPLORE path).

## 3.4 Canonicalization Conditions

We evaluate five experimental conditions:

| Condition | Preprocessing | Purpose |
|-----------|---------------|---------|
| A | Raw weights (no preprocessing) | NFT baseline |
| B | Scaling canonicalization only | Isolate scaling effect |
| C | Sign-flip canonicalization only | Isolate sign-flip effect |
| D | Scaling + sign-flip canonicalization | Full canonicalization |
| E | Random normalization control | Test normalization artifact hypothesis |

**Scaling canonicalization.** Per-layer L2 normalization: each hidden neuron's incoming weight vector is scaled to unit L2 norm, with the corresponding outgoing weights scaled by the inverse. This collapses all scaling-orbit members to the same canonical representative (always unique and well-defined).

**Sign-flip canonicalization (majority-sign).** For each hidden neuron i, compute the sign majority of row W₁[:, i]. If more weights are negative than positive, flip: W₁[:, i] ← -W₁[:, i], W₂[i, :] ← -W₂[i, :]. This produces a canonical form where each neuron has a non-negative weight majority. For the algorithm to produce a unique canonical form, there must be a strict majority (no ties).

**Random normalization control (Condition E).** Each hidden neuron's incoming weights are scaled by a random factor drawn from N(1, 0.1) — a meaningless normalization that preserves sign structure. If Condition D outperforms E, the effect is symmetry-specific; if D ≈ E or E > D, the effect is a normalization artifact (or worse, D is harmful).

## 3.5 Canonicalization Uniqueness Audit

The majority-sign algorithm requires a strict sign majority per neuron. For d_in=784 weights per neuron, a tie occurs when exactly 392 weights are positive and 392 are negative. The binomial probability of this event is:

$$P(\text{tie}) = \binom{784}{392} 0.5^{784} \approx 2.8\%$$

(using Stirling's approximation). For h=64 neurons per model, the probability of at least one tie per model is:

$$P(\text{at least one tie}) \approx 1 - (1 - 0.028)^{64} \approx 83\%$$

We empirically audit all N=500 zoo models, recording: fraction with unique canonical form (fraction_unique), number of tied neurons per model (tied_neuron_count), and idempotency verification (applying the algorithm twice yields the same result). The audit uses a fixed +1 tie-breaking convention (tied neurons keep their original sign or default to +1).

## 3.6 Geometric Concentration Analysis

To test whether canonicalization concentrates property-relevant geometric structure, we apply PCA to both raw (Condition A) and canonicalized (Condition D) weight matrices. We measure:

- **Explained Variance Ratio (EVR)** at k ∈ {10, 20, 50} principal components: what fraction of total variance is captured by the top-k PCs?
- **Linear regression R²** from top-k PCs onto each property label, with bootstrap 95% CIs.

If canonicalization concentrates property-relevant information, we expect EVR to increase (the same number of PCs captures more variance) and R² to improve (the concentrated variance is more predictive).

## 3.7 Property Prediction Experiments

**Protocol.** For each condition (A–E), we train NFT from scratch as a property predictor on the 400 training models (N=500 zoo, 80/10/10 split: 400 train, 50 validation, 50 test), using the corresponding preprocessed weights as input. Hyperparameters: Adam optimizer, lr=1e-3, weight_decay=1e-4, max_epochs=50, early stopping on validation Spearman ρ (patience=10). Evaluation: Spearman ρ on the 50-model held-out test split, averaged across 3 random seeds.

**Statistical analysis.** Bootstrap 95% CIs (n_boot=1,000) on Spearman ρ and on condition differences (Δρ). At n=50 test samples, CI width for Spearman ρ is approximately ±0.3, yielding CI width ≈0.6. To detect Δρ=0.05 with adequate power (CI width <0.05 on the difference), approximately n≥1,000–5,000 test samples are required. We report this explicitly as a quantified limitation and do not claim significance of directional Δρ estimates.

**Figures.** Key visualizations: orbit distance distributions (histograms per symmetry type), within-orbit vs. cross-orbit similarity distributions (overlapping density plots, scaling and sign-flip panels), PCA embedding visualization (2D PCA of NFT embeddings colored by orbit membership), cumulative EVR curves (Condition A vs. D), and tied-neuron histogram with binomial prediction overlay.
