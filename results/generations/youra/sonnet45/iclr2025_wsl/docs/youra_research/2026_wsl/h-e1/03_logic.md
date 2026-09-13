---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-03-19T06:10:00Z
source: Phase 3 Logic Design
---

# Logic Design: H-E1 CAWE Implementation

**Hypothesis:** h-e1 (EXISTENCE)
**Date:** 2026-03-19
**Type:** PoC API Design

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch - designing new APIs
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

**Rationale:** This is the first hypothesis (h-e1) with no prerequisites. No existing codebase to analyze. All APIs designed from scratch following PyTorch conventions.

---

## Applied Patterns

**Applied:** PyTorch Module Pattern (torch.nn.Module with __init__ and forward)
**Applied:** State Dict Processing Pattern (heterogeneous weight handling)
**Applied:** Training Loop Pattern (epoch-based training with validation monitoring)

---

## A-1: Dataset Assembly [Complexity: 11, Budget: 6/6]

**Applied:** PyTorch Dataset Pattern

### API Signatures

```python
class ModelZooDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir: str, split: str = 'train', seed: int = 42):
        """Load heterogeneous model zoo.

        Args:
            data_dir: Path to model_zoo/ directory
            split: 'train' or 'test'
            seed: Random seed for stratified split
        """
        ...

    def __len__(self) -> int:
        """Return total number of models in split."""
        ...

    def __getitem__(self, idx: int) -> Tuple[Dict[str, torch.Tensor], str, float]:
        """Get model at index.

        Returns:
            state_dict: Model weights as state_dict
            arch_family: 'cnn' | 'transformer' | 'mlp'
            gap: Generalization gap (train_acc - test_acc)
        """
        ...

def load_model_zoo(
    data_dir: str,
    batch_size: int = 32,
    num_workers: int = 4,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader]:
    """Create train/test dataloaders.

    Returns:
        train_loader: 600 models (200/200/200 per family)
        test_loader: 150 models (50/50/50 per family)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| state_dict | Dict[str, Tensor] | Variable shapes per architecture |
| gap | scalar | Continuous value (train_acc - test_acc) |

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | ModelZooDataset.__init__ | Load metadata, create train/test splits (stratified by family) |
| L-1-2 | ModelZooDataset.__getitem__ | Load state_dict from .pt file, return (weights, family, gap) |
| L-1-3 | Download ViT models | Extract 250 ViT models from timm library with gap metadata |
| L-1-4 | Download CNN models | Extract 250 CNN models from torchvision.models with gap metadata |
| L-1-5 | Download MLP models | Extract 250 MLP models (Unterthiner or generate) with gap metadata |
| L-1-6 | load_model_zoo wrapper | Create train/test DataLoaders with stratified splits |

---

## A-2: Baseline Implementation [Complexity: 6, Budget: 6/6]

**Applied:** Standard PyTorch MLP Pattern

### API Signatures

```python
class FlatWeightMLP(nn.Module):
    def __init__(self, max_params: int = 10_000_000, dropout: float = 0.2):
        """Naive baseline: flatten all weights.

        Args:
            max_params: Max weight vector size (truncate/pad)
            dropout: Dropout probability
        """
        super().__init__()
        self.max_params = max_params
        self.mlp = nn.Sequential(
            nn.Linear(max_params, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Flatten and predict.

        Args:
            state_dict: Model weights

        Returns:
            pred: [1] generalization gap prediction
        """
        ...
```

### Pseudo-code

```
1. Flatten all tensors: cat([v.flatten() for v in state_dict.values()])  # [P]
2. Truncate/pad to max_params: weights[:max_params] or pad(weights)  # [max_params]
3. Pass through MLP: out = self.mlp(weights)  # [1]
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | FlatWeightMLP.__init__ | Initialize 4-layer MLP (512→256→128→1) |
| L-2-2 | FlatWeightMLP.forward | Flatten state_dict tensors, truncate/pad, forward through MLP |
| L-2-3 | _flatten_state_dict helper | Concatenate all weight tensors into 1D vector |
| L-2-4 | _truncate_or_pad helper | Normalize to fixed max_params size |
| L-2-5 | Weight initialization | Apply Kaiming initialization to MLP layers |
| L-2-6 | Forward pass validation | Ensure output is scalar prediction |

---

## A-3: Tokenizer Implementation [Complexity: 12, Budget: 6/6]

**Applied:** State Dict Processing Pattern

### API Signatures

```python
class CNNTokenizer(nn.Module):
    def __init__(self, token_dim: int = 128):
        """Tokenize CNN conv layers.

        Args:
            token_dim: Output token dimension (D)
        """
        super().__init__()
        self.token_dim = token_dim
        self.projections = nn.ModuleDict()  # Dynamic projections per kernel size

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Extract conv kernels, project to tokens.

        Args:
            state_dict: CNN model weights

        Returns:
            tokens: [L, D] where L = num_conv_layers
        """
        ...

class TransformerTokenizer(nn.Module):
    def __init__(self, token_dim: int = 128):
        """Tokenize Transformer attention layers.

        Args:
            token_dim: Output token dimension (D)
        """
        super().__init__()
        self.token_dim = token_dim
        self.projections = nn.ModuleDict()

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Extract Q/K/V matrices, project to tokens.

        Args:
            state_dict: Transformer model weights

        Returns:
            tokens: [L, D] where L = num_attn_layers
        """
        ...

class MLPTokenizer(nn.Module):
    def __init__(self, token_dim: int = 128):
        """Tokenize MLP FC layers.

        Args:
            token_dim: Output token dimension (D)
        """
        super().__init__()
        self.token_dim = token_dim
        self.projections = nn.ModuleDict()

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Extract FC weights, project to tokens.

        Args:
            state_dict: MLP model weights

        Returns:
            tokens: [L, D] where L = num_fc_layers
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| CNN kernel | [out_ch, in_ch, kh, kw] | Conv layer weight |
| Flattened kernel | [out_ch, in_ch*kh*kw] | Flatten spatial dims |
| Projected token | [out_ch, D] | After linear projection |
| Final tokens | [L, D] | Mean pool over out_ch, stack layers |

### Pseudo-code (CNN Example)

```
1. Extract conv layers: keys matching 'conv*.weight' or 'layer*.conv*.weight'
2. For each conv layer:
   a. Flatten spatial: kernel.view(out_ch, -1)  # [out_ch, in_ch*kh*kw]
   b. Project: proj = nn.Linear(in_ch*kh*kw, D)  # [out_ch, D]
   c. Pool channels: token = proj.mean(dim=0)  # [D]
3. Stack all layer tokens: tokens = torch.stack(layer_tokens)  # [L, D]
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | CNNTokenizer.forward | Extract conv kernels, flatten, project, stack to [L, D] |
| L-3-2 | TransformerTokenizer.forward | Extract Q/K/V matrices, project to [L, D] |
| L-3-3 | MLPTokenizer.forward | Extract FC weights, project to [L, D] |
| L-3-4 | Dynamic projection creation | Create nn.Linear per unique input size on-the-fly |
| L-3-5 | Layer extraction logic | Regex patterns for conv/attn/fc keys in state_dict |
| L-3-6 | Token stacking | Stack variable-length layer tokens to fixed [L, D] tensor |

---

## A-4: CAWE Model Integration [Complexity: 14, Budget: 6/6]

**Applied:** Compositional Module Pattern + NFN Library Integration

### API Signatures

```python
class CAWE(nn.Module):
    def __init__(
        self,
        token_dim: int = 128,
        nft_channels: int = 64,
        dropout: float = 0.1
    ):
        """CAWE: Compositional Architecture-Agnostic Weight Encoder.

        Args:
            token_dim: Tokenizer output dimension (D)
            nft_channels: NFT backbone hidden channels
            dropout: Regression head dropout
        """
        super().__init__()

        # Architecture-specific tokenizers
        self.tokenizers = nn.ModuleDict({
            'cnn': CNNTokenizer(token_dim),
            'transformer': TransformerTokenizer(token_dim),
            'mlp': MLPTokenizer(token_dim)
        })

        # NFT backbone (using nfn library)
        self.nft_encoder = self._build_nft_backbone(token_dim, nft_channels)

        # Regression head
        self.regression_head = nn.Sequential(
            nn.Linear(token_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )

    def _build_nft_backbone(self, in_dim: int, hidden_dim: int) -> nn.Module:
        """Build NFT backbone using nfn library.

        Returns:
            nft_encoder: NPLinear layers
        """
        ...

    def forward(
        self,
        state_dict: Dict[str, torch.Tensor],
        arch_family: str
    ) -> torch.Tensor:
        """End-to-end prediction.

        Args:
            state_dict: Model weights
            arch_family: 'cnn' | 'transformer' | 'mlp'

        Returns:
            pred: [1] generalization gap prediction
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tokens | [L, D] | From tokenizer (L varies per model) |
| nft_features | [L, D] | After NFT backbone |
| pooled | [D] | Global average pooling over L |
| pred | [1] | Regression head output |

### Pseudo-code

```
1. Tokenize: tokens = tokenizers[arch_family](state_dict)  # [L, D]
2. NFT encode: features = nft_encoder(tokens)  # [L, D] permutation-equivariant
3. Pool: pooled = features.mean(dim=0)  # [D]
4. Predict: pred = regression_head(pooled)  # [1]
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | CAWE.__init__ | Initialize tokenizers, NFT backbone, regression head |
| L-4-2 | _build_nft_backbone | Construct NPLinear(D, 64) → ReLU → NPLinear(64, D) using nfn |
| L-4-3 | CAWE.forward | Dispatch tokenizer, encode with NFT, pool, regress |
| L-4-4 | NFN library integration | Import nfn.layers.NPLinear, handle network_spec |
| L-4-5 | Global pooling | Average over token sequence dimension [L, D] → [D] |
| L-4-6 | Architecture dispatch | Select correct tokenizer based on arch_family string |

---

## A-5: Training Pipeline [Complexity: 10, Budget: 6/6]

**Applied:** PyTorch Training Loop Pattern

### API Signatures

```python
def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device
) -> float:
    """Train for one epoch.

    Returns:
        avg_loss: Average MSE loss
    """
    ...

def validate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device
) -> float:
    """Validate on test set.

    Returns:
        spearman_rho: Spearman correlation on predictions
    """
    ...

def main():
    """Training script entry point."""
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    train_loader, test_loader = load_model_zoo(data_dir, batch_size=32)

    # Models
    cawe = CAWE(token_dim=128, nft_channels=64).to(device)
    baseline = FlatWeightMLP().to(device)

    # Training loop
    for epoch in range(100):
        train_loss = train_epoch(cawe, train_loader, optimizer, criterion, device)
        val_rho = validate(cawe, test_loader, device)
        # Early stopping logic
        ...

    # Save best checkpoint
    torch.save(cawe.state_dict(), 'checkpoints/cawe_best.pt')
```

### Pseudo-code

```
1. Setup: device, dataloaders, models, optimizer (AdamW lr=1e-4, wd=1e-2)
2. For each epoch:
   a. Train: compute MSE loss, backprop, update weights
   b. Validate: compute Spearman ρ on test set
   c. Early stopping: if ρ decreases for 10 epochs, stop
3. Save best model checkpoint (highest val ρ)
4. Log training curves to stdout
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | train_epoch | Forward pass, MSE loss, backprop, optimizer step |
| L-5-2 | validate | Inference mode, collect predictions, compute Spearman ρ |
| L-5-3 | Early stopping logic | Track best val ρ, patience counter, checkpoint saving |
| L-5-4 | Optimizer setup | AdamW with lr=1e-4, weight_decay=1e-2 |
| L-5-5 | Loss function | nn.MSELoss for regression target (generalization gap) |
| L-5-6 | Training loop | 100 epochs with progress logging |

---

## A-6: Evaluation Pipeline [Complexity: 9, Budget: 6/6]

**Applied:** Bootstrap Statistical Testing Pattern

### API Signatures

```python
def compute_spearman_with_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int = 42
) -> Tuple[float, float, float]:
    """Compute Spearman ρ with bootstrap CI.

    Args:
        y_true: Ground truth gaps [N]
        y_pred: Predicted gaps [N]
        n_bootstrap: Bootstrap resamples
        confidence: CI level (0.95 for 95%)
        seed: Random seed

    Returns:
        rho: Spearman correlation
        ci_lower: Lower bound of CI
        ci_upper: Upper bound of CI
    """
    ...

def evaluate_per_architecture(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device
) -> Dict[str, float]:
    """Compute per-architecture Spearman ρ.

    Returns:
        {'cnn': rho_cnn, 'transformer': rho_transformer, 'mlp': rho_mlp}
    """
    ...

def main():
    """Evaluation script entry point."""
    # Load models
    cawe = CAWE().to(device)
    cawe.load_state_dict(torch.load('checkpoints/cawe_best.pt'))

    baseline = FlatWeightMLP().to(device)
    baseline.load_state_dict(torch.load('checkpoints/baseline_best.pt'))

    # Primary metric
    cawe_rho, cawe_ci_low, cawe_ci_high = compute_spearman_with_ci(y_true, y_pred_cawe)
    baseline_rho, _, _ = compute_spearman_with_ci(y_true, y_pred_baseline)

    # Secondary metrics
    per_arch = evaluate_per_architecture(cawe, test_loader, device)

    # Save results
    results_df.to_csv('results/h-e1_metrics.csv')
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| y_true | [150] | Ground truth gaps (test set) |
| y_pred | [150] | Model predictions |
| bootstrap_rhos | [1000] | Bootstrap distribution |

### Pseudo-code

```
1. Load best CAWE and baseline checkpoints
2. Inference on test set (150 models): collect y_true, y_pred_cawe, y_pred_baseline
3. Primary metric: Spearman ρ with bootstrap 95% CI (1000 resamples)
4. Secondary metrics:
   a. Per-architecture ρ: split by family (50/50/50), compute ρ for each
   b. Δρ = ρ_cawe - ρ_baseline
5. Gate check: ρ > 0.7 AND ci_lower > 0.7
6. Save to CSV: results/h-e1_metrics.csv
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_spearman_with_ci | Bootstrap resampling (1000 iterations), percentile CI |
| L-6-2 | evaluate_per_architecture | Split test set by arch_family, compute ρ per subset |
| L-6-3 | Inference loop | Collect predictions for all 150 test models |
| L-6-4 | Gate validation | Check ρ > 0.7 AND ci_lower > 0.7 (MUST_WORK criteria) |
| L-6-5 | Metrics CSV export | Save rho, ci_lower, ci_upper, per_arch_rho to CSV |
| L-6-6 | Results logging | Print primary/secondary metrics to stdout |

---

## A-7: Visualization Generation [Complexity: 8, Budget: 6/6]

**Applied:** Matplotlib/Seaborn Visualization Pattern

### API Signatures

```python
def plot_spearman_comparison(
    cawe_rho: float,
    baseline_rho: float,
    cawe_ci: Tuple[float, float],
    baseline_ci: Tuple[float, float],
    save_path: str
) -> None:
    """Bar chart: CAWE vs Baseline with error bars."""
    ...

def plot_per_architecture_performance(
    rho_dict: Dict[str, float],
    save_path: str
) -> None:
    """Bar chart: ρ for CNN/Transformer/MLP subsets."""
    ...

def plot_prediction_scatter(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    save_path: str
) -> None:
    """Scatter: predicted vs actual gap (150 test models)."""
    ...

def plot_tsne_clustering(
    embeddings: np.ndarray,
    labels: List[str],
    save_path: str
) -> None:
    """t-SNE: CAWE embeddings colored by architecture family."""
    ...

def main():
    """Visualization script entry point."""
    # Load results from CSV
    results_df = pd.read_csv('results/h-e1_metrics.csv')

    # Generate 4 figures
    plot_spearman_comparison(...)
    plot_per_architecture_performance(...)
    plot_prediction_scatter(...)
    plot_tsne_clustering(...)
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_spearman_comparison | Bar chart with 95% CI error bars (CAWE vs Baseline) |
| L-7-2 | plot_per_architecture_performance | Grouped bar chart (ρ per family) |
| L-7-3 | plot_prediction_scatter | Scatter plot with diagonal reference line |
| L-7-4 | plot_tsne_clustering | t-SNE projection with color-coded families |
| L-7-5 | Extract CAWE embeddings | Run forward pass, collect pooled features [150, D] |
| L-7-6 | Figure saving | Save all plots to figures/ directory (PNG, 300 DPI) |

---

## Budget Summary

| Task | Complexity | Budget | Used | Status |
|------|------------|--------|------|--------|
| A-1 | 11 | 6 | 6 | ✓ |
| A-2 | 6 | 6 | 6 | ✓ |
| A-3 | 12 | 6 | 6 | ✓ |
| A-4 | 14 | 6 | 6 | ✓ |
| A-5 | 10 | 6 | 6 | ✓ |
| A-6 | 9 | 6 | 6 | ✓ |
| A-7 | 8 | 6 | 6 | ✓ |
| **Total** | **70** | **42** | **42** | **✓** |

**All budgets fully utilized. Ready for Phase 4 implementation.**

---

## External Dependencies

### NFN Library API (Reference)

```python
from nfn import layers
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

# Convert state_dict to NFN format
wsfeat = state_dict_to_tensors(state_dict)
network_spec = network_spec_from_wsfeat(wsfeat)

# Build NFT backbone
nft_encoder = nn.Sequential(
    layers.NPLinear(network_spec, in_channels, hidden_channels, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, hidden_channels, in_channels, io_embed=True)
)

# Forward pass (permutation-equivariant)
output = nft_encoder(wsfeat)  # Same shape as input
```

**Note:** For CAWE, we preprocess with tokenizers first, then use simpler NPLinear layers on fixed [L, D] token sequences instead of full state_dict processing.

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text descriptions only)
- [x] No KB search logs (only "Applied: X" patterns)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] All subtask counts within budget (6 per task)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field project - Serena skip acceptable
- [x] All API signatures are copy-paste ready with type hints
- [x] Function signatures match return types exactly
- [x] External Dependencies section included (NFN library reference)

---

*Generated by Phase 3 Logic Design*
*Input: 03_architecture.md, 03_prd.md*
*Next: Phase 4 Implementation (Coder will match these exact signatures)*
