# Experimental Setup

We design experiments to answer the following questions:

**RQ1:** Do DWS and NFT architectures encode measurably different inductive biases?

**RQ2:** Does this inductive bias difference translate to task-dependent performance advantages?

**RQ3:** Is there a statistically significant interaction effect between architecture and task type?

## Datasets

We evaluate on synthetic weight-space datasets designed to isolate architecture-task interactions:

### MNIST-INR Dataset (Existence/Mechanism Validation)

Implicit Neural Representation (INR) networks trained on MNIST digits, following Zhou et al. [2024]. Each sample is a complete neural network's weights with a class label.

| Statistic | Value |
|-----------|-------|
| Training samples | 600 |
| Test samples | 200 |
| Weight dimensions | ~40K per model |
| Classes | 10 (digits 0-9) |

**Why chosen:** Standard benchmark for weight-space learning; enables comparison with prior work on INR classification.

### Synthetic Property Prediction Dataset (Interaction Testing)

Two-task dataset designed to test architecture-task interaction:

| Task | Target | Type | Signal Type |
|------|--------|------|-------------|
| Backdoor | Binary (clean/backdoored) | Classification | Local perturbation |
| Accuracy | Predicted accuracy (0-100) | Regression | Global statistic |

**Backdoor signal:** Localized weight perturbation in a randomly selected layer and row, simulating trojan injection.

**Accuracy signal:** Sigmoid of aggregated weight statistics (mean norms, layer-wise means), representing holistic model properties.

**Why chosen:** Isolates local vs global signal processing to test hypothesized architecture-task alignment.

## Baselines

We compare three architectures representing different inductive biases:

### MLP Baseline
Standard multi-layer perceptron that flattens weight matrices into vectors.
- **Why included:** Establishes performance floor when permutation symmetry is ignored; tests whether equivariance provides any benefit.
- **Configuration:** 3 hidden layers, ~9.8M parameters.

### Deep Weight Space (DWS) [Navon et al., 2023]
Equivariant layers that preserve weight locality through structured operations.
- **Why included:** Tests whether locality bias helps local anomaly detection (backdoor).
- **Configuration:** 3 equivariant layers, ~4.9M parameters.

### Neural Functional Transformer (NFT) [Zhou et al., 2024]
Transformer with self-attention across all weight tokens.
- **Why included:** Tests whether global attention helps holistic property aggregation (accuracy).
- **Configuration:** 4 attention layers, 4 heads, ~5.3M parameters.

**Note on parameter mismatch:** Architectures are not perfectly matched (4.9M-9.8M range). However, MLP has the MOST parameters yet underperforms NFT on accuracy prediction, suggesting results reflect inductive bias rather than capacity.

## Implementation Details

All experiments implemented in PyTorch with identical training procedures across architectures.

**Hyperparameters:**

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning rate | 1e-4 |
| Weight decay | 1e-2 |
| Batch size | 64 |
| Epochs | 30 (h-e1, h-m1), 10 (h-m2), 100 (h-m3) |
| Seeds | [42, 123, 456] (3 runs each) |

**Compute Resources:** Single NVIDIA GPU, ~3 hours total training time.

**Data Processing:** Z-score normalization of weight matrices before input.

## Evaluation Metrics

### Inductive Bias Measurement
- **Coefficient of Variation (CoV):** Standard deviation divided by mean of layer-wise weight update magnitudes. Higher CoV indicates more localized processing.

### Task Performance
- **AUC (Backdoor):** Area under ROC curve for binary backdoor classification.
- **RMSE (Accuracy):** Root mean squared error for accuracy prediction regression.

### Interaction Testing
- **Two-way ANOVA:** Tests for significant interaction between architecture and task type.
- **Statistical significance:** p < 0.05 threshold.

## Hypotheses Tested

| ID | Hypothesis | Gate | Success Criterion |
|----|------------|------|-------------------|
| h-e1 | Locality bias difference exists | MUST_WORK | Measurable pattern difference |
| h-m1 | Architecture encodes different biases | MUST_WORK | DWS CoV > NFT CoV |
| h-m2 | Locality reduces sample complexity | SHOULD_WORK | DWS > NFT at 25% data |
| h-m3 | Task-dependent optimal bias | SHOULD_WORK | Significant interaction |
