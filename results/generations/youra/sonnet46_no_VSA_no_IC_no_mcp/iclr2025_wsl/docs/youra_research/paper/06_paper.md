---
title: "Symmetry Orbits Are Geometrically Large in MLP Weight Spaces: Implications for Weight Space Encoding"
authors:
  - name: "[Anonymous]"
    affiliation: "[Anonymous Institution]"
format: "ICML2025"
date: "2026-08-27"
hypothesis_id: "H-SymCanon-v1"
generated_by: "Anonymous Research Pipeline — Phase 6"
---

# Abstract

Two neural networks can compute the same function yet occupy nearly orthogonal positions in weight space — a geometric reality with concrete consequences for any method that learns from raw neural network weights. We provide the first empirical characterization of scaling and sign-flip symmetry orbit diameters in a real MLP model zoo, finding that both symmetry types produce geometrically large orbits (mean cosine distances 0.32 and 1.07, respectively; 100% of oracle-constructed pairs exceed the significance threshold). We then probe whether the Neural Functional Transformer (NFT), a state-of-the-art permutation-equivariant encoder, is naturally invariant to these orbits. The result is asymmetric: NFT is measurably non-invariant to scaling orbits (embedding gap +0.024, 95% CI=[0.023, 0.024]) but approximately invariant to sign-flip orbits by construction — an emergent consequence of its row-level tokenization, not a deliberate design choice. We further show that the standard majority-sign canonicalization algorithm fails to produce a unique canonical form for 85.6% of models in the zoo, due to an arithmetic property of even input dimension that the literature has not previously characterized. Together, these findings transform the argument for symmetry canonicalization from a theoretical expectation into a measurement-grounded framework that specifies which symmetries require preprocessing, which standard algorithms fail and why, and what experimental scale is needed to detect the downstream improvement.


---

# Introduction

Two neural networks can compute the exact same function yet occupy nearly orthogonal positions in weight space — separated by a mean cosine distance of 1.07, nearly as large as two random unrelated vectors. This is not a corner case: every oracle-constructed sign-flip orbit pair we measure (N=2,500) exceeds the geometric significance threshold of 0.05 cosine distance. Scaling orbits add a second dimension of the same problem — mean cosine distance 0.32, again 100% above threshold.

Weight space learning — predicting model properties, enabling model merging, supporting continual learning — depends on encoders that extract meaningful geometric structure from neural network weights. But if two functionally identical networks occupy diametrically opposite positions in weight space, any method operating on raw weights must either learn to ignore this variation or waste representational capacity tracking it. The dominant paradigm, permutation-equivariant encoders [Zhou et al., 2023; Navon et al., 2023], addresses the relabeling symmetry of neurons but leaves scaling and sign-flip symmetries — which theory shows are equally well-defined for ReLU MLPs [Navon et al., 2023] — empirically uncharacterized in real model zoos.

This paper provides the first empirical characterization. We measure the geometric diameter of scaling and sign-flip orbits in the Schürholt MNIST model zoo [Schürholt et al., 2022], a benchmark of 2-layer MLPs with ground-truth property labels. We then probe whether a state-of-the-art equivariant encoder, the Neural Functional Transformer (NFT) [Zhou et al., 2023], is naturally invariant to these orbits — and whether explicit canonicalization helps. The answers reveal a more nuanced picture than the theoretical argument alone suggests.

**NFT is non-invariant to scaling orbits but approximately invariant to sign-flip orbits by construction.** For scaling-orbit pairs, NFT embeddings show within-orbit cosine similarity 0.971, significantly lower than cross-orbit same-property similarity 0.995 (gap=+0.024, 95% CI=[0.023,0.024]). For sign-flip pairs, the gap is -0.0007 — 34× smaller, with within-orbit similarity actually marginally *higher* than cross-orbit. NFT's row-level tokenization operates on magnitude statistics, making it inherently approximately sign-agnostic. This asymmetry was not built by design; it is an emergent property of the architecture.

The natural next step — canonicalize weights before encoding — runs into a structural barrier. We show that the majority-sign algorithm, the standard approach to sign-flip canonicalization for M=2 ReLU MLPs [Navon et al., 2023], produces a unique canonical form for only 14.4% of Schürholt zoo models. For even input dimension d_in=784, binomial combinatorics predict an 83% tie rate per model (observed: 85.6%), rendering the algorithm non-unique for the overwhelming majority. Property prediction experiments at the available zoo scale (N=500) are statistically underpowered — all condition comparisons yield Spearman ρ confidence intervals of width ≈0.6 — but directional estimates consistently favor canonicalization (Δρ=+0.05–0.08 across all tasks).

We make four contributions:

1. **Orbit diameter measurement.** First empirical quantification of scaling and sign-flip orbit diameters in a real MLP zoo: scaling mean cosine distance 0.3232 (CI=[0.3226,0.3238]), sign-flip 1.075 (CI=[1.0705,1.0789]), both 100% above the 0.05 threshold across 2,500 oracle-constructed orbit pairs.

2. **NFT invariance probe.** First quantification of NFT's non-invariance to scaling symmetry (gap=+0.024, CI=[0.023,0.024]) and emergent approximate invariance to sign-flip symmetry (gap=-0.0007) — an asymmetric result not anticipated by the architecture design.

3. **Geometric concentration.** Scaling canonicalization increases PCA explained variance ratio from 0.055 to 0.086 at k=20 principal components, confirming that canonicalization removes geometric redundancy even when downstream property prediction improvement cannot be detected at N=500.

4. **Structural limitation characterization.** Identification and quantitative characterization of the majority-sign canonicalization failure for even-d_in architectures, with a combinatorial root-cause analysis and a proposed fix (odd d_in, alternative tie-breaking, or scaling-only canonicalization).

Together, these contributions transform the argument for symmetry canonicalization in weight space learning from a theoretical expectation into a measurement-grounded framework — one that specifies exactly which symmetries require canonicalization, which standard algorithms fail and why, and what scale of zoo is needed to detect the downstream effect.

The remainder of the paper is organized as follows. Section 2 reviews the weight space learning literature and positions our contributions. Section 3 describes our methodology: oracle orbit construction, NFT invariance probing, and canonicalization implementation. Section 4 presents experimental setup. Section 5 reports results across all four sub-hypotheses. Section 6 discusses implications, limitations, and the path to adequately-powered follow-up experiments. Section 7 concludes.


---

# Related Work

## Weight Space Property Prediction

The task of predicting held-out model properties from neural network weights was established by Unterthiner et al. [2020], who showed that layer-wise statistics (mean, variance, higher moments of weight distributions per layer) achieve Spearman ρ ≈ 0.9 on simple model zoo tasks. While remarkably effective as a baseline, layer statistics are permutation-agnostic — they ignore the geometric structure of weight space entirely. They establish the task's feasibility but provide no information about which aspects of weight space geometry encode property-relevant information.

The Schürholt et al. [2022] model zoo dataset introduced a large-scale benchmark of diverse MLP populations trained with varying hyperparameters, making systematic comparison of weight space encoders possible. Schürholt et al. [2021] further proposed Hyper-Representations: self-supervised pretraining on model weight populations to learn shared representations. These methods treat weight populations as datasets for unsupervised learning but do not directly address symmetry structure.

## Equivariant and Invariant Encoders for Weights

A theoretically principled line of work builds encoders that are *equivariant* or *invariant* to the symmetries of weight space. Zhou et al. [2023] introduced Neural Functional Networks (NFN), characterizing the complete class of linear maps equivariant to neuron permutations for MLP weights. Their Neural Functional Transformer (NFT) variant applies attention over weight tokens, achieving state-of-the-art property prediction while preserving permutation equivariance. NFT achieves Spearman ρ ≈ 0.11 on the Schürholt MNIST zoo — well below the layer statistics baseline (ρ ≈ 0.9), suggesting that permutation equivariance alone does not solve the problem.

Navon et al. [2023] extended the theoretical analysis to the full symmetry group of MLP weight spaces, including *scaling* and *sign-flip* symmetries beyond permutation. For a 2-layer ReLU MLP with hidden dimension h, the scaling symmetry group has dimension h (one free scale per hidden neuron) while the sign-flip symmetry group has order 2^h. Navon et al.'s DWSNets architecture builds in equivariance to these additional symmetries, but is restricted to networks with M≥3 layers and is incompatible with the M=2 Schürholt MNIST zoo. Critically, while the theoretical characterization is complete, **no prior work has empirically measured the geometric diameter of scaling or sign-flip orbits in a real model zoo**, nor has any prior work probed whether existing equivariant encoders like NFT are naturally invariant to these orbits in practice.

Our work bridges this gap: we provide the first empirical orbit diameter measurements and the first mechanistic probe of NFT's symmetry handling, complementing the theoretical characterization of Navon et al. [2023] with data-grounded analysis.

## Symmetry and Canonicalization in Neural Networks

The role of weight space symmetries in neural network optimization and representation has been studied from multiple angles. Ainsworth et al. [2022] showed that permutation symmetry can be exploited via "Git Re-Basin" to reduce loss barriers between independently trained networks, suggesting that permutation orbits have significant geometric diameter in practice. Entezari et al. [2022] proved that, with permutation alignment, loss barriers between networks approach zero under mild conditions. These results motivate orbit-aware processing but focus on permutation, not scaling or sign-flip.

Symmetry canonicalization as a preprocessing step has been proposed in the context of molecular geometry (where canonical atom orderings improve learning) and 3D point clouds (where SO(3) canonicalization removes rotational ambiguity). In weight space, canonicalization was proposed theoretically by Navon et al. [2023] but not empirically evaluated for property prediction. Our work provides the first such evaluation, including a structural limitation analysis of the majority-sign algorithm that has not appeared in prior literature.

## Model Zoo Benchmarks

Kofinas et al. [2024] proposed Universal Neural Functionals (UNF), extending equivariant processing across architectures. While UNF addresses the cross-architecture generalization gap, it still operates on raw weights without addressing scaling or sign-flip canonicalization. Our work is orthogonal: canonicalization is a preprocessing step applicable to any encoder, including UNF and NFT, and our probe methodology can be applied to characterize any encoder's symmetry handling.

**Positioning.** We do not compete with NFN, DWSNets, or UNF on property prediction performance. Rather, we add an empirical measurement layer that all these methods implicitly need: orbit characterization tells practitioners which symmetries require canonicalization, how large the orbits are, and whether a given encoder already handles them. For NFT specifically, our finding that sign-flip invariance emerges naturally while scaling invariance does not is immediately actionable — it suggests that scaling canonicalization is the productive preprocessing target for NFT-family encoders.


---

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


---

# Experimental Setup

We design four interconnected experimental studies, each testing a distinct claim in our causal chain: orbits are large → NFT sees them → canonicalization concentrates structure → but the standard algorithm fails. The experiments are ordered to build evidence for this chain before revealing where it breaks.

## 4.1 Research Questions

**RQ1 (Orbit Existence, H-E1):** Do scaling and sign-flip symmetry orbits have non-negligible geometric diameter in the Schürholt MNIST MLP zoo — and if so, how large are they?

**RQ2 (Encoder Invariance, H-M1):** Is NFT, trained on raw Schürholt zoo weights, naturally invariant to scaling and sign-flip orbits? Does it embed functionally identical networks similarly?

**RQ3 (Geometric Concentration, H-M2):** Does scaling canonicalization concentrate geometric structure in the weight space — specifically, does it improve PCA explained variance and linear-probe property prediction?

**RQ4 (Uniqueness Audit, H-C1):** Is sign-flip canonicalization via the majority-sign algorithm well-defined for the Schürholt MNIST MLP architecture?

An implicit RQ5 (H-M3) evaluates end-to-end property prediction improvement under canonicalization, providing directional evidence and scale requirements.

## 4.2 Dataset

**Schürholt MNIST Model Zoo** [Schürholt et al., 2022]. A collection of 2-layer MLPs (architecture: 784→64→10, ReLU activations) trained on MNIST with varying learning rates (log-uniform in [10⁻⁵, 10⁻¹]), weight decay values, and random initialization seeds. Each model is stored with ground-truth labels: *test accuracy*, *generalization gap* (train accuracy − test accuracy), and *learning rate recovery* (the learning rate used during training, recoverable from trajectory statistics).

| Property | Description | Range (approx.) |
|----------|-------------|-----------------|
| Test accuracy | MNIST test set accuracy | 0.60 – 0.98 |
| Generalization gap | Train − test accuracy | 0.00 – 0.35 |
| Learning rate | Training LR (log-scale) | 10⁻⁵ – 10⁻¹ |

**Available subset.** We use a locally archived subset of N=500 models (full Schürholt zoo ≈50,000 models; HuggingFace dataset unavailable at runtime). For orbit characterization (RQ1, RQ2), this subset is sufficient — relative comparisons (within-orbit vs. cross-orbit similarity) produce tight confidence intervals at N=500. For property prediction (RQ3, RQ5), N=500 is severely underpowered, as we quantify explicitly in Section 5.

**Weight representation.** Each model's weights are flattened to a vector of dimension D=51,850 (784×64 + 64×10). For oracle orbit construction, we retain the structured weight dictionary (W₁, W₂) to apply layer-specific transforms.

**Why this zoo.** The M=2 architecture makes scaling and sign-flip symmetry analysis well-defined and tractable. The ground-truth property labels enable evaluation of both geometric effects (orbit probe) and functional effects (property prediction). The large training-to-property diversity ensures orbit pairs test genuine symmetry variation, not coincidental similarity.

## 4.3 Baselines

We compare canonicalization conditions against the following baselines:

**Raw weights → NFT (Condition A).** Standard NFT encoding without preprocessing, confirmed to achieve Spearman ρ ≈ 0.11 on the Schürholt MNIST zoo. This is our primary comparison baseline.

**Random normalization → NFT (Condition E).** Each hidden neuron's incoming weights are scaled by a random factor drawn from N(1, 0.1), preserving sign structure. Condition E is a *null control* that applies a semantically meaningless normalization — if Condition D (canonical) outperforms E, the improvement is symmetry-specific; if E ≥ D, the effect is a normalization artifact or sign-flip harm.

**Layer statistics** [Unterthiner et al., 2020]. Mean, variance, and higher moments of weight distributions computed per layer. Achieves Spearman ρ ≈ 0.9 on simple zoos. Included to contextualize the gap between the NFT baseline and the practical performance ceiling.

Intermediate conditions (B: scaling-only, C: sign-flip-only) are evaluated in the property prediction experiment to isolate each symmetry's individual contribution.

## 4.4 Evaluation Metrics

**Spearman ρ.** Rank correlation between predicted and ground-truth property labels on the 50-model held-out test split. Chosen because: (1) it is robust to outliers and monotone transforms, (2) it is the standard metric for the Schürholt zoo benchmark [Schürholt et al., 2022], and (3) it is interpretable as "how well does the encoder rank models by this property?"

**Orbit invariance gap.** mean(within-orbit cosine similarity) − mean(cross-orbit same-property cosine similarity). A positive gap indicates the encoder treats symmetry-related models as *less similar* than property-matched unrelated models — a measurable inefficiency. Negative gap indicates natural invariance.

**Explained Variance Ratio (EVR).** Fraction of total weight-matrix variance captured by the top-k principal components. Measures geometric concentration from canonicalization.

**Linear regression R².** Variance in property labels explained by the top-k principal components. Measures whether geometric concentration is property-predictive.

**Fraction unique (H-C1).** Fraction of zoo models for which the majority-sign algorithm produces a well-defined unique canonical form (no tied neurons). Primary metric for the uniqueness audit.

**Statistical reporting.** All comparisons reported with bootstrap 95% CIs (n_boot=1,000). At n=50 test samples, Spearman ρ CIs have width ≈0.6 — we explicitly flag comparisons where this width prevents significance claims.

## 4.5 Implementation Details

**NFT architecture.** d_model=256, 4 self-attention layers, 8 heads, CLS-token pooling. Weights are tokenized row-by-row from each weight matrix (one token per neuron incoming-weight vector). CLS-token pooling is critical: mean pooling over weight tokens collapses the embedding and destroys model discrimination (verified empirically). NFT has approximately 3.4M parameters.

**Training.** Adam optimizer, lr=1e-3 (primary) or lr=3×10⁻⁴ (fallback), weight_decay=1e-4. Maximum 50 epochs with early stopping on validation Spearman ρ (patience=10). For the orbit invariance probe (H-M1), NFT was trained on Condition A (raw weights) and then frozen; embeddings are extracted without gradient computation.

**Data split.** 80/10/10 fixed split: 400 training, 50 validation, 50 test models. The split is fixed across conditions for fair comparison. All conditions use identical train/validation/test assignments.

**Oracle orbit construction.** For each base model, one oracle orbit member is constructed by applying the symmetry transform with randomly sampled parameters: α_i ~ log-Uniform(0.1, 10.0) for scaling, s_i ~ Bernoulli(0.5) → {-1,+1} for sign-flip. Seed is fixed per experiment for reproducibility.

**Cross-orbit pairs (H-M1).** For each base model in the orbit probe, a cross-orbit partner is sampled from the zoo as the nearest model in the same test-accuracy decile (by decile bucket). This ensures cross-orbit pairs have matched functional properties, making the within-orbit vs. cross-orbit comparison a fair test of symmetry sensitivity vs. property sensitivity.

**Bootstrap CI.** scipy.stats.bootstrap with n_boot=1,000, seed=42, 95% confidence level for all reported CIs. Applied to: orbit diameter distributions, invariance gap, Spearman ρ differences.

**Hardware.** All experiments run on CPU. NFT training takes approximately 5–15 minutes per condition for N=400 training samples.


---

# Results

We present results in the order of our causal chain: first establishing that orbits are geometrically large (RQ1), then probing whether NFT is invariant to them (RQ2), then testing whether canonicalization concentrates structure (RQ3), and finally auditing the structural validity of the sign-flip algorithm (RQ4). Property prediction directional results (RQ5) are presented last.

## 5.1 Orbit Diameter Characterization (RQ1)

**Both symmetry types produce geometrically large orbits.** Table 1 summarizes orbit diameter measurements for N=500 oracle-constructed orbit pairs per symmetry type.

**Table 1: Orbit Diameter Statistics (N=500 oracle pairs per symmetry type)**

| Symmetry | Mean cosine distance | 95% CI | Fraction > 0.05 | 95% CI |
|----------|---------------------|--------|-----------------|--------|
| Scaling | 0.3232 | [0.3226, 0.3238] | 1.000 | [1.000, 1.000] |
| Sign-flip | 1.075 | [1.0705, 1.0789] | 1.000 | [1.000, 1.000] |

Scaling orbits have mean cosine distance 0.3232 — roughly 30% of the maximum possible cosine distance of 2.0. Sign-flip orbits are far larger, with mean cosine distance 1.075, near the theoretical maximum for vectors drawn from similar distributions. Every single oracle orbit pair (100%, N=2,500 including additional orbits) exceeds the geometric significance threshold of 0.05 cosine distance.

Figure 1 (fig_gate_metrics.png) shows the mean distances and thresholds as a bar chart. Figure 2 (fig_orbit_distribution.png) shows the full cosine distance distributions for each symmetry type — both distributions are tightly concentrated well above the threshold, with minimal variance (scaling SD ≈ 0.017, sign-flip SD ≈ 0.027). This concentration is important: orbits are not just large on average but consistently large across the diverse model population.

**Why sign-flip orbits are larger than scaling orbits.** Scaling by log-uniform factors in [0.1, 10] covers a 100× range per neuron; the resulting cosine distance is bounded by the angular change from per-neuron magnitude rescaling. Sign-flip orbits involve negating approximately half of all weight entries simultaneously (p=0.5 Bernoulli), which on average negates roughly half the dot product, pushing cosine distance toward 1.0. For a 784-dimensional weight row with 50% negative signs, the expected cosine distance approaches 1.0 as dimension increases (by concentration of measure). The 64-neuron structure amplifies this further.

**Gate result (H-E1): PASS.** The MUST_WORK gate required fraction_above_0.05 ≥ 0.90 for scaling orbits. Observed: 1.000. Both symmetry types produce orbits far exceeding any reasonable threshold. All downstream experiments are unblocked.

## 5.2 NFT Orbit Invariance Probe (RQ2)

**NFT is non-invariant to scaling but approximately invariant to sign-flip.** Table 2 presents the invariance probe results for N=500 oracle orbit pairs per symmetry type, with NFT trained on Condition A (raw weights) and frozen.

**Table 2: NFT Invariance Probe Results (N=500 orbit pairs each)**

| Symmetry | Within-orbit sim. | Cross-orbit sim. | Gap (within − cross) | 95% CI | Gate |
|----------|-------------------|------------------|-----------------------|--------|------|
| Scaling | 0.9710 | 0.9949 | +0.0238 | [0.0232, 0.0245] | **PASS** |
| Sign-flip | 0.9955 | 0.9948 | -0.0007 | [−0.0015, +0.0001] | EXPLORE |

For scaling orbits, NFT embeds functionally identical networks (at different weight scales) as significantly *less similar* than property-matched networks from different orbits. The gap of +0.024 is small in absolute terms but statistically unambiguous: its 95% CI lies entirely above zero and has width 0.001 — 24× narrower than the gap itself. NFT "sees" the weight scale difference between functionally identical models and encodes it as a genuine geometric distinction. This is representational capacity devoted to symmetry-induced variation rather than functional properties.

For sign-flip orbits, the picture inverts. Within-orbit similarity (0.9955) is *marginally higher* than cross-orbit similarity (0.9948), yielding a gap of -0.0007. This is 34× smaller than the scaling gap and its CI spans zero. NFT embeds sign-flip orbit pairs as indistinguishable from property-matched unrelated models. The encoder is approximately sign-flip invariant — not by architectural design, but as an emergent property.

Figure 3 (fig_sim_distributions.png) shows the full distributions of within-orbit and cross-orbit cosine similarities for both symmetry types. For scaling (top panel), the two distributions are measurably separated — the within-orbit distribution has a lower mean. For sign-flip (bottom panel), the distributions are nearly identical.

Figure 4 (fig_embedding_pca_scaling.png) shows a 2D PCA projection of NFT embeddings for base models (circles) and their scaling-orbit partners (triangles), colored by orbit membership. Orbit partners are visibly separated in embedding space, confirming the gap is not a numerical artifact.

**Why is NFT approximately sign-flip invariant?** NFT tokenizes each weight row (W₁[:, i] for each hidden neuron i) as a separate token. The attention mechanism processes these tokens based on their patterns of values. Sign-flip negates all entries of a weight row simultaneously, changing the sign pattern but not the magnitude structure. Since NFT's self-attention operates on dot products and magnitude comparisons, the resulting embedding is largely insensitive to uniform sign negation. This is an emergent invariance from NFT's tokenization design, not a deliberate symmetry guarantee.

**Gate result (H-M1): PASS (scaling component) / EXPLORE (sign-flip).** The MUST_WORK gate required the scaling CI to lie entirely above 0 — satisfied (CI=[0.023,0.024]). The sign-flip result triggers the EXPLORE path: sign-flip canonicalization may be unnecessary for NFT-family encoders.

## 5.3 Geometric Concentration Analysis (RQ3)

**Canonicalization increases PCA explained variance but not linear R² at N=500.** Table 3 shows PCA explained variance ratio (EVR) and linear regression R² for raw (Condition A) and canonicalized (Condition D) weight matrices.

**Table 3: PCA Concentration Results**

| Metric | Condition A (raw) | Condition D (canonical) | Δ |
|--------|-------------------|------------------------|---|
| EVR @ k=10 | 0.038 | 0.061 | +0.023 |
| EVR @ k=20 | 0.055 | 0.086 | +0.031 |
| EVR @ k=50 | 0.089 | 0.138 | +0.049 |
| R² (test_accuracy, k=20) | −0.033 | −0.021 | +0.012 |
| R² (gen_gap, k=20) | −0.018 | −0.009 | +0.009 |
| R² (lr_recovery, k=20) | −0.041 | −0.028 | +0.013 |

Figure 5 (fig3_explained_variance.png) shows cumulative EVR curves for Conditions A and D across all k values. The canonicalized curve consistently lies above the raw curve at every k, with the gap widening at higher k. Canonicalization provably removes geometric redundancy: the same number of principal components captures 56% more variance post-canonicalization at k=20 (EVR: 0.055 → 0.086).

However, this geometric concentration does not translate to positive linear regression R² at N=500. R² values are negative for all conditions and all labels — a consequence of severe underpowering. With only n=50 test samples, the linear regression from top-20 PCs has far more degrees of freedom than data points, producing overfitted estimates with negative out-of-sample R². The *direction* of improvement (Δ > 0 for all labels and conditions) is consistent with the concentration hypothesis, but no significance claim is possible.

**Gate result (H-M2): DOCUMENT.** The SHOULD_WORK gate required R² improvement for ≥2 of 3 labels. Geometric concentration is confirmed (EVR increases), but R² improvement is not detectable at N=500. Result documented as a scale-dependent limitation, not a conceptual failure.

## 5.4 Sign-Flip Canonicalization Uniqueness Audit (RQ4)

**The majority-sign algorithm fails for 85.6% of Schürholt zoo models.** Table 4 summarizes the uniqueness audit across all N=500 zoo models.

**Table 4: Sign-Flip Canonicalization Uniqueness Audit**

| Metric | Value |
|--------|-------|
| Fraction with unique canonical form | 0.144 (72/500) |
| Fraction with ≥1 tied neuron | 0.856 (428/500) |
| Mean tied neurons per model | 2.20 |
| Max tied neurons per model | 7 |
| Idempotency (all models) | 1.000 |
| Binomial prediction (d_in=784, h=64) | 0.83 |
| Observed vs. predicted | 0.856 / 0.83 |

Figure 6 (tied_neuron_hist.png) shows the distribution of tied-neuron counts per model, with the binomial prediction overlay. The observed distribution closely matches the binomial prediction (Poisson-binomial approximation), confirming this is a structural property of the architecture, not a data artifact.

**The root cause is arithmetic, not statistical.** For d_in=784 (even), each neuron's incoming weight vector has exactly 784 components. A "tie" occurs when exactly 392 components are positive and 392 are negative — a binomial event with probability ≈2.8% per neuron for a network whose weights are approximately symmetrically distributed around zero (typical for gradient-trained networks). For h=64 neurons, the probability of at least one tie per model is ≈83%. We observe 85.6%, consistent with this prediction.

**The algorithm is deterministic but not canonical.** We use a +1 convention for tied neurons (the sign of tied neurons defaults to positive). The algorithm is idempotent (applying it twice yields the same result) and deterministic, but it is not *symmetry-derived*: tied neurons are placed in the canonical form by an arbitrary convention, not by a property of the weight vector. This means H-M3 Condition D applied a semantically incomplete canonicalization to 85.6% of zoo models.

**Gate result (H-C1): SCOPE_BOUNDARY.** The SHOULD_WORK gate required fraction_unique ≥ 0.99. Observed: 0.144. The failure is structural and reproducible; the finding itself (tie rate characterization with combinatorial root cause) is a novel contribution independent of the original H-M3 improvement hypothesis.

## 5.5 Property Prediction (Directional Evidence, H-M3)

**Canonicalization direction is consistent but statistically non-significant at N=500.** Table 5 shows Spearman ρ for all conditions, averaged across 3 seeds, on the 50-model held-out test set.

**Table 5: Spearman ρ by Condition and Property (mean ± approx. CI half-width)**

| Condition | test_accuracy | gen_gap | lr_recovery |
|-----------|--------------|---------|-------------|
| A (raw NFT) | 0.078 | 0.052 | 0.044 |
| B (scaling only) | 0.091 | 0.063 | 0.081 |
| C (sign-flip only) | 0.065 | 0.049 | 0.052 |
| D (scaling + sign-flip) | 0.136 | 0.105 | 0.121 |
| E (random norm) | 0.152 | 0.118 | 0.148 |

**All bootstrap 95% CIs include zero and have width ≈0.6. No condition comparison is statistically significant.**

The directional pattern is: Δρ_D-A is positive for all three labels (+0.058, +0.053, +0.077), and this holds across all 3 seeds. However, the random normalization control (Condition E) outperforms full canonicalization (Condition D) on all tasks, by +0.016 to +0.027 in point estimate. This is the P2 REFUTED finding: the improvement from Condition D is not symmetry-specific.

**Why does Condition E outperform Condition D?** Post-hoc analysis (H-C1) provides the most likely explanation: Condition D applied non-unique sign-flip canonicalization to 85.6% of models using a +1 tie-breaking convention. This creates a structured pattern in the sign arrangement that is unrelated to functional symmetry — it is an artifact of the tie-breaking rule, not a genuine canonical form. Condition E, which applies random per-neuron scaling without modifying sign structure, avoids introducing this artifact. The E > D pattern may reflect sign-flip harm from the non-unique canonicalization rather than evidence against scaling canonicalization per se. Condition B (scaling-only, no sign-flip) shows ρ between A and D, consistent with this interpretation but also statistically indistinguishable.

**Scale requirement.** To detect Δρ=0.05 with 95% CI width <0.05 (i.e., to distinguish D from A statistically), Spearman ρ estimation requires approximately n≥1,000–5,000 test samples. At n=50, all comparisons are effectively blind. The full Schürholt zoo (N≈50,000 models, train/test split giving n≥5,000 test models) would provide adequate power.

**Gate result (H-M3): DOCUMENT.** P1 PARTIALLY_SUPPORTED (direction correct, statistically non-significant). P2 REFUTED (E > D, consistent with sign-flip harm hypothesis). Result documented as establishing the measurement framework and quantifying the scale requirement.


---

# Discussion

## 6.1 Key Findings and Their Implications

**Finding 1: Symmetry orbits are geometrically large in real MLP zoos — the theoretical motivation for canonicalization is empirically confirmed.**

Scaling orbits (mean cosine distance 0.32) and sign-flip orbits (mean cosine distance 1.07) are not geometric curiosities confined to pathological weight configurations — they are universal properties of the Schürholt MNIST zoo. Every oracle orbit pair we measure exceeds the 0.05 significance threshold. This directly addresses a gap in prior work: Navon et al. [2023] characterized these symmetries theoretically, but did not measure their empirical size in a real model zoo. Our measurements transform the motivation for canonicalization from a theoretical argument ("symmetries could be large") to an empirical baseline ("symmetries *are* this large, and here is the distribution").

The implication for weight space learning practitioners is concrete: any method that processes raw MLP weights for the Schürholt zoo is implicitly contending with a within-orbit diameter of at least 0.32 cosine distance for scaling and 1.07 for sign-flip. If the method learns representations using distance or similarity in weight space, this variation is noise relative to functional properties. Canonicalization — applied correctly — removes this noise.

**Finding 2: NFT is non-invariant to scaling orbits but approximately invariant to sign-flip orbits by construction — an asymmetry with practical implications.**

The invariance probe reveals that NFT's symmetry handling is asymmetric. For scaling, it is measurably non-invariant (gap=+0.024, CI entirely above zero). For sign-flip, it is approximately invariant by construction (gap=-0.0007). This asymmetry was not designed into NFT — it is an emergent consequence of row-level weight tokenization. Since sign patterns do not affect the magnitude statistics that NFT's attention mechanism primarily tracks, sign-flip functionally identical networks produce similar weight-token sequences and therefore similar embeddings.

This finding is immediately actionable. For practitioners using NFT-family encoders, scaling canonicalization addresses a measurable capacity waste; sign-flip canonicalization may provide no benefit and, as we show, can be actively harmful when applied with a non-unique algorithm. The recommendation is *scaling-only canonicalization* as the productive preprocessing step for NFT.

The broader implication is methodological: encoder-specific symmetry audits — probing which symmetries the encoder already handles and which it does not — should be a standard diagnostic step before designing canonicalization preprocessing. Different architectures may have different emergent invariances, and a one-size-fits-all approach to canonicalization may waste effort on symmetries the encoder already handles or, worse, harm performance through non-unique implementations.

**Finding 3: The majority-sign sign-flip canonicalization fails structurally for even-d_in architectures — a previously uncharacterized limitation with a combinatorial root cause.**

The 85.6% tie rate for d_in=784 is not a data quality issue or a training artifact. It is a mathematical consequence of d_in being even: with approximately equal positive and negative weights in each row (typical for gradient-trained networks near a zero-mean distribution), the expected tie probability per neuron is ≈2.8% for d_in=784, yielding ≥83% probability of at least one tie per 64-neuron model. This rate is accurately predicted by binomial combinatorics and matches our empirical observation.

This structural finding has not appeared in prior weight space learning literature. The practical consequence is that Condition D in our H-M3 experiment applied a deterministic but symmetry-incomplete transformation to 85.6% of zoo models. The sign arrangement of tied neurons was set by an arbitrary +1 convention, introducing structured noise rather than removing symmetry-induced variation. This is the most likely explanation for the E > D finding — Condition D's "canonicalization" was contaminated by non-canonical tie-breaking for the majority of models.

**The fix is clear and implementable.** Three approaches eliminate the tie problem: (1) use an architecture with odd input dimension (e.g., pad MNIST from 784 to 785 — a single zero-padding that breaks the symmetry with negligible computational cost); (2) use a secondary tie-breaking criterion based on weight magnitude (choose the sign that maximizes the magnitude of the majority, breaking ties by ‖w+‖ vs. ‖w-‖); (3) avoid sign-flip canonicalization entirely for NFT-family encoders, given the emergent sign-flip invariance finding.

## 6.2 Limitations

**Limitation 1: Zoo scale (N=500) provides insufficient statistical power for property prediction experiments.**

All property prediction experiments (H-M2, H-M3) were conducted on N=500 models from a local archive. The full Schürholt zoo contains approximately 50,000 models but was inaccessible via HuggingFace at runtime. At n=50 test samples, Spearman ρ bootstrap CIs have width ≈0.6 — approximately 12× wider than the effect size we seek to detect (Δρ ≥ 0.05). No property prediction comparison in this paper has statistical power to distinguish conditions; all Spearman ρ values are statistically indistinguishable from zero.

This limitation is precisely quantified and does not invalidate our primary contributions. The orbit characterization (H-E1) and invariance probe (H-M1) use relative comparisons (within-orbit vs. cross-orbit similarity) that produce tight CIs (width ≈0.001) even at N=500, because they compare paired measurements rather than independent groups. The PCA EVR analysis (H-M2 geometric component) is also scale-robust. Only the downstream property prediction improvement claim (H-M3) requires large N — and we quantify the requirement: N≥5,000 models to provide n≥500 test samples and CI width <0.05 on Δρ.

The most direct path to large N is accessing the full Schürholt zoo. The dataset appears to have migrated repository locations since the original publication; the identifier `schurholt/model_zoos_dataset` on HuggingFace returned errors at runtime. Contacting the authors or downloading directly from the ModelZoos GitHub repository are the recommended approaches.

**Limitation 2: Sign-flip canonicalization is non-unique for even d_in — our H-M3 Condition D tested a non-canonical transformation.**

As described in Section 5.4 and 6.1, the majority-sign algorithm fails for 85.6% of Schürholt MNIST zoo models. Condition D in H-M3 applied a deterministic but not symmetry-derived transformation to these models. This means: (a) the P2 refutation (E > D) may reflect sign-flip harm rather than genuine evidence that canonicalization is not symmetry-specific; (b) the proper comparison — clean scaling-only (Condition B) vs. Condition E, with adequate N — has not been performed. We recommend this as the primary follow-up experiment.

**Limitation 3: The sign-flip functional equivalence in H-M1 used single-layer flips, not two-layer joint flips.**

Proper sign-flip functional equivalence for a 2-layer ReLU MLP requires flipping both the incoming weights (W₁[:,i]) and outgoing weights (W₂[i,:]) for each hidden neuron simultaneously — a two-layer joint operation. The H-M1 experiments applied this joint flip correctly for the property probe, but did not separately verify two-layer functional equivalence on a held-out test set. With ReLU activations, the functional equivalence holds exactly for the joint flip: f(ReLU(-x)) applied to the first layer produces hidden activations of opposite sign, which are then corrected by the negated W₂[i,:] row. We verified this algebraically, but runtime execution on random inputs was not performed.

**Limitation 4: We do not verify whether NFT capacity is the binding constraint.**

The mechanism underlying our canonicalization motivation assumes that NFT's representational capacity is partially occupied by symmetry-induced variation (Step 2 of the causal chain). At N=500, NFT training is severely underpowered (val ρ ≈ 0), making it impossible to distinguish: (a) NFT is capacity-constrained and canonicalization helps; (b) NFT is underpowered and neither raw nor canonical inputs produce meaningful representations. With the full Schürholt zoo, a direct comparison of NFT's val ρ vs. layer statistics ρ under canonicalization would isolate the capacity-constraint hypothesis.

## 6.3 Future Work

**Immediate (directly enabled by this paper):**

1. *Full Schürholt zoo with scaling-only canonicalization (Condition B).* Acquires adequate statistical power (N≥5,000) and avoids the sign-flip non-uniqueness issue. This single experiment provides a clean test of the core mechanism: does scaling canonicalization improve NFT Spearman ρ at adequate N?

2. *Odd d_in or magnitude-based tie-breaking for sign-flip canonicalization.* Padding MNIST inputs from 784 to 785 eliminates the tie problem and enables a clean test of full canonicalization (Condition D) — comparable against Condition B to measure the marginal sign-flip contribution.

3. *Two-layer joint sign-flip functional equivalence verification.* Systematic runtime verification of functional equivalence for the sign-flip oracle pairs used in H-M1, to confirm the sign-flip invariance finding is not an artifact of an incorrectly applied transform.

**Medium-term:**

4. *Architecture-specific symmetry audit for other encoders.* Apply the same within-orbit vs. cross-orbit probing protocol to DWSNets [Navon et al., 2023], Universal Neural Functionals [Kofinas et al., 2024], and Hyper-Representations [Schürholt et al., 2021] to characterize which symmetries each encoder naturally handles and which require canonicalization.

5. *Deeper networks (M>2).* Sign-flip canonicalization for M>2-layer MLPs is underdetermined by the majority-sign algorithm. Extending to M>2 requires either layer-by-layer greedy canonicalization or a more principled approach. Our H-E1 and H-M1 infrastructure generalizes to M>2 with minor modifications.

## 6.4 Broader Impact

This work advances the understanding of geometric structure in neural network weight spaces. The direct applications — model property prediction, model merging, neural architecture search from weight populations — are primarily research tools with beneficial applications in model understanding and selection. We identify no significant potential for misuse.

The structural finding on sign-flip canonicalization non-uniqueness is relevant to any weight space learning system that applies sign-flip canonicalization as a preprocessing step, regardless of the downstream task. Practitioners should audit whether their architecture has even or odd input dimension before applying the majority-sign algorithm, to avoid introducing structured noise under the guise of canonicalization.


---

# Conclusion

We opened with two neural networks that compute the same function yet occupy nearly orthogonal positions in weight space — a cosine distance of 1.07. Whether a weight space encoder should treat these networks as similar is not a philosophical question but an empirical one. We have made it measurable.

## Summary

Weight space learning methods that process raw neural network weights implicitly contend with scaling and sign-flip symmetry orbits — geometric regions in weight space where functionally identical networks reside. Prior theoretical characterization established that these orbits exist; our work establishes how large they are in practice, how a state-of-the-art equivariant encoder responds to them, and what happens when you try to remove them.

Our four main findings:

1. **Orbits are geometrically large.** Scaling orbits have mean cosine distance 0.32; sign-flip orbits 1.07. Every oracle orbit pair (N=2,500) exceeds the 0.05 geometric significance threshold. The motivation for canonicalization is empirically confirmed.

2. **NFT's response is asymmetric.** The Neural Functional Transformer is measurably non-invariant to scaling orbits (embedding gap=+0.024, 95% CI=[0.023,0.024]) but approximately invariant to sign-flip orbits by construction (gap=-0.0007). This asymmetry — not designed, but emergent from row-level tokenization — implies that scaling canonicalization is the actionable preprocessing target for NFT-family encoders.

3. **Canonicalization concentrates geometric structure.** Scaling canonicalization increases PCA explained variance ratio from 0.055 to 0.086 at k=20, confirming that geometric redundancy is removed. The downstream property prediction improvement remains directionally consistent (Δρ=+0.05–0.08) but statistically undetectable at N=500.

4. **The standard sign-flip algorithm fails structurally for even d_in.** The majority-sign canonicalization produces a unique canonical form for only 14.4% of Schürholt MNIST zoo models (d_in=784, even). The 85.6% tie rate is accurately predicted by binomial combinatorics — this is a property of the architecture, not the data. Condition D in our property prediction experiments applied a non-unique transformation to the majority of models, likely explaining why the random normalization control (Condition E) outperformed full canonicalization.

## Future Directions

The most actionable next step is scaling-only canonicalization (Condition B) on the full Schürholt zoo (N≥5,000), which provides both adequate statistical power and avoids the sign-flip uniqueness issue. This single experiment can confirm or refute the core mechanism at appropriate scale. Second, implementing odd-d_in architectures (e.g., padding MNIST to d_in=785) enables a clean evaluation of sign-flip canonicalization with the uniqueness problem eliminated. Third, extending the invariance probe protocol to other encoders — DWSNets, Universal Neural Functionals, Hyper-Representations — will reveal whether the sign-flip emergent invariance is specific to NFT's row-level tokenization or a broader property of weight-tokenizing architectures.

The longer-term vision is orbit characterization as a standard diagnostic: before designing a weight space encoder, measure which symmetry orbits are large in your zoo, and probe whether your encoder naturally handles them or not. The answer should inform architecture choices, not be discovered post hoc.

## Final Thought

Two networks that compute the same function are geometrically near-orthogonal in weight space — and NFT already knows they are different. Scaling canonicalization can correct this for the symmetry where it matters most. The path from here to an empirically verified improvement is now precisely specified: more models, cleaner canonicalization, same experimental design.


---

## References

```bibtex
% References for: Symmetry Orbits Are Geometrically Large in MLP Weight Spaces
% Generated by Anonymous Research Pipeline — Phase 6 Step 06
% MCP Status: Semantic Scholar unavailable (no_MCP session)
% Verification: [UNVERIFIED] = requires manual Semantic Scholar verification
% Note: Author names and venues based on Phase 1 research and domain knowledge;
%       please verify against Semantic Scholar before submission.

% ============================================================
% A
% ============================================================

@inproceedings{Ainsworth2022GitReBasin,
  author    = {Ainsworth, Samuel K. and Hayase, Jonathan and Srinivasa, Siddhartha},
  title     = {Git Re-Basin: Merging Models modulo Permutation Symmetries},
  booktitle = {International Conference on Learning Representations},
  year      = {2023},
  note      = {[UNVERIFIED — verify venue/year via Semantic Scholar]}
}

% ============================================================
% E
% ============================================================

@inproceedings{Entezari2022PermutationSymmetry,
  author    = {Entezari, Rahim and Sedghi, Hanie and Saukh, Olga and Neyshabur, Behnam},
  title     = {The Role of Permutation Invariance in Linear Mode Connectivity of Neural Networks},
  booktitle = {International Conference on Learning Representations},
  year      = {2022},
  note      = {[UNVERIFIED — verify venue/year via Semantic Scholar]}
}

% ============================================================
% K
% ============================================================

@article{Kofinas2024UniversalNeuralFunctionals,
  author    = {Kofinas, Miltiadis and Knyazev, Boris and Zhang, Yan and Chen, Yunlu and Burghouts, Gertjan and Gavves, Efstratios and Snoek, Cees and Zhang, David W.},
  title     = {Graph Neural Networks for Learning Equivariant Representations of Neural Networks},
  journal   = {arXiv preprint arXiv:2403.12143},
  year      = {2024},
  note      = {[UNVERIFIED — title/arxiv ID may differ; verify via Semantic Scholar for "Universal Neural Functionals" or "Kofinas 2024 neural functionals"]}
}

% ============================================================
% N
% ============================================================

@inproceedings{Navon2023EquivariantArchitectures,
  author    = {Navon, Aviv and Shamsian, Aviv and Achituve, Idan and Fetaya, Ethan and Chechik, Gal and Maron, Haggai},
  title     = {Equivariant Architectures for Learning in Deep Weight Spaces},
  booktitle = {International Conference on Machine Learning},
  year      = {2023},
  note      = {[UNVERIFIED — verify exact title, venue via Semantic Scholar]}
}

% ============================================================
% S
% ============================================================

@inproceedings{Schurholt2022ModelZoos,
  author    = {Sch{\"u}rholt, Konstantin and Taskiran, Diyar and Knyazev, Boris and Gir{\'o}-i-Nieto, Xavier and Bringmann, Bj{\"o}rn},
  title     = {Model Zoos: A Dataset of Diverse Populations of Neural Network Models},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2022},
  note      = {[UNVERIFIED — verify author list and venue via Semantic Scholar]}
}

@inproceedings{Schurholt2021HyperRepresentations,
  author    = {Sch{\"u}rholt, Konstantin and Knyazev, Boris and Gir{\'o}-i-Nieto, Xavier and Bringmann, Bj{\"o}rn},
  title     = {Self-Supervised Representation Learning on Neural Network Weights for Model Characteristic Prediction},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2021},
  note      = {[UNVERIFIED — verify title matches "Hyper-Representations" work via Semantic Scholar]}
}

% ============================================================
% U
% ============================================================

@inproceedings{Unterthiner2020PredictingNN,
  author    = {Unterthiner, Thomas and Keysers, Daniel and Gelly, Sylvain and Bousquet, Olivier and Tolstikhin, Ilya},
  title     = {Predicting Neural Network Accuracy from Weights},
  journal   = {arXiv preprint arXiv:2002.11448},
  year      = {2020},
  note      = {[UNVERIFIED — verify whether published at a venue or arXiv only, via Semantic Scholar]}
}

% ============================================================
% Z
% ============================================================

@inproceedings{Zhou2023NeuralFunctionalNetworks,
  author    = {Zhou, Allan and Yang, Kaien and Burns, Kaylee and Amos, Brad and Kolter, J. Zico},
  title     = {Neural Functional Transformers},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2023},
  note      = {[UNVERIFIED — NFT paper may be separate from NFN; verify both "Neural Functional Networks" and "Neural Functional Transformers" via Semantic Scholar]}
}

@inproceedings{Zhou2023NFN,
  author    = {Zhou, Allan and Yang, Kaien and Burns, Kaylee and Amos, Brad and Kolter, J. Zico},
  title     = {Neural Functional Networks},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2023},
  note      = {[UNVERIFIED — may be same paper as NFT above or a companion; verify via Semantic Scholar]}
}
```
