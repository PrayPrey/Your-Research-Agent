# H-M3 Logic: Background Linear Decodability — API Signatures & Pseudo-code

Applied: flat-two-file pattern (h-m2 verified, copy-adapt inline)
Applied: sklearn probe pattern (C=1e9, lbfgs, fit+score on same set)
Applied: sequential checkpoint load/unload (avoid OOM)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (INCREMENTAL — reuses h-m2 code)
**Analyzed**: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/h-m2/code/`
**Key findings:**
- `load_resnet50(ckpt_path, device)` — L26-40: handles dict keys `model_state_dict`, `model`, `state_dict`; `model.fc = Linear(2048, 2)` before loading
- `get_transform()` — L45-50: uses `Resize((224,224))` (H-M3 spec says Resize(256)+CenterCrop(224) — override)
- `get_loader(split, batch_size, shuffle=False)` — L53-60: `wilds.get_dataset(download=False)`, `num_workers=4`, `pin_memory=True`
- `extract_layer4_features` — L168-188: `model.eval()` + `torch.no_grad()`, batch loop, `adaptive_avg_pool2d`, `flatten(1)`, returns `(features_np, labels_np)`
- `linear_probe(train_features, train_labels, test_features, test_labels)` — L191-199: `LogisticRegression(solver, C, max_iter, random_state).fit().score()`
- `paired_ttest` — L223-235: `scipy.stats.ttest_rel(a, b, alternative='greater')`, Cohen's d = `mean(diff)/std(diff, ddof=1)`
- `gate_verdict` — L237-240: tiered threshold check

**H-M3 delta from H-M2:**
- DROP `verify_gradient_propagation` (FR-1)
- DROP `compute_layer4_gradient_norm` (FR-2)
- DROP `compare_all_methods` (weight diff)
- CHANGE transform: Resize(256)+CenterCrop(224) (vs Resize((224,224)))
- CHANGE probe: fit AND score on SAME test set (H-M3 measures raw decodability)
- CHANGE methods: `["erm", "groupdro", "sam"]` — no `dfr`
- ADD convergence guard: retry with max_iter=5000 on ConvergenceWarning

---

## External Dependencies API

Verified signatures from `h-m2/code/run_experiment.py`:

```python
# L26-40 — use as-is
def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module:
    """Load ResNet-50. Sets fc=Linear(2048,2). Handles dict keys."""

# L53-60 — use as-is (transform injected separately)
def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader:
    """Load WILDS Waterbirds subset with transform."""

# L168-188 — adapt: bg_label = metadata[:,0] % 2 (not class label)
def extract_layer4_features(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (features [N,2048], bg_labels [N])."""
```

---

## Module: config.py

```python
"""H-M3 experiment constants."""
import os

WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
RESULTS_JSON: str = os.path.join(BASE_DIR, "results.json")
VALIDATION_REPORT: str = os.path.join(BASE_DIR, "04_validation.md")

METHODS: list = ["erm", "groupdro", "sam"]
SEEDS: list = [1, 2, 3]
PRIMARY_METHODS: list = ["erm", "groupdro"]

PROBE_C: float = 1e9
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
BATCH_SIZE: int = 100
PROBE_N_TEST_SAMPLES: int = 5794

IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]

# WGA values for Fig4 (probe_acc vs WGA scatter)
WGA_BY_METHOD_SEED: dict = {
    "erm_seed1": 0.72, "erm_seed2": 0.72, "erm_seed3": 0.72,
    "groupdro_seed1": 0.88, "groupdro_seed2": 0.88, "groupdro_seed3": 0.88,
    "sam_seed1": 0.78, "sam_seed2": 0.78, "sam_seed3": 0.78,
}
```

---

## Module: run_experiment.py — Full API

### load_resnet50

```python
def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module:
    """
    Load ResNet-50 from checkpoint. Handles dict wrapping.
    Input: ckpt_path (str), device (str)
    Output: torch.nn.Module in eval mode on device
    """
    model = tv_models.resnet50(weights=None)
    model.fc = torch.nn.Linear(2048, 2)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    if isinstance(ckpt, dict):
        for key in ('model_state_dict', 'model', 'state_dict'):
            if key in ckpt:
                model.load_state_dict(ckpt[key])
                break
        else:
            model.load_state_dict(ckpt)
    else:
        model.load_state_dict(ckpt)
    return model.eval().to(device)
```

### get_transform

```python
def get_transform() -> T.Compose:
    """
    H-M3 standard preprocessing (Resize(256)+CenterCrop(224) per experiment brief).
    Override from H-M2 which used Resize((224,224)).
    """
    return T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
    ])
```

### get_loader

```python
def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader:
    """
    Input: split ('test'), batch_size (100), shuffle (False)
    Output: DataLoader with Waterbirds subset
    """
    dataset = get_dataset(dataset=config.WILDS_DATASET, download=False,
                          root_dir=config.WILDS_CACHE)
    subset = dataset.get_subset(split, transform=get_transform())
    return DataLoader(subset, batch_size=batch_size, shuffle=shuffle,
                      num_workers=4, pin_memory=True)
```

### extract_layer4_features

```python
def extract_layer4_features(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract frozen layer4 D=2048 features + background labels.
    Input:  model (ResNet-50, eval mode), dataloader, device
    Output: (features [N, 2048] float32, bg_labels [N] int)
    Tensor shape: (B,3,224,224) → layer4 → (B,2048,H,W) → pool → (B,2048) → flatten
    """
    model.eval()
    all_feats, all_labels = [], []
    with torch.no_grad():
        for x, y, metadata in dataloader:
            x = x.to(device)
            # Full forward to layer4
            x = model.conv1(x); x = model.bn1(x); x = model.relu(x); x = model.maxpool(x)
            x = model.layer1(x); x = model.layer2(x); x = model.layer3(x); x = model.layer4(x)
            x = torch.nn.functional.adaptive_avg_pool2d(x, (1, 1))
            x = x.flatten(1)                     # (B, 2048)
            all_feats.append(x.cpu().numpy())
            bg = metadata[:, 0].numpy() % 2      # group_array % 2 → land=0, water=1
            all_labels.append(bg)
    features = np.concatenate(all_feats, axis=0)   # (N, 2048)
    labels   = np.concatenate(all_labels, axis=0)  # (N,)
    print(f"[H-M3] Features extracted: {features.shape}")
    print(f"[H-M3] Background label distribution: {np.bincount(labels.astype(int))}")
    return features, labels
```

### run_probe

```python
def run_probe(
    features: np.ndarray,
    labels: np.ndarray,
    method: str,
    seed: int,
) -> float:
    """
    Fit L-BFGS probe and score on SAME features (measuring raw decodability).
    Input:  features [N, 2048], labels [N], method str, seed int
    Output: probe accuracy float in [0, 1]
    """
    import warnings
    from sklearn.exceptions import ConvergenceWarning
    probe = LogisticRegression(solver=config.PROBE_SOLVER, C=config.PROBE_C,
                               max_iter=config.PROBE_MAX_ITER,
                               random_state=config.PROBE_RANDOM_STATE)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        probe.fit(features, labels)
        if w and any(issubclass(x.category, ConvergenceWarning) for x in w):
            probe = LogisticRegression(solver=config.PROBE_SOLVER, C=config.PROBE_C,
                                       max_iter=5000,
                                       random_state=config.PROBE_RANDOM_STATE)
            probe.fit(features, labels)
    acc = probe.score(features, labels)
    print(f"[H-M3] Probe acc {method}_seed{seed}: {acc:.4f}")
    return acc
```

### run_all_probes

```python
def run_all_probes(
    test_loader: DataLoader,
    device: str,
) -> dict[str, float]:
    """
    Run probe for all 9 checkpoints (ERM×3, GroupDRO×3, SAM×3).
    Input:  test_loader, device
    Output: dict {"erm_seed1": acc, ..., "sam_seed3": acc}
    """
    results = {}
    ckpt_dir = config.CHECKPOINT_ARCHIVE
    for method in config.METHODS:
        for seed in config.SEEDS:
            ckpt_path = os.path.join(ckpt_dir, f"{method}_seed{seed}.pt")
            model = load_resnet50(ckpt_path, device)
            features, bg_labels = extract_layer4_features(model, test_loader, device)
            del model; gc.collect()
            acc = run_probe(features, bg_labels, method, seed)
            results[f"{method}_seed{seed}"] = acc
    return results
```

### paired_ttest

```python
def paired_ttest(
    erm_accs: list[float],
    gdro_accs: list[float],
) -> tuple[float, float]:
    """
    One-sided paired t-test: H1: ERM > GroupDRO.
    Input:  erm_accs [3], gdro_accs [3]
    Output: (p_value, cohens_d)
    """
    t_stat, p_value = scipy.stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')
    diff = np.array(erm_accs) - np.array(gdro_accs)
    cohens_d = diff.mean() / diff.std(ddof=1)
    print(f"[H-M3] Paired t-test: t={t_stat:.4f}, p={p_value:.4f} (one-sided)")
    print(f"[H-M3] Cohen's d: {cohens_d:.4f}")
    return p_value, cohens_d
```

### gate_verdict

```python
def gate_verdict(
    p_value: float,
    cohens_d: float,
    gdro_mean: float,
    erm_mean: float,
) -> str:
    """
    Input:  p_value, cohens_d, gdro_mean, erm_mean
    Output: 'CONFIRMED' | 'SUGGESTIVE' | 'REJECTED'
    """
    if gdro_mean >= erm_mean:
        verdict = "REJECTED"
    elif p_value < 0.05 and cohens_d > 0:
        verdict = "CONFIRMED"
    elif p_value < 0.10 and cohens_d > 0.5:
        verdict = "SUGGESTIVE"
    else:
        verdict = "REJECTED"
    print(f"[H-M3] Verdict: {verdict}")
    return verdict
```

### save_figures

```python
def save_figures(probe_results: dict[str, float], stat_results: dict) -> None:
    """
    Generate 4 required figures.
    Input:  probe_results {"erm_seed1": acc, ...}, stat_results {"p_value": ..., "cohens_d": ..., "verdict": ...}
    Output: saves 4 PNG files to FIGURES_DIR
    """
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    # Fig1: gate_metrics.png — grouped bar ERM vs GroupDRO, p-value annotation
    # X: [Seed1, Seed2, Seed3], two bars per group (ERM, GroupDRO)
    # Inset: paired differences (ERM_i - GroupDRO_i)

    # Fig2: all_probes.png — 9 checkpoints grouped by method
    # X: methods [erm, groupdro, sam] × seeds [1,2,3], bar chart

    # Fig3: paired_diff.png — scatter (ERM_i - GroupDRO_i) i=1,2,3 + mean±std bar

    # Fig4: probe_vs_wga.png — probe_acc vs WGA for 9 checkpoints, Pearson r annotation
    # WGA values from config.WGA_BY_METHOD_SEED
```

### save_results

```python
def save_results(results: dict) -> None:
    """
    Input:  results dict (see PRD FR-8 schema)
    Output: writes JSON to config.RESULTS_JSON
    """
    with open(config.RESULTS_JSON, 'w') as f:
        json.dump(results, f, indent=2)
```

### generate_validation_report

```python
def generate_validation_report(results: dict) -> None:
    """
    Input:  results dict
    Output: writes 04_validation.md to config.VALIDATION_REPORT
    Sections: gate verdict, probe acc table, stat test, sanity checks, gate result
    """
```

### main (Subtask A-8-1: orchestration flow)

```python
def main() -> None:
    """
    Orchestration:
    1. device = 'cuda' if torch.cuda.is_available() else 'cpu'
    2. test_loader = get_loader('test', config.BATCH_SIZE)
    3. probe_results = run_all_probes(test_loader, device)
    4. erm_accs  = [probe_results[f"erm_seed{s}"]      for s in config.SEEDS]
    5. gdro_accs = [probe_results[f"groupdro_seed{s}"] for s in config.SEEDS]
    6. sam_accs  = [probe_results[f"sam_seed{s}"]      for s in config.SEEDS]
    7. erm_mean, gdro_mean = np.mean(erm_accs), np.mean(gdro_accs)
    8. Sanity checks:
       assert erm_mean > 0.6
       assert all(0.5 <= a <= 1.0 for a in erm_accs + gdro_accs + sam_accs)
    9. p_value, cohens_d = paired_ttest(erm_accs, gdro_accs)
    10. verdict = gate_verdict(p_value, cohens_d, gdro_mean, erm_mean)
    11. Compute SAM exploratory: sam_mean, sam_cohens_d = np.mean(sam_accs), ...
    12. results = build_results_dict(...)
    13. save_figures(probe_results, {"p_value": p_value, "cohens_d": cohens_d, "verdict": verdict})
    14. save_results(results)
    15. generate_validation_report(results)
    16. print summary lines [H-M3]
    """
```

### Subtask A-8-2: error handling

```python
# Sanity check failure → abort with clear message
if erm_mean <= 0.6:
    raise RuntimeError(
        f"[H-M3] ABORT: ERM mean probe acc {erm_mean:.4f} <= 0.6 (A2 violated — metric non-discriminative)"
    )

# Checkpoint not found
if not os.path.exists(ckpt_path):
    raise FileNotFoundError(f"[H-M3] Checkpoint not found: {ckpt_path}")

# WILDS dataset not found
# get_dataset raises if cache missing — let propagate with informative path
```

### Subtask A-6-1: Figure 1 detailed spec

```python
# gate_metrics.png
fig, (ax_main, ax_inset) = plt.subplots(1, 2, figsize=(10, 5))

# ax_main: grouped bar
x = np.arange(3)  # seeds 1,2,3
w = 0.35
ax_main.bar(x - w/2, erm_accs, w, label='ERM', color='steelblue')
ax_main.bar(x + w/2, gdro_accs, w, label='GroupDRO', color='coral')
ax_main.set_xticks(x); ax_main.set_xticklabels(['Seed 1', 'Seed 2', 'Seed 3'])
ax_main.set_ylabel('Background Probe Accuracy')
ax_main.set_title(f'ERM vs GroupDRO Background Probe (p={p_value:.4f})')
ax_main.legend()
ax_main.set_ylim(0.8, 1.0)

# ax_inset: paired differences
diffs = np.array(erm_accs) - np.array(gdro_accs)
ax_inset.bar(x, diffs, color='green', alpha=0.7)
ax_inset.axhline(diffs.mean(), color='red', linestyle='--', label=f'mean={diffs.mean():.4f}')
ax_inset.set_title('Paired Differences (ERM - GroupDRO)')
ax_inset.set_xticks(x); ax_inset.set_xticklabels(['Seed 1', 'Seed 2', 'Seed 3'])
ax_inset.legend()
plt.tight_layout()
plt.savefig(os.path.join(config.FIGURES_DIR, 'gate_metrics.png'), dpi=150)
plt.close()
```

### Subtask A-6-2: Figure 4 detailed spec (probe_vs_wga)

```python
# probe_vs_wga.png
fig, ax = plt.subplots(figsize=(7, 5))
for key, acc in probe_results.items():
    wga = config.WGA_BY_METHOD_SEED.get(key, 0.75)
    method = key.split('_seed')[0]
    color = {'erm': 'steelblue', 'groupdro': 'coral', 'sam': 'green'}.get(method, 'gray')
    ax.scatter(acc, wga, color=color, s=80, label=method)

# Pearson r
accs_all = list(probe_results.values())
wgas_all = [config.WGA_BY_METHOD_SEED.get(k, 0.75) for k in probe_results]
r, pval = scipy.stats.pearsonr(accs_all, wgas_all)
ax.set_xlabel('Background Probe Accuracy'); ax.set_ylabel('WGA')
ax.set_title(f'Probe Accuracy vs WGA (r={r:.3f}, p={pval:.3f})')
# deduplicate legend
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())
plt.tight_layout()
plt.savefig(os.path.join(config.FIGURES_DIR, 'probe_vs_wga.png'), dpi=150)
plt.close()
```

---

## Budget Summary

| Task | Subtasks | Agent |
|------|----------|-------|
| A-8 (orchestration) | A-8-1 (main flow), A-8-2 (error handling) | Logic |
| A-6 (visualization) | A-6-1 (Fig1 spec), A-6-2 (Fig4 spec) | Logic |
| **Total** | **4** | within budget |
