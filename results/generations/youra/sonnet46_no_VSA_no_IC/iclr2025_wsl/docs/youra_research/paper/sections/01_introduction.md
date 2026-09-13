# 1. Introduction

A simple trick — randomly shuffling neurons before each training step — outperforms a mathematically guaranteed equivariant architecture when only 100 models are available for training. Yet with 250 models, the structural guarantee wins decisively, and by a factor of nearly seven. Why does a symmetry-enforcing architecture fail at the very scale where its inductive bias should matter most?

This question arises in the setting of *weight-space property prediction*: given a collection of trained neural networks (a model zoo), we want to learn an encoder that predicts model properties — such as test accuracy — directly from the network weights. The encoder must handle a fundamental symmetry: permuting the neurons in any hidden layer produces a functionally identical network, yet a different weight vector. Encoders that ignore this symmetry are forced to learn the invariance from data; those that enforce it by construction — *equivariant encoders* — are expected to be more sample-efficient, especially when labeled model zoos are small.

This expectation is intuitive and has motivated a line of powerful equivariant architectures: DWSNets [Navon et al., 2023], GNN-NFN [Kofinas et al., 2024], and NFN [Zhou et al., 2023]. These encoders achieve state-of-the-art property prediction on model zoos. However, a critical question has remained unanswered: *How much more sample-efficient are they than plain encoders, and does this advantage hold uniformly across all zoo sizes?*

The difficulty is methodological. Prior equivariant encoder papers use private or custom train/test splits; prior plain encoder papers use different datasets. No controlled, shared-split comparison of equivariant vs. plain weight-space encoders at systematically varied training set sizes has been conducted. This means practitioners facing a data constraint — how many models must I train to form a useful zoo? — cannot answer from the existing literature.

A deeper issue lurks beneath the surface. Dayan, Eitan, and Maron [2026] proved that all permutation-equivariant weight-space networks are equivalent in *expressivity* given sufficient data. Their theorem implies that equivariant encoders have no ceiling advantage over plain encoders — the difference must be in *sample complexity*. But the magnitude of this difference, and whether it is uniform across data regimes, is precisely what has not been measured.

We fill this gap with a controlled learning curve study on the ModelZooDataset CIFAR-10 CNN zoo [Schürholt et al., 2022], comparing three conditions at training sizes {100, 250, 500, 1000, full}: (1) flat-MLP (plain encoder), (2) flat-MLP with permutation augmentation (PermAug, a data-level approximation of equivariance), and (3) GNN-NFN (a structural equivariant encoder). Our key insight: the advantage is real and large, but it is *data-regime dependent*.

Our key findings and contributions are:

**1. A 6.8× sample efficiency advantage.** GNN-NFN reaches 90% of its peak R² at N≈147 training models; flat-MLP requires N=1000. The efficiency ratio (6.804×) far exceeds our 2× gate criterion, establishing a strong quantitative benchmark for weight-space encoder comparison.

**2. A novel data-regime crossover.** At N=100, PermAug (R²=0.138) outperforms structural equivariance (GNN-NFN R²=−0.016). At N=250, the ordering reverses (GNN-NFN 0.767 vs. PermAug 0.532 vs. flat-MLP 0.449). This crossover — not predicted in Phase 2A and not present in any prior weight-space learning study — reveals a minimum-data threshold of approximately 150–250 models for equivariant graph encoders to outperform augmented plain alternatives.

**3. Mechanistic grounding.** We verify permutation equivariance to floating-point precision for GNN-NFN (max_diff=1.80×10⁻⁶ across 10,000 checks) and DWSNets (max_diff=7.45×10⁻⁹), confirming the structural basis for the efficiency advantage. Flat-MLP serves as a non-equivariant control (max_diff=5.59×10⁻²; gap ratio ≈7.5M).

**4. A reusable evaluation protocol.** We establish a shared-split learning curve methodology — training sizes {100, 250, 500, 1000, full}, 90%-peak efficiency ratio, bootstrap CI — that enables future encoder comparisons without redesigning experiments.

These findings have direct practical implications: practitioners with small model zoos (<150 models) should prefer flat-MLP with permutation augmentation over equivariant graph encoders; those with medium zoos (250–1000 models) should invest in structural equivariance. The crossover point itself is a new design target for efficient equivariant architectures.

The remainder of this paper is organized as follows. Section 2 situates our work within three streams of prior research. Section 3 describes our methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.
