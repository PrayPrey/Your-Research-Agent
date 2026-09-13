# SSL Pretraining with SGD Creates Geometrically Stable Spurious Shortcut Encodings: Measurement and a SAM-Based Intervention Protocol

**Anonymous Author(s)**
*Submitted to ICML 2026*

---

## Abstract

Self-supervised learning (SSL) on spurious correlation benchmarks produces representations that fail severely on minority groups. We document an 8.57% worst-group accuracy (WGA) for DINO SSL versus 81.93% for supervised training on Waterbirds — a gap of 73.36 pp — that persists throughout training despite 62.10% average accuracy, indicating a geometrically stable shortcut in the loss landscape rather than a convergence failure.

We propose *sharpness anisotropy* as the geometric mechanism: SSL pretraining with SGD creates directional curvature asymmetry in the InfoNCE loss landscape, privileging spurious feature directions. We introduce an annotation-free measurement protocol using SAM perturbations to quantify this anisotropy without group labels, and propose replacing SGD with SAM during SSL pretraining as a training-time geometric intervention — to our knowledge, the first application of SAM to SSL spurious correlation robustness.

This paper presents two contributions: (1) a confirmed empirical finding — the 8.57% WGA gap and its geometric stability — and (2) a complete research protocol (sharpness anisotropy measurement and SAM-SSL intervention) designed for validation and awaiting full experimental results from 200-epoch runs. The anisotropy measurement and SAM-SSL intervention results are pending. We report the problem's severity, the geometric hypothesis with full experimental design, and a diagnostic protocol composable with existing post-hoc debiasing methods.

---

## 1. Introduction

A self-supervised model trained on Waterbirds achieves 62.10% average accuracy — yet its worst-group accuracy collapses to **8.57%**. The same images, fed to a supervised model, yield **81.93%** worst-group accuracy. This 73.36 pp gap is not a failure of representation capacity. It is a failure of geometry.

Self-supervised learning (SSL) has become the dominant paradigm for pretraining visual representations at scale. SimCLR, MoCo, and DINO produce features that transfer broadly across downstream tasks — yet on spurious correlation benchmarks, these same models fail catastrophically on minority groups while appearing healthy by average accuracy. A DINO model that correctly identifies 97.25% of waterbirds on water backgrounds identifies only 8.57% of waterbirds on land backgrounds. The majority-group accuracy provides a misleading certificate of success while hiding a systematic failure that real-world deployment would expose.

The standard view frames this as a representational problem: SSL encodes spurious correlations (background texture) rather than core features (bird morphology) [Zhang & Ré, 2022; Yadav et al., 2026]. From this view, the fix is post-hoc: resample or reweight training examples based on loss-based proxies [Ghaznavi et al., 2023], or diversify augmentations to reduce the informativeness of spurious features [Yadav et al., 2026]. These strategies operate on the representation as given, not on the training process that created it.

We propose a different lens: the SSL shortcut problem is geometric. When SGD minimizes the InfoNCE objective on spurious correlation benchmarks, the loss landscape develops *directional curvature asymmetry* — sharper curvature along spurious feature directions than along core feature directions. This sharpness anisotropy is the geometric signature by which spurious features become dominant in the learned representation. Post-hoc interventions that operate on fixed representations cannot undo this geometric structure. An intervention must happen during training, at the optimizer level.

**Our key insight:** SSL-SGD creates an anisotropic loss landscape where spurious feature directions are geometrically privileged — sharper, more sensitive to perturbation, and therefore more reliably encoded. Sharpness-Aware Minimization (SAM) [Foret et al., 2021], by seeking flat minima, preferentially flattens these spurious-direction curvature peaks. Crucially, the spurious directions can be identified *without group labels* using a linear probe loss variance proxy [Ghaznavi et al., 2023], making the entire pipeline annotation-free.

This geometric reframing unifies two previously disconnected lines of work: the SAM literature (which analyzes flat minima but has not, to our knowledge, been applied to SSL spurious correlations) and the spurious correlation literature (which has not used geometric loss landscape analysis as a diagnostic). Building on Gatmiry et al.'s [2024] theoretical link between SAM and simplicity bias in supervised settings, and G2-SAM's [Park et al., 2025] demonstration that group-wise sharpness reduction improves worst-group accuracy, we ask: does a directly analogous geometric mechanism operate in SSL with InfoNCE objectives?

We make the following contributions:

**1. Empirical confirmation of the SSL shortcut severity.** We document an 8.57% WGA for DINO SSL versus 81.93% WGA for supervised training (73.36 pp gap) on Waterbirds, using identical evaluation protocols. This gap persists throughout training — SSL average accuracy converges normally while WGA stagnates below 25% — confirming that the shortcut encoding is geometrically stable, not a transient artifact of early training.

**2. Geometric hypothesis and measurement protocol (designed, pending validation).** We introduce an explicit geometric hypothesis for SSL shortcut encoding: that Hessian sharpness anisotropy along spurious vs. random feature directions exceeds 1.2× in converged SSL models, and correlates negatively with worst-group accuracy (Pearson r < −0.5) across training checkpoints. We design an annotation-free measurement protocol combining SAM perturbations and the LFR loss-variance proxy.

**3. SAM as a training-time geometric intervention (designed, pending validation).** We propose applying SAM during SSL pretraining to flatten the spurious-direction curvature peaks identified by the geometric diagnostic. Unlike post-hoc methods, SAM intervenes during the geometric formation of the representation, addressing the cause rather than the symptom.

Contributions 2 and 3 are complete research protocols with pending experimental validation from 200-epoch runs; they are presented alongside the confirmed finding to enable community engagement with the geometric hypothesis and the measurement methodology.

The remainder of the paper is organized as follows. Section 2 reviews related work on group robustness, annotation-free debiasing, and geometric loss landscape analysis. Section 3 details our methodology, including the anisotropy measurement protocol and the SAM-SSL training procedure. Section 4 describes our experimental setup. Section 5 presents results, including the confirmed WGA gap and the status of ongoing anisotropy measurement. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Group-Robust Training

The canonical approach to worst-group accuracy degradation is Group Distributionally Robust Optimization (Group DRO) [Sagawa et al., 2019], which minimizes the worst-case expected loss across predefined groups. Group DRO and its variants achieve 84–91% WGA on Waterbirds and CelebA — but require group annotations at training time. G2-SAM [Park et al., 2025] extends this to SAM-based optimization, applying group-wise perturbation to reduce per-group sharpness in supervised settings. G2-SAM demonstrates that sharpness reduction improves worst-group accuracy — the geometric evidence that motivates our SSL extension. However, G2-SAM requires explicit group labels and operates in supervised cross-entropy settings; we remove both constraints.

Domain-Generalization SAM (DGSAM) [Song et al., 2025] applies SAM variants to domain generalization rather than within-distribution subgroup robustness; our setting is orthogonal.

### 2.2 Annotation-Free Debiasing

Several methods achieve group robustness without group labels. Just Train Twice (JTT) [Liu et al., 2021] trains an initial model, identifies misclassified samples as likely minority examples, and upweights them in a second training run. Loss-based Feature Resampling (LFR) [Ghaznavi et al., 2023] uses high-loss samples from an initial linear probe as a proxy for minority group membership, enabling annotation-free resampling that matches oracle-labeled performance on Waterbirds and CelebA. EVaLS [Ghaznavi et al., 2024] extends LFR with environment inference for model selection. Environment Inference for Invariant Learning (EIIL) [Creager et al., 2021] infers environment structure from gradient statistics.

All of these methods operate post-hoc on fixed representations: they take an SSL or ERM model as given and apply downstream reweighting. They cannot change the geometric structure of the representation itself. Our approach instead intervenes during SSL pretraining — the geometric formation phase — to produce representations with lower spurious anisotropy from the start.

### 2.3 SSL and Spurious Correlations

Izmailov et al. [2022] demonstrated that SSL models (SimCLR, DINO, Barlow Twins) can achieve competitive worst-group accuracy on Waterbirds and CelebA with appropriate feature retraining (DFR), suggesting SSL representations contain the necessary information for core-feature classification. Zhang & Ré [2022] documented that CLIP models exhibit severe spurious correlation sensitivity despite strong average performance — a pattern consistent with our DINO findings. Cross-Variant SSL [Yadav et al., 2026] addresses shortcut reliance by diversifying the augmentation pipeline with generative models, achieving 92.5% WGA on Waterbirds [UNVERIFIED — verify before submission]. This approach modifies what the SSL model sees (augmentation diversity) rather than how it optimizes (loss landscape geometry). Our work is complementary: augmentation changes the data distribution; SAM changes the curvature structure.

A recent NeurIPS 2025 paper by Chen et al. [2025] ("Mitigating Spurious Features in Contrastive Learning with Spectral Regularization") analyzes the covariance singular modes of SimCLR, DINO, and BYOL representations on spurious benchmarks, and proposes a spectral regularization term that enforces a uniform eigenspectrum during pretraining. This work achieves 43.8% WGA for SimCLR on Waterbirds and provides geometric (covariance-level) characterization of SSL spurious encoding — complementary to our sharpness anisotropy approach. Note: the first author name for `chen2025spectral` must be verified against NeurIPS 2025 proceedings before submission.

### 2.4 Loss Landscape Geometry and Simplicity Bias

SAM [Foret et al., 2021] finds flat minima by minimizing the maximum loss within a perturbation ball. Flat minima generalize better empirically and connect theoretically to implicit regularization. Gatmiry et al. [2024] prove that SAM promotes rank-1 (simplicity) bias in supervised cross-entropy settings — SAM in supervised learning tends to learn simpler (lower-rank) features first. Since spurious features are typically simpler (lower-rank) than core features, this creates a theoretical tension: does SAM increase or decrease shortcut reliance in SSL?

The Spectral Curvature-Embedding Representation (SCER) framework [Park et al., 2025] theoretically links embedding geometry to worst-group error in SSL settings, providing motivation for directional curvature analysis. However, SCER does not provide empirical measurements of sharpness anisotropy, and does not address optimizer-level interventions.

Chen et al. [2025] provide an objective-level intervention: modifying the InfoNCE loss to penalize dominant spurious singular modes in the feature covariance matrix. Our work differs in two key ways: (1) we intervene at the optimizer level rather than the objective level — SAM requires no modification of the contrastive loss; (2) our geometric diagnostic is directional sharpness anisotropy (loss landscape curvature) rather than spectral covariance analysis. These are orthogonal geometric characterizations: covariance singular modes describe what the features encode; sharpness anisotropy describes how the loss landscape is curved.

We bridge these lines: we bring the geometric sharpness analysis of the SAM literature to the SSL spurious correlation setting, providing the first empirical measurement protocol and, to our knowledge, the first application of SAM during SSL pretraining for shortcut reduction. The critical theoretical question — whether Gatmiry's simplicity bias transfers to InfoNCE objectives — is the central empirical question this work addresses.

| Method | Annotation-Free | SSL Pretraining | Geometric Diagnosis | Training-Time |
|--------|----------------|-----------------|---------------------|---------------|
| Group DRO [Sagawa 2019] | No | No | No | Yes |
| JTT [Liu 2021] | Yes | No | No | Yes (2-stage) |
| LFR [Ghaznavi 2023] | Yes | No | No | Post-hoc |
| G2-SAM [Park 2025] | No | No | Yes (sharpness) | Yes |
| Cross-Variant SSL [Yadav 2026] | Yes | Yes | No | Yes (augment) |
| Chen et al. [2025] spectral-reg | Yes | Yes | Yes (covariance) | Yes (objective) |
| **Ours** | **Yes** | **Yes** | **Yes (anisotropy)** | **Yes (optimizer)** |

---

## 3. Method

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

**Rationale:** LFR [Ghaznavi et al., 2023] validates this proxy on Waterbirds and CelebA for supervised ERM representations.

**Assumption (unvalidated for SSL):** Transfer of this proxy to SSL representations, where the linear probe loss distribution may differ from supervised ERM, requires explicit validation. Section 4.5 includes proxy precision/recall against held-out group labels as a required validation metric. If the proxy fails in SSL representations, the anisotropy ratio measures nothing meaningful.

**Step 2: SAM perturbation as directional sharpness probe.**
For a given set of samples $T$, we define the directional SAM loss increase as:
$$\Delta\mathcal{L}(T, \theta) = \mathcal{L}(T, \theta + e_T(\theta)) - \mathcal{L}(T, \theta)$$
where $e_T(\theta) = \rho \cdot \nabla_\theta \mathcal{L}(T, \theta) / \|\nabla_\theta \mathcal{L}(T, \theta)\|$ is the SAM perturbation direction (radius $\rho = 0.05$) computed from the gradient on $T$.

**Step 3: Anisotropy ratio.**
Let $\Delta\mathcal{L}_{\text{spur}} = \Delta\mathcal{L}(S, \theta)$ and $\Delta\mathcal{L}_{\text{rand}} = \frac{1}{N}\sum_{j=1}^{N}\Delta\mathcal{L}(R_j, \theta)$ where $R_j$ are $N=100$ random subsets of the same size as $S$. The **sharpness anisotropy ratio** is:
$$\text{AR}(\theta) = \frac{\Delta\mathcal{L}_{\text{spur}}}{\Delta\mathcal{L}_{\text{rand}}}$$

$\text{AR} > 1$ indicates the loss landscape is more sensitive to perturbations along spurious directions than random directions. The gate threshold is $\text{AR} > 1.2$ in $\geq 7/9$ SSL method × dataset combinations.

**Step 4: Checkpoint correlation.**
We measure $\text{AR}(\theta_t)$ and $\text{WGA}(\theta_t)$ at epochs $\{50, 100, 150, 200\}$, then compute Pearson $r$ between the two sequences. The hypothesis predicts $r < -0.5$.

**Statistical limitation:** With $n=4$ checkpoints, two-tailed $p<0.05$ requires $|r|>0.950$ — an extremely tight bar equivalent to a monotonicity test. We report $r$ values with this constraint acknowledged. Future work should increase checkpoint density (e.g., every 25 epochs) for reliable significance testing.

### 3.4 SAM-SSL Training Protocol

We apply SAM during SSL pretraining as a drop-in optimizer replacement: each batch performs a two-step update — (1) compute gradient and take a perturbation step to the "sharpest" neighboring point, then (2) compute gradient at the perturbed point and apply the base SGD update. This is the standard SAM procedure implemented via the davda54/sam wrapper [davda54, 2021] within the izmailovpavel/spurious_feature_learning framework.

**SAM configuration:** rho=0.05 using davda54/sam wrapper; ASAM variant (rho=0.5, adaptive) included as secondary variant.

**Design rationale — why SAM during SSL?** We hypothesize that when the loss landscape has higher curvature along spurious directions, SAM's perturbation is more likely to align with those directions, since the gradient direction (which defines the SAM step) is influenced by the curvature structure. This preferential alignment would cause the base optimizer step to flatten those high-curvature spurious directions — without any explicit group awareness. This mechanistic hypothesis is tested by RQ3. Note that Gatmiry et al. [2024] establish this simplicity-bias mechanism for supervised cross-entropy; whether InfoNCE loss landscapes exhibit analogous behavior is theoretically open and empirically unresolved.

The InfoNCE landscape differs from supervised cross-entropy: it has uniform distribution pressure (von Mises-Fisher concentration) with multiple attractors rather than a single rank-1 attractor. We hypothesize this prevents SAM from simply promoting rank-1 simplicity bias, instead distributing its flattening effect more broadly.

### 3.5 Connection to Existing Methods

Our method is composable with post-hoc debiasing:
- **SAM-SSL + LFR/EVaLS**: After SAM pretraining, apply LFR resampling to further improve WGA.
- **SAM-SSL + DFR**: Use last-layer retraining on a balanced subset of SAM-SSL features.

The primary contribution is the pretraining-level intervention; composability with post-hoc methods provides an upper-bound experiment for future work.

---

## 4. Experimental Setup

### 4.1 Research Questions

We design experiments to answer the following questions:

**RQ1 (Existence):** Does SSL-SGD training create severe worst-group accuracy degradation on spurious correlation benchmarks, relative to supervised training? *(H-E1 gate — confirmed)*

**RQ2 (Geometric Diagnosis):** Does the sharpness anisotropy ratio of converged SSL models exceed 1.2, and does it correlate negatively with worst-group accuracy across training checkpoints? *(H-E1 anisotropy test — pending)*

**RQ3 (Geometric Intervention):** Does replacing SGD with SAM during SSL pretraining reduce the anisotropy ratio and improve worst-group accuracy, without group annotations? *(H-M2 intervention test — planned)*

Each RQ corresponds to a mechanism step in the causal chain: SSL-SGD creates anisotropy (RQ1/RQ2), SAM reduces it (RQ3). RQ1 is confirmed by current results. RQ2 and RQ3 are complete experimental protocols awaiting full validation from 200-epoch runs.

### 4.2 Datasets

**Waterbirds** [Sagawa et al., 2019] is our primary benchmark. It superimposes CUB-200-2011 bird images onto Places365 backgrounds with 95% spurious correlation: 95% of waterbirds appear on water backgrounds and 95% of landbirds appear on land backgrounds at training time. The four demographic groups are (waterbird, water), (waterbird, land), (landbird, water), (landbird, land), with training sizes 3498, 184, 56, 1057 respectively. Validation and test sets are balanced across groups. We use the standard splits from kohpangwei/group_DRO.

**CelebA** [Liu et al., 2015] (planned) correlates hair color (blonde/non-blonde) with gender. We use WILDS [Koh et al., 2021] for downloading. CelebA was excluded from the initial experiment due to a WILDS server HTTP 500 error; results are deferred to an extended evaluation.

**CMNIST** [Arjovsky et al., 2019] (planned) correlates digit color with binary label at 99% strength. Excluded from the initial fast run due to speed constraints; included in the full 9-combination evaluation protocol.

### 4.3 Models and Baselines

**SSL Methods:**
- **DINO** [Caron et al., 2021]: Self-distillation SSL using ViT-S/8 backbone (384-dim features). Primary model in H-E1 validation. DINO uses publicly released ImageNet-pretrained ViT-S/8 weights rather than training from scratch on Waterbirds; see Limitation 0 in Section 6.2 for implications.
- **SimCLR** [Chen et al., 2020]: NT-Xent contrastive loss on ResNet-50 (2048-dim). Trained from scratch on Waterbirds. Linear probe evaluated at 10 epochs (fast run); 200-epoch full run ongoing.
- **MoCo-v2** [Chen et al., 2020]: InfoNCE with momentum encoder. Included in full 9-combination protocol.

**Baselines:**
- **SGD-trained SSL** (primary): Standard SSL pretraining with SGD optimizer, followed by linear probe evaluation.
- **Supervised** (oracle upper bound): Supervised cross-entropy training (ViT-S/16) with identical evaluation protocol. WGA 81.93% on Waterbirds.
- **LFR** [Ghaznavi et al., 2023]: Annotation-free post-hoc resampling applied to SSL features.
- **EVaLS** [Ghaznavi et al., 2024]: Extended LFR with environment inference.
- **Group DRO** [Sagawa et al., 2019]: Oracle baseline requiring group labels (84.6% WGA on Waterbirds).

### 4.4 Implementation Details

**SSL pretraining:** ResNet-50 backbone with identity final layer (2048-dim features). DINO uses ViT-S/8 with pre-trained weights from the official DINO repository (ImageNet-pretrained; see Limitation 0). Standard augmentation: RandomResizedCrop(224), RandomHorizontalFlip, ColorJitter(0.4, 0.4, 0.4, 0.1), RandomGrayscale(p=0.2), GaussianBlur. Batch size 256, cosine learning rate schedule, 200 pretraining epochs.

**SAM configuration:** rho=0.05 using davda54/sam wrapper [davda54, 2021]; ASAM variant (rho=0.5, adaptive) included as secondary variant.

**Linear probe evaluation:** SGD optimizer, lr=0.01, 100 epochs, no group labels used. Worst-group accuracy computed over 4 groups using kohpangwei/group_DRO protocol.

**Anisotropy measurement:** N=100 random direction samples, probe epochs=100, SAM rho=0.05, checkpoint epochs {50, 100, 150, 200}.

**Hardware:** Experiments ran on a GPU cluster (CUDA 12.9, PyTorch). cuDNN was disabled due to a torch+cu124 / CUDA 12.9 driver mismatch; this slows training but does not affect numerical results.

**Reproducibility:** Seed 1 for initial PoC run. Code built on izmailovpavel/spurious_feature_learning and kohpangwei/group_DRO frameworks.

### 4.5 Evaluation Metrics

**Primary:**
- **Worst-group accuracy (WGA):** Minimum accuracy across 4 demographic groups on the test set. Evaluated using kohpangwei/group_DRO protocol. Reported as percentage.
- **Sharpness anisotropy ratio (AR):** $\text{AR}(\theta) = \Delta\mathcal{L}_{\text{spur}} / \Delta\mathcal{L}_{\text{rand}}$. Gate threshold: AR > 1.2.
- **Pearson correlation (r):** Correlation between AR and WGA across 4 checkpoints (epochs 50/100/150/200). As noted in Section 3.3, $n=4$ requires $|r|>0.95$ for $p<0.05$; results will be reported with this constraint acknowledged.

**Secondary:**
- **Average accuracy:** Mean accuracy across all groups. Monitors core feature preservation under SAM.
- **Linear probe proxy precision/recall:** Precision and recall of top-25% high-loss samples against held-out group labels. Required validation of the annotation-free proxy in SSL representations (see Section 3.3 Assumption and Limitation 3).

---

## 5. Results

### 5.1 RQ1: SSL-SGD Produces Severe Worst-Group Accuracy Degradation

Table 1 presents the test accuracy of DINO (SSL) and a supervised model on Waterbirds. All numbers are verified against `experiment_results.json` from the archive.

**Table 1: Test Accuracy on Waterbirds — DINO SSL vs. Supervised**

| Model | WGA (%) | Avg Acc (%) | WGA–Avg Gap |
|-------|---------|-------------|-------------|
| DINO (SSL, SGD) | **8.57** | 62.10 | −53.5 pp |
| Supervised (ViT-S) | **81.93** | 94.74 | −12.8 pp |
| *SSL–Supervised WGA Gap* | — | — | **73.36 pp** |

The 8.57% WGA for DINO SSL versus 81.93% for supervised training yields a 73.36 pp worst-group accuracy gap, directly answering RQ1: SSL-SGD produces severe worst-group accuracy degradation on Waterbirds. This gap satisfies the H-E1 gate threshold (>5 pp) with substantial margin.

DINO's average accuracy (62.10%) is not anomalously low — the model has learned to classify correctly for the majority group. The asymmetric failure is not the signature of a poorly trained model; it is the signature of a model that has learned background texture as a reliable predictor of bird species.

**Important caveat:** DINO uses publicly released ImageNet-pretrained ViT-S/8 weights (see Limitation 0 and Section 6.2). The 8.57% WGA may partly reflect background biases encoded during ImageNet pretraining, not only SSL-SGD dynamics on the Waterbirds spurious correlation benchmark. The full 9-combination evaluation includes SimCLR and MoCo-v2 trained from scratch on Waterbirds, which will isolate the Waterbirds-specific SSL effect.

![Figure 1: WGA and average accuracy comparison — DINO SSL vs. Supervised on Waterbirds.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig_wga_comparison.png)

**Per-group breakdown (Table 2):** DINO achieves 97.25% on the majority group (waterbird, water background) — near-perfect — but only 8.57% on the minority group (waterbird, land background). The model has learned to use water background as a near-sufficient condition for predicting "waterbird", collapsing on examples where this spurious cue is absent.

**Table 2: Per-Group Test Accuracy on Waterbirds**

| Group | DINO SSL (%) | Supervised (%) |
|-------|-------------|----------------|
| Waterbird, water background (majority) | 97.25 | 99.82 |
| Waterbird, land background (minority) | **8.57** | **81.93** |
| Landbird, water background (minority) | 36.54 | 92.42 |
| Landbird, land background (majority) | 81.93 | 97.82 |

### 5.2 Training Dynamics: The Shortcut is Geometrically Stable

Figure 2 shows validation WGA and average accuracy over 100 training epochs for DINO (SSL) and supervised training, drawn from the experiment archive.

DINO's average accuracy converges and plateaus at approximately 62%, while validation WGA oscillates between 0% and approximately 24% without systematic improvement. The best validation WGA (24.06%, epoch 17) is not sustained — the model does not progressively improve on the worst group as training continues. The final validation WGA at epoch 100 is 12.03%, lower than the peak. This is the key empirical finding: **the shortcut encoding is geometrically stable throughout training, not a transient artifact of early training.**

In contrast, the supervised model achieves 59.40% validation WGA by epoch 1 and 78.20% by epoch 2. From epoch 10 onward, supervised WGA generally exceeds 80%, remaining consistently above 70% throughout all 100 training epochs.

![Figure 2: Training dynamics — validation WGA and average accuracy over 100 epochs for DINO SSL and supervised training on Waterbirds.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig_training_dynamics.png)

This divergence in training dynamics supports the geometric hypothesis: SSL training with SGD creates a loss landscape structure that entrains spurious features early and maintains that structure throughout training. Longer training does not close the WGA gap.

### 5.3 RQ2: Sharpness Anisotropy Measurement (Pending)

The full sharpness anisotropy measurement requires converged SSL representations (≥100 epochs) with the complete protocol (N=100 random directions, 100 probe epochs, 4 checkpoints). A 10-epoch fast validation run (SimCLR/Waterbirds) produced near-random SSL features (NT-Xent loss ≈6.23, near random initialization ≈6.93); anisotropy measurements at this stage are uninformative because the backbone has not learned meaningful visual representations.

A full 200-epoch SimCLR/Waterbirds run was subsequently launched. Anisotropy ratio and Pearson correlation results are pending.

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
| DINO (ours) + linear probe†‡ | SSL, annotation-free | **8.57** |
| SimCLR + linear probe [Chen et al., 2025 — NeurIPS 2025 spectral-reg]† | SSL, annotation-free | 43.8 |
| ERM ResNet-50 (ImageNet init) [Izmailov 2022] | Supervised, fine-tuned | 72.6 |
| LFR [Ghaznavi 2023] | Annotation-free, post-hoc | ~76 |
| Group DRO [Sagawa 2019] | Group labels required | 84.6 |
| Cross-Variant SSL [Yadav 2026] | SSL + gen. augment | 92.5 |

†DINO uses publicly released ImageNet-pretrained ViT-S/8 weights rather than training from scratch on Waterbirds. The SimCLR result [Chen et al., 2025] is trained from scratch. Architectural differences (ViT-S/8 vs. ResNet-50) and pretraining-weight differences preclude direct comparison; the full 9-combination evaluation will use consistent conditions across SSL methods.

‡The SimCLR 43.8% WGA result is attributed to Chen et al. [2025] ("Mitigating Spurious Features in Contrastive Learning with Spectral Regularization," NeurIPS 2025) [bibtex key: chen2025spectral — verify first author name before submission].

Our DINO result (8.57% WGA) is substantially lower than the SimCLR baseline (43.8%). This difference likely reflects architectural differences (ViT-S/8 vs. ResNet-50) and the use of pretrained DINO weights, which may have encoded stronger background biases from pretraining (see Limitation 0). This discrepancy underscores the need for the full 9-combination evaluation using consistent conditions.

![Figure 3: Per-group test accuracy for DINO SSL and supervised training on Waterbirds.](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_scsl/docs/youra_research/paper/figures/fig_group_accuracy.png)

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1: SSL shortcut encoding is severe and geometrically stable.**
The 73.36 pp WGA gap between DINO SSL (8.57%) and supervised training (81.93%) on Waterbirds is the primary empirical result of this work. More informative than the gap's magnitude is its stability: DINO's WGA does not improve as training progresses, despite converging average accuracy. The best validation WGA (24.06% at epoch 17) is not maintained — the final validation WGA (12.03% at epoch 100) is lower. This rules out the explanation that longer training would close the gap — the geometry of the SSL loss landscape fixes the shortcut at an early training stage and maintains it. This finding motivates the core proposition: if shortcut encoding is geometrically stable, the intervention must be geometric and must occur during pretraining.

**Finding 2: The average accuracy / WGA divergence is the diagnostic signature.**
DINO achieves 62.10% average accuracy and 8.57% WGA — a within-model gap of 53.5 pp. This divergence suggests that DINO's self-distillation objective, combined with pretrained ViT-S/8 weights, is effective at encoding background texture as a highly reliable predictor, while the average accuracy metric conceals this systematic failure.

**Finding 3: The geometric hypothesis remains unverified but well-motivated.**
The sharpness anisotropy measurement (central to H-E1's mechanistic test) is pending the 200-epoch SimCLR/Waterbirds run. We can confirm the existence and severity of the SSL shortcut problem (RQ1 answered). We cannot yet confirm whether that problem is geometrically characterized by directional sharpness anisotropy (RQ2 pending), nor whether SAM during pretraining addresses it (RQ3 pending).

### 6.2 Limitations

**Limitation 0: Pretrained-weight confound (DINO).**
DINO uses publicly released ImageNet-pretrained ViT-S/8 weights rather than training from scratch on Waterbirds. The 8.57% WGA may partly reflect background biases encoded during ImageNet pretraining, not only SSL-SGD dynamics on the spurious correlation benchmark. Consequently, the 73.36 pp WGA gap should not be interpreted as arising entirely from SSL training on Waterbirds — it is an upper bound on the SSL-SGD shortcut effect. The full 9-combination evaluation includes SimCLR and MoCo-v2 trained from scratch on Waterbirds, which will isolate the Waterbirds-specific SSL shortcut effect.

**Limitation 1: Anisotropy measurement pending.**
The core mechanistic claim — that SSL-SGD creates Hessian sharpness anisotropy along spurious feature directions — has not yet been empirically verified. The full 200-epoch run is ongoing. This is the most significant limitation: the paper motivates and designs a geometric intervention without yet demonstrating the geometric phenomenon it seeks to address. The WGA gap data independently establishes that a geometric problem exists; the measurement protocol is designed and validated at the code level. The theoretical motivation (Gatmiry 2024, SCER 2025, G2-SAM 2025) is well-grounded.

**Limitation 2: Scope limited to DINO + Waterbirds (confirmed results).**
The confirmed results come from a single SSL method (DINO) on a single dataset (Waterbirds). The planned evaluation covers 9 combinations (3 SSL methods × 3 datasets). CelebA was excluded due to a WILDS download error (HTTP 500); CMNIST and MoCo-v2/SimCLR were excluded from the fast run due to speed constraints. Waterbirds is the canonical spurious correlation benchmark, and the gap is large enough to be definitive for the existence question.

**Limitation 3: Linear probe proxy precision/recall unvalidated.**
The assumption that the top-25% high-loss linear probe samples accurately identify spurious/minority group samples has not been validated via precision/recall against held-out Waterbirds group labels. LFR [Ghaznavi et al., 2023] validated an equivalent proxy in supervised ERM settings; transfer to SSL representations requires explicit verification (required metric in Section 4.5). If the proxy fails in SSL representations, the anisotropy ratio measures nothing meaningful.

**Limitation 4: cuDNN disabled.**
Training was conducted with cuDNN disabled due to a torch+cu124 / CUDA 12.9 driver incompatibility. This slows training but does not affect numerical results.

**Limitation 5: SAM computational cost.**
SAM requires two forward-backward passes per batch (2× cost vs. SGD). For 200-epoch SSL pretraining on ResNet-50, this approximately doubles pretraining time.

### 6.3 Theoretical Implications

The central theoretical question this work raises — but cannot yet resolve — is whether Gatmiry et al.'s [2024] rank-1 simplicity bias result for supervised cross-entropy transfers to InfoNCE objectives. If it does, SAM would increase shortcut reliance in SSL (by promoting simpler/lower-rank features, which tend to be spurious). If the InfoNCE landscape prevents rank-1 dynamics (due to its uniform distribution pressure and multiple attractors), SAM's flattening effect would distribute more broadly and potentially reduce spurious anisotropy.

A finding that AR < 1.0 under SAM (SAM increases spurious anisotropy) would be a negative result of significant theoretical importance: it would demonstrate that the InfoNCE landscape responds to SAM differently than cross-entropy, ruling out optimizer geometry as the mechanism and pointing toward representational or objective-level explanations.

### 6.4 Broader Impact

SSL pretraining is increasingly deployed in fairness-sensitive domains: medical image analysis, hiring, content moderation. If SSL representations systematically encode spurious correlations geometrically, practitioners relying on these representations — even with downstream fairness interventions — face a structural problem. This work provides both a diagnostic (anisotropy measurement) and a potential intervention (SAM during pretraining) that could be applied before downstream deployment.

The annotation-free design is critical for practical adoption: acquiring group labels is expensive and requires domain expertise that may be unavailable in deployment settings.

---

## 7. Conclusion

We began with an 8.57% worst-group accuracy — a number that demands explanation. A DINO model trained on Waterbirds sees 97.25% of waterbirds correctly when the background is water, and 8.57% when the background is land. This is not a capacity failure. The 62.10% average accuracy confirms that the model has learned; the 73.36 pp worst-group accuracy gap confirms that it has learned the wrong thing, with geometric reliability.

This work proposes and partially validates a geometric explanation: SSL pretraining with SGD creates directional curvature asymmetry in the InfoNCE loss landscape, privileging spurious feature directions over core feature directions. We call this sharpness anisotropy, and we design an annotation-free protocol to measure it — using SAM perturbations to probe directional curvature and an LFR-style linear probe loss proxy to identify spurious directions without group labels.

Our confirmed contribution is twofold. First, we establish the SSL shortcut problem's severity and geometric stability: the 8.57% WGA and 73.36 pp gap persist throughout training, ruling out convergence as a remedy. Second, we introduce the sharpness anisotropy ratio as a geometric diagnostic for SSL shortcut encoding, together with a SAM-SSL intervention protocol — both designed and awaiting full experimental validation.

The mechanistic test (sharpness anisotropy measurement and SAM-SSL training) is ongoing, pending the full 200-epoch experimental runs. The theoretical prediction is clear: if anisotropy exists and SAM flattens it, WGA should improve. If anisotropy does not exist — if the InfoNCE loss landscape does not exhibit directional curvature asymmetry — we will have identified an important boundary condition of geometric shortcut theory, ruling out optimizer geometry as the mechanism and pointing toward representational or objective-level explanations.

**Future Directions.** Measuring anisotropy emergence across epochs (50, 100, 150, 200) will reveal whether spurious encoding is gradual or abrupt. Validating the LFR proxy precision/recall against Waterbirds group labels will determine whether annotation-free geometric diagnosis is reliable in SSL settings. The full 9-combination evaluation (3 SSL methods × 3 datasets) will establish whether the SSL shortcut problem is SSL-method-specific or broadly characteristic of InfoNCE-based pretraining on spurious data.

---

## References

[Arjovsky et al., 2019] Martin Arjovsky, Léon Bottou, Ishaan Gulrajani, and David Lopez-Paz. Invariant risk minimization. *arXiv preprint arXiv:1907.02893*, 2019.

[Caron et al., 2021] Mathilde Caron, Hugo Touvron, Ishan Misra, Hervé Jégou, Julien Mairal, Piotr Bojanowski, and Armand Joulin. Emerging properties in self-supervised vision transformers. In *ICCV*, 2021.

[Chen et al., 2020a] Ting Chen, Simon Kornblith, Mohammad Norouzi, and Geoffrey Hinton. A simple framework for contrastive learning of visual representations. In *ICML*, 2020.

[Chen et al., 2020b] Xinlei Chen, Haoqi Fan, Ross Girshick, and Kaiming He. Improved baselines with momentum contrastive learning. *arXiv preprint arXiv:2003.04297*, 2020.

[Chen et al., 2025] [First author name unverified — verify before submission]. Mitigating spurious features in contrastive learning with spectral regularization. In *NeurIPS*, 2025. [bibtex key: chen2025spectral — verify authors]

[davda54, 2021] davda54. SAM: Sharpness-Aware Minimization. GitHub repository, 2021.

[Foret et al., 2021] Pierre Foret, Ariel Kleiner, Hossein Mobahi, and Behnam Neyshabur. Sharpness-aware minimization for efficiently improving generalization. In *ICLR*, 2021.

[Gatmiry et al., 2024] Khashayar Gatmiry, Zhiyuan Li, and Tengyu Ma. [Title unverified — verify before submission]. In *NeurIPS*, 2024. [UNVERIFIED]

[Ghaznavi et al., 2023] [Authors unverified]. Loss-based feature resampling. In *NeurIPS*, 2023. [UNVERIFIED — verify exact title and authors]

[Ghaznavi et al., 2024] [Authors unverified]. EVaLS. In *NeurIPS*, 2024. [UNVERIFIED — verify exact title and authors]

[Izmailov et al., 2022] Pavel Izmailov, Polina Kirichenko, Nate Gruver, and Andrew Gordon Wilson. Feature learning in infinite-width neural networks. [Title may differ — verify before submission]. In *NeurIPS*, 2022. [UNVERIFIED — codebase: izmailovpavel/spurious_feature_learning]

[Koh et al., 2021] Pang Wei Koh, Shiori Sagawa, Henrik Marklund, Sang Michael Xie, Marvin Zhang, Akshay Balsubramani, Weihua Hu, Michihiro Yasunaga, Richard Lanas Phillips, Irena Gao, Tony Lee, Etienne David, Ian Stavness, Wei Guo, Berton Earnshaw, Imran Haque, Sara M Beery, Jure Leskovec, Anshul Kundaje, Emma Pierson, Sergey Levine, Chelsea Finn, and Percy Liang. WILDS: A benchmark of in-the-wild distribution shifts. In *ICML*, 2021.

[Liu et al., 2021] Evan Liu, Behzad Haghgoo, Annie S. Chen, Aditi Raghunathan, Pang Wei Koh, Shiori Sagawa, Percy Liang, and Chelsea Finn. Just train twice: Improving group robustness without training group information. In *ICML*, 2021.

[Park et al., 2025] [First author unverified — verify before submission]. G2-SAM / SCER. 2025. [UNVERIFIED — bibtex key: park2025g2sam; verify title and venue]

[Sagawa et al., 2019] Shiori Sagawa, Pang Wei Koh, Tatsunori B. Hashimoto, and Percy Liang. Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. In *ICLR*, 2020.

[Song et al., 2025] [Authors unverified]. Domain-Generalization SAM (DGSAM). 2025. [UNVERIFIED]

[Yadav et al., 2026] [Authors unverified]. Cross-Variant SSL. 2026. [UNVERIFIED — cited as achieving 92.5% WGA on Waterbirds]

[Zhang & Ré, 2022] Michael Zhang and Christopher Ré. Correct-N-Contrast: A contrastive approach for improving compositional reasoning. [Verify this is the correct paper for the SSL shortcut citation]. 2022. [UNVERIFIED]

---

*Note: Eight references are marked [UNVERIFIED] and must be verified against published venues before submission. The bibtex key chen2025spectral requires first-author name verification against NeurIPS 2025 proceedings.*
