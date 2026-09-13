# Logic Design: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-05-12  
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - designing new APIs  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## A-1: Setup (Complexity: 6, Budget: 1)

**Applied:** Standard Python project structure

### API Signatures

```python
# config.py
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    data_root: str = "./data/datasets"
    output_dir: str = "./h-e1"
    device: str = "cuda"
    batch_size: int = 256
    n_pca_components: int = 2
    thresholds: dict = None
    seed: int = 42
    
    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = {"major": 0.07, "minor": 0.02, "patch": 0.005}

def get_default_config() -> ExperimentConfig:
    """Return default experiment configuration."""
    return ExperimentConfig()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Project Structure | Create directories, requirements.txt, config.py, ground_truth_labels.json |

---

## A-2: Data Loading (Complexity: 11, Budget: 1)

**Applied:** PyTorch Dataset API patterns

### API Signatures

```python
# src/data_loader.py
import torch
from typing import Tuple, List

class DatasetPairLoader:
    def __init__(self, data_root: str):
        """Initialize loader. data_root: path to datasets directory."""
        self.data_root = data_root
        
    def load_pair(self, dataset_name: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load v_old and v_new. Returns: (v_old: [N1, C, H, W], v_new: [N2, C, H, W])"""
        ...
        
    def get_all_pairs(self) -> List[Tuple[str, torch.Tensor, torch.Tensor, str]]:
        """Iterate all 15 pairs. Returns: [(name, v_old, v_new, true_label), ...]"""
        ...

def load_ground_truth_labels() -> dict:
    """Load ground truth from JSON. Returns: {dataset_name: label}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| v_old | [N1, C, H, W] or [N1, seq_len] | Vision or NLP |
| v_new | [N2, C, H, W] or [N2, seq_len] | Same modality as v_old |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | DataLoader | Implement DatasetPairLoader with torchvision/HuggingFace loaders for 15 pairs |

---

## A-3: Feature Extraction (Complexity: 10, Budget: 1)

**Applied:** PyTorch frozen model feature extraction

### API Signatures

```python
# src/feature_extractor.py
import torch
import torch.nn as nn

class FeatureExtractor:
    def __init__(self, model_type: str = "resnet50", device: str = "cuda"):
        """Initialize with frozen model. model_type: 'resnet50' or 'bert-base'."""
        self.device = device
        self.model = load_pretrained_model(model_type).to(device)
        self.model.eval()
        
    def extract_features(
        self, 
        data: torch.Tensor, 
        batch_size: int = 256
    ) -> torch.Tensor:
        """Extract features in batches. data: [N, ...] -> [N, F]"""
        ...
        
    def get_feature_dim(self) -> int:
        """Return feature dimension F."""
        ...

def load_pretrained_model(model_type: str) -> nn.Module:
    """Load frozen model without classification head."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| data | [N, C, H, W] or [N, seq] | Input images or text |
| features | [N, F] | F=512-2048 |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Feature Extractor | Implement FeatureExtractor with ResNet-50/BERT, remove heads, batch processing |

---

## A-4: SVAD Classifier (Complexity: 14, Budget: 1)

**Applied:** Scikit-learn PCA + Scipy KS test + Custom MMD

### API Signatures

```python
# src/svad_classifier.py
import torch
from sklearn.decomposition import PCA
from typing import Tuple, Dict

class SVADDriftClassifier:
    def __init__(self, n_pca_components: int = 2, thresholds: dict = None):
        """Initialize PCA and detectors. thresholds: {major: 0.07, minor: 0.02, patch: 0.005}"""
        self.n_components = n_pca_components
        self.pca = PCA(n_components=n_pca_components)
        self.thresholds = thresholds or {"major": 0.07, "minor": 0.02, "patch": 0.005}
        self.ref_features_pca = None
        
    def fit_reference(self, ref_features: torch.Tensor) -> None:
        """Fit PCA on v_old. ref_features: [N, F]"""
        ...
        
    def classify_version_change(
        self, 
        new_features: torch.Tensor
    ) -> Tuple[str, Dict[str, float]]:
        """Classify v_new. Returns: (label, {ks_score: float, mmd_score: float})"""
        ...
        
    def _compute_ks_score(self, features: torch.Tensor) -> float:
        """KS test on PCA features. features: [N, 2] -> ks_stat"""
        ...
        
    def _compute_mmd_score(self, features: torch.Tensor) -> float:
        """MMD with Gaussian RBF kernel. features: [N, 2] -> mmd_stat"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ref_features | [N1, F] | v_old features |
| new_features | [N2, F] | v_new features |
| ref_features_pca | [N1, 2] | PCA-reduced |
| new_features_pca | [N2, 2] | PCA-reduced |

### Pseudo-code

```
1. fit_reference(ref_features):
   - fit PCA on ref_features [N1, F]
   - transform to ref_features_pca [N1, 2]
   - store ref_features_pca

2. classify_version_change(new_features):
   - transform new_features to new_features_pca [N2, 2]
   - ks_score = max(KS_test(ref_pca[:, i], new_pca[:, i]) for i in [0, 1])
   - mmd_score = MMD(ref_pca, new_pca, kernel=RBF)
   - max_score = max(ks_score, mmd_score)
   - if max_score >= 0.07: return "MAJOR"
   - elif max_score >= 0.02: return "MINOR"
   - else: return "PATCH"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | SVAD Classifier | Implement PCA fit, KS test (scipy.stats.ks_2samp), MMD (custom RBF kernel), threshold classification |

---

## A-5: Evaluation (Complexity: 9, Budget: 0)

**Applied:** Scikit-learn metrics

### API Signatures

```python
# src/evaluator.py
import numpy as np
from typing import Dict, Tuple

class ClassificationEvaluator:
    def __init__(self):
        """Initialize evaluator."""
        self.predictions = []
        self.true_labels = []
        self.scores = []
        
    def add_prediction(
        self, 
        true_label: str, 
        pred_label: str, 
        scores: Dict[str, float]
    ) -> None:
        """Store prediction result."""
        ...
        
    def compute_metrics(self) -> Dict[str, float]:
        """Compute precision/recall/F1/accuracy. Returns: {precision: float, recall: float, ...}"""
        ...
        
    def get_confusion_matrix(self) -> np.ndarray:
        """Get 3x3 confusion matrix. Returns: [3, 3]"""
        ...
        
    def check_gate_condition(self) -> Tuple[bool, Dict]:
        """Check PoC pass: precision>=0.7 AND recall>=0.85. Returns: (passed, metrics)"""
        ...
```

---

## A-6: Visualization (Complexity: 8, Budget: 0)

**Applied:** Matplotlib/Seaborn plotting

### API Signatures

```python
# src/visualizer.py
import numpy as np
from typing import List, Dict

def plot_gate_metrics(metrics: Dict[str, float], save_path: str) -> None:
    """Bar chart with target lines. metrics: {precision, recall, f1, accuracy}"""
    ...

def plot_confusion_matrix(cm: np.ndarray, save_path: str) -> None:
    """Seaborn heatmap. cm: [3, 3]"""
    ...

def plot_drift_scores(results: List[Dict], save_path: str) -> None:
    """Histogram of KS/MMD scores by label."""
    ...

def plot_per_dataset_performance(results: List[Dict], save_path: str) -> None:
    """Bar chart of accuracy per dataset."""
    ...
```

---

## A-7: Experiment Runner (Complexity: 10, Budget: 0)

**Applied:** Standard experiment orchestration

### API Signatures

```python
# run_experiment.py
import json
from pathlib import Path

def main():
    """Main experiment loop.
    
    Flow:
    1. Load config
    2. Initialize components (DataLoader, FeatureExtractor, SVADClassifier, Evaluator)
    3. For each of 15 dataset pairs:
       - Load v_old, v_new
       - Extract features
       - Fit classifier on v_old
       - Classify v_new
       - Store result
    4. Compute metrics
    5. Generate visualizations
    6. Save results to 04_results.json
    """
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
1. config = get_default_config()
2. loader = DatasetPairLoader(config.data_root)
3. extractor = FeatureExtractor("resnet50", config.device)
4. classifier = SVADDriftClassifier(config.n_pca_components, config.thresholds)
5. evaluator = ClassificationEvaluator()

6. For (name, v_old, v_new, true_label) in loader.get_all_pairs():
   a. feat_old = extractor.extract_features(v_old, config.batch_size)
   b. feat_new = extractor.extract_features(v_new, config.batch_size)
   c. classifier.fit_reference(feat_old)
   d. pred_label, scores = classifier.classify_version_change(feat_new)
   e. evaluator.add_prediction(true_label, pred_label, scores)

7. metrics = evaluator.compute_metrics()
8. passed, gate_metrics = evaluator.check_gate_condition()
9. Generate all visualizations
10. Save results to 04_results.json
```

---

## Budget Summary

| Task | Complexity | Budget Allocated | Subtasks Used |
|------|------------|------------------|---------------|
| A-1 | 6 | 1 | 1 |
| A-2 | 11 | 1 | 1 |
| A-3 | 10 | 1 | 1 |
| A-4 | 14 | 1 | 1 |
| A-5 | 9 | 0 | 0 |
| A-6 | 8 | 0 | 0 |
| A-7 | 10 | 0 | 0 |
| **Total** | **68** | **4** | **4** |

---

## Key Design Decisions

1. **PCA Components**: Fixed at 2 (TorchDrift best practice for KS test)
2. **Thresholds**: Cold-start values (7%/2%/0.5%) from hypothesis
3. **Feature Extraction**: Frozen models only (no training)
4. **Batch Processing**: batch_size=256 for memory efficiency
5. **Drift Score**: max(ks_score, mmd_score) for classification

---

## Validation Checkpoints

1. **After L-2-1**: All 15 dataset pairs load without error
2. **After L-3-1**: Feature dimensions [N, 512-2048] verified
3. **After L-4-1**: Drift scores computed (no NaN/Inf)
4. **After full run**: Gate condition check executed

---

**Document Status:** READY FOR PHASE 4  
**Total Subtasks:** 4/4 used  
**Next Phase:** Phase 4 - Task-Driven Implementation
