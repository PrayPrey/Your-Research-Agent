# System Architecture: h-m-integrated CAWE Mechanism Validation

**Hypothesis:** h-m-integrated (MECHANISM)
**Date:** 2026-03-19
**Type:** FULL
**Applied:** Standard DL experiment pattern (5-component validation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from h-e1 base code
**Analyzed Path:** docs/youra_research/20260319_wsl/h-e1/code/
**Findings:** h-e1 validated CAWE implementation with tokenizers, NFT backbone (simplified), FlatWeightMLP baseline, and ModelZooDataset. Real pretrained models from torchvision/timm, MNIST MLPs trained locally. Import paths verified from actual code structure.

---

## System Overview

Extends h-e1 CAWE implementation with 5-component mechanism validation: (1) per-family ablation training, (2) architecture clustering analysis, (3) flat-weight MLP baseline comparison, (4) random forest engineered-feature baseline, (5) robustness validation across tokenization variants and hyperparameters.

**Core Components (Extension from h-e1):**
- Reuse h-e1: DataLoader, tokenizers, CAWE model, FlatWeightMLP baseline
- New: PerFamilyTrainer, ClusteringEvaluator, RandomForestBaseline, RobustnessValidator
- New: 5-component evaluation pipeline, comprehensive visualization suite

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CAWE | `from h_e1.code.cawe.models.cawe import CAWE` | `h-e1/code/cawe/models/cawe.py` |
| Tokenizers | `from h_e1.code.cawe.tokenizers.tokenizers import CNNTokenizer, TransformerTokenizer, MLPTokenizer` | `h-e1/code/cawe/tokenizers/tokenizers.py` |
| DataLoader | `from h_e1.code.cawe.data.loader import create_dataloaders` | `h-e1/code/cawe/data/loader.py` |
| FlatWeightMLP | `from h_e1.code.cawe.baselines.flat_mlp import FlatWeightMLP` | `h-e1/code/cawe/baselines/flat_mlp.py` |

**Verified from**: h-e1/code/ (actual implementation)

**Note:** Import paths assume h-e1/code is added to Python path or copied to h-m-integrated workspace.

---

## Module Architecture

### PerFamilyTrainer (`cawe/training/per_family.py`)

**Dependencies:** CAWE (from h-e1), DataLoader (from h-e1)

```python
class PerFamilyTrainer:
    def __init__(self, cawe_model: CAWE, train_loader: DataLoader, test_loader: DataLoader): ...
    def train_single_family(self, family: str, epochs: int = 100) -> float: ...
    def evaluate_family(self, family: str) -> Dict[str, float]: ...
    # Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float}
```

### ClusteringEvaluator (`cawe/evaluation/clustering.py`)

**Dependencies:** CAWE (from h-e1), sklearn.metrics

```python
class ClusteringEvaluator:
    def __init__(self, cawe_model: CAWE, dataset: ModelZooDataset): ...
    def extract_embeddings(self) -> np.ndarray: ...
    # Returns: (num_models, embed_dim)
    def compute_silhouette_score(self, embeddings: np.ndarray, labels: np.ndarray) -> float: ...
    def visualize_clustering(self, embeddings: np.ndarray, labels: np.ndarray, save_path: str): ...
```

### RandomForestBaseline (`cawe/baselines/random_forest.py`)

**Dependencies:** sklearn.ensemble, scipy

```python
class WeightFeatureExtractor:
    def extract_features(self, state_dict: Dict[str, torch.Tensor]) -> np.ndarray: ...
    # Returns: [l2_norms, sparsity, spectral_radius, mean_stats, std_stats]

class RandomForestBaseline:
    def __init__(self, n_estimators: int = 100, max_depth: int = 10): ...
    def train(self, features: np.ndarray, targets: np.ndarray): ...
    def predict(self, features: np.ndarray) -> np.ndarray: ...
```

### RobustnessValidator (`cawe/evaluation/robustness.py`)

**Dependencies:** Tokenizers (from h-e1), CAWE

```python
class RobustnessValidator:
    def __init__(self, base_cawe_model: CAWE, train_loader: DataLoader, test_loader: DataLoader): ...
    def test_tokenization_variants(self) -> Dict[str, float]: ...
    # Returns: {'variant_1': rho, 'variant_2': rho, ...}
    def test_token_dimension_variants(self, dimensions: List[int]) -> Dict[int, float]: ...
    # Returns: {64: rho, 128: rho, 256: rho}
```

### MechanismEvaluationPipeline (`scripts/evaluate_mechanism.py`)

**Dependencies:** All components above

```python
class MechanismEvaluationPipeline:
    def __init__(self, config: Dict): ...
    def run_component_1_per_family_ablation(self) -> Dict[str, float]: ...
    def run_component_2_clustering(self) -> float: ...
    def run_component_3_flat_baseline(self) -> Dict[str, float]: ...
    def run_component_4_rf_baseline(self) -> Dict[str, float]: ...
    def run_component_5_robustness(self) -> Dict[str, Any]: ...
    def aggregate_results(self) -> Dict[str, Any]: ...
    # Returns: {'component_1_pass': bool, ..., 'total_passed': int, 'gate_status': str}
```

### VisualizationSuite (`scripts/visualize_mechanism.py`)

**Dependencies:** matplotlib, seaborn, sklearn.manifold

```python
def plot_component_pass_fail_matrix(results: Dict, save_path: str): ...
def plot_per_family_comparison(family_rhos: Dict[str, float], threshold: float, save_path: str): ...
def plot_architecture_clustering_tsne(embeddings: np.ndarray, labels: np.ndarray, silhouette: float, save_path: str): ...
def plot_baseline_comparison(metrics: Dict[str, float], save_path: str): ...
def plot_robustness_heatmap(robustness_results: Dict, save_path: str): ...
```

---

## File Structure

```
h-m-integrated/
├── code/
│   ├── cawe/
│   │   ├── __init__.py
│   │   ├── training/
│   │   │   ├── __init__.py
│   │   │   └── per_family.py           # PerFamilyTrainer
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── clustering.py           # ClusteringEvaluator
│   │   │   └── robustness.py           # RobustnessValidator
│   │   └── baselines/
│   │       ├── __init__.py
│   │       └── random_forest.py        # RandomForestBaseline, WeightFeatureExtractor
│   ├── scripts/
│   │   ├── train_per_family.py         # Per-family ablation training script
│   │   ├── train_full_cawe.py          # Full CAWE training (600 models)
│   │   ├── evaluate_mechanism.py       # MechanismEvaluationPipeline
│   │   └── visualize_mechanism.py      # VisualizationSuite
│   ├── requirements.txt
│   └── README.md
├── checkpoints/                         # Per-family, full, baseline model checkpoints
│   ├── cawe_cnn_only.pt
│   ├── cawe_transformer_only.pt
│   ├── cawe_mlp_only.pt
│   ├── cawe_full.pt
│   ├── flat_mlp.pt
│   └── rf_baseline.pkl
├── results/
│   └── mechanism_metrics.csv           # 5-component results
└── figures/                            # All 5 component visualizations
    ├── component_matrix.png
    ├── per_family_comparison.png
    ├── clustering_tsne.png
    ├── baseline_comparison.png
    └── robustness_heatmap.png
```

**Note:** h-e1/code/ modules are reused via import or copy. No modification to h-e1 codebase.

---

## Data Flow

```
Model Zoo (750 models, reused from h-e1)
    ↓
[Component 1: Per-Family Ablation]
    ├── CNN-only subset (200 train, 50 test) → CAWE → ρ_cnn
    ├── Transformer-only subset (200 train, 50 test) → CAWE → ρ_transformer
    └── MLP-only subset (200 train, 50 test) → CAWE → ρ_mlp
    ↓
[Component 2: Architecture Clustering]
    Full dataset → CAWE.get_embeddings() → Silhouette score
    ↓
[Component 3: Flat-Weight Baseline]
    Full dataset → FlatWeightMLP (reused from h-e1) → Δρ comparison
    ↓
[Component 4: Random Forest Baseline]
    Full dataset → Feature extraction → RandomForest → Δρ comparison
    ↓
[Component 5: Robustness Validation]
    Tokenization variants (D=64,128,256) → CAWE variants → ρ variance
    ↓
[Aggregation]
    5 component results → Pass/Fail matrix → Gate decision (≥3 PASS)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Per-Family Ablation | Implement PerFamilyTrainer for 3 architecture-specific experiments (CNN/Transformer/MLP) | 13 | Module(3) + Dep(3) + Algo(4) + Integ(3) |
| B-2 | Clustering Validation | Implement ClusteringEvaluator with embedding extraction and silhouette scoring | 11 | Module(3) + Dep(2) + Algo(3) + Integ(3) |
| B-3 | Random Forest Baseline | Implement WeightFeatureExtractor and RandomForestBaseline with engineered features | 12 | Module(3) + Dep(2) + Algo(4) + Integ(3) |
| B-4 | Robustness Validator | Implement RobustnessValidator for tokenization and dimension variant testing | 14 | Module(3) + Dep(3) + Algo(4) + Integ(4) |
| B-5 | Flat Baseline Training | Train FlatWeightMLP baseline (reused from h-e1) on full dataset for Δρ comparison | 7 | Module(1) + Dep(2) + Algo(2) + Integ(2) |
| B-6 | Full CAWE Training | Train full CAWE model on 600-model dataset for clustering and baseline comparison | 8 | Module(2) + Dep(2) + Algo(2) + Integ(2) |
| B-7 | Mechanism Evaluation Pipeline | Implement MechanismEvaluationPipeline orchestrating all 5 components | 15 | Module(3) + Dep(4) + Algo(4) + Integ(4) |
| B-8 | Visualization Suite | Generate 5 component figures (matrix, per-family, clustering, baselines, robustness) | 10 | Module(2) + Dep(3) + Algo(2) + Integ(3) |

**Total Complexity:** 90
**Distribution:** VeryHigh(18-20): [], High(14-17): [B-4, B-7], Medium(9-13): [B-1, B-2, B-3, B-8], Low(4-8): [B-5, B-6]

**Task Dependencies:**
- B-1, B-2, B-3, B-4, B-5, B-6 can run in parallel (independent training)
- B-7 depends on B-1 through B-6 (all components complete)
- B-8 depends on B-7 (evaluation results ready)

---

## Configuration

**Hardcoded Constants (FULL tier - config file optional but accepted):**

```python
# Reused from h-e1
LEARNING_RATE = 1e-4
BATCH_SIZE = 32
EPOCHS = 100
EARLY_STOPPING_PATIENCE = 10
WEIGHT_DECAY = 1e-2
TOKEN_DIM = 128
NFT_CHANNELS = 64
DROPOUT = 0.1
RANDOM_SEED = 42

# Dataset split (stratified by architecture)
TRAIN_SIZE = 600  # 200/200/200 per family
TEST_SIZE = 150   # 50/50/50 per family

# Component thresholds
THRESHOLD_PER_FAMILY_RHO = 0.7
THRESHOLD_SILHOUETTE = 0.5
THRESHOLD_DELTA_FLAT = 0.15
THRESHOLD_DELTA_RF = 0.1
THRESHOLD_ROBUSTNESS_VARIANTS = 2  # Out of 4 tokenization variants
THRESHOLD_ROBUSTNESS_DIMENSIONS = 2  # Out of 3 D-values

# Random Forest config
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 10

# Robustness test variants
TOKENIZATION_VARIANTS = ['D64', 'D256', 'alt_layer', 'weight_norm']
TOKEN_DIMENSION_VARIANTS = [64, 128, 256]

# Bootstrap
N_BOOTSTRAP = 1000

# Gate condition
GATE_MIN_COMPONENTS_PASS = 3  # Out of 5
```

---

## Success Criteria

### PoC Pass (SHOULD_WORK Gate)
1. Code runs without error for all 5 components
2. At least 2/5 components pass thresholds

### Hypothesis Validation (Primary)
1. At least 3/5 components pass:
   - Component 1: All 3 per-family ρ > 0.7
   - Component 2: Silhouette > 0.5
   - Component 3: Δρ_flat > 0.15 (p < 0.001)
   - Component 4: Δρ_RF > 0.1 (p < 0.01)
   - Component 5: 2/4 tokenization + 2/3 D-values pass

### Secondary Metrics
1. Full success: All 5/5 components pass
2. Per-architecture consistency: CNN ≈ MLP > Transformer (from h-e1 pattern)

### Failure Response
- If 0-2/5 components pass → SHOULD_WORK gate PARTIAL → Document, continue workflow
- If 0/5 pass → PIVOT or EXPLORE alternative mechanisms

---

## Implementation Notes

### Code Reuse Strategy

**Primary reuse from h-e1:**
- DataLoader: `create_dataloaders()` unchanged
- CAWE model: Tokenizers + NFT backbone unchanged
- FlatWeightMLP: Reused for Component 3
- Training utilities: Optimizer config, early stopping

**New implementations:**
- Per-family training wrapper (separates dataset by architecture)
- Clustering evaluation (sklearn.metrics.silhouette_score)
- Random forest baseline (sklearn.ensemble.RandomForestRegressor)
- Robustness validation (variant model training)

### Per-Family Ablation Strategy

**Split dataset by architecture family:**
- CNN-only: Filter dataset where arch_family='cnn' → 200 train, 50 test
- Transformer-only: Filter dataset where arch_family='transformer' → 200 train, 50 test
- MLP-only: Filter dataset where arch_family='mlp' → 200 train, 50 test

**Train separate CAWE models:**
- Each model uses same hyperparameters as full training
- Controlled comparison: Same optimizer, lr, batch size, epochs
- Evaluation metric: Spearman ρ on held-out 50-model test set per family

### Clustering Validation Strategy

**Embedding extraction:**
- Use CAWE NFT backbone output before regression head
- Embedding dimension: TOKEN_DIM=128 (from h-e1 config)
- Extract for all 750 models in dataset

**Silhouette score computation:**
- Labels: [0]*250 (CNN) + [1]*250 (Transformer) + [2]*250 (MLP)
- Metric: sklearn.metrics.silhouette_score(embeddings, labels)
- Threshold: > 0.5 (moderate cluster separation)

### Random Forest Baseline Strategy

**Feature engineering:**
- Layer-wise L2 norms: `torch.linalg.norm(weight_matrix, ord=2)`
- Weight sparsity: `(torch.abs(weight_matrix) < 1e-5).float().mean()`
- Spectral radius: `torch.linalg.eigvals(weight_matrix @ weight_matrix.T).abs().max()`
- Mean/std statistics: `weight_matrix.mean()`, `weight_matrix.std()`

**Training:**
- Model: sklearn.ensemble.RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
- Train on 600-model feature vectors
- Evaluate on 150-model test set

### Robustness Validation Strategy

**Tokenization variants (4 total):**
1. D=64 token projection (instead of D=128)
2. D=256 token projection
3. Alternative layer selection (skip first/last layers)
4. Weight normalization before tokenization (L2 normalize per layer)

**Token dimension variants (3 total):**
- D=64, D=128, D=256 (train separate CAWE models)

**Success criteria:**
- 2/4 tokenization variants achieve ρ > 0.65
- 2/3 D-values achieve ρ > 0.65

### Statistical Testing

**Paired t-test (Component 3):**
- Null hypothesis: ρ_CAWE = ρ_flat
- Alternative: ρ_CAWE > ρ_flat
- Significance: p < 0.001
- Library: scipy.stats.ttest_rel(cawe_preds, flat_preds)

**Wilcoxon signed-rank (Component 4):**
- Null hypothesis: ρ_CAWE = ρ_RF
- Alternative: ρ_CAWE > ρ_RF
- Significance: p < 0.01
- Library: scipy.stats.wilcoxon(cawe_preds, rf_preds, alternative='greater')

---

## Resource Requirements

**GPU:**
- Single GPU (user sets `CUDA_VISIBLE_DEVICES`)
- Estimated memory: < 16GB (same as h-e1, sequential training)

**Disk:**
- Model zoo: ~2GB (reused from h-e1)
- Checkpoints: ~2GB (per-family × 3, full, baselines, robustness variants)
- Results: ~50MB (metrics CSV + visualizations)

**Training Time:**
- Per-family ablation: 3 × 2 hours = 6 hours
- Full CAWE: 2 hours
- Flat baseline: 1 hour
- Random forest: < 10 minutes
- Robustness variants: 4 × 1.5 hours = 6 hours
- **Total:** ~15 hours (sequential execution)

---

*Generated by Phase 3 Architecture Design*
*Next: Phase 4 Implementation*
