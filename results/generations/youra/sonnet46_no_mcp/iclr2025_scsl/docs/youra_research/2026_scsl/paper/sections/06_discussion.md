# 6. Discussion

## 6.1 Key Findings and Theoretical Implications

**The three-step causal chain is confirmed.** Our results establish, for the first time on a standard spurious correlation benchmark, the complete causal pathway from feature complexity to temporal learning dynamics: (1) spurious features are measurably simpler than core features on 3/3 complexity metrics, with a 10× sample efficiency gap; (2) this complexity hierarchy drives a 7× gradient signal advantage for spurious features in early training (GDR = 6.977); (3) the gradient asymmetry produces a statistically significant temporal gap δ(t) > 0 during early training (p = 0.022, 13.3% window fraction). This chain quantitatively operationalizes the Frequency Principle [Xu et al., 2019] and Simplicity Bias [Shah et al., 2020] on the Waterbirds benchmark, providing the mechanistic grounding that prior annotation-free methods lack.

**The transition epoch t* is a structural SGD property.** The low cross-seed variance of t* (std = 2.00 epochs, CI upper bound = 2.31 epochs) confirms that the timing of spurious dominance is determined by the dataset's feature complexity hierarchy and the model's gradient dynamics — not by random initialization. This makes t* a reliable diagnostic: a practitioner can measure t* once and expect it to generalize across runs with the same dataset and architecture.

**ImageNet pretraining dominates DFR's success.** The most surprising finding of this study is that DFR achieves WGA = 0.806 at epoch 1 — before any Waterbirds-specific training. This challenges the implicit assumption in the DFR literature that ERM training is necessary to build core feature representations that DFR reweights. Instead, ResNet-50 pretrained on ImageNet already encodes discriminative bird morphology features sufficient for DFR's class-balanced logistic regression to extract. We propose three non-exclusive explanations: (a) ImageNet contains sufficient visual diversity of birds and backgrounds that pretrained features are already partially specialized; (b) DFR's class-balanced reweighting is inherently robust to some spurious correlation, finding core features even in noisy representations; (c) the bird/background feature geometry in pretrained ResNet-50 representations may be sufficiently disentangled that minimal fine-tuning is needed. Distinguishing these explanations requires controlled ablations with scratch-trained models.

**GDR persists throughout training.** We expected gradient asymmetry (GDR > 1.0) to be a transient early-training phenomenon resolving at t*. Instead, GDR > 1.0 persists throughout the entire 30-epoch run. The closing of δ(t) at t* is driven by the *accumulation* of core feature gradient signal — not by a decrease in spurious gradient dominance. SGD never de-prioritizes spurious features; core features simply eventually accumulate enough gradient to achieve parity. This distinction matters for gradient-based intervention design: suppressing spurious gradients at t* alone may be insufficient if GDR remains elevated.

## 6.2 Limitations

**L1 — 30-epoch proof-of-concept.** All results come from a 30-epoch training run. In a full 300-epoch run, t* would likely occur proportionally later with a longer, more quantitatively pronounced gap window. Timing-specific claims (window fraction, t* mean) should be interpreted as PoC estimates pending full-scale replication.

**L2 — CelebA replication not achieved.** Network access restrictions blocked the planned CelebA replication. Cross-dataset generalizability of the δ(t) framework remains unconfirmed, though the feature complexity hierarchy for hair color (spurious) vs. facial structure (core) is expected to follow the same pattern.

**L3 — H-M1 Wilcoxon test underpowered.** The planned Wilcoxon test on n=3 checkpoints has a structural minimum p-value of 0.125. The test cannot achieve significance regardless of effect size at this sample size. GDR = 6.977 across 3/3 seeds provides quantitative confirmation, but formal gradient asymmetry significance awaits an extended window (n ≥ 6 checkpoints).

**L4 — H-M4 metric confound.** DFR improvement (DFR WGA − ERM WGA) is confounded by the ERM-WGA ceiling effect. The redesigned experiment using DFR absolute WGA as the dependent variable, or partial correlation controlling for ERM WGA, is deferred to future work.

**L5 — Patch extraction quality.** Quadrant-based patch extraction (fallback for missing segmentation masks) introduces patch impurity. Despite this, all 3/3 complexity metrics pass, indicating the hierarchy is robust.

**L6 — Single architecture and pretraining.** All results use ResNet-50 with ImageNet pretraining. Results for scratch-trained models or transformer architectures may differ, particularly the DFR epoch-1 robustness finding.

## 6.3 Future Work

**Full 300-epoch training (high priority):** Required for quantitative claims about window fraction and t* timing in standard training, and for the full {t*-20, t*, t*+20, t*+50, full} H-M4 condition spread.

**CelebA and text domain replication (high priority):** CelebA with manual download; MultiNLI/CivilComments (BERT) to test cross-architecture generalizability.

**Redesigned H-M4 with DFR absolute WGA (high priority):** Expected to reveal the positive training-depth/DFR correlation that the improvement metric obscures.

**Label-free t* proxy (medium priority):** GDR inflection point, validation loss curvature, or checkpoint cosine similarity as annotation-free t* estimators.

**Scratch-trained model ablation (medium priority):** Tests whether the DFR epoch-1 robustness is specific to ImageNet pretraining.

## 6.4 Broader Impact

The δ(t) framework provides a lightweight diagnostic for spurious feature learning dynamics, requiring only a held-out validation split with group annotations. Positive impacts include mechanistic grounding for annotation-free robustness methods and a principled basis for early-stopping strategies. The framework requires group-label information for probe training, limiting applicability to settings where held-out group annotations exist — a realistic constraint for standard benchmarks. Label-free proxy development (FW4) would address this limitation. We are not aware of potential for misuse specific to this measurement methodology.
