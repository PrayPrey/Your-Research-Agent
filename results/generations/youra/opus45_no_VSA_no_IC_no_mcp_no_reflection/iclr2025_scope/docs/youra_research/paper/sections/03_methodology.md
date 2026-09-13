# Methodology

Building on our observation that duality provides a principled mapping from attention to SSM parameters, we design a two-stage verification protocol that isolates parameter validity from structural fidelity. This separation allows us to identify precisely where duality-based conversion succeeds and fails.

## Overview

Our methodology tests whether Mamba-2 duality equations can initialize SSM parameters from BERT attention weights such that:

1. **Stage 1 (Existence - h-e1):** The derived parameters produce stable, non-divergent SSM outputs.
2. **Stage 2 (Mechanism - h-m1):** The derived parameters reconstruct attention outputs better than random initialization.

If Stage 1 fails, duality equations are incorrectly implemented or fundamentally incompatible. If Stage 1 passes but Stage 2 fails, duality produces valid parameters that do not capture attention structure—the regime we discover.

## Duality-Based Parameter Extraction

We implement closed-form SSM parameter derivation from BERT attention weights following the Mamba-2 SSD framework. For each attention layer with query, key, and value projections (W_Q, W_K, W_V ∈ ℝ^{768×768}):

**A Matrix (State Dynamics):** We compute QK^T = W_Q · W_K^T and extract its principal components via SVD:

```
QK^T = U · Σ · V^T
A = -|Σ[:d_state]| ∈ ℝ^{d_model × d_state}
```

The negative absolute values ensure stability (negative eigenvalues prevent divergence). We use d_state = 64 for computational efficiency.

**Rationale:** The QK^T matrix captures the attention pattern structure. Its singular values represent the dominant modes of interaction between query and key spaces. Using these as A matrix entries preserves the relative importance of different interaction patterns.

**B and C Matrices (Input-to-State and State-to-Output):** We derive B and C from the SVD components:

```
B = (V[:d_state, :].T @ W_K[:, :d_state]).T  # [d_state, d_model]
C = U[:, :d_state] @ W_V[:d_state, :]         # [d_model, d_state]
```

Both are L2-normalized for numerical stability.

**Rationale:** B maps inputs to state space using key structure; C maps state to outputs using value structure. This preserves the functional roles of K (what to attend to) and V (what to output).

**D and Δ (Skip Connection and Discretization):** We set D = 0.1 (skip connection) and Δ = 1/√d_model (discretization step).

**Rationale:** The skip connection provides a direct path analogous to residual connections. The discretization step is initialized conservatively to prevent instability during the initial forward pass.

## Stability Validation (h-e1)

We validate parameter stability by running SSM forward passes on calibration data:

```python
def validate_stability(ssm_params, inputs, transformer_outputs):
    ssm_output = selective_scan(inputs, *ssm_params)
    
    is_stable = not (isnan(ssm_output).any() or isinf(ssm_output).any())
    magnitude_ratio = norm(ssm_output) / norm(transformer_outputs)
    
    return is_stable, magnitude_ratio
```

**Success Criteria:**
- NaN/Inf rate: 0%
- Magnitude ratio: < 10× (SSM outputs within order of magnitude of Transformer)

## Reconstruction Error Comparison (h-m1)

We compare duality initialization against random initialization using output Frobenius norm:

```python
def reconstruction_error(ssm_output, attention_output):
    return norm(ssm_output - attention_output, 'fro')
```

For each BERT layer, we:
1. Initialize SSM via duality equations from attention weights
2. Initialize SSM via random (Xavier) initialization
3. Run both on identical inputs (100 WikiText-103 samples, 64-512 tokens)
4. Compare reconstruction errors

**Success Criteria (original hypothesis):** Duality error < random error, with statistical significance (p < 0.05, paired t-test).

## Selective Scan Implementation

We implement a reference selective scan following Mamba-2's recurrent formulation:

```python
def selective_scan(x, A, B, C, D, dt):
    batch, seq_len, d_model = x.shape
    d_state = A.shape[1]
    h = zeros(batch, d_model, d_state)
    
    for t in range(seq_len):
        A_bar = exp(dt * A)           # Discretized dynamics
        B_bar = dt * B.T              # Discretized input
        h = A_bar * h + B_bar * x[t]  # State update
        y[t] = (C * h).sum(-1) + D * x[t]  # Output
    
    return y
```

This reference implementation prioritizes correctness over efficiency, suitable for validation purposes.

## Design Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Output Frobenius norm | Direct measure of SSM approximating attention | Matrix alignment (CB^T vs. QK^T)—noted as future work |
| d_state = 64 | Computational efficiency | d_state = 768 (full dimension)—too expensive |
| Single layer → full model | Isolates layer-level effects | Full model conversion—conflates layers |
| Zero-shot evaluation | Tests initialization quality directly | Post-optimization—tests convergence, not init |

## Connection to Key Insight

Our methodology directly tests whether duality provides structural fidelity, not just parameter validity. By separating Stage 1 (stability) from Stage 2 (reconstruction), we identify that duality-derived parameters are valid but do not preserve attention structure at the output level. This separation is the key methodological contribution enabling our negative finding.
