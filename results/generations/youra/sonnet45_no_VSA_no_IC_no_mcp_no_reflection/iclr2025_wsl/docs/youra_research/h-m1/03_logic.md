# Logic Specification: h-m1

**Date:** 2026-08-28  
**Author:** Phase 3 Logic Agent  
**Hypothesis:** Transformer captures global dependencies while Equivariant GNN captures local permutation-symmetric patterns  
**Type:** MECHANISM

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 actual code  
**Analyzed Path:** h-e1/src/  
**Relevant Symbols:** TimmModelZooLoader, WeightTokenizer, WeightTransformer, Trainer, EarlyStopping

---

## Task Allocation

| Task ID | Name | Complexity | Budget | Status |
|---------|------|------------|--------|--------|
| M1-2 | Perturbations | 6 | 6 | ALLOCATED |
| M1-4 | Perturbation evaluation | 9 | 9 | ALLOCATED |
| M1-6 | Visualization | 8 | 8 | ALLOCATED |

**Total Budget:** 23 subtasks (3 allocated from available 3)

**Note:** Tasks M1-1 (GNN model), M1-3 (training), M1-5 (differential) deferred to Config Agent as standard configurations.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1. Signatures verified from actual implementation:

```python
# From: h-e1/src/data_loader.py
class TimmModelZooLoader:
    def __init__(self, families: List[str], num_models: int, cache_path: str, seed: int = 42):
        """Initialize loader with model filtering criteria."""
        
    def load_models(self) -> List[Tuple[str, nn.Module, int]]:
        """Load models from timm. Returns: [(name, model, family_id), ...]"""
        
    def extract_weights(self, model: nn.Module) -> List[Tensor]:
        """Extract layer weights. Returns: [layer_tensor, ...]"""
        
    def split_data(
        self,
        models_data: List,
        train_size: float = 0.7,
        val_size: float = 0.15,
        test_size: float = 0.15
    ) -> Tuple[List, List, List]:
        """Stratified split by family. Returns: (train, val, test)"""

class WeightTokenizer:
    def __init__(self, max_layer_size: int = 4096, normalize: bool = True):
        """Initialize tokenizer with padding parameters."""
        
    def tokenize(self, layer_weights: List[Tensor]) -> Tensor:
        """Flatten + pad layers. Returns: [T, max_size]"""

# From: h-e1/src/model.py
class WeightTransformer(nn.Module):
    def __init__(
        self,
        max_layer_size: int = 4096,
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 1024,
        dropout: float = 0.1,
        num_classes: int = 4
    ):
        """Initialize weight transformer."""
        
    def forward(self, layer_tokens: Tensor) -> Tensor:
        """Forward pass. tokens: [B, T, max_size] -> [B, C]"""

# From: h-e1/src/train.py
class EarlyStopping:
    def __init__(self, patience: int = 10, min_delta: float = 1e-4):
        """Initialize early stopping."""
        
    def __call__(self, val_loss: float) -> bool:
        """Check if should stop. Returns: True if no improvement"""

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        optimizer: Optimizer,
        scheduler: _LRScheduler,
        criterion: nn.Module,
        device: str = "cuda",
        gradient_clip_max_norm: float = 1.0
    ):
        """Initialize trainer."""
        
    def train_epoch(self, dataloader: DataLoader) -> Dict[str, float]:
        """Single training epoch. Returns: {loss, accuracy}"""
        
    def validate(self, dataloader: DataLoader) -> Dict[str, float]:
        """Validation pass. Returns: {loss, accuracy}"""
        
    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        patience: int = 10,
        checkpoint_path: str = "best_model.pt"
    ) -> Dict:
        """Full training loop. Returns: {train_history, val_history, best_epoch}"""
```

**Verified from:** h-e1/src/ (actual implementation)

---

## M1-2: Perturbations [Complexity: 6, Budget: 6]

**Applied:** Standard PyTorch tensor manipulation

### API Signatures

```python
def permute_within_layer(layer_tokens: Tensor, seed: Optional[int] = None) -> Tensor:
    """Shuffle indices within each layer. [B, T, L] -> [B, T, L]"""
    
def permute_across_layers(layer_tokens: Tensor, seed: Optional[int] = None) -> Tensor:
    """Shuffle indices across all layers. [B, T, L] -> [B, T, L]"""
    
def apply_perturbation(layer_tokens: Tensor, perturb_type: Optional[str], seed: int = 42) -> Tensor:
    """Unified interface. type in {None, 'within', 'across'}. [B, T, L] -> [B, T, L]"""
```

### Pseudo-code

```
permute_within_layer(tokens, seed):
    set_seed(seed)
    B, T, L = tokens.shape
    perturbed = tokens.clone()
    for b in range(B):
        for t in range(T):
            idx = randperm(L)
            perturbed[b, t] = perturbed[b, t, idx]
    return perturbed

permute_across_layers(tokens, seed):
    set_seed(seed)
    B, T, L = tokens.shape
    perturbed = tokens.view(B, -1)  # [B, T*L]
    for b in range(B):
        idx = randperm(T * L)
        perturbed[b] = perturbed[b, idx]
    return perturbed.view(B, T, L)

apply_perturbation(tokens, type, seed):
    if type is None:
        return tokens
    elif type == 'within':
        return permute_within_layer(tokens, seed)
    elif type == 'across':
        return permute_across_layers(tokens, seed)
    else:
        raise ValueError(f"Unknown perturbation type: {type}")
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | within_layer_shuffle | Implement per-layer index permutation |
| L-2-2 | across_layer_shuffle | Implement global index permutation |
| L-2-3 | seed_control | Deterministic seeding for reproducibility |
| L-2-4 | tensor_cloning | Avoid in-place mutation |
| L-2-5 | shape_preservation | Maintain [B, T, L] throughout |
| L-2-6 | unified_interface | Single apply_perturbation dispatcher |

---

## M1-4: Perturbation Evaluation [Complexity: 9, Budget: 9]

**Applied:** PyTorch evaluation loop pattern

### API Signatures

```python
def evaluate_with_perturbations(
    model: nn.Module,
    test_loader: DataLoader,
    device: str,
    seed: int = 42
) -> Dict[str, float]:
    """Evaluate on unperturbed/within/across. Returns: {unperturbed_acc, within_acc, across_acc}"""
    
def compute_symmetry_differential(results: Dict[str, float]) -> float:
    """Compute |within_acc - across_acc|. Returns: differential in [0, 1]"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_tokens | [B, T, L] | Input batch |
| logits | [B, C] | Model output |
| preds | [B] | Argmax predictions |

### Pseudo-code

```
evaluate_with_perturbations(model, test_loader, device, seed):
    model.eval()
    results = {}
    
    for perturb_type in [None, 'within', 'across']:
        correct = 0
        total = 0
        
        for batch_tokens, labels in test_loader:
            batch_tokens = batch_tokens.to(device)
            labels = labels.to(device)
            
            # Apply perturbation
            perturbed = apply_perturbation(batch_tokens, perturb_type, seed)
            
            # Forward pass
            with torch.no_grad():
                logits = model(perturbed)
                preds = logits.argmax(dim=1)
            
            correct += (preds == labels).sum().item()
            total += labels.size(0)
        
        key = 'unperturbed_acc' if perturb_type is None else f'{perturb_type}_acc'
        results[key] = correct / total
    
    return results

compute_symmetry_differential(results):
    within = results['within_acc']
    across = results['across_acc']
    return abs(within - across)
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | eval_loop_structure | Iterate over perturbation types |
| L-4-2 | batch_perturbation | Apply perturbation before forward |
| L-4-3 | accuracy_computation | Track correct predictions |
| L-4-4 | unperturbed_baseline | Evaluate without perturbation |
| L-4-5 | within_layer_eval | Evaluate on within-layer perturbation |
| L-4-6 | across_layer_eval | Evaluate on across-layer perturbation |
| L-4-7 | differential_computation | Compute absolute difference |
| L-4-8 | result_dict_assembly | Structure output |
| L-4-9 | no_grad_context | Disable gradient computation |

---

## M1-6: Visualization [Complexity: 8, Budget: 8]

**Applied:** Matplotlib bar chart and heatmap patterns

### API Signatures

```python
def plot_differential_comparison(
    transformer_results: Dict[str, float],
    gnn_results: Dict[str, float],
    save_path: str
) -> None:
    """Bar chart: Transformer vs GNN differential."""
    
def plot_degradation_heatmap(
    transformer_results: Dict[str, float],
    gnn_results: Dict[str, float],
    save_path: str
) -> None:
    """Heatmap: 2 models × 3 perturbation types accuracy."""
```

### Pseudo-code

```
plot_differential_comparison(transformer_results, gnn_results, save_path):
    transformer_diff = compute_symmetry_differential(transformer_results)
    gnn_diff = compute_symmetry_differential(gnn_results)
    
    fig, ax = plt.subplots()
    models = ['Transformer', 'GNN']
    diffs = [transformer_diff, gnn_diff]
    
    ax.bar(models, diffs)
    ax.axhline(0.30, color='green', linestyle='--', label='GNN threshold (30%)')
    ax.axhline(0.10, color='red', linestyle='--', label='Transformer threshold (10%)')
    ax.set_ylabel('Symmetry Differential')
    ax.set_title('Perturbation Sensitivity Comparison')
    ax.legend()
    
    plt.savefig(save_path)
    plt.close()

plot_degradation_heatmap(transformer_results, gnn_results, save_path):
    data = [
        [transformer_results['unperturbed_acc'], 
         transformer_results['within_acc'], 
         transformer_results['across_acc']],
        [gnn_results['unperturbed_acc'], 
         gnn_results['within_acc'], 
         gnn_results['across_acc']]
    ]
    
    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap='RdYlGn', vmin=0, vmax=1)
    
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Unperturbed', 'Within-Layer', 'Across-Layer'])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Transformer', 'GNN'])
    
    for i in range(2):
        for j in range(3):
            ax.text(j, i, f'{data[i][j]:.2f}', ha='center', va='center')
    
    plt.colorbar(im, ax=ax, label='Accuracy')
    plt.title('Accuracy Under Perturbations')
    plt.savefig(save_path)
    plt.close()
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | differential_extraction | Extract differential from results |
| L-6-2 | bar_chart_setup | Create matplotlib bar plot |
| L-6-3 | threshold_lines | Add horizontal reference lines |
| L-6-4 | heatmap_data_prep | Assemble 2×3 accuracy matrix |
| L-6-5 | heatmap_colormap | Apply RdYlGn colormap |
| L-6-6 | cell_annotations | Add accuracy values to cells |
| L-6-7 | axis_labels | Set model and perturbation labels |
| L-6-8 | save_figures | Save to PNG/PDF |

---

*Logic Status: FINAL*  
*Next Phase: Phase 4 - Implementation (Coder-Validator loop)*
