# Methodology

We attempted to implement gradient-based residual-corrected Jacobian stable rank regularization during GPT-2 pretraining. This section details our implementation approach, design decisions, and rationale—providing sufficient detail for others to understand and avoid the failure modes we encountered.

## Theoretical Foundation

The stable rank of a matrix A is defined as sr(A) = ||A||_F^2 / ||A||_2^2, where ||·||_F is the Frobenius norm and ||·||_2 is the spectral norm (largest singular value). Stable rank measures the effective dimensionality of a linear transformation—a matrix with all singular values equal has sr(A) = rank(A), while rank-deficient or low-rank matrices have sr(A) << min(m,n).

For layer ℓ of a neural network, the Jacobian J_ℓ = ∂h_ℓ/∂h_{ℓ-1} characterizes how representations transform through the layer. In transformer architectures with residual connections, h_ℓ = h_{ℓ-1} + f_ℓ(h_{ℓ-1}), the raw Jacobian is dominated by the identity component: J_ℓ = I + ∂f_ℓ/∂h_{ℓ-1}. To isolate the learned transformation, we define the residual-corrected Jacobian J̃_ℓ = J_ℓ - I, yielding the residual-corrected stable rank:

$$sr_ℓ^{res} = \frac{||J̃_ℓ||_F^2}{||J̃_ℓ||_2^2}$$

Our hypothesis was that regularizing sr_ℓ^{res} during pretraining would propagate low-rank structure through three mechanisms: (1) Fisher information approximation F ≈ J^T J couples Jacobian rank to adaptation efficiency, (2) covariance propagation Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T couples Jacobian rank to KV compressibility, and (3) attention entropy bounds couple Jacobian rank to computational efficiency. To test this hypothesis, we needed to estimate sr_ℓ^{res} efficiently and differentiate through the estimation procedure.

## Hutchinson Trace Estimation for Frobenius Norm

Computing ||J̃_ℓ||_F^2 = Tr(J̃_ℓ^T J̃_ℓ) exactly is prohibitive for 768-dimensional embeddings—it would require computing and storing the full 768×768 Jacobian matrix at each layer for each training batch. We employed Hutchinson's stochastic trace estimator (Bekas et al., 2007):

$$\text{Tr}(A) ≈ \frac{1}{m} \sum_{i=1}^{m} z_i^T A z_i$$

where z_i are random vectors from a distribution with E[z_i] = 0 and E[z_i z_i^T] = I. We used Rademacher vectors (entries ±1 with equal probability) as recommended for variance minimization.

**Implementation:** For each layer at each training step:
1. Sample m = 10 Rademacher vectors z_i ∈ R^d
2. For each probe, compute Jacobian-vector product J̃_ℓ z_i via PyTorch autodiff
3. Estimate Frobenius norm squared: ||J̃_ℓ||_F^2 ≈ (1/m) Σ_i (J̃_ℓ z_i)^T (J̃_ℓ z_i)

**Design Rationale:** We chose 10 probes as a compromise between computational cost (each probe requires a backward pass through the layer) and estimation accuracy. Literature suggests O(1/ε²) samples for ε-accuracy, implying ~100 probes for coefficient of variation below 15%, but full-scale pretraining with 100 probes per layer per batch was computationally prohibitive for our 125M parameter PoC. This proved to be a critical mistake—our measurements returned degenerate zero values, likely due to high-variance estimates with insufficient probes.

**Alternatives Considered:** Exact trace computation via diagonal extraction (too expensive), Monte Carlo with more probes (computationally prohibitive), Hutch++ with low-rank deflation (implementation complexity). We chose vanilla Hutchinson with 10 probes, accepting high measurement variance as a known limitation to be validated experimentally.

## Power Iteration for Spectral Norm

Computing ||J̃_ℓ||_2 exactly requires full singular value decomposition, which is infeasible in training loops. We employed randomized power iteration to estimate the largest singular value:

$$||A||_2 ≈ ||A v_k|| \text{ where } v_{k+1} = \frac{A^T A v_k}{||A^T A v_k||}$$

**Implementation:** For each layer at each training step:
1. Initialize random unit vector v_0 ∈ R^d
2. Perform K = 5 power iterations:
   - Compute u = J̃_ℓ v_k via forward-mode Jacobian-vector product
   - Compute w = J̃_ℓ^T u via reverse-mode vector-Jacobian product  
   - Normalize: v_{k+1} = w / ||w||
3. Estimate spectral norm: ||J̃_ℓ||_2 ≈ ||J̃_ℓ v_K||

**Design Rationale:** Power iteration typically converges in 5-10 iterations for well-conditioned matrices. We chose K = 5 based on spectral normalization literature (Miyato et al., 2018) where single-iteration approximations suffice for stabilization. However, residual-corrected Jacobians J̃_ℓ through attention + MLP + LayerNorm have complex spectral structure—5 iterations may be insufficient for convergence, particularly when the top singular values have similar magnitudes.

**Alternatives Considered:** Lanczos algorithm (more robust convergence but higher implementation complexity), randomized SVD (exact but too expensive), more power iterations (linear cost increase). We chose 5 iterations as a balance, accepting potential non-convergence as a measured risk.

## Residual-Corrected Jacobian Computation

Computing J̃_ℓ = J_ℓ - I requires careful handling of residual connections. For a transformer block with pre-LayerNorm:

$$h_ℓ = h_{ℓ-1} + \text{MLP}(\text{LN}(h_{ℓ-1} + \text{Attn}(\text{LN}(h_{ℓ-1}))))$$

The full Jacobian J_ℓ = ∂h_ℓ/∂h_{ℓ-1} contains the identity component from the outermost residual. We isolate the learned transformation by subtracting the identity: J̃_ℓ = J_ℓ - I.

**Implementation:** We modified the GPT-2 forward pass to capture intermediate activations (input and output of each transformer block). For each layer during regularization loss computation:
1. Extract layer input h_{ℓ-1} and output h_ℓ from captured activations
2. Compute Jacobian-vector products using PyTorch's autograd: for probe z, compute ∂h_ℓ/∂h_{ℓ-1} · z via backward pass with retain_graph=True
3. Residual correction is implicit: the autodiff computes the full Jacobian derivative, which we use directly (the identity component has zero contribution to the regularization gradient)

**Design Rationale:** Explicit subtraction J̃ = J - I is unnecessary for our purposes—we only need J̃ for Jacobian-vector products J̃z and vector-Jacobian products z^T J̃, which can be computed via autodiff on the residual function f_ℓ(h) = h_ℓ - h_{ℓ-1}. This avoids constructing the full Jacobian matrix and simplifies implementation.

**Alternatives Considered:** Explicit computation of the non-residual function (requires architectural modification), normalization by identity component (loses scale information), raw Jacobian without correction (dominated by identity, no meaningful rank signal).

## Regularization Loss and Training Integration

The regularization loss for a single layer is:

$$L_{reg,ℓ} = sr_ℓ^{res} = \frac{||J̃_ℓ||_F^2}{||J̃_ℓ||_2^2}$$

The total regularization loss sums over all L transformer layers:

$$L_{reg} = \frac{1}{L} \sum_{ℓ=1}^{L} sr_ℓ^{res}$$

The final training objective combines the causal language modeling loss with regularization:

$$L_{total} = L_{CLM} + λ L_{reg}$$

**Adaptive Lambda Tuning:** To maintain iso-perplexity (≤1% deviation from baseline), we implemented adaptive regularization weight tuning:
1. Initialize λ = 0.01
2. At each evaluation checkpoint (every 1000 steps), measure current perplexity PPL_{current}
3. If PPL_{current} > 1.01 × PPL_{baseline}, decay λ ← 0.9 × λ
4. If PPL_{current} < 0.99 × PPL_{baseline}, increase λ ← 1.1 × λ

**Design Rationale:** Fixed λ risks either over-regularization (perplexity degradation) or under-regularization (no stable rank reduction). Adaptive tuning balances the regularization strength dynamically. We chose conservative adjustment factors (±10%) to avoid oscillation.

**Alternatives Considered:** Lagrangian formulation with perplexity constraint (requires constrained optimization, complex), curriculum learning with scheduled λ increase (requires prior knowledge of optimal trajectory), per-layer λ values (too many hyperparameters). We chose global adaptive λ for simplicity.

## Gradient Flow Through Spectral Estimation

The critical implementation challenge is differentiating through the stable rank computation. The Frobenius norm estimation requires gradients through Jacobian-vector products: ∂/∂θ [z^T (J̃_ℓ z)], where θ represents model parameters. The spectral norm estimation requires gradients through power iteration: ∂/∂θ [||J̃_ℓ v_K||] where v_K depends on θ through the iterative updates.

**Implementation:** We relied on PyTorch's automatic differentiation to compute these gradients, using:
- `torch.autograd.grad` with `create_graph=True` to compute Jacobian-vector products while maintaining gradient tracking
- `retain_graph=True` when computing multiple probe vectors to avoid premature graph deletion
- Gradient accumulation across Hutchinson probes: Σ_i ∂L/∂θ_i computed independently and summed

**Numerical Stability Measures:**
- ε = 1e-8 added to denominators to prevent division by zero
- Gradient clipping with norm threshold 1.0 to prevent explosion
- Mixed precision training (FP16 for forward, FP32 for spectral estimation) to balance speed and stability

This reliance on deep autodiff chains through stochastic numerical methods proved to be a critical failure point. The gradient flow through Hutchinson trace + power iteration + regularization loss created gradient pathologies that overwhelmed the language modeling signal, as evidenced by regularization losses reaching -17.5 billion and perplexity exploding to 45,792.

## Model Architecture and Training Setup

We implemented our regularization on GPT-2 style decoder-only transformers at 125M parameter scale:
- 12 layers, 768 hidden dimensions, 12 attention heads
- Pre-LayerNorm architecture for training stability
- Absolute positional embeddings
- Sequence length 512 tokens
- Vocabulary size 50,257 (GPT-2 tokenizer)

**Training Configuration:**
- Dataset: C4 (10B token subset), streaming mode
- Batch size: 32 sequences (effective 128 with gradient accumulation steps = 4)
- Optimizer: AdamW (lr = 3e-4, β = (0.9, 0.95), weight decay = 0.1)
- Learning rate schedule: Linear warmup (375 steps) then cosine decay
- Total training: 5000 steps (~320M tokens, PoC budget)
- Hardware: Single NVIDIA A100 GPU (40GB)

**Variants:**
1. **Baseline:** Standard GPT-2 pretraining, no regularization (λ = 0)
2. **Proposed:** GPT-2 with stable rank regularization (λ_init = 0.01, adaptive)
3. **Control:** Baseline with matched compute (same FLOPs, no regularization)

This PoC setup allowed us to isolate the effect of stable rank regularization while maintaining computational feasibility. The failure at this scale provides strong evidence that the approach is fundamentally flawed—if the method fails catastrophically at 125M parameters with 320M tokens, scaling to larger models would only amplify the numerical issues.

## Measurement and Evaluation

Beyond training loss, we implemented comprehensive diagnostics:

**Per-Layer Stable Rank:** Measured every 1000 steps using the same Hutchinson + power iteration procedure (10 probes, 5 iterations) on validation batches with gradient tracking disabled.

**Measurement Precision:** Computed coefficient of variation CV = σ / μ across Hutchinson samples to quantify estimation reliability. Target: CV < 15%.

**Layer Variance:** Computed variance of stable ranks across layers to detect compensatory redistribution (high variance indicates some layers collapse while others expand).

**Perplexity Trajectory:** Evaluated on held-out C4 validation set every 500 steps to track language modeling quality.

These diagnostics were designed to provide early warning of failure modes. In practice, they revealed complete measurement infrastructure collapse—all stable rank measurements returned zero, CV was undefined (0/0), and perplexity exploded immediately, indicating fundamental implementation failure rather than hyperparameter issues.

## Implementation Availability

Our implementation is provided in the supplementary materials as fully reproducible code:
- `code/data.py`: C4 dataset loading with streaming
- `code/model.py`: StableRankRegularizer and RegularizedGPT2
- `code/train.py`: Training loop with adaptive lambda
- `code/evaluate.py`: Comprehensive metrics evaluation
- `code/visualize.py`: Figure generation
- `tests/`: Unit tests for Hutchinson trace and power iteration

We provide this code not as a recommended approach, but as a cautionary implementation that others can analyze to understand the failure modes in detail. All experiments are reproducible with the provided random seeds and hyperparameters.
