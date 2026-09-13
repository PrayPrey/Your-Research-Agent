# Related Work

Our work sits at the intersection of two research areas: data augmentation techniques for deep learning and learning under label noise. While both areas are well-established, neither addresses the core question of semantic validity—whether standard augmentations violate domain-specific constraints and thereby introduce systematic label noise.

## Data Augmentation Surveys

Data augmentation has been extensively studied as a regularization technique to improve model generalization. Comprehensive surveys (Yang et al., 2022; Shorten & Khoshgoftaar, 2019) catalogue a wide range of augmentation methods across different modalities: geometric transformations (flip, rotation, crop, affine), photometric adjustments (brightness, contrast, color jitter), learned augmentations (AutoAugment, RandAugment), and mixing strategies (Mixup, CutMix). These surveys typically focus on cataloguing techniques, reporting empirical performance gains, and analyzing computational costs.

Yang et al. (2022), with 399 citations, provide the most comprehensive recent survey, organizing augmentation techniques by approach (geometric, photometric, kernel-based, learned) and application domain (image classification, object detection, segmentation). However, their analysis emphasizes what augmentations exist and how they improve aggregate performance metrics, not whether augmentations preserve semantic validity for specific classes. The implicit assumption is that standard transformations like horizontal flip are universally applicable—beneficial or at worst neutral—across datasets.

Domain-specific augmentation studies (Perez & Wang, 2017 for medical imaging; Wen et al., 2020 for time series) acknowledge that augmentation choices should match domain characteristics. For instance, vertical flip is inappropriate for chest X-rays due to anatomical orientation constraints. Yet these insights remain implicit practitioner knowledge rather than formalized validation frameworks. No prior work systematically tests whether standard augmentations violate semantic constraints on canonical benchmarks like MNIST, or quantifies the resulting degradation.

Automated augmentation search methods (Cubuk et al., 2019; Lim et al., 2019) discover effective augmentation policies through reinforcement learning or population-based training. AutoAugment searches over a discrete space of augmentation operations and magnitudes, optimizing validation accuracy. However, the search is purely empirical—the learned policies lack explicit semantic validity constraints. If horizontal flip degrades accuracy on asymmetric classes but improves aggregate performance (due to benefits on symmetric classes or increased data diversity), AutoAugment may still select it. Our framework provides a validation criterion that could constrain such searches.

## Label Noise Literature

Learning under label noise addresses training with corrupted ground-truth labels (Song et al., 2022; Wei et al., 2021). The standard model distinguishes symmetric noise (labels flipped uniformly across classes) from asymmetric noise (class-specific corruption patterns). Noise-robust training methods include loss correction (Patrini et al., 2017), sample reweighting (Ren et al., 2018), and robust loss functions (Zhang & Sabuncu, 2018; Ma et al., 2020).

This literature overwhelmingly focuses on annotation errors: mistakes by human labelers, adversarial label flips, or systematic biases in crowdsourced labels. Wei et al. (2021) survey over 100 papers on noisy label learning, categorizing methods by approach (sample selection, robust loss, label correction, semi-supervised). Remarkably, none consider data augmentation as a source of label noise. The implicit assumption is that labels are corrupted during annotation, not during training through augmentation.

Yet augmentation-induced label noise has distinct properties. First, it is deterministic and tunable: flip probability directly controls the proportion of semantically invalid training examples. Second, it is class-specific: only asymmetric classes are affected by horizontal flip, creating an asymmetric noise pattern. Third, it is reproducible: every training run with flip probability p produces the same noise structure (up to random augmentation sampling). These properties make augmentation-induced noise an ideal controlled experimental paradigm for testing label noise theories.

Our contribution connects these literatures. We demonstrate that horizontal flip functions as a tunable asymmetric label noise source, with noise rate proportional to flip probability. The perfect dose-response relationship (Spearman ρ = -1.0) we observe aligns precisely with label noise theory: accuracy degrades monotonically with noise rate for affected classes. This finding extends label noise research by identifying augmentation as a systematic noise source, distinct from annotation errors.

## MNIST Benchmarks and Practitioner Folklore

MNIST handwritten digit classification (LeCun et al., 1998) remains a canonical benchmark for validating deep learning techniques. Winning Kaggle solutions on MNIST consistently exclude horizontal flip from their augmentation pipelines, instead favoring rotation (±10-15°), small translations, and elastic deformations. PyTorch official tutorials (MNIST quickstart, CNN examples) similarly omit horizontal flip while including rotation and affine transformations.

This folklore is well-established but unexplained. Why is flip avoided? Online discussions offer intuition: "flipping 2 or 5 makes them backwards," "MNIST digits aren't symmetric." Yet no published work quantifies the harm, identifies affected classes systematically, or tests the mechanism rigorously. The gap between implicit practitioner knowledge and formal validation is precisely what we address.

Recent work applies horizontal flip to MNIST without semantic analysis (Purba et al., 2025), reporting overall accuracy without per-class breakdowns. This oversight reflects the broader problem: aggregate metrics mask class-specific degradation. A model achieving 99% overall accuracy may degrade significantly on asymmetric digits while maintaining high accuracy on symmetric digits, obscuring the semantic invalidity issue.

## Positioning Our Work

We position our work at the intersection of augmentation surveys and label noise research, filling a gap neither addresses. Augmentation surveys catalogue techniques but lack semantic validity frameworks. Label noise research studies annotation errors but ignores augmentation-induced noise. We demonstrate that:

1. **Semantic validity is testable**: Per-class accuracy grouped by digit symmetry reveals differential effects hidden in aggregate metrics.

2. **Augmentation induces label noise**: Horizontal flip on MNIST creates class-specific asymmetric noise with dose-response behavior (ρ = -1.0).

3. **Folklore has quantitative foundation**: Practitioners correctly avoid flip (0.37-4.10% degradation on asymmetric digits), but now we provide reproducible evidence and mechanistic understanding.

By formalizing semantic validity as an explicit augmentation design criterion, we establish a validation methodology applicable beyond MNIST: dose-response testing, differential class-group analysis, and positive control experiments (semantically valid augmentation like rotation). This framework generalizes to any domain with semantic asymmetry—medical imaging (anatomical orientation), traffic signs (directional arrows), character recognition (script chirality)—wherever augmentation-induced invariances may misalign with domain-specific constraints.
