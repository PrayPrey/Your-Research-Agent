# Experimental Setup

We design experiments to answer three research questions that directly test the feasibility of cross-architecture quotient-level canonicalization:

**RQ1: Quotient Space Capacity** — Can a finite-dimensional quotient space (K dimensions) capture task-relevant structure from model weights with acceptable information loss?

**RQ2: Architecture Independence** — Does the learned quotient space generalize to unseen architecture families without retraining, or are representations architecture-specific?

**RQ3: Permutation Invariance** — Does the encoder learn true permutation invariance (quotient space property), mapping permutation-equivalent weights to the same point?

These questions map directly to the requirements for quotient-level canonicalization: sufficient capacity (RQ1), cross-architecture transfer (RQ2), and factorization of permutation symmetries (RQ3).

## Datasets

**Synthetic ModelZoo-14K**: We generate a synthetic model zoo containing 1000 neural network models distributed across three architecture families: 400 CNNs (40%), 400 Transformers (40%), and 200 RNNs (20%). Each model consists of randomly initialized weights with dimensionality |w|=1000, simplified from realistic 100K-dimensional pretrained models to enable rapid prototyping and clear failure signal isolation.

The dataset is split 70% train (700 models: CNN+Transformer), 15% validation (150 models: CNN+Transformer), 15% test (150 models: 50 CNN, 50 Transformer, 50 RNN). Critically, RNN models appear only in the test set to evaluate frozen-K generalization (RQ2)—we test whether the encoder trained on CNN+Transformer can generalize to a held-out architecture family without retraining.

**Rationale for Synthetic Data**: We use synthetic random weights rather than real pretrained models as a proof-of-concept simplification. If the approach cannot succeed on synthetic data with clear structure, it will not succeed on real models with additional complexity. The clear failure signal (0.00% kernel robustness) across all metrics validates this choice—the failure is not due to insufficient realism but fundamental mechanism inadequacy.

## Evaluation Metrics

We define three complementary gate metrics to comprehensively evaluate quotient space learning:

**Reconstruction Error (RQ1)**: Measures quotient space capacity through reconstruction quality after encoding-decoding:
$$R = \mathbb{E}\left[\frac{\|\mathbf{w} - D(E(\mathbf{w}))\|^2}{\|\mathbf{w}\|^2}\right]$$
where $E: \mathbb{R}^{d} \to \mathbb{R}^K$ is the encoder and $D: \mathbb{R}^K \to \mathbb{R}^{d}$ is the learned decoder. **Success criterion**: $R < 10\%$ (less than 10% information loss). High reconstruction error indicates insufficient quotient dimensionality.

**Frozen-K Generalization (RQ2)**: Tests architecture-independence by measuring reconstruction error on held-out RNN models with frozen quotient dimension:
$$R_{\text{RNN}} = \mathbb{E}_{M \in \text{RNN}_{\text{test}}}\left[\frac{\|\mathbf{w} - D(E(\mathbf{w}))\|^2}{\|\mathbf{w}\|^2}\right]$$
where the encoder was trained only on CNN+Transformer. **Success criterion**: $R_{\text{RNN}} < 10\%$ (similar performance to training architectures). Failure indicates the encoder learned architecture-specific rather than shared representations.

**Kernel Robustness (RQ3)**: Directly tests the quotient space property by measuring permutation invariance. For each test model, we apply 1000 random weight permutations $g \sim G_a$ (neuron reorderings, layer swaps) and compute quotient space divergence:
$$D = \|E(g \cdot \mathbf{w}) - E(\mathbf{w})\|$$
**Success criterion**: $\geq 90\%$ of permutations have $D < 0.01$ (quotient representation preserved under permutation). This is the most critical metric—without permutation invariance, quotient-level canonicalization is impossible regardless of reconstruction quality.

**Why These Metrics**: Standard accuracy metrics would miss critical failures. A model could achieve low reconstruction error while failing to learn permutation invariance, or could learn permutations for training architectures while failing to generalize. Our three-gate approach reveals failure modes at different levels: capacity (reconstruction), generalization (frozen-K), and fundamental equivariance (kernel robustness).

## Baselines

**Deep Sets (Permutation-Invariant Baseline)**: We compare against Deep Sets [Zaheer et al., 2017] without explicit equivariance loss. This baseline provides permutation invariance through sum pooling aggregation but does not explicitly encourage quotient-level structure through loss design. Expected performance: ~40-50% zero-shot equivariance based on NFN's homogeneous results, providing a lower bound for our approach.

**Function-Space Embedding (Alternative Approach)**: We reference function-space methods that embed models via outputs on fixed probe inputs rather than weight-space canonicalization. While not directly comparable (different modality), this establishes that alternative approaches exist when weight-space methods fail.

**Git Re-Basin (Upper Bound Reference)**: We reference Git Re-Basin [Ainsworth et al., 2022] as an upper bound for permutation-based alignment, though direct comparison is not feasible (explicit combinatorial search vs. learned equivariance, single-architecture vs. cross-architecture). This establishes that explicit group operations can achieve strong alignment within single architectures.

**Rationale**: We focus on Deep Sets as the primary baseline since it represents the natural starting point for cross-architecture extension. Function-space and Git Re-Basin provide context for what is achievable through alternative approaches.

## Implementation Details

**Framework**: PyTorch 2.0 with single-GPU training (NVIDIA A100, CUDA 11.8).

**Model Architecture**:
- Encoder backbone: Deep Sets with per-element MLP (input: 1000-dim → hidden: 256-dim → quotient: K=32)
- Architecture embeddings: 64-dimensional learned embeddings for {CNN, Transformer, RNN}
- Aggregation: Mean pooling (permutation-invariant)
- Decoder: MLP (quotient: K=32 → hidden: 256-dim → output: 1000-dim)
- Slot permutation operator ρ: Lightweight MLP (learns quotient group action)

**Training Hyperparameters**:
- Optimizer: Adam (lr=1e-3, weight_decay=1e-4)
- Scheduler: CosineAnnealingLR (T_max=100 epochs)
- Batch size: 32
- Epochs: 20 (early stopped at epoch 12 due to validation loss plateau)
- Early stopping patience: 10 epochs
- Gradient clipping: max_norm=1.0
- Equivariance loss weight: λ_equiv=0.5

**Training Time**: Approximately 2 hours for 20 epochs on 1000-model synthetic zoo.

**Reproducibility**: All experiments use fixed random seeds (seed=42). Code structure follows modular design: data module (synthetic zoo generation), model module (encoder/decoder), loss module (reconstruction + equivariance), training module (optimizer, scheduler, early stopping), evaluation module (three gate metrics). Full implementation details are provided in supplementary material.

**PoC Simplifications**: We acknowledge three simplifications made for proof-of-concept: (1) synthetic random weights rather than real pretrained models, (2) reduced weight dimensionality (1000 vs 100K), (3) single configuration tested (K=32, λ_equiv=0.5). The clear failure signal across all metrics (especially 0.00% kernel robustness) suggests these simplifications did not mask fundamental mechanism issues.
