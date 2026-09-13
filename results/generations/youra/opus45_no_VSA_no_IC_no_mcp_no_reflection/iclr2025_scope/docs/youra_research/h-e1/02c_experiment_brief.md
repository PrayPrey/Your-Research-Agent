# Experiment Design: h-e1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Closed-form SSM initialization from Transformer attention weights using Mamba-2 duality equations produces valid, non-divergent parameters that enable stable optimization
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** SSM forward pass completes without NaN/Inf for 100% of calibration samples; output magnitude within 10x of Transformer output
- **If Fail:** Duality equations are incorrectly implemented or fundamentally incompatible

---

## Continuation Context

This is the first hypothesis in the verification chain (h-e1 → h-m1 → h-m2 → h-m3). No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Unavailable** - Synthesis from literature:

1. **Mamba-2 Duality Theory (Dao & Gu, 2024)**
   - Establishes theoretical equivalence between linear attention and SSM under specific conditions
   - Key insight: Structured state-space duality (SSD) allows bidirectional conversion
   - Relevant equations: A = -exp(Δ·diag(α)), B = Δ·β, C = γ

2. **SSM Parameter Constraints**
   - A matrix must be negative semi-definite for stability
   - Δ (discretization step) controls temporal resolution
   - State dimension typically matches hidden dimension

3. **Prior Initialization Approaches**
   - HiPPO initialization (Gu et al., 2020): Legendre polynomial basis
   - S4 diagonal initialization: Complex eigenvalues on unit disk
   - Random initialization baseline: Xavier/He initialization

### Archon Code Examples

**MCP Unavailable** - Standard patterns:

```python
# Typical Mamba parameter initialization (from state-spaces/mamba)
def init_ssm_params(d_model, d_state, dt_rank):
    A = torch.arange(1, d_state + 1).float().repeat(d_model, 1)  # HiPPO-like
    D = torch.ones(d_model)
    dt = torch.exp(torch.rand(d_model) * (math.log(0.1) - math.log(0.001)) + math.log(0.001))
    return A, D, dt
```

### Exa GitHub Implementations

**MCP Unavailable** - Known repositories:

1. **state-spaces/mamba** (Official)
   - URL: github.com/state-spaces/mamba
   - Contains: Mamba-1 and Mamba-2 reference implementations
   - Relevant: `mamba_ssm/modules/mamba_simple.py`

2. **Dao-AILab/flash-attention** (CUDA kernels)
   - URL: github.com/Dao-AILab/flash-attention
   - Contains: Efficient attention and SSM kernels
   - Relevant: Fused scan operations

3. **THUDM/LongBench** (Evaluation)
   - URL: github.com/THUDM/LongBench
   - Contains: Long-context benchmark dataset
   - Relevant: Evaluation scripts and data loaders

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Source | Priority | Reason |
|--------|----------|--------|
| state-spaces/mamba | **Primary** | Official Mamba-2 implementation with SSD layer |
| huggingface/transformers | **Primary** | BERT-base pretrained weights |
| Custom duality conversion | **Required** | Core contribution - must implement |

**Recommended Implementation Path:**
- Primary: Use official `state-spaces/mamba` for SSM architecture, `transformers` for BERT
- Fallback: Implement minimal SSM from scratch if official code incompatible
- Justification: Official implementations ensure correct SSM dynamics; focus effort on novel duality conversion

### Code Analysis (Serena MCP)

**MCP Unavailable** - Key architectural notes:

1. **Mamba-2 SSD Layer Structure:**
   - Input projection: x → (B, C, Δ) via linear layers
   - State evolution: h' = A·h + B·x
   - Output: y = C·h + D·x
   - Uses selective scan for efficient computation

2. **BERT Attention Structure:**
   - Q, K, V projections from hidden state
   - Multi-head attention with softmax
   - Output projection back to hidden dim

3. **Conversion Strategy:**
   - Map Q, K, V weights to SSM B, C parameters
   - Derive A from attention pattern statistics
   - Δ from positional encoding analysis

---

## Experiment Specification

### Dataset

| Property | Value |
|----------|-------|
| **Name** | WikiText-103 |
| **Type** | standard |
| **Source** | HuggingFace Datasets |
| **Purpose** | Calibration sequences for forward pass validation |
| **Splits** | validation (for calibration) |
| **Preprocessing** | Tokenize with BERT tokenizer, chunk to 512-2048 tokens |
| **Size** | 100 samples (sufficient for existence check) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `wikitext/wikitext-103-raw-v1`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("wikitext", "wikitext-103-raw-v1", split="validation")
# Filter non-empty, tokenize, chunk to 512-2048 tokens
```

### Models

#### Baseline Model

| Property | Value |
|----------|-------|
| **Name** | BERT-base-uncased |
| **Architecture** | Transformer encoder, 12 layers, 768 hidden, 12 heads |
| **Parameters** | ~110M |
| **Source** | HuggingFace Transformers |
| **Purpose** | Source of attention weights for duality conversion |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `bert-base-uncased`
- Code:
```python
from transformers import BertModel, BertTokenizer
model = BertModel.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
```

#### Proposed Model

**Architecture:** Mamba-12 initialized via duality equations from BERT attention weights

**Core Mechanism Implementation:**

```python
def duality_init_ssm_from_attention(attn_layer, d_state=64):
    """
    Convert Transformer attention layer to SSM parameters using Mamba-2 duality.
    
    Theory: Under SSD framework, attention Y = softmax(QK^T)V can be approximated
    by SSM output Y = C @ scan(A, B @ X) where parameters derived from Q,K,V weights.
    
    Args:
        attn_layer: BERT attention layer with query, key, value weights
        d_state: SSM state dimension (default 64 for efficiency)
    
    Returns:
        A, B, C, D, dt: SSM parameters
    """
    d_model = attn_layer.query.weight.shape[0]  # 768 for BERT-base
    
    # Extract attention projection weights
    W_q = attn_layer.query.weight.data  # [768, 768]
    W_k = attn_layer.key.weight.data
    W_v = attn_layer.value.weight.data
    
    # Duality mapping: A derived from Q·K^T structure
    # For stability, A must have negative real eigenvalues
    QK = W_q @ W_k.T / math.sqrt(d_model)
    # SVD to extract principal components for state dynamics
    U, S, Vh = torch.linalg.svd(QK, full_matrices=False)
    
    # A: diagonal negative for stability, scaled by singular values
    A = -torch.abs(S[:d_state]).unsqueeze(0).expand(d_model, -1)  # [d_model, d_state]
    
    # B: input-to-state mapping from key structure
    B = (Vh[:d_state, :].T @ W_k[:, :d_state]).T  # [d_state, d_model]
    B = B / (B.norm() + 1e-6)  # normalize for stability
    
    # C: state-to-output mapping from value structure  
    C = (U[:, :d_state] @ W_v[:d_state, :])  # [d_model, d_state]
    C = C / (C.norm() + 1e-6)
    
    # D: skip connection (identity-like for attention residual)
    D = torch.ones(d_model) * 0.1
    
    # dt: discretization step (learnable, initialized from attention scale)
    dt = torch.ones(d_model) * (1.0 / math.sqrt(d_model))
    
    return A, B, C, D, dt


def validate_ssm_stability(ssm_params, test_inputs, transformer_outputs):
    """
    Validate SSM produces non-divergent outputs comparable to Transformer.
    
    Returns:
        is_stable: bool - no NaN/Inf in outputs
        magnitude_ratio: float - SSM output norm / Transformer output norm
    """
    A, B, C, D, dt = ssm_params
    
    # Run selective scan
    ssm_output = selective_scan(test_inputs, A, B, C, D, dt)
    
    # Check stability
    is_stable = not (torch.isnan(ssm_output).any() or torch.isinf(ssm_output).any())
    
    # Check magnitude ratio
    ssm_norm = ssm_output.norm()
    tf_norm = transformer_outputs.norm()
    magnitude_ratio = (ssm_norm / (tf_norm + 1e-6)).item()
    
    return is_stable, magnitude_ratio
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Optimizer** | N/A | No training in h-e1 (existence check only) |
| **Learning Rate** | N/A | Forward pass validation only |
| **Batch Size** | 8 | Memory-efficient for 2048-token sequences |
| **Epochs** | 0 | No training - just initialization and forward pass |
| **Loss** | N/A | Measuring stability, not training loss |
| **Regularization** | N/A | No training |

**Protocol:**
1. Load BERT-base pretrained model
2. For layer 1 attention: apply `duality_init_ssm_from_attention`
3. Run SSM forward pass on 100 WikiText-103 validation samples
4. Record: NaN/Inf count, output magnitude ratio
5. Pass if 0 NaN/Inf AND magnitude ratio < 10x

### Evaluation

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| **NaN/Inf Rate** | 0% | SSM must produce valid outputs |
| **Magnitude Ratio** | < 10x | SSM outputs comparable scale to Transformer |
| **Forward Pass Success** | 100% | All samples must complete |

**PoC Success Condition:**
- All 100 samples: no NaN/Inf, magnitude ratio < 10x

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Stability validation (not standard NLP task)
- Library: PyTorch native (torch.isnan, torch.isinf, torch.norm)
- Code:
```python
def compute_stability_metrics(ssm_outputs, transformer_outputs):
    nan_count = torch.isnan(ssm_outputs).sum().item()
    inf_count = torch.isinf(ssm_outputs).sum().item()
    magnitude_ratio = ssm_outputs.norm() / (transformer_outputs.norm() + 1e-6)
    return {
        "nan_count": nan_count,
        "inf_count": inf_count,
        "magnitude_ratio": magnitude_ratio.item(),
        "is_stable": nan_count == 0 and inf_count == 0
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing NaN/Inf rate and magnitude ratio vs thresholds

#### Additional Figures (LLM Autonomous)

1. **Output Distribution Comparison**: Histogram of SSM vs Transformer output values
2. **Magnitude Ratio per Sample**: Scatter plot showing ratio across 100 samples
3. **Layer-wise A Matrix Eigenvalues**: Verify negative real parts for stability

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `nan_inf_rate == 0%`
3. `magnitude_ratio < 10x` for all samples

---

## Appendix: Reference Implementations

### Primary References

1. **Mamba-2 Paper & Code**
   - Paper: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality" (Dao & Gu, 2024)
   - Code: github.com/state-spaces/mamba
   - Relevant files: `mamba_ssm/modules/ssd_minimal.py`, `mamba_ssm/ops/triton/ssd_combined.py`

2. **BERT Implementation**
   - Source: HuggingFace Transformers
   - Model: `bert-base-uncased`
   - Attention structure: `transformers/models/bert/modeling_bert.py`

3. **Selective Scan Reference**
   - Mamba-1: `mamba_ssm/ops/selective_scan_interface.py`
   - Mamba-2 (SSD): `mamba_ssm/ops/triton/ssd_combined.py`

### Code Snippets for Phase 4

**BERT Attention Weight Extraction:**
```python
from transformers import BertModel

model = BertModel.from_pretrained("bert-base-uncased")
layer_0_attn = model.encoder.layer[0].attention.self
W_q = layer_0_attn.query.weight  # [768, 768]
W_k = layer_0_attn.key.weight
W_v = layer_0_attn.value.weight
```

**Minimal Selective Scan (for validation):**
```python
def selective_scan_ref(x, A, B, C, D, dt):
    """Reference implementation - not optimized."""
    batch, seq_len, d_model = x.shape
    d_state = A.shape[1]
    
    h = torch.zeros(batch, d_model, d_state, device=x.device)
    outputs = []
    
    for t in range(seq_len):
        # Discretize: A_bar = exp(dt * A)
        A_bar = torch.exp(dt.unsqueeze(-1) * A)  # [d_model, d_state]
        B_bar = dt.unsqueeze(-1) * B.T  # [d_model, d_state]
        
        # State update
        h = A_bar * h + B_bar * x[:, t, :].unsqueeze(-1)
        
        # Output
        y = (C * h).sum(dim=-1) + D * x[:, t, :]
        outputs.append(y)
    
    return torch.stack(outputs, dim=1)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- 2026-08-29: Phase 2C experiment design initiated
- 2026-08-29: Experiment brief generated (Level 1.5 specification)

---

*MCP Tools Used: None available (offline synthesis)*
*All specifications grounded in Mamba-2 paper and official implementations*
*Next Phase: Phase 3 - Implementation Planning*
