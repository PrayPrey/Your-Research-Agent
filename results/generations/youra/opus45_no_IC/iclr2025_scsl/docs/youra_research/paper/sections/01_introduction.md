# Introduction

Minority-group samples exhibit 8× higher loss at just 5% of training epochs compared to majority samples—a signature of simplicity bias that enables automatic detection without group labels. This finding reveals that training dynamics contain rich information about spurious correlation reliance, detectable far earlier than previously demonstrated.

## The Problem

Deep neural networks trained with empirical risk minimization (ERM) learn spurious correlations that fail on minority groups. A classifier distinguishing waterbirds from landbirds learns to rely on background (water vs. land) rather than the bird itself, because background provides a simpler, more consistent signal during training. When waterbirds appear on land—a minority of the training distribution—the model fails catastrophically.

Existing solutions require either group labels during training (Group DRO) or two-stage procedures that first train a biased model, then identify failing samples for upweighting (JTT). While effective, these approaches introduce computational overhead and cannot detect minority samples *during* a single training run. SPARE identifies spurious correlations early via simplicity bias, but uses fixed epoch thresholds rather than per-sample trajectory analysis.

The deeper gap is this: no method exploits the *continuous* per-sample loss trajectory as a discriminative signal. Binary misclassification captures only whether a sample is learned; loss trajectory shape captures *how* it is learned.

## Our Insight

We demonstrate that simplicity bias creates a measurable signature in loss dynamics. Because neural networks learn simpler patterns first, representations encode spurious features (background) with ~10 percentage points higher linear probe accuracy than core features (bird shape) throughout training. This asymmetry causes majority-group samples—which can be correctly classified via spurious features alone—to achieve low loss rapidly, while minority-group samples—which require core features—converge slowly with persistently higher loss.

At epoch 5 (5% of 100-epoch training), minority samples exhibit mean loss of 0.158 vs. 0.019 for majority samples (Mann-Whitney *p* < 10⁻¹⁴). This 8× difference persists as a statistically robust signal for minority detection.

## Contributions

1. **Detection Signal**: We establish that early-epoch loss magnitude provides a statistically significant signal for minority-group detection (6.6× improvement over random baseline) without requiring group labels.

2. **Mechanism Analysis**: Using linear probes, we verify that simplicity bias manifests as a ~10% accuracy gap between spurious and core feature encoding, explaining the loss trajectory difference between groups.

3. **Base-Rate Characterization**: We provide the first explicit analysis of precision limits under minority imbalance, showing that 33% precision at 5% minority rate represents 6.6× lift over random—a meaningful signal despite appearing modest in absolute terms.

4. **Timing Clarification**: With ImageNet-pretrained features, simplicity bias manifests as an *accuracy magnitude gap* rather than a *temporal gap* (both feature types peak at epoch 81), refining theoretical understanding of how pretraining affects learning dynamics.

The remainder of this paper presents related work (Section 2), methodology for loss trajectory tracking and linear probe analysis (Section 3), experimental setup on Waterbirds (Section 4), results demonstrating the detection signal and mechanism (Section 5), discussion of limitations (Section 6), and conclusions (Section 7).
