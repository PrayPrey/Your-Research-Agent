## 3. Methodology

### 3.1 Overview

Our geometric hypothesis has two parts: (1) SSL-SGD creates sharpness anisotropy in the loss landscape, privileging spurious feature directions; (2) SAM applied during SSL pretraining flattens this anisotropy and improves worst-group accuracy. The methodology follows these parts: first, a diagnostic protocol to measure anisotropy annotation-free; second, a training protocol where SAM replaces SGD during SSL pretraining.

**Connecting to the key insight:** If the loss landscape is geometrically biased toward spurious features, then the SAM perturbation — which finds the most loss-increasing direction from the current weights — will naturally find spurious-feature directions more often. This directional preference is measurable, and SAM's flat-minima objective directly counteracts it.

### 3.2 Problem Setup

Let $f_\theta: \mathcal{X} \to \mathbb{R}^d$ be an SSL-pretrained encoder (ResNet-50 backbone, $d=2048$). The dataset $\mathcal{D}$ contains images from a spurious correlation benchmark with underlying group structure $(y, c) \in \{0,1\}^2$, where $y$ is the core label and $c$ is the spurious attribute, correlated at strength $p \approx 0.95$ in training data. Group labels are used only for evaluation, never during training or pretraining.

Let $\mathcal{L}_{SSL}(\theta)$ be the InfoNCE contrastive loss (NT-Xent for SimCLR, InfoNCE for MoCo-v2, self-distillation for DINO). Worst-group accuracy is:
$$\text{WGA} = \min_{g \in \mathcal{G}} \text{Acc}_g(\theta)$$
where $\mathcal{G} = \{(y,c) : y,c \in \{0,1\}\}$ defines four demographic groups.

### 3.3 Sharpness Anisotropy Measurement (Annotation-Free)

We measure directional sharpness anisotropy using three components:

**Step 1: Linear probe and spurious direction proxy.**
Given a pretrained encoder $f_\theta$, we train a linear probe $h: \mathbb{R}^d \to \mathbb{R}^K$ on the downstream classification task. The per-sample probe loss $\ell_i = \ell(h(f_\theta(x_i)), y_i)$ serves as an annotation-free proxy for spurious correlation reliance: samples in the top-25% by loss are likely minority group members whose spurious feature conflicts with their label [Ghaznavi et al., 2023]. Let $S = \{i : \ell_i > Q_{0.75}(\ell)\}$ denote this spurious proxy set.

**Rationale:** LFR [Ghaznavi et al., 2023] validates this proxy on Waterbirds and CelebA for supervised ERM representations. We apply the same proxy to SSL representations, extending its annotation-free property to the contrastive setting.

**Step 2: SAM perturbation as directional sharpness probe.**
For a given set of samples $T$, we define the directional SAM loss increase as:
$$\Delta\mathcal{L}(T, \theta) = \mathcal{L}(T, \theta + e_T(\theta)) - \mathcal{L}(T, \theta)$$
where $e_T(\theta) = \rho \cdot \nabla_\theta \mathcal{L}(T, \theta) / \|\nabla_\theta \mathcal{L}(T, \theta)\|$ is the SAM perturbation direction (radius $\rho = 0.05$) computed from gradient on $T$.

**Rationale:** $e_T(\theta)$ is the normalized gradient direction with respect to samples $T$ — it points in the direction of maximum loss increase from the current weights restricted to the subspace defined by $T$'s gradient. This is exactly the SAM first-step direction from davda54/sam [davda54, 2021].

**Step 3: Anisotropy ratio.**
Let $\Delta\mathcal{L}_{\text{spur}} = \Delta\mathcal{L}(S, \theta)$ and $\Delta\mathcal{L}_{\text{rand}} = \frac{1}{N}\sum_{j=1}^{N}\Delta\mathcal{L}(R_j, \theta)$ where $R_j$ are $N=100$ random subsets of the same size as $S$. The **sharpness anisotropy ratio** is:
$$\text{AR}(\theta) = \frac{\Delta\mathcal{L}_{\text{spur}}}{\Delta\mathcal{L}_{\text{rand}}}$$

$\text{AR} > 1$ indicates the loss landscape is more sensitive to perturbations along spurious directions than random directions. Our gate threshold is $\text{AR} > 1.2$ in $\geq 7/9$ SSL method × dataset combinations.

**Step 4: Checkpoint correlation.**
We measure $\text{AR}(\theta_t)$ and $\text{WGA}(\theta_t)$ at epochs $\{50, 100, 150, 200\}$, then compute Pearson $r$ between the two sequences. The hypothesis predicts $r < -0.5$: as the model trains further (increasing AR), WGA decreases due to spurious feature entrenchment.

### 3.4 SAM-SSL Training Protocol

We apply SAM during SSL pretraining with a two-step update per batch:

```
Algorithm 1: SAM-SSL Training
Input: Dataset X, SSL encoder f_θ, SAM radius ρ
For each batch B:
  1. Compute gradient: g = ∇_θ L_SSL(B, θ)
  2. First step (SAM): θ̂ = θ + ρ · g / ||g||
  3. Compute gradient at perturbed point: ĝ = ∇_θ L_SSL(B, θ̂)
  4. Second step (update): θ = θ - lr · ĝ   (via base SGD)
  5. Restore: (handled by base optimizer step)
```

Implementation uses the davda54/sam wrapper [davda54, 2021] as a drop-in replacement for the SGD optimizer within standard SSL training loops (izmailovpavel/spurious_feature_learning framework).

**Design rationale — why SAM during SSL?** SAM seeks parameters $\theta$ where the loss is jointly low and flat within a $\rho$-ball. When the loss landscape has higher curvature along spurious directions, SAM's perturbation will more frequently step in spurious directions to find the worst-case loss — and then the base optimizer step will flatten those directions. This preferential flattening of high-curvature directions, without any explicit group awareness, is the mechanism we hypothesize reduces spurious anisotropy.

The InfoNCE landscape differs from supervised cross-entropy: it has uniform distribution pressure (von Mises-Fisher concentration) with multiple attractors rather than a single rank-1 attractor. We hypothesize this prevents SAM from simply promoting rank-1 simplicity bias (as in Gatmiry 2024 for supervised cross-entropy), instead distributing its flattening effect more broadly. This is the central theoretical claim that our experiments test.

### 3.5 Connection to Existing Methods

Our method is composable with post-hoc debiasing:
- **SAM-SSL + LFR/EVaLS**: After SAM pretraining, apply LFR resampling to further improve WGA.
- **SAM-SSL + DFR**: Use last-layer retraining on balanced subset of SAM-SSL features.

The primary contribution is the pretraining-level intervention; composability with post-hoc methods provides an upper-bound experiment for future work.
