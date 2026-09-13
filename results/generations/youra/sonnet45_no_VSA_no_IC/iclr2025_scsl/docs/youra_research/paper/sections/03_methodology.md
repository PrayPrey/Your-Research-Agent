# 3. Methodology

## 3.1 Gradient Abnormality Detection Pipeline

We extend GAIA [@chen2023exploring] from out-of-distribution (OOD) detection to minority group detection within in-distribution data. The pipeline operates in three stages:

**Stage 1: GradCAM Extraction**  
For test sample $x_i$ with predicted class $c$, compute gradient of class score $S_c$ w.r.t. final convolutional layer activations $A^k$ (channel $k$):
$$\alpha_c^k = \frac{1}{Z} \sum_{i,j} \frac{\partial S_c}{\partial A_{i,j}^k}$$
where $Z$ is the spatial dimension. Gradient-weighted activation map:
$$L_{\text{GradCAM}} = \text{ReLU}\left(\sum_k \alpha_c^k A^k\right)$$

**Stage 2: GAIA-Z Computation (Zero-Deflation)**  
Measure gradient sparsity via near-zero element ratio:
$$\text{GAIA-Z}(x) = \frac{|\{g_{ij} : |g_{ij}| < \epsilon\}|}{|G|}$$
where $G = \nabla_A S_c$ is the gradient tensor, $\epsilon = 10^{-5}$ is the near-zero threshold. Higher GAIA-Z indicates denser gradients (more abnormal). Minority samples expected to have lower GAIA-Z (fewer near-zero gradients) due to gradient scattering.

**Stage 3: Statistical Testing**  
Split test samples by group membership: $\mathcal{M}$ (minority), $\mathcal{J}$ (majority). Compute:
- **Divergence:** $\Delta = |\text{mean}(\text{GAIA-Z}_\mathcal{M}) - \text{mean}(\text{GAIA-Z}_\mathcal{J})|$
- **Significance:** Welch's t-test (unequal variance), $H_0: \mu_\mathcal{M} = \mu_\mathcal{J}$
- **Effect size:** Cohen's d = $\frac{\mu_\mathcal{M} - \mu_\mathcal{J}}{\sqrt{\frac{\sigma_\mathcal{M}^2 + \sigma_\mathcal{J}^2}{2}}}$

**Detection criterion:** Divergence ≥0.2, p<0.01, Cohen's d≥0.8 (large effect).

## 3.2 Causal Mechanism: 4-Step Chain

Our hypothesis proposes gradient abnormality arises causally from spurious conflict:

**Step 1:** Model learns spurious shortcut (e.g., 90% background-class correlation in training).  
**Step 2:** Minority samples create conflict — spurious feature (waterbird on land) contradicts expected shortcut (waterbird on water).  
**Step 3:** Conflict manifests as gradient scattering — attribution attempts to explain prediction using both spurious region (background) and core region (bird), producing dense, noisy gradients.  
**Step 4:** Higher GAIA-Z score detects scattering, enabling minority group identification.

**Falsifiable prediction (Step 2 validation):** If spurious mismatch *causes* abnormality, then background swap (minority → majority background) should reduce GAIA-Z by ≥30%.

## 3.3 Background Augmentation Causality Test

To validate Step 2 (conflict → scattering), we perform an intervention:

**Procedure:**
1. Select minority samples $\{x_i\}_{i \in \mathcal{M}}$ with mismatched backgrounds
2. Apply background swap: $\tilde{x}_i = \text{SegFormer}(x_i, \text{bg}_{\text{majority}})$  
   (Replace minority background with majority-group background using semantic segmentation)
3. Compute GAIA-Z before ($z_i$) and after ($\tilde{z}_i$) augmentation
4. Paired t-test: $H_0: \text{mean}(z - \tilde{z}) = 0$

**Success criterion:** Mean reduction ≥30%, p<0.05, Cohen's d≥0.5 (medium effect).

**Rationale:** Causal intervention removes spurious conflict → gradient scattering should decrease. Non-causal explanation (e.g., sample complexity) would not change after background swap.

## 3.4 Spatial Gradient Regularization

### 3.4.1 Algorithm Overview

We propose a training-time regularization that penalizes gradients in spurious regions identified via GradCAM difference maps:

**Input:** Training batch $(x, y)$, model $f_\theta$  
**Output:** Loss $L = L_{\text{CE}} + \lambda \cdot L_{\text{spatial}}$

**Step 1: GradCAM Difference Map**  
Compute per-class GradCAM maps:
$$M_c = \text{GradCAM}(x, c) \quad \forall c \in \{0,1\}$$
Difference map highlights spurious regions:
$$M_{\text{diff}} = |M_{\hat{y}} - M_{y}|$$
where $\hat{y}$ is predicted class, $y$ is true label. High values indicate regions where predicted class attribution differs from true class.

**Step 2: Percentile Thresholding**  
Binary mask isolates top-$p$ spurious pixels:
$$\mathcal{S} = \{(i,j) : M_{\text{diff}}(i,j) \geq \text{percentile}(M_{\text{diff}}, p)\}$$
Default: $p = 75$ (top 25% most spurious). **Note (Assumption A2):** This choice is not empirically validated — grid search over $p \in \{50, 75, 90\}$ deferred to full experiment.

**Step 3: Gradient Variance Penalty**  
Measure gradient variance in spurious region:
$$L_{\text{spatial}} = \text{Var}\left(\nabla_x f_\theta(x) \odot \mathbb{1}_\mathcal{S}\right)$$
where $\odot$ is element-wise product, $\mathbb{1}_\mathcal{S}$ is the binary mask. Higher variance in spurious regions indicates scattered gradients.

**Step 4: Adaptive Lambda Scaling**  
Adjust penalty strength based on worst-group accuracy on validation set:
$$\lambda_{t+1} = \begin{cases}
\lambda_t \cdot 1.2 & \text{if } \text{WGA}_{\text{val}} < \text{target} \\
\lambda_t \cdot 0.8 & \text{if } \text{WGA}_{\text{val}} > \text{target} + 5\% \\
\lambda_t & \text{otherwise}
\end{cases}$$
Initial: $\lambda_0 = 0.01$. Prevents under/over-regularization.

### 3.4.2 Theoretical Justification

**Mechanism:** Spurious gradients are dense (high variance) due to conflict between core and spurious features. Penalizing variance in spurious regions forces the model to rely on core features, reducing spurious shortcut.

**Why percentile normalization?** Absolute thresholding biases toward majority samples (majority gradients dominate distribution). Percentile thresholding selects top-$p$ spurious pixels *per sample*, avoiding majority bias.

**Why adaptive lambda?** Fixed penalty may be too weak (no WGA improvement) or too strong (catastrophic accuracy drop). Adaptive scaling maintains balance.

### 3.4.3 Hyperparameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| $\lambda_0$ | 0.01 | Conservative initial penalty (avoid catastrophic forgetting) |
| Percentile $p$ | 75 | Top quartile (empirically effective on MNIST PoC) |
| Scaling factor | 1.2 / 0.8 | Gradual adjustment (20% steps) |
| WGA target | 75% | Dataset-dependent (Waterbirds: 75%, MNIST: 70%) |

**Grid search (deferred):** Full experiment tests $\lambda_0 \in \{0.001, 0.01, 0.1\}$ and $p \in \{50, 75, 90\}$ (9 configs).

## 3.5 Implementation Details

**Framework:** PyTorch 2.1+ (required for H100 sm_90 support)  
**GradCAM library:** pytorch-grad-cam (pip install grad-cam)  
**SegFormer:** HuggingFace transformers (semantic segmentation for background swap)  
**Statistical tests:** scipy.stats (Welch's t-test, Pearson correlation)  

**Reproducibility:** All experiments use seed=42. Code released upon publication.

## 3.6 Assumptions

**A1 (GradCAM Validity):** Minority samples correctly classified ≥60% (else GradCAM may not localize to bird region).  
**A2 (Percentile Normalization):** 75th percentile avoids majority bias (lower percentiles may include non-spurious regions).  
**A3 (Causal Attribution):** Gradient scattering *caused* by spurious conflict, not sample complexity. Validated via background swap test.  
**A4 (Regularization Mechanism):** Spatial penalty reduces spurious reliance, not just smooths gradients. Validated via WGA improvement in PoC.  

**Assumption validation:** A1 checked via minority accuracy measurement (h-m-integrated Experiment 3). A3 validated via causality test (Section 5.3). A4 validated via MNIST PoC (Section 5.5).
