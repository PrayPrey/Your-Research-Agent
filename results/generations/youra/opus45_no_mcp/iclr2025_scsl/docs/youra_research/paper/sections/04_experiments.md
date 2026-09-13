# Experimental Setup

We design experiments to answer five questions, each corresponding to a sub-hypothesis from our verification plan:

1. **Existence (H-E1)**: Does the crystallization zone exist as a detectable phenomenon?
2. **Mechanism (H-M1)**: Does gradient starvation causally precede crystallization?
3. **Commitment (H-M2)**: Is post-crystallization commitment irreversible under ERM?
4. **Detection (H-M3)**: Can second derivative analysis reliably detect crystallization?
5. **Timing (H-M4)**: Is crystallization timing consistent across benchmarks?

## Datasets

We evaluate on three standard spurious correlation benchmarks from the WILDS suite:

**Waterbirds** (Sagawa et al. 2020): Binary classification of bird species (waterbirds vs. landbirds) with background as spurious attribute. Training set: 4,795 images. Spurious correlation: ~95% of waterbirds appear on water backgrounds. Worst group: waterbirds on land.

**CelebA** (Liu et al. 2015): Binary classification of hair color (blond vs. non-blond) with gender as spurious attribute. Training set: 162,770 images. Spurious correlation: ~94% of blond individuals are female. Worst group: blond males.

**ColoredMNIST** (Arjovsky et al. 2019): Digit classification with color as spurious attribute. Training set: 60,000 images. Spurious correlation: 95% of digits have color correlated with label. Worst group: digits with anti-correlated color.

These benchmarks span different image types (natural photos vs. synthetic), spurious correlation strengths (94-95%), and worst-group sizes. Together they test whether crystallization is a general phenomenon.

## Model Architecture

We use ResNet-50 pretrained on ImageNet for Waterbirds and CelebA, and a smaller CNN for ColoredMNIST (standard practice for this benchmark). The final classification layer is randomly initialized and trained from scratch.

We focus on ResNet-50 to enable comparison with prior work on group robustness. Extension to vision transformers (ViT) is noted as a limitation and future direction.

## Training Configuration

All experiments use identical hyperparameters to isolate the crystallization phenomenon from optimizer confounds:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Optimizer | SGD | Standard for benchmark comparisons |
| Momentum | 0.9 | Standard setting |
| Learning rate | 0.001 | Constant (no schedule) |
| Weight decay | 1e-4 | Light regularization |
| Batch size | 128 | Balanced compute/variance |
| Random seeds | 5 | Statistical reliability |

The constant learning rate is critical: learning rate decay could confound crystallization detection by artificially changing optimization dynamics mid-training.

## Baseline

We compare against ERM (Empirical Risk Minimization)—standard cross-entropy training without group balancing or robust optimization. ERM serves as the reference condition where crystallization occurs naturally.

We do not evaluate Group DRO, JTT, or DFR in this work, as our goal is to characterize crystallization under standard training, not to propose a new robustness method.

## Evaluation Metrics

**Primary: Detection Rate.** Fraction of training runs where a valid crystallization peak is detected using our methodology. Target: >80%.

**Secondary:**
- **Timing Variance**: Standard deviation of crystallization epoch across seeds. Target: <5 epochs.
- **Signal-to-Noise Ratio (SNR)**: Peak prominence divided by baseline noise. Target: >2.0.
- **Normalized Timing**: Crystallization epoch as percentage of total training. Hypothesis: 15-40%.

**Mechanism Verification:**
- **Gradient Ratio Inflection**: Epoch where gradient ratio shows maximum rate of change.
- **Temporal Precedence**: Whether gradient inflection precedes WGA peak.

**Commitment Verification:**
- **Spurious Probe Accuracy**: Linear probe predicting spurious attribute from frozen embeddings.
- **Core Probe Accuracy**: Linear probe predicting true label from frozen embeddings.
- **Probe Stability**: Whether spurious probe accuracy is maintained post-crystallization.

## Experimental Protocol

For each benchmark and seed:
1. Initialize model with pretrained weights (except final layer)
2. Train with ERM, checkpointing every epoch
3. Compute WGA at each checkpoint
4. Apply 5-epoch smoothing and compute second derivative
5. Detect crystallization peak using prominence threshold
6. Extract gradient ratios and probe accuracies at key epochs
7. Record timing, SNR, and verification metrics

Total experiments: 3 benchmarks × 5 seeds = 15 training runs. Each run produces dense checkpoint data enabling post-hoc analysis.
