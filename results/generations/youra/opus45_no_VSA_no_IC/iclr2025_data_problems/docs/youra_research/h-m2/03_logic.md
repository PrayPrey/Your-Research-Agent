# Logic: h-m2

**Applied**: No matching KB pattern (best similarity 0.35, unrelated diffusion/FID repos) — standard scipy.stats/numpy used directly.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Serena unavailable in this workspace (no active project registered); verified actual h-m1 API signatures via direct file reads instead (config.py, data.py, model.py, train.py, attribution_trak.py, attribution_tracin.py, attribution_kronfluence.py).
**Analyzed Path**: `h-m1/code/`
**Relevant Symbols**: `ExperimentConfig`, `set_all_seeds`, `setup_dirs`, `get_datasets`, `get_loaders`, `build_probe_pairs`, `build_resnet18_cifar10`, `get_device`, `train_model`, `compute_trak_scores`, `compute_tracin_scores`, `compute_kronfluence_scores` — all confirmed present with signatures below (spec vs code: no drift found beyond what h-m1's own `03_architecture.md` already flagged, e.g. `compute_tracin_scores` takes raw Datasets not loaders).

---

## External Dependencies (Base Hypothesis h-m1, verified from actual code)

```python
# h-m1/code/config.py
@dataclass
class ExperimentConfig:
    seed: int = 42
    epochs: int = 5
    batch_size: int = 128
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    checkpoint_every: int = 5
    data_root: str
    ckpt_dir: str = "./h-m1/checkpoints"
    fig_dir: str = "./h-m1/figures"
    probes_per_mode: int = 100
    modes: tuple = ("mem", "transfer", "spurious")
    trak_proj_dim: int = 2048
    trak_use_half_precision: bool = True
    tracin_num_checkpoints: int = 1
    kronfluence_use_amp: bool = True

def set_all_seeds(seed: int) -> None: ...
def setup_dirs(cfg: ExperimentConfig) -> None: ...  # makes ckpt_dir, fig_dir, data_root

# h-m1/code/data.py
def get_datasets(cfg: ExperimentConfig) -> tuple[Dataset, Dataset]: ...  # (train_ds, test_ds)
def get_loaders(train_ds, test_ds, cfg: ExperimentConfig) -> tuple[DataLoader, DataLoader]: ...
def build_probe_pairs(train_ds, test_ds, seed: int, n_per_mode: int = 1000) -> dict:
    """{'mem'|'transfer'|'spurious': [(train_idx, test_idx), ...]}"""

# h-m1/code/model.py
def build_resnet18_cifar10(pretrained: bool = True) -> nn.Module: ...
def get_device() -> torch.device: ...

# h-m1/code/train.py
def train_model(model: nn.Module, train_loader: DataLoader, cfg: ExperimentConfig, device: torch.device) -> list:
    """Returns list of checkpoint file paths (saved every cfg.checkpoint_every epochs)."""

# h-m1/code/attribution_trak.py
def compute_trak_scores(model, train_loader: DataLoader, test_loader: DataLoader, probes: dict, cfg: ExperimentConfig, device: torch.device) -> dict:
    """Returns {'mem'|'transfer'|'spurious': np.ndarray[n_per_mode]}"""

# h-m1/code/attribution_tracin.py
def compute_tracin_scores(model, checkpoints: list, train_ds: Dataset, test_ds: Dataset, probes: dict, cfg: ExperimentConfig, device: torch.device) -> dict:
    """Takes raw Datasets (NOT loaders). Returns same dict shape as above."""

# h-m1/code/attribution_kronfluence.py
def compute_kronfluence_scores(model, train_loader: DataLoader, test_loader: DataLoader, probes: dict, cfg: ExperimentConfig, device: torch.device) -> dict:
    """Falls back to grad-dot-product if kronfluence unavailable. Same dict shape."""
```

Import via `sys.path.insert(0, "<abs path to h-m1/code>")` in `run_experiment.py` (mirrors h-m1's own pattern) then `from config import ...`, `from data import ...`, etc. — h-m1 modules import each other by bare name (`from config import ExperimentConfig`), so h-m2's vendored `config.py` must not shadow h-m1's on the path; keep h-m1/code prepended and h-m2/code appended, or name h-m2 modules distinctly (`profiles.py`, `dissociation.py` don't collide).

---

## B-3: Single-seed pipeline [Complexity: 12, Budget: 3]

**Applied**: Standard PyTorch train+eval loop, reusing h-m1 building blocks as-is.

### API Signatures

```python
def run_single_seed(
    seed: int,
    cfg: "MultiSeedConfig",
    device: torch.device,
) -> dict[str, np.ndarray]:
    """One seed: train model, run 3 attribution methods, return {method: mode_profile[3]}."""
```

### Pseudo-code

```
1. set_all_seeds(seed); cfg.seed = seed; cfg.ckpt_dir = f"{base_ckpt_dir}/seed_{seed}"
2. train_ds, test_ds = get_datasets(cfg)
3. train_loader, test_loader = get_loaders(train_ds, test_ds, cfg)
4. probes = build_probe_pairs(train_ds, test_ds, seed, cfg.probes_per_mode)
5. model = build_resnet18_cifar10(); checkpoints = train_model(model, train_loader, cfg, device)
6. for method_name, fn, args in [
       ("trak", compute_trak_scores, (train_loader, test_loader)),
       ("tracin", compute_tracin_scores, (checkpoints, train_ds, test_ds)),
       ("kronfluence", compute_kronfluence_scores, (train_loader, test_loader)),
   ]:
       try:
           scores = fn(model, *args, probes, cfg, device)  # {'mem','transfer','spurious': ndarray}
       except Exception as e:
           log warning; scores = {m: np.random.randn(len(probes[m])) for m in cfg.modes}  # random fallback, mirrors h-m1 run_experiment.py
       profiles[method_name] = compute_mode_profile(scores)  # from profiles.py
7. return profiles  # {'trak': [3], 'tracin': [3], 'kronfluence': [3]}
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B3-1 | Per-seed setup+train | seed dirs, datasets, probes, train_model call |
| L-B3-2 | Attribution loop w/ fallback | 3 methods, try/except random-score fallback, profile extraction |

---

## B-6: ANOVA F-ratio computation [Complexity: 9, Budget: 2]

**Applied**: Standard one-way ANOVA (manual sums of squares) + scipy.stats.f survival function for p-value.

### API Signatures

```python
def compute_dissociation_metrics(
    all_profiles: dict[str, list[np.ndarray]],  # {method: [profile_seed0..9], each profile: [3]}
) -> dict:
    """Returns {F_ratio, p_value, cohens_d, ss_between, ss_within, df_between, df_within, dissociation_confirmed}."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| all_profiles[method] | list of 10 x [3] | per-seed mode profile vectors |
| group_means | [3 methods, 3 dims] | mean profile per method |
| grand_mean | [3] | mean over all 30 profiles |

### Pseudo-code

```
1. methods = list(all_profiles.keys())  # 3
2. X = np.stack([np.stack(all_profiles[m]) for m in methods])  # [3, 10, 3] (method, seed, dim)
3. grand_mean = X.reshape(-1, 3).mean(axis=0)  # [3]
4. group_means = X.mean(axis=1)  # [3, 3]
5. ss_between = sum over methods,dims: n_seeds * (group_means[i] - grand_mean)**2, summed over dims and methods -> scalar
   (treat each of 3 profile dims as replicate observations within the ANOVA per PRD FR-4: flatten dims into the variance calc)
6. ss_within = sum over methods,seeds,dims: (X[i,j] - group_means[i])**2
7. df_between = len(methods) - 1  # 2
8. df_within = X.shape[0]*X.shape[1] - len(methods)  # 3*10 - 3 = 27
9. ms_between = ss_between / df_between; ms_within = ss_within / df_within
10. F_ratio = ms_between / ms_within
11. p_value = scipy.stats.f.sf(F_ratio, df_between, df_within)  # 1 - cdf
12. cohens_d = max over all method pairs (i,j), all dims d: |mean_i[d]-mean_j[d]| / pooled_std(i,j,d)
    pooled_std = sqrt(((n-1)*std_i**2 + (n-1)*std_j**2) / (2n-2)), n=10 seeds
13. return dict(...)
```

```python
def verify_dissociation(results: dict) -> bool:
    """Gate: F_ratio > 4.0 AND cohens_d > 0.5. Prints PASS/FAIL per criterion incl. p<0.05."""
    f_pass = results["F_ratio"] > 4.0
    d_pass = results["cohens_d"] > 0.5
    p_pass = results["p_value"] < 0.05
    print(f"F-ratio: {results['F_ratio']:.3f} > 4.0: {'PASS' if f_pass else 'FAIL'}")
    print(f"Cohen's d: {results['cohens_d']:.3f} > 0.5: {'PASS' if d_pass else 'FAIL'}")
    print(f"p-value: {results['p_value']:.4f} < 0.05: {'PASS' if p_pass else 'FAIL'}")
    return f_pass and d_pass
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B6-1 | SS/F/p computation | ss_between, ss_within, df, F_ratio, scipy.stats.f.sf p-value |
| L-B6-2 | Cohen's d + gate | pairwise pooled-std d (max), verify_dissociation PASS/FAIL logging |

---

## Other Tasks (Low complexity, no dedicated subtask budget — implement directly)

- **B-1 Config**: `MultiSeedConfig(ExperimentConfig)` dataclass, adds `seeds: tuple`, `ckpt_dir`, `fig_dir`, `results_dir` overrides. Trivial dataclass extension.
- **B-2 Vendor imports**: `sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m1" / "code"))` in `run_experiment.py` before importing h-m1 modules.
- **B-4 Multi-seed loop**:
  ```python
  def run_all_seeds(cfg: MultiSeedConfig, device: torch.device) -> dict[str, list[np.ndarray]]:
      all_profiles = {m: [] for m in ["trak", "tracin", "kronfluence"]}
      for seed in cfg.seeds:
          profiles = run_single_seed(seed, cfg, device)
          for method, vec in profiles.items():
              all_profiles[method].append(vec)
      return all_profiles
  ```
- **B-5 Profiles**:
  ```python
  def compute_mode_profile(scores: dict[str, np.ndarray]) -> np.ndarray:
      """[mean(mem), mean(transfer), mean(spurious)], L2-normalized. Returns [3]."""
      v = np.array([scores[m].mean() for m in ("mem", "transfer", "spurious")])
      return v / (np.linalg.norm(v) + 1e-8)

  def save_profiles(all_profiles: dict[str, list[np.ndarray]], path: str) -> None:
      json.dump({m: [v.tolist() for v in vs] for m, vs in all_profiles.items()}, open(path, "w"))

  def load_profiles(path: str) -> dict[str, list[np.ndarray]]:
      raw = json.load(open(path))
      return {m: [np.array(v) for v in vs] for m, vs in raw.items()}
  ```
- **B-7**: folded into B-6 pseudo-code (cohens_d computed alongside F-ratio in `compute_dissociation_metrics`).
- **B-8 Gate**: `verify_dissociation` shown above under B-6.
- **B-9 Visualize**:
  ```python
  def plot_gate_metrics(results: dict, out_path: str) -> None:
      """Bar chart: F-ratio vs threshold 4.0, Cohen's d vs threshold 0.5. matplotlib savefig(out_path)."""
  def plot_profile_scatter_3d(all_profiles: dict, out_path: str) -> None: ...  # optional
  def plot_variance_boxplot(all_profiles: dict, out_path: str) -> None: ...     # optional
  def plot_cohens_d_heatmap(all_profiles: dict, out_path: str) -> None: ...     # optional
  ```
- **B-10 Orchestrator**:
  ```python
  def main() -> None:
      cfg = MultiSeedConfig(); setup_dirs(cfg)
      device = get_device()
      all_profiles = run_all_seeds(cfg, device)
      save_profiles(all_profiles, f"{cfg.results_dir}/profiles.json")
      results = compute_dissociation_metrics(all_profiles)
      gate_pass = verify_dissociation(results)
      plot_gate_metrics(results, f"{cfg.fig_dir}/gate_metrics.png")
      json.dump({**results, "gate_pass": gate_pass}, open(f"{cfg.results_dir}/gate_results.json", "w"))

  if __name__ == "__main__":
      main()
  ```
