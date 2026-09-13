# Related Work

Our work connects two research threads that have developed largely independently: *training dynamics analysis*, which studies how neural networks learn individual examples over time, and *spurious correlation robustness*, which addresses model failures on minority subgroups. We review each thread and identify the gap at their intersection.

## Training Dynamics and Per-Sample Learning

Understanding how neural networks learn individual training examples has been an active research area. Toneva et al. [2018] introduced the concept of *forgetting events*—transitions where a training example goes from correctly to incorrectly classified between epochs. They showed that certain examples are forgotten repeatedly while others are never forgotten, and that forgettable examples transfer across architectures. This work established that per-sample training dynamics carry meaningful information beyond aggregate loss curves.

Subsequent work has explored training dynamics for various purposes. Li et al. [2025] extract 142-dimensional training dynamics (TD) features per sample and demonstrate their utility for noisy label detection and class imbalance learning. Chen et al. [2025] track per-sample privacy vulnerability throughout training, discovering correlations between learning difficulty and membership inference risk. Leybzon and Kervadec [2024] study memorization dynamics in language models, finding that examples memorized early are more likely to remain "crystallized."

However, this line of work focuses on general notions of sample difficulty, memorization, or privacy—not the specific signature of spurious correlation learning. While training dynamics features may correlate with various sample properties, no prior work has examined whether they can specifically identify samples affected by spurious correlations.

## Spurious Correlations and Group Robustness

Spurious correlations cause models to exploit statistical shortcuts that do not generalize [Geirhos et al., 2020]. The standard solution is Group Distributionally Robust Optimization (GroupDRO) [Sagawa et al., 2020], which minimizes worst-group loss by upweighting minority groups during training. GroupDRO achieves strong worst-group accuracy but requires group annotations during training.

Recent work has sought to reduce annotation requirements. Just Train Twice (JTT) [Liu et al., 2021] trains an initial ERM model, identifies high-error samples as likely minority examples, and upweights them in a second training run. Spread Spurious Attribute (SSA) [Nam et al., 2022] uses pseudo-attribute prediction to estimate group membership. Probabilistic Group DRO [Ghosal and Li, 2023] extends GroupDRO to soft group assignments. GIC [Han and Zou, 2024] improves group inference accuracy by leveraging correlations between spurious attributes and labels.

These methods focus on *intervention*—correcting spurious reliance—rather than *diagnosis*—identifying which samples are affected. JTT's error-based identification captures some minority samples but conflates spurious-correlation-affected samples with generally difficult examples. None of these methods leverage the temporal evolution of per-sample losses; they rely on single-epoch snapshots or accuracy signals.

## Gradient-Based Sample Analysis

An alternative approach analyzes gradient information to characterize samples. Gradient norms have been used for sample difficulty estimation [Katharopoulos and Fleuret, 2018] and importance sampling [Johnson and Guestrin, 2018]. In prior exploratory work, we found that gradient norms can identify minority samples with AUC = 0.914 on Waterbirds, but this detection did not translate into successful intervention—highlighting that detection and correction are distinct challenges.

Maini et al. [2023] use gradient accounting to study memorization localization, finding that memorization is confined to small sets of neurons. Gilmer et al. [2021] analyze loss Hessian evolution to understand training instability. These gradient-based approaches provide complementary perspectives but do not specifically target spurious correlation signatures.

## The Gap: Training Dynamics for Spurious Correlation Detection

Our work addresses the intersection missing from prior research: **Can training dynamics specifically identify spurious correlation-affected samples?** 

Prior training dynamics work (Toneva, Li) characterizes general difficulty without targeting spurious correlations. Prior spurious correlation work (GroupDRO, JTT) focuses on intervention, not trajectory-based diagnosis. Gradient-based approaches provide single-epoch signals rather than temporal patterns.

We contribute the first analysis of whether loss trajectory divergence is *specific* to spurious feature conflict—not just correlated with generic sample difficulty. Our controlled experiment with GroupDRO and variance-matched random reweighting directly tests this specificity, distinguishing our approach from prior trajectory analysis that does not address the spurious-specificity question.
