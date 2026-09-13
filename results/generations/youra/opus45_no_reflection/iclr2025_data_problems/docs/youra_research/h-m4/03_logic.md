# Logic: H-M4

**Scope:** High-complexity modules only — A-3 (EK-FAC), A-4 (TracIn), A-5 (TRAK)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M3), but no importable code exists on disk (`h-m3/code/` not found — only spec). Confirmed by architecture.md's own analysis.
**Status:** Green-field for actual API — no real code to verify signatures against. Following `03_architecture.md` conventions (same as H-M3 spec) for consistency.
**Analyzed Path:** N/A (no code directory)
**Relevant Symbols:** None — new implementation

---

## A-3: EK-FAC Budget Sweep [Complexity: 15, Budget: 15]

**Applied:** Standard PyTorch + kronfluence Analyzer pattern (KB search returned no direct EK-FAC examples; using PRD-specified kronfluence API)

### API Signatures

```python
# ekfac_attribution.py
from kronfluence import Analyzer
from kronfluence.task import ClassificationTask
import time

def build_analyzer(model: nn.Module, analysis_name: str) -> Analyzer:
    """Wraps model in kronfluence Analyzer with ClassificationTask."""
    ...

def compute_ekfac_scores(
    model: nn.Module,
    task: ClassificationTask,
    train_loader: DataLoader,
    query_loader: DataLoader,
    proj_dim: int,
) -> np.ndarray:
    """Fit EK-FAC factors + compute influence. Returns [N_query, N_train] or self-influence [N_train]."""
    ...

def run_ekfac_budget_sweep(
    model: nn.Module,
    task: ClassificationTask,
    train_loader: DataLoader,
    query_loader: DataLoader,
    proj_dims: list[int],
) -> dict[int, tuple[np.ndarray, float]]:
    """Sweep proj_dims=[64,128,256,512,1024]. Returns {proj_dim: (scores, wall_time_sec)}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores (pairwise) | [N_query, N_train] | full influence matrix |
| scores (self-influence, used for mislabel AUC) | [N_train] | diagonal-equivalent; query_loader == train subset for self-influence |
| proj_dim | scalar int | EK-FAC low-rank projection rank, controls compute budget |

### Pseudo-code

```
for proj_dim in [64, 128, 256, 512, 1024]:
    t0 = time.time()
    analyzer = Analyzer(model, task=task)
    analyzer.set_projection_dim(proj_dim)
    analyzer.fit(train_loader)                     # fits EK-FAC factors (Kronecker-factored curvature)
    scores = analyzer.compute_influence_scores(train_loader, query_loader)  # [N_train] self-influence
    wall_time = time.time() - t0
    results[proj_dim] = (scores, wall_time)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `build_analyzer` | Wrap model+task, configure ClassificationTask for BERT/GPT-2 logits |
| L-3-2 | `compute_ekfac_scores` | Single proj_dim: fit factors, compute self-influence scores |
| L-3-3 | `run_ekfac_budget_sweep` | Loop 5 proj_dims, wrap each in `time.time()` timing, collect dict |
| L-3-4 | Arch dispatch in `run_experiment.py` | Call sweep once per arch (bert, gpt2), store under `results[arch]["ekfac"]` |

---

## A-4: TracIn Budget Sweep [Complexity: 14, Budget: 14]

**Applied:** dattri TracInCPFast wrapper pattern (per PRD/brief reference API)

### API Signatures

```python
# tracin_attribution.py
from dattri.attributors import TracInCPFast
import time

def compute_tracin_scores(
    model: nn.Module,
    checkpoint_paths: list[str],
    query_loader: DataLoader,
    train_loader: DataLoader,
    lr: float,
    device: str,
) -> np.ndarray:
    """TracInCPFast over given checkpoints. Returns self-influence scores [N_train]."""
    ...

def select_checkpoint_subset(all_ckpts: list[str], n: int) -> list[str]:
    """Evenly-spaced subset of n checkpoints from all_ckpts (budget knob)."""
    ...

def run_tracin_budget_sweep(
    model: nn.Module,
    all_checkpoint_paths: list[str],
    query_loader: DataLoader,
    train_loader: DataLoader,
    lr: float,
    device: str,
    budget_to_ckpt_count: dict[int, int],
) -> dict[int, tuple[np.ndarray, float]]:
    """Maps 5 budget levels (proj_dim-equivalent labels 64..1024) to checkpoint-subset sizes.
    Returns {budget: (scores, wall_time_sec)}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | [N_train] | self-influence via summed per-checkpoint gradient dot-products |
| checkpoint_paths | list[str], len = n_checkpoints | budget controls how many checkpoints included (more ckpts = more compute) |

### Pseudo-code

```
# budget_to_ckpt_count e.g. {64:1, 128:2, 256:3, 512:4, 1024:5} (config.tracin_checkpoint_counts)
for budget, n_ckpt in budget_to_ckpt_count.items():
    t0 = time.time()
    ckpts = select_checkpoint_subset(all_checkpoint_paths, n_ckpt)
    attributor = TracInCPFast(model, train_loader, checkpoint_paths=ckpts)
    scores = attributor.attribute(query_loader)     # aggregated across ckpts -> [N_train]
    wall_time = time.time() - t0
    results[budget] = (scores, wall_time)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `select_checkpoint_subset` | Evenly-spaced index selection over saved epoch checkpoints |
| L-4-2 | `compute_tracin_scores` | Single-budget TracInCPFast call, self-influence over train set |
| L-4-3 | `run_tracin_budget_sweep` | Loop 5 budget levels via `budget_to_ckpt_count`, time each, collect dict |
| L-4-4 | Config wiring | Populate `config.tracin_checkpoint_counts` mapping 5 proj-dim-labels -> ckpt counts (1-5) |

---

## A-5: TRAK Budget Sweep [Complexity: 14, Budget: 14]

**Applied:** traker TRAKer featurize/score pattern (per PRD/brief reference API)

### API Signatures

```python
# trak_attribution.py
from trak import TRAKer
import time

def compute_trak_scores(
    model: nn.Module,
    task: str,
    train_loader: DataLoader,
    query_loader: DataLoader,
    proj_dim: int,
    seed: int,
    train_set_size: int,
) -> np.ndarray:
    """Featurize train set, score against query. Returns self-influence [N_train]."""
    ...

def run_trak_budget_sweep(
    model: nn.Module,
    task: str,
    train_loader: DataLoader,
    query_loader: DataLoader,
    seed: int,
    train_set_size: int,
    proj_dims: list[int],
) -> dict[int, tuple[np.ndarray, float]]:
    """Sweep proj_dims=[64,128,256,512,1024]. Returns {proj_dim: (scores, wall_time_sec)}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features (internal, TRAKer) | [N_train, proj_dim] | random-projected gradient features |
| scores | [N_train] | self-influence (train_loader used as both train and query for mislabel AUC) |

### Pseudo-code

```
for proj_dim in [64, 128, 256, 512, 1024]:
    t0 = time.time()
    traker = TRAKer(model, task=task, train_set_size=train_set_size, proj_dim=proj_dim, seed=seed)
    traker.featurize(loader=train_loader, batch_size=32)
    traker.finalize_features()
    scores = traker.score(targets=query_loader)     # -> [N_train]
    wall_time = time.time() - t0
    results[proj_dim] = (scores, wall_time)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | `compute_trak_scores` | Single proj_dim: featurize + finalize + score |
| L-5-2 | `run_trak_budget_sweep` | Loop 5 proj_dims, wrap in timing, collect dict |
| L-5-3 | Seed handling | Pass seed into TRAKer for reproducible random projections |
| L-5-4 | Arch dispatch in `run_experiment.py` | Call sweep once per arch, store under `results[arch]["trak"]` |

---

## Shared Timing Wrapper (used by all three)

```python
def timed(fn, *args, **kwargs) -> tuple[Any, float]:
    """Generic wall-clock wrapper: (result, elapsed_sec)."""
    t0 = time.time()
    result = fn(*args, **kwargs)
    return result, time.time() - t0
```

Each sweep function stores results as `dict[budget_level: int, tuple[np.ndarray, float]]`, consumed directly by `pareto.build_pareto_points()`.
