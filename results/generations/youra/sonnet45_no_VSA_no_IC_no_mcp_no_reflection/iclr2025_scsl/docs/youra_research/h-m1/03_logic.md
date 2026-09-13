# Logic Design: h-m1 Layer-Neuron Consistency Analysis

**Date:** 2026-08-29  
**Hypothesis:** h-m1 (MECHANISM)  
**Author:** Logic Agent  
**Input:** 03_architecture.md, 03_prd.md

---

## Codebase Analysis (Serena)

### Base Hypothesis Code (h-e1) API Verification

**Analyzed Files:**
- `h-e1/code/` (model training scripts)
- `h-e1/checkpoints/baseline_seed0.pt` (checkpoint format)

**Verified Interfaces:**

```python
# h-e1 checkpoint structure (verified from saved files)
checkpoint = {
    'model_state_dict': OrderedDict(...),  # PyTorch state dict
    'epoch': int,
    'optimizer_state_dict': OrderedDict(...),
    # Note: No 'spurious_labels' in checkpoint - must regenerate from dataset
}

# h-e1 dataset loading pattern (inferred from standard CMNIST)
class CMNISTDataset:
    def __getitem__(self, idx) -> Tuple[torch.Tensor, int, int]:
        """
        Returns:
            image: (3, 28, 28) RGB tensor
            label: int (digit 0-9)
            color: int (spurious feature 0-9)
        """
```

**Reuse Decision:** h-m1 loads h-e1 checkpoint model_state_dict only. Spurious labels regenerated via same color corruption transform.

---

## Applied: DL Module API Pattern

**Source:** Standard PyTorch module design  
**Pattern:** Class-based encapsulation with clear input/output contracts  
**Justification:** LayerNeuronAnalyzer follows standard hook-based activation extraction pattern

---

## Core APIs

### 1. LayerNeuronAnalyzer Class

```python
class LayerNeuronAnalyzer:
    """
    Analyzes layer-wise neuron correlations with spurious features.
    
    Attributes:
        model: Pre-trained ResNet-18 from h-e1
        layer_names: List of layer names to analyze
        activations: Dict[str, torch.Tensor] storing layer outputs
    """
    
    def __init__(
        self,
        model: torch.nn.Module,
        layer_names: List[str] = ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']
    ) -> None:
        """
        Initialize analyzer and register forward hooks.
        
        Args:
            model: Pre-trained model (ResNet-18)
            layer_names: Layers to extract activations from
        
        Postconditions:
            - Hooks registered for all specified layers
            - self.activations initialized as empty dict
        """
        self.model = model
        self.layer_names = layer_names
        self.activations: Dict[str, torch.Tensor] = {}
        self._register_hooks()
    
    def _register_hooks(self) -> None:
        """
        Register forward hooks for layer-wise activation extraction.
        
        Side Effects:
            - Forward hook attached to each layer in layer_names
            - Hook stores activations in self.activations dict
        """
        def get_activation(name: str):
            def hook(module, input, output):
                # Detach to avoid gradient tracking
                self.activations[name] = output.detach()
            return hook
        
        for layer_name in self.layer_names:
            layer = getattr(self.model, layer_name)
            layer.register_forward_hook(get_activation(layer_name))
    
    def compute_layer_correlations(
        self,
        dataloader: torch.utils.data.DataLoader,
        spurious_labels: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Compute per-neuron Pearson correlation with spurious feature.
        
        Args:
            dataloader: CMNIST test set loader
            spurious_labels: (N,) array of color labels (0-9)
        
        Returns:
            layer_rho_j: Dict mapping layer_name → (num_channels,) correlation array
        
        Tensor Shapes:
            - Input batch: (batch_size, 3, 28, 28)
            - conv1 activation: (batch_size, 64, 28, 28) → pooled (batch_size, 64)
            - layer1 activation: (batch_size, 64, 28, 28) → pooled (batch_size, 64)
            - layer2 activation: (batch_size, 128, 14, 14) → pooled (batch_size, 128)
            - layer3 activation: (batch_size, 256, 7, 7) → pooled (batch_size, 256)
            - layer4 activation: (batch_size, 512, 4, 4) → pooled (batch_size, 512)
        
        Algorithm:
            1. Forward pass through model (all samples)
            2. Spatial pooling: mean over H×W dimensions
            3. Concatenate batches → (N, channels)
            4. Per-neuron Pearson correlation with spurious_labels
        """
        layer_activations: Dict[str, List[torch.Tensor]] = {
            name: [] for name in self.layer_names
        }
        
        self.model.eval()
        with torch.no_grad():
            for batch_x, _, _ in dataloader:  # (x, label, spurious_label)
                batch_x = batch_x.cuda()
                _ = self.model(batch_x)  # Triggers hooks
                
                for layer_name in self.layer_names:
                    act = self.activations[layer_name]
                    # Spatial pooling: (B, C, H, W) → (B, C)
                    pooled = act.mean(dim=(2, 3))
                    layer_activations[layer_name].append(pooled.cpu())
        
        # Compute per-neuron correlations
        layer_rho_j: Dict[str, np.ndarray] = {}
        for layer_name, acts in layer_activations.items():
            # Concatenate all batches: (N, C)
            acts_array = torch.cat(acts, dim=0).numpy()  # (10000, num_channels)
            
            # Per-neuron correlation with spurious labels
            rho_j = np.array([
                pearsonr(acts_array[:, i], spurious_labels)[0]
                for i in range(acts_array.shape[1])
            ])
            layer_rho_j[layer_name] = rho_j
        
        return layer_rho_j
    
    def test_layer_consistency(
        self,
        layer_rho_j: Dict[str, np.ndarray]
    ) -> Tuple[float, float, Dict[str, float]]:
        """
        Test if early layers have higher spurious correlation than late layers.
        
        Args:
            layer_rho_j: Per-layer correlation arrays
        
        Returns:
            t_stat: t-statistic (positive if early > late)
            p_value: One-sided p-value
            layer_means: Mean correlation per layer (for reporting)
        
        Algorithm:
            1. Group: Early = concat(conv1, layer1), Late = concat(layer3, layer4)
            2. One-sided t-test (alternative='greater')
            3. Null hypothesis: mean(early) ≤ mean(late)
        """
        # Group correlations
        early = np.concatenate([
            layer_rho_j['conv1'],
            layer_rho_j['layer1']
        ])
        late = np.concatenate([
            layer_rho_j['layer3'],
            layer_rho_j['layer4']
        ])
        
        # Statistical test
        t_stat, p_value = ttest_ind(early, late, alternative='greater')
        
        # Per-layer means for reporting
        layer_means = {
            name: np.mean(rho) for name, rho in layer_rho_j.items()
        }
        
        return t_stat, p_value, layer_means
```

---

## External Dependencies API (h-e1)

### Model Checkpoint Loading

```python
def load_h_e1_model(checkpoint_path: str) -> torch.nn.Module:
    """
    Load ResNet-18 from h-e1 checkpoint.
    
    Args:
        checkpoint_path: Path to h-e1/checkpoints/baseline_seed0.pt
    
    Returns:
        model: ResNet-18 in eval mode
    
    Verified Signature (from h-e1 code):
        - Checkpoint key: 'model_state_dict' (not 'state_dict')
        - Model: torchvision.models.resnet18(pretrained=False, num_classes=10)
    """
    import torchvision.models as models
    
    model = models.resnet18(pretrained=False, num_classes=10)
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model
```

### Spurious Label Extraction

```python
def get_spurious_labels(dataset: CMNISTDataset) -> np.ndarray:
    """
    Extract spurious feature labels (color) from CMNIST dataset.
    
    Args:
        dataset: CMNIST test set
    
    Returns:
        spurious_labels: (N,) array of color indices (0-9)
    
    Note: h-e1 did not save spurious labels in checkpoint.
          Must regenerate via same color corruption transform.
    """
    spurious_labels = []
    for i in range(len(dataset)):
        _, _, color = dataset[i]  # (image, label, color)
        spurious_labels.append(color)
    return np.array(spurious_labels)
```

---

## Visualization APIs

### 1. Bar Chart (Mean Correlation per Layer)

```python
def plot_layer_means(
    layer_means: Dict[str, float],
    layer_rho_j: Dict[str, np.ndarray],
    save_path: str
) -> None:
    """
    Bar chart with 95% confidence intervals.
    
    Args:
        layer_means: Mean correlation per layer
        layer_rho_j: Full correlation arrays (for CI calculation)
        save_path: Output PNG path
    
    Figure Specs:
        - X-axis: 5 layers (conv1, layer1, layer2, layer3, layer4)
        - Y-axis: Mean Pearson ρ_j
        - Error bars: 95% CI (1.96 * SEM)
        - Expected pattern: Monotonic decrease
    """
    import matplotlib.pyplot as plt
    from scipy import stats
    
    layers = ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']
    means = [layer_means[l] for l in layers]
    
    # 95% CI
    cis = [1.96 * stats.sem(layer_rho_j[l]) for l in layers]
    
    plt.figure(figsize=(10, 6))
    plt.bar(layers, means, yerr=cis, capsize=5)
    plt.ylabel('Mean Pearson Correlation (ρ_j)')
    plt.xlabel('Layer')
    plt.title('Layer-wise Spurious Correlation (Early > Late)')
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

### 2. Heatmap (Per-Neuron Correlations)

```python
def plot_heatmap(
    layer_rho_j: Dict[str, np.ndarray],
    save_path: str,
    max_neurons_per_layer: int = 100
) -> None:
    """
    Heatmap (layers × neurons) showing individual ρ_j values.
    
    Args:
        layer_rho_j: Per-layer correlation arrays
        save_path: Output PNG path
        max_neurons_per_layer: Subsample if >100 neurons
    
    Figure Specs:
        - Rows: Layers
        - Columns: Neurons (subsampled if needed)
        - Colormap: RdBu_r (red=positive, blue=negative)
        - Range: [-1, +1]
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Subsample neurons if needed
    data = []
    for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
        rho = layer_rho_j[layer_name]
        if len(rho) > max_neurons_per_layer:
            rho = rho[:max_neurons_per_layer]
        data.append(rho)
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(
        data,
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        yticklabels=['conv1', 'layer1', 'layer2', 'layer3', 'layer4'],
        cbar_kws={'label': 'Pearson ρ_j'}
    )
    plt.xlabel('Neuron Index')
    plt.ylabel('Layer')
    plt.title('Neuron-Spurious Correlation (Per Layer)')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

### 3. CDF Comparison (Early vs Late)

```python
def plot_cdf(
    layer_rho_j: Dict[str, np.ndarray],
    save_path: str
) -> None:
    """
    Cumulative distribution of ρ_j for early vs late layer groups.
    
    Args:
        layer_rho_j: Per-layer correlation arrays
        save_path: Output PNG path
    
    Figure Specs:
        - Two curves: Early (conv1+layer1), Late (layer3+layer4)
        - X-axis: Correlation value
        - Y-axis: Cumulative probability
        - Expected: Early curve shifted right (higher values)
    """
    import matplotlib.pyplot as plt
    
    early = np.concatenate([layer_rho_j['conv1'], layer_rho_j['layer1']])
    late = np.concatenate([layer_rho_j['layer3'], layer_rho_j['layer4']])
    
    plt.figure(figsize=(10, 6))
    plt.hist(early, bins=50, cumulative=True, density=True, 
             alpha=0.6, label='Early (conv1, layer1)', histtype='step', linewidth=2)
    plt.hist(late, bins=50, cumulative=True, density=True,
             alpha=0.6, label='Late (layer3, layer4)', histtype='step', linewidth=2)
    plt.xlabel('Pearson Correlation (ρ_j)')
    plt.ylabel('Cumulative Probability')
    plt.title('CDF: Early vs Late Layer Correlations')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

---

## Report Generation API

```python
def generate_validation_report(
    t_stat: float,
    p_value: float,
    layer_means: Dict[str, float],
    layer_rho_j: Dict[str, np.ndarray],
    output_path: str
) -> None:
    """
    Generate 04_validation.md with gate verdict and statistics.
    
    Args:
        t_stat: t-test statistic
        p_value: One-sided p-value
        layer_means: Mean correlation per layer
        layer_rho_j: Full correlation arrays (for std/CI)
        output_path: Path to 04_validation.md
    
    Gate Logic:
        PASS if: p_value < 0.05 AND mean(early) > mean(late)
        FAIL otherwise
    
    Sections:
        1. Executive Summary (gate verdict)
        2. Statistical Test Results (t-stat, p-value, effect size)
        3. Per-Layer Statistics (table with mean/std/CI)
        4. Visualizations (references to 3 figures)
        5. Interpretation (mechanism supported or not)
    """
    from scipy import stats as scipy_stats
    
    # Gate verdict
    early_mean = np.mean(np.concatenate([
        layer_rho_j['conv1'], layer_rho_j['layer1']
    ]))
    late_mean = np.mean(np.concatenate([
        layer_rho_j['layer3'], layer_rho_j['layer4']
    ]))
    gate_pass = (p_value < 0.05) and (early_mean > late_mean)
    
    # Cohen's d effect size
    early_std = np.std(np.concatenate([
        layer_rho_j['conv1'], layer_rho_j['layer1']
    ]))
    late_std = np.std(np.concatenate([
        layer_rho_j['layer3'], layer_rho_j['layer4']
    ]))
    pooled_std = np.sqrt((early_std**2 + late_std**2) / 2)
    cohens_d = (early_mean - late_mean) / pooled_std
    
    # Build markdown content
    report = f"""# Validation Report: h-m1

## Gate Verdict: {'✅ PASS' if gate_pass else '❌ FAIL'}

**Test:** Layer-wise neuron consistency (early > late spurious correlation)  
**Result:** p = {p_value:.4f}, t = {t_stat:.2f}, d = {cohens_d:.2f}  
**Conclusion:** {'Mechanism hypothesis SUPPORTED' if gate_pass else 'Mechanism hypothesis NOT SUPPORTED'}

## Statistical Test Results

| Metric | Value |
|--------|-------|
| Early Mean (ρ) | {early_mean:.3f} |
| Late Mean (ρ) | {late_mean:.3f} |
| Difference | {early_mean - late_mean:.3f} |
| t-statistic | {t_stat:.2f} |
| p-value (one-sided) | {p_value:.4f} |
| Cohen's d | {cohens_d:.2f} |

## Per-Layer Statistics

| Layer | Mean(ρ_j) | Std(ρ_j) | 95% CI |
|-------|----------|----------|--------|
"""
    for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
        mean = layer_means[layer_name]
        std = np.std(layer_rho_j[layer_name])
        ci = 1.96 * scipy_stats.sem(layer_rho_j[layer_name])
        report += f"| {layer_name} | {mean:.3f} | {std:.3f} | ±{ci:.3f} |\n"
    
    report += f"""
## Visualizations

1. **Bar Chart:** `figures/layer_correlation_means.png` - Mean ρ_j per layer with 95% CI
2. **Heatmap:** `figures/neuron_correlation_heatmap.png` - Per-neuron correlations
3. **CDF:** `figures/correlation_cdf.png` - Early vs late distribution comparison

## Interpretation

{'Early layers (conv1, layer1) show significantly higher spurious correlation than late layers (layer3, layer4), supporting the feature complexity hypothesis. Simpler spurious features (color) are learned earlier in the network hierarchy.' if gate_pass else 'No significant difference found between early and late layers. Alternative mechanisms should be investigated.'}
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
```

---

## Subtask Breakdown (4 subtasks)

### Subtask 3.1: Hook Registration Logic
- Implement `_register_hooks()` with closure pattern
- Test: Verify activations dict populated after forward pass

### Subtask 3.2: Correlation Computation
- Implement `compute_layer_correlations()` with spatial pooling
- Test: Verify output shape (dict of 1D arrays)

### Subtask 6.1: Main Orchestration
- Implement `main()` in analyze_layers.py
- Integrate: Model loading → Analyzer → Visualization → Report

### Subtask 4.1: T-Test Implementation
- Implement `test_layer_consistency()` with scipy.stats
- Test: Verify one-sided alternative='greater'

---

**Version:** 1.0  
**Status:** Ready for Configuration Design
