# Experimental Setup

We design experiments to answer two fundamental questions about Mamba-2 duality for distillation:

**RQ1 (Existence):** Do duality equations produce valid, non-divergent SSM parameters from Transformer attention weights?

**RQ2 (Mechanism):** Does duality-based initialization provide lower reconstruction error than random initialization?

These questions test the two stages of our verification protocol: parameter validity (RQ1) and structural fidelity (RQ2). A "yes" to RQ1 alone demonstrates technical feasibility but not utility; a "yes" to RQ2 would demonstrate that duality captures meaningful attention structure.

## Dataset

We evaluate on WikiText-103 [Merity et al., 2017], a standard language modeling benchmark containing over 100 million tokens of high-quality Wikipedia text.

| Property | Value |
|----------|-------|
| Source | HuggingFace Datasets |
| Split | Validation |
| Samples | 100 (h-e1), 500 (h-m1) |
| Sequence Length | 64-512 tokens |
| Tokenization | BERT WordPiece |

**Why WikiText-103:** Provides diverse, natural text for evaluating attention pattern conversion. The validation split avoids train/test contamination while offering sufficient samples for statistical significance.

## Models

### Teacher Model

**BERT-base-uncased** [Devlin et al., 2019]: 12-layer Transformer encoder with 768 hidden dimensions, 12 attention heads, and 110M parameters. We use the pretrained HuggingFace checkpoint.

### Student Architecture

**Mamba-12:** 12-layer SSM with matching hidden dimension (768) and state dimension d_state = 64. Parameters initialized via either:
- **Duality:** SVD-based extraction from BERT attention weights (our method)
- **Random:** Xavier initialization (baseline)

## Baselines

**Random Initialization:** Xavier/Glorot initialization for SSM parameters. This represents the lower bound—if duality cannot beat random, it provides no structural benefit.

**Rationale:** We deliberately avoid comparing to trained baselines (e.g., DistilBERT, naive KD) because our hypothesis tests *initialization quality*, not *post-optimization performance*. The comparison to random isolates whether duality equations extract useful structure.

## Implementation Details

All experiments run on a single NVIDIA H100 GPU.

**Framework:** PyTorch 2.0 with HuggingFace Transformers 4.30

**Hyperparameters:**
- SSM state dimension (d_state): 64
- Skip connection (D): 0.1
- Discretization step (Δ): 1/√768 ≈ 0.036
- Batch size: 8
- No optimization (zero-shot evaluation)

**Duality Conversion:** For each BERT layer, we extract Q, K, V projection weights, compute QK^T, perform SVD, and derive SSM parameters as described in Methodology.

## Evaluation Metrics

### h-e1 (Existence)

| Metric | Definition | Threshold |
|--------|------------|-----------|
| NaN/Inf Rate | Fraction of samples with invalid outputs | 0% |
| Magnitude Ratio | ‖SSM output‖ / ‖Transformer output‖ | < 10× |

**Why these metrics:** NaN/Inf indicates numerical instability (unusable parameters). Magnitude ratio ensures outputs are in comparable scale—extreme ratios suggest the SSM is either vanishing or exploding.

### h-m1 (Mechanism)

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| Reconstruction Error | ‖SSM output - Attention output‖_F | Duality < Random |
| Effect Size | Cohen's d across samples | d > 0 (positive effect) |
| P-value | Paired t-test | p < 0.05 |

**Why these metrics:** Frobenius norm directly measures how well SSM output approximates attention output. Effect size quantifies practical significance. P-value establishes statistical significance.

## Experimental Protocol

**h-e1 Protocol:**
1. Load BERT-base pretrained model
2. For layer 0, apply duality conversion to extract SSM parameters
3. Run SSM forward pass on 100 WikiText-103 validation samples
4. Record NaN/Inf count and magnitude ratio for each sample
5. Pass if 0 NaN/Inf AND all magnitude ratios < 10×

**h-m1 Protocol:**
1. For each BERT layer (0-11):
   a. Initialize SSM via duality equations
   b. Initialize SSM via random (Xavier)
   c. Run both on 500 identical input samples
   d. Compute reconstruction error for each
2. Perform paired t-test comparing duality vs. random errors
3. Compute Cohen's d for effect size
4. Pass if duality mean error < random mean error with p < 0.05
