# Logic Specification: h-e1

**Type:** EXISTENCE (PoC)
**Hypothesis:** TRAK, TracIn, Kronfluence compute influence via mathematically distinct operations

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs (no base hypothesis, no existing codebase)
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Model + Checkpoint Setup [Complexity: 1, Budget: 1]

**Applied:** Standard PyTorch (torchvision ResNet18 adapted for CIFAR-10)

### API Signatures

```python
def build_model(num_classes: int = 10) -> nn.Module:
    """ResNet18 adapted for 32x32 CIFAR input."""
    ...

def train_or_load_checkpoints(model: nn.Module, train_loader: DataLoader,
                               n_ckpts: int = 3) -> List[str]:
    """Returns list of checkpoint file paths."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | [B, 3, 32, 32] | CIFAR batch |
| logits | [B, 10] | model output |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | build_model | ResNet18, conv1/maxpool patched for CIFAR |

---

## A-2: TRAK Influence Computation [Complexity: 2, Budget: 2]

**Applied:** Official `traker.TRAKer` (random projection + gradient sketching)

### API Signatures

```python
from trak import TRAKer

def compute_trak_scores(model: nn.Module, checkpoints: List[str],
                         train_loader: DataLoader, test_loader: DataLoader,
                         train_set_size: int) -> np.ndarray:
    """Returns influence matrix [N_test, N_train]."""
    traker = TRAKer(model=model, task='image_classification',
                     train_set_size=train_set_size)
    for model_id, ckpt in enumerate(checkpoints):
        traker.load_checkpoint(torch.load(ckpt), model_id=model_id)
        for batch in train_loader:
            # batch: (images [B,3,32,32], labels [B])
            traker.featurize(batch=batch, num_samples=batch[0].shape[0])
    traker.finalize_features()

    for model_id, ckpt in enumerate(checkpoints):
        traker.start_scoring_checkpoint(exp_name='test', checkpoint=torch.load(ckpt),
                                         model_id=model_id, num_targets=len(test_loader.dataset))
        for batch in test_loader:
            traker.score(batch=batch, num_samples=batch[0].shape[0])
    scores = traker.finalize_scores(exp_name='test')  # [N_train, N_test]
    return scores.T  # -> [N_test, N_train]
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores (raw) | [N_train, N_test] | TRAKer native output |
| scores (returned) | [N_test, N_train] | transposed for consistency |

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | compute_trak_scores | featurize -> finalize_features -> score -> finalize_scores |

---

## A-3: TracIn Influence Computation [Complexity: 2, Budget: 2]

**Applied:** Official `captum.influence.TracInCP` (gradient dot products across checkpoints)

### API Signatures

```python
from captum.influence import TracInCP

def compute_tracin_scores(model: nn.Module, train_dataset: Dataset,
                           checkpoints: List[str], test_batch: Tuple[Tensor, Tensor],
                           loss_fn: nn.Module = nn.CrossEntropyLoss()) -> np.ndarray:
    """Returns influence matrix [N_test, N_train]."""
    tracin = TracInCP(
        model=model,
        train_dataset=train_dataset,
        checkpoints=checkpoints,
        checkpoints_load_func=lambda m, p: m.load_state_dict(torch.load(p)),
        loss_fn=loss_fn,
        batch_size=128,
    )
    inputs, targets = test_batch  # inputs: [N_test,3,32,32], targets: [N_test]
    scores = tracin.influence((inputs, targets))  # [N_test, N_train]
    return scores.cpu().numpy()
```

### Pseudo-code (algorithm)

```
for ckpt_t in checkpoints:
    load ckpt_t into model
    for test_z in test_batch:
        g_test = grad(loss(model, test_z))
    for train_z in train_dataset:
        g_train = grad(loss(model, train_z))
        score[test, train] += lr_t * dot(g_test, g_train)
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_tracin_scores | TracInCP init + influence() call |

---

## A-4: Kronfluence Influence Computation [Complexity: 3, Budget: 3]

**Applied:** Official `kronfluence.Analyzer` (EKFAC approximation of Fisher inverse)

### API Signatures

```python
from kronfluence import Analyzer, prepare_model
from kronfluence.task import Task

class CIFARTask(Task):
    def compute_train_loss(self, batch, model, sample=False) -> Tensor: ...
    def compute_measurement(self, batch, model) -> Tensor: ...

def compute_kronfluence_scores(model: nn.Module, train_dataset: Dataset,
                                test_dataset: Dataset) -> np.ndarray:
    """Returns influence matrix [N_test, N_train]."""
    task = CIFARTask()
    kron_model = prepare_model(model=model, task=task)
    analyzer = Analyzer(analysis_name="h-e1", model=kron_model, task=task)

    analyzer.fit_all_factors(factors_name="factors", dataset=train_dataset)
    analyzer.compute_pairwise_scores(
        scores_name="scores", factors_name="factors",
        query_dataset=test_dataset, train_dataset=train_dataset,
        per_device_query_batch_size=128,
    )
    scores = analyzer.load_pairwise_scores(scores_name="scores")  # dict or Tensor [N_test, N_train]
    return scores["all_modules"].cpu().numpy() if isinstance(scores, dict) else scores.cpu().numpy()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | [N_test, N_train] | pairwise EKFAC-approximated influence |

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | compute_kronfluence_scores | prepare_model -> fit_all_factors -> compute_pairwise_scores -> load |

---

## A-5: Correlation + Verification [Complexity: 2, Budget: 2]

**Applied:** scipy.stats (Pearson/Spearman/Kendall)

### API Signatures

```python
from scipy.stats import pearsonr, spearmanr, kendalltau
import numpy as np

def compute_method_correlations(scores_dict: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """scores_dict[method] shape [N_test, N_train]. Returns pairwise correlation dict."""
    methods = list(scores_dict.keys())
    correlations = {}
    for i, m1 in enumerate(methods):
        for m2 in methods[i+1:]:
            s1 = scores_dict[m1].flatten()  # [N_test*N_train]
            s2 = scores_dict[m2].flatten()
            correlations[f'{m1}_vs_{m2}'] = {
                'pearson': pearsonr(s1, s2)[0],
                'spearman': spearmanr(s1, s2)[0],
                'kendall': kendalltau(s1, s2)[0],
            }
    return correlations


def verify_mathematical_distinctness(scores_dict: Dict[str, np.ndarray],
                                      threshold: float = 0.9) -> Tuple[bool, dict]:
    """Checks all pairwise |Pearson r| < threshold. Also checks no NaN/Inf in scores."""
    for name, s in scores_dict.items():
        assert np.all(np.isfinite(s)), f"{name} contains NaN/Inf"

    correlations = compute_method_correlations(scores_dict)
    max_correlation = max(abs(c['pearson']) for c in correlations.values())
    passed = max_correlation < threshold
    evidence = {
        'max_correlation': max_correlation,
        'threshold': threshold,
        'all_correlations': correlations,
        'verdict': 'DISTINCT' if passed else 'TOO_SIMILAR',
    }
    return passed, evidence
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | compute_method_correlations | pairwise Pearson/Spearman/Kendall |
| L-5-2 | verify_mathematical_distinctness | NaN/Inf check + threshold gate |

---

## Input/Output Summary

- **Input:** trained model + checkpoints (2-3), CIFAR-10 train/test loaders, ≥1000 test samples
- **Output per method:** influence matrix `[N_test, N_train]` (float32, finite)
- **Final output:** `correlations.json` (pairwise Pearson/Spearman/Kendall) + `(passed: bool, evidence: dict)` from `verify_mathematical_distinctness`
