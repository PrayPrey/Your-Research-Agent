# Related Work

## Spurious Correlation and Group Robustness

Spurious correlations arise when features correlated with labels in training data do not hold in deployment. Sagawa et al. (2019) formalized this as a group robustness problem, introducing Group DRO to optimize worst-group accuracy (WGA). While effective, Group DRO requires group annotations during training—often unavailable in practice.

Subsequent work removes this requirement. JTT (Liu et al., 2021) trains an initial ERM model, identifies misclassified samples as likely minorities, and upweights them in a second training stage. This closes 75% of the gap to Group DRO on Waterbirds without training group labels. DFR (Izmailov et al., 2022) demonstrates that ERM already learns good features—the problem is the classifier head—and achieves 97% WGA by retraining only the last layer on a balanced validation set.

Our work differs from these two-stage approaches by characterizing the *continuous* loss trajectory signal, enabling detection during single-run training rather than after convergence.

## Early Training Dynamics

SPARE (Yang et al., 2023) exploits simplicity bias for early spurious correlation identification, achieving +21.1% WGA improvement while being 12× faster than prior methods. SPARE uses fixed epoch thresholds to identify when models become spuriously biased. LA-SSL (Zhu et al., 2023) observes that minority samples learn *slower* than majority samples and uses inverse learning speed for sampling weights.

We build on these insights but differ in approach: rather than fixed thresholds (SPARE) or aggregate learning speed (LA-SSL), we analyze per-sample loss trajectories as continuous discriminative signals. This enables finer-grained detection at the individual sample level.

## Simplicity Bias

Neural networks exhibit a bias toward learning simpler patterns first (Shah et al., 2020). In the presence of spurious correlations, this causes early-training representations to favor spurious features over core features. Our linear probe experiments quantify this bias: at epoch 5, probes classifying background (spurious) achieve 91.2% accuracy vs. 80.5% for probes classifying bird type (core)—a 10.7 percentage point gap that persists throughout training.

Unlike prior work that treats simplicity bias as a qualitative phenomenon to exploit, we provide quantitative characterization of its magnitude and temporal dynamics with pretrained features, finding that the bias manifests as an accuracy gap rather than a timing gap.

## Sample Difficulty and Curriculum Learning

The observation that some samples are harder than others underlies curriculum learning (Bengio et al., 2009) and hard example mining. Our finding—that minority samples have higher loss throughout training—is related but distinct: the difficulty is not intrinsic to the sample but emerges from the spurious correlation structure. Majority samples have redundant cues (both spurious and core features predict correctly), while minority samples require core feature learning.

## Positioning

| Method | Signal Type | Group Labels | Training Stages | Our Difference |
|--------|------------|--------------|-----------------|----------------|
| Group DRO | Worst-group loss | Required | 1 | No labels required |
| JTT | Binary misclassification | Validation only | 2 | Continuous trajectory |
| DFR | Feature reweighting | Balanced val set | 1.5 | Detection, not intervention |
| SPARE | Fixed epoch threshold | None | 1 | Per-sample trajectory |
| **Ours** | **Loss magnitude at early epoch** | **None** | **1** | — |

Our contribution is the characterization of loss trajectory as a continuous detection signal, with explicit quantification of the simplicity bias mechanism and base-rate precision limits.
