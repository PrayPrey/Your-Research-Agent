# Logic: H-E1 — Permutation Orbit Non-Triviality Analysis

**Applied**: stratified-analysis-pipeline pattern (load → verify → sample → compute → gate)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Data Loading [Complexity: 10, Budget: 2 subtasks]

**Applied**: try/except dual-path loading pattern

### API Signatures

```python
# h-e1/code/data_loader.py
from typing import List, Dict, Any
from collections import OrderedDict
import torch
from config import ExperimentConfig

def load_zoo_checkpoints(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load all checkpoints; try package first, fall back to files.
    Returns list of {'state_dict': OrderedDict, 'test_accuracy': float}."""
    ...

def load_via_package(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load using ModelZooDataset pip package.
    Returns list of {'state_dict': OrderedDict, 'test_accuracy': float}."""
    ...

def load_via_files(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load .pt files from cfg.data_dir via torch.load.
    Returns list of {'state_dict': OrderedDict, 'test_accuracy': float}."""
    ...
```

### Pseudo-code

```
load_zoo_checkpoints(cfg):
    try:
        return load_via_package(cfg)
    except ImportError:
        return load_via_files(cfg)

load_via_package(cfg):
    from modelzoo.datasets import ModelZooDataset
    ds = ModelZooDataset(name=cfg.zoo_name, root=cfg.data_dir)
    return [{'state_dict': ds[i]['state_dict'], 'test_accuracy': ds[i]['test_accuracy']} for i in range(len(ds))]

load_via_files(cfg):
    pts = sorted(cfg.data_dir.glob("*.pt"))
    results = []
    for p in tqdm(pts):
        ckpt = torch.load(p, map_location='cpu')
        # ckpt may be {'state_dict': ..., 'test_accuracy': float} or raw state_dict
        if isinstance(ckpt, dict) and 'state_dict' in ckpt:
            results.append({'state_dict': ckpt['state_dict'], 'test_accuracy': ckpt['test_accuracy']})
        else:
            # raw state_dict, no accuracy — skip or store with acc=None
            pass
    return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_via_package | Implement ModelZooDataset import path with error handling |
| L-2-2 | load_via_files | Implement torch.load fallback with .pt glob and tqdm |

---

## A-4: Weight Analysis Pipeline [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard PyTorch cosine_similarity + numpy percentile binning

### API Signatures

```python
# h-e1/code/weight_analysis.py
from typing import List, Dict, Tuple, Any
import torch
import torch.nn.functional as F
import numpy as np
from config import ExperimentConfig

def flatten_weights(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Concatenate weight/bias tensors into 1D float32 CPU tensor.
    # Input: state_dict with keys containing 'weight' or 'bias'
    # conv1.weight: [32, 1, 3, 3], conv1.bias: [32]
    # conv2.weight: [64, 32, 3, 3], conv2.bias: [64]
    # fc1.weight: [128, 9216], fc1.bias: [128]  (64*6*6=9216 for 28x28 after 2x maxpool)
    # fc2.weight: [10, 128], fc2.bias: [10]
    # Output: [N_params] float32 cpu  (N_params ~ 500K)
    """
    ...

def compute_cosine_distance(w1: torch.Tensor, w2: torch.Tensor) -> float:
    """Compute 1 - cosine_similarity(w1, w2).
    # w1, w2: [N_params] float32
    # Returns scalar in [0, 2]
    """
    ...

def stratified_pair_sample(
    checkpoints: List[Dict[str, Any]],
    n_per_decile: int = 50,
    acc_threshold: float = 0.01,
    seed: int = 42
) -> List[Tuple[Dict, Dict, int]]:
    """Sample pairs stratified by accuracy decile with |delta_acc| < threshold.
    # Returns: List of (model_1, model_2, decile_index), total <= n_per_decile * 10
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| conv1.weight | [32, 1, 3, 3] | 288 params |
| conv1.bias | [32] | 32 params |
| conv2.weight | [64, 32, 3, 3] | 18432 params |
| conv2.bias | [64] | 64 params |
| fc1.weight | [128, 9216] | 1179648 params; 9216=64*6*6 |
| fc1.bias | [128] | 128 params |
| fc2.weight | [10, 128] | 1280 params |
| fc2.bias | [10] | 10 params |
| flattened | [N_params] | ~1.2M float32, cpu |

### Pseudo-code

```
flatten_weights(state_dict):
    tensors = [v.float().cpu().view(-1) for k, v in state_dict.items()
               if 'weight' in k or 'bias' in k]
    return torch.cat(tensors)  # [N_params]

compute_cosine_distance(w1, w2):
    sim = F.cosine_similarity(w1.unsqueeze(0), w2.unsqueeze(0)).item()
    return 1.0 - sim  # scalar in [0, 2]

stratified_pair_sample(checkpoints, n_per_decile, acc_threshold, seed):
    rng = np.random.default_rng(seed)
    accs = np.array([c['test_accuracy'] for c in checkpoints])
    boundaries = np.percentile(accs, np.linspace(0, 100, 11))  # 11 points -> 10 bins
    pairs = []
    for d in range(10):
        lo, hi = boundaries[d], boundaries[d+1]
        bin_idxs = np.where((accs >= lo) & (accs <= hi))[0]
        candidates = [(i, j) for i in bin_idxs for j in bin_idxs
                      if i < j and abs(accs[i] - accs[j]) < acc_threshold]
        sampled = rng.choice(len(candidates), size=min(n_per_decile, len(candidates)), replace=False)
        for s in sampled:
            i, j = candidates[s]
            pairs.append((checkpoints[i], checkpoints[j], d))
    return pairs
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | flatten_and_cosine | Implement flatten_weights + compute_cosine_distance |
| L-4-2 | stratified_sampling | Implement stratified_pair_sample with np.percentile binning |

---

## A-5: Orbit Statistics & Gate [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard numpy aggregation + threshold gate pattern

### API Signatures

```python
# h-e1/code/orbit_statistics.py
from typing import List, Dict, Tuple, Any
import numpy as np
from weight_analysis import compute_cosine_distance, flatten_weights

def compute_orbit_statistics(
    pairs: List[Tuple[Dict, Dict, int]],
    cosine_dist_threshold: float = 0.1
) -> Tuple[List[Dict], float]:
    """Compute cosine distances for all pairs and orbit proportion.
    # Returns:
    #   distances: List of {'decile': int, 'cosine_dist': float, 'is_orbit_candidate': bool}
    #   orbit_proportion: float in [0, 1]
    """
    ...

def per_decile_proportions(distances: List[Dict]) -> Dict[int, float]:
    """Compute orbit candidate proportion per decile.
    # Returns: {decile_idx: proportion} for decile_idx in 0..9
    """
    ...

def evaluate_gate(
    bn_free: bool,
    orbit_proportion: float,
    threshold: float = 0.05
) -> Dict[str, Any]:
    """Evaluate MUST_WORK gate conditions.
    # Returns: {'passed': bool, 'bn_free': bool, 'orbit_proportion': float,
    #           'threshold': float, 'message': str}
    """
    ...
```

### Pseudo-code

```
compute_orbit_statistics(pairs, cosine_dist_threshold):
    distances = []
    for (m1, m2, decile) in tqdm(pairs):
        w1 = flatten_weights(m1['state_dict'])
        w2 = flatten_weights(m2['state_dict'])
        d = compute_cosine_distance(w1, w2)
        distances.append({'decile': decile,
                          'cosine_dist': d,
                          'is_orbit_candidate': d > cosine_dist_threshold})
    orbit_proportion = mean([r['is_orbit_candidate'] for r in distances])
    return distances, orbit_proportion

per_decile_proportions(distances):
    from collections import defaultdict
    buckets = defaultdict(list)
    for r in distances:
        buckets[r['decile']].append(r['is_orbit_candidate'])
    return {d: np.mean(v) for d, v in buckets.items()}

evaluate_gate(bn_free, orbit_proportion, threshold):
    passed = bn_free and (orbit_proportion > threshold)
    msg = "PASS" if passed else ("FAIL: BN found" if not bn_free else
          f"FAIL: orbit_proportion={orbit_proportion:.3f} <= {threshold}")
    return {'passed': passed, 'bn_free': bn_free,
            'orbit_proportion': orbit_proportion,
            'threshold': threshold, 'message': msg}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_orbit_statistics | Iterate pairs, call flatten+cosine, collect distances list + proportion |
| L-5-2 | per_decile_gate | Implement per_decile_proportions + evaluate_gate with PASS/FAIL message |

---

## Summary

| Module | Functions | Subtasks |
|--------|-----------|----------|
| A-2 data_loader.py | load_zoo_checkpoints, load_via_package, load_via_files | L-2-1, L-2-2 |
| A-4 weight_analysis.py | flatten_weights, compute_cosine_distance, stratified_pair_sample | L-4-1, L-4-2 |
| A-5 orbit_statistics.py | compute_orbit_statistics, per_decile_proportions, evaluate_gate | L-5-1, L-5-2 |

**Total subtasks**: 6/6
