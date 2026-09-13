# Logic Design: h-e1

**Version:** 1.0
**Date:** 2026-08-29
**Hypothesis:** h-e1 (EXISTENCE)

---

## Codebase Analysis (Serena)

Green-field implementation. No existing codebase.

Applied: Type-Annotated API Pattern (Archon KB)
Applied: Tensor Shape Documentation Pattern

---

## API Signatures

### duality_conversion.py

```python
from typing import Tuple
import torch
from torch import Tensor
from transformers.models.bert.modeling_bert import BertSelfAttention

def extract_attention_weights(
    attn_layer: BertSelfAttention
) -> Tuple[Tensor, Tensor, Tensor]:
    """
    Extract Q, K, V weight matrices from BERT attention layer.
    
    Args:
        attn_layer: BERT self-attention layer
        
    Returns:
        W_q: [768, 768] query projection weights
        W_k: [768, 768] key projection weights  
        W_v: [768, 768] value projection weights
    """
    ...

def duality_init_ssm_from_attention(
    attn_layer: BertSelfAttention,
    d_state: int = 64
) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """
    Convert Transformer attention to SSM parameters via Mamba-2 duality.
    
    Args:
        attn_layer: BERT attention layer with Q, K, V weights
        d_state: SSM state dimension (default: 64)
        
    Returns:
        A: [d_model, d_state] state transition matrix (negative eigenvalues)
        B: [d_state, d_model] input-to-state projection
        C: [d_model, d_state] state-to-output projection
        D: [d_model] skip connection weights
        dt: [d_model] discretization step
        
    Tensor Shapes:
        Input attention layer:
            W_q: [768, 768]
            W_k: [768, 768]
            W_v: [768, 768]
        
        Intermediate:
            QK: [768, 768] = W_q @ W_k.T / sqrt(768)
            U, S, Vh: SVD decomposition
            
        Output SSM params:
            A: [768, 64] - negative for stability
            B: [64, 768] - normalized
            C: [768, 64] - normalized
            D: [768] - scalar 0.1
            dt: [768] - 1/sqrt(768)
    """
    ...
```

### selective_scan.py

```python
def selective_scan_ref(
    x: Tensor,
    A: Tensor,
    B: Tensor,
    C: Tensor,
    D: Tensor,
    dt: Tensor
) -> Tensor:
    """
    Reference selective scan implementation.
    
    Args:
        x: [batch, seq_len, d_model] input tensor
        A: [d_model, d_state] state transition
        B: [d_state, d_model] input projection
        C: [d_model, d_state] output projection
        D: [d_model] skip connection
        dt: [d_model] discretization step
        
    Returns:
        y: [batch, seq_len, d_model] output tensor
        
    Algorithm:
        for t in range(seq_len):
            A_bar = exp(dt * A)  # [d_model, d_state]
            B_bar = dt * B.T     # [d_model, d_state]
            h = A_bar * h + B_bar * x[:, t, :].unsqueeze(-1)
            y[:, t, :] = (C * h).sum(-1) + D * x[:, t, :]
    """
    ...
```

### stability_validation.py

```python
from typing import Dict, Any, Tuple

def validate_ssm_stability(
    ssm_output: Tensor,
    transformer_output: Tensor
) -> Tuple[bool, float]:
    """
    Validate SSM output stability.
    
    Args:
        ssm_output: [batch, seq_len, d_model] SSM forward pass output
        transformer_output: [batch, seq_len, d_model] reference output
        
    Returns:
        is_stable: True if no NaN/Inf
        magnitude_ratio: SSM norm / Transformer norm
    """
    ...

def compute_stability_metrics(
    ssm_outputs: Tensor,
    transformer_outputs: Tensor
) -> Dict[str, Any]:
    """
    Compute comprehensive stability metrics.
    
    Returns:
        {
            "nan_count": int,
            "inf_count": int,
            "magnitude_ratio": float,
            "is_stable": bool,
            "max_value": float,
            "min_value": float
        }
    """
    ...
```

### data_loader.py

```python
from typing import List, Dict
from torch import Tensor

def load_wikitext_samples(
    num_samples: int = 100,
    min_length: int = 512,
    max_length: int = 2048
) -> List[Dict[str, Tensor]]:
    """
    Load WikiText-103 validation samples.
    
    Args:
        num_samples: Number of samples to load
        min_length: Minimum token length
        max_length: Maximum token length
        
    Returns:
        List of {"input_ids": Tensor, "attention_mask": Tensor}
        Each input_ids: [1, seq_len] where min_length <= seq_len <= max_length
    """
    ...
```

### run_experiment.py

```python
def run_existence_validation(
    config_path: str = "configs/experiment_config.yaml"
) -> Dict[str, Any]:
    """
    Run h-e1 existence validation experiment.
    
    Returns:
        {
            "pass": bool,
            "nan_inf_rate": float,
            "magnitude_ratio_mean": float,
            "magnitude_ratio_max": float,
            "samples_tested": int
        }
    """
    ...

def generate_figures(
    results: Dict[str, Any],
    output_dir: str = "figures/"
) -> List[str]:
    """
    Generate visualization figures.
    
    Returns:
        List of saved figure paths
    """
    ...
```

---

## Tensor Flow Diagram

```
BERT Layer 0 Attention
    │
    ├── W_q [768, 768]
    ├── W_k [768, 768]
    └── W_v [768, 768]
          │
          ▼
    duality_init_ssm_from_attention()
          │
          ├── QK = W_q @ W_k.T / sqrt(768)  →  [768, 768]
          ├── SVD(QK) → U, S, Vh
          │
          ├── A = -|S[:64]| expanded        →  [768, 64]
          ├── B = (Vh[:64] @ W_k[:64]).T    →  [64, 768]
          ├── C = U[:,:64] @ W_v[:64,:]     →  [768, 64]
          ├── D = ones(768) * 0.1           →  [768]
          └── dt = ones(768) / sqrt(768)    →  [768]
                    │
                    ▼
            selective_scan_ref()
                    │
    x [B, L, 768] ──┤
                    │
                    ▼
            y [B, L, 768]
                    │
                    ▼
            validate_ssm_stability()
                    │
                    ▼
            {is_stable, magnitude_ratio}
```

---

## Pseudo-code: Core Algorithm

```python
# Main validation loop
def validate_duality_existence():
    # 1. Load pretrained BERT
    bert = BertModel.from_pretrained("bert-base-uncased")
    layer_0_attn = bert.encoder.layer[0].attention.self
    
    # 2. Convert to SSM via duality
    A, B, C, D, dt = duality_init_ssm_from_attention(layer_0_attn, d_state=64)
    
    # 3. Load calibration data
    samples = load_wikitext_samples(num_samples=100)
    
    # 4. Validate each sample
    results = []
    for sample in samples:
        # Get BERT output for reference
        with torch.no_grad():
            bert_out = bert(sample["input_ids"]).last_hidden_state
        
        # Get embeddings (skip attention, just get input to layer 0)
        x = bert.embeddings(sample["input_ids"])
        
        # Run SSM forward pass
        ssm_out = selective_scan_ref(x, A, B, C, D, dt)
        
        # Validate
        is_stable, mag_ratio = validate_ssm_stability(ssm_out, bert_out)
        results.append({"stable": is_stable, "ratio": mag_ratio})
    
    # 5. Aggregate results
    all_stable = all(r["stable"] for r in results)
    max_ratio = max(r["ratio"] for r in results)
    
    return {
        "pass": all_stable and max_ratio < 10.0,
        "nan_inf_rate": sum(not r["stable"] for r in results) / len(results),
        "magnitude_ratio_max": max_ratio
    }
```

---

## Subtasks (from E-3: Duality Conversion - High Complexity)

| Subtask | Description | Est. LOC |
|---------|-------------|----------|
| E-3.1 | Extract BERT attention weights | 20 |
| E-3.2 | Implement QK computation + SVD | 30 |
| E-3.3 | Implement A matrix derivation (negative eigenvalues) | 25 |
| E-3.4 | Implement B, C matrix derivation + normalization | 40 |

---

*Logic design for EXISTENCE hypothesis*
*Next: Configuration Design*
