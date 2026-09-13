# Architecture: H-M2
# Feature Complexity Measurement — Spurious vs. Core Feature Analysis

**Hypothesis ID:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-M1)
**Date:** 2026-05-04

Applied: DL incremental extension pattern (dataset characterization pipeline on existing ResNet-50 backbone)
Applied: FFT spatial frequency complexity metric pattern (Geirhos et al. 2019)
Applied: Linear separability probe learning curve pattern (Shah et al. 2020)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Architecture reference used (H-M1 code not yet generated — Phase 4 pending)
**Analyzed Path**: `h-m1/code/` (not yet created; using 03_architecture.md as reference)
**Findings**: H-M1 flat layout with `data/waterbirds.py`, `config.py`, `train.py`. H-M2 is inference-only — no training loop needed. ResNet-50 feature extraction pattern reused from H-M1 `GradientAlignmentAnalyzer.extract_features()`. WaterbirdsDataset provides `spurious_label` per batch. H-M2 adds patch extraction, FFT, intra-class variance, and linear separability probe modules — no gradient instrumentation required.

---

## File Organization

```
h-m2/code/
  config.py                        # ExperimentConfig (dataset paths, metric params)
  run_experiment.py                # Main orchestrator (entry point)
  data_pipeline/
    __init__.py
    waterbirds_loader.py           # WaterbirdsDataset wrapper + patch extractor
    celeba_loader.py               # CelebA loader + patch extractor
    patch_extractor.py             # Mask-based and quadrant-based patch extraction
  feature_extractor/
    __init__.py
    resnet_extractor.py            # Frozen ResNet-50, layer-4 (2048-dim) features
  complexity_metrics/
    __init__.py
    fft_metric.py                  # Metric 1: FFT mean spatial frequency
    variance_metric.py             # Metric 2: Intra-class feature variance
    separability_metric.py         # Metric 3: Linear separability learning curve
  analysis/
    __init__.py
    statistical_tests.py           # t-test, Bonferroni correction, gate evaluation
    mechanism_verifier.py          # verify_mechanism_activated()
  visualization/
    __init__.py
    figures.py                     # All 5 figure generation functions
  configs/
    experiment.yaml                # Single fixed config
  results/                         # results_h_m2.json (auto-created)
  figures/                         # complexity_comparison.png etc. (auto-created)
```

---

## External Dependencies (Base Hypothesis)

H-M1 code does not yet exist (generated in Phase 4). H-M2 re-implements the ResNet-50 backbone using the same pattern defined in H-M1 architecture.

| Module | Pattern Source | Notes |
|--------|---------------|-------|
| ResNet-50 backbone | H-M1 `GradientAlignmentAnalyzer.extract_features()` | Frozen backbone, layer-4, 2048-dim; implemented independently in `resnet_extractor.py` |
| WaterbirdsDataset | H-M1 `data/waterbirds.py` | Re-implemented in `waterbirds_loader.py`; adds mask-based patch extraction |

**Verified from**: `h-m1/03_architecture.md` (code not yet generated)

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DataConfig:
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    celeba_root: str = ".data_cache/datasets/celeba"
    patch_size: int = 64
    batch_size: int = 256
    num_workers: int = 4
    celeba_samples_per_group: int = 5000
    use_segmentation_masks: bool = True  # fallback to quadrant if False

@dataclass
class MetricConfig:
    n_samples_list: List[int] = field(default_factory=lambda: [50, 100, 200, 500, 1000, 2000])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    alpha: float = 0.05
    min_patches_per_class: int = 100
    logistic_c: float = 1.0
    logistic_max_iter: int = 1000

@dataclass
class ExperimentConfig:
    data: DataConfig
    metric: MetricConfig
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    device: str = "cuda:0"

def load_config(config_path: str) -> ExperimentConfig: ...
```

---

### PatchExtractor (`data_pipeline/patch_extractor.py`)

**Dependencies**: config.DataConfig

```python
import numpy as np
from PIL import Image
from typing import Tuple, Optional

class PatchExtractor:
    def __init__(self, patch_size: int = 64): ...

    def extract_from_mask(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns (spurious_patch, core_patch) from binary segmentation mask.
        spurious = background region; core = foreground (bird) region.
        Both resized to (patch_size, patch_size, 3) uint8.
        Falls back to quadrant if mask is invalid.
        """
        ...

    def extract_quadrant(
        self,
        image: np.ndarray,
        spurious_top_frac: float = 0.4,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fallback: spurious = top spurious_top_frac; core = center crop.
        Returns (spurious_patch, core_patch) uint8.
        """
        ...

    def extract_celeba_patches(
        self,
        image: np.ndarray,
        hair_top_frac: float = 0.25,
        face_crop_size: int = 112,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        CelebA: spurious = top hair_top_frac; core = center face crop.
        Returns (spurious_patch, core_patch) uint8 resized to patch_size.
        """
        ...

    def to_imagenet_tensor(self, patch_uint8: np.ndarray) -> "torch.Tensor":
        """Convert uint8 patch to ImageNet-normalized tensor for feature extraction."""
        ...
```

---

### WaterbirdsLoader (`data_pipeline/waterbirds_loader.py`)

**Dependencies**: patch_extractor.PatchExtractor, config.DataConfig

```python
import numpy as np
from typing import Dict, Tuple
from torch.utils.data import Dataset, DataLoader

class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str = "train", transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict:
        """Returns dict: image, core_label, spurious_label, mask_path, img_path."""
        ...

def extract_waterbirds_patches(
    root: str,
    extractor: "PatchExtractor",
    split: str = "train",
    use_masks: bool = True,
) -> Dict[str, np.ndarray]:
    """
    Returns {
        spurious_patches: (N, H, W, 3) uint8,
        core_patches: (N, H, W, 3) uint8,
        spurious_labels: (N,),
        core_labels: (N,),
    }
    Logs fallback if masks unavailable.
    """
    ...

def get_waterbirds_feature_loader(
    root: str,
    split: str = "train",
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    """DataLoader for ImageNet-normalized tensors (for ResNet-50 feature extraction)."""
    ...
```

---

### CelebALoader (`data_pipeline/celeba_loader.py`)

**Dependencies**: patch_extractor.PatchExtractor, config.DataConfig

```python
import numpy as np
from typing import Dict
from torch.utils.data import DataLoader

def extract_celeba_patches(
    root: str,
    extractor: "PatchExtractor",
    samples_per_group: int = 5000,
    split: str = "train",
) -> Dict[str, np.ndarray]:
    """
    Stratified sample: 4 groups (blond×gender) × samples_per_group.
    Returns {spurious_patches, core_patches, spurious_labels, core_labels}.
    Spurious attr: hair_color (index 9); Core attr: gender (index 20).
    """
    ...

def get_celeba_feature_loader(
    root: str,
    samples_per_group: int = 5000,
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    """DataLoader for ImageNet-normalized CelebA tensors."""
    ...
```

---

### ResNetExtractor (`feature_extractor/resnet_extractor.py`)

**Dependencies**: config.DataConfig

```python
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader
from typing import Tuple

class ResNetExtractor:
    def __init__(self, device: str): ...

    def build_model(self) -> nn.Module:
        """torchvision.models.resnet50(pretrained=True), fc=Identity(), frozen, eval."""
        ...

    def extract_features(
        self,
        loader: DataLoader,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns (features, core_labels, spurious_labels).
        features shape: (N, 2048). No gradient. Batch size 256.
        """
        ...

    def extract_split_features(
        self,
        spurious_loader: DataLoader,
        core_loader: DataLoader,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns (spurious_feats, core_feats) each (N, 2048).
        Convenience wrapper for patch-based loaders.
        """
        ...
```

---

### FFTMetric (`complexity_metrics/fft_metric.py`)

**Dependencies**: None (numpy only)

```python
import numpy as np
from typing import Tuple, List
from scipy import stats

def compute_mean_spatial_frequency(patch: np.ndarray) -> float:
    """
    patch: (H, W, C) or (H, W) uint8.
    Returns weighted mean frequency of 2D FFT power spectrum.
    Formula: sum(|F|^2 * freq_grid) / sum(|F|^2)
    """
    ...

def compute_fft_metric(
    spurious_patches: np.ndarray,
    core_patches: np.ndarray,
) -> dict:
    """
    Returns {
        spurious_mean_freq, core_mean_freq,
        spurious_freqs: List[float], core_freqs: List[float],
        t_stat, p_value, direction_correct
    }
    """
    ...
```

---

### VarianceMetric (`complexity_metrics/variance_metric.py`)

**Dependencies**: None (numpy + scipy)

```python
import numpy as np
from scipy import stats
from typing import Tuple

def compute_intraclass_variance(features: np.ndarray) -> float:
    """Returns trace(Cov(features.T)). features: (N, 2048)."""
    ...

def compute_variance_metric(
    spurious_feats: np.ndarray,
    core_feats: np.ndarray,
) -> dict:
    """
    Per-feature variance t-test (ttest_ind on per-feature std arrays).
    Returns {
        var_spurious, var_core,
        per_feature_var_spurious: (2048,), per_feature_var_core: (2048,),
        t_stat, p_value, direction_correct
    }
    """
    ...
```

---

### SeparabilityMetric (`complexity_metrics/separability_metric.py`)

**Dependencies**: None (sklearn + numpy)

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import List, Tuple, Dict

def probe_learning_curve(
    features: np.ndarray,
    labels: np.ndarray,
    n_samples_list: List[int],
    seeds: List[int],
    c: float = 1.0,
    max_iter: int = 1000,
) -> Dict:
    """
    For each n in n_samples_list and each seed, subsample n training samples,
    fit LogisticRegression, evaluate on full features.
    Returns {
        n_samples_list, mean_accs: List[float], std_accs: List[float],
        per_seed_accs: (len(seeds), len(n_samples_list)),
        auc: float, samples_to_90pct: Optional[int]
    }
    """
    ...

def compute_separability_metric(
    features: np.ndarray,
    spurious_labels: np.ndarray,
    core_labels: np.ndarray,
    n_samples_list: List[int],
    seeds: List[int],
) -> dict:
    """
    Returns {
        spurious_curve, core_curve,  # each from probe_learning_curve()
        auc_ratio, samples_to_90_spurious, samples_to_90_core,
        direction_correct
    }
    """
    ...
```

---

### StatisticalTests (`analysis/statistical_tests.py`)

**Dependencies**: None (scipy)

```python
import numpy as np
from typing import Dict, Any

def apply_bonferroni_correction(p_values: Dict[str, float], alpha: float = 0.05) -> Dict[str, float]:
    """6 tests (3 metrics x 2 datasets). Returns corrected thresholds."""
    ...

def evaluate_gate(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Gate: >= 2/3 metrics direction_correct AND p_value < alpha on Waterbirds.
    Secondary: >= 2/3 directional match on CelebA.
    Returns {
        gate_pass: bool, n_metrics_pass_waterbirds: int,
        n_metrics_pass_celeba: int, gate_label: str,
        per_metric_result: dict
    }
    """
    ...

def compute_complexity_delta_ci(
    spurious_vals: np.ndarray,
    core_vals: np.ndarray,
    confidence: float = 0.95,
) -> Dict[str, float]:
    """Bootstrap 95% CI for delta = mean(core) - mean(spurious). Returns {delta, ci_low, ci_high}."""
    ...
```

---

### MechanismVerifier (`analysis/mechanism_verifier.py`)

**Dependencies**: None

```python
from typing import Dict, Any, Tuple

def verify_mechanism_activated(results: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
    """
    Checks: patches_extracted > 100, features shape = (N, 2048),
    direction_correct_fft, p_value_computed.
    Returns (activated: bool, indicators: dict).
    """
    ...
```

---

### Figures (`visualization/figures.py`)

**Dependencies**: analysis.statistical_tests (gate results)

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any

def plot_complexity_comparison(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    gate_result: Dict[str, Any],
    figures_dir: str,
) -> str:
    """Required: Bar chart spurious vs. core on 3 metrics x 2 datasets with p-value annotations. Returns path."""
    ...

def plot_fft_spectrum(
    spurious_patches: np.ndarray,
    core_patches: np.ndarray,
    figures_dir: str,
    n_examples: int = 4,
) -> str:
    """2D FFT power spectrum heatmap for example patches. Returns path."""
    ...

def plot_learning_curves(
    waterbirds_sep: Dict,
    celeba_sep: Dict,
    figures_dir: str,
) -> str:
    """Probe accuracy vs. N curves for spurious vs. core (both datasets). Returns path."""
    ...

def plot_feature_pca(
    spurious_feats: np.ndarray,
    core_feats: np.ndarray,
    figures_dir: str,
    method: str = "pca",
) -> str:
    """PCA or t-SNE 2D projection of layer-4 features. Returns path."""
    ...

def plot_complexity_gap(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    figures_dir: str,
) -> str:
    """delta_complexity with 95% CI per metric per dataset. Returns path."""
    ...

def generate_all_figures(
    waterbirds_patches: Dict,
    core_patches: Dict,
    spurious_feats: np.ndarray,
    core_feats: np.ndarray,
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    gate_result: Dict[str, Any],
    figures_dir: str,
) -> None: ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: config, data_pipeline, feature_extractor, complexity_metrics, analysis, visualization

```python
import argparse
import json
from config import load_config, ExperimentConfig

def run_dataset(
    cfg: ExperimentConfig,
    dataset: str,  # "waterbirds" | "celeba"
) -> dict:
    """
    Steps: patch extraction → feature extraction → 3 metrics → statistical tests.
    Returns per-dataset results dict.
    """
    ...

def main(config_path: str, device: str) -> dict:
    """
    Orchestrates:
    1. Waterbirds patch extraction + feature extraction + 3 metrics
    2. CelebA patch extraction + feature extraction + 3 metrics
    3. Gate evaluation (Bonferroni, >= 2/3 metrics)
    4. verify_mechanism_activated()
    5. Generate 5 figures
    6. Write results/results_h_m2.json
    Returns full results dict.
    """
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiment.yaml")
    parser.add_argument("--device", default="cuda:0")
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Create config.py (DataConfig, MetricConfig, ExperimentConfig), configs/experiment.yaml, directory structure | 5 | 1+1+1+2 |
| A-2 | Patch Extractor | Implement PatchExtractor: mask-based extraction (foreground/background), quadrant fallback, CelebA hair/face crop, resize to 64x64 uint8 | 12 | 3+2+4+3 |
| A-3 | Waterbirds Data Pipeline | Implement WaterbirdsDataset (metadata.csv + segmentation masks), extract_waterbirds_patches(), get_waterbirds_feature_loader(); handle mask fallback | 13 | 3+3+4+3 |
| A-4 | CelebA Data Pipeline | Implement CelebA stratified loader (4 groups, 5000/group), extract_celeba_patches() (hair top-25% vs. center face crop), get_celeba_feature_loader() | 11 | 3+2+3+3 |
| A-5 | ResNet-50 Feature Extractor | Implement ResNetExtractor: frozen ResNet-50 (fc=Identity), batch inference (256), extract_features() returning (N,2048), extract_split_features() | 10 | 2+3+3+2 |
| A-6 | FFT Complexity Metric | Implement compute_mean_spatial_frequency() (numpy fft2+fftshift, weighted mean freq), compute_fft_metric() (t-test, direction check) | 11 | 2+1+5+3 |
| A-7 | Intra-class Variance Metric | Implement compute_intraclass_variance() (trace of cov), compute_variance_metric() (per-feature t-test on std arrays) | 9 | 2+1+4+2 |
| A-8 | Linear Separability Probe | Implement probe_learning_curve() (LogisticRegression sweep N∈{50,...,full}, 3 seeds, AUC, samples-to-90%), compute_separability_metric() | 13 | 3+2+5+3 |
| A-9 | Statistical Analysis & Gate | Implement apply_bonferroni_correction(), evaluate_gate() (>=2/3 metrics, primary Waterbirds), compute_complexity_delta_ci() (bootstrap), verify_mechanism_activated() | 12 | 2+2+4+4 |
| A-10 | Visualization (5 Figures) | Implement all 5 figure functions: complexity_comparison (required), fft_spectrum, learning_curves, feature_pca, complexity_gap with CI | 11 | 2+2+4+3 |
| A-11 | Experiment Orchestrator | Implement run_dataset() and main() in run_experiment.py: full pipeline for both datasets, gate evaluation, JSON output, figure generation | 10 | 2+3+2+3 |
| A-12 | End-to-End Validation | Run full pipeline on both datasets, verify patches > 100 per class, features shape (N,2048), >= 2/3 metrics pass gate, all 5 figures generated | 8 | 1+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9, A-10, A-11], Low(4-8): [A-1, A-12]

**Total Complexity**: 125 | **Task Count**: 12 (within 6-12 range)
