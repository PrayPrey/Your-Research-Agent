# Logic: H-E1 (EXISTENCE PoC)

**Hypothesis:** CV of probe accuracy trajectories distinguishes spurious from core features (AUC >= 0.75)

Applied: feature-cache-then-probe pattern (extract CLIP features once, reuse across probing sweeps)
Applied: sklearn-linear-probe pattern (LogisticRegression C-sweep as training-trajectory proxy)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze; designing new APIs from scratch
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Flow

```
download_waterbirds -> load_metadata -> WaterbirdsDataset
  -> extract_features (CLIP) -> cache_features [N,512]
  -> run_cv_analysis(background) -> background_cv: float
  -> run_cv_analysis(bird_type)  -> bird_type_cv: float
  -> compute_metrics([cv_bg, cv_bird], [1, 0]) -> {auc, best_f1}
  -> check_gate(metrics, 0.75) -> bool
  -> visualize.* -> figures/*.png
  -> results.yaml
```

---

## data.py

```python
def download_waterbirds(data_dir: str) -> str:
    """Download+extract tar if missing. Returns dataset root path."""
    ...

def load_metadata(data_dir: str) -> "pd.DataFrame":
    """Read metadata.csv (img_filename, y, place, split)."""
    ...

class WaterbirdsDataset:
    def __init__(self, data_dir: str, split: str, preprocess):
        """split: 'train'|'val'|'test'. preprocess: CLIP preprocess transform."""
        ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple:
        """Returns (image: Tensor [3,224,224], y: int, place: int)."""
        ...
```

---

## features.py

```python
def load_clip_model(device: str) -> tuple:
    """Returns (model, preprocess). clip.load('ViT-B/16', device=device); model.eval()."""
    ...

def extract_features(
    dataset: "WaterbirdsDataset", model, device: str, batch_size: int = 100
) -> tuple:
    """DataLoader(shuffle=False) -> encode_image -> L2-normalize.
    Returns (features: np.ndarray [N,512], y: np.ndarray [N], place: np.ndarray [N])."""
    ...

def cache_features(path: str, features: "np.ndarray", y: "np.ndarray", place: "np.ndarray") -> None:
    """np.savez(path, features=features, y=y, place=place)."""
    ...

def load_cached_features(path: str) -> tuple:
    """np.load(path) -> (features, y, place). Raises FileNotFoundError if absent."""
    ...
```

---

## cv_probe.py

**Applied**: sklearn-linear-probe pattern (C-sweep as epoch-trajectory proxy)

```python
def compute_cv_for_feature(
    features: "np.ndarray",   # [N, 512]
    labels: "np.ndarray",     # [N] binary (0/1)
    n_subsets: int = 5,
    subset_frac: float = 0.2,
    n_epochs: int = 10,
    seed: int = 42,
) -> float:
    """Returns CV = std(improvement_rates) / (mean(improvement_rates) + 1e-8)."""
    ...

def run_cv_analysis(
    features: "np.ndarray",       # [N, 512]
    y_labels: "np.ndarray",       # [N] bird_type (core)
    place_labels: "np.ndarray",   # [N] background (spurious)
) -> dict:
    """Calls compute_cv_for_feature for background and bird_type.
    Returns {"background_cv": float, "bird_type_cv": float,
             "trajectories": {"background": [n_subsets x n_epochs], "bird_type": [...]}}."""
    ...
```

### Pseudo-code: compute_cv_for_feature

```
rng = RandomState(seed)
subset_size = int(N * subset_frac)
C_values = logspace(-3, 2, n_epochs)   # 0.001 -> 100
trajectories = []                       # [n_subsets, n_epochs]

for s in range(n_subsets):
    idx = rng.choice(N, subset_size, replace=False)
    X, y = features[idx], labels[idx]
    accs = []
    for C in C_values:
        clf = LogisticRegression(C=C, max_iter=1000, random_state=seed, solver="lbfgs")
        clf.fit(X, y)
        accs.append(clf.score(X, y))
    trajectories.append(accs)

improvement_rates = [traj[-1] - traj[0] for traj in trajectories]
cv = std(improvement_rates) / (mean(improvement_rates) + 1e-8)
return cv, trajectories   # trajectories exposed via run_cv_analysis
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N, 512] | CLIP ViT-B/16 output, L2-normalized |
| labels | [N] | binary per probed concept |
| trajectories | [n_subsets=5, n_epochs=10] | accuracy per C checkpoint |
| improvement_rates | [n_subsets=5] | final_acc - initial_acc |

---

## evaluate.py

```python
def compute_metrics(cv_values: list, ground_truth_spurious: list) -> dict:
    """scores = -np.array(cv_values) (lower CV -> more spurious).
    Returns {"auc": roc_auc_score(...), "best_f1": max F1 over PR curve}."""
    ...

def check_gate(metrics: dict, threshold: float = 0.75) -> bool:
    """Returns metrics["auc"] >= threshold."""
    ...
```

---

## visualize.py

```python
def plot_gate_comparison(auc: float, threshold: float, out_path: str) -> None:
    """Bar chart: AUC vs threshold line. Required figure."""
    ...

def plot_cv_distribution(cv_values: dict, out_path: str) -> None:
    """cv_values: {"background": float, "bird_type": float}. Bar/hist overlay."""
    ...

def plot_roc_curve(cv_values: list, ground_truth: list, out_path: str) -> None:
    """roc_curve(ground_truth, -np.array(cv_values)) -> plot with AUC annotation."""
    ...

def plot_trajectories(trajectories: dict, out_path: str) -> None:
    """trajectories: {"background": [5,10], "bird_type": [5,10]}. Line plot per subset, colored by feature type."""
    ...
```

---

## run_experiment.py

```python
def main(config_path: str = "config.yaml") -> None:
    """
    1. cfg = yaml.safe_load(config_path)
    2. root = download_waterbirds(cfg.data_dir); meta = load_metadata(root)
    3. model, preprocess = load_clip_model(device)
       ds = WaterbirdsDataset(root, "train", preprocess)
       if cache exists: features, y, place = load_cached_features(cache_path)
       else: features, y, place = extract_features(ds, model, device, cfg.batch_size); cache_features(...)
    4. result = run_cv_analysis(features, y, place)
    5. metrics = compute_metrics(
           [result["background_cv"], result["bird_type_cv"]], [1, 0])
       gate_pass = check_gate(metrics, cfg.auc_threshold)
    6. plot_gate_comparison(...); plot_cv_distribution(...); plot_roc_curve(...); plot_trajectories(...)
    7. yaml.dump({"auc": metrics["auc"], "best_f1": metrics["best_f1"],
                  "gate_pass": gate_pass, "background_cv": ..., "bird_type_cv": ...}, results.yaml)
    """
    ...
```

---

## Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1 | Data + feature API | `data.py`, `features.py` signatures, cache format |
| L-2 | CV algorithm | `compute_cv_for_feature` pseudo-code, subset/C-sweep logic |
| L-3 | Eval + gate API | `evaluate.py` AUC/F1/gate signatures |
| L-4 | Visualize + orchestration API | `visualize.py` 4 figures, `run_experiment.py` pipeline steps |
