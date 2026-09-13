# 4. Experimental Setup

We design four research questions (RQs) that map directly to the claims in the Introduction. Each experimental choice is motivated by the specific claim it tests.

## 4.1 Research Questions

**RQ1 (Main efficiency claim):** Does GNN-NFN achieve a sample efficiency ratio ≥2× over flat-MLP on shared ModelZooDataset splits? This is the primary test of Prediction P1 from Phase 2A.

**RQ2 (Mechanistic grounding):** Is permutation equivariance verified to floating-point precision for GNN-NFN and DWSNets? Does this structural property distinguish them from flat-MLP in practice?

**RQ3 (Data-regime dependence):** What is the role of permutation augmentation across data regimes — is it always intermediate between plain and structural equivariance, or does the ordering depend on training set size?

**RQ4 (Full-scale convergence):** At full training scale, do all encoder types converge in performance — consistent with Dayan et al. [2026]'s expressivity equivalence theorem?

## 4.2 Dataset

We evaluate on the **ModelZooDataset CIFAR-10 CNN zoo** [Schürholt et al., 2022]. The zoo contains approximately 9,000 convolutional neural networks trained on CIFAR-10 with systematic hyperparameter variation (learning rates in {0.001, 0.003, 0.01}, weight decay in {0, 0.0001, 0.001}, with and without dropout). Ground-truth test accuracy on the CIFAR-10 test set serves as the prediction target.

| Attribute | Value |
|-----------|-------|
| Total models | ~9,000 |
| Architecture | CNN (conv layers + 2 FC layers) |
| Training set | ~7,000 models |
| Test set | ~2,000 models |
| Property | Test accuracy on CIFAR-10 |
| Split | Standardized from ModelZooDataset repository |

**Why CIFAR-10 zoo:** It is the larger and more challenging zoo, enabling training-size ablation down to N=100 while maintaining a large test split. It is also the appropriate zoo for GNN-NFN (which handles CNN weight spaces via computational graph construction), while DWSNets is better suited to MLP weight spaces.

*Scope limitation:* The MNIST MLP zoo (~4,860 models) was not available in our local environment and is left for future work.

## 4.3 Baselines

| Encoder | Type | Parameters | Key feature |
|---------|------|------------|-------------|
| Flat-MLP | Plain | ~190K | Flattened weights, no symmetry handling |
| Flat-MLP + PermAug | Augmented | ~190K | Flat-MLP + 11× permutation expansion |
| GNN-NFN | Equivariant | ~180K | Graph-structured, permutation-equivariant |

**Why PermAug is included:** Without PermAug as an intermediate condition, we cannot determine whether GNN-NFN's advantage at N≥250 is due to equivariance per se or simply due to training data expansion. PermAug controls for the data quantity effect — if PermAug (with 11× expansion) underperforms GNN-NFN (without expansion), the structural advantage is real.

**Why this encoder selection:** DWSNets requires M>2 fully connected layers — the CIFAR-10 CNN zoo architecture (2 FC layers) is incompatible. DWSNets is verified structurally equivariant on synthetic MLP weights (H-M1) but excluded from property prediction comparisons. GNN-NFN is architecturally general to CNN weight spaces and is the current state-of-the-art equivariant encoder.

## 4.4 Training Sizes

Training sizes: $N \in \{100, 250, 500, 1000, \text{full} (\approx 7000)\}$

The logarithmic spacing is deliberate: the crossover is expected (and found) between N=100 and N=250. A coarser grid (e.g., {500, 1000, full}) would miss it entirely.

## 4.5 Implementation Details

| Hyperparameter | Value |
|----------------|-------|
| Optimizer | Adam |
| Learning rate | 1×10⁻³ |
| Weight decay | 1×10⁻⁴ |
| Batch size | 64 |
| Epochs | 100 |
| GNN-NFN hidden dim | 64 |
| GNN-NFN layers | 4 |
| Flat-MLP hidden dim | 256 |
| Flat-MLP layers | 3 |
| PermAug expansion | 11× (N_aug = N_base × 11) |
| Bootstrap resamples | 1,000 (percentile method) |
| Seeds | 1 (PoC mode) |

All experiments run on NVIDIA H100 NVL GPUs. H-M2 (efficiency ratio computation) completes in ~10 seconds by loading H-E1 stored results. H-M3 (PermAug training) completes in ~20 minutes per training-size condition.

## 4.6 Evaluation Metrics

**Test R²:** Primary metric. $R^2 = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$. Values above 0 indicate better-than-mean prediction; values below 0 indicate worse-than-mean.

**Efficiency ratio:** $N_{\text{plain},90} / N_{\text{equiv},90}$, where $N_{x,90}$ is the minimum training size at which encoder $x$ reaches 90% of its full-data R² (interpolated from the learning curve).

**PermAug fraction of gap:** $(R^2_{\text{PermAug}} - R^2_{\text{flat}}) / (R^2_{\text{GNN-NFN}} - R^2_{\text{flat}})$ at each training size.

**Permutation equivariance:** max|f(Pθ) − Pf(θ)| across 10,000 permutation checks per encoder (GNN-NFN on real CIFAR-10 zoo models; DWSNets on synthetic 4-layer MLP weights).
