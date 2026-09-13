# Logic Design: H-E2

**Date:** 2026-08-26
**Hypothesis:** H-E2 — CelebA replication of H-E1 paradigm effect
**Tier:** LIGHT | **Budget:** 9 subtasks (A-3: 4, A-2: 3, A-5: 2)

Applied: dataset-agnostic probe pipeline (H-E1 modules imported unchanged)
Applied: group-balanced stratified sampler (4-group CelebA × attribute indices)
Applied: feature caching pattern (get_or_extract_features with cache_key)

---

## Codebase Analysis (Serena)

**Analyzed path:** `docs/youra_research/h-e1/code/` (manual read — no-MCP session)

**Findings:**

| File | Key Symbols | Notes |
|------|-------------|-------|
| `model_utils.py` | `extract_features(model, loader, device)`, `get_or_extract_features(model, loader, device, cache_key, cache_dir)`, `LOADERS` dict | `extract_features` expects batch `(x, y, metadata)` — H-E1 WILDS format. H-E2 must adapt: CelebA yields `(imgs, attrs)`, need wrapper loader |
| `probe_utils.py` | `compute_ratio(feats_val, task_lbls_val, spur_lbls_val, metadata_val, feats_test, task_lbls_test, spur_lbls_test, seed, paradigm)` | Internally calls `get_balanced_probe_indices(metadata_val, seed)` from H-E1 `data_utils` — **cannot reuse this call**; H-E2 balanced sampling uses CelebA attrs |
| `stats_utils.py` | `run_anova(ratios)`, `pairwise_tests(ratios, n_bonferroni)`, `check_gate(pair_results, alpha, min_diff)`, `export_results(...)` | Fully dataset-agnostic. Reuse verbatim. `ratios` is `dict[str, list[float]]` |
| `viz_utils.py` | `plot_ratio_bar(ratios, pair_results, out_dir)`, `plot_acc_heatmap(acc_records, out_dir)`, `plot_pvalue_matrix(pair_results, paradigms, out_dir)`, `plot_ratio_violin(ratios, out_dir)`, `_savefig(fig, out_dir, filename)` | All reusable. New function `plot_cross_dataset_bar` added in H-E2 |
| `config.py` | Module-level constants (plain, no dataclass) | H-E2 config.py overrides `DATA_ROOT`, `CACHE_DIR`, adds `BLOND_ATTR`, `MALE_ATTR`, `N_PER_GROUP` |

**Critical finding:** `probe_utils.compute_ratio` calls `get_balanced_probe_indices(metadata_val, seed)` internally — this is WILDS-specific (uses `metadata` tensor with group index at column 0). H-E2 cannot call `compute_ratio` directly. Must implement `compute_ratio_celeba` as a thin adaptation.

---

## External Dependencies API

**Verified from actual H-E1 code (not specs):**

```python
# model_utils.py
def get_or_extract_features(
    model,        # nn.Module, frozen, eval
    loader,       # DataLoader yielding (x, y, metadata) — NOTE: H-E2 wraps CelebA loader
    device,       # str | torch.device
    cache_key,    # str — filename stem for .pt cache
    cache_dir,    # str — defaults to config.CACHE_DIR
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # returns: (features (N,2048), task_lbls (N,), spur_lbls (N,))

LOADERS: dict[str, Callable[[device], nn.Module]]
# keys: 'erm', 'moco', 'dino', 'barlowtwins'

# stats_utils.py
def run_anova(ratios: dict[str, list[float]]) -> tuple[float, float]: ...
def pairwise_tests(ratios: dict[str, list[float]], n_bonferroni: int = 6) -> list[dict]: ...
def check_gate(pair_results: list[dict], alpha: float, min_diff: float) -> tuple[bool, list[dict]]: ...
def export_results(ratios, anova_result, pair_results, gate_ok, passing_pairs, out_path: str) -> None: ...

# viz_utils.py
def plot_ratio_bar(ratios: dict[str, list[float]], pair_results: list[dict], out_dir: str) -> None: ...
def plot_acc_heatmap(acc_records: list[dict], out_dir: str) -> None: ...
def plot_pvalue_matrix(pair_results: list[dict], paradigms: list[str], out_dir: str) -> None: ...
def plot_ratio_violin(ratios: dict[str, list[float]], out_dir: str) -> None: ...
```

---

## New Code: `data/celeba_loader.py`

### L-2-1: `get_celeba_loaders`

```python
def get_celeba_loaders(
    root: str,           # DATA_ROOT from config, e.g. './data'
    batch_size: int,     # BATCH_SIZE from config
    download: bool = True,
) -> tuple[DataLoader, CelebA]:
    """
    Returns (train_loader, test_dataset).
    train_loader: full CelebA train split, for feature extraction on training set.
    test_dataset: CelebA test split object (for balanced sampling in get_balanced_celeba_indices).

    Preprocessing: Resize(256) -> CenterCrop(224) -> ToTensor -> Normalize(ImageNet).
    Loader yields: (imgs: Tensor(B,3,224,224), attrs: Tensor(B,40))
    """
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    train_ds = CelebA(root=root, split='train', target_type='attr',
                      transform=transform, download=download)
    test_ds  = CelebA(root=root, split='test',  target_type='attr',
                      transform=transform, download=download)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=False,
                              num_workers=4, pin_memory=True)
    return train_loader, test_ds
```

**Tensor shapes:** imgs `(B, 3, 224, 224)`, attrs `(B, 40)` int tensor.

### L-2-2: `get_balanced_celeba_indices`

```python
def get_balanced_celeba_indices(
    dataset: CelebA,
    blond_attr: int,    # 9
    male_attr: int,     # 20
    n_per_group: int,   # 180
    seed: int,
) -> np.ndarray:
    """
    Returns indices (720,) sampling equal n from 4 groups:
      (blond=1,male=1), (blond=1,male=0), (blond=0,male=1), (blond=0,male=0)

    Pseudo-code:
      attrs = dataset.attr.numpy()  # (N, 40)
      blond = attrs[:, blond_attr]
      male  = attrs[:, male_attr]
      groups = {
          (1,1): where(blond==1 & male==1),
          (1,0): where(blond==1 & male==0),
          (0,1): where(blond==0 & male==1),
          (0,0): where(blond==0 & male==0),
      }
      n = min(n_per_group, min(len(g) for g in groups.values()))
      rng = np.random.default_rng(seed)
      idx = concat([rng.choice(g, n, replace=False) for g in groups.values()])
      assert len(idx) == n * 4
      return idx
    """
```

**Assert:** `assert len(idx) == n * 4, f"Balanced test size wrong: {len(idx)}"`

### L-2-3: `get_balanced_test_loader`

```python
def get_balanced_test_loader(
    dataset: CelebA,
    indices: np.ndarray,    # (720,) from get_balanced_celeba_indices
    batch_size: int,
) -> tuple[DataLoader, np.ndarray, np.ndarray]:
    """
    Returns (loader, task_labels, spur_labels) for the balanced subset.
    task_labels: attrs[indices, blond_attr]  shape (720,)
    spur_labels: attrs[indices, male_attr]   shape (720,)
    loader: Subset DataLoader yielding (imgs, attrs) for the 720 balanced samples
    """
```

---

## New Code: `run_experiment.py`

### L-3-1: `sys.path injection` (module-level)

```python
# At top of run_experiment.py, before any H-E1 imports:
import sys, os
H_E1_CODE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../h-e1/code')
)
sys.path.insert(0, H_E1_CODE)

# Then import H-E1 modules:
from model_utils import get_or_extract_features, LOADERS
from stats_utils import run_anova, pairwise_tests, check_gate, export_results
import viz_utils
```

**Verified:** H-E1 `model_utils.py` is a plain module (no package `__init__`); `sys.path.insert` is the correct import mechanism.

### L-3-2: `extract_features_celeba` (adapter)

```python
def extract_features_celeba(
    model: nn.Module,
    loader: DataLoader,    # yields (imgs: Tensor(B,3,224,224), attrs: Tensor(B,40))
    device: str,
    blond_attr: int,       # 9
    male_attr: int,        # 20
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Adapter: wraps CelebA loader to match H-E1 extract_features return contract.
    Returns: (features (N,2048), task_lbls (N,) Blond_Hair, spur_lbls (N,) Male)

    Cannot reuse H-E1 extract_features directly (expects (x, y, metadata) batches).

    Pseudo-code:
      feats, task_lbls, spur_lbls = [], [], []
      with torch.no_grad():
          for imgs, attrs in loader:
              f = model(imgs.to(device))       # (B, 2048)
              feats.append(f.cpu())
              task_lbls.append(attrs[:, blond_attr])
              spur_lbls.append(attrs[:, male_attr])
      features = cat(feats)                    # (N, 2048)
      assert features.shape[1] == 2048
      return features, cat(task_lbls).long(), cat(spur_lbls).long()
    """
```

**Tensor shapes:** features `(N, 2048)`, labels `(N,)` int64.

### L-3-3: `compute_ratio_celeba`

```python
def compute_ratio_celeba(
    feats_train: torch.Tensor,      # (N_train, 2048)
    task_lbls_train: torch.Tensor,  # (N_train,)
    spur_lbls_train: torch.Tensor,  # (N_train,)
    feats_test: torch.Tensor,       # (720, 2048) balanced
    task_lbls_test: torch.Tensor,   # (720,)
    spur_lbls_test: torch.Tensor,   # (720,)
    seed: int,
    paradigm: str,
) -> dict:
    """
    Thin adaptation of H-E1 probe_utils logic for CelebA.
    Cannot call probe_utils.compute_ratio directly (WILDS-specific internals).

    Returns: {'ratio': float, 'spurious_acc': float, 'task_acc': float, 'paradigm': str, 'seed': int}

    Pseudo-code:
      np.random.seed(seed); torch.manual_seed(seed)
      # Train probes on full train features (not group-balanced for training)
      X_tr = feats_train.numpy()
      clf_task = LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs').fit(X_tr, task_lbls_train.numpy())
      clf_spur = LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs').fit(X_tr, spur_lbls_train.numpy())
      # Evaluate on balanced test
      X_te = feats_test.numpy()
      acc_task = clf_task.score(X_te, task_lbls_test.numpy())
      acc_spur = clf_spur.score(X_te, spur_lbls_test.numpy())
      assert acc_task > 0.5, f"Degenerate probe: task_acc={acc_task}"
      assert acc_spur > 0.5, f"Degenerate probe: spur_acc={acc_spur}"
      ratio = acc_spur / acc_task
      log: "CelebA: paradigm={paradigm}, seed={seed}, task_acc={acc_task:.4f}, spur_acc={acc_spur:.4f}, ratio={ratio:.4f}"
      return {'ratio': ratio, 'spurious_acc': acc_spur, 'task_acc': acc_task, 'paradigm': paradigm, 'seed': seed}
    """
```

### L-3-4: `main` orchestration loop

```python
def main(device: str | None = None) -> None:
    """
    Pseudo-code:
      device = device or ('cuda' if cuda.is_available() else 'cpu')
      setup_logging()

      train_loader, test_ds = get_celeba_loaders(DATA_ROOT, BATCH_SIZE)

      ratios: dict[str, list[float]] = {p: [] for p in PARADIGMS}
      acc_records: list[dict] = []

      for paradigm in PARADIGMS:
          model = LOADERS[paradigm](device)

          # Feature extraction (cached per paradigm)
          feats_train, task_tr, spur_tr = extract_features_celeba(
              model, train_loader, device, BLOND_ATTR, MALE_ATTR
          )
          # Cache test features once (balanced indices vary per seed but features don't)
          test_full_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)
          feats_test_full, _, _ = extract_features_celeba(
              model, test_full_loader, device, BLOND_ATTR, MALE_ATTR
          )

          for seed in SEEDS:
              bal_idx = get_balanced_celeba_indices(test_ds, BLOND_ATTR, MALE_ATTR, N_PER_GROUP, seed)
              task_te = test_ds.attr[bal_idx, BLOND_ATTR].long()
              spur_te = test_ds.attr[bal_idx, MALE_ATTR].long()
              feats_te = feats_test_full[bal_idx]

              result = compute_ratio_celeba(
                  feats_train, task_tr, spur_tr,
                  feats_te, task_te, spur_te,
                  seed, paradigm,
              )
              ratios[paradigm].append(result['ratio'])
              acc_records.append(result)

      anova_result = run_anova(ratios)
      pair_results = pairwise_tests(ratios)
      gate_ok, passing = check_gate(pair_results, GATE_ALPHA, GATE_MIN_DIFF)
      export_results(ratios, anova_result, pair_results, gate_ok, passing,
                     os.path.join(RESULTS_DIR, 'stats.json'))

      # Visualizations (H-E1 functions reused, new cross-dataset figure)
      viz_utils.plot_ratio_bar(ratios, pair_results, FIGURES_DIR)
      viz_utils.plot_acc_heatmap(acc_records, FIGURES_DIR)
      viz_utils.plot_pvalue_matrix(pair_results, PARADIGMS, FIGURES_DIR)
      viz_utils.plot_ratio_violin(ratios, FIGURES_DIR)
      plot_cross_dataset_bar(ratios, FIGURES_DIR)   # new in H-E2

      return gate_ok, ratios, pair_results
    """
```

---

## Subtask: A-4 (Cross-Dataset Figure)

### `plot_cross_dataset_bar` (new in H-E2)

```python
def plot_cross_dataset_bar(
    ratios_celeba: dict[str, list[float]],  # H-E2 ratios
    out_dir: str,
    h_e1_means: dict[str, float] | None = None,  # precomputed H-E1 means
) -> None:
    """
    Grouped bar chart: 4 paradigms × 2 datasets (Waterbirds, CelebA).
    H-E1 means: {'erm': 1.052, 'moco': 1.027, 'dino': 1.050, 'barlowtwins': 1.033}
    (hardcoded from H-E1 validated results if h_e1_means not provided)

    Pseudo-code:
      if h_e1_means is None:
          h_e1_means = {'erm': 1.052, 'moco': 1.027, 'dino': 1.050, 'barlowtwins': 1.033}
      celeba_means = {p: np.mean(ratios_celeba[p]) for p in PARADIGMS}
      celeba_stds  = {p: np.std(ratios_celeba[p], ddof=1) for p in PARADIGMS}
      # grouped bar: x = paradigm positions, offset bars by dataset
      # save as 'cross_dataset_bar.png'
    """
```

---

## Validation Logic: A-5

### L-5-1: Gate evaluation schema

```python
# Gate result dict (returned by check_gate, saved in stats.json):
gate_result = {
    'satisfied': bool,                   # True if ≥1 pair passes
    'passing_pairs': list[str],          # e.g. ['erm_vs_moco']
    'anova_f': float,
    'anova_p': float,
    'n_significant_pairs': int,
}
```

### L-5-2: Results CSV schema

```python
# Per-run record (acc_records list → saved as results.csv):
record = {
    'paradigm': str,        # 'erm' | 'moco' | 'dino' | 'barlowtwins'
    'seed': int,            # 0-4
    'task_acc': float,      # Blond_Hair probe accuracy on balanced test
    'spurious_acc': float,  # Male probe accuracy on balanced test
    'ratio': float,         # spurious_acc / task_acc
    'dataset': 'celeba',    # literal string for H-D1 cross-dataset join
}
# Save: pd.DataFrame(acc_records).to_csv(RESULTS_DIR + '/results.csv', index=False)
```

---

## Subtask Index

| ID | Title | Parent Epic | File |
|----|-------|-------------|------|
| L-2-1 | `get_celeba_loaders` API | A-2 | `data/celeba_loader.py` |
| L-2-2 | `get_balanced_celeba_indices` pseudo-code | A-2 | `data/celeba_loader.py` |
| L-2-3 | `get_balanced_test_loader` API | A-2 | `data/celeba_loader.py` |
| L-3-1 | `sys.path` injection pattern | A-3 | `run_experiment.py` |
| L-3-2 | `extract_features_celeba` adapter | A-3 | `run_experiment.py` |
| L-3-3 | `compute_ratio_celeba` adaptation | A-3 | `run_experiment.py` |
| L-3-4 | `main` orchestration pseudo-code | A-3 | `run_experiment.py` |
| L-5-1 | Gate result schema | A-5 | `stats_utils` / `stats.json` |
| L-5-2 | Results CSV schema | A-5 | `results.csv` |
