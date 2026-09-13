# Related Work

## Spurious Correlations and Worst-Group Accuracy

Spurious correlations — statistical associations between input features and labels that hold in training data but not at test time — are a well-documented failure mode of empirical risk minimization [Sagawa et al., 2019; Arjovsky et al., 2019]. On the Waterbirds benchmark [Sagawa et al., 2019], ResNet-50 models trained with ERM exploit the background attribute (land vs. water) as a shortcut for bird species classification, achieving high average accuracy but failing on minority groups (e.g., landbirds on water). WGA — the accuracy on the worst-performing group — has become the standard measure for spurious correlation robustness.

Multiple training-time interventions improve WGA over ERM: GroupDRO [Sagawa et al., 2019] reweights groups dynamically; JTT [Liu et al., 2021] upweights misclassified examples from a warm-started ERM model; CVaR-DRO minimizes the conditional value at risk; SAM [Foret et al., 2021] improves sharpness-aware generalization. All achieve WGA improvements on Waterbirds, yet *why* they improve — specifically, what mechanism drives the improvement — remains underspecified in existing work. Our study addresses this mechanistic gap for GroupDRO and DFR.

## Deep Feature Reweighting and Last-Layer Retraining

Kirichenko et al. [2022] showed that much of WGA improvement can be achieved by simply retraining the final classification head on a group-balanced held-out set, while freezing the backbone entirely (DFR). This "last-layer retraining" finding was initially interpreted as evidence that ERM backbones already contain sufficient information to separate spurious and core features — head recalibration just redirects attention toward the core features. Subsequent work [LaBonte et al., 2023; Hill et al., 2025] has refined this understanding: the key condition is group balance in the held-out set used for head retraining, not neural collapse or other architectural properties.

Importantly, DFR's architectural design — freeze backbone, retrain head — means that DFR and ERM backbones should be *identical at the weight level*. Izmailov et al. [2022] release both DFR and ERM checkpoints (3 seeds) but do not explicitly quantify this backbone identity empirically. We fill this gap in H-P0: cosine similarity = 1.000000 ± 1e-14 for all 3 seed pairs, establishing the structural DFR−ERM equivalence with precision.

Le et al. [2023] provide a cautionary counterpoint: in medical imaging domains, DFR (last-layer retraining) is insufficient when backbone features still strongly encode spurious attributes, and backbone-level intervention is required. This work corroborates our framework: the sufficiency of head-only retraining depends on the backbone's spurious encoding level, which is precisely the quantity we measure.

## Feature Analysis of Robustification Methods

Izmailov et al. [2022] provide the most directly related work: they use a spurious-DFR proxy (s-DFR, using the spurious attribute as the classification target for head retraining) to estimate how much information ERM backbones encode about spurious attributes. Their analysis yields an approximate 85% spurious attribute accuracy for ERM backbone features. However, they do not report per-method, per-seed probe accuracy values with statistical tests comparing GroupDRO to ERM. Our study fills this gap: per-seed probe accuracy for all 12 checkpoints, one-sided paired t-test, pre-registered thresholds.

Murotkar et al. [2024] use sklearn L-BFGS linear probes on frozen ResNet-50 layer4 features for spurious feature disentanglement — establishing the probe methodology we adopt. Their focus is on disentanglement rather than inter-method comparison. We adapt their protocol for the backbone-vs-head diagnostic question.

Park et al. [2025] introduce SCER (Spurious Correlation Elimination via Regularization), which *explicitly* regularizes the spurious feature subspace during training to reduce spurious linear decodability. SCER demonstrates a causal link between reducing background decodability and improving WGA — a link our study validates from the opposite direction: GroupDRO *implicitly* achieves what SCER does explicitly, as our probe results confirm. Both SCER and our study use linear decodability as the target construct; SCER makes it an optimization objective while we measure it diagnostically.

Raymond et al. [2026] provide corroborating evidence that GroupDRO reshapes backbone representations across all layers in representation space, consistent with our weight-difference (H-M2) and probe accuracy (H-M3) findings. Their work focuses on representation geometry; ours provides quantitative decodability evidence with pre-registered statistical tests.

## Linear Probing for Representation Analysis

Linear probing — training a linear classifier on frozen features — is a standard tool for analyzing what information backbone representations encode [Alain and Bengio, 2016]. The conventions we follow (sklearn L-BFGS, C=1e9, frozen layer4 features with global average pooling) match those established by Kirichenko et al. [2022] and Murotkar et al. [2024]. Sagawa et al. [2019] use WGA as a representation quality proxy; our probe provides a more direct measure of spurious-attribute linear decodability from the backbone.

A key methodological consideration from our earlier failed attempts (full-model gradient cosine similarity, head Hessian eigenvalues) is that backward-pass-based metrics are sensitive to optimizer geometry and dimensionality confounds. Forward-pass linear probe accuracy — bounded [0,1], numerically stable, directly interpretable — avoids these confounds. Our probe design is motivated by this negative experience, as detailed in Section 3.

## Positioning

Relative to prior work, our contribution is the *measurement* of backbone spurious encoding across methods with pre-registered statistical tests and per-seed granularity, enabling the backbone-vs-head typology. We do not propose a new robustification method; we provide a diagnostic framework for understanding existing ones. The closest prior measurement (Izmailov et al. [2022] s-DFR proxy) lacks per-seed statistical testing and does not compare GroupDRO to ERM on this metric. Our study fills this gap.
