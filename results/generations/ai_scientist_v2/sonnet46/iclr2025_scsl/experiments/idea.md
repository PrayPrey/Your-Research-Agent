## Name

shortcut_transition_detection_intervention

## Title

Detecting and Accelerating the Shortcut-to-Core-Feature Transition in Neural Network Training

## Short Hypothesis

Neural networks exhibit a predictable 'shortcut plateau' phase during training — a period where loss stagnates while the model relies on spurious features before transitioning to core features. We hypothesize that this transition can be detected online using cheap training-time signals (loss curvature, gradient alignment, or representation similarity metrics), and that applying targeted, transient interventions precisely at the detected transition point can dramatically accelerate abandonment of shortcuts and improve worst-group accuracy — without requiring group annotations or significant computational overhead. This is the right setting because: (1) the transition is a universal phenomenon across architectures and tasks, (2) intervening at the right moment is more efficient than continuous debiasing, and (3) no existing work exploits the temporal structure of shortcut learning for intervention timing.

## Related Work

The Norm-Hierarchy Transition (NHT) framework (Khanh & Hoa, 2026) theoretically characterizes the delay in shortcut abandonment as logarithmic in norm ratios, but offers no method to accelerate it. Grokking work (Kumar et al., ICLR 2024; Zhang et al., 2025) explains delayed generalization as lazy-to-rich transitions but focuses on understanding, not intervention. Saddle-to-saddle dynamics (Zhang et al., 2025) explains simplicity bias across architectures but does not propose training-time solutions. On the solutions side, last-layer retraining methods (DFR, SELF, LFR, EVaLS) are post-hoc and require held-out data. Standard debiasing methods (JTT, GroupDRO) apply uniform interventions throughout training, ignoring the temporal structure of shortcut learning. Our proposal is the first to (1) operationalize the shortcut plateau as a detectable training-time event, and (2) design interventions timed to the transition point rather than applied uniformly, making it fundamentally different from all prior work.

## Abstract

Deep neural networks reliably pass through a 'shortcut plateau' during training — an extended period where training loss stagnates and the model relies predominantly on spurious, easy-to-learn features before eventually transitioning to core, generalizable features. Recent theoretical work has characterized this transition in terms of norm hierarchies and saddle-to-saddle dynamics, but no practical method exists to detect or accelerate it during training. We propose a framework called Transition-Aware Shortcut Intervention (TASI) that (1) detects the shortcut plateau online using cheap signals derived from loss curvature, gradient alignment between easy and hard samples, or representation similarity collapse, and (2) applies a targeted, transient intervention — such as a temporary increase in weight decay, a gradient projection step, or a brief feature diversity regularization — precisely when the plateau is detected, to accelerate the transition to core-feature reliance. Unlike prior debiasing methods that apply interventions uniformly throughout training, TASI exploits the temporal structure of shortcut learning, making interventions more efficient and less disruptive to overall training. Unlike post-hoc methods like last-layer retraining, TASI requires no held-out data or group annotations. We validate TASI on standard spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, CivilComments) and controlled synthetic settings where the shortcut plateau timing is known. We show that TASI significantly improves worst-group accuracy over ERM and matches or exceeds annotation-free baselines, while requiring no additional data and adding minimal computational cost.

## Experiments

1. **Plateau Detection Validation**: On Waterbirds and CelebA with known group labels, verify that the shortcut plateau is detectable via three candidate signals: (a) second derivative of training loss (curvature), (b) cosine similarity between gradients of high-loss vs. low-loss samples, and (c) CKA (centered kernel alignment) between early and current layer representations. Measure correlation between detected plateau end and actual worst-group accuracy inflection point. Metric: Pearson correlation, timing error in epochs.

2. **Synthetic Controlled Experiment**: Create a dataset with a known spurious feature (e.g., colored background correlated 95% with label) and a core feature. Train a ResNet-18. Compare: (a) ERM baseline, (b) TASI with each detection signal + weight decay spike intervention, (c) TASI with gradient projection intervention. Measure worst-group accuracy and time-to-transition (epochs until core feature dominates by probing classifier). Metric: Worst-group accuracy, feature attribution ratio.

3. **Main Benchmark Evaluation**: Evaluate TASI on Waterbirds, CelebA, MultiNLI, CivilComments against baselines: ERM, JTT, LfF, LFR, EVaLS (annotation-free), and DFR (with annotations as upper bound). No group annotations used for TASI. Metric: Worst-group accuracy, average accuracy.

4. **Intervention Timing Ablation**: On Waterbirds, apply the same intervention (weight decay spike) at: (a) random times, (b) early training, (c) TASI-detected time, (d) oracle time (known from group labels). Show that timing matters and that TASI-detected time closely approximates oracle. Metric: Worst-group accuracy vs. intervention epoch.

5. **Intervention Type Ablation**: Compare three intervention types at TASI-detected time: (a) temporary weight decay increase (10x for 5 epochs), (b) gradient projection removing shortcut-aligned directions, (c) feature diversity regularization (maximize pairwise distance in representation space). Metric: Worst-group accuracy, training stability (variance across seeds).

6. **Cross-Architecture Generalization**: Test TASI on ViT-B/16, ResNet-50, and a text classifier (BERT) to verify the plateau detection signals generalize across architectures. Metric: Worst-group accuracy improvement over ERM.

## Risk Factors And Limitations

1. **Detection Signal Reliability**: The proposed plateau detection signals (loss curvature, gradient alignment, CKA) may be noisy in practice, leading to false detections or missed transitions. Mitigation: test multiple signals and use ensemble detection.
2. **Intervention Sensitivity**: The optimal intervention strength and duration may vary across datasets and architectures, requiring hyperparameter tuning that could reduce the annotation-free appeal. Mitigation: use a fixed, principled schedule (e.g., 10x weight decay for 5 epochs) and show robustness across a range.
3. **Multiple Shortcuts**: Real datasets may have multiple spurious features with different transition timings, making a single intervention insufficient. This is a genuine limitation we will acknowledge.
4. **Theoretical Grounding**: While motivated by NHT and grokking theory, the exact mechanism by which the intervention accelerates the transition may be hard to prove theoretically. The paper will focus on empirical validation with theoretical intuition.
5. **Benchmark Saturation**: Some benchmarks (Waterbirds, CelebA) are becoming saturated. We will include harder benchmarks and synthetic settings with controlled spuriosity rates to demonstrate clear gains.
6. **Computational Overhead**: CKA computation can be expensive for large models. Mitigation: use approximate CKA on a subset of samples, or prefer the cheaper gradient alignment signal.

