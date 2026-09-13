---
source_paper: "arxiv_2204_02937.md"
generated_at: "2026-08-04T03:10:27.079605"
model: "openai/gpt-5.2"
summary_chars: 16626
---

# Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations

## Key Metadata
- **Authors:** Polina Kirichenko et al.
- **Year:** 2023
- **Venue:** ICLR 2023
- **Core Contribution:** Show that ERM models often learn strong *core* representations despite relying on spurious features, and that simply retraining the **last linear layer** on a small group-balanced “reweighting” set (DFR) can match/beat state-of-the-art worst-group robustness methods at far lower cost.

## Section Summaries

### Abstract
Neural network classifiers can largely rely on simple spurious features, such as backgrounds, to make predictions. However, even in these cases, we show that they still often learn core features associated with the desired attributes of the data, contrary to recent findings. Inspired by this insight, we demonstrate that simple last layer retraining can match or outperform state-of-the-art approaches on spurious correlation benchmarks, but with profoundly lower complexity and computational expenses. Moreover, we show that last layer retraining on large ImageNet-trained models can also significantly reduce reliance on background and texture information, improving robustness to covariate shift, after only minutes of training on a single GPU.

### Introduction & Motivation
Deep models trained with standard empirical risk minimization (ERM) often exploit **spurious correlations** (e.g., background context, metadata artifacts, lexical cues), yielding high average accuracy but poor performance on **minority groups** where the spurious correlation breaks. Prior work frequently attributes this failure to *bad representations*—i.e., models “ignore” core features under simplicity bias—motivating complex distributionally robust optimization (DRO) or multi-model pipelines. This paper challenges that view: even when ERM fails on minority groups, the learned representation often still encodes the **core** signal. The authors hypothesize the main issue is **mis-weighting at the classifier head**, and propose a minimal fix: re-train only the last layer using a small, group-balanced dataset where the shortcut is not predictive.

### Methodology
**Problem setup (group mixtures).** Data consist of groups \(G_i\) (typically label × spurious attribute), each with distribution \(p_i(x,y)\). The training distribution is a mixture:
\[
p(x,y) = \sum_i \alpha_i\, p_i(x,y),
\]
where \(\alpha_i\) is the (imbalanced) group proportion. The evaluation emphasizes **worst-group accuracy**, i.e., performance on the smallest / hardest group(s).

**Key representation-learning claim (WHY DFR should work).** Through controlled experiments (Waterbirds variants; “Dominoes” simplicity-bias datasets), the authors show ERM models frequently learn **both** spurious and core features in their embeddings—even when predictions are dominated by the spurious feature and worst-group accuracy collapses. Evidence includes: (i) strong performance when spurious features are removed at test time (FG-only evaluation), and (ii) high accuracy when a simple linear probe/logistic regression is trained on frozen embeddings to decode the core signal.

**Deep Feature Reweighting (DFR): last-layer retraining.** DFR is a two-stage procedure:

1. **Stage 1 (feature learning, ERM):** Train a standard model on the full (possibly spurious/imbalanced) dataset \(D=\{(x_i,y_i)\}\) using ERM. Architecturally, the network is decomposed into:
   - a **feature extractor** \(f_\theta(x)\) (e.g., ResNet-50 trunk or BERT encoder),
   - a **linear classification layer** (head) producing logits \(W f_\theta(x)\).

2. **Stage 2 (feature reweighting, linear retraining):** Discard the original head and train a **new linear head** (logistic regression / linear classifier) *from scratch* on a small **reweighting dataset** \(\hat D\), where groups are **equally represented** (constructed via group-balanced subsampling). Only the last layer parameters are optimized; \(f_\theta\) is frozen.

**Optimization objective for Stage 2.** The paper emphasizes \(\ell_1\)-regularization to induce sparsity because \(|\hat D|\) can be small relative to embedding dimension (especially for large pretrained models). A canonical formulation consistent with their description is:
\[
\min_{W}\;\; \frac{1}{|\hat D|}\sum_{(x,y)\in \hat D} \ell\big(y, W f_\theta(x)\big) \;+\; \lambda \|W\|_1,
\]
where \(\ell\) is cross-entropy/logistic loss and \(\lambda\) is the **single tuned hyperparameter** (“regularization strength”).

**Data usage / variants and notation.**
- Base features are learned on \(D\) (imbalanced, spurious).
- Reweighting head is trained on \(\hat D\) (balanced).
- Notation: \(\mathrm{DFR}_{\hat D}^{D}\) (in the paper’s text: “DFR \( \hat D / D\)”) to indicate the dataset used for ERM features vs. last-layer training.

**Practical training details explicitly described.**
- For benchmark DFR (denoted \( \mathrm{DFR}^{\text{Val}}_{\text{Tr}} \)): the reweighting set \(\hat D\) is a **group-balanced subset of the validation set** (so group labels are only needed on validation).
- They **train logistic regression 10 times** on different random balanced subsets and **average the learned weights** to better exploit limited reweighting data.
- Hyperparameter tuning: only \(\lambda\) (regularization). They split validation in half: one half to tune \(\lambda\), then retrain logistic regression on the full validation set with the chosen \(\lambda\).

**Architectures used across settings.**
- Vision spurious-correlation benchmarks (Waterbirds, CelebA): **ResNet-50**, initialized from **ImageNet pretrained weights**.
- NLP benchmarks (MultiNLI, CivilComments): **BERT**, pretrained on BookCorpus + English Wikipedia.
- Simplicity-bias synthetic tests: **ResNet-20** on Dominoes variants (MNIST-MNIST, MNIST-FashionMNIST, MNIST-CIFAR).

**Novelty vs prior work.**
- Conceptual: robustness can often be obtained by **reweighting** already-learned features rather than re-learning representations with DRO/IRM-style objectives.
- Algorithmic: unlike retraining-on-train-set approaches (e.g., related classifier retraining work), DFR emphasizes **held-out, group-balanced reweighting data** and **regularized** linear retraining, yielding consistently better worst-group results in their comparisons.

### Experiments & Results
**Benchmarks and datasets.**
1. **Waterbirds** (Sagawa et al., 2019): synthetic composition of CUB birds (foreground) with Places backgrounds (spurious). Groups are (bird type × background). Example group sizes given: **3498, 184, 56, 1057** (heavy imbalance; minority groups are those where background contradicts bird type).
2. **CelebA hair color prediction** (Liu et al., 2015): target = blond vs non-blond; spurious attribute = gender. Group proportions reported: **44%**, **14%**, **41%**, **1%** (minority: blond males at 1%).
3. **MultiNLI**: 3-way NLI; spurious cue = presence of negation words correlated with contradiction.
4. **CivilComments (WILDS)** (Borkan et al., 2019; Koh et al., 2021): toxicity classification with 8 identity attributes \(s_i\). Evaluation reports worst accuracy across **16 overlapping groups** \((y, s_i)\) (for each attribute).

**Metrics.**
- **Worst-group test accuracy** (primary).
- **Mean test accuracy**, computed as prevalence-weighted average of group accuracies (as in Sagawa et al., 2019).
- For ImageNet analyses:
  - **Top-1 accuracy** on ImageNet variants and OOD sets (ImageNet-R, ImageNet-C).
  - **Shape bias (%)** on the Geirhos et al. cue-conflict evaluation (GST): fraction of predictions following shape vs texture.

**Baselines compared (with different supervision assumptions).**
- **ERM** (standard training).
- **Group DRO** (Sagawa et al., 2019) (uses group labels on train).
- **JTT** (Just Train Twice; Liu et al., 2021) (detect minority examples; group labels mainly for validation tuning).
- **CnC** (Correct-n-Contrast; Zhang et al., 2022) (detect minority + contrastive).
- **SUBG** (Idrissi et al., 2021): ERM on a group-balanced subset.
- **SSA** (Nam et al., 2022): semi-supervised propagation of group labels from validation.

**Main spurious-correlation benchmark results (Table 2).**  
(“Group Info” indicates whether group labels are available on Train / Val; DFR uses group labels on validation for tuning *and* head training.)

| Method | Group Info (Train/Val) | Waterbirds Worst | Waterbirds Mean | MultiNLI Worst | MultiNLI Mean | CelebA Worst | CelebA Mean | CivilComments Worst | CivilComments Mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| JTT | ✗ / ✓ | 86.7 | 93.3 | 81.1 | 88.0 | 72.6 | 78.6 | 69.3 | 91.1 |
| CnC | ✗ / ✓ | 88.5 ± 0.3 | 90.9 ± 0.1 | 88.8 ± 0.9 | 89.9 ± 0.5 | – | – | 68.9 ± 2.1 | 81.7 ± 0.5 |
| SUBG | ✓ / ✓ | 89.1 ± 1.1 | – | 85.6 ± 2.3 | – | 68.9 ± 0.8 | – | – | – |
| SSA | ✗ / ✓✓ | 89.0 ± 0.6 | 92.2 ± 0.9 | 89.8 ± 1.3 | 92.8 ± 0.1 | 76.6 ± 0.7 | 79.9 ± 0.87 | 69.9 ± 2.0 | 88.2 ± 2.* |
| Group DRO | ✓ / ✓ | 91.4 | 93.5 | 88.9 | 92.9 | 77.7 | 81.4 | 69.9 | 88.9 |
| Base (ERM) | ✗ / ✗ | 74.9 ± 2.4 | 98.1 ± 0.1 | 46.9 ± 2.8 | 95.3 ± 0.0 | 65.9 ± 0.3 | 82.8 ± 0.1 | 55.6 ± 0.6 | 92.1 ± 0.1 |
| **DFR\(_\text{Tr}^\text{Val}\)** | ✗ / ✓✓ | **92.9 ± 0.2** | 94.2 ± 0.4 | 88.3 ± 1.1 | 91.3 ± 0.3 | 74.7 ± 0.7 | 82.1 ± 0.2 | **70.1 ± 0.8** | 87.2 ± 0.3 |

Key takeaways:
- DFR achieves **best reported worst-group accuracy** among listed methods on **Waterbirds (92.9%)** and **CivilComments (70.1%)**.
- It is broadly **competitive with Group DRO** while requiring only a small group-balanced validation set for head retraining (and only one tuned hyperparameter \(\lambda\)).

**Representation-learning evidence (Waterbirds variants, Table 1).**
They vary correlation strength and evaluate on (i) Original test distribution and (ii) FG-only test where the background spurious feature is removed.

| Train dataset | Worst-group acc on Original test | Worst-group acc on FG-Only test |
|---|---:|---:|
| Balanced (50%) | 91.9% | 94.7% |
| Original (95%) | 73.8% | 93.7% |
| Original (100%) (no minority groups in train) | 38.4% | 94.0% |
| FG-Only (no spurious bg) | 75.2% | 95.5% |

Interpretation: even when ERM collapses on the Original test minority groups (e.g., **38.4%** worst-group under 100% spurious correlation), the same model achieves **~94%** on FG-only inputs—supporting the claim that **core bird features are learned** but underweighted in the final decision.

**Extreme simplicity bias (Dominoes; Figure 2 summary).**
- Datasets: MNIST-MNIST, MNIST-FashionMNIST, MNIST-CIFAR, with top-half “simple” spurious feature and bottom-half “complex” core feature.
- When spurious correlation is **100%**, worst-group accuracy on the original mixed-group test can drop to **0%** (model uses only the shortcut).
- Yet **linear decoding** (logistic regression trained on final-layer embeddings using a balanced set) can recover the core feature with high worst-group accuracy in multiple settings, especially when correlation is **99%/95%**—motivating DFR as “decode + reweight”.

**Natural spurious correlations on ImageNet-scale models.**

1. **Background reliance (Backgrounds Challenge; ImageNet-9).**
   - Dataset: **ImageNet-9** has **45k training images** and **4050 validation images** (9 coarse classes).
   - Validation variants: Original, Mixed-Rand (random foreground/background recombination), FG-Only (black background), Paintings-BG (paintings as backgrounds), plus ImageNet-R restricted to the 9 classes.
   - Feature extractor: **ImageNet-trained ResNet-50** (frozen).
   - Heads trained with DFR:
     - **Baseline**: train linear head on Original train set.
     - **DFR\(_\text{MR}\)**: retrain head on Mixed-Rand.
     - **DFR\(_\text{OG+MR}\)**: retrain head on a mixture of Mixed-Rand and Original.
   - Result summary (from Figure 3 narrative):
     - Baseline performs better on **FG-Only (92%)** than on **Mixed-Rand (86%)**, indicating representational support for foreground classification but background-dependent head weights.
     - With Mixed-Rand reweighting data, DFR **improves accuracy** on Mixed-Rand, FG-Only, Paintings-BG, while **DFR\(_\text{OG+MR}\)** largely preserves Original accuracy (small drop because background helps on Original).

2. **Texture vs shape bias (Stylized ImageNet; Table 3).**
   - Evaluate models on:
     - **Shape bias (%)** (cue conflict),
     - **Top-1 accuracy** on ImageNet, ImageNet-R, ImageNet-C.
   - Compare: RN-50 trained on IN, SIN, IN+SIN; Shape-RN-50; and DFR with frozen IN-trained RN-50 features but head retrained on SIN or IN+SIN.

| Method | Training data | Shape bias (%) | ImageNet Top-1 (%) | ImageNet-R (%) | ImageNet-C (%) |
|---|---|---:|---:|---:|---:|
| RN-50 | IN | 21.4 | 76.0 | 23.8 | 39.8 |
| RN-50 | SIN | **81.4** | 60.3 | 26.9 | 38.1 |
| RN-50 | IN+SIN | 34.7 | 74.6 | 27.6 | **45.7** |
| Shape-RN-50 | IN+SIN (then finetune on IN) | 20.5 | **76.8** | 25.6 | 42.3 |
| **DFR** (frozen IN features) | SIN | 34.0 | 65.1 | 24.6 | 36.7 |
| **DFR** (frozen IN features) | IN+SIN | 30.6 | 74.5 | 27.2 | 40.7 |

Key takeaways:
- Shape bias is strongly influenced by the **last layer**: Shape-RN-50 has ImageNet accuracy gains but **shape bias ~20.5%**, close to baseline IN RN-50 (21.4%).
- DFR increases shape bias vs the base IN head (e.g., **21.4% → 34.0%** when retraining on SIN), and DFR on IN+SIN improves robustness metrics relative to base RN-50 on ImageNet-R/C (**23.8 → 27.2** on R; **39.8 → 40.7** on C), though it does not match training-from-scratch on IN+SIN for ImageNet-C.

**Ablations / diagnostic findings emphasized in the paper.**
- **Correlation strength matters**: in Dominoes, 100% correlation can cause 0% worst-group accuracy, but embeddings can still encode the core feature; at 99%/95% correlation, both direct performance and decodability improve.
- **Held-out reweighting beats retraining on train subsets** (discussed relative to prior retraining approaches): using balanced *held-out* data for the head is argued to be “significantly better” across benchmarks (details referenced to appendices).
- **Regularization is important** in small-\(\hat D\) regimes: \(\ell_1\) encourages sparse heads that drop irrelevant/spurious dimensions.

**Computational cost.**
- DFR only retrains the last linear layer; authors state it can run at **ImageNet scale in minutes on a single GPU** (after one-time embedding extraction), and is dramatically cheaper than methods requiring end-to-end retraining (e.g., Group DRO with hyperparameter sweeps).

### Discussion & Conclusion
The central conclusion is that poor worst-group robustness under spurious correlations often stems more from **final-layer weighting** than from a failure to learn core representations. **Deep Feature Reweighting (DFR)**—retraining only the last layer on a small balanced set—can match state-of-the-art benchmark robustness and can reduce background/texture reliance in ImageNet-scale models. Limitations acknowledged include the reliance on some form of **balanced reweighting data** (typically requiring group labels) and that fully maximizing certain properties (e.g., very high shape bias) may still require end-to-end retraining.

## Key Contributions
- Empirically demonstrate that ERM-trained networks often learn **core features** even when they appear to rely on **spurious shortcuts** (e.g., Waterbirds FG-only tests; linear decodability in simplicity-bias Dominoes).
- Propose **Deep Feature Reweighting (DFR)**: a two-stage approach that freezes the ERM feature extractor and **retrains only the last linear layer** on a small group-balanced reweighting set with \(\ell_1\) regularization.
- Show DFR achieves **state-of-the-art or competitive worst-group accuracy** on major spurious correlation benchmarks (notably **92.9%** worst-group on Waterbirds; **70.1%** on CivilComments) and improves robustness properties (reduced background reliance; increased shape bias; gains on ImageNet-R/C).

## Potential Relevance
DFR is a strong “minimal intervention” baseline for any robustness-to-shortcuts hypothesis: it isolates whether failures are due to **representation learning** or merely **linear readout/feature weighting**. The paper’s evidence (FG-only evaluations; linear probing; last-layer sensitivity of shape bias) is also useful for designing diagnostic experiments: before proposing complex robust training, test whether a small balanced set + last-layer retrain already fixes worst-group performance. Finally, DFR’s low compute and single main hyperparameter (\(\ell_1\) strength) make it practical for rapid hypothesis iteration on large pretrained models.