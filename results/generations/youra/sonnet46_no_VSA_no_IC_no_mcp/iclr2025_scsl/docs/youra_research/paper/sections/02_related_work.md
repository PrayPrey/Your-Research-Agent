# 2. Related Work

### Spurious Correlations and Group Robustness

The study of spurious correlations in deep learning traces to observations that models exploit dataset biases rather than learning causal features [Geirhos et al., 2020; Zhang et al., 2017]. Sagawa et al. [2020] formalize this via group robustness: in Waterbirds and CelebA, a model achieving high average accuracy still fails badly on minority groups whose spurious attribute contradicts the majority correlation. Their Group DRO method explicitly minimizes worst-group loss, requiring group annotations at training time. Our work is complementary: we characterize how much spurious content enters frozen representations *before* any downstream training, as a function of pretraining paradigm — without assuming group labels are available.

Kirichenko et al. [2022] demonstrate that ERM features are sufficient for robustness: only the classifier head needs retraining on a small group-balanced set (Deep Feature Reweighting, DFR), achieving near-oracle performance on Waterbirds. This result motivates studying frozen representation quality directly, as we do. However, DFR focuses entirely on supervised ERM and does not compare to SSL paradigms — leaving open whether ERM's spurious feature content is typical or atypical among pretraining objectives.

Izmailov et al. [2022] provide a broader study of feature learning under spurious correlations, including comparisons with DINO on Waterbirds. Their analysis is closest to ours in scope, but does not use a controlled spurious/task ratio metric and does not perform a 4-paradigm comparison with Bonferroni-corrected pairwise tests. We provide this systematic comparison.

### Self-Supervised and Contrastive Representation Learning

Contrastive SSL methods [Chen et al., 2020 (SimCLR); He et al., 2020 (MoCo)] learn representations by maximizing agreement between two augmented views of the same image. DINO [Caron et al., 2021] uses self-distillation with a momentum teacher, producing emergent class-discriminative attention maps. BarlowTwins [Zbontar et al., 2021] optimizes redundancy-reduction across cross-correlation matrices. All four paradigms use ResNet-50 in their standard evaluation protocols, making controlled comparison feasible.

These methods are primarily evaluated on ImageNet linear probe accuracy [Chen et al., 2020; Caron et al., 2021], which measures task-relevant encoding but says nothing about spurious feature content. The key gap is that *no prior work measures spurious attribute probe accuracy as a function of pretraining paradigm using a controlled backbone and group-annotated datasets.*

Robinson et al. [2021] show that contrastive learning can encode shortcut features, particularly when spurious attributes are stable across augmentations. Wen et al. [2021] analyze what features contrastive objectives encode as a function of augmentation design. These works establish that SSL is not spurious-feature-free — but they do not compare to supervised baselines under controlled conditions. We do, and find that supervised ERM encodes spurious features *more* strongly, not less.

### Distribution Shift Benchmarks

WILDS [Koh et al., 2021] provides ten real-world distribution shift datasets with standardized splits, including Waterbirds and CelebA under the spurious correlation framing. DomainBed [Gulrajani & Lopez-Paz, 2021] benchmarks 20+ domain generalization algorithms on seven datasets, showing that careful ERM tuning matches or surpasses specialized methods. Both evaluate *fine-tuned* models, making it impossible to attribute performance differences to the pretraining representation versus the fine-tuning procedure. We isolate the pretraining effect by freezing the backbone throughout.

### Augmentation and Feature Learning

Shah et al. [2020] characterize SGD's "simplicity bias" — the tendency to prefer low-complexity predictors even when more complex task-relevant features exist. This connects to our finding that ERM encodes spurious features aggressively: spurious attributes (background texture) are often simpler and more predictive than task-relevant features (bird morphology) in biased training distributions. Zimmermann et al. [2021] show theoretically that contrastive learning approximately inverts the data generating process, recovering latent structure. Our empirical finding — that label-agnostic contrastive SSL encodes spurious features less than label-supervised ERM — is consistent with this theoretical framework when spurious attributes are not in the true latent structure.

**Our position:** We synthesize and extend these threads by providing the first controlled 4-paradigm × 2-dataset comparison of spurious attribute linear probe accuracy on frozen ResNet-50 representations, using a spurious/task ratio metric that decouples paradigm effects from absolute accuracy differences across datasets.
