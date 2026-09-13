# Logic Design: H-D1
# Directional Paradigm × Dataset Interaction Analysis

**Hypothesis:** H-D1 (DIRECTIONAL — INCREMENTAL on H-E1)
**Date:** 2026-08-26
**Author:** Anonymous
**Tier:** FULL

Applied: Frozen-backbone linear probe API pattern (DFR, Izmailov et al. NeurIPS 2022)
Applied: scipy.stats directional t-test with alternative='greater' (one-tailed)
Applied: Bootstrap confidence interval for Pearson r (n_bootstrap=1000)
Applied: Group-balanced sampling across 4 groups (Blond_Hair × Male)

---

## Codebase Analysis (Serena)

**Project Type**: incremental (base H-E1), green-field for code
**Status**: H-E1 Phase 4 never ran — no h-e1/code/ folder exists
**Analyzed Path**: `docs/youra_research/h-e1/03_architecture.md` (interfaces only)
**Findings**: H-E1 architecture defines probe_utils, stats_utils interfaces consistent with H-D1 design. No implemented code to reuse. H-D1 implements all modules from scratch following H-E1 interface conventions. All API signatures below are new implementations.

---

## Subtasks

### L-3-1: Feature Extraction — Backbone Loading & Batch Inference

**Parent Epic:** A-3 (Feature Extraction, complexity 10)

**Function Signatures:**

```python
def load_erm_backbone(device: str = 'cuda') -> torch.nn.Module:
    """
    Load torchvision ResNet-50 ERM backbone with identity fc.

    Returns:
        model: ResNet-50 in eval mode, fc replaced with nn.Identity()
    """

def load_moco_backbone(device: str = 'cuda') -> torch.nn.Module:
    """
    Load MoCo-v3 ResNet-50 via torch.hub.

    Returns:
        model: MoCo-v3 ResNet-50 in eval mode
    """

def extract_features(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    device: str = 'cuda',
) -> np.ndarray:
    """
    Extract frozen features via forward pass (no grad).

    Args:
        model: backbone with Identity fc
        dataloader: yields (images, labels) batches
        device: 'cuda' or 'cpu'

    Returns:
        features: np.ndarray shape (N, 2048), float32
    """
```

**Tensor Shapes:**
- Input batch: `(B, 3, 224, 224)` float32, ImageNet-normalized
- Per-batch output: `(B, 2048)` float32
- Full output: `(N, 2048)` where N = balanced CelebA test size

**Pseudo-code:**
```
load_erm_backbone():
    model = torchvision.models.resnet50(pretrained=True)
    model.fc = nn.Identity()
    model.eval()
    model.to(device)
    return model

extract_features(model, dataloader, device):
    all_feats = []
    with torch.no_grad():
        for images, _ in dataloader:
            images = images.to(device)
            feats = model(images)          # (B, 2048)
            all_feats.append(feats.cpu().numpy())
    return np.concatenate(all_feats, axis=0)   # (N, 2048)
```

**Edge Cases:**
- MoCo hub load fails → catch RuntimeError, retry with `force_reload=True`
- CUDA OOM → halve batch_size, retry (log warning)
- Feature file already exists → skip extraction, load from cache

---

### L-3-2: Feature Extraction — Cache Management & Persistence

**Parent Epic:** A-3 (Feature Extraction, complexity 10)

**Function Signatures:**

```python
def extract_and_save_celeba_features(
    paradigm: str,           # 'erm' | 'moco'
    dataloader: torch.utils.data.DataLoader,
    save_path: str,
    device: str = 'cuda',
    force_recompute: bool = False,
) -> np.ndarray:
    """
    Extract CelebA features for one paradigm, save to .pt cache.

    Returns:
        features: np.ndarray shape (N, 2048)

    Cache logic: if save_path exists and not force_recompute, load from cache.
    """

def load_cached_features(path: str) -> np.ndarray:
    """
    Load features from .pt file.

    Returns:
        features: np.ndarray shape (N, 2048)
    Raises:
        FileNotFoundError if path does not exist
    """
```

**Pseudo-code:**
```
extract_and_save_celeba_features(paradigm, dataloader, save_path, device, force_recompute):
    if exists(save_path) and not force_recompute:
        return load_cached_features(save_path)
    loader_fn = load_erm_backbone if paradigm == 'erm' else load_moco_backbone
    model = loader_fn(device)
    features = extract_features(model, dataloader, device)
    torch.save(torch.tensor(features), save_path)
    print(f"Saved {paradigm} features: {features.shape} → {save_path}")
    return features
```

---

### L-4-1: Linear Probe — Training & Ratio Computation

**Parent Epic:** A-4 (Linear Probe CelebA, complexity 10)

**Function Signatures:**

```python
def train_probe(
    features: np.ndarray,        # shape (N_train, 2048)
    labels: np.ndarray,          # shape (N_train,) int {0,1}
    seed: int,
    C: float = 1.0,
    max_iter: int = 1000,
) -> LogisticRegression:
    """
    Train logistic regression probe.

    Returns:
        clf: fitted LogisticRegression
    """

def eval_probe(
    clf: LogisticRegression,
    features: np.ndarray,        # shape (N_test, 2048)
    labels: np.ndarray,          # shape (N_test,) int {0,1}
) -> float:
    """
    Evaluate probe on balanced test split.

    Returns:
        balanced_accuracy: float in [0, 1]
    """

def compute_ratio_one_seed(
    features: np.ndarray,        # shape (N, 2048)
    task_labels: np.ndarray,     # shape (N,) — Blond_Hair
    spurious_labels: np.ndarray, # shape (N,) — Male
    train_idx: np.ndarray,       # balanced group train indices
    test_idx: np.ndarray,        # balanced group test indices
    seed: int,
) -> dict[str, float]:
    """
    Returns {'spurious_acc': float, 'task_acc': float, 'ratio': float}
    ratio = spurious_acc / task_acc
    """
```

**Pseudo-code:**
```
compute_ratio_one_seed(features, task_labels, spurious_labels, train_idx, test_idx, seed):
    X_train = features[train_idx]
    X_test  = features[test_idx]

    # Spurious probe
    clf_s = train_probe(X_train, spurious_labels[train_idx], seed)
    spurious_acc = eval_probe(clf_s, X_test, spurious_labels[test_idx])

    # Task probe
    clf_t = train_probe(X_train, task_labels[train_idx], seed)
    task_acc = eval_probe(clf_t, X_test, task_labels[test_idx])

    return {
        'spurious_acc': spurious_acc,
        'task_acc': task_acc,
        'ratio': spurious_acc / task_acc,  # task_acc > 0 guaranteed (balanced)
    }
```

---

### L-4-2: Linear Probe — Multi-seed CelebA Probing Pipeline

**Parent Epic:** A-4 (Linear Probe CelebA, complexity 10)

**Function Signatures:**

```python
def run_celeba_probing(
    features_by_paradigm: dict[str, np.ndarray],
    # {'erm': (N,2048), 'moco': (N,2048)}
    task_labels: np.ndarray,     # shape (N,)
    spurious_labels: np.ndarray, # shape (N,)
    seeds: list[int] = [0,1,2,3,4],
    save_path: str = None,
) -> dict[str, list[float]]:
    """
    Run 5-seed probing for each paradigm.

    Returns:
        {'erm': [ratio_s0..s4], 'moco': [ratio_s0..s4]}

    Saves JSON to save_path if provided.
    """
```

**Pseudo-code:**
```
run_celeba_probing(features_by_paradigm, task_labels, spurious_labels, seeds, save_path):
    results = {}
    for paradigm, features in features_by_paradigm.items():
        ratios = []
        for seed in seeds:
            np.random.seed(seed)
            # Build group-balanced train/test split for this seed
            train_idx, test_idx = build_balanced_split(
                task_labels, spurious_labels, seed=seed)
            r = compute_ratio_one_seed(features, task_labels, spurious_labels,
                                       train_idx, test_idx, seed)
            ratios.append(r['ratio'])
        results[paradigm] = ratios
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
    return results
```

---

### L-6-1: Primary Tests — Directional & Null t-tests

**Parent Epic:** A-6 (Primary Statistical Tests, complexity 10)

**Function Signatures:**

```python
def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    """
    Pooled-std Cohen's d: (mean(a) - mean(b)) / pooled_std.
    """

def directional_test(
    moco_ratios: np.ndarray,   # shape (5,)
    erm_ratios: np.ndarray,    # shape (5,)
) -> dict[str, float]:
    """
    One-tailed t-test: MoCo > ERM.

    Returns:
        {
          't': float,
          'p_directional': float,   # one-tailed p-value
          'cohen_d': float,
          'diff_mean': float,       # moco_mean - erm_mean
          'moco_mean': float,
          'erm_mean': float,
          'direction': 'moco_gt_erm' | 'erm_gt_moco',
        }
    """

def null_test(
    moco_ratios: np.ndarray,   # shape (5,)
    erm_ratios: np.ndarray,    # shape (5,)
) -> dict[str, float]:
    """
    Two-tailed t-test (CelebA null test).

    Returns:
        {
          't': float,
          'p_two_sided': float,
          'cohen_d': float,
          'diff_mean': float,
          'moco_mean': float,
          'erm_mean': float,
        }
    """

def evaluate_gate(
    p_wb_directional: float,
    p_ca_two_sided: float,
    alpha_directional: float = 0.05,
    alpha_null: float = 0.1,
) -> str:
    """
    Returns: 'full_support' | 'partial_wb' | 'partial_ca' | 'no_support'
    """
```

**Pseudo-code:**
```
directional_test(moco_ratios, erm_ratios):
    t, p_two = scipy.stats.ttest_ind(moco_ratios, erm_ratios, alternative='two-sided')
    _, p_one = scipy.stats.ttest_ind(moco_ratios, erm_ratios, alternative='greater')
    d = cohen_d(moco_ratios, erm_ratios)
    diff = moco_ratios.mean() - erm_ratios.mean()
    return {
        't': t,
        'p_directional': p_one,
        'cohen_d': d,
        'diff_mean': diff,
        'moco_mean': moco_ratios.mean(),
        'erm_mean': erm_ratios.mean(),
        'direction': 'moco_gt_erm' if diff > 0 else 'erm_gt_moco',
    }

evaluate_gate(p_wb_directional, p_ca_two_sided, alpha_directional, alpha_null):
    wb_pass = p_wb_directional < alpha_directional
    ca_pass = p_ca_two_sided > alpha_null
    if wb_pass and ca_pass:   return 'full_support'
    if wb_pass and not ca_pass: return 'partial_wb'
    if not wb_pass and ca_pass: return 'partial_ca'
    return 'no_support'
```

---

### L-6-2: Primary Tests — Gate Evaluation & Interpretation

**Parent Epic:** A-6 (Primary Statistical Tests, complexity 10)

**Function Signatures:**

```python
def interpret_result(
    wb_result: dict,
    ca_result: dict,
    gate_verdict: str,
) -> dict[str, str]:
    """
    Map gate_verdict + direction to pre-registered interpretation strings.

    Returns:
        {
          'gate_verdict': str,
          'interpretation': str,   # one of 4 pre-registered interpretations
          'scientific_finding': str,
        }

    Pre-registered interpretations (from 02b_verification_plan.md):
    1. MoCo > ERM on WB only → 'augmentation_invariance_supported'
    2. MoCo > ERM on both   → 'label_correlation_confound'
    3. No diff on either    → 'effects_cancel'
    4. ERM > MoCo on WB     → 'supervised_label_drives_spurious'  [expected]
    """
```

**Pseudo-code:**
```
interpret_result(wb_result, ca_result, gate_verdict):
    wb_direction = wb_result['direction']   # 'moco_gt_erm' | 'erm_gt_moco'

    if gate_verdict == 'full_support' and wb_direction == 'moco_gt_erm':
        interp = 'augmentation_invariance_supported'
    elif gate_verdict == 'partial_wb' and wb_direction == 'moco_gt_erm':
        interp = 'label_correlation_confound'  # MoCo>ERM on both datasets
    elif gate_verdict == 'no_support':
        if wb_direction == 'erm_gt_moco':
            interp = 'supervised_label_drives_spurious'
        else:
            interp = 'effects_cancel'
    else:
        interp = 'partial_ca'  # WB test fails, CelebA passes

    scientific_finding = INTERPRETATION_STRINGS[interp]
    return {'gate_verdict': gate_verdict, 'interpretation': interp,
            'scientific_finding': scientific_finding}
```

---

### L-7-1: Secondary Analysis — Pearson r with Bootstrap CI

**Parent Epic:** A-7 (Secondary Analysis, complexity 12)

**Function Signatures:**

```python
def pearson_r_with_ci(
    ratios_all: np.ndarray,     # shape (40,) — 4 paradigms × 2 datasets × 5 seeds
    wga_gaps_all: np.ndarray,   # shape (40,) — worst-group accuracy gap
    n_bootstrap: int = 1000,
    seed: int = 0,
) -> dict[str, float]:
    """
    Pearson r + bootstrap 95% CI.

    Returns:
        {'r': float, 'p': float, 'ci_low': float, 'ci_high': float,
         'n': int}
    """

def build_ratio_wga_arrays(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    wb_wga: dict[str, list[float]],
    celeba_wga: dict[str, list[float]],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build (ratios_all, wga_gaps_all) arrays of shape (40,) each.
    Order: paradigm × dataset × seed (4 × 2 × 5 = 40).
    wga_gap = max_group_acc - min_group_acc per probe run.

    Returns:
        ratios_all: shape (40,)
        wga_gaps_all: shape (40,)
    """
```

**Pseudo-code:**
```
pearson_r_with_ci(ratios_all, wga_gaps_all, n_bootstrap, seed):
    r, p = scipy.stats.pearsonr(ratios_all, wga_gaps_all)
    # Bootstrap CI
    rng = np.random.default_rng(seed)
    n = len(ratios_all)
    boot_rs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        r_b, _ = scipy.stats.pearsonr(ratios_all[idx], wga_gaps_all[idx])
        boot_rs.append(r_b)
    ci_low, ci_high = np.percentile(boot_rs, [2.5, 97.5])
    return {'r': r, 'p': p, 'ci_low': ci_low, 'ci_high': ci_high, 'n': n}
```

---

### L-7-2: Secondary Analysis — Ablations A/B/C/D

**Parent Epic:** A-7 (Secondary Analysis, complexity 12)

**Function Signatures:**

```python
def run_ablation_a(wb_results: dict[str, list[float]]) -> dict:
    """Ablation A: Waterbirds-only directional test (no CelebA required)."""

def run_ablation_b(celeba_results: dict[str, list[float]]) -> dict:
    """Ablation B: CelebA-only null test."""

def run_ablation_c(wb_results: dict[str, list[float]]) -> dict:
    """
    Ablation C: All-paradigm comparison on Waterbirds.
    Run directional_test for all 6 pairs from [erm, moco, dino, barlowtwins].
    """

def run_ablation_d(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
) -> dict:
    """
    Ablation D: Reversed-direction test.
    ttest_ind(erm_wb, moco_wb, alternative='greater') — tests ERM > MoCo.
    Reports p-value for observed direction.
    """

def run_all_analyses(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    wga_data: dict | None = None,
    save_path: str = None,
) -> dict:
    """
    Orchestrates all primary + secondary analyses.
    Returns full results dict; saves to h_d1_results.json if save_path given.
    """
```

**Pseudo-code:**
```
run_ablation_d(wb_results, celeba_results):
    erm_wb  = np.array(wb_results['erm'])
    moco_wb = np.array(wb_results['moco'])
    # Test: is ERM > MoCo on WB? (reversed direction, expected to pass per H-E1)
    _, p_reversed = scipy.stats.ttest_ind(erm_wb, moco_wb, alternative='greater')
    d = cohen_d(erm_wb, moco_wb)
    return {
        'description': 'Reversed direction: ERM > MoCo on Waterbirds',
        'p_reversed_directional': p_reversed,
        'cohen_d': d,
        'erm_mean': erm_wb.mean(),
        'moco_mean': moco_wb.mean(),
        'diff_erm_minus_moco': erm_wb.mean() - moco_wb.mean(),
        'note': 'Expected to be significant per H-E1 (ERM=1.052 > MoCo=1.027)',
    }

run_all_analyses(wb_results, celeba_results, wga_data, save_path):
    erm_wb  = np.array(wb_results['erm'])
    moco_wb = np.array(wb_results['moco'])
    erm_ca  = np.array(celeba_results['erm'])
    moco_ca = np.array(celeba_results['moco'])

    wb_primary = directional_test(moco_wb, erm_wb)
    ca_primary = null_test(moco_ca, erm_ca)
    gate = evaluate_gate(wb_primary['p_directional'], ca_primary['p_two_sided'])
    interpretation = interpret_result(wb_primary, ca_primary, gate)

    ablations = {
        'A': run_ablation_a(wb_results),
        'B': run_ablation_b(celeba_results),
        'C': run_ablation_c(wb_results),
        'D': run_ablation_d(wb_results, celeba_results),
    }

    pearson = None
    if wga_data:
        ratios, gaps = build_ratio_wga_arrays(wb_results, celeba_results,
                                              wga_data['wb'], wga_data['ca'])
        pearson = pearson_r_with_ci(ratios, gaps)

    results = {
        'wb_primary': wb_primary,
        'ca_primary': ca_primary,
        'gate_verdict': gate,
        'interpretation': interpretation,
        'ablations': ablations,
        'pearson_r': pearson,
    }
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2, default=float)
    return results
```

---

### L-9-1: Visualization — Required Figures (FR-8.1, FR-8.2)

**Parent Epic:** A-9 (Visualization Extended, complexity 10)

**Function Signatures:**

```python
def plot_gate_metrics(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    save_path: str,
    figsize: tuple = (8, 5),
) -> None:
    """
    FR-8.1: Bar chart MoCo-v3 vs ERM spurious/task ratio on WB + CelebA.
    2 datasets × 2 paradigms = 4 bars. Error bars = ±1 SD across 5 seeds.
    """

def plot_interaction(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    save_path: str,
    figsize: tuple = (10, 6),
) -> None:
    """
    FR-8.2: All 4 paradigms × 2 datasets, error bars.
    Grouped bar chart or line plot with markers.
    """
```

**Pseudo-code:**
```
plot_gate_metrics(wb_results, celeba_results, save_path):
    paradigms = ['erm', 'moco']
    datasets = {'Waterbirds': wb_results, 'CelebA': celeba_results}
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(datasets))
    width = 0.35
    for i, (paradigm, color) in enumerate(zip(paradigms, ['steelblue', 'coral'])):
        means = [np.mean(ds[paradigm]) for ds in datasets.values()]
        stds  = [np.std(ds[paradigm])  for ds in datasets.values()]
        ax.bar(x + i*width, means, width, yerr=stds, label=paradigm.upper(),
               color=color, capsize=5)
    ax.set_xticks(x + width/2)
    ax.set_xticklabels(datasets.keys())
    ax.set_ylabel('Spurious / Task Probe Accuracy Ratio')
    ax.set_title('H-D1: MoCo-v3 vs ERM Spurious Encoding Ratio')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
```

---

### L-9-2: Visualization — Extended Figures (FR-8.3, FR-8.4, FR-8.5)

**Parent Epic:** A-9 (Visualization Extended, complexity 10)

**Function Signatures:**

```python
def plot_directional_test(
    analysis_results: dict,
    save_path: str,
) -> None:
    """
    FR-8.3: Horizontal bar of MoCo−ERM diff + 95% CI for WB (directional)
    and CelebA (null). Significance thresholds marked.
    95% CI via scipy.stats.t.interval(0.95, df=8, loc=diff, scale=se).
    """

def plot_ratio_vs_wga(
    ratios_all: np.ndarray,     # shape (40,)
    wga_gaps_all: np.ndarray,   # shape (40,)
    paradigm_labels: list[str], # shape (40,) — label per point
    pearson_result: dict,
    save_path: str,
) -> None:
    """
    FR-8.4: Scatter 40 points, color by paradigm, Pearson r + p annotation.
    """

def plot_seed_distributions(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    save_path: str,
) -> None:
    """
    FR-8.5: Violin/strip plot of ratio distributions per paradigm × dataset.
    4 paradigms × 2 datasets = 8 distributions.
    """

def generate_all_figures(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    analysis_results: dict,
    figures_dir: str,
    wga_data: dict | None = None,
) -> list[str]:
    """
    Generates all 5 required figures. Returns list of saved paths.
    Creates figures_dir if not exists.
    """
```

**Pseudo-code:**
```
generate_all_figures(wb_results, celeba_results, analysis_results, figures_dir, wga_data):
    os.makedirs(figures_dir, exist_ok=True)
    paths = []
    plot_gate_metrics(wb_results, celeba_results,
                      f'{figures_dir}/gate_metrics.png')
    paths.append('gate_metrics.png')

    plot_interaction(wb_results, celeba_results,
                     f'{figures_dir}/interaction_plot.png')
    paths.append('interaction_plot.png')

    plot_directional_test(analysis_results,
                          f'{figures_dir}/directional_test.png')
    paths.append('directional_test.png')

    plot_seed_distributions(wb_results, celeba_results,
                            f'{figures_dir}/seed_distributions.png')
    paths.append('seed_distributions.png')

    if wga_data:
        ratios, gaps = build_ratio_wga_arrays(wb_results, celeba_results,
                                              wga_data['wb'], wga_data['ca'])
        labels = [f'{p}-{d}' for p in PARADIGMS for d in ['WB','CA']
                  for _ in range(5)]
        plot_ratio_vs_wga(ratios, gaps, labels,
                          analysis_results['pearson_r'],
                          f'{figures_dir}/ratio_vs_wga.png')
        paths.append('ratio_vs_wga.png')

    return paths
```
