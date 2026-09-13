# 6. Discussion

## 6.1 Key Findings and Their Interpretation

**Finding 1: Spurious direction recoverability is determined by the pretrained initialization prior, not by spurious correlation strength.**

Both Waterbirds and CelebA have spurious correlations strong enough to substantially degrade worst-group accuracy under ERM — that is why they are standard benchmarks. Yet our results show that clustering-based spurious direction recovery works for one and fails for the other. The differentiating factor is not dataset difficulty in the worst-group accuracy sense, but the alignment between the spurious attribute and the ImageNet pretraining representation.

ImageNet-pretrained ResNet-50 encodes scene-level and background features (birds, habitats, contexts) as high-salience semantic dimensions. Fine-tuning on Waterbirds immediately activates these pre-encoded features, making spurious group structure cluster-separable as early as epoch 5. Hair color, by contrast, is not a primary ImageNet semantic category. The pretrained model does not encode hair-color variation as a high-salience separable dimension, so ERM fine-tuning on CelebA cannot build spurious-direction cluster structure quickly enough at epoch 5.

This reframes what "spurious feature strength" means for annotation-free detection: it is not the correlation magnitude in the label space, but the pretrained representation's affinity for the spurious attribute.

**Finding 2: The detection failure is categorical, not marginal.**

CelebA purity (0.456) is only 0.016 above the random baseline (0.440). This is not a case of a method that works poorly — it is a case of a method that provides essentially no signal above chance. A practitioner deploying annotation-free clustering on CelebA epoch-5 embeddings would obtain cluster assignments nearly indistinguishable from random group labels. Any downstream robustification using these cluster assignments as pseudo-labels would be equivalent to random reweighting.

This categorical failure — not a soft degradation — motivates the need for a pre-screen before applying the detection pipeline.

**Finding 3: Published benchmark results do not transfer across experimental configurations.**

The >95% CelebA purity in PruSC [Kim et al., 2024] and similar results in other clustering-based papers are obtained under configurations that differ from early-epoch settings: they use post-convergence embeddings, potentially larger k, and possibly different preprocessing. Our epoch-5, k=2 result (purity=0.456) shows that these published results should not be cited as evidence that early-epoch annotation-free detection is reliable on CelebA. The field needs to distinguish between detection results at convergence and detection results at early training phases, as these have fundamentally different applicability to intervention methods.

## 6.2 Proposed Diagnostic: Spurious Feature Salience Pre-Screen

Based on our findings, we propose a lightweight pre-screen that practitioners can run before trusting annotation-free cluster-based spurious direction estimates:

**Pretrained linear probe accuracy for the spurious attribute.** Before any fine-tuning, extract embeddings from the pretrained model (no task-specific training) and train a linear classifier on a small labeled set for the suspected spurious attribute. If linear probe accuracy exceeds ~70% from pretrained embeddings, the pretrained model already encodes the spurious attribute as a separable feature — epoch-5 k-means is likely to succeed. If accuracy is near chance, the pretrained prior does not align with the spurious attribute, and epoch-5 k-means will likely fail.

This pre-screen requires labeled examples for the spurious attribute (not group labels), which are typically much cheaper to obtain than full group annotations — often available from existing dataset metadata.

## 6.3 Limitations

**L1 — Single random seed.** Our experiments use one fixed seed (PoC mode), matching the design of the existence gate (02c_experiment_brief.md). The Waterbirds gap above threshold is large (AMI 0.262 above, purity 0.142 above), making it likely to be robust across seeds. CelebA's near-random result is also unlikely to reverse with different seeds. However, formal characterization of variance across ≥5 seeds is absent and should be addressed in follow-up work.

**L2 — k=2 underspecification.** Both datasets have 4-group spurious structures (binary class × binary spurious attribute), but k=2 can only create 2 clusters. For Waterbirds, the dominant spurious axis (water vs. land background) maps cleanly onto k=2. For CelebA, the minority group (blonde male, ~1% of data) cannot be captured by k=2, which collapses the 4-group structure. Using k=4 or BIC-guided GMM may improve CelebA performance. We intentionally use k=2 to match published methodology, but acknowledge this underspecification as a genuine limitation.

**L3 — Epoch 5 as a non-universal critical period marker.** Waterbirds has 4,795 training samples; CelebA has 162,770. At epoch 5, the number of gradient updates per sample differs substantially — CelebA may require epochs 10–20 for sufficient spurious-direction consolidation. Defining the probe epoch by representational stability criteria rather than absolute epoch count would make the method more principled.

**L4 — Downstream mechanism (GSB) untested.** Our work validates the existence of a conditionality in the detection step. The downstream Gradient SNR Balancing (GSB) intervention — which would equalize gradient SNR along cluster-discovered directions to improve worst-group accuracy — was blocked by the CelebA gate failure and remains untested. The mechanistic chain from gradient SNR imbalance to representational suppression (H-M1 through H-M4) is theoretically motivated but not empirically validated.

**L5 — Restricted to vision with ResNet-50.** Our findings are grounded in ImageNet-pretrained ResNet-50. ViT-B and other architectures may encode spurious attributes differently, and NLP/audio domains may exhibit different forms of pretraining alignment. Cross-architecture and cross-modality generalization of the conditionality finding requires future investigation.

## 6.4 Broader Impact

This work identifies a silent failure mode in annotation-free robustification pipelines — one that could lead practitioners to apply robustification with false confidence on datasets where the detection step produces random outputs. Raising awareness of feature-strength conditionality encourages more careful validation of the detection step before trusting downstream robustification results.

On the positive side, the proposed salience pre-screen provides a cheap, practical gate for practitioners. The finding that the pretrained initialization prior is the key determinant also suggests that foundation model fine-tuning — where pretraining encodes an extremely broad set of features — may be more amenable to annotation-free spurious detection than task-specific pretrained models. This is a potentially valuable direction for scalable robustification.

There are no direct negative societal impacts of this diagnostic work. Indirectly, improving the reliability of spurious correlation detection benefits high-stakes applications (medical imaging, fairness-sensitive prediction) where worst-group accuracy failures have real consequences.
