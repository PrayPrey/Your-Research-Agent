# Logic Design: H-M4 Geometry-Phenotype Coupling

**Project:** H-M4 Implementation
**Date:** 2026-04-24
**Author:** Logic Agent
**Hypothesis Type:** MECHANISM (FULL tier)

---

## Codebase Analysis (Serena)

**Base Implementation Review (h-m3):**

Verified actual API signatures from h-m3/code/:

```python
# From h-m3/code/metrics/alignment.py
def compute_alignment_metric(
    model: nn.Module,
    dataloader: DataLoader,
    outlier_subspace: np.ndarray,
    group_id: int,
    device: str = "cuda"
) -> float:
    """Compute A(w) = ||P_S_out g_minority||² / ||g_minority||²"""
    
# From h-m3/code/data/minority_gradients.py
def extract_group_gradients(
    model: nn.Module,
    dataloader: DataLoader,
    group_id: int,
    device: str = "cuda"
) -> torch.Tensor:
    """Extract gradients for specific group"""
    
# From h-m3/code/data/waterbirds.py
def get_waterbirds_dataloader(
    split: str,
    batch_size: int = 128,
    shuffle: bool = False,
    num_workers: int = 4
) -> DataLoader:
    """Load Waterbirds dataset with group labels"""
```

**All parameter names and types verified from actual implementation.**

---

## Applied Patterns

**Applied:** Dependency Injection Pattern (Archon KB)
- Pass model, dataloader as dependencies to metrics functions
- Enables testing with mock models

**Applied:** Builder Pattern (Archon KB)
- PathSamplerBuilder constructs sampler with configuration
- Fluent interface for checkpoint loading

---

## API Signatures

### Module 1: Path Sampling

#### Class: PathSampler (Abstract)

```python
from abc import ABC, abstractmethod
from typing import List, Dict
import torch.nn as nn

class PathSampler(ABC):
    """Abstract base for checkpoint sampling strategies"""
    
    def __init__(
        self,
        endpoint_1: Dict[str, torch.Tensor],
        endpoint_2: Dict[str, torch.Tensor],
        num_samples: int = 20
    ):
        """
        Args:
            endpoint_1: First endpoint state_dict (ERM)
            endpoint_2: Second endpoint state_dict (DRO)
            num_samples: Number of checkpoints to sample
        """
        self.endpoint_1 = endpoint_1
        self.endpoint_2 = endpoint_2
        self.num_samples = num_samples
    
    @abstractmethod
    def sample(self) -> List[Dict[str, torch.Tensor]]:
        """
        Sample checkpoints along path.
        
        Returns:
            List of M state_dicts (checkpoints)
        """
        pass
```

**Tensor Shapes:**
- `endpoint_1`, `endpoint_2`: Dict mapping layer names → parameter tensors
  - e.g., `"fc.weight"` → `(2, 2048)` for ResNet-50 final layer
- `sample()` returns: List[state_dict] of length M=20

#### Class: FGESampler (Concrete)

```python
class FGESampler(PathSampler):
    """Fast Geometric Ensembling path sampler (linear interpolation)"""
    
    def sample(self) -> List[Dict[str, torch.Tensor]]:
        """
        Linear interpolation: θ(α) = (1-α)θ₁ + αθ₂
        
        Algorithm:
        1. For α in linspace(0, 1, M):
        2.   For each parameter key:
        3.     Interpolate: θ[key] = (1-α)*θ₁[key] + α*θ₂[key]
        4.   Append interpolated state_dict to checkpoints
        
        Returns:
            List[Dict] of M=20 checkpoints
        """
        checkpoints = []
        alphas = np.linspace(0, 1, self.num_samples)
        
        for alpha in alphas:
            checkpoint = {}
            for key in self.endpoint_1.keys():
                checkpoint[key] = (
                    (1 - alpha) * self.endpoint_1[key] + 
                    alpha * self.endpoint_2[key]
                )
            checkpoints.append(checkpoint)
        
        return checkpoints
```

**Complexity:** O(M × P) where M=20 samples, P=parameter count (~25M for ResNet-50)

#### Class: LinearSampler (Concrete)

```python
class LinearSampler(PathSampler):
    """Linear interpolation baseline (identical to FGE for validation)"""
    
    def sample(self) -> List[Dict[str, torch.Tensor]]:
        """Same as FGESampler - validates FGE is not over-engineered"""
        # Identical implementation
        pass
```

#### Function: load_checkpoint

```python
def load_checkpoint(
    checkpoint_path: str,
    device: str = "cuda"
) -> Dict[str, torch.Tensor]:
    """
    Load checkpoint from disk.
    
    Args:
        checkpoint_path: Path to .pt file
        device: Device to load tensors
        
    Returns:
        state_dict: Dict mapping layer names → tensors
        
    Raises:
        FileNotFoundError: If checkpoint doesn't exist
        RuntimeError: If checkpoint is corrupted
    """
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Handle different checkpoint formats
    if "state_dict" in checkpoint:
        return checkpoint["state_dict"]
    return checkpoint
```

---

### Module 2: Metrics

#### Class: WGAEvaluator

```python
class WGAEvaluator:
    """Worst-group accuracy evaluator"""
    
    def __init__(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        num_groups: int = 4,
        device: str = "cuda"
    ):
        """
        Args:
            model: ResNet-50 model
            dataloader: Waterbirds test loader with group labels
            num_groups: Number of groups (4 for Waterbirds)
            device: Computation device
        """
        self.model = model
        self.dataloader = dataloader
        self.num_groups = num_groups
        self.device = device
    
    def evaluate(self) -> float:
        """
        Compute WGA = min(group_accuracies).
        
        Algorithm:
        1. For each group g in [0, 1, 2, 3]:
        2.   Compute accuracy_g on samples where group_label == g
        3. Return min(accuracy_0, accuracy_1, accuracy_2, accuracy_3)
        
        Returns:
            wga: Float in [0, 1]
        """
        group_accs = self._compute_group_accuracies()
        return min(group_accs)
    
    def _compute_group_accuracies(self) -> List[float]:
        """
        Compute per-group accuracy.
        
        Returns:
            List[float] of length num_groups (4)
        """
        group_correct = [0] * self.num_groups
        group_total = [0] * self.num_groups
        
        self.model.eval()
        with torch.no_grad():
            for images, labels, groups in self.dataloader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                preds = outputs.argmax(dim=1)
                
                for g in range(self.num_groups):
                    mask = (groups == g)
                    group_correct[g] += (preds[mask] == labels[mask]).sum().item()
                    group_total[g] += mask.sum().item()
        
        return [
            group_correct[g] / group_total[g] 
            for g in range(self.num_groups)
        ]
```

**Tensor Shapes:**
- `images`: (B, 3, 224, 224)
- `labels`: (B,)
- `groups`: (B,) - group IDs in [0, 1, 2, 3]
- `outputs`: (B, 2) - logits for 2 classes
- `preds`: (B,) - predicted class indices

#### Function: compute_alignment_wrapper

```python
def compute_alignment_wrapper(
    model: nn.Module,
    dataloader: DataLoader,
    device: str = "cuda"
) -> float:
    """
    Wrapper for h-m2 alignment computation.
    
    Algorithm:
    1. Compute Hessian eigenvalues (reuse h-m1)
    2. Detect outlier subspace via Marchenko-Pastur (reuse h-m1)
    3. Extract minority gradients (reuse h-m2)
    4. Compute alignment A(w) (reuse h-m2)
    
    Args:
        model: ResNet-50 model
        dataloader: Waterbirds val loader
        device: Computation device
        
    Returns:
        alignment: Float in [0, 1]
    """
    # Import from h-m1
    from curvature.marchenko_pastur import (
        compute_hessian_eigenvalues,
        detect_outlier_eigenvalues
    )
    # Import from h-m2
    from metrics.alignment import compute_alignment_metric
    from data.minority_gradients import extract_group_gradients
    
    # Step 1: Compute Hessian eigenvalues
    eigenvalues, eigenvectors = compute_hessian_eigenvalues(
        model, dataloader, device
    )
    
    # Step 2: Detect outlier subspace
    outlier_indices = detect_outlier_eigenvalues(eigenvalues)
    outlier_subspace = eigenvectors[:, outlier_indices]
    
    # Step 3: Compute alignment for minority groups (groups 1 and 3)
    alignments = []
    for group_id in [1, 3]:  # Minority groups
        alignment = compute_alignment_metric(
            model, dataloader, outlier_subspace, group_id, device
        )
        alignments.append(alignment)
    
    # Step 4: Average minority alignments
    return np.mean(alignments)
```

**Complexity:** O(P²) for Hessian computation, P=parameter count

---

### Module 3: Analysis

#### Function: compute_spearman_correlation

```python
from scipy.stats import spearmanr
from typing import Tuple

def compute_spearman_correlation(
    alignment_values: np.ndarray,
    wga_values: np.ndarray
) -> Tuple[float, float]:
    """
    Compute Spearman correlation between A(w) and WGA.
    
    Args:
        alignment_values: Array of A(w) values, shape (M,)
        wga_values: Array of WGA values, shape (M,)
        
    Returns:
        rho: Spearman correlation coefficient
        p_value: Statistical significance (H0: rho = 0)
        
    Raises:
        ValueError: If arrays have different lengths
    """
    if len(alignment_values) != len(wga_values):
        raise ValueError("Arrays must have same length")
    
    rho, p_value = spearmanr(alignment_values, wga_values)
    return rho, p_value
```

**Expected Output:**
- `rho`: Float in [-1, 1], expected < -0.6
- `p_value`: Float in [0, 1], expected < 0.01

#### Class: ResultsAggregator

```python
@dataclass
class CouplingResults:
    """Results container for coupling experiment"""
    fge_rho: float
    fge_p_value: float
    linear_rho: float
    linear_p_value: float
    alignment_values_fge: np.ndarray  # Shape: (M,)
    wga_values_fge: np.ndarray        # Shape: (M,)
    alignment_values_linear: np.ndarray  # Shape: (M,)
    wga_values_linear: np.ndarray        # Shape: (M,)

class ResultsAggregator:
    """Aggregate FGE and linear results"""
    
    def aggregate(
        self,
        fge_results: Dict,
        linear_results: Dict
    ) -> CouplingResults:
        """
        Combine FGE and linear path results.
        
        Args:
            fge_results: Dict with keys ["alignments", "wgas", "rho", "p_value"]
            linear_results: Dict with same structure
            
        Returns:
            CouplingResults dataclass
        """
        return CouplingResults(
            fge_rho=fge_results["rho"],
            fge_p_value=fge_results["p_value"],
            linear_rho=linear_results["rho"],
            linear_p_value=linear_results["p_value"],
            alignment_values_fge=fge_results["alignments"],
            wga_values_fge=fge_results["wgas"],
            alignment_values_linear=linear_results["alignments"],
            wga_values_linear=linear_results["wgas"]
        )
```

---

### Module 4: Visualization

#### Function: plot_coupling_scatter

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_coupling_scatter(
    alignment_values: np.ndarray,
    wga_values: np.ndarray,
    rho: float,
    p_value: float,
    save_path: str
) -> None:
    """
    Generate scatter plot: A(w) vs WGA with regression.
    
    Args:
        alignment_values: Shape (M,)
        wga_values: Shape (M,)
        rho: Spearman correlation
        p_value: Statistical significance
        save_path: Output path for figure
        
    Algorithm:
    1. Create scatter plot (alignment vs wga)
    2. Add linear regression line
    3. Annotate with ρ and p-value
    4. Save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Scatter plot with color gradient by position along path
    colors = np.linspace(0, 1, len(alignment_values))
    scatter = ax.scatter(
        alignment_values, wga_values, 
        c=colors, cmap='viridis', s=100, alpha=0.6
    )
    
    # Regression line
    z = np.polyfit(alignment_values, wga_values, 1)
    p = np.poly1d(z)
    ax.plot(
        alignment_values, p(alignment_values), 
        "r--", alpha=0.8, label='Linear fit'
    )
    
    # Annotations
    ax.text(
        0.05, 0.95, 
        f'ρ = {rho:.3f}\np = {p_value:.4f}',
        transform=ax.transAxes, 
        fontsize=12, 
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    ax.set_xlabel('Curvature Alignment A(w)', fontsize=12)
    ax.set_ylabel('Worst-Group Accuracy (WGA)', fontsize=12)
    ax.set_title('Geometry-Phenotype Coupling', fontsize=14)
    ax.legend()
    plt.colorbar(scatter, label='Position along path (0=ERM, 1=DRO)')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
```

#### Function: plot_trajectory

```python
def plot_trajectory(
    alphas: np.ndarray,
    alignment_values: np.ndarray,
    wga_values: np.ndarray,
    save_path: str
) -> None:
    """
    Generate trajectory plot: α vs A(w) and WGA (dual axes).
    
    Args:
        alphas: Interpolation values, shape (M,)
        alignment_values: A(w) values, shape (M,)
        wga_values: WGA values, shape (M,)
        save_path: Output path
        
    Algorithm:
    1. Create figure with dual y-axes
    2. Plot A(w) vs α (left axis, blue)
    3. Plot WGA vs α (right axis, orange)
    4. Highlight monotonic coupling pattern
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Left axis: A(w)
    color = 'tab:blue'
    ax1.set_xlabel('Interpolation α (0=ERM, 1=DRO)', fontsize=12)
    ax1.set_ylabel('Curvature Alignment A(w)', color=color, fontsize=12)
    ax1.plot(alphas, alignment_values, color=color, marker='o', label='A(w)')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Right axis: WGA
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Worst-Group Accuracy (WGA)', color=color, fontsize=12)
    ax2.plot(alphas, wga_values, color=color, marker='s', label='WGA')
    ax2.tick_params(axis='y', labelcolor=color)
    
    ax1.set_title('Metric Evolution Along Mode-Connected Path', fontsize=14)
    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
```

---

### Module 5: Experiment Orchestration

#### Class: CouplingExperiment

```python
@dataclass
class ExperimentConfig:
    """Experiment configuration"""
    erm_checkpoint_path: str
    dro_checkpoint_path: str
    num_samples: int = 20
    batch_size: int = 128
    device: str = "cuda"
    output_dir: str = "h-m4/results/"

class CouplingExperiment:
    """Main experiment orchestrator"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None
        self.dataloader = None
    
    def run(self) -> CouplingResults:
        """
        Execute full coupling experiment pipeline.
        
        Algorithm:
        1. Load ERM and DRO checkpoints
        2. Sample FGE path (M=20 checkpoints)
        3. For each checkpoint:
        4.   Load into model
        5.   Compute A(w)
        6.   Compute WGA
        7. Compute Spearman correlation (FGE)
        8. Repeat steps 2-7 for linear path
        9. Aggregate results
        10. Generate visualizations
        11. Save validation report
        
        Returns:
            CouplingResults with all metrics
        """
        # Step 1: Load endpoints
        erm_checkpoint = load_checkpoint(self.config.erm_checkpoint_path)
        dro_checkpoint = load_checkpoint(self.config.dro_checkpoint_path)
        
        # Step 2-7: FGE path
        fge_results = self._evaluate_path(
            FGESampler(erm_checkpoint, dro_checkpoint, self.config.num_samples)
        )
        
        # Step 8: Linear path
        linear_results = self._evaluate_path(
            LinearSampler(erm_checkpoint, dro_checkpoint, self.config.num_samples)
        )
        
        # Step 9: Aggregate
        aggregator = ResultsAggregator()
        results = aggregator.aggregate(fge_results, linear_results)
        
        # Step 10: Visualize
        self._generate_visualizations(results)
        
        # Step 11: Report
        self._save_validation_report(results)
        
        return results
    
    def _evaluate_path(self, sampler: PathSampler) -> Dict:
        """
        Evaluate A(w) and WGA for all checkpoints along path.
        
        Returns:
            Dict with ["alignments", "wgas", "rho", "p_value"]
        """
        checkpoints = sampler.sample()
        
        alignments = []
        wgas = []
        
        for checkpoint in checkpoints:
            # Load checkpoint
            self.model.load_state_dict(checkpoint)
            
            # Compute A(w)
            alignment = compute_alignment_wrapper(
                self.model, self.dataloader, self.config.device
            )
            alignments.append(alignment)
            
            # Compute WGA
            wga_evaluator = WGAEvaluator(
                self.model, self.dataloader, device=self.config.device
            )
            wga = wga_evaluator.evaluate()
            wgas.append(wga)
        
        # Compute correlation
        rho, p_value = compute_spearman_correlation(
            np.array(alignments), np.array(wgas)
        )
        
        return {
            "alignments": np.array(alignments),
            "wgas": np.array(wgas),
            "rho": rho,
            "p_value": p_value
        }
```

---

## External Dependencies API

**From h-m1 (curvature/):**
```python
def compute_hessian_eigenvalues(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Tuple[np.ndarray, np.ndarray]:
    """Returns: (eigenvalues, eigenvectors)"""

def detect_outlier_eigenvalues(
    eigenvalues: np.ndarray
) -> np.ndarray:
    """Returns: outlier_indices (array of int)"""
```

**From h-m2 (metrics/):**
```python
def compute_alignment_metric(
    model: nn.Module,
    dataloader: DataLoader,
    outlier_subspace: np.ndarray,
    group_id: int,
    device: str
) -> float:
    """Returns: alignment A(w) in [0, 1]"""
```

**From h-m3 (data/):**
```python
def get_waterbirds_dataloader(
    split: str,
    batch_size: int,
    shuffle: bool,
    num_workers: int
) -> DataLoader:
    """Returns: DataLoader yielding (images, labels, groups)"""
```

---

## Subtask Breakdown

**Epic E-1 Subtasks (4):**
- L-1-1: Implement PathSampler abstract class
- L-1-2: Implement FGESampler.sample()
- L-1-3: Implement LinearSampler.sample()
- L-1-4: Implement load_checkpoint() with validation

**Epic E-2 Subtasks (3):**
- L-2-1: Implement WGAEvaluator.evaluate()
- L-2-2: Implement _compute_group_accuracies()
- L-2-3: Unit tests for WGA computation

**Epic E-3 Subtasks (2):**
- L-3-1: Implement compute_alignment_wrapper()
- L-3-2: Integration test with h-m1/h-m2 code

**Epic E-4 Subtasks (3):**
- L-4-1: Implement compute_spearman_correlation()
- L-4-2: Implement ResultsAggregator
- L-4-3: Statistical significance tests

**Epic E-5 Subtasks (4):**
- L-5-1: Implement plot_coupling_scatter()
- L-5-2: Implement plot_trajectory()
- L-5-3: Implement plot_comparison() (FGE vs linear)
- L-5-4: Implement plot_group_accuracy()

**Epic E-6 Subtasks (3):**
- L-6-1: Implement CouplingExperiment.run()
- L-6-2: Implement _evaluate_path()
- L-6-3: Implement ExperimentConfig dataclass

**Epic E-7 Subtasks (2):**
- L-7-1: Implement _save_validation_report()
- L-7-2: Gate evaluation (SHOULD_WORK criteria)

**Total Subtasks:** 21

---

*Logic Design v1.0 | Generated for Phase 3 Implementation Planning*
*Applied patterns: Dependency Injection, Builder*
