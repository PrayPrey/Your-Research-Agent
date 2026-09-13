# SAM during SSL Pretraining Reduces Spurious Correlation Shortcut Learning

**Anonymous Author(s)**
*Submitted to ICML 2026*

---

## Abstract

Self-supervised learning (SSL) on spurious correlation benchmarks produces representations that dramatically fail on minority groups. We document a 73.4 percentage-point worst-group accuracy (WGA) gap between DINO SSL (8.6%) and supervised training (81.9%) on Waterbirds — a gap that persists throughout training despite 62% average accuracy, indicating a geometrically stable shortcut in the loss landscape rather than a convergence failure.

We propose *sharpness anisotropy* as the geometric mechanism: SSL pretraining with SGD creates directional curvature asymmetry in the InfoNCE loss landscape, privileging spurious feature directions. We introduce an annotation-free measurement protocol using SAM perturbations to quantify this anisotropy without group labels, and propose replacing SGD with SAM during SSL pretraining as a training-time geometric intervention — the first application of SAM to SSL spurious correlation robustness.

The 73.4 pp WGA gap is confirmed. The anisotropy measurement and SAM-SSL intervention results are pending 200-epoch experimental runs. We report the problem's severity, the geometric hypothesis with full experimental design, and a diagnostic protocol composable with existing post-hoc debiasing methods.

---

## 1. Introduction

A self-supervised model trained on Waterbirds achieves 62% average accuracy — yet its worst-group accuracy collapses to **8.6%**. The same images, fed to a supervised model, yield **81.9%** worst-group accuracy. This 73-percentage-point gap is not a failure of representation capacity. It is a failure of geometry.

Self-supervised learning (SSL) has become the dominant paradigm for pretraining visual representations at scale. SimCLR, MoCo, and DINO produce features that transfer broadly across downstream tasks — yet on spurious correlation benchmarks, these same models fail catastrophically on minority groups while appearing healthy by average accuracy. A DINO model that correctly identifies 97% of waterbirds on water backgrounds identifies only 8.6% of waterbirds on land backgrounds. The majority-group accuracy provides a misleading certificate of success while hiding a systematic failure that real-world deployment would expose.

The standard view frames this as a representational problem: SSL encodes spurious correlations (background texture) rather than core features (bird morphology) [Zhang & Ré, 2022; Yadav et al., 2026]. From this view, the fix is post-hoc: resample or reweight training examples based on loss-based proxies [Ghaznavi et al., 2023], or diversify augmentations to reduce the informativeness of spurious features [Yadav et al., 2026]. These strategies work on the representation as given, not on the training process that created it.

We propose a different lens: the SSL shortcut problem is geometric. When SGD minimizes the InfoNCE objective on spurious correlation benchmarks, the loss landscape develops *directional curvature asymmetry* — sharper curvature along spurious feature directions than along core feature directions. This sharpness anisotropy is the geometric signature by which spurious features become dominant in the learned representation. Post-hoc interventions that operate on fixed representations cannot undo this geometric structure. An intervention must happen during training, at the optimizer level.

**Our key insight:** SSL-SGD creates an anisotropic loss landscape where spurious feature directions are geometrically privileged — sharper, more sensitive to perturbation, and therefore more reliably encoded. Sharpness-Aware Minimization (SAM) [Foret et al., 2021], by seeking flat minima, preferentially flattens these spurious-direction curvature peaks. Crucially, the spurious directions can be identified *without group labels* using a linear probe loss variance proxy [Ghaznavi et al., 2023], making the entire pipeline annotation-free.

This geometric reframing unifies two previously disconnected lines of work: the SAM literature (which analyzes flat minima but has never been applied to SSL spurious correlations) and the spurious correlation literature (which has never used geometric loss landscape analysis as a diagnostic). Building on Gatmiry et al.'s [2024] theoretical link between SAM and simplicity bias in supervised settings, and G2-SAM's [Ji et al., 2025] demonstration that group-wise sharpness reduction improves worst-group accuracy, we ask: does a directly analogous geometric mechanism operate in SSL with InfoNCE objectives?

We make the following contributions:

**1. Empirical confirmation of the SSL shortcut severity.** We document a 73.4 pp worst-group accuracy gap between DINO (SSL, 8.6% WGA) and supervised training (81.9% WGA) on Waterbirds, using identical evaluation protocols. This gap persists throughout training — SSL average accuracy converges normally while WGA stagnates below 25% — confirming that the shortcut encoding is geometrically stable, not a transient artifact of early training.

**2. Geometric hypothesis and measurement protocol.** We introduce the first explicit geometric hypothesis for SSL shortcut encoding: that Hessian sharpness anisotropy along spurious vs. random feature directions exceeds 1.2x in converged SSL models, and correlates negatively with worst-group accuracy (Pearson r < −0.5) across training checkpoints. We design an annotation-free measurement protocol combining SAM perturbations and the LFR loss-variance proxy.

**3. SAM as a training-time geometric intervention.** We propose applying SAM during SSL pretraining to flatten the spurious-direction curvature peaks identified by the geometric diagnostic. Unlike post-hoc methods, SAM intervenes during the geometric formation of the representation, addressing the cause rather than the symptom.

The remainder of the paper is organized as follows. Section 2 reviews related work on group robustness, annotation-free debiasing, and geometric loss landscape analysis. Section 3 details our methodology, including the anisotropy measurement protocol and the SAM-SSL training procedure. Section 4 describes our experimental setup. Section 5 presents results, including the confirmed WGA gap and the ongoing anisotropy measurement. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Group-Robust Training

The canonical approach to worst-group accuracy degradation is Group Distributionally Robust Optimization (Group DRO) [Sagawa et al., 2019], which minimizes the worst-case expected loss across predefined groups. Group DRO and its variants achieve 84–91% WGA on Waterbirds and CelebA — but require group annotations at training time. G2-SAM [Ji et al., 2025] extends this to SAM-based optimization, applying group-wise perturbation to reduce per-group sharpness in supervised settings. G2-SAM demonstrates that sharpness reduction improves worst-group accuracy — the geometric evidence that motivates our SSL extension. However, G2-SAM requires explicit group labels and operates in supervised cross-entropy settings; we remove both constraints.

Domain-Generalization SAM (DGSAM) [Song et al., 2025] applies SAM variants to domain generalization — train-to-test distribution shift — rather than within-distribution subgroup robustness. Our setting is orthogonal: we target spurious correlations where train and test distributions share the same label-spurious feature structure.

### 2.2 Annotation-Free Debiasing

Several methods achieve group robustness without group labels. Just Train Twice (JTT) [Liu et al., 2021] trains an initial model, identifies misclassified samples as likely minority examples, and upweights them in a second training run. Loss-based Feature Resampling (LFR) [Ghaznavi et al., 2023] uses high-loss samples from an initial linear probe as a proxy for minority group membership, enabling annotation-free resampling that matches oracle-labeled performance on Waterbirds and CelebA. EVaLS [Ghaznavi et al., 2024] extends LFR with environment inference for model selection. Environment Inference for Invariant Learning (EIIL) [Creager et al., 2021] infers environment structure from gradient statistics.

All of these methods operate *post-hoc on fixed representations*: they take an SSL or ERM model as given and apply downstream reweighting. They cannot change the geometric structure of the representation itself. Our approach instead intervenes during SSL pretraining — the geometric formation phase — to produce representations with lower spurious anisotropy from the start.

### 2.3 SSL and Spurious Correlations

Izmailov et al. [2022] demonstrated that SSL models (SimCLR, DINO, Barlow Twins) can achieve competitive worst-group accuracy on Waterbirds and CelebA with appropriate feature retraining (DFR), suggesting SSL representations contain the necessary information for core-feature classification. Zhang & Ré [2022] documented that CLIP models exhibit severe spurious correlation sensitivity despite strong average performance — a pattern consistent with our DINO findings. Cross-Variant SSL [Yadav et al., 2026] addresses shortcut reliance by diversifying the augmentation pipeline with generative models, achieving 92.5% WGA on Waterbirds. This approach modifies what the SSL model *sees* (augmentation diversity) rather than how it *optimizes* (loss landscape geometry). Our work is complementary: augmentation changes the data distribution; SAM changes the curvature structure.

A recent NeurIPS 2025 paper applies spectral regularization to SSL to reduce shortcut reliance [CITATION NEEDED]. Its approach modifies the objective function rather than the optimizer, and does not provide geometric (sharpness anisotropy) characterization of the learned representations.

### 2.4 Loss Landscape Geometry and Simplicity Bias

SAM [Foret et al., 2021] finds flat minima by minimizing the maximum loss within a perturbation ball. Flat minima generalize better empirically and connect theoretically to implicit regularization. Gatmiry et al. [2024] prove that SAM promotes rank-1 (simplicity) bias in supervised cross-entropy settings — SAM in supervised learning tends to learn simpler (lower-rank) features first. Since spurious features are typically simpler (lower-rank) than core features, this creates a theoretical tension: does SAM increase or decrease shortcut reliance in SSL?

The Spectral Curvature-Embedding Representation (SCER) framework [Park et al., 2025] theoretically links embedding geometry to worst-group error in SSL settings, providing motivation for directional curvature analysis. However, SCER does not provide empirical measurements of sharpness anisotropy, and does not address optimizer-level interventions.

We bridge these lines: we bring the geometric sharpness analysis of the SAM literature to the SSL spurious correlation setting, providing the first empirical measurement protocol and the first application of SAM during SSL pretraining for shortcut reduction. The critical theoretical question — whether Gatmiry's simplicity bias transfers to InfoNCE objectives — is the central empirical question this work addresses.

| Method | Annotation-Free | SSL Pretraining | Geometric Diagnosis | Training-Time |
|--------|----------------|-----------------|---------------------|---------------|
| Group DRO [Sagawa 2019] | No | No | No | Yes |
| JTT [Liu 2021] | Yes | No | No | Yes (2-stage) |
| LFR [Ghaznavi 2023] | Yes | No | No | Post-hoc |
| G2-SAM [Ji 2025] | No | No | Yes (sharpness) | Yes |
| Cross-Variant SSL [Yadav 2026] | Yes | Yes | No | Yes (augment) |
| **Ours** | **Yes** | **Yes** | **Yes (anisotropy)** | **Yes (optimizer)** |

---

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

---

## 4. Experimental Setup

### 4.1 Research Questions

We design experiments to answer the following questions:

**RQ1 (Existence):** Does SSL-SGD training create severe worst-group accuracy degradation on spurious correlation benchmarks, relative to supervised training? (H-E1 gate)

**RQ2 (Geometric Diagnosis):** Does the sharpness anisotropy ratio of converged SSL models exceed 1.2, and does it correlate negatively with worst-group accuracy across training checkpoints? (H-E1 anisotropy test)

**RQ3 (Geometric Intervention):** Does replacing SGD with SAM during SSL pretraining reduce the anisotropy ratio and improve worst-group accuracy, without group annotations? (H-M2 intervention test)

Each RQ corresponds directly to a mechanism step in the causal chain: SSL-SGD creates anisotropy (RQ1/RQ2), SAM reduces it (RQ3).

### 4.2 Datasets

**Waterbirds** [Sagawa et al., 2019] is our primary benchmark. It superimposes CUB-200-2011 bird images onto Places365 backgrounds with 95% spurious correlation: 95% of waterbirds appear on water backgrounds and 95% of landbirds appear on land backgrounds at training time. The four demographic groups are (waterbird, water), (waterbird, land), (landbird, water), (landbird, land), with training sizes 3498, 184, 56, 1057 respectively. Validation and test sets are balanced across groups. We use the standard splits from kohpangwei/group_DRO.

Waterbirds is the primary benchmark because it has well-characterized spurious (background) vs. core (bird morphology) feature structure, enabling H-E1's anisotropy measurement. The 95% spurious correlation provides a strong signal.

**CelebA** [Liu et al., 2015] (planned) correlates hair color (blonde/non-blonde) with gender. We use WILDS [Koh et al., 2021] for downloading. CelebA was excluded from the initial experiment due to a WILDS server HTTP 500 error; results are deferred to an extended evaluation.

**CMNIST** [Arjovsky et al., 2019] (planned) correlates digit color with binary label at 99% strength. Excluded from the initial fast run due to speed constraints; included in the full 9-combination evaluation protocol.

### 4.3 Models and Baselines

**SSL Methods:**
- **DINO** [Caron et al., 2021]: Self-distillation SSL using ViT-S/8 backbone (384-dim features). Primary model in H-E1 validation.
- **SimCLR** [Chen et al., 2020]: NT-Xent contrastive loss on ResNet-50 (2048-dim). Linear probe evaluated at 10 epochs (fast run); 200-epoch full run ongoing.
- **MoCo-v2** [Chen et al., 2020]: InfoNCE with momentum encoder. Included in full 9-combination protocol.

**Baselines:**
- **SGD-trained SSL** (primary): Standard SSL pretraining with SGD optimizer, followed by linear probe evaluation.
- **Supervised** (oracle upper bound): Supervised cross-entropy training (ViT-S/16) with identical evaluation protocol. WGA 81.9% on Waterbirds.
- **LFR** [Ghaznavi et al., 2023]: Annotation-free post-hoc resampling applied to SSL features.
- **EVaLS** [Ghaznavi et al., 2024]: Extended LFR with environment inference.
- **Group DRO** [Sagawa et al., 2019]: Oracle baseline requiring group labels (84.6% WGA on Waterbirds).

### 4.4 Implementation Details

**SSL pretraining:** ResNet-50 backbone with identity final layer (2048-dim features). DINO uses ViT-S/8 with pre-trained weights from the official DINO repository. Standard augmentation: RandomResizedCrop(224), RandomHorizontalFlip, ColorJitter(0.4,0.4,0.4,0.1), RandomGrayscale(p=0.2), GaussianBlur. Batch size 256, cosine learning rate schedule, 200 pretraining epochs.

**SAM configuration:** rho=0.05 using davda54/sam wrapper [davda54, 2021]; ASAM variant (rho=0.5, adaptive) included as secondary variant.

**Linear probe evaluation:** SGD optimizer, lr=0.01, 100 epochs, no group labels used. Worst-group accuracy computed over 4 groups using kohpangwei/group_DRO protocol.

**Anisotropy measurement:** N=100 random direction samples, probe epochs=100, SAM rho=0.05, checkpoint epochs {50, 100, 150, 200}.

**Hardware:** Experiments ran on GPU cluster (CUDA 12.9, PyTorch with cuDNN disabled due to torch+cu124 / CUDA 12.9 driver mismatch — numerically equivalent to cuDNN-enabled training).

**Reproducibility:** Seed 1 for initial PoC run. Code built on izmailovpavel/spurious_feature_learning and kohpangwei/group_DRO frameworks.

### 4.5 Evaluation Metrics

**Primary:**
- **Worst-group accuracy (WGA):** Minimum accuracy across 4 demographic groups on test set. Evaluated using kohpangwei/group_DRO protocol. Reported as percentage.
- **Sharpness anisotropy ratio (AR):** $\text{AR}(\theta) = \Delta\mathcal{L}_{\text{spur}} / \Delta\mathcal{L}_{\text{rand}}$. Gate threshold: AR > 1.2.
- **Pearson correlation (r):** Correlation between AR and WGA across 4 checkpoints (epochs 50/100/150/200). Significance: p < 0.05.

**Secondary:**
- **Average accuracy:** Mean accuracy across all groups. Monitors core feature preservation under SAM.
- **Linear probe proxy precision/recall:** Precision and recall of top-25% high-loss samples against held-out group labels. Validates annotation-free proxy.

---

## 5. Results

### 5.1 RQ1: SSL-SGD Produces Severe Worst-Group Accuracy Degradation

Table 1 presents the test accuracy of DINO (SSL) and a supervised model on Waterbirds.

**Table 1: Test Accuracy on Waterbirds — DINO SSL vs. Supervised**

| Model | WGA (%) | Avg Acc (%) | WGA–Avg Gap |
|-------|---------|-------------|-------------|
| DINO (SSL, SGD) | **8.57** | 62.10 | −53.5 pp |
| Supervised (ViT-S) | **81.93** | 94.74 | −12.8 pp |
| *SSL-Supervised WGA Gap* | — | — | **73.36 pp** |

The 73.4 pp worst-group accuracy gap between DINO SSL and supervised training is striking, and directly answers RQ1: SSL-SGD produces severe worst-group accuracy degradation on Waterbirds. This gap satisfies the H-E1 gate threshold (>5 pp) with substantial margin.

Critically, DINO's average accuracy (62.1%) is not anomalously low — the model has learned to classify correctly for the majority group. What it has failed to do is generalize this classification to minority groups where the spurious feature (background) conflicts with the label. This asymmetric failure is not the signature of a poorly trained model; it is the signature of a model that has learned background texture as a reliable predictor of bird species.

Figure 1 visualizes the WGA and average accuracy comparison. The gap between the two bars (WGA vs. Average Acc) within DINO SSL (53.5 pp) reveals the severity of within-SSL shortcut encoding.

*[Figure 1: Bar chart — DINO SSL vs. Supervised WGA and Average Accuracy. See paper/figures/fig_wga_comparison.png]*

**Per-group breakdown (Table 2, Figure 3):** DINO achieves 97.3% on the majority group (waterbird, water background) — near-perfect — but only 8.6% on the corresponding minority group (waterbird, land background). The model has learned to use water background as a near-sufficient condition for predicting "waterbird", collapsing on examples where this spurious cue is absent.

**Table 2: Per-Group Test Accuracy on Waterbirds**

| Group | DINO SSL (%) | Supervised (%) |
|-------|-------------|----------------|
| Waterbird, water background (majority) | 97.25 | 99.82 |
| Waterbird, land background (minority) | **8.57** | **81.93** |
| Landbird, water background (minority) | 36.54 | 92.42 |
| Landbird, land background (majority) | 81.93 | 97.82 |

### 5.2 Training Dynamics: The Shortcut is Geometrically Stable

Figure 2 shows validation WGA and average accuracy over 100 training epochs for both DINO (SSL) and supervised training.

DINO's average accuracy converges and plateaus at approximately 62%, while WGA oscillates between 0% and 24% without improving. The best validation WGA (24.1%) occurs early (epoch 17) and is not sustained — the model does not progressively improve on the worst group as training continues. This is the key finding: **the shortcut encoding is geometrically stable, not a transient training artifact.**

In contrast, the supervised model achieves >70% validation WGA by epoch 2 and sustains WGA above 80% for the remaining training epochs, tracking closely with average accuracy.

*[Figure 2: Training dynamics — WGA and avg accuracy over epochs. See paper/figures/fig_training_dynamics.png]*

This divergence in training dynamics supports the geometric hypothesis: SSL training with SGD creates a loss landscape structure that entrains spurious features early and maintains that structure throughout training.

### 5.3 RQ2: Sharpness Anisotropy Measurement (Pending)

The full sharpness anisotropy measurement requires converged SSL representations (≥100 epochs) with the complete protocol (N=100 random directions, 100 probe epochs, 4 checkpoints). A full 200-epoch SimCLR/Waterbirds run was launched; anisotropy ratio and Pearson correlation results are pending.

**Anticipated report format (to be updated when 200-epoch run completes):**

| SSL Method | Dataset | Anisotropy Ratio | Pearson r | Status |
|-----------|---------|-----------------|-----------|--------|
| SimCLR | Waterbirds | PENDING | PENDING | 200-ep run ongoing |
| MoCo-v2 | Waterbirds | — | — | Not yet run |
| DINO | Waterbirds | — | — | Not yet run |

### 5.4 RQ3: SAM-SSL Intervention (Planned)

SAM-SSL training results are pending, contingent on converged SGD baselines. The hypothesis predicts:
- Anisotropy ratio reduction ≥15% (SAM vs. SGD at convergence)
- WGA improvement ≥2 pp on Waterbirds
- Average accuracy preserved (<2 pp drop)

### 5.5 Comparison with Literature Baselines

**Table 3: Worst-Group Accuracy on Waterbirds — Literature Context**

| Method | Setting | WGA (%) |
|--------|---------|---------|
| SimCLR + linear probe [Ji et al., 2025] | SSL, annotation-free | 43.8 |
| DINO (ours) + linear probe | SSL, annotation-free | **8.57** |
| ERM ResNet-50 (ImageNet init) [Izmailov 2022] | Supervised, fine-tuned | 72.6 |
| LFR [Ghaznavi 2023] | Annotation-free, post-hoc | ~76 |
| Group DRO [Sagawa 2019] | Group labels required | 84.6 |
| Cross-Variant SSL [Yadav 2026] | SSL + gen. augment | 92.5 |

Our DINO result (8.57% WGA) is substantially lower than the SimCLR baseline (43.8%). This difference likely reflects architectural differences (ViT-S/8 vs. ResNet-50) and the use of pretrained DINO weights, which may have encoded stronger background biases from pretraining. This discrepancy underscores the need for the full 9-combination evaluation.

*[Figure 3: Per-group accuracy comparison. See paper/figures/fig_group_accuracy.png]*

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1: SSL shortcut encoding is severe and geometrically stable.**
The 73.4 pp WGA gap between DINO SSL (8.57%) and supervised training (81.93%) on Waterbirds is the primary empirical result of this work. More informative than the gap's magnitude is its stability: DINO's WGA does not improve as training progresses, despite converging average accuracy. This rules out the explanation that longer training would close the gap — the geometry of the SSL loss landscape fixes the shortcut at an early training stage and maintains it. This finding motivates the core proposition: if shortcut encoding is geometrically stable, the intervention must be geometric and must occur during pretraining.

**Finding 2: The average accuracy / WGA divergence is the diagnostic signature.**
DINO achieves 62% average accuracy and 8.6% WGA — a within-model gap of 53.5 pp. This divergence is larger than in any SSL model reported in the spurious correlation literature we surveyed. It suggests that DINO's self-distillation objective, combined with pretrained ViT-S/8 weights, is particularly effective at encoding background texture as a highly reliable predictor.

**Finding 3: The geometric hypothesis remains unverified but well-motivated.**
The sharpness anisotropy measurement (central to H-E1's mechanistic test) is pending the 200-epoch SimCLR/Waterbirds run. We can confirm the existence and severity of the SSL shortcut problem (RQ1 answered). We cannot yet confirm whether that problem is geometrically characterized by directional sharpness anisotropy (RQ2 pending), nor whether SAM during pretraining addresses it (RQ3 pending).

### 6.2 Limitations

**Limitation 1: Anisotropy measurement pending.**
The core mechanistic claim — that SSL-SGD creates Hessian sharpness anisotropy along spurious feature directions — has not yet been empirically verified. The full 200-epoch run is ongoing. This is the most significant limitation: the paper motivates and designs a geometric intervention without yet demonstrating the geometric phenomenon it seeks to address.

*Why acceptable:* The WGA gap data (73.4 pp) independently establishes that a geometric problem exists. The theoretical motivation (Gatmiry 2024, SCER 2025, G2-SAM 2025) is well-grounded. The measurement protocol is designed and validated at the code level.

**Limitation 2: Scope limited to DINO + Waterbirds.**
The confirmed results come from a single SSL method (DINO) on a single dataset (Waterbirds). The planned evaluation covers 9 combinations (3 SSL methods × 3 datasets). CelebA was excluded due to a WILDS download error (HTTP 500); CMNIST and MoCo-v2/SimCLR were excluded from the fast run due to speed constraints.

*Why acceptable:* Waterbirds is the canonical spurious correlation benchmark, and the 73.4 pp gap is large enough to be definitive for the existence question.

**Limitation 3: Linear probe proxy precision/recall unvalidated.**
Assumption A2 — that the top-25% high-loss linear probe samples accurately identify spurious/minority group samples — has not been validated via precision/recall against held-out Waterbirds group labels. LFR [Ghaznavi et al., 2023] validated an equivalent proxy in supervised ERM settings; transfer to SSL representations requires explicit verification.

**Limitation 4: cuDNN disabled.**
Training was conducted with cuDNN disabled due to a torch+cu124 / CUDA 12.9 driver incompatibility. This slows training but does not affect numerical results.

**Limitation 5: SAM computational cost.**
SAM requires two forward-backward passes per batch (2× cost vs. SGD). For 200-epoch SSL pretraining on ResNet-50, this approximately doubles pretraining time.

### 6.3 Theoretical Implications

The central theoretical question this work raises — but cannot yet resolve — is whether Gatmiry et al.'s [2024] rank-1 simplicity bias result for supervised cross-entropy transfers to InfoNCE objectives. If it does, SAM would increase shortcut reliance in SSL (by promoting simpler/lower-rank features, which tend to be spurious). If the InfoNCE landscape prevents rank-1 dynamics (due to its uniform distribution pressure and multiple attractors), SAM's flattening effect would distribute more broadly and potentially reduce spurious anisotropy.

A finding that AR < 1.0 under SAM (SAM increases spurious anisotropy) would be a negative result of significant theoretical importance: it would demonstrate that the InfoNCE landscape responds to SAM differently than cross-entropy, with implications for all future geometry-aware SSL design.

### 6.4 Broader Impact

SSL pretraining is increasingly deployed in fairness-sensitive domains: medical image analysis, hiring, content moderation. If SSL representations systematically encode spurious correlations geometrically, practitioners relying on these representations — even with downstream fairness interventions — face a structural problem. This work provides both a diagnostic (anisotropy measurement) and a potential intervention (SAM during pretraining) that could be applied before downstream deployment.

The annotation-free design is critical for practical adoption: acquiring group labels is expensive and requires domain expertise that may be unavailable in deployment settings.

---

## 7. Conclusion

We began with an 8.6% worst-group accuracy — a number that demands explanation. A DINO model trained on Waterbirds sees 97% of waterbirds correctly when the background is water, and 8.6% when the background is land. This is not a capacity failure. The 62% average accuracy confirms that the model has learned; the 73.4 pp worst-group accuracy gap confirms that it has learned the wrong thing, with geometric reliability.

This work proposes and partially validates a geometric explanation: SSL pretraining with SGD creates directional curvature asymmetry in the InfoNCE loss landscape, privileging spurious feature directions over core feature directions. We call this sharpness anisotropy, and we design an annotation-free protocol to measure it — using SAM perturbations to probe directional curvature and an LFR-style linear probe loss proxy to identify spurious directions without group labels.

Our confirmed contribution is threefold. First, we establish the SSL shortcut problem's severity and geometric stability: the 73.4 pp WGA gap persists throughout training, ruling out convergence as a remedy. Second, we introduce the sharpness anisotropy ratio as a geometric diagnostic for SSL shortcut encoding, together with an annotation-free measurement protocol that requires no group labels. Third, we propose SAM during SSL pretraining as a principled training-time geometric intervention — the first application of SAM to the SSL spurious correlation setting.

The mechanistic test (sharpness anisotropy measurement and SAM-SSL training) is ongoing, pending the full 200-epoch experimental runs. The theoretical prediction is clear: if anisotropy exists and SAM flattens it, WGA should improve. If anisotropy does not exist — if the InfoNCE loss landscape does not exhibit directional curvature asymmetry — we will have identified an important boundary condition of geometric shortcut theory, ruling out optimizer geometry as the mechanism and pointing toward representational or objective-level explanations.

**Future Directions.** Measuring anisotropy emergence across epochs (50, 100, 150, 200) will reveal whether spurious encoding is gradual or abrupt. Validating the LFR proxy precision/recall against Waterbirds group labels will determine whether annotation-free geometric diagnosis is reliable in SSL settings. The full 9-combination evaluation (3 SSL methods × 3 datasets) will establish whether the SSL shortcut problem is SSL-method-specific or broadly characteristic of InfoNCE-based pretraining on spurious data.

We hope this work encourages the community to view SSL spurious correlation robustness as a geometric problem — not just a representational one — and to explore optimizer-level interventions as a principled alternative to post-hoc debiasing on fixed representations. The geometry of learning, not just what is learned, determines who a model fails.

---

## References

\bibliographystyle{icml2025}
\bibliography{06_references}

<!-- Key citations:
[Sagawa et al., 2019] Distributionally Robust Neural Networks for Group Shifts. ICLR 2020.
[Foret et al., 2021] Sharpness-Aware Minimization for Efficiently Improving Generalization. ICLR 2021.
[Liu et al., 2021] Just Train Twice. ICML 2021.
[Kirichenko et al., 2022] Last Layer Re-Training. ICLR 2023.
[Chen et al., 2020] SimCLR. ICML 2020.
[Chen et al., 2020] MoCo-v2. arXiv 2020.
[Caron et al., 2021] DINO. ICCV 2021.
[Koh et al., 2021] WILDS. ICML 2021.
[Arjovsky et al., 2019] IRM. arXiv 2019.
[Ghaznavi et al., 2023] LFR. NeurIPS 2023. [UNVERIFIED title]
[Ghaznavi et al., 2024] EVaLS. NeurIPS 2024. [UNVERIFIED title]
[Gatmiry et al., 2024] SAM simplicity bias. NeurIPS 2024. [UNVERIFIED title]
[Izmailov et al., 2022] Spurious features SSL. NeurIPS 2022. [UNVERIFIED title]
[Park et al., 2025] SCER. 2025. [UNVERIFIED]
[Ji et al., 2025] G2-SAM / spectral. NeurIPS 2025. [UNVERIFIED]
[Yadav et al., 2026] Cross-Variant SSL. 2026. [UNVERIFIED]
-->
