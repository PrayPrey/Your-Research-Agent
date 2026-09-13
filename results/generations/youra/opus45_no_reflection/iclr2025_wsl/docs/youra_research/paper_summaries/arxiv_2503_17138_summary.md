---
source_paper: "arxiv_2503_17138.md"
generated_at: "2026-08-18T23:56:01.489188"
model: "openai/gpt-5.2"
summary_chars: 16183
---

# Structure Is Not Enough: Leveraging Behavior for Neural Network Weight Reconstruction

## Key Metadata
- **Authors:** Léo Meynent et al.
- **Year:** 2025
- **Venue:** ICLR Workshop on Neural Network Weights as a New Data Modality (2025)
- **Core Contribution:** Shows that adding a *behavioral* (function-matching) loss to weight-space autoencoder training—alongside standard Euclidean weight reconstruction—substantially improves reconstructed and generated models’ *task accuracy*, not just weight MSE.

## Section Summaries

### Abstract
The weights of neural networks (NNs) have recently gained prominence as a new
data modality in machine learning, with applications ranging from accuracy and
hyperparameter prediction to representation learning or weight generation. One
approach to leverage NN weights involves training autoencoders (AEs), using con-
trastive and reconstruction losses. This allows such models to be applied to a wide
variety of downstream tasks, and they demonstrate strong predictive performance
and low reconstruction error. However, despite the low reconstruction error, these
AEs reconstruct NN models with deteriorated performance compared to the orig-
inal ones, limiting their usability with regard to model weight generation. In this
paper, we identify a limitation of weight-space AEs, specifically highlighting that a
structural loss, that uses the Euclidean distance between original and reconstructed
weights, fails to capture some features critical for reconstructing high-performing
models. We analyze the addition of a behavioral loss for training AEs in weight
space, where we compare the output of the reconstructed model with that of the
original one, given some common input. We show a strong synergy between struc-
tural and behavioral signals, leading to increased performance in all downstream
tasks evaluated, in particular NN weights reconstruction and generation.

### Introduction & Motivation
Weight-space learning treats trained neural network parameters as structured data, enabling representation learning, model property prediction, and even *weight generation*. Prior weight-space autoencoders (AEs) (e.g., hyper-representations / SANE) achieve low *structural* reconstruction error (e.g., low MSE between original and decoded weights) and strong performance on discriminative downstream tasks, yet their reconstructed (and generated) weights often yield models with substantially degraded task accuracy. The paper argues that Euclidean proximity in parameter space is not sufficient to preserve function: (i) MSE-trained undercomplete AEs bias toward coarse/smoothed reconstructions, (ii) weight-space distances are confounded by neuron permutations and other equivalences, and (iii) small parameter perturbations can move a solution into a region with poor generalization. The key idea is therefore to train weight-space AEs using not only *structure* (weight-space MSE) but also *behavior* (matching model outputs on unlabeled queries), and to show that combining these signals markedly improves reconstruction and generation fidelity.

### Methodology
The paper extends weight-space autoencoder training by adding a *behavioral* reconstruction objective that matches the **function** implemented by a reconstructed network, not just its raw parameters.

**Setup / notation.** A model zoo contains \(k\) trained networks with parameters \(\theta_j \in \Theta \subset \mathbb{R}^p\). A weight-space AE (with learnable parameters \(w\)) maps weights to reconstructed weights \(\hat{\theta}_j = g_w(\theta_j)\). Each set of weights defines a predictor \(f_\theta: \mathcal{X} \to \mathcal{Y}\) (classification logits / outputs).

**Behavioral loss (new).** Given \(n\) query inputs \(\{x_i\}_{i=1}^n\) (unlabeled images), compare outputs of original and reconstructed models:
\[
L_B = \frac{1}{2kn}\sum_{j=1}^{k}\sum_{i=1}^{n}\left\lVert f_{\hat{\theta}_j}(x_i) - f_{\theta_j}(x_i)\right\rVert_2^2.
\tag{1}
\]
This is explicitly *not* a supervised loss to ground-truth labels; it is a function-matching loss (“match teacher behavior”).

**Structural and contrastive losses (prior SANE / hyper-representations).**
- Structural loss (parameter MSE):
\[
L_S = \frac{1}{2k}\sum_{j=1}^{k}\left\lVert \hat{\theta}_j - \theta_j\right\rVert_2^2.
\tag{4}
\]
- Contrastive loss \(L_C\): NTXent (Sohn, 2016) on latent embeddings, using *behavior-preserving weight permutations* as augmentations (as in SANE). The goal is to learn discriminative “hyper-representations” useful for downstream prediction.

**Composite objective (proposed).** Prior work used
\[
L_{C+S}=\gamma L_C + (1-\gamma)L_S. \tag{2}
\]
They add \(L_B\) as a second reconstructive term:
\[
L = \gamma L_C + (1-\gamma)\Big(\beta L_S + (1-\beta)L_B\Big),
\quad \gamma,\beta\in[0,1].
\tag{3}
\]
Interpretation: \(\gamma\) trades off contrastive vs reconstruction; \(\beta\) trades off structural vs behavioral reconstruction.

**Architecture / representation model (SANE backbone).** They use SANE (Schürholt et al., 2024): weights are **tokenized** into a sequence (token length reported as 289), embedded with dimension 64, producing a compression ratio of 4.52. The encoder outputs one latent representation per token; a projection head maps embeddings for \(L_C\); the decoder consumes embeddings to reconstruct the full model’s weights. Unlike some SANE variants that operate on token windows, they **feed and reconstruct an entire model at once**, which they later note as a scalability limitation.

**Training details / hyperparameters (as reported in the extracted text).**
- Train on the train split of each model zoo; evaluate on held-out test models.
- Use model checkpoints from zoo training epochs \(\{20,30,40,50\}\) as training data for the AE (increasing intra-zoo diversity across training time).
- Loss weights: when using both contrastive and reconstruction, set \(\gamma=0.05\) (matching SANE). When combining \(L_S\) and \(L_B\), set \(\beta=0.1\) (chosen via validation sweep; Appendix D.6).
- Behavioral queries for \(L_B\): for each AE batch, sample \(n_{\text{queries}}=256\) images from the **same training set** used to train the model zoo.

**Why behavioral loss changes learning (gradient analysis).**
Structural gradient:
\[
\frac{\partial L_S}{\partial w} = \frac{1}{k}\sum_{j=1}^{k}\Delta\theta_j^\top \frac{\partial \hat{\theta}_j}{\partial w},\quad
\Delta\theta_j=\hat{\theta}_j-\theta_j.
\tag{5}
\]
Behavioral gradient:
\[
\frac{\partial L_B}{\partial w}
=
\frac{1}{kn}\sum_{j=1}^{k}\sum_{i=1}^{n}
\Big(f_{\hat{\theta}_j}(x_i)-f_{\theta_j}(x_i)\Big)^\top
\frac{\partial f_{\hat{\theta}_j}(x_i)}{\partial \hat{\theta}_j}
\frac{\partial \hat{\theta}_j}{\partial w}.
\tag{6}
\]
Assuming \(\hat{\theta}_j\approx \theta_j\), Taylor expand:
\[
f_{\hat{\theta}_j}(x_i)\approx f_{\theta_j}(x_i)+J_{\theta_j}(x_i)\Delta\theta_j,
\quad
J_{\theta_j}(x_i)=\frac{\partial f_{\theta_j}(x_i)}{\partial \theta_j}.
\tag{7}
\]
This yields an approximate form:
\[
\frac{\partial L_B}{\partial w}\approx
\frac{1}{k}\sum_{j=1}^{k}\Delta\theta_j^\top F_j \frac{\partial \hat{\theta}_j}{\partial w},
\quad
F_j=\frac{1}{n}\sum_{i=1}^{n}J_{\theta_j}(x_i)^\top J_{\hat{\theta}_j}(x_i).
\tag{9–10}
\]
So \(L_B\) effectively *reweights* parameter errors by a sensitivity/alignment matrix \(F_j\) derived from Jacobians on query inputs—emphasizing weight directions that matter for the network’s outputs, not all parameters equally. This motivates the central claim: **Euclidean reconstruction ignores functional saliency**, while behavioral matching injects information about which discrepancies are functionally damaging.

**Query distribution matters.** Because \(L_B\) is defined on a chosen query set, the AE learns to preserve behavior on that input distribution. The authors warn that out-of-domain or random queries can force matching in regions where the zoo models’ behavior is “ill-defined,” potentially harming in-domain fidelity (further explored in Appendix D.3 per the text).

### Experiments & Results
**Model zoos / data.** Experiments use three CNN model zoos (Schürholt et al., 2022c) trained on:
- **SVHN** (Netzer et al., 2011)
- **CIFAR-10** (Krizhevsky, 2009)
- **EuroSAT** (Helber et al., 2019)

Each zoo contains **1,200 models**, all sharing the *same architecture*, trained on the *same dataset*, using a common hyperparameter grid (details in Appendix A). Each model has **10,853 parameters** and is trained for **50 epochs**. Zoo models are split into **80% / 5% / 15%** train/val/test partitions (disjoint by model instance). Hyper-representation AEs are trained on the zoo train split, and evaluation is on the zoo test split (unseen models), using zoo checkpoints from epochs \(\{20,30,40,50\}\).

**Methods compared (loss variants).**
- **Baseline (SANE):** \(L_C \oplus L_S\) with \(\gamma=0.05\), \(\beta=1\) (i.e., no behavioral term).
- **Proposed:** \(L_C \oplus L_S \oplus L_B\) with \(\gamma=0.05\), \(\beta=0.1\).
- Additional diagnostic variants discussed around Fig. 2: using \(L_S\) only, \(L_B\) only, and combinations, to assess necessity/sufficiency of structure vs behavior signals.

**Behavioral training protocol.** For each AE update step, compute \(L_B\) using **256 query images** sampled from the *zoo dataset’s training set* (unlabeled). This means behavioral matching is aligned with the in-distribution data manifold.

**Reconstructive evaluation metrics.**
1. **Structural fidelity:** distribution of pairwise \(\ell_2\) distances \(\|\hat{\theta}-\theta\|_2\) (reported as “structural L2 distances”).
2. **Behavioral fidelity:** *model agreement* between original and reconstructed networks (fraction of matching predictions on a shared evaluation set; the paper uses this as a behavioral similarity score).
3. **Task accuracy:** compare distributions of test accuracies of (i) original zoo models vs (ii) reconstructed models.

**Key reconstructive findings (Fig. 2–3).**
- Using **only** \(L_S\) is “sufficient and necessary” to reduce structural error (tight \(\ell_2\) distance distribution), but **low structural error does not imply behavioral similarity** or preserved accuracy.
- Using **only** \(L_B\) performs poorly: it yields **highest structural error and lowest agreement**, suggesting that behavioral matching alone (at least in their setup) is unstable/underconstrained without structural anchoring.
- **Combining** \(L_S\) and \(L_B\) yields the **highest model agreement** distributions; adding \(L_B\) to the baseline is described as “essential” for behaviorally similar reconstructions.
- Accuracy distributions (Fig. 3): baseline reconstructions are systematically worse than original zoo models, whereas the \(L_C\!+\!L_S\!+\!L_B\) reconstructions closely match high-performing zoo models. They also note a possible *upward bias* (reconstructions sometimes skew toward higher accuracy than originals), hypothesized to come from overrepresentation of good models in the zoo.

**Generative downstream task (weight generation).**
Goal: generate *new* weights by sampling in latent space then decoding.
1. Select **anchor models** that are well-performing (criteria in Appendix B).
2. Compute their latent hyper-representations.
3. Apply **PCA** to reduce latent dimension to **32**.
4. Fit a **kernel density estimate (KDE)** over PCA coordinates, with an **independence assumption** (“coordinates are orthogonal”).
5. Sample synthetic points from the KDE, invert PCA back to latent space, then decode to weights.
6. Evaluate generated models’ test accuracy and diversity (diversity details referenced to Appendix Table 5).

**Main quantitative results (Table 1: max accuracies).**

| Dataset | Losses | Zoo (max) | Recon. (max) | \(\Delta\)Acc Rec. | Gener. (max) | \(\Delta\)Acc Gen. |
|---|---|---:|---:|---:|---:|---:|
| SVHN | \(L_C \oplus L_S\) (baseline) | 91.0% | 74.5% | -16.5% | 61.3% | -29.7% |
| SVHN | \(L_C \oplus L_S \oplus L_B\) | 91.0% | 90.4% | -0.6% | 90.4% | -0.6% |
| CIFAR-10 | \(L_C \oplus L_S\) (baseline) | 70.1% | 51.2% | -18.9% | 46.0% | -24.1% |
| CIFAR-10 | \(L_C \oplus L_S \oplus L_B\) | 70.1% | 69.5% | -0.6% | 69.5% | -0.6% |
| EuroSAT | \(L_C \oplus L_S\) (baseline) | 88.5% | 68.6% | -19.9% | 56.5% | -32.0% |
| EuroSAT | \(L_C \oplus L_S \oplus L_B\) | 88.5% | 87.7% | -0.8% | 87.5% | -1.0% |

**Interpretation.**
- The baseline AE can achieve low weight reconstruction error (per earlier discussion) yet fails catastrophically in *functional* reconstruction and generation (drops of \(\approx 16.5\)–\(19.9\) points for best reconstructions; \(\approx 24.1\)–\(32.0\) points for best generations).
- Adding \(L_B\) nearly closes the gap to the best zoo models for both reconstruction and generation (within \(\approx 0.6\)–\(1.0\) points of the zoo maximum across all three datasets).
- The generated models under the proposed loss “match the performance of the best reconstructed models” and are reported to be “somewhat diverse” (Appendix Table 5), indicating the method is not simply reproducing identical weights.

**Ablations / ancillary claims (as referenced in the excerpt).**
- **\(\beta\) tuning:** \(\beta=0.1\) chosen via validation; implies behavioral term must be strong relative to structural to recover function, but structural still necessary.
- **Query choice:** random queries hypothesized to degrade reconstructions; in-distribution queries help (Appendix D.3).
- **Compute cost:** behavioral loss adds overhead because it requires forward passes through original + reconstructed models per step; Appendix D.4 reportedly shows that for comparable compute time, the structure+behavior approach still outperforms fully structural training.

**Notably missing in the extracted text:** explicit optimizer, learning rate, batch size, temperature for NTXent, hardware/runtime, and statistical significance reporting (confidence intervals / multiple seeds) are not provided in the visible portion (they may appear in appendices/references not included).

### Discussion & Conclusion
The central takeaway is that **structural similarity in weight space is insufficient** for faithful model reconstruction/generation; adding a behavioral matching signal yields a strong synergy, improving both agreement and downstream test accuracy of reconstructed and generated models. Limitations include scalability (transformer-based weight tokenization over large parameter sequences) and added computational overhead from behavioral querying during training. The authors suggest future work on scaling behavioral losses to larger networks and improving efficiency.

## Key Contributions
- Introduces a **behavioral loss \(L_B\)** for weight-space autoencoders that matches original vs reconstructed model outputs on shared (unlabeled) queries, and integrates it with contrastive and structural objectives via
  \[
  L = \gamma L_C + (1-\gamma)\big(\beta L_S + (1-\beta)L_B\big).
  \]
- Provides a **gradient/Taylor analysis** showing \(L_B\) effectively reweights parameter errors by a Jacobian-alignment term \(F_j=\frac{1}{n}\sum_i J_{\theta_j}(x_i)^\top J_{\hat{\theta}_j}(x_i)\), explaining why behavioral supervision targets functionally salient directions missed by Euclidean MSE.
- Demonstrates large **empirical gains for reconstruction and generation** across SVHN/CIFAR-10/EuroSAT zoos: best reconstructed/generative accuracies improve from large gaps (up to \(-32.0\%\)) to near-parity (within \(\approx 0.6\)–\(1.0\%\)) with the best original zoo models.

## Potential Relevance
If you are developing hypotheses about *weight-space foundation models* or *model weight generative modeling*, this paper isolates an important failure mode: low weight MSE does not guarantee preserved function, and adding function-level constraints can fix generation fidelity. The proposed loss is also a practical template for combining **equivariance-aware structural constraints** (e.g., permutations) with **query-based functional constraints**, suggesting future directions like smarter query selection, distillation-style objectives, or scaling to transformer/Large Language Model weight tokenizations where Euclidean losses are especially brittle.