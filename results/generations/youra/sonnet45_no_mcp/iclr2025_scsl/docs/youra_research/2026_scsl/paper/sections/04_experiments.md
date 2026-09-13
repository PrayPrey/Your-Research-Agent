# Experimental Setup

We design experiments to test whether curvature subspace orientation reliably distinguishes spurious from robust training, and to validate the mechanistic steps in our proposed causal chain.

## Research Questions

Our experiments address the following questions:

**RQ1 (Existence):** Do ERM and Group-DRO solutions exhibit significantly different curvature subspace alignments as measured by Marchenko-Pastur-defined outlier eigenvectors?

**RQ2 (Mechanism - Concentration):** Does sharp curvature concentrate in discrete Hessian eigenspace subspaces (outlier eigenvalues) rather than being diffusely distributed?

**RQ3 (Mechanism - SGD Bias):** Does SGD exhibit measurable directional bias toward locally flat (bulk) directions over sharp (outlier) directions during training?

**RQ4 (Diagnostic Value):** Can the alignment metric distinguish training regimes (ERM vs robust optimization) without requiring group labels at inference time?

## Datasets

We evaluate on the Waterbirds benchmark, which provides ground-truth spurious correlation structure necessary for validating our geometric diagnostic.

**Waterbirds:** A fine-grained bird classification dataset with spurious background correlation. The dataset contains 11,788 images across 4 groups: landbirds on land backgrounds (majority, 3,498 samples), landbirds on water backgrounds (minority, 184 samples), waterbirds on land backgrounds (minority, 56 samples), and waterbirds on water backgrounds (majority, 1,057 samples). The spurious correlation (background type predicts bird type) allows ERM to achieve high average accuracy while failing on minority groups.

**Why Waterbirds:** The dataset provides (1) ground-truth group annotations enabling worst-group accuracy measurement, (2) natural spurious correlation that ERM exploits, and (3) sufficient sample size for reliable Hessian eigenvalue spectrum analysis. The benchmark has been extensively studied in prior robustification work, enabling direct comparison.

## Baselines

We compare against the following methods:

**Standard ERM:** Cross-entropy loss minimization with SGD. Represents standard practice and is expected to exploit the spurious background correlation, achieving high average accuracy but poor worst-group performance. Included as the primary case study for spurious correlation exploitation.

**Group Distributionally Robust Optimization (Group-DRO)** [Sagawa et al., 2020]: Minimizes worst-group loss via adaptive group reweighting. Requires group labels during training. Expected to learn core features and achieve better worst-group accuracy. Included as the gold-standard robust training method that our geometric diagnostic should distinguish from ERM.

## Implementation Details

We use ResNet-50 architecture pretrained on ImageNet and fine-tuned on Waterbirds. Training uses SGD optimizer with learning rate 0.001, momentum 0.9, and batch size 128. Standard data augmentation includes random cropping and horizontal flipping. Models are trained for 45-100 epochs depending on convergence, with early stopping based on validation loss.

**Hessian Computation:** We compute the top-100 eigenvalues of the Hessian using Lanczos iteration to avoid full O(M³) eigendecomposition. For ResNet-50 with M = 25.6M parameters and N = 11,788 samples, Marchenko-Pastur bulk edge λ₊ is estimated via maximum likelihood fitting of the empirical eigenvalue distribution.

**Minority-Group Gradients:** Gradients are computed on balanced batches of 240 minority samples (groups 1 and 2) and averaged to obtain g_minority. Similarly, g_majority is computed from 4,555 majority samples.

**Compute Resources:** All experiments run on NVIDIA V100 GPUs. Hessian eigenvalue computation requires ~2 hours per model. Full training (100 epochs) requires ~6 hours. Total compute for all experiments: approximately 40 GPU-hours.

**Proof-of-Concept Mode:** Following the hypothesis validation protocol, we run key experiments (H-E1, H-M1) with 1 seed to establish feasibility and measure effect sizes. SGD trajectory analysis (H-M3) uses 3 seeds (42, 43, 44) for statistical validation.

## Evaluation Metrics

We use the following metrics to evaluate our geometric diagnostic and mechanism validation:

**Curvature Subspace Alignment A(θ):** Fraction of minority-gradient variance in the outlier subspace, defined as ||P_S_out g_minority||² / ||g_minority||². Measures spurious correlation exploitation geometrically. Primary diagnostic metric.

**Worst-Group Accuracy (WGA):** Minimum accuracy across the 4 subgroups. Measures robustness to distribution shift. Ground-truth phenotype metric for validation.

**Outlier Eigenvalue Count:** Number of eigenvalues exceeding Marchenko-Pastur bulk edge λ₊. Measures sharp curvature concentration.

**SGD Directional Bias:** Difference between bulk alignment and outlier alignment during training trajectories. Measures optimization dynamics preference for flat versus sharp directions.

**Statistical Significance:** We evaluate significance using two-sample t-tests for group comparisons (ERM vs DRO) and Spearman correlation for coupling tests. Significance threshold: p < 0.05. Effect sizes reported via Cohen's d for mean differences.
