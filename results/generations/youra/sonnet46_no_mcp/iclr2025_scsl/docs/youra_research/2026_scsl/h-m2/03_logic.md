# Logic: H-M2
# Feature Complexity Measurement — Spurious vs. Core Feature Analysis

**Hypothesis ID:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-M1)
**Date:** 2026-05-04

Applied: FFT spatial frequency complexity metric pattern (Geirhos et al. 2019)
Applied: Linear separability probe learning curve pattern (Shah et al. 2020)
Applied: Bootstrap CI for effect size estimation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Green-field — H-M1 code not yet generated (Phase 4 pending). Architecture spec used as reference.
**Analyzed Path**: `h-m1/code/` (not yet created)
**Relevant Symbols**: None — new implementation. ResNet-50 feature extraction pattern re-implemented independently in `resnet_extractor.py` per H-M1 architecture spec.

---

## External Dependencies API

H-M1 code does not exist yet. H-M2 re-implements ResNet-50 feature extraction independently following the same pattern defined in H-M1 architecture. No runtime dependency on H-M1 code.

```python
# Implemented independently in h-m2/code/feature_extractor/resnet_extractor.py
# Pattern source: h-m1/03_architecture.md — GradientAlignmentAnalyzer.extract_features()

class ResNetExtractor:
    def extract_features(
        self,
        loader: DataLoader,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Returns (features: [N, 2048], core_labels: [N,], spurious_labels: [N,])
        ...
```

---

## A-3: Waterbirds Data Pipeline [Complexity: 13, Budget: 2]

Applied: Standard PyTorch Dataset + metadata.csv pattern

### API Signatures

```python
# data_pipeline/waterbirds_loader.py

class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str = "train", transform=None):
        """Load metadata.csv, resolve image and mask paths."""
        # Reads: {root}/metadata.csv  (cols: img_filename, y, place, split, img_id)
        # Mask path: {root}/segmentation_masks/{img_filename}.png (if exists)
        ...

    def __len__(self) -> int: ...

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        # Returns: {
        #   "image": Tensor [3, H, W] (transform applied if given),
        #   "core_label": int,       # y  (bird species 0/1)
        #   "spurious_label": int,   # place (background 0/1)
        #   "mask_path": str,        # empty string if mask not found
        #   "img_path": str,
        # }
        ...


def extract_waterbirds_patches(
    root: str,
    extractor: "PatchExtractor",
    split: str = "train",
    use_masks: bool = True,
) -> Dict[str, np.ndarray]:
    """Extract spurious/core patches from Waterbirds train split.

    Returns dict with keys:
        spurious_patches: np.ndarray  # [N, 64, 64, 3] uint8
        core_patches:     np.ndarray  # [N, 64, 64, 3] uint8
        spurious_labels:  np.ndarray  # [N,] int  (place attribute)
        core_labels:      np.ndarray  # [N,] int  (bird species)
    N ~ 4795 (full train split); logs fallback count if masks missing.
    """
    ...


def get_waterbirds_feature_loader(
    root: str,
    split: str = "train",
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    """DataLoader yielding ImageNet-normalized tensors for ResNet-50 inference.

    Batch yields: {
        "image": Tensor [B, 3, 224, 224],  # Resize256 + CenterCrop224 + ImageNet norm
        "core_label": Tensor [B,],
        "spurious_label": Tensor [B,],
    }
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| spurious_patches | [N, 64, 64, 3] | uint8 raw pixels for FFT |
| core_patches | [N, 64, 64, 3] | uint8 raw pixels for FFT |
| image (loader) | [B, 3, 224, 224] | float32 ImageNet-normalized |

### Pseudo-code: extract_waterbirds_patches

```
1. Build WaterbirdsDataset(root, split, transform=None)
2. spurious_list, core_list, s_labels, c_labels = [], [], [], []
3. fallback_count = 0
4. For each item in dataset (raw PIL images):
   a. Load image as np.ndarray [H, W, 3] uint8
   b. If use_masks and mask_path exists:
        spurious_patch, core_patch = extractor.extract_from_mask(image, mask)
      Else:
        spurious_patch, core_patch = extractor.extract_quadrant(image)
        fallback_count += 1
   c. Append patches and labels
5. Log: f"Waterbirds: {N} patches extracted, {fallback_count} quadrant fallbacks"
6. Assert len(spurious_list) >= 100 and len(core_list) >= 100
7. Return stacked arrays
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | WaterbirdsDataset | `__init__` reads metadata.csv, resolves paths; `__getitem__` loads PIL image + mask path; handles missing masks gracefully |
| L-3-2 | extract_waterbirds_patches + loader | Iterates dataset, dispatches mask vs. quadrant extraction, stacks arrays; `get_waterbirds_feature_loader` uses torchvision transforms (Resize256, CenterCrop224, ImageNet norm) |

---

## A-8: Linear Separability Probe [Complexity: 13, Budget: 2]

Applied: Learning curve AUC pattern (Shah et al. 2020)

### API Signatures

```python
# complexity_metrics/separability_metric.py

def probe_learning_curve(
    features: np.ndarray,          # [N, 2048] float32
    labels: np.ndarray,            # [N,] int
    n_samples_list: List[int],     # e.g. [50, 100, 200, 500, 1000, 2000]
    seeds: List[int],              # e.g. [42, 123, 456]
    c: float = 1.0,
    max_iter: int = 1000,
) -> Dict[str, Any]:
    """Probe accuracy learning curve via LogisticRegression.

    Returns {
        n_samples_list: List[int],
        mean_accs: List[float],          # mean over seeds per N
        std_accs: List[float],
        per_seed_accs: np.ndarray,       # [len(seeds), len(n_samples_list)]
        auc: float,                      # trapz(mean_accs, log(n_samples_list)), normalized
        samples_to_90pct: Optional[int], # smallest n where mean_acc >= 0.90; None if never reached
    }
    """
    ...


def compute_separability_metric(
    features: np.ndarray,           # [N, 2048] float32
    spurious_labels: np.ndarray,    # [N,] int
    core_labels: np.ndarray,        # [N,] int
    n_samples_list: List[int],
    seeds: List[int],
) -> Dict[str, Any]:
    """Run probe_learning_curve for spurious and core labels separately.

    Returns {
        spurious_curve: Dict,           # from probe_learning_curve
        core_curve: Dict,
        auc_ratio: float,               # spurious_auc / core_auc (> 1 = spurious easier)
        samples_to_90_spurious: Optional[int],
        samples_to_90_core: Optional[int],
        direction_correct: bool,        # spurious_auc > core_auc
    }
    """
    ...
```

### Pseudo-code: probe_learning_curve

```
1. Validate: len(features) == len(labels); features.shape[1] == 2048
2. per_seed_accs = np.zeros((len(seeds), len(n_samples_list)))
3. For i, seed in enumerate(seeds):
   rng = np.random.RandomState(seed)
   For j, n in enumerate(n_samples_list):
     n_actual = min(n, len(features))
     idx = rng.choice(len(features), size=n_actual, replace=False)
     X_train, y_train = features[idx], labels[idx]
     clf = LogisticRegression(C=c, max_iter=max_iter, random_state=seed)
     clf.fit(X_train, y_train)
     per_seed_accs[i, j] = clf.score(features, labels)  # eval on full set
4. mean_accs = per_seed_accs.mean(axis=0)
5. std_accs = per_seed_accs.std(axis=0)
6. log_n = np.log(n_samples_list)
7. auc = np.trapz(mean_accs, log_n) / (log_n[-1] - log_n[0])  # normalize to [0,1]
8. samples_to_90pct = first n where mean_accs[j] >= 0.90, else None
9. Return dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | probe_learning_curve | Seed-controlled subsampling loop; LogisticRegression at each N; AUC via log-normalized trapz; samples_to_90pct scan |
| L-8-2 | compute_separability_metric | Calls probe_learning_curve twice (spurious/core labels); computes auc_ratio and direction_correct; handles None samples_to_90pct |

---

## A-2: Patch Extractor [Complexity: 12, Budget: 2]

Applied: Standard PyTorch

### API Signatures

```python
# data_pipeline/patch_extractor.py

class PatchExtractor:
    def __init__(self, patch_size: int = 64):
        self.patch_size = patch_size  # output spatial size

    def extract_from_mask(
        self,
        image: np.ndarray,   # [H, W, 3] uint8
        mask: np.ndarray,    # [H, W] uint8 or bool (foreground=True/255)
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract spurious (background) and core (foreground) patches.

        Returns (spurious_patch, core_patch) each [64, 64, 3] uint8.
        Falls back to extract_quadrant if mask is all-zero or all-one.
        """
        ...

    def extract_quadrant(
        self,
        image: np.ndarray,         # [H, W, 3] uint8
        spurious_top_frac: float = 0.4,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Fallback: top fraction → spurious; center crop → core.

        Returns (spurious_patch, core_patch) each [64, 64, 3] uint8.
        """
        ...

    def extract_celeba_patches(
        self,
        image: np.ndarray,         # [H, W, 3] uint8
        hair_top_frac: float = 0.25,
        face_crop_size: int = 112,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """CelebA: top hair_top_frac → spurious; center face crop → core.

        Returns (spurious_patch, core_patch) each [64, 64, 3] uint8.
        """
        ...

    def to_imagenet_tensor(self, patch_uint8: np.ndarray) -> "torch.Tensor":
        """Convert [64, 64, 3] uint8 → [3, 224, 224] float32 ImageNet-normalized tensor."""
        # Resize to 256 → CenterCrop 224 → ToTensor → Normalize
        ...
```

### Pseudo-code: extract_from_mask

```
1. Validate mask is binary (0/255 or bool); reshape to [H, W]
2. If mask.sum() < 0.01 * H * W or mask.sum() > 0.99 * H * W:
     return extract_quadrant(image)  # degenerate mask fallback
3. bg_pixels = image[mask == 0]  # background → spurious
4. fg_pixels = image[mask != 0]  # foreground → core
5. bg_bbox = bounding_box(mask == 0); fg_bbox = bounding_box(mask != 0)
6. spurious_crop = image[bg_bbox]; core_crop = image[fg_bbox]
7. spurious_patch = PIL.Image.fromarray(spurious_crop).resize((64,64))
8. core_patch = PIL.Image.fromarray(core_crop).resize((64,64))
9. Return (np.array(spurious_patch), np.array(core_patch))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | extract_from_mask | Bounding box of fg/bg mask regions; resize crops to patch_size; fallback to quadrant on degenerate mask |
| L-2-2 | extract_quadrant + extract_celeba_patches + to_imagenet_tensor | Top-N-row crop for spurious; center square crop for core; PIL resize; ImageNet normalization pipeline |

---

## A-9: Statistical Analysis & Gate [Complexity: 12, Budget: 2]

Applied: Bonferroni correction, bootstrap CI pattern

### API Signatures

```python
# analysis/statistical_tests.py

def apply_bonferroni_correction(
    p_values: Dict[str, float],  # {metric_name: p_value}
    alpha: float = 0.05,
) -> Dict[str, float]:
    """Return corrected alpha thresholds per test. 6 tests → alpha/6 = 0.0083."""
    ...


def evaluate_gate(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Evaluate SHOULD_WORK gate.

    Gate rule: >=2/3 metrics direction_correct AND p_value < alpha on Waterbirds.
    Secondary: >=2/3 directional match on CelebA (no p-value requirement).

    Returns {
        gate_pass: bool,
        n_metrics_pass_waterbirds: int,    # metrics with direction_correct & p < alpha
        n_metrics_pass_celeba: int,        # metrics direction_correct only
        gate_label: str,                   # "PASS" | "FAIL"
        per_metric_result: Dict[str, Dict] # per-metric breakdown
    }
    """
    ...


def compute_complexity_delta_ci(
    spurious_vals: np.ndarray,   # [N,] per-sample complexity values
    core_vals: np.ndarray,       # [M,] per-sample complexity values
    confidence: float = 0.95,
) -> Dict[str, float]:
    """Bootstrap 95% CI for delta = mean(core) - mean(spurious).

    Returns {
        delta: float,
        ci_low: float,
        ci_high: float,
        n_bootstrap: int,   # 10000
        significant: bool,  # ci_low > 0
    }
    """
    ...
```

### Pseudo-code: evaluate_gate

```
metrics = ["fft", "variance", "separability"]
per_metric_result = {}
n_pass_wb = 0
n_pass_cb = 0

For metric in metrics:
  wb = waterbirds_results[metric]
  cb = celeba_results[metric]
  direction_ok_wb = wb["direction_correct"]
  p_ok_wb = wb["p_value"] < alpha
  direction_ok_cb = cb["direction_correct"]
  if direction_ok_wb and p_ok_wb: n_pass_wb += 1
  if direction_ok_cb: n_pass_cb += 1
  per_metric_result[metric] = {wb, cb results}

gate_pass = n_pass_wb >= 2
gate_label = "PASS" if gate_pass else "FAIL"
```

### Pseudo-code: compute_complexity_delta_ci

```
delta = mean(core_vals) - mean(spurious_vals)
boot_deltas = []
rng = np.random.RandomState(42)
For _ in range(10000):
  s_boot = rng.choice(spurious_vals, size=len(spurious_vals), replace=True)
  c_boot = rng.choice(core_vals, size=len(core_vals), replace=True)
  boot_deltas.append(mean(c_boot) - mean(s_boot))
ci_low = percentile(boot_deltas, 2.5)
ci_high = percentile(boot_deltas, 97.5)
significant = ci_low > 0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | evaluate_gate + apply_bonferroni_correction | Extract direction_correct and p_value from each metric result dict; count passing metrics; Bonferroni: corrected_alpha = alpha / n_tests |
| L-9-2 | compute_complexity_delta_ci | 10k bootstrap resampling of spurious/core value arrays; 2.5/97.5 percentile CI; significant if ci_low > 0 |

---

## A-6: FFT Complexity Metric [Complexity: 11, Budget: 2]

Applied: FFT spatial frequency complexity metric (Geirhos et al. 2019)

### API Signatures

```python
# complexity_metrics/fft_metric.py

def compute_mean_spatial_frequency(patch: np.ndarray) -> float:
    """Compute weighted mean spatial frequency of a patch.

    patch: [H, W, 3] or [H, W] uint8
    Returns scalar float: sum(|F|^2 * freq_grid) / sum(|F|^2)
    Higher value = higher frequency content = more complex texture.
    """
    ...


def compute_fft_metric(
    spurious_patches: np.ndarray,   # [N, 64, 64, 3] uint8
    core_patches: np.ndarray,       # [M, 64, 64, 3] uint8
) -> Dict[str, Any]:
    """Compute FFT complexity metric and t-test.

    Returns {
        spurious_mean_freq: float,
        core_mean_freq: float,
        spurious_freqs: List[float],   # per-patch, length N
        core_freqs: List[float],       # per-patch, length M
        t_stat: float,
        p_value: float,
        direction_correct: bool,       # spurious_mean_freq < core_mean_freq
    }
    """
    ...
```

### Pseudo-code: compute_mean_spatial_frequency

```
1. If patch.ndim == 3: gray = 0.299*R + 0.587*G + 0.114*B  # [H, W]
   Else: gray = patch.astype(float)
2. F = np.fft.fft2(gray)
3. F_shift = np.fft.fftshift(F)
4. power = np.abs(F_shift) ** 2  # [H, W]
5. H, W = gray.shape
6. freq_y = np.fft.fftfreq(H)  # cycles/pixel
7. freq_x = np.fft.fftfreq(W)
8. freq_y_shift = np.fft.fftshift(freq_y)
9. freq_x_shift = np.fft.fftshift(freq_x)
10. freq_grid = np.sqrt(freq_y_shift[:,None]**2 + freq_x_shift[None,:]**2)  # [H, W]
11. mean_freq = (power * freq_grid).sum() / (power.sum() + 1e-10)
12. Return float(mean_freq)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_mean_spatial_frequency | Grayscale conversion; fft2 + fftshift; radial frequency grid; power-weighted mean; epsilon denominator guard |
| L-6-2 | compute_fft_metric | Vectorized per-patch frequency computation; scipy.stats.ttest_ind on freq arrays; direction_correct = spurious_mean < core_mean |

---

## A-4: CelebA Data Pipeline [Complexity: 11, Budget: 2]

Applied: Stratified group sampling pattern (4 groups × samples_per_group)

### API Signatures

```python
# data_pipeline/celeba_loader.py

def extract_celeba_patches(
    root: str,
    extractor: "PatchExtractor",
    samples_per_group: int = 5000,
    split: str = "train",
) -> Dict[str, np.ndarray]:
    """Stratified sample from 4 CelebA groups; extract hair/face patches.

    Groups: {(blond=0, male=0), (blond=0, male=1), (blond=1, male=0), (blond=1, male=1)}
    Spurious attr: hair_color (attr index 9, blond=1)
    Core attr: gender (attr index 20, male=1)

    Returns {
        spurious_patches: np.ndarray,   # [N, 64, 64, 3] uint8  (hair crop)
        core_patches:     np.ndarray,   # [N, 64, 64, 3] uint8  (face crop)
        spurious_labels:  np.ndarray,   # [N,] int  (blond label)
        core_labels:      np.ndarray,   # [N,] int  (gender label)
    }
    N = min(samples_per_group, group_size) × 4 groups
    """
    ...


def get_celeba_feature_loader(
    root: str,
    samples_per_group: int = 5000,
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    """DataLoader for ImageNet-normalized CelebA images.

    Batch yields: {
        "image": Tensor [B, 3, 224, 224],   # ImageNet-normalized
        "spurious_label": Tensor [B,],       # blond
        "core_label": Tensor [B,],           # gender
    }
    """
    ...
```

### Pseudo-code: extract_celeba_patches

```
1. ds = torchvision.datasets.CelebA(root, split=split, target_type="attr", download=False)
2. attrs = ds.attr  # [total_N, 40] int tensor
3. blond_col, gender_col = 9, 20
4. groups = [(0,0), (0,1), (1,0), (1,1)]  # (blond, male)
5. all_spurious, all_core, all_sl, all_cl = [], [], [], []
6. For (b, g) in groups:
   mask = (attrs[:, blond_col] == b) & (attrs[:, gender_col] == g)
   indices = np.where(mask)[0]
   rng = np.random.RandomState(42)
   chosen = rng.choice(indices, size=min(samples_per_group, len(indices)), replace=False)
   For idx in chosen:
     img, _ = ds[int(idx)]  # PIL Image
     img_arr = np.array(img)  # [H, W, 3]
     sp_patch, co_patch = extractor.extract_celeba_patches(img_arr)
     all_spurious.append(sp_patch); all_core.append(co_patch)
     all_sl.append(b); all_cl.append(g)
7. Return stacked arrays
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | extract_celeba_patches | Load torchvision CelebA; build group masks from attr columns 9/20; stratified rng.choice per group; call extractor.extract_celeba_patches per image |
| L-4-2 | get_celeba_feature_loader | CelebAFeatureDataset wrapping sampled indices; Resize256+CenterCrop224+ImageNet-norm transform; DataLoader with num_workers |

---

## Edge Cases & Error Conditions

| Case | Module | Handling |
|------|--------|----------|
| Degenerate mask (all-fg or all-bg) | extract_from_mask | Fallback to extract_quadrant; log warning |
| n_samples > len(features) in probe | probe_learning_curve | Clamp to len(features); skip that N in AUC if all available |
| CelebA group size < samples_per_group | extract_celeba_patches | Use all available samples; log actual count |
| FFT denominator near zero | compute_mean_spatial_frequency | Add 1e-10 to denominator |
| < 100 patches extracted | extract_waterbirds_patches | Raise ValueError with descriptive message |
| samples_to_90pct never reached | probe_learning_curve | Return None; downstream handles gracefully |

---

## Test Assertions

```python
# Smoke test assertions (Phase 4 E2E validation)

# Patch extraction
assert spurious_patches.shape == (N, 64, 64, 3), f"Expected [N,64,64,3], got {spurious_patches.shape}"
assert spurious_patches.dtype == np.uint8
assert N >= 100, "Need at least 100 patches per class"

# FFT metric
assert 0 < result["spurious_mean_freq"] < 1.0
assert 0 < result["core_mean_freq"] < 1.0
assert isinstance(result["direction_correct"], bool)

# Probe learning curve
assert len(curve["mean_accs"]) == len(n_samples_list)
assert curve["per_seed_accs"].shape == (len(seeds), len(n_samples_list))
assert 0.0 <= curve["auc"] <= 1.0

# Gate
assert gate_result["gate_pass"] in [True, False]
assert gate_result["n_metrics_pass_waterbirds"] in [0, 1, 2, 3]

# Bootstrap CI
assert ci_result["ci_low"] <= ci_result["delta"] <= ci_result["ci_high"]
```
