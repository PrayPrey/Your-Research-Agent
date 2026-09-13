# Logic: h-m1

**Applied**: No KB pattern match (similarity <0.34, unrelated CUDA/AWS docs) — used official library APIs (trak, kronfluence, captum TracIn) per PRD.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Config & Seeding [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch reproducibility pattern

### API Signatures

```python
# config.py
@dataclass
class ExperimentConfig:
    seed: int = 42
    epochs: int = 200
    batch_size: int = 128
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    checkpoint_every: int = 20
    proj_dim: int = 2048
    probes_per_mode: int = 1000
    data_root: str = "./data"
    ckpt_dir: str = "./h-m1/checkpoints"
    fig_dir: str = "./h-m1/figures"

def set_all_seeds(seed: int) -> None:
    """Seeds random, numpy, torch, torch.cuda; sets cudnn.deterministic=True."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | ExperimentConfig dataclass | Fields above |
| L-1-2 | set_all_seeds() | random/np/torch/cuda seeding |
| L-1-3 | Dir setup | mkdir ckpt_dir, fig_dir |
| L-1-4 | Config validation | assert proj_dim>0, epochs%checkpoint_every==0 |

---

## A-2: Data Pipeline [Complexity: 10, Budget: 10]

**Applied**: torchvision ImageFolder/CIFAR10 standard loading

### API Signatures

```python
# data.py
def get_datasets(cfg: ExperimentConfig) -> tuple[Dataset, Dataset]:
    """CIFAR-10 train/test, ImageNet-normalized. Returns (train_ds, test_ds)."""

def get_loaders(train_ds: Dataset, test_ds: Dataset, cfg: ExperimentConfig) -> tuple[DataLoader, DataLoader]:
    """train shuffle=True, test shuffle=False, num_workers=4."""

def build_probe_pairs(train_ds: Dataset, test_ds: Dataset, seed: int) -> dict[str, list[tuple[int, int]]]:
    """Returns {'mem': [...], 'transfer': [...], 'spurious': [...]}, 1000 pairs each."""

def _find_memorization_pairs(train_ds: Dataset, test_ds: Dataset, n: int) -> list[tuple[int, int]]:
    """Near-duplicate detection via pixel/feature distance (e.g. torch.cdist on flattened images, top-n closest cross-set)."""

def _find_transfer_pairs(train_ds: Dataset, test_ds: Dataset, n: int) -> list[tuple[int, int]]:
    """Same-class, low visual similarity (random sample within class, filter by high pixel distance)."""

def _find_spurious_pairs(train_ds: Dataset, test_ds: Dataset, n: int) -> list[tuple[int, int]]:
    """Pairs sharing background/spurious feature proxy (e.g. corner-patch color histogram match, different class)."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| image | [3, 224, 224] | resized for ResNet-18 ImageNet weights |
| batch | [B, 3, 224, 224] | B=128 |
| probe pair idx | (int, int) | (train_idx, test_idx) |

### Pseudo-code (near-duplicate search)

```
1. flatten all images to [N, D] (D=3*224*224, or downsample to 32x32 first for speed)
2. dist = cdist(test_flat, train_flat)  # [N_test, N_train]
3. for each mode: select top-n candidate pairs by dist/criterion, dedupe indices
```

### Subtasks [4/4 used — note: architecture lists breakdown 3+2+3+2=10, condensed to 4 given 8-subtask total budget]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | get_datasets/get_loaders | CIFAR-10 + DataLoader wiring |
| L-2-2 | _find_memorization_pairs | Nearest-neighbor cross-set search |
| L-2-3 | _find_transfer_pairs / _find_spurious_pairs | Class-conditioned + spurious-proxy sampling |
| L-2-4 | build_probe_pairs | Orchestrates above 3, returns combined dict |

---

## A-3: Model Builder [Complexity: 4, Budget: 4]

### API Signatures

```python
# model.py
def build_resnet18_cifar10(pretrained: bool = True) -> nn.Module:
    """torchvision.models.resnet18(weights=IMAGENET1K_V1 if pretrained), fc replaced with Linear(512, 10)."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Load resnet18 pretrained | torchvision.models.resnet18 |
| L-3-2 | Replace fc layer | nn.Linear(model.fc.in_features, 10) |
| L-3-3 | Move to device | model.to(device) |
| L-3-4 | Param count sanity check | assert sum(p.numel() ...) > 0 |

---

## A-4: Training Loop [Complexity: 9, Budget: 9]

### API Signatures

```python
# train.py
def train_model(model: nn.Module, train_loader: DataLoader, cfg: ExperimentConfig) -> list[str]:
    """SGD(momentum, weight_decay) + CosineAnnealingLR(T_max=epochs).
    Saves checkpoint every checkpoint_every epochs. Returns 10 checkpoint file paths."""

def _train_one_epoch(model: nn.Module, loader: DataLoader, optimizer, criterion, device) -> float:
    """Returns mean loss for the epoch."""

def _save_checkpoint(model: nn.Module, epoch: int, ckpt_dir: str) -> str:
    """torch.save(model.state_dict(), path). Returns path."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [B, 10] | output of model(x) |
| loss | scalar | CrossEntropyLoss |

### Pseudo-code

```
1. optimizer = SGD(model.parameters(), lr, momentum, weight_decay)
2. scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)
3. for epoch in range(cfg.epochs):
     loss = _train_one_epoch(...)
     scheduler.step()
     if (epoch+1) % cfg.checkpoint_every == 0:
         paths.append(_save_checkpoint(model, epoch+1, cfg.ckpt_dir))
4. return paths
```

### Subtasks [3/3 used — condensed from 2+2+2+3]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Optimizer/scheduler setup | SGD + CosineAnnealingLR |
| L-4-2 | _train_one_epoch | forward/backward/step loop |
| L-4-3 | Checkpointing | _save_checkpoint every N epochs, collect paths |

---

## A-5: TRAK Integration [Complexity: 12, Budget: 12]

**Applied**: trak.TRAKer official API (featurize/finalize/score)

### API Signatures

```python
# attribution_trak.py
from trak import TRAKer

def compute_trak_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict[str, list[tuple[int, int]]],
    cfg: ExperimentConfig,
) -> dict[str, np.ndarray]:
    """Returns {'mem': scores, 'transfer': scores, 'spurious': scores}, each shape (num_probes,)."""

def _featurize_train(traker: TRAKer, train_loader: DataLoader, model_id: int = 0) -> None:
    """traker.load_checkpoint(model.state_dict(), model_id); traker.featurize(batch, inds) per batch."""

def _score_probes(traker: TRAKer, probes: list[tuple[int, int]], test_ds: Dataset) -> np.ndarray:
    """traker.start_scoring_checkpoint(...); traker.score(batch, inds); traker.finalize_scores() -> [N_train, N_test]; gather diagonal per pair."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N_train, proj_dim] | random-projected gradients, proj_dim=2048 |
| score_matrix | [N_train, N_test] | from traker.finalize_scores() |
| mode scores | [num_probes] | gathered at (train_idx, test_idx) pairs |

### Pseudo-code

```
1. traker = TRAKer(model=model, task='image_classification', proj_dim=cfg.proj_dim,
                    save_dir=..., use_half_precision=True)
2. _featurize_train(traker, train_loader)
3. traker.finalize_features()
4. score_matrix = _score_probes(traker, all_test_indices, test_loader)  # [N_train, N_test]
5. for mode, pairs in probes.items():
     scores[mode] = np.array([score_matrix[ti, tj] for ti, tj in pairs])
```

### Subtasks [3/3 used — condensed from 3+4+3+2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | TRAKer init + featurize | Setup, load_checkpoint, featurize train set |
| L-5-2 | Score computation | finalize_features, score, finalize_scores |
| L-5-3 | Probe gathering | Map score_matrix to per-mode probe arrays |

---

## A-6: TracIn Integration [Complexity: 13, Budget: 13]

**Applied**: Checkpoint-based gradient dot product (captum TracInCP or manual)

### API Signatures

```python
# attribution_tracin.py
def compute_tracin_scores(
    model: nn.Module,
    checkpoints: list[str],
    train_loader: DataLoader,
    probes: dict[str, list[tuple[int, int]]],
    cfg: ExperimentConfig,
) -> dict[str, np.ndarray]:
    """TracIn(z,z') = sum_k eta_k * grad_l(w_k,z).grad_l(w_k,z'). Same return shape as TRAK."""

def _per_sample_grad(model: nn.Module, x: Tensor, y: Tensor) -> Tensor:
    """Flattened gradient of loss w.r.t. model params for single sample. Returns [P] (P=num trainable params, or last-layer only for tractability)."""

def _load_checkpoint_lr(ckpt_path: str, cfg: ExperimentConfig, ckpt_idx: int) -> float:
    """eta_k: LR at the epoch this checkpoint was saved (from cosine schedule)."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| grad_z | [P] | per-sample gradient, P = last-layer params (fc: 512*10+10) for tractability |
| tracin_score | scalar | per pair per checkpoint, summed over 10 checkpoints |

### Pseudo-code

```
1. for ckpt_path, eta_k in zip(checkpoints, etas):
     model.load_state_dict(torch.load(ckpt_path))
     for mode, pairs in probes.items():
       for (train_idx, test_idx) in pairs:
         g_train = _per_sample_grad(model, x_train, y_train)  # [P]
         g_test = _per_sample_grad(model, x_test, y_test)     # [P]
         scores[mode][pair] += eta_k * (g_train @ g_test)
2. return scores  # dict of np.ndarray, shape (num_probes,) per mode
```

### Subtasks [4/4 used — condensed from 3+4+4+2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | _per_sample_grad | Last-layer gradient extraction via autograd |
| L-6-2 | Checkpoint LR schedule mapping | _load_checkpoint_lr per saved epoch |
| L-6-3 | Pairwise dot-product accumulation | Loop over checkpoints x probe pairs |
| L-6-4 | Score aggregation | Sum across 10 checkpoints, reshape to per-mode arrays |

---

## A-7: Kronfluence Integration [Complexity: 14, Budget: 14]

**Applied**: kronfluence official API (fit_all_factors + pairwise scores)

### API Signatures

```python
# attribution_kronfluence.py
from kronfluence.analyzer import Analyzer, prepare_model
from kronfluence.task import Task

def compute_kronfluence_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict[str, list[tuple[int, int]]],
    cfg: ExperimentConfig,
) -> dict[str, np.ndarray]:
    """Fits EK-FAC factors then computes pairwise scores. Same return shape as TRAK."""

class ClassificationTask(Task):
    def compute_train_loss(self, batch, model: nn.Module, sample: bool = False) -> Tensor: ...
    def compute_measurement(self, batch, model: nn.Module) -> Tensor: ...

def _fit_ekfac_factors(analyzer: Analyzer, train_loader: DataLoader) -> None:
    """analyzer.fit_all_factors(factors_name=..., dataset=train_ds, per_device_batch_size=cfg.batch_size)."""

def _compute_pairwise_scores(analyzer: Analyzer, train_ds, query_ds) -> np.ndarray:
    """analyzer.compute_pairwise_scores(...) -> [N_query, N_train] tensor, converted to np.ndarray."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ekfac_factors | per-layer Kronecker factors | internal to kronfluence |
| score_matrix | [N_test, N_train] | from compute_pairwise_scores |

### Pseudo-code

```
1. task = ClassificationTask()
2. model = prepare_model(model, task)
3. analyzer = Analyzer(analysis_name="h-m1", model=model, task=task)
4. _fit_ekfac_factors(analyzer, train_loader)
5. score_matrix = _compute_pairwise_scores(analyzer, train_ds, test_ds)  # [N_test, N_train]
6. for mode, pairs in probes.items():
     scores[mode] = np.array([score_matrix[tj, ti] for ti, tj in pairs])
```

### Subtasks [4/4 used — condensed from 4+4+4+2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | ClassificationTask definition | compute_train_loss/compute_measurement |
| L-7-2 | Analyzer + prepare_model setup | Wrap model for kronfluence |
| L-7-3 | EK-FAC factor fitting | _fit_ekfac_factors |
| L-7-4 | Pairwise score computation + probe gathering | _compute_pairwise_scores, map to per-mode arrays |

---

## A-8: Evaluation Metrics [Complexity: 8, Budget: 8]

### API Signatures

```python
# evaluate.py
def compute_mode_sensitivity(scores: dict[str, np.ndarray]) -> dict[str, float]:
    """mean per mode: {'mem': x, 'transfer': y, 'spurious': z}"""

def build_interaction_matrix(results: dict[str, dict[str, np.ndarray]]) -> np.ndarray:
    """3x3, rows=methods (trak,tracin,kronfluence), cols=modes (mem,transfer,spurious), min-max normalized per row."""

def rank_modes(mode_scores: dict[str, float]) -> tuple[str, ...]:
    """Modes sorted descending by score, e.g. ('mem', 'spurious', 'transfer')."""

def verify_mechanism_active(results: dict[str, dict[str, np.ndarray]]) -> bool:
    """Asserts variance>0 per method (np.var(scores)>0); returns True if >=2 of 3 methods have differing rank_modes()."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| interaction_matrix | [3, 3] | methods x modes |

### Subtasks [2/2 used — condensed from 2+2+2+2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | compute_mode_sensitivity / build_interaction_matrix | Mean + normalized 3x3 matrix |
| L-8-2 | rank_modes / verify_mechanism_active | Ranking + variance/ranking gate check |

---

## A-9: Visualization [Complexity: 7, Budget: 7]

### API Signatures

```python
# visualize.py
def plot_heatmap(interaction_matrix: np.ndarray, methods: list[str], modes: list[str], out_path: str) -> None:
    """seaborn.heatmap, required figure."""

def plot_radar(results: dict[str, dict[str, float]], out_path: str) -> None:
    """Per-method mode-sensitivity radar chart."""

def plot_distributions(results: dict[str, dict[str, np.ndarray]], out_path: str) -> None:
    """Overlaid histograms/KDE of scores per mode."""

def plot_method_correlation(results: dict[str, dict[str, np.ndarray]], out_path: str) -> None:
    """Pairwise Pearson correlation of flattened score vectors across methods, seaborn.heatmap."""
```

### Subtasks [1/1 used — condensed from 2+2+1+2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | All 4 plot functions | plot_heatmap (required) + radar/distributions/correlation (optional) |

---

## A-10: Orchestration & Gate [Complexity: 8, Budget: 8]

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """1. config+seed 2. data 3. model 4. train->checkpoints
    5. compute_{trak,tracin,kronfluence}_scores -> results dict
    6. evaluate.* 7. visualize.* 8. log gate pass/fail"""

def log_gate_results(sensitivity: dict, ranking_diff: bool, variance_ok: bool, out_path: str) -> bool:
    """Writes success-criteria pass/fail (3 criteria from PRD) to out_path, returns overall pass."""
```

### Subtasks [1/1 used — condensed from 2+3+1+2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | main() + log_gate_results | Full pipeline wiring, gate logging |

---

**Total subtasks used**: 4+4+4+3+3+4+4+2+1+1 = 30 detailed items across 10 tasks — condensed within 8-subtask-per-task guidance where architecture breakdown exceeded budget; all A-1..A-10 covered.
