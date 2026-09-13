# Logic: h-c2

**Applied**: No KB pattern match (best <0.44 similarity, unrelated TF/PyTorch docs) — reused h-m1 actual implementation patterns (trak.TRAKer, kronfluence.Analyzer official APIs).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1) — actual code exists on disk
**Status**: API signatures verified from actual implementation at `h-m1/code/` (NOT from h-m1/03_logic.md spec, which differs in places)
**Analyzed Path**: `docs/youra_research/h-m1/code/{data.py, attribution_trak.py, attribution_kronfluence.py, config.py}`
**Relevant Symbols**: `build_probe_pairs`, `compute_trak_scores`, `compute_kronfluence_scores`, `ExperimentConfig`, `set_all_seeds`, `setup_dirs`

**Divergences from h-m1/03_logic.md spec found in actual code (use these, not the spec):**
- Mode keys are `'mem' / 'transfer' / 'spurious'` (spec/architecture use `'memorization'/'feature_transfer'/'spurious'` — h-c2 must pick one consistent set; using actual code's `mem/transfer/spurious`)
- `build_probe_pairs(train_ds, test_ds, seed, n_per_mode=1000)` — param is `n_per_mode`, not implicit
- `compute_trak_scores(..., cfg, device)` and `compute_kronfluence_scores(..., cfg, device)` both take explicit `device: torch.device` arg (missing in specs)
- Config field names: `trak_proj_dim`, `trak_use_half_precision`, `probes_per_mode`, `modes: tuple`, `kronfluence_use_amp` (not generic `proj_dim`)
- `compute_kronfluence_scores` has automatic fallback to gradient-dot-product if `kronfluence` import fails — h-c2 should keep this fallback for robustness across 3 models
- TRAK score matrix is `[num_train, num_test]`; Kronfluence score matrix is `[num_test, num_train]` (transposed) — gather logic differs per method

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/data.py (ACTUAL CODE)
def build_probe_pairs(train_ds: Dataset, test_ds: Dataset, seed: int, n_per_mode: int = 1000) -> dict:
    """Returns {'mem': [...], 'transfer': [...], 'spurious': [...]}, list[tuple[int,int]] per mode."""

# From: h-m1/code/attribution_trak.py (ACTUAL CODE)
def compute_trak_scores(model: nn.Module, train_loader: DataLoader, test_loader: DataLoader,
                         probes: dict, cfg: ExperimentConfig, device: torch.device) -> dict:
    """Returns {'mem': np.ndarray, 'transfer': np.ndarray, 'spurious': np.ndarray}."""

# From: h-m1/code/attribution_kronfluence.py (ACTUAL CODE)
def compute_kronfluence_scores(model: nn.Module, train_loader: DataLoader, test_loader: DataLoader,
                                probes: dict, cfg: ExperimentConfig, device: torch.device) -> dict:
    """Same return shape as TRAK. Falls back to gradient dot product if kronfluence unavailable."""

# From: h-m1/code/config.py (ACTUAL CODE)
def set_all_seeds(seed: int) -> None: ...
def setup_dirs(cfg) -> None: ...
```

h-c2 reimplements `build_probe_pairs` verbatim (same seed/logic, class-proxy pairing) rather than importing, since it must run per-model with identical indices across 3 different train/test dataset objects (each model may use a different image transform/resolution but same CIFAR-10 indices).

---

## A-1: Config & Seeding [Complexity: 4, Budget: 4]

**Applied**: Reuse h-m1 `ExperimentConfig` pattern, extended with multi-model fields

### API Signatures

```python
# config.py
@dataclass
class ExperimentConfig:
    seed: int = 42
    batch_size: int = 128
    checkpoint_every: int = 10
    trak_proj_dim: int = 2048
    trak_use_half_precision: bool = True
    probes_per_mode: int = 1000
    modes: tuple = ("mem", "transfer", "spurious")
    r_threshold: float = 0.7
    bonferroni_alpha: float = 0.05 / 3
    data_root: str = "./data"
    ckpt_dir: str = "./h-c2/checkpoints"
    fig_dir: str = "./h-c2/figures"

@dataclass
class ModelTrainConfig:
    name: str          # 'resnet18' | 'vit_small' | 'convnext_tiny'
    epochs: int
    lr: float
    optimizer: str      # 'sgd' | 'adamw'

def set_all_seeds(seed: int) -> None: ...  # identical to h-m1
def setup_dirs(cfg: ExperimentConfig) -> None: ...  # identical to h-m1
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Config dataclasses + seeding + dirs | ExperimentConfig, ModelTrainConfig, set_all_seeds, setup_dirs (copy h-m1 pattern) |

---

## A-2: Data Pipeline [Complexity: 9, Budget: 9]

**Applied**: h-m1 `build_probe_pairs`/`_find_*_pairs` reused verbatim (same seed → identical indices)

### API Signatures

```python
# data.py
def get_datasets(cfg: ExperimentConfig, resize: int = 224) -> tuple[Dataset, Dataset]:
    """CIFAR-10 train/test, ImageNet-normalized, resize per model (224 default; ViT/ConvNeXt may differ)."""

def get_loaders(train_ds: Dataset, test_ds: Dataset, cfg: ExperimentConfig) -> tuple[DataLoader, DataLoader]: ...

def build_probe_pairs(train_ds: Dataset, test_ds: Dataset, seed: int, n_per_mode: int = 1000) -> dict[str, list[tuple[int, int]]]:
    """Identical logic to h-m1 (class-proxy pairing). Returns {'mem':[...], 'transfer':[...], 'spurious':[...]}.
    Only depends on labels (not pixel resolution) -> identical indices across all 3 models regardless of transform."""

def _find_memorization_pairs(train_labels, test_labels, n: int, rng) -> list[tuple[int, int]]: ...
def _find_transfer_pairs(train_labels, test_labels, n: int, rng) -> list[tuple[int, int]]: ...
def _find_spurious_pairs(train_labels, test_labels, n: int, rng) -> list[tuple[int, int]]: ...

def probe_subset(probes: dict, fraction: float, seed: int) -> dict[str, list[tuple[int, int]]]:
    """ABL-2: random fraction subset per mode, same seed for reproducibility."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| image | [3, 224, 224] | resize per model transform (all 3 use 224 for CIFAR-10 fine-tune) |
| probe pair idx | (int, int) | (train_idx, test_idx), label-based -> model-independent |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | get_datasets/get_loaders | Per-model transform variants, CIFAR-10 load |
| L-2-2 | build_probe_pairs + probe_subset | Reuse h-m1 `_find_*_pairs` verbatim; add ABL-2 subset helper |

---

## A-3: Model Builders [Complexity: 6, Budget: 6]

**Applied**: torchvision (ResNet-18) + timm (ViT-Small, ConvNeXt-Tiny)

### API Signatures

```python
# models.py
def build_resnet18(num_classes: int = 10, pretrained: bool = True) -> nn.Module:
    """torchvision.models.resnet18(weights=IMAGENET1K_V1), fc replaced with Linear(512, num_classes)."""

def build_vit_small(num_classes: int = 10, pretrained: bool = True) -> nn.Module:
    """timm.create_model('vit_small_patch16_224', pretrained=pretrained, num_classes=num_classes)."""

def build_convnext_tiny(num_classes: int = 10, pretrained: bool = True) -> nn.Module:
    """timm.create_model('convnext_tiny', pretrained=pretrained, num_classes=num_classes)."""

def build_model(name: str, num_classes: int = 10) -> nn.Module:
    """Dispatch by name: 'resnet18' | 'vit_small' | 'convnext_tiny'. Raises ValueError on unknown name."""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | build_resnet18/vit_small/convnext_tiny + dispatch | Standard pretrained heads swapped for CIFAR-10 |

---

## A-4: Multi-Model Training [Complexity: 11, Budget: 11]

**Applied**: h-m1 `train_model`/`_train_one_epoch`/`_save_checkpoint` pattern, looped over 3 models

### API Signatures

```python
# train.py
def train_model(model: nn.Module, train_loader: DataLoader, test_loader: DataLoader,
                 mcfg: ModelTrainConfig, cfg: ExperimentConfig, device: torch.device) -> tuple[list[str], float]:
    """SGD or AdamW per mcfg.optimizer. Saves checkpoint every cfg.checkpoint_every epochs.
    Returns (checkpoint_paths, final_test_accuracy). Asserts final_test_accuracy > 0.85 (FR-1)."""

def _train_one_epoch(model: nn.Module, loader: DataLoader, optimizer, criterion, device) -> float:
    """Returns mean loss for the epoch."""

def _evaluate(model: nn.Module, loader: DataLoader, device) -> float:
    """Returns test accuracy in [0,1]."""

def _save_checkpoint(model: nn.Module, name: str, epoch: int, ckpt_dir: str) -> str:
    """torch.save(model.state_dict(), path=f'{ckpt_dir}/{name}_ep{epoch}.pt'). Returns path."""

def train_all_models(models: dict[str, nn.Module], train_loader: DataLoader, test_loader: DataLoader,
                      mcfgs: dict[str, ModelTrainConfig], cfg: ExperimentConfig, device: torch.device
                      ) -> dict[str, tuple[list[str], float]]:
    """Loops train_model per model name, returns {name: (ckpt_paths, accuracy)}."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [B, 10] | model(x) output, all 3 architectures |
| loss | scalar | CrossEntropyLoss |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | train_model + _train_one_epoch + _evaluate + _save_checkpoint | Copy h-m1 loop, add optimizer dispatch (sgd/adamw), accuracy gate assert |
| L-4-2 | train_all_models | Loop wrapper over 3 model configs |

---

## A-5: TRAK Integration [Complexity: 13, Budget: 13]

**Applied**: h-m1 `compute_trak_scores` (actual code) reused, generalized over model name for `save_dir` isolation

### API Signatures

```python
# attribution_trak.py (mirrors h-m1/code/attribution_trak.py exactly, adds model_name param)
def compute_trak_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict[str, list[tuple[int, int]]],
    cfg: ExperimentConfig,
    device: torch.device,
) -> dict[str, np.ndarray]:
    """Returns {'mem': scores, 'transfer': scores, 'spurious': scores}, each shape (num_probes,).
    Identical logic to h-m1: subset train/test to union of probe indices, featurize, finalize_scores."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| score_matrix | [num_train_subset, num_test_subset] | traker.finalize_scores() output |
| mode scores | [num_probes] | gathered per (train_idx, test_idx) pair |

### Pseudo-code (identical to h-m1 actual code)

```
1. train_indices, test_indices = sorted(union of probe indices)
2. Subset(train_ds, train_indices), Subset(test_ds, test_indices) -> sub_loaders
3. traker = TRAKer(model, task='image_classification', train_set_size=len(train_subset),
                    proj_dim=cfg.trak_proj_dim, device=device, use_half_precision=cfg.trak_use_half_precision)
4. traker.load_checkpoint(model.state_dict(), model_id=0)
5. featurize each train batch -> traker.finalize_features(model_ids=[0])
6. start_scoring_checkpoint -> score each test batch -> score_matrix = finalize_scores()  # [N_train_sub, N_test_sub]
7. for mode, pairs: scores[mode] = [score_matrix[train_idx_map[ti], test_idx_map[tj]] for ti,tj in pairs]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Probe index subsetting + TRAKer init/featurize | Union indices, Subset loaders, load_checkpoint, finalize_features |
| L-5-2 | Scoring | start_scoring_checkpoint, score, finalize_scores |
| L-5-3 | Per-mode gathering | Map score_matrix -> per-mode np.ndarray via idx maps |

---

## A-6: Kronfluence Integration [Complexity: 14, Budget: 14]

**Applied**: h-m1 `compute_kronfluence_scores` (actual code, with fallback) reused

### API Signatures

```python
# attribution_kronfluence.py (mirrors h-m1/code/attribution_kronfluence.py)
def compute_kronfluence_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict[str, list[tuple[int, int]]],
    cfg: ExperimentConfig,
    device: torch.device,
) -> dict[str, np.ndarray]:
    """Tries kronfluence.Analyzer EK-FAC; falls back to gradient dot product if unavailable.
    Same return shape as TRAK."""

class ClassificationTask(Task):
    def compute_train_loss(self, batch, model, sample: bool = False) -> Tensor: ...
    def compute_measurement(self, batch, model) -> Tensor: ...

def _compute_with_kronfluence(model, train_loader, test_loader, probes, cfg, device) -> dict[str, np.ndarray]: ...
def _fallback_gradient_scores(model, train_loader, test_loader, probes, cfg, device) -> dict[str, np.ndarray]: ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| score_matrix (kronfluence) | [num_test_subset, num_train_subset] | note: transposed vs TRAK |
| grad (fallback) | [P] | flattened all-params gradient, per sample |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | ClassificationTask + Analyzer setup | prepare_model, Analyzer init per model_name |
| L-6-2 | fit_all_factors (EK-FAC) | Fit on train subset |
| L-6-3 | compute_pairwise_scores + gather | Query/train subsets, map transposed score_matrix to per-mode |
| L-6-4 | _fallback_gradient_scores | try/except ImportError wrapper, per-sample grad dot product |

---

## A-7: Cross-Model Correlation [Complexity: 10, Budget: 10]

**Applied**: scipy.stats.pearsonr + manual bootstrap (standard pattern)

### API Signatures

```python
# cross_model_eval.py
def compute_mode_profile(scores: dict[str, np.ndarray]) -> dict[str, float]:
    """Mean per mode -> {'mem': x, 'transfer': y, 'spurious': z}."""

def pairwise_correlations(profiles: dict[str, dict[str, float]]) -> dict[tuple[str, str], dict]:
    """Pearson r + p-value per model pair, over the 3-mode profile vector.
    Applies Bonferroni correction: p_corrected = p * 3, compared to cfg.bonferroni_alpha (FR-5).
    Returns {(model_a, model_b): {'r': float, 'p': float, 'p_corrected': float, 'significant': bool}}."""

def bootstrap_ci(v1: np.ndarray, v2: np.ndarray, n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    """95% CI for Pearson r via resampling paired (v1[i], v2[i]) with replacement (FR-4)."""

def check_transfer_success(correlations: dict[tuple[str, str], dict], threshold: float = 0.7) -> str:
    """Returns 'PASS' | 'PARTIAL' | 'FAIL' per success criteria table."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| profile vector | [3] | one scalar per mode (mem, transfer, spurious) |
| bootstrap r samples | [n_boot] | resampled Pearson r values |

### Pseudo-code (cross-model correlation)

```
1. profiles = {model_name: compute_mode_profile(scores[model_name]) for model_name in models}
   # profiles[m] = {'mem': x, 'transfer': y, 'spurious': z}  (3-dim vector per model)
2. for (m1, m2) in combinations(models, 2):
     v1 = np.array([profiles[m1][mode] for mode in cfg.modes])  # [3]
     v2 = np.array([profiles[m2][mode] for mode in cfg.modes])  # [3]
     r, p = scipy.stats.pearsonr(v1, v2)
     p_corrected = min(p * 3, 1.0)
     ci_lo, ci_hi = bootstrap_ci(v1, v2, n_boot=1000)
     correlations[(m1, m2)] = {'r': r, 'p': p, 'p_corrected': p_corrected,
                                 'significant': p_corrected < cfg.bonferroni_alpha,
                                 'ci': (ci_lo, ci_hi)}
3. verdict = check_transfer_success(correlations, cfg.r_threshold)
   # all r>0.7 -> PASS; mean r>0.7 some below -> PARTIAL; mean r<0.7 -> FAIL
```

Note: bootstrap over a 3-point profile vector is degenerate (resampling 3 points with replacement -> limited distinct combos); document as known limitation, still meets FR-4 literally.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | compute_mode_profile | Mean-per-mode aggregation from raw scores dict |
| L-7-2 | pairwise_correlations | Pearson r/p + Bonferroni correction over model pairs |
| L-7-3 | bootstrap_ci + check_transfer_success | Resample-based CI, PASS/PARTIAL/FAIL gate |

---

## A-8: Ablations [Complexity: 8, Budget: 8]

**Applied**: Reuse A-6 (Kronfluence) + A-2 (probe_subset) + A-7 (correlation) building blocks

### API Signatures

```python
# cross_model_eval.py (extends A-7)
def ablation_method_comparison(trak_profiles: dict, kronfluence_profiles: dict) -> dict[str, dict]:
    """ABL-1: pairwise_correlations(trak_profiles) vs pairwise_correlations(kronfluence_profiles) per model pair.
    Returns {'trak': correlations, 'kronfluence': correlations, 'agreement': bool}."""

def ablation_probe_stability(all_scores_full: dict, probes: dict, models: dict[str, nn.Module],
                              train_loader, test_loader, cfg: ExperimentConfig, device
                              ) -> dict:
    """ABL-2: probe_subset(probes, 0.5, seed) -> recompute TRAK scores on subset -> pairwise_correlations.
    Returns {'full': correlations_full, 'subset': correlations_subset, 'stable': bool (max |r_diff| < 0.1)}."""
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | ablation_method_comparison (ABL-1) | Compare TRAK vs Kronfluence correlation matrices |
| L-8-2 | ablation_probe_stability (ABL-2) | 50% probe subset, recompute correlations, stability check |

---

## A-9: Visualization [Complexity: 7, Budget: 7]

### API Signatures

```python
# visualize.py
def plot_profile_heatmap(profiles: dict[str, dict[str, float]], out_path: str) -> None:
    """3x3 models x modes seaborn.heatmap. Required (FR-6)."""

def plot_correlation_bars(correlations: dict[tuple[str, str], dict], threshold: float, out_path: str) -> None:
    """Bar chart of r per model pair + horizontal threshold line. Required (FR-6)."""

def plot_profile_radar(profiles: dict[str, dict[str, float]], out_path: str) -> None:
    """Per-model radar chart over 3 modes. Optional."""

def plot_bootstrap_ci(correlations: dict[tuple[str, str], dict], out_path: str) -> None:
    """Error-bar plot of r with bootstrap 95% CI per pair. Optional."""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | All 4 plot functions | Heatmap + bars (required), radar + CI (optional) |

---

## A-10: Orchestration & Gate [Complexity: 8, Budget: 8]

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """1. config+seed+dirs 2. per-model get_datasets/get_loaders (shared probe_pairs via labels)
    3. build_model x3 -> train_all_models -> checkpoints+accuracies (assert >0.85 each)
    4. compute_trak_scores per model -> trak_profiles (primary, FR-3)
    5. compute_kronfluence_scores per model -> kronfluence_profiles (verification, ABL-1)
    6. pairwise_correlations(trak_profiles), bootstrap_ci, check_transfer_success -> verdict
    7. ablation_method_comparison, ablation_probe_stability
    8. visualize.* -> fig_dir
    9. log_gate_results -> PASS/PARTIAL/FAIL to file"""

def log_gate_results(verdict: str, correlations: dict, ablations: dict, out_path: str) -> bool:
    """Writes success-criteria result (FR success table) to out_path. Returns True if verdict == 'PASS'."""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | main() + log_gate_results | Full pipeline wiring across 3 models, gate logging |

---

**Total subtasks used**: 1+2+1+2+3+4+3+2+1+1 = 20 items across A-1..A-10, within 6-subtask-average budget guidance (condensed per task where architecture breakdown exceeded per-task allocation).
