# System Architecture: H-M-Integrated (Full CAPE Mechanism Validation)

**Date:** 2026-07-13
**Hypothesis ID:** H-M-Integrated
**Type:** MECHANISM
**Architecture Patterns Applied:** Modular encoder composition, Contrastive learning pipeline, Multi-task training

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Analyzed h-e1 actual implementation
**Analyzed Path:** `/workspace/TEST_wsl/docs/youra_research/h-e1/code/`
**Findings:** H-E1 provides reusable data collection (ModelZooCollector) and feature extraction (FeatureExtractor) utilities. Import paths verified from actual implementation using timm library for model loading.

---

## Module Structure

### CAPEEncoder (`src/models/cape_encoder.py`)

**Dependencies:** torch, torch_geometric

```python
class CAPEEncoder(nn.Module):
    def __init__(self, d_z: int = 256, d_arch: int = 64, tau: float = 0.07): ...
    def forward(self, model_weights: Dict[str, Tensor], arch_graph: Tuple) -> Tensor: ...
    def get_operation_embeddings(self, model_weights: Dict) -> Tensor: ...
    def compute_infonce_loss(self, z_proj: Tensor) -> Tensor: ...
```

### OperationEncoders (`src/models/operation_encoders.py`)

**Dependencies:** torch

```python
class SANEConvEncoder(nn.Module):
    def __init__(self, d_out: int = 256): ...
    def forward(self, conv_weights: Tensor) -> Tensor: ...
    def spatial_tokenize(self, weight: Tensor) -> Tensor: ...

class UNFAttentionEncoder(nn.Module):
    def __init__(self, d_out: int = 256): ...
    def forward(self, attn_weights: Tensor) -> Tensor: ...
    def equivariant_process(self, weight: Tensor) -> Tensor: ...

class MLPEncoder(nn.Module):
    def __init__(self, d_out: int = 256): ...
    def forward(self, mlp_weights: Tensor) -> Tensor: ...
```

### ContrastiveProjector (`src/models/contrastive_projector.py`)

**Dependencies:** torch

```python
class ContrastiveProjector(nn.Module):
    def __init__(self, d_z: int = 256, tau: float = 0.07): ...
    def forward(self, z_op: Tensor) -> Tensor: ...
    def infonce_loss(self, z_proj: Tensor, temperature: float) -> Tensor: ...
```

### ArchitectureGNN (`src/models/architecture_gnn.py`)

**Dependencies:** torch_geometric

```python
class ArchitectureGNN(nn.Module):
    def __init__(self, d_arch: int = 64, d_z: int = 256, num_layers: int = 3): ...
    def forward(self, node_features: Tensor, edge_index: Tensor) -> Tensor: ...
    def global_pooling(self, x: Tensor, batch: Tensor) -> Tensor: ...
```

### SNEBaseline (`src/models/sne_baseline.py`)

**Dependencies:** torch

```python
class SNEBaseline(nn.Module):
    def __init__(self, d_model: int = 256): ...
    def forward(self, weight_set: Tensor) -> Tensor: ...
    def set_aggregate(self, embeddings: Tensor) -> Tensor: ...
```

### PropertyPredictor (`src/models/property_predictor.py`)

**Dependencies:** torch

```python
class PropertyPredictor(nn.Module):
    def __init__(self, d_z: int = 256, num_properties: int = 1): ...
    def forward(self, z_final: Tensor) -> Tensor: ...
```

### ModelZooDataset (`src/data/dataset.py`)

**Dependencies:** torch, h-e1.model_zoo

```python
class ModelZooDataset(Dataset):
    def __init__(self, metadata: List[Dict], features_dir: str, arch_graphs_dir: str): ...
    def __getitem__(self, idx: int) -> Dict: ...
    def __len__(self) -> int: ...
    def collate_fn(self, batch: List[Dict]) -> Dict: ...
```

### WeightPreprocessor (`src/data/preprocessor.py`)

**Dependencies:** torch, numpy, h-e1.feature_extractor

```python
class WeightPreprocessor:
    def __init__(self, normalization: str = "frobenius"): ...
    def normalize_weights(self, state_dict: Dict) -> Dict: ...
    def extract_operation_groups(self, state_dict: Dict) -> Dict[str, List]: ...
    def save_preprocessed(self, processed_data: Dict, filepath: str): ...
```

### ArchitectureGraphBuilder (`src/data/graph_builder.py`)

**Dependencies:** torch, torch_geometric, networkx

```python
class ArchitectureGraphBuilder:
    def __init__(self, d_arch: int = 64): ...
    def build_dag(self, model: nn.Module) -> Tuple[Tensor, Tensor]: ...
    def extract_node_features(self, layer: nn.Module) -> Tensor: ...
    def save_graph(self, graph: Tuple, filepath: str): ...
```

### MultiTaskTrainer (`src/training/trainer.py`)

**Dependencies:** torch, torch.optim

```python
class MultiTaskTrainer:
    def __init__(self, model: nn.Module, config: Dict): ...
    def train_epoch(self, train_loader: DataLoader) -> Dict: ...
    def validate(self, val_loader: DataLoader) -> Dict: ...
    def compute_combined_loss(self, z_proj: Tensor, predictions: Tensor, targets: Tensor) -> Tensor: ...
    def save_checkpoint(self, filepath: str, epoch: int): ...
    def load_checkpoint(self, filepath: str): ...
```

### CrossArchEvaluator (`src/evaluation/evaluator.py`)

**Dependencies:** scipy, sklearn, numpy

```python
class CrossArchEvaluator:
    def __init__(self, n_permutations: int = 1000): ...
    def evaluate_transfer(self, predictions: np.ndarray, targets: np.ndarray) -> Dict: ...
    def compute_spearman(self, y_pred: np.ndarray, y_true: np.ndarray) -> Tuple[float, float]: ...
    def permutation_test(self, rho_cape: float, rho_baseline: float) -> Dict: ...
    def compute_transfer_matrix(self, results: Dict) -> np.ndarray: ...
```

### DiagnosticMetrics (`src/evaluation/diagnostics.py`)

**Dependencies:** torch, sklearn

```python
class DiagnosticMetrics:
    def __init__(self): ...
    def compute_operation_similarity(self, z_conv: Tensor, z_attn: Tensor) -> float: ...
    def compute_intra_arch_variance(self, z_proj: Tensor, labels: Tensor) -> float: ...
    def compute_gnn_weight(self, model: CAPEEncoder) -> float: ...
    def check_falsifiers(self, diagnostics: Dict) -> Dict[str, bool]: ...
```

### Visualizer (`src/visualization/visualizer.py`)

**Dependencies:** matplotlib, seaborn, sklearn

```python
class Visualizer:
    def __init__(self, output_dir: str, dpi: int = 300): ...
    def plot_gate_comparison(self, metrics: Dict, thresholds: Dict) -> str: ...
    def plot_transfer_matrix(self, matrix: np.ndarray, arch_names: List) -> str: ...
    def plot_ablation_bars(self, variants: Dict[str, float]) -> str: ...
    def plot_embedding_space(self, embeddings: np.ndarray, labels: np.ndarray) -> str: ...
    def plot_operation_similarity(self, similarity_matrix: np.ndarray) -> str: ...
    def plot_training_curves(self, history: Dict) -> str: ...
```

---

## File Organization

```
docs/youra_research/h-m-integrated/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── cape_encoder.py         # FR-6: Full CAPE integration
│   │   │   ├── operation_encoders.py   # FR-3: Operation-specific encoders
│   │   │   ├── contrastive_projector.py # FR-4: Contrastive projection
│   │   │   ├── architecture_gnn.py     # FR-5: GNN residual
│   │   │   ├── sne_baseline.py         # FR-2: SNE baseline
│   │   │   └── property_predictor.py   # FR-6: Property prediction head
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── dataset.py              # FR-1: Dataset wrapper
│   │   │   ├── preprocessor.py         # FR-1: Weight preprocessing
│   │   │   └── graph_builder.py        # FR-1: Architecture DAG construction
│   │   ├── training/
│   │   │   ├── __init__.py
│   │   │   └── trainer.py              # FR-6: Multi-task training loop
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── evaluator.py            # FR-8: Cross-architecture evaluation
│   │   │   └── diagnostics.py          # FR-9: Component diagnostics
│   │   └── visualization/
│   │       ├── __init__.py
│   │       └── visualizer.py           # FR-10: Figure generation
│   ├── config.py                        # Configuration parameters
│   ├── run_experiment.py                # Main orchestration
│   └── requirements.txt                 # Dependencies
├── data/
│   ├── raw/
│   │   └── models_metadata.json         # Model zoo metadata (reuse h-e1)
│   ├── preprocessed/
│   │   ├── weight_features/             # Preprocessed weight features
│   │   └── arch_graphs/                 # Architecture DAG representations
│   ├── splits/
│   │   ├── train_indices.json
│   │   ├── val_indices.json
│   │   └── test_indices.json
├── checkpoints/
│   ├── cape_full/
│   ├── cape_op_only/
│   ├── cape_op_contrastive/
│   └── sne_baseline/
├── results/
│   ├── transfer_matrix.json
│   ├── diagnostics.json
│   ├── ablation_results.json
│   └── gate_metrics.json
└── figures/
    ├── gate_comparison.png              # REQUIRED
    ├── transfer_matrix.png
    ├── ablation_bars.png
    ├── embedding_space.png
    ├── operation_similarity.png
    ├── gnn_residual_analysis.png
    └── training_curves.png
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ModelZooCollector | `from sys import path; path.append('../h-e1/code'); from src.model_zoo import ModelZooCollector` | `h-e1/code/src/model_zoo.py` |
| FeatureExtractor | `from sys import path; path.append('../h-e1/code'); from src.feature_extractor import FeatureExtractor` | `h-e1/code/src/feature_extractor.py` |

**Verified from:** `/workspace/TEST_wsl/docs/youra_research/h-e1/code/` (actual implementation)

**Reuse Strategy:**
- ModelZooCollector: Reuse for 400-model collection (scale up from 100)
- FeatureExtractor: Extend for operation-type separation (conv/attention/MLP grouping)

---

## Configuration (`config.py`)

```python
CONFIG = {
    "hypothesis_id": "H-M-Integrated",
    "random_seed": 42,
    
    # Model Zoo Collection (FR-1)
    "model_zoo": {
        "n_per_architecture": 100,
        "architectures": ["resnet50", "vit_base_patch16_224", "mobilenetv2_100", "efficientnet_b0"],
        "dataset_filter": "imagenet-1k",
        "retry_attempts": 3,
        "min_success_rate": 0.90
    },
    
    # Data Preprocessing (FR-1)
    "preprocessing": {
        "normalization": "frobenius",  # Per-layer Frobenius norm
        "operation_types": ["conv", "attention", "mlp"],
        "cache_preprocessed": True
    },
    
    # Architecture DAG (FR-1, FR-5)
    "architecture_dag": {
        "d_arch": 64,  # Node feature dimension
        "include_layer_types": True,
        "include_dimensions": True
    },
    
    # Train/Val/Test Split (FR-1)
    "data_split": {
        "train_ratio": 0.70,
        "val_ratio": 0.15,
        "test_ratio": 0.15,
        "stratify_by_architecture": True
    },
    
    # CAPE Encoder (FR-3, FR-4, FR-5, FR-6)
    "cape_encoder": {
        "d_z": 256,  # Embedding dimension
        "d_arch": 64,  # Architecture embedding dimension
        "tau": 0.07,  # InfoNCE temperature
        "dropout": 0.1,
        "gnn_layers": 3
    },
    
    # Training (FR-6)
    "training": {
        "batch_size": 32,
        "epochs": 100,
        "optimizer": "adamw",
        "lr": 1e-4,
        "weight_decay": 1e-4,
        "lr_schedule": "cosine",
        "warmup_ratio": 0.10,
        "early_stopping_patience": 10,
        "mixed_precision": True
    },
    
    # Loss Function (FR-6)
    "loss": {
        "lambda_contrast": 1.0,  # InfoNCE weight
        "lambda_property": 0.5   # Property prediction weight
    },
    
    # Ablation Variants (FR-7)
    "ablation": {
        "variants": ["sne_baseline", "operation_only", "op_contrastive", "full_cape"]
    },
    
    # Evaluation (FR-8)
    "evaluation": {
        "primary_transfer": "resnet50->vit_base",
        "n_permutations": 1000,
        "alpha": 0.05
    },
    
    # Diagnostic Thresholds (FR-9)
    "diagnostics": {
        "operation_similarity_threshold": 0.95,  # Falsifier
        "intra_variance_threshold": 0.1,          # Falsifier
        "gnn_weight_threshold": 0.1               # Falsifier
    },
    
    # Success Criteria
    "success_criteria": {
        "target_rho": 0.65,
        "baseline_rho": 0.54,
        "min_improvement": 0.10,
        "p_value_threshold": 0.05
    },
    
    # Directories
    "directories": {
        "data": "data/",
        "checkpoints": "checkpoints/",
        "results": "results/",
        "figures": "figures/"
    }
}
```

---

## Data Flow

1. **Collection & Preprocessing Phase** (FR-1):
   - `ModelZooCollector` (from h-e1) → 400 models → `models_metadata.json`
   - `WeightPreprocessor` → operation-grouped weights → `preprocessed/weight_features/`
   - `ArchitectureGraphBuilder` → DAG representations → `preprocessed/arch_graphs/`

2. **Training Phase** (FR-6, FR-7):
   - `ModelZooDataset` → `DataLoader` → batched inputs
   - `CAPEEncoder` → forward pass → embeddings
   - `MultiTaskTrainer` → combined loss → optimizer step
   - Checkpoint saving every 10 epochs

3. **Evaluation Phase** (FR-8, FR-9):
   - Load checkpoint → inference on test set
   - `CrossArchEvaluator` → transfer correlations → `transfer_matrix.json`
   - `DiagnosticMetrics` → component validation → `diagnostics.json`

4. **Visualization Phase** (FR-10):
   - Load results → `Visualizer` → all figures → `figures/`

---

## Proposed Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Model Zoo & Preprocessing | Collect 400 models, preprocess weights, build architecture DAGs | 14 | 4+3+4+3 |
| A-2 | Operation-Specific Encoders | Implement SANE conv encoder, UNF attention encoder, MLP encoder | 17 | 5+4+5+3 |
| A-3 | Contrastive Projection Module | Implement projector network and InfoNCE loss computation | 12 | 3+3+4+2 |
| A-4 | Architecture GNN Residual | Implement 3-layer GCN, global pooling, residual combination | 13 | 4+3+4+2 |
| A-5 | SNE Baseline Implementation | Implement DeepSets-style baseline for comparison | 8 | 2+2+2+2 |
| A-6 | Full CAPE Integration | Integrate all components, implement property predictor | 15 | 4+3+5+3 |
| A-7 | Multi-Task Training Pipeline | Implement training loop with combined loss, checkpointing | 14 | 4+3+4+3 |
| A-8 | Ablation Study Framework | Train 4 variants with identical hyperparameters | 13 | 3+3+4+3 |
| A-9 | Cross-Architecture Evaluation | Implement transfer matrix, statistical testing | 11 | 3+2+4+2 |
| A-10 | Diagnostic Metrics & Falsifiers | Implement component diagnostics, falsifier checks | 10 | 2+2+4+2 |
| A-11 | Visualization Pipeline | Generate all required and optional figures | 11 | 3+2+4+2 |

**Complexity Breakdown:** Module_Size + Dependencies + Algorithm + Integration (each 1-5)

**Distribution:**
- VeryHigh (16-20): [A-2]
- High (14-17): [A-1, A-6, A-7]
- Medium (9-13): [A-3, A-4, A-8, A-9, A-10, A-11]
- Low (4-8): [A-5]

**Total Complexity:** 138 points (11 Epic tasks)

---

## Task Details

### A-1: Model Zoo & Preprocessing (Complexity: 14)
**Modules:** `data/dataset.py`, `data/preprocessor.py`, `data/graph_builder.py`
**Prerequisites:** None
**Deliverables:**
- Scale ModelZooCollector to 400 models (4 architectures × 100 each)
- Implement per-layer Frobenius norm normalization
- Group weights by operation type (conv/attention/MLP)
- Build architecture DAG for each model
- 70/15/15 stratified train/val/test split
**Acceptance:**
- 400 models successfully collected and preprocessed
- Operation groupings validated (all 3 types present per model)
- DAG representations saved for all architectures
- Data splits balanced across architectures

### A-2: Operation-Specific Encoders (Complexity: 17)
**Modules:** `models/operation_encoders.py`
**Prerequisites:** A-1
**Deliverables:**
- SANEConvEncoder: Spatial tokenization preserving convolutional structure
- UNFAttentionEncoder: Permutation-equivariant processing for attention weights
- MLPEncoder: Standard set encoding for fully-connected layers
- All encoders output d=256
- Mean pooling aggregation across operation types
**Acceptance:**
- All 3 encoders process respective weight types correctly
- Output dimensionality uniform (d=256)
- Cosine similarity between conv and attention embeddings <0.95 (validation check)

### A-3: Contrastive Projection Module (Complexity: 12)
**Modules:** `models/contrastive_projector.py`
**Prerequisites:** A-2
**Deliverables:**
- 2-layer MLP projector (d_z → d_z → d_z)
- L2 normalization before contrastive loss
- InfoNCE loss implementation with τ=0.07
- Dropout=0.1 for regularization
**Acceptance:**
- Projector maintains embedding dimension
- InfoNCE loss computed correctly (checked against reference implementation)
- Normalized embeddings have unit L2 norm

### A-4: Architecture GNN Residual (Complexity: 13)
**Modules:** `models/architecture_gnn.py`
**Prerequisites:** A-1
**Deliverables:**
- 3-layer GCN processing architecture DAG
- Global graph pooling (mean aggregation)
- Linear projection to d_z=256
- Learnable residual weight α
**Acceptance:**
- GCN processes DAG inputs correctly
- Global pooling produces single architecture embedding per model
- Residual weight α initialized and learnable

### A-5: SNE Baseline Implementation (Complexity: 8)
**Modules:** `models/sne_baseline.py`
**Prerequisites:** A-1
**Deliverables:**
- DeepSets-style permutation-invariant encoder
- Mean pooling aggregation
- Linear property prediction head
- Target: reproduce ρ=0.54 on ResNet→ViT transfer
**Acceptance:**
- Baseline model trains without errors
- ResNet→ViT correlation ≈0.54 (±0.05 acceptable)

### A-6: Full CAPE Integration (Complexity: 15)
**Modules:** `models/cape_encoder.py`, `models/property_predictor.py`
**Prerequisites:** A-2, A-3, A-4
**Deliverables:**
- Integrate operation encoders, contrastive projector, GNN residual
- Forward pass: weights + arch_graph → z_final
- Property predictor: z_final → accuracy predictions
- Component accessor methods for diagnostics
**Acceptance:**
- Forward pass processes batched inputs correctly
- All 3 components contribute to final embeddings
- Property predictions output correct shape

### A-7: Multi-Task Training Pipeline (Complexity: 14)
**Modules:** `training/trainer.py`
**Prerequisites:** A-6
**Deliverables:**
- Combined loss: λ_contrast × InfoNCE + λ_property × MSE
- AdamW optimizer with cosine annealing (10% warmup)
- Early stopping (patience=10 on validation loss)
- Checkpoint saving/loading
- Mixed precision training (optional)
**Acceptance:**
- Training loop runs for 100 epochs without errors
- Combined loss decreases over epochs
- Checkpoints saved every 10 epochs
- Early stopping triggers correctly

### A-8: Ablation Study Framework (Complexity: 13)
**Modules:** `run_experiment.py` (ablation orchestration)
**Prerequisites:** A-5, A-7
**Deliverables:**
- Train 4 variants: SNE baseline, Operation-only, Op+Contrastive, Full CAPE
- Identical hyperparameters across variants
- Save separate checkpoints per variant
- Compare ResNet→ViT correlation across variants
**Acceptance:**
- All 4 variants train successfully
- Results saved per variant
- Performance ordering validated (Full CAPE ≥ others)

### A-9: Cross-Architecture Evaluation (Complexity: 11)
**Modules:** `evaluation/evaluator.py`
**Prerequisites:** A-7, A-8
**Deliverables:**
- Compute Spearman correlation for all 12 architecture pairs
- Permutation test: ρ_CAPE - ρ_SNE ≥0.10, p<0.05
- Generate 4×4 transfer matrix
- Statistical significance testing (1000 permutations)
**Acceptance:**
- Primary gate: ResNet→ViT correlation ρ ≥0.65
- Statistical test: p<0.05 for improvement over baseline
- Transfer matrix generated for all architecture pairs

### A-10: Diagnostic Metrics & Falsifiers (Complexity: 10)
**Modules:** `evaluation/diagnostics.py`
**Prerequisites:** A-7
**Deliverables:**
- Diagnostic 1: Cosine similarity between conv and attention embeddings
- Diagnostic 2: Intra-architecture embedding variance
- Diagnostic 3: Learned GNN residual weight α
- Falsifier checks: trigger warnings if thresholds violated
**Acceptance:**
- All 3 diagnostics computed during training and evaluation
- Falsifier logic implemented correctly
- Results logged to diagnostics.json

### A-11: Visualization Pipeline (Complexity: 11)
**Modules:** `visualization/visualizer.py`
**Prerequisites:** A-9, A-10
**Deliverables:**
- Gate comparison bar chart (REQUIRED)
- Transfer matrix heatmap (12×12)
- Ablation bars (4 variants)
- Embedding space t-SNE/UMAP
- Operation similarity matrix
- GNN residual analysis scatter plot
- Training curves (InfoNCE, Property MSE, Combined)
**Acceptance:**
- All 7 figures generated and saved to figures/
- Gate comparison includes threshold lines
- All plots properly labeled and styled

---

## Dependencies

**External Libraries:**
- `torch>=2.0` - Neural network framework
- `torch-geometric>=2.3` - GNN components (GCNConv)
- `numpy>=1.21` - Array operations
- `scipy>=1.9` - Spearman correlation
- `scikit-learn>=1.0` - t-SNE/UMAP, metrics
- `timm>=0.9` - Model loading (reuse from h-e1)
- `matplotlib>=3.5` - Visualization
- `seaborn>=0.11` - Styled plots
- `networkx>=2.8` - Graph structures

**Data Dependencies:**
- HuggingFace Model Hub / timm library (400 ImageNet-1K models)
- H-E1 codebase (ModelZooCollector, FeatureExtractor utilities)

---

## Success Validation

**Primary Gate (MUST_WORK):**
- Full CAPE achieves ρ ≥0.65 on ResNet→ViT transfer
- Statistical significance: ρ_CAPE - ρ_SNE ≥0.10 with p<0.05

**Component Validation (Diagnostics):**
- Diagnostic 1: Cosine similarity <0.95 → modular encoding works
- Diagnostic 2: Intra-architecture variance ≥0.1 → alignment preserves structure
- Diagnostic 3: α >0.1 OR performance with GNN ≥ without → GNN contributes

**Fail Actions:**
- Primary gate fails → PIVOT to Contrastive-Aligned variant (no GNN)
- Diagnostic 1 fails (>0.95) → ABANDON modular encoding, fall back to SNE
- Diagnostic 2 fails (<0.1) → Re-tune contrastive hyperparameters (τ, λ)
- Diagnostic 3 fails (α→0 or degradation) → Degrade to Op+Contrastive variant

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model collection failures at 400-scale | High | Reuse h-e1 collection logic, implement retry with exponential backoff |
| Operation-type grouping ambiguity | High | Manual architecture inspection, conservative layer-type classification |
| GNN component provides no benefit | Medium | Diagnostic 3 falsifier triggers fallback to Contrastive-Aligned variant |
| InfoNCE loss divergence | Medium | Standard τ=0.07, warmup schedule, gradient clipping |
| Operation encoders collapse to identical representations | High | Diagnostic 1 monitors similarity, early warning system |
| Insufficient improvement over baseline (<0.10) | Critical | Partial success path explores hyperparameter tuning |

---

**Architecture Status:** COMPLETE
**Next Phase:** Phase 4 - Implementation (Epic task execution)
**Estimated Timeline:** 25-30 hours (full mechanism validation)

---

**Knowledge Base Patterns Applied:**
- Applied: Multi-component encoder composition (DALLE2 cascading pattern)
- Applied: Contrastive learning with projection network (InfoNCE τ=0.07 standard)
- Applied: Graph neural network architecture processing (GCN for topology signals)
