# Experimental Setup

We design experiments to answer four research questions, each corresponding to a contribution from the
Introduction:

**RQ1 (Existence):** Is generalization gap learnable from weight tensors at Spearman r > 0.5, and is
gap genuinely independent of test accuracy (A1 audit)?

**RQ2 (Architecture ranking):** Which encoder architecture achieves the highest gap Spearman, and with
what statistical confidence?

**RQ3 (Gap-specific signal):** Do gap predictions from the best encoder contain information about true
gap that is statistically independent of test accuracy?

**RQ4 (Differential advantage):** Do equivariant encoders show larger Spearman improvement on gap than
on test accuracy (Δ > 0.02) — the target-specificity mechanism hypothesis?

## 4.1 Dataset

**Unterthiner CIFAR-10 CNN Zoo.** We evaluate on the model zoo from Unterthiner et al. [2020]: N = 10,000
small convolutional neural networks trained on CIFAR-10 with a fixed 4-layer architecture and varying
hyperparameters (learning rate ∈ {0.0001, 0.001, 0.01, 0.1}, weight decay, optimizer ∈ {SGD, Adam,
RMSprop}). Each model provides a weight tensor of dimension D = 33,890 (all parameters concatenated)
and training logs from which we compute:
- $y^{\text{acc}}$ = test accuracy at the epoch with best validation accuracy
- $y^{\text{gap}} = y^{\text{train}} - y^{\text{acc}}$ (generalization gap at convergence)

**Rationale.** The Unterthiner zoo is the standard benchmark for weight-space model property prediction,
enabling direct comparison with prior encoders. Its dense coverage of hyperparameter configurations
provides meaningful variance in both test accuracy and generalization gap.

**Split.** 80% training (8,000 models), 10% validation (1,000 models), 10% test (1,000 models).
Stratified by hyperparameter configuration, seed 42. Test split is never used during encoder training
or hyperparameter selection.

**A1 Audit.** Before any training, we verify that generalization gap and test accuracy are not collinear:
Spearman(gap, −test_acc) = −0.142 (|−0.142| << 0.95). Gap and test accuracy are only weakly negatively
correlated in this zoo, confirming that gap prediction is a genuinely distinct task.

## 4.2 Encoders (Baselines and Proposed)

We compare four weight-space encoders spanning the range from non-equivariant to fully equivariant:

| Encoder | Equivariance Type | Architecture | Source |
|---------|-----------------|--------------|--------|
| FlatMLP | None (position-indexed) | 3-layer MLP on sorted weights | Unterthiner et al. [2020] |
| DWSNet | Within-layer (row/col) | Equivariant linear layers per matrix | Navon et al. [2023] |
| NFT | Cross-layer (sequence attention) | Multi-head attention on weight matrix sequence | Zhou et al. [2023] |
| GNN | Graph-structured | Message passing over neuron graph | Kofinas et al. [2024] |

**Why these baselines.** FlatMLP is the foundational baseline from the zoo benchmark paper — any claim
about gap learnability must be benchmarked against it. DWSNet, NFT, and GNN are the three dominant
equivariant architectures in the literature, each representing a distinct inductive bias: within-layer
averaging, cross-layer attention, and graph connectivity, respectively. Testing all three allows us to
attribute architecture-specific effects rather than "equivariance in general."

**Dual-target design.** For RQ4, all four encoders are trained on each target (gap and test_acc)
independently, with identical hyperparameter budget and training procedure. This controls for
zoo-specific effects and isolates target-specificity.

## 4.3 Training Protocol

All encoders use:
- Optimizer: Adam
- Learning rate search: 3-trial random search over {5×10⁻⁴, 1×10⁻³, 2×10⁻³}
- Batch size: 64
- Epochs: 100
- Learning rate schedule: cosine (NFT, GNN); none (FlatMLP, DWSNet)
- Selection criterion: best validation Spearman across 3 trials
- Random seed: 42 for all data splits, model initialization, and training

**Computational resources.** All experiments run on a single GPU. NFT and GNN require ~3× more compute
per trial than FlatMLP due to attention and message-passing overhead.

**Acknowledged limitation.** The pre-specified protocol called for 50-trial random search. Resource
constraints reduced this to 3 trials. The impact is most evident in FlatMLP test_acc Spearman (r = 0.279
vs. literature ~0.85) and is discussed in Section 5.3.

## 4.4 Evaluation Metrics

**Spearman rank correlation** (primary): $\rho(\hat{y}, y)$ on the test split (N = 1,000). Chosen
because practitioners care about relative ranking (which models are least overfit?) rather than absolute
predictions.

**Bootstrap 95% confidence intervals** (uncertainty quantification): $N_{\text{boot}} = 1{,}000$
resamples, seed 42, percentile CI. Applied to all Spearman estimates and to Δ values.

**Differential advantage** (RQ4): $\Delta(e) = [\rho_{\text{gap}}(e) - \rho_{\text{gap}}(\text{FlatMLP})] - [\rho_{\text{acc}}(e) - \rho_{\text{acc}}(\text{FlatMLP})]$ for each equivariant encoder $e$. Gate criterion: $\Delta > 0.02$ for $\geq 2$ of 3 equivariant encoders.

**Partial Spearman** (RQ3): $\rho_{\text{partial}}(\hat{y}^{\text{gap}}, y^{\text{gap}} | y^{\text{acc}})$ via rank residual regression (described in Section 3.7). Threshold: $\rho_{\text{partial}} > 0$, $p < 0.05$.

**Mean Squared Error** (secondary): MSE on the test split, reported alongside Spearman.

## 4.5 Statistical Validity

Experiments follow a pre-registered design (Phase 2B verification plan):
- A1 audit computed before any training
- Threshold values (Δ > 0.02, r > 0.5, partial ρ > 0) pre-specified
- Test split never used for hyperparameter selection
- Bootstrap CI used for all reported statistical comparisons

All gate decisions (PASS/FAIL) are made against pre-specified thresholds, not post-hoc.
