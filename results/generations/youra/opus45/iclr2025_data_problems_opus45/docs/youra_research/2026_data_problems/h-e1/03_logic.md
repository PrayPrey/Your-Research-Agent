# Logic: H-E1
# Data Attribution Method Comparison - Pareto Trade-off Detection

**Date:** 2026-03-26
**Hypothesis Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

Applied: Standard PyTorch wrapper pattern
Applied: scipy.stats bootstrap CI pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: Attribution Methods [Complexity: 16, Budget: 3 subtasks]

### API Signatures

```python
# attribution.py
import numpy as np
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any
from config import ExperimentConfig

BUDGET_MAP: Dict[str, Dict[int, Any]] = {
    'TRAK':   {10: {'proj_dim': 10},  25: {'proj_dim': 25},  50: {'proj_dim': 50},
               75: {'proj_dim': 75},  100: {'proj_dim': 100}},
    'TracIn': {10: {'n_ckpts': 1},    25: {'n_ckpts': 2},    50: {'n_ckpts': 3},
               75: {'n_ckpts': 4},    100: {'n_ckpts': 5}},
    'IF':     {10: {'depth': 10},     25: {'depth': 25},     50: {'depth': 50},
               75: {'depth': 75},     100: {'depth': 100}},
    'FastIF': {10: {'n_ckpts': 1},    25: {'n_ckpts': 2},    50: {'n_ckpts': 3},
               75: {'n_ckpts': 4},    100: {'n_ckpts': 5}},
}


class AttributionMethod:
    """Base wrapper for a data attribution method."""

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """Compute attribution scores. Returns [n_train, n_test]."""
        raise NotImplementedError


class TRAKMethod(AttributionMethod):
    """Wraps MadryLab/trak TRAKer. Budget maps to proj_dim."""

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """TRAK attribution. Returns scores [n_train, n_test]."""
        ...


class TracInMethod(AttributionMethod):
    """Wraps Captum TracInCPFast. Budget maps to n_checkpoints (1-5)."""

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """TracIn attribution. Returns scores [n_train, n_test]."""
        ...


class IFMethod(AttributionMethod):
    """Wraps nimarb/pytorch_influence_functions LISSA. Budget maps to recursion_depth."""

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """IF attribution. Returns scores [n_train, n_test]."""
        ...


class FastIFMethod(AttributionMethod):
    """Last-layer IF via Captum TracInCPFast. Budget maps to n_checkpoints."""

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """FastIF attribution. Returns scores [n_train, n_test]."""
        ...


def get_method(name: str) -> AttributionMethod:
    """Factory: 'TRAK' | 'TracIn' | 'IF' | 'FastIF' -> AttributionMethod instance."""
    _registry = {
        'TRAK': TRAKMethod,
        'TracIn': TracInMethod,
        'IF': IFMethod,
        'FastIF': FastIFMethod,
    }
    return _registry[name]()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores (output) | [5000, 100] | Attribution score matrix |
| proj_dim (TRAK) | scalar int | From BUDGET_MAP |
| n_ckpts (TracIn/FastIF) | scalar int 1-5 | Evenly spaced from checkpoint_dir |

### Pseudo-code: TRAKMethod.compute_scores

```
1. proj_dim = BUDGET_MAP['TRAK'][budget]['proj_dim']
2. torch.manual_seed(seed)
3. traker = TRAKer(model, task='image_classification', train_set_size=5000,
                   proj_dim=proj_dim, device=device)
4. traker.load_checkpoint(checkpoint_path, model_id=0)
5. for batch in train_loader:
       traker.featurize(batch=batch, num_samples=batch[0].shape[0])
6. traker.finalize_features(model_id=0)
7. scores = traker.score(exp_name='trak_b{budget}_s{seed}', test_dset=test_subset)
   # trak returns [n_test, n_train] -> transpose
8. return scores.T   # [n_train, n_test] = [5000, 100]
```

### Pseudo-code: TracInMethod.compute_scores

```
1. n_ckpts = BUDGET_MAP['TracIn'][budget]['n_ckpts']
2. ckpt_paths = select_n_checkpoints(cfg.checkpoint_dir, n_ckpts)
   # Evenly spaced; checkpoints saved every 25 epochs during training
3. tracin = TracInCPFast(model, ckpt_paths, checkpoints_load_func,
                         loss_fn=nn.CrossEntropyLoss(reduction='none'),
                         final_fc_layer=model.fc)
4. scores = tracin.influence(test_inputs, train_loader, top_k=None)
   # shape: [n_test, n_train]
5. return scores.T.numpy()   # [n_train, n_test]
```

### Pseudo-code: IFMethod.compute_scores

```
1. depth = BUDGET_MAP['IF'][budget]['depth']
2. scores = np.zeros((n_train, n_test))   # [5000, 100]
3. for j, test_sample in enumerate(test_samples):
       for i in range(n_train):
           scores[i, j] = calc_influence_single(
               model, train_loader, test_sample,
               train_idx=i, gpu=device_id,
               recursion_depth=depth, r=1
           )
4. return scores   # [n_train, n_test]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | TRAK wrapper | TRAKMethod.compute_scores + checkpoint loading |
| L-4-2 | TracIn/FastIF wrappers | TracInMethod + FastIFMethod via Captum TracInCPFast |
| L-4-3 | IF wrapper + factory | IFMethod + get_method + BUDGET_MAP |

---

## A-3: LOO Ground Truth [Complexity: 13, Budget: 2 subtasks]

### API Signatures

```python
# evaluate.py (LOO section)
import numpy as np
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from typing import Callable, Optional
from config import ExperimentConfig


def compute_loo_ground_truth(
    model_fn: Callable[[int], nn.Module],   # seed -> freshly initialized nn.Module
    train_loader: DataLoader,               # full 5000-sample train loader
    loo_test_loader: DataLoader,            # 100-sample test loader
    loo_test_indices: np.ndarray,           # [100] test sample indices
    cfg: ExperimentConfig,
    device: str = 'cuda',
) -> np.ndarray:
    """Compute LOO ground truth via R=10 retraining. Returns [n_train, n_loo_test]."""
    ...


def _compute_full_losses(
    model: nn.Module,
    test_loader: DataLoader,
    device: str,
) -> np.ndarray:
    """Per-sample cross-entropy losses. Returns [n_test]."""
    ...


def _make_loo_loader(
    train_dataset: Subset,
    leave_out_idx: int,
    cfg: ExperimentConfig,
) -> DataLoader:
    """DataLoader over all training samples except leave_out_idx."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| loo_ground_truth | [5000, 100] | LOO delta per (train, test) pair |
| base_losses | [100] | L(z_test; theta) for base model |
| loo_losses_i | [100] | L(z_test; theta^(-i)) |
| deltas[i] | [100] | loo_losses_i - base_losses for train idx i |

### Pseudo-code: compute_loo_ground_truth

```
1. cache_path = cfg.results_dir + '/loo_cache.npy'
2. if os.path.exists(cache_path): return np.load(cache_path)
3. deltas = np.zeros((n_train, n_loo_test))   # [5000, 100]
4. for r in range(cfg.n_loo_retrains):         # R=10
       base_model = train_model(model_fn(r), train_loader, cfg, seed=r, device)
       base_losses = _compute_full_losses(base_model, loo_test_loader, device)  # [100]
       for i in range(n_train):                # 5000
           loo_loader = _make_loo_loader(train_dataset, i, cfg)
           loo_model = train_model(model_fn(r), loo_loader, cfg, seed=r, device)
           loo_losses = _compute_full_losses(loo_model, loo_test_loader, device)
           deltas[i] += (loo_losses - base_losses)   # accumulate [100]
5. deltas /= cfg.n_loo_retrains   # average over R seeds
6. np.save(cache_path, deltas)
7. return deltas   # [5000, 100]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | LOO retraining loop | compute_loo_ground_truth + caching to results/loo_cache.npy |
| L-3-2 | Loss helpers | _compute_full_losses + _make_loo_loader |

---

## A-5: Metrics + Stats [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# evaluate.py (metrics section)
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy.stats import spearmanr, pearsonr, bootstrap
from config import ExperimentConfig


@dataclass
class MetricResult:
    rho_r: float                            # Spearman correlation
    rho_m: float                            # Pearson correlation
    S: float                                # Normalized stability (Var ratio)
    rho_r_ci: Tuple[float, float]           # 95% bootstrap CI
    rho_m_ci: Tuple[float, float]           # 95% bootstrap CI


@dataclass
class CrossingResult:
    method_a: str
    method_b: str
    budget: int
    crosses_rho_r: bool     # CI of (rho_r_a - rho_r_b) excludes 0
    crosses_rho_m: bool     # CI of (rho_m_a - rho_m_b) excludes 0


def compute_metrics(
    pred_scores: np.ndarray,                                # [n_train, n_test]
    loo_ground_truth: np.ndarray,                           # [n_train, n_test]
    cfg: ExperimentConfig,
    seed_scores_list: Optional[List[np.ndarray]] = None,    # list of [n_train, n_test]
) -> MetricResult:
    """Compute rho_r, rho_m, S + bootstrap CIs. Flattens inputs for correlation."""
    ...


def detect_crossings(
    results: Dict[str, Dict[int, List[MetricResult]]],  # [method][budget][seed_idx]
    cfg: ExperimentConfig,
) -> List[CrossingResult]:
    """Detect CI-separated metric crossings for all method pairs x budgets."""
    ...


def identify_pareto_front(
    results: Dict[str, Dict[int, List[MetricResult]]],
    budget: int,
) -> List[str]:
    """Non-dominated method names at given budget (higher rho_r + rho_m = better)."""
    ...


def plot_all_figures(
    results: Dict[str, Dict[int, List[MetricResult]]],
    crossings: List[CrossingResult],
    cfg: ExperimentConfig,
) -> None:
    """Generate and save 4+ figures to cfg.figures_dir."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| pred_scores | [5000, 100] | Flattened to [500000] for correlation |
| loo_ground_truth | [5000, 100] | Same flattening |
| seed_scores_list | list of [5000, 100] | len=3 for S computation |

### Pseudo-code: compute_metrics

```
1. flat_pred = pred_scores.flatten()    # [500000]
2. flat_loo  = loo_ground_truth.flatten()
3. rho_r = spearmanr(flat_pred, flat_loo).statistic
4. rho_m = pearsonr(flat_pred, flat_loo).statistic
5. ci_r = bootstrap((flat_pred, flat_loo),
                    lambda a,b: spearmanr(a,b).statistic,
                    n_resamples=cfg.n_bootstrap,
                    confidence_level=cfg.confidence_level,
                    method='BCa', paired=True)
   rho_r_ci = (ci_r.confidence_interval.low, ci_r.confidence_interval.high)
6. ci_m = bootstrap((flat_pred, flat_loo),
                    lambda a,b: pearsonr(a,b).statistic, ...)
   rho_m_ci = (ci_m.confidence_interval.low, ci_m.confidence_interval.high)
7. if seed_scores_list is not None and len(seed_scores_list) > 1:
       seed_var = np.var(np.stack(seed_scores_list), axis=0).mean()
       S = seed_var / (np.var(loo_ground_truth) + 1e-8)
   else: S = 0.0
8. return MetricResult(rho_r, rho_m, S, rho_r_ci, rho_m_ci)
```

### Pseudo-code: detect_crossings

```
1. crossings = []
2. for (ma, mb) in combinations(results.keys(), 2):
       for budget in cfg.compute_budgets:
           rho_r_diffs = [results[ma][budget][s].rho_r - results[mb][budget][s].rho_r
                          for s in range(len(results[ma][budget]))]
           rho_m_diffs = [results[ma][budget][s].rho_m - results[mb][budget][s].rho_m
                          for s in range(len(results[ma][budget]))]
           ci_r = bootstrap((np.array(rho_r_diffs),), np.mean,
                             n_resamples=cfg.n_bootstrap,
                             confidence_level=cfg.confidence_level)
           ci_m = bootstrap((np.array(rho_m_diffs),), np.mean, ...)
           crosses_r = ci_r.confidence_interval.high < 0 or ci_r.confidence_interval.low > 0
           crosses_m = ci_m.confidence_interval.high < 0 or ci_m.confidence_interval.low > 0
           # Crossing = CI-separated on BOTH metrics AND opposite ordering
           mean_r_diff = np.mean(rho_r_diffs)
           mean_m_diff = np.mean(rho_m_diffs)
           if crosses_r and crosses_m and np.sign(mean_r_diff) != np.sign(mean_m_diff):
               crossings.append(CrossingResult(ma, mb, budget, crosses_r, crosses_m))
3. return crossings
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Metric computation | compute_metrics: rho_r, rho_m, S, bootstrap CIs |
| L-5-2 | Crossing + Pareto | detect_crossings, identify_pareto_front, plot_all_figures |

---

## Summary: Subtask Budget

| Task | Budget | Used | Subtasks |
|------|--------|------|----------|
| A-4 | 3 | 3 | L-4-1, L-4-2, L-4-3 |
| A-3 | 2 | 2 | L-3-1, L-3-2 |
| A-5 | 2 | 2 | L-5-1, L-5-2 |
| **Total** | **7** | **7** | |
