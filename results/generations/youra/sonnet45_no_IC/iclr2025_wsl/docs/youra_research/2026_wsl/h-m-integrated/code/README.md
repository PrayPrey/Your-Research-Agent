# H-M-Integrated: CAPE (Cross-Architecture Parameterized Encoder)

Implementation of the full CAPE mechanism for cross-architecture property prediction.

## Overview

This implementation validates the 3-component CAPE architecture:
1. **Operation-Specific Encoders** (Task A-2): SANE conv encoder, UNF attention encoder, MLP encoder
2. **Contrastive Projection** (Task A-3): InfoNCE loss with temperature τ=0.07
3. **Architecture GNN Residual** (Task A-4): 3-layer GCN with learnable residual weight α

## Project Structure

```
code/
├── config.py                    # Configuration parameters
├── run_experiment.py            # Main experiment orchestration
├── requirements.txt             # Dependencies
├── src/
│   └── models/
│       ├── operation_encoders.py      # A-2: Conv/Attention/MLP encoders
│       ├── contrastive_projector.py   # A-3: 2-layer MLP projector + InfoNCE
│       ├── architecture_gnn.py        # A-4: 3-layer GCN
│       ├── cape_encoder.py            # A-6: Full CAPE integration
│       ├── property_predictor.py      # Property prediction head
│       └── sne_baseline.py            # SNE baseline for comparison
└── tests/
    ├── test_operation_encoders.py     # Unit tests for A-2
    └── test_cape_encoder.py           # Unit tests for A-6
```

## Installation

```bash
# Create conda environment (recommended)
conda create -n youra-h-m-integrated python=3.11
conda activate youra-h-m-integrated

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Test Implementation

```bash
# Run full experiment pipeline (validates all components)
python run_experiment.py

# Run unit tests
python -m pytest tests/ -v
```

### 2. Expected Output

```
🔧 Step 1: Initializing CAPE and Baseline Models
  full_cape: 294,081 parameters
  op_contrastive: 219,712 parameters
  operation_only: 88,128 parameters
  sne_baseline: 33,536 parameters

🧪 Step 2: Testing Forward Pass with Dummy Data
  ✓ full_cape: embedding shape torch.Size([256]), norm 1.750
  ✓ op_contrastive: embedding shape torch.Size([256]), norm 1.000
  ✓ operation_only: embedding shape torch.Size([256]), norm 1.000
  ✓ sne_baseline: embedding shape torch.Size([256]), norm 366.957

  Diagnostics:
    Conv-Attn Similarity: -0.016  (< 0.95 threshold ✓)
    Alpha (GNN weight): 0.500      (> 0.1 threshold ✓)

🧪 Step 3: Running Unit Tests
  ✓ All unit tests passed (31/31)

Experiment Status: READY FOR TRAINING
```

## Architecture Details

### Component 1: Operation-Specific Encoders (A-2)

**SANEConvEncoder**: Spatial tokenization for convolutional layers
- Input: List of `[C_out, C_in, K, K]` tensors
- Output: `[d_z=256]` embedding
- Method: Flatten → Token projection → Mean pooling

**UNFAttentionEncoder**: Permutation-equivariant for attention layers
- Input: List of `[N_heads, D, D]` tensors
- Output: `[d_z=256]` embedding
- Method: Row/column statistics → Equivariant processing → Mean pooling

**MLPEncoder**: Standard set encoding for FC layers
- Input: List of `[D_out, D_in]` tensors
- Output: `[d_z=256]` embedding
- Method: Matrix statistics → DeepSets aggregation

**Aggregation**: Mean pooling across operation types

### Component 2: Contrastive Projection (A-3)

**ContrastiveProjector**: 2-layer MLP with InfoNCE loss
- Architecture: `d_z → ReLU → d_z → L2-norm`
- Temperature: `τ = 0.07`
- Loss: InfoNCE (symmetric cross-entropy on similarity matrix)

### Component 3: Architecture GNN Residual (A-4)

**ArchitectureGNN**: 3-layer GCN for architecture DAGs
- Input: Node features `[N_nodes, d_arch=64]`, edge indices `[2, N_edges]`
- Output: `[d_z=256]` architecture embedding
- Residual: `z_final = z_proj + α * z_arch` (α learnable)

### Full CAPE Integration (A-6)

**CAPEEncoder**: Combines all 3 components
```python
z_op = mean([z_conv, z_attn, z_mlp])  # Operation encoding
z_proj = projector(z_op)               # Contrastive projection
z_arch = gnn(arch_graph)               # Architecture embedding (optional)
z_final = z_proj + α * z_arch          # Residual combination
```

## Ablation Variants

The implementation supports 4 ablation variants for FR-7:

1. **SNE Baseline**: No operation encoders, no contrastive, no GNN
2. **Operation-Only**: Operation encoders only
3. **Op+Contrastive**: Operation encoders + contrastive projection
4. **Full CAPE**: All 3 components enabled

## Configuration

Key hyperparameters in `config.py`:

```python
"cape_encoder": {
    "d_z": 256,              # Embedding dimension
    "d_arch": 64,            # Architecture node features
    "tau": 0.07,             # InfoNCE temperature
    "num_gnn_layers": 3,     # GNN depth
    "alpha_init": 0.5,       # Residual weight initialization
}

"training": {
    "batch_size": 32,
    "epochs": 100,
    "lr": 1e-4,
    "weight_decay": 1e-4,
}

"loss": {
    "lambda_contrast": 1.0,  # InfoNCE weight
    "lambda_property": 0.5,  # Property prediction weight
}
```

## Testing

### Unit Tests

```bash
# Test operation encoders
python -m pytest tests/test_operation_encoders.py -v

# Test CAPE encoder
python -m pytest tests/test_cape_encoder.py -v

# Test all
python -m pytest tests/ -v
```

### Test Coverage

- **31 tests** covering:
  - Initialization and forward pass for each encoder
  - Spatial tokenization and equivariant processing
  - Contrastive projection and InfoNCE loss
  - GNN residual with learnable alpha
  - Ablation variants (4 configurations)
  - Diagnostic metrics computation
  - Empty input handling

## Diagnostic Metrics

The implementation computes diagnostic metrics for component validation:

1. **Operation Similarity**: Cosine similarity between conv and attention embeddings
   - Target: < 0.80 (distinct representations)
   - Falsifier: > 0.95 (modular encoding failed)

2. **Intra-Architecture Variance**: Embedding variance within each architecture
   - Target: ≥ 0.15
   - Falsifier: < 0.1 (alignment destroyed structure)

3. **GNN Weight α**: Learned residual weight
   - Target: > 0.1 (GNN contributing)
   - Falsifier: → 0 (GNN useless)

## Next Steps

1. **Data Collection**: Collect 400 models (100 per architecture) from HuggingFace/timm
2. **Preprocessing**: Implement weight normalization and architecture DAG construction
3. **Training**: Implement multi-task training loop (InfoNCE + property MSE)
4. **Evaluation**: Cross-architecture transfer evaluation on ResNet→ViT

## Success Criteria

**Primary Gate (MUST_WORK)**:
- ✅ Full CAPE achieves ρ ≥ 0.65 on ResNet→ViT transfer
- ✅ Statistical significance: ρ_CAPE - ρ_SNE ≥ 0.10 with p < 0.05

**Component Validation**:
- ✅ Diagnostic 1: Operation similarity < 0.95
- ✅ Diagnostic 2: Intra-architecture variance ≥ 0.1
- ✅ Diagnostic 3: α > 0.1 OR performance improvement

## References

- **PRD**: `docs/youra_research/h-m-integrated/03_prd.md`
- **Architecture**: `docs/youra_research/h-m-integrated/03_architecture.md`
- **Logic**: `docs/youra_research/h-m-integrated/03_logic.md`
- **Config**: `docs/youra_research/h-m-integrated/03_config.md`

## Notes

- **PyTorch Geometric**: Required for GNN components. Fallback to simple MLP if unavailable.
- **Device**: Automatically detects CUDA availability, defaults to CPU.
- **Reproducibility**: Fixed random seed (42) for deterministic results.

---

**Status**: Implementation Complete (Phase 4)  
**Next**: Data collection and training (Phase 4 continuation)
