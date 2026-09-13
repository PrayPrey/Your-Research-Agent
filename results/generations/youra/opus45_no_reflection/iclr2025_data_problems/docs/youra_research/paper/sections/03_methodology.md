# Methodology

## Experimental Design

We design experiments to isolate the effect of attention structure on attribution method performance. The key challenge is controlling for confounding factors—model size, depth, training procedure—that could obscure architecture-specific effects.

### Architecture Selection

We compare BERT-base-uncased (110M parameters, 12 layers) with GPT-2 (124M parameters, 12 layers). Both models:
- Have identical layer counts (12 transformer blocks)
- Have similar parameter counts (~110-125M)
- Use the same hidden dimension (768)
- Were pretrained on large text corpora

The primary architectural difference is attention structure: BERT uses bidirectional attention (all positions attend to all positions), while GPT-2 uses causal attention (each position attends only to earlier positions).

### Task Selection

We use SST-2 binary sentiment classification from the GLUE benchmark. This task is suitable because:
- Both architectures can perform it natively (BERT: [CLS] classification, GPT-2: last-token classification)
- Standard benchmark for influence function evaluation
- Binary classification simplifies mislabeled detection analysis

We inject 5% random label noise (standard rate from Koh & Liang 2017) to create ground-truth mislabeled examples.

### Training Protocol

Both models are fine-tuned with identical hyperparameters:
- Optimizer: AdamW
- Learning rate: 2e-5
- Epochs: 3
- Batch size: 32
- For GPT-2: pad token set to EOS token

This ensures any performance differences are due to architecture, not training dynamics.

## Attribution Methods

We evaluate three representative methods spanning the approximation spectrum.

### TRAK (Random Projection)

TRAK (Park et al., 2023) projects model gradients to a random subspace and performs linear regression in this space. We use the official implementation with projection dimensions {64, 256, 1024} to capture the efficiency-accuracy trade-off.

The random projection mechanism is architecture-agnostic by design—it treats gradients as vectors without exploiting structure. We hypothesize this provides robustness to architecture variation.

### EK-FAC (Curvature Approximation)

EK-FAC (Grosse et al., 2023) approximates the Hessian using Kronecker-factored eigenbasis decomposition. We use kronfluence with projection dimensions {64, 256, 1024} matching TRAK.

EK-FAC's Kronecker assumption imposes structure on the Hessian approximation. Prior work suggested this fits causal attention patterns, potentially favoring decoder architectures.

### TracIn (First-Order)

TracIn (Pruthi et al., 2020) sums gradient dot-products at checkpoints saved during training. We evaluate with {1, 2, 3} checkpoints, corresponding to saves at each epoch.

TracIn ignores curvature, relying solely on gradient alignment. Dense bidirectional gradients in encoders may provide richer information for this approximation.

## Evaluation Metrics

### Primary Metric: Mislabeled Detection AUC

For each test example, we compute influence scores for all training examples, rank by influence (most harmful first), and measure AUC for detecting the 5% mislabeled examples. Higher AUC indicates better attribution quality.

### Secondary Metrics

- **Efficiency-Accuracy Ratio**: AUC / gradient computations
- **Cross-Architecture Difference**: |AUC_BERT - AUC_GPT2|

## Causal Mechanism Verification

Beyond end-to-end performance, we verify the hypothesized causal chain:

**Step 1 (h-m1):** Measure attention sparsity to confirm structural difference exists.
- Metric: Upper-triangle sparsity in attention weights
- Threshold: BERT < 10%, GPT-2 > 99%

**Step 2 (h-m2):** Measure Hessian eigenvalue spectrum to confirm curvature difference.
- Metric: Top eigenvalue relative difference
- Threshold: >10% difference

**Step 3 (h-m3):** Verify all methods show measurable architecture effects.
- Metric: Any method with >10% relative AUC difference
- Purpose: Confirms architecture-method interaction exists

**Step 4 (h-m4):** Test predictions about specific architecture-method pairings.
- P1: EK-FAC GPT-2 > BERT (p<0.05)
- P2: TracIn BERT > GPT-2 (p<0.05)
- P3: TRAK |diff| < 5%

This multi-step verification ensures we understand *why* methods behave differently, not just *that* they do.
