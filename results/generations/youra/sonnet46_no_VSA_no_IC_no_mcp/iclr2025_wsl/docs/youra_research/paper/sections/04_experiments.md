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
