# Experimental Setup

We design experiments to answer three research questions that directly test our structural alignment thesis:

**RQ1:** Does permutation stress cause a large, statistically significant performance drop in flat-MLP
encoders while NFT encoders maintain robustness? *(Tests the phenomenon: permutation sensitivity differential exists)*

**RQ2:** Is NFT's robustness advantage mediated by equivariant attention capturing neuron influence
concentration signals, as measured by ΔR² ≥ 0.10 in hierarchical regression? *(Tests the mechanism)*

**RQ3:** Do alternative approaches — permutation augmentation (E2) and canonicalization (E3) — provide
sufficient alternatives to architectural equivariance, or does NFT uniquely achieve reliable robustness?
*(Tests the alternatives: does architecture matter, or can training-time approaches substitute?)*

## Dataset

**Unterthiner MNIST Zoo (adapted).** We evaluate on a zoo of 29,997 trained neural networks
adapted from the Unterthiner benchmark [Unterthiner et al., 2020]. Each model is a 4-layer
convolutional network with fan_in = 16 per layer; weight matrices are reshaped to per-neuron
token format (each neuron represented by its 16 incoming weights) for compatibility with both
flat-MLP and NFT encoders. The zoo spans diverse generalization gap values, enabling Spearman
rank correlation analysis.

| Property | Value |
|----------|-------|
| Total models | 29,997 |
| Training split | 23,997 models (80%) |
| Test split | 6,000 models (20%) |
| Network depth | 4 layers |
| Neurons per layer | Variable; fan_in = 16 |
| Prediction target | Generalization gap (train_loss − test_loss) |

The original Unterthiner FC-MLP zoo was unavailable at execution time (URL 404); we adapt the
CNN zoo by reshaping weight matrices to per-neuron token format, which preserves the permutation
structure relevant to our theoretical claims (see Section 6 for full discussion).

**Why this dataset:** It is the established benchmark for weight-space property prediction
[Unterthiner et al., 2020], with sufficient scale (30K models) for statistical analysis and
publicly available. Our adaptation maintains the permutation-symmetry structure that our
hypothesis concerns, making the comparison scientifically valid.

## Encoder Baselines

We compare the following six encoders, spanning the full spectrum of permutation handling:

| Encoder | Architecture | Params | Permutation Handling |
|---------|-------------|--------|---------------------|
| **flat-MLP** | 3-layer MLP, hidden=512 | 3.04M | None (position-dependent) |
| **flat-MLP+aug** | Same as flat-MLP | 3.04M | Augmentation at training time |
| **flat-MLP+canon** | Same as flat-MLP, L2-normed inputs | 3.04M | L2 canonicalization (post-hoc) |
| **NFT-base** | NFT, d_model=128, n_heads=4 | 75K | Architectural equivariance |
| **NFT+aug** | NFT + augmentation | 75K | Architectural + augmentation |
| **Oracle-canon** | flat-MLP, optimal alignment | 3.04M | Oracle (theoretical upper bound) |

**Baseline rationale:** flat-MLP is the prior work baseline [Unterthiner et al., 2020]. flat-MLP+aug
implements [Schürholt et al., 2021] data augmentation strategy. flat-MLP+canon tests post-hoc
symmetry breaking. NFT-base tests architectural equivariance [Zhou et al., 2023]. NFT+aug tests
whether augmentation adds value to an already-equivariant architecture. Oracle-canon establishes
the theoretical upper bound achievable by any canonicalization approach given oracle access to
the optimal neuron alignment.

## Evaluation Protocol

**Permutation Stress.** At test time, we apply random neuron permutations to test model weights at
severity s ∈ {0, 0.25, 0.5, 1.0}, where s is the fraction of neurons randomly permuted within
each layer. Severity s = 0 gives the original ordering (in-distribution evaluation); s = 1.0
applies a fully random permutation.

**Primary Metric.** Spearman rank correlation ρ between predicted and true generalization gap
across 6,000 test models. We report ρ at each severity level and Δρ = ρ(s=0) − ρ(s=1.0)
as the primary measure of permutation sensitivity.

**Statistical Testing.** Bootstrap test for Δρ significance: n = 10,000 paired resamples from
the test set; Holm-Bonferroni correction for multiple comparison correction across severity
levels (4 tests per encoder). We report two-sided p-values for the null hypothesis Δρ = 0.

**Mediation Analysis (RQ2).** Hierarchical regression following Baron & Kenny [1986]: Step 1 fits
R² with flat-MLP+aug embeddings as predictor; Step 2 fits R² with NFT-base embeddings; ΔR² =
R²(NFT-base) − R²(flat-MLP+aug) measures the additional variance explained by equivariant
attention mediation. Gate condition: ΔR² ≥ 0.10.

**Seeds and Replication.** All encoders trained with 3 random seeds (42, 123, 456). Primary
encoder comparisons (RQ1: flat-MLP vs. NFT-base) use single seeds for initial experiments (h-e1,
2 runs) and full 3-seed ablations for mechanism analysis (h-m1, 18 runs = 6 encoders × 3 seeds).

## Implementation Details

All experiments implemented in PyTorch. Encoders trained with Adam optimizer
(lr = 0.001, β₁ = 0.9, β₂ = 0.999, weight decay = 0.0001), CosineAnnealingLR scheduler
(T_max = 100, η_min = 1e-5), for 100 epochs with batch size 64.
NFT configuration: d_model = 128, n_heads = 4, 4 transformer layers (one per zoo network layer).
flat-MLP configuration: 3 layers, hidden dimension 512, input dimension 4,912.
Hardware: single GPU (experiments completed on local cluster). Total training: 21 training runs
(h-e1: 2, h-m1: 18, h-m2: 1 evaluation-only run reusing h-m1 checkpoints).
