# Experimental Setup

We design experiments to answer three research questions that test our central claim: Batch Normalization amplifies worst-group gaps via gradient-level mechanisms during early training.

## Research Questions

**RQ1 (Existence):** Does Batch Normalization exhibit a higher worst-group accuracy gap than Layer Normalization when both architectures reach equivalent average accuracy on a spurious correlation task?

*Maps to Contribution 1 (Introduction): Quantitative existence proof of 9.41pp gap difference.*

**RQ2 (Mechanism):** Does Batch Normalization show measurably higher gradient flow toward spurious-aligned samples during early training compared to Layer Normalization?

*Maps to Contribution 2 (Introduction): Gradient-level mechanistic explanation.*

**RQ3 (Consistency):** Do architectural rankings (by worst-group gap at matched accuracy) remain consistent across different spurious correlation datasets?

*Maps to generalization claim: temporal signatures are architectural, not dataset-specific.*

## Datasets

We evaluate on spurious correlation benchmarks where group labels are available for worst-group accuracy computation.

**Synthetic Spurious Correlation Dataset (Primary):**  
A binary classification task with 5000 training samples and 1000 test samples. Each sample belongs to one of four groups: (label 0, spurious feature 0), (label 0, spurious feature 1), (label 1, spurious feature 0), (label 1, spurious feature 1). The dataset exhibits 90% spurious correlation: 90% of label 0 samples have spurious feature 0, and 90% of label 1 samples have spurious feature 1. The remaining 10% are minority groups where label and spurious feature conflict.

*Rationale:* This synthetic dataset serves as a proof-of-concept, enabling controlled evaluation of the BN-LN gap hypothesis. It was used due to WILDS Waterbirds server unavailability (HTTP 500 error during download). While synthetic data demonstrates workflow validity, real dataset validation is planned as future work (see Limitations).

**Waterbirds (Planned):**  
The Waterbirds dataset (Sagawa et al., 2020) contains 4795 training images and 1199 test images of landbirds and waterbirds on land or water backgrounds. The spurious correlation is 95%: 95% of landbirds appear on land backgrounds, and 95% of waterbirds appear on water backgrounds. Group labels partition samples into four groups (landbird-land, landbird-water, waterbird-land, waterbird-water), with worst-group accuracy measured as the minimum accuracy across these four groups.

*Rationale:* Waterbirds is the standard benchmark for spurious correlation research, with established baselines (Group DRO: 91.4% worst-group, ERM: 72.6% worst-group). It enables direct comparison with prior work and validates findings on real image data.

**CelebA (Planned):**  
The CelebA dataset (Liu et al., 2015) contains images of celebrities annotated with binary attributes (e.g., "Blond Hair", "Male"). Following Sagawa et al. (2020), we use the task of predicting "Blond Hair" given "Male" as a spurious feature (95% correlation: blond hair strongly correlated with female gender in training data). Group labels partition samples into four groups.

*Rationale:* CelebA tests generalization across datasets with similar spurious structure (binary, stochastic) but different content (human faces vs. natural scenes).

## Baselines and Comparisons

**Architectural Comparison:**  
Our primary comparison is ResNet-18-BN vs. ResNet-18-LN (same depth, same parameter count within 1%). This controlled comparison isolates the effect of normalization type (batch-level vs. instance-level) while holding all other architectural factors constant.

**Baseline: Empirical Risk Minimization (ERM):**  
Standard training minimizes average cross-entropy loss without group reweighting. Both ResNet-18-BN and ResNet-18-LN are trained with ERM to compare their worst-group gaps under identical optimization objectives.

*Rationale:* Group DRO (Sagawa et al., 2020) requires group labels and modifies the loss function. Our hypothesis is that architectural choice (LN vs. BN) alone can reduce worst-group gaps without algorithmic intervention. ERM baseline enables fair comparison.

**Comparison with Group DRO (Discussion only):**  
Sagawa et al. (2020) report Waterbirds worst-group accuracy of 91.4% for ResNet-50 with Group DRO (vs. 72.6% for ERM). We discuss how our approach (ResNet-18-LN with ERM) compares to this baseline in Section 6.

## Evaluation Metrics

**Average Accuracy (Avg Acc):**  
Standard classification accuracy over all test samples.

**Worst-Group Accuracy (WGA):**  
Minimum accuracy across all four groups (label × spurious feature). For Waterbirds: $\min(\text{Acc}_{\text{landbird-land}}, \text{Acc}_{\text{landbird-water}}, \text{Acc}_{\text{waterbird-land}}, \text{Acc}_{\text{waterbird-water}})$.

**Worst-Group Gap:**  
$\text{Gap} = \text{Avg Acc} - \text{WGA}$. Larger gaps indicate stronger spurious reliance.

**Gradient Ratio (for RQ2):**  
$r = \frac{\|g_{\text{maj}}\|_2}{\|g_{\text{min}}\|_2}$, where $g_{\text{maj}}$ and $g_{\text{min}}$ are gradients with respect to `conv1.weight` for majority-group (spurious-aligned) and minority-group (spurious-misaligned) samples, respectively.

## Success Criteria

**RQ1 (Existence):**  
- Null hypothesis $H_0$: $\text{Gap}_{\text{BN}} - \text{Gap}_{\text{LN}} < 5.0$ percentage points at 90% average accuracy.
- Alternative $H_1$: $\text{Gap}_{\text{BN}} - \text{Gap}_{\text{LN}} \geq 5.0$ percentage points.
- Success: Reject $H_0$ with *p* < 0.05, Cohen's *d* ≥ 0.8, and at least 8/10 seeds reaching 90% average accuracy for both architectures.

**RQ2 (Mechanism):**  
- Null hypothesis $H_0$: $r_{\text{BN}} - r_{\text{LN}} < 20\%$ during epochs 0–19.
- Alternative $H_1$: $r_{\text{BN}} - r_{\text{LN}} \geq 20\%$.
- Success: Reject $H_0$ with *p* < 0.05, Cohen's *d* ≥ 0.5.

**RQ3 (Consistency):**  
- Null hypothesis $H_0$: Spearman rank correlation $\rho < 0.6$ between Waterbirds and CelebA architecture rankings.
- Alternative $H_1$: $\rho \geq 0.8$ (strong positive correlation).
- Success: $\rho > 0.8$, *p* < 0.05, no rank reversals.

## Experimental Protocol

All experiments use 10 random seeds ([0, 1, 2, ..., 9]) for statistical power. For each seed:

1. Initialize ResNet-18-BN and ResNet-18-LN with He normal initialization.
2. Train both architectures on the training set for up to 100 epochs (20 epochs for proof-of-concept on synthetic data).
3. Log average accuracy, worst-group accuracy, and per-group accuracies every epoch.
4. For RQ2, instrument `conv1.weight` with gradient hooks during epochs 0–19; compute gradient ratio per batch; average over epochs.
5. Identify the epoch where each architecture first reaches 90% average accuracy.
6. Record worst-group gap at those epochs.

Statistical tests (paired *t*-tests, Cohen's *d*) are performed across the 10 seeds to evaluate success criteria.

## Implementation Details

**Framework:** PyTorch 1.13 with torchvision 0.14  
**Hardware:** CPU (proof-of-concept; GPU planned for production)  
**Training time:** ~2 hours per seed on CPU for 20 epochs (synthetic data)  
**Hyperparameters:** See Methodology (Section 3) — constant LR 0.01, SGD with momentum 0.9, batch size 64, weight decay $10^{-4}$  
**Reproducibility:** All random seeds fixed (`torch.manual_seed()`, `numpy.random.seed()`, `random.seed()`), deterministic CUDA enabled
