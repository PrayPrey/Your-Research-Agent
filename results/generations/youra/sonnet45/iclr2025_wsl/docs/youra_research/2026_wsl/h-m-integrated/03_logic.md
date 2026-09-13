---
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_at: 2026-03-19T08:15:00Z
source: Phase 3 Logic Design
---

# Logic Design: H-M-Integrated CAWE Mechanism Validation

**Hypothesis:** h-m-integrated (MECHANISM)
**Date:** 2026-03-19
**Type:** FULL (5-Component Validation)
**Budget:** 14 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual code
**Analyzed Path:** docs/youra_research/20260319_wsl/h-e1/code/
**Relevant Symbols:**
- CAWE.forward(weights, arch_family) - verified parameter names
- create_dataloaders(data_dir, batch_size, seed, train_samples, val_samples, test_samples)
- FlatWeightMLP.forward(weights) - expects pre-flattened tensor
- CNNTokenizer.forward(state_dict), TransformerTokenizer.forward(state_dict), MLPTokenizer.forward(state_dict)

**Critical Finding:** Base hypothesis uses `weights` (not `state_dict`), `arch_family` (not `family`). FlatWeightMLP expects pre-flattened tensor input, not state_dict.

---

## Applied Patterns

**Applied:** PyTorch Module Pattern (nn.Module with __init__ and forward)
**Applied:** Sklearn Evaluation Pattern (silhouette_score, RandomForestRegressor)
**Applied:** Statistical Testing Pattern (scipy.stats for paired t-test, Wilcoxon)

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1 base hypothesis. Signatures verified from actual implementation:

```python
# From: h-e1/code/cawe/models/cawe.py (ACTUAL CODE)
class CAWE(nn.Module):
    def __init__(self, token_dim: int = 128, nft_channels: int = 64):
        """CAWE model with tokenizers + NFT backbone."""
        ...

    def forward(self, weights: Dict[str, torch.Tensor], arch_family: str) -> torch.Tensor:
        """Forward pass. weights: state_dict, arch_family: 'cnn'|'transformer'|'mlp' -> scalar"""
        # Returns: scalar prediction (squeezed)
        ...

# From: h-e1/code/cawe/data/loader.py (ACTUAL CODE)
def create_dataloaders(
    data_dir: str = None,
    batch_size: int = 32,
    seed: int = 42,
    train_samples: int = 600,
    val_samples: int = 150,
    test_samples: int = 150
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create train, val, test dataloaders.

    Returns:
        train_loader, val_loader, test_loader
    """
    ...

# From: h-e1/code/cawe/baselines/flat_mlp.py (ACTUAL CODE)
class FlatWeightMLP(nn.Module):
    def __init__(self, input_dim: int):
        """Flat-weight baseline. Requires pre-flattened input."""
        ...

    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """Forward pass. weights: [input_dim] -> scalar"""
        # NOTE: Expects pre-flattened tensor, NOT state_dict!
        ...

# From: h-e1/code/cawe/tokenizers/tokenizers.py (ACTUAL CODE)
class CNNTokenizer(nn.Module):
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """CNN tokenization. state_dict -> [L, D]"""
        ...

class TransformerTokenizer(nn.Module):
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Transformer tokenization. state_dict -> [L, D]"""
        ...

class MLPTokenizer(nn.Module):
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """MLP tokenization. state_dict -> [L, D]"""
        ...
```

**Verified from**: h-e1/code/ (actual implementation, NOT specs!)
**Import Paths**: Assume h-e1/code is added to PYTHONPATH or copied to workspace.

---

## B-1: Per-Family Ablation [Complexity: 13, Budget: 2/14]

**Applied:** PyTorch Training Loop Pattern

### API Signatures

```python
class PerFamilyTrainer:
    def __init__(
        self,
        cawe_model: CAWE,
        data_dir: str,
        device: torch.device,
        seed: int = 42
    ):
        """Train CAWE on single-family subsets."""
        ...

    def train_family(
        self,
        family: str,
        epochs: int = 100,
        batch_size: int = 32,
        lr: float = 1e-4
    ) -> Tuple[float, float, float]:
        """Train on family subset. family: 'cnn'|'transformer'|'mlp' -> (rho, ci_lower, ci_upper)"""
        ...

    def evaluate_family(self, family: str) -> Dict[str, float]:
        """Evaluate on family test set. Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weights | Dict[str, Tensor] | State dict (variable shapes) |
| gap_pred | scalar | CAWE output |
| rho | scalar | Spearman correlation |

### Pseudo-code

```
1. Filter dataset by family: train_samples = [s for s in all_samples if s.family == family]
2. Create family-specific dataloaders (200 train, 50 test per family)
3. Train CAWE with AdamW (lr=1e-4, wd=1e-2, epochs=100)
4. Evaluate on family test set: compute Spearman ρ with bootstrap CI
5. Return (rho, ci_lower, ci_upper)
```

### Subtasks [2/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | PerFamilyTrainer.train_family | Filter dataset by family, train CAWE on 200 samples |
| L-1-2 | PerFamilyTrainer.evaluate_family | Compute Spearman ρ with 1000 bootstrap resamples |

---

## B-2: Clustering Validation [Complexity: 11, Budget: 2/14]

**Applied:** Sklearn Clustering Pattern

### API Signatures

```python
class ClusteringEvaluator:
    def __init__(self, cawe_model: CAWE, dataset: ModelZooDataset):
        """Evaluate architecture clustering from CAWE embeddings."""
        ...

    def extract_embeddings(self) -> np.ndarray:
        """Extract embeddings from all models. Returns: [750, 128] (after pooling)"""
        ...

    def compute_silhouette_score(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray
    ) -> float:
        """Compute silhouette score. embeddings: [N, D], labels: [N] -> float"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [750, 128] | Pooled NFT features |
| labels | [750] | Architecture family (0=CNN, 1=Transformer, 2=MLP) |
| silhouette | scalar | Cluster quality score |

### Pseudo-code

```
1. For each model in dataset (750 total):
   a. tokens = cawe.tokenizers[family](state_dict)  # [L, 128]
   b. features = cawe.nft_backbone(tokens)  # [L, 128]
   c. embedding = features.mean(dim=0)  # [128] pooled
2. Stack all embeddings: embeddings = np.stack(all_embeddings)  # [750, 128]
3. Create labels: [0]*250 + [1]*250 + [2]*250 (CNN, Transformer, MLP)
4. Compute: silhouette_score(embeddings, labels) using sklearn
5. Return: silhouette (threshold: > 0.5)
```

### Subtasks [2/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ClusteringEvaluator.extract_embeddings | Extract pooled NFT features for all 750 models |
| L-2-2 | ClusteringEvaluator.compute_silhouette_score | sklearn.metrics.silhouette_score wrapper |

---

## B-3: Random Forest Baseline [Complexity: 12, Budget: 2/14]

**Applied:** Sklearn RandomForest + Feature Engineering Pattern

### API Signatures

```python
class WeightFeatureExtractor:
    def extract_features(self, state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        """Extract engineered features. state_dict -> [num_features]"""
        # Features: L2 norms, sparsity, spectral radius, mean/std per layer
        ...

class RandomForestBaseline:
    def __init__(self, n_estimators: int = 100, max_depth: int = 10, seed: int = 42):
        """Random forest regressor baseline."""
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=seed
        )

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train RF. X: [N, F], y: [N] gaps"""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict gaps. X: [N, F] -> [N] predictions"""
        ...
```

### Pseudo-code

```
1. For each model in train set:
   a. Extract layer-wise L2 norms: [torch.linalg.norm(w, ord=2) for w in state_dict.values()]
   b. Compute sparsity: [(torch.abs(w) < 1e-5).float().mean() for w in state_dict.values()]
   c. Spectral radius: [torch.linalg.eigvals(w @ w.T).abs().max() for w in 2D weights]
   d. Stats: [w.mean(), w.std() for w in state_dict.values()]
   e. Concatenate all features -> [num_features]
2. Train RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
3. Predict on test set
4. Compute Δρ = ρ_CAWE - ρ_RF (threshold: > 0.1, p < 0.01 Wilcoxon test)
```

### Subtasks [2/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | WeightFeatureExtractor.extract_features | L2 norms, sparsity, spectral radius, mean/std per layer |
| L-3-2 | RandomForestBaseline train/predict | sklearn.ensemble.RandomForestRegressor wrapper |

---

## B-4: Robustness Validator [Complexity: 14, Budget: 2/14]

**Applied:** Variant Training Pattern

### API Signatures

```python
class RobustnessValidator:
    def __init__(
        self,
        base_cawe_model: CAWE,
        data_dir: str,
        device: torch.device,
        seed: int = 42
    ):
        """Test robustness across tokenization and dimension variants."""
        ...

    def test_tokenization_variants(self) -> Dict[str, float]:
        """Test 4 tokenization variants. Returns: {'D64': rho, 'D256': rho, 'alt_layer': rho, 'weight_norm': rho}"""
        ...

    def test_token_dimension_variants(
        self,
        dimensions: List[int] = [64, 128, 256]
    ) -> Dict[int, float]:
        """Test D-value variants. Returns: {64: rho, 128: rho, 256: rho}"""
        ...
```

### Pseudo-code

```
1. Tokenization variants (4 total):
   a. D=64 projection: Modify tokenizers to project to 64 dims instead of 128
   b. D=256 projection: Modify tokenizers to project to 256 dims
   c. Alternative layer selection: Skip first/last layers in tokenization
   d. Weight normalization: L2 normalize each layer before tokenization
2. Train separate CAWE model for each variant (same hyperparams, 100 epochs)
3. Evaluate each variant on test set: compute Spearman ρ
4. Success: 2/4 variants achieve ρ > 0.65
5. Dimension variants: Train CAWE with D=64, 128, 256 (success: 2/3 > 0.65)
```

### Subtasks [2/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | RobustnessValidator.test_tokenization_variants | Train 4 variant CAWE models, evaluate each |
| L-4-2 | RobustnessValidator.test_token_dimension_variants | Train D=64,128,256 CAWE models |

---

## B-5: Flat Baseline Training [Complexity: 7, Budget: 1/14]

**Applied:** Standard PyTorch Training Pattern

### API Signatures

```python
def train_flat_baseline(
    data_dir: str,
    input_dim: int,
    epochs: int = 100,
    batch_size: int = 32,
    lr: float = 1e-4,
    device: torch.device = torch.device('cuda'),
    seed: int = 42
) -> Tuple[FlatWeightMLP, float, float, float]:
    """Train FlatWeightMLP baseline. Returns: (model, rho, ci_lower, ci_upper)"""
    # NOTE: Must flatten state_dicts to tensors before passing to FlatWeightMLP!
    ...
```

### Pseudo-code

```
1. Load dataloaders: train_loader, test_loader = create_dataloaders(data_dir)
2. Determine max_params from dataset: max([sum(p.numel() for p in sd.values()) for sd in all_models])
3. Initialize: model = FlatWeightMLP(input_dim=max_params)
4. For each batch:
   a. Flatten state_dicts: weights_flat = [torch.cat([v.flatten() for v in sd.values()]) for sd in batch]
   b. Pad/truncate to max_params: weights_padded = [pad_or_truncate(w, max_params) for w in weights_flat]
   c. Forward: preds = model(torch.stack(weights_padded))
   d. Loss: MSELoss(preds, gaps)
5. Evaluate on test set: compute Spearman ρ with bootstrap CI
```

### Subtasks [1/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | train_flat_baseline | Train FlatWeightMLP with state_dict flattening + padding |

---

## B-6: Full CAWE Training [Complexity: 8, Budget: 1/14]

**Applied:** Standard PyTorch Training Pattern

### API Signatures

```python
def train_full_cawe(
    data_dir: str,
    token_dim: int = 128,
    nft_channels: int = 64,
    epochs: int = 100,
    batch_size: int = 32,
    lr: float = 1e-4,
    device: torch.device = torch.device('cuda'),
    seed: int = 42
) -> Tuple[CAWE, float, float, float]:
    """Train full CAWE on 600 models. Returns: (model, rho, ci_lower, ci_upper)"""
    ...
```

### Pseudo-code

```
1. Load dataloaders: train_loader, val_loader, test_loader = create_dataloaders(data_dir, train_samples=600)
2. Initialize: model = CAWE(token_dim=128, nft_channels=64)
3. Train: AdamW optimizer (lr=1e-4, wd=1e-2), MSELoss, 100 epochs
4. Early stopping: patience=10 on validation ρ
5. Evaluate on test set: compute Spearman ρ with bootstrap CI
6. Save checkpoint for clustering + baseline comparison
```

### Subtasks [1/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | train_full_cawe | Full CAWE training with validation monitoring |

---

## B-7: Mechanism Evaluation Pipeline [Complexity: 15, Budget: 2/14]

**Applied:** Multi-Component Validation Pattern

### API Signatures

```python
class MechanismEvaluationPipeline:
    def __init__(
        self,
        data_dir: str,
        device: torch.device,
        seed: int = 42
    ):
        """Orchestrate 5-component validation."""
        ...

    def run_component_1_per_family_ablation(self) -> Dict[str, Any]:
        """Component 1: Per-family ablation. Returns: {'cnn_rho': float, 'transformer_rho': float, 'mlp_rho': float, 'pass': bool}"""
        ...

    def run_component_2_clustering(self) -> Dict[str, Any]:
        """Component 2: Clustering. Returns: {'silhouette': float, 'pass': bool}"""
        ...

    def run_component_3_flat_baseline(self) -> Dict[str, Any]:
        """Component 3: Flat baseline. Returns: {'delta_rho': float, 'p_value': float, 'pass': bool}"""
        ...

    def run_component_4_rf_baseline(self) -> Dict[str, Any]:
        """Component 4: RF baseline. Returns: {'delta_rho': float, 'p_value': float, 'pass': bool}"""
        ...

    def run_component_5_robustness(self) -> Dict[str, Any]:
        """Component 5: Robustness. Returns: {'tokenization_pass_count': int, 'dimension_pass_count': int, 'pass': bool}"""
        ...

    def aggregate_results(self) -> Dict[str, Any]:
        """Aggregate all component results. Returns: {'component_1_pass': bool, ..., 'total_passed': int, 'gate_status': str}"""
        ...
```

### Pseudo-code

```
1. Run Component 1: Per-family ablation (B-1)
   - Train 3 separate CAWE models (CNN-only, Transformer-only, MLP-only)
   - Threshold: All 3 ρ > 0.7 → PASS
2. Run Component 2: Clustering (B-2)
   - Extract embeddings from full CAWE (600 models)
   - Silhouette score > 0.5 → PASS
3. Run Component 3: Flat baseline (B-5)
   - Train FlatWeightMLP, compute Δρ = ρ_CAWE - ρ_flat
   - Paired t-test: Δρ > 0.15, p < 0.001 → PASS
4. Run Component 4: RF baseline (B-3)
   - Train RandomForest, compute Δρ = ρ_CAWE - ρ_RF
   - Wilcoxon test: Δρ > 0.1, p < 0.01 → PASS
5. Run Component 5: Robustness (B-4)
   - Test 4 tokenization variants + 3 D-values
   - 2/4 tokenization + 2/3 D-values pass ρ > 0.65 → PASS
6. Aggregate: Count total passed (threshold: ≥3/5 for SHOULD_WORK gate)
```

### Subtasks [2/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | MechanismEvaluationPipeline orchestration | Run all 5 components sequentially |
| L-7-2 | aggregate_results | Compute pass/fail per component, gate decision |

---

## B-8: Visualization Suite [Complexity: 10, Budget: 2/14]

**Applied:** Matplotlib/Seaborn Visualization Pattern

### API Signatures

```python
def plot_component_pass_fail_matrix(
    results: Dict[str, Any],
    save_path: str
) -> None:
    """Plot 5-component pass/fail matrix. results: {'component_1_pass': bool, ...}"""
    ...

def plot_per_family_comparison(
    family_rhos: Dict[str, float],
    threshold: float = 0.7,
    save_path: str
) -> None:
    """Plot per-family ρ bar chart with threshold line."""
    ...

def plot_architecture_clustering_tsne(
    embeddings: np.ndarray,
    labels: np.ndarray,
    silhouette: float,
    save_path: str
) -> None:
    """t-SNE visualization of CAWE embeddings. embeddings: [750, 128], labels: [750]"""
    ...

def plot_baseline_comparison(
    cawe_rho: float,
    flat_rho: float,
    rf_rho: float,
    save_path: str
) -> None:
    """Grouped bar chart: CAWE vs Flat vs RF with Δρ annotations."""
    ...

def plot_robustness_heatmap(
    robustness_results: Dict[str, Any],
    save_path: str
) -> None:
    """Heatmap: tokenization variants × D-values with ρ values."""
    ...
```

### Subtasks [2/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Component pass/fail matrix + per-family + clustering plots | 3 mandatory figures |
| L-8-2 | Baseline comparison + robustness heatmap | 2 additional figures |

---

## Budget Summary

| Task | Complexity | Budget | Used | Status |
|------|------------|--------|------|--------|
| B-1 | 13 | 2 | 2 | ✓ |
| B-2 | 11 | 2 | 2 | ✓ |
| B-3 | 12 | 2 | 2 | ✓ |
| B-4 | 14 | 2 | 2 | ✓ |
| B-5 | 7 | 1 | 1 | ✓ |
| B-6 | 8 | 1 | 1 | ✓ |
| B-7 | 15 | 2 | 2 | ✓ |
| B-8 | 10 | 2 | 2 | ✓ |
| **Total** | **90** | **14** | **14** | **✓** |

**All budgets fully utilized. Ready for Phase 4 implementation.**

---

## Statistical Testing Details

### Paired t-test (Component 3)

```python
from scipy.stats import ttest_rel

# Compute predictions
cawe_preds = [cawe.forward(sd, family) for sd, family, _ in test_dataset]
flat_preds = [flat_model.forward(flatten(sd)) for sd, _, _ in test_dataset]

# Paired t-test (one-tailed)
t_stat, p_value = ttest_rel(cawe_preds, flat_preds, alternative='greater')
# Success: p_value < 0.001
```

### Wilcoxon Signed-Rank Test (Component 4)

```python
from scipy.stats import wilcoxon

# Compute predictions
cawe_preds = [cawe.forward(sd, family) for sd, family, _ in test_dataset]
rf_preds = [rf_model.predict(extract_features(sd)) for sd, _, _ in test_dataset]

# Wilcoxon test (non-parametric, one-tailed)
statistic, p_value = wilcoxon(cawe_preds, rf_preds, alternative='greater')
# Success: p_value < 0.01
```

### Bootstrap Confidence Interval (All Components)

```python
from scipy.stats import spearmanr
import numpy as np

def compute_spearman_with_ci(y_true, y_pred, n_bootstrap=1000, confidence=0.95, seed=42):
    """Compute Spearman ρ with bootstrap CI."""
    rng = np.random.default_rng(seed)
    rho, _ = spearmanr(y_true, y_pred)

    # Bootstrap resampling
    bootstrap_rhos = []
    for _ in range(n_bootstrap):
        indices = rng.choice(len(y_true), size=len(y_true), replace=True)
        boot_rho, _ = spearmanr(y_true[indices], y_pred[indices])
        bootstrap_rhos.append(boot_rho)

    # Percentile CI
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_rhos, 100 * alpha / 2)
    ci_upper = np.percentile(bootstrap_rhos, 100 * (1 - alpha / 2))

    return rho, ci_lower, ci_upper
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text descriptions only)
- [x] No KB search logs (only "Applied: X" patterns)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] All subtask counts within budget (14 total)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Base hypothesis code verified (parameter names match actual implementation)
- [x] "External Dependencies API" section included
- [x] All API signatures are copy-paste ready with type hints
- [x] Parameter names verified from actual h-e1 code (weights, arch_family, NOT state_dict/family)
- [x] FlatWeightMLP pre-flattening requirement documented

---

*Generated by Phase 3 Logic Design*
*Input: 03_architecture.md, 03_prd.md*
*Base Hypothesis: h-e1 (APIs verified from actual code)*
*Next: Phase 4 Implementation (Coder will match these exact signatures)*
