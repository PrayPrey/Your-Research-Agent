# Logic Design: H-P0
## DFR Backbone Identity Sanity Check — API Signatures & Pseudo-code

**hypothesis_id:** h-p0
**hypothesis_type:** EXISTENCE
**tier:** LIGHT
**generated_at:** 2026-08-05

Applied: Standard PyTorch inference pattern (forward hook, cosine similarity — no domain-specific Archon KB match; Archon KB indexed for diffusers, not spurious correlation research)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase to analyze — new implementation from scratch
**Analyzed Path**: N/A
**Findings**: All API signatures derived from izmailovpavel/spurious_feature_learning reference implementation and standard PyTorch/sklearn patterns. No Serena analysis needed (green-field).

---

## Module: `h-p0/code/run_experiment.py`

### Function 1: `get_transform`

```python
def get_transform() -> transforms.Compose:
    """Return standard ImageNet normalization transform."""
```

**Returns:** `transforms.Compose` with Resize(256) → CenterCrop(224) → ToTensor() → Normalize(ImageNet mean/std)

**Pseudo-code:**
```
return transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```

---

### Function 2: `load_test_images`

```python
def load_test_images(
    n: int = 50,
    seed: int = 42,
    wilds_cache: str = "/home/PrayPrey/.wilds_cache"
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Load fixed subset of Waterbirds WILDS test images.

    Returns:
        images: (n, 3, 224, 224) float32 tensor
        background_labels: (n,) int64 tensor — group_array % 2 (0=land, 1=water)
    """
```

**Tensor shapes:**
- Output images: `(50, 3, 224, 224)` float32
- Output background_labels: `(50,)` int64

**Pseudo-code:**
```
dataset = get_dataset(dataset='waterbirds', download=False, root_dir=wilds_cache)
test_data = dataset.get_subset('test', transform=get_transform())
# test split has 5794 images

torch.manual_seed(seed)
indices = torch.randperm(len(test_data))[:n]  # first n after seeded permutation

images = []
labels = []
for idx in indices:
    x, y, metadata = test_data[idx]
    images.append(x)
    labels.append(metadata[0] % 2)  # group_array % 2 = background label

images = torch.stack(images)        # (50, 3, 224, 224)
labels = torch.tensor(labels)       # (50,)
return images, labels
```

**Notes:**
- Uses `torch.manual_seed(42)` for reproducible fixed subset
- `metadata[0]` = `group_array` ∈ {0,1,2,3} → `% 2` gives background (0=land, 1=water)

---

### Function 3: `download_checkpoint`

```python
def download_checkpoint(
    seed: int,
    method: str,
    hf_repo: str = "izmailovpavel/spurious_feature_learning",
    local_dir: str = "./checkpoints"
) -> pathlib.Path:
    """
    Download checkpoint from HuggingFace Hub.

    Args:
        seed: 1, 2, or 3
        method: "erm" or "dfr"

    Returns:
        Path to local checkpoint file
    """
```

**Pseudo-code:**
```
filename = f"{method}_seed{seed}/final_checkpoint.pt"
local_path = hf_hub_download(
    repo_id=hf_repo,
    filename=filename,
    local_dir=local_dir,
    repo_type="model"
)
return Path(local_path)
```

**Notes:**
- `huggingface_hub.hf_hub_download` caches locally — safe to call multiple times
- Checkpoint naming: `erm_seed1/final_checkpoint.pt`, `dfr_seed1/final_checkpoint.pt`, etc.

---

### Function 4: `load_model`

```python
def load_model(
    ckpt_path: pathlib.Path,
    device: str = "cuda",
    n_classes: int = 2
) -> torch.nn.Module:
    """
    Load ResNet-50 from izmailovpavel checkpoint.

    Returns:
        model: ResNet-50 in eval mode on specified device
    """
```

**Pseudo-code:**
```
# imagenet_resnet50_pretrained: torchvision ResNet-50 with replaced fc(2048→n_classes)
# Either import from cloned izmailovpavel repo OR reimplement:
model = torchvision.models.resnet50(pretrained=False)
model.fc = torch.nn.Linear(2048, n_classes)

ckpt_dict = torch.load(ckpt_path, map_location='cpu')
model.load_state_dict(ckpt_dict)
model = model.to(device)
model.eval()
return model
```

**Notes:**
- `map_location='cpu'` avoids GPU OOM during loading; move to device afterward
- No 1→2 output adaptation needed for DFR/ERM (both use n_classes=2)

---

### Function 5: `extract_layer4_features`

```python
def extract_layer4_features(
    model: torch.nn.Module,
    images: torch.Tensor,
    device: str = "cuda"
) -> torch.Tensor:
    """
    Extract pooled layer4 features from ResNet-50.

    Args:
        images: (B, 3, 224, 224) float32

    Returns:
        features: (B, 2048) float32
    """
```

**Tensor shapes:**
- Input: `(50, 3, 224, 224)` float32
- layer4 hook output: `(50, 2048, 7, 7)` float32
- After AdaptiveAvgPool2d(1,1): `(50, 2048, 1, 1)` float32
- After flatten: `(50, 2048)` float32

**Pseudo-code:**
```
captured = []
def hook_fn(module, input, output):
    captured.append(output.detach().cpu())

handle = model.layer4.register_forward_hook(hook_fn)

with torch.no_grad():
    _ = model(images.to(device))

handle.remove()

feat = captured[0]  # (50, 2048, 7, 7)
pool = torch.nn.AdaptiveAvgPool2d((1, 1))
feat = pool(feat).flatten(1)  # (50, 2048)
return feat
```

**Notes:**
- Register hook BEFORE forward pass, remove AFTER to avoid accumulation
- `.detach().cpu()` in hook prevents GPU memory accumulation
- AdaptiveAvgPool2d mirrors ResNet-50's `avgpool` layer behavior

---

### Function 6: `compute_cosine_similarity`

```python
def compute_cosine_similarity(
    feat1: torch.Tensor,
    feat2: torch.Tensor
) -> dict:
    """
    Compute pairwise cosine similarity between two feature sets.

    Args:
        feat1: (N, 2048) float32 — ERM features
        feat2: (N, 2048) float32 — DFR features

    Returns:
        dict with keys:
            mean: float — mean cosine similarity across N pairs
            variance: float — variance of per-sample similarities
            per_sample: Tensor(N,) — per-sample cosine similarities
    """
```

**Tensor shapes:**
- Both inputs: `(50, 2048)` float32
- `per_sample` output: `(50,)` float32 ∈ [-1, 1]

**Pseudo-code:**
```
sim = F.cosine_similarity(feat1, feat2, dim=1)  # (N,)
return {
    'mean': sim.mean().item(),
    'variance': sim.var().item(),
    'per_sample': sim
}
```

**Gate condition:** `mean >= 0.9999 AND variance < 1e-6`

---

### Function 7: `run_probe`

```python
def run_probe(
    features: torch.Tensor,
    background_labels: torch.Tensor
) -> float:
    """
    Fit sklearn logistic regression probe on ERM features vs background label.

    Args:
        features: (N, 2048) float32
        background_labels: (N,) int64 — 0=land, 1=water

    Returns:
        accuracy: float — probe accuracy ∈ [0, 1]
    """
```

**Pseudo-code:**
```
X = features.numpy()          # (N, 2048)
y = background_labels.numpy() # (N,)

clf = LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)
# Use cross-val or simple fit+score (50 samples — just sanity check)
from sklearn.model_selection import cross_val_score
scores = cross_val_score(clf, X, y, cv=5, scoring='accuracy')
return scores.mean()
```

**Notes:**
- 50 samples is minimal for 5-fold CV; alternatively fit on all 50 and report train accuracy (sanity only)
- C=1e9 = near-zero regularization (consistent with Phase 2C spec)
- Secondary check only — not gate-blocking

---

### Function 8: `evaluate_gate`

```python
def evaluate_gate(
    results: dict
) -> bool:
    """
    Evaluate MUST_WORK gate for H-P0.

    Args:
        results: {seed: {'mean_cosine_sim': float, 'variance': float}}

    Returns:
        gate_passed: bool — True iff all seeds pass both thresholds
    """
```

**Pseudo-code:**
```
gate_passed = True
for seed, r in results.items():
    if r['mean_cosine_sim'] < GATE_MEAN_SIM:
        gate_passed = False
        print(f"FAIL seed {seed}: mean_cosine_sim={r['mean_cosine_sim']:.6f} < {GATE_MEAN_SIM}")
    if r['variance'] >= GATE_VARIANCE:
        gate_passed = False
        print(f"FAIL seed {seed}: variance={r['variance']:.2e} >= {GATE_VARIANCE}")

return gate_passed
```

---

### Function 9: `save_figures`

```python
def save_figures(
    results: dict,
    output_dir: str = "h-p0/figures"
) -> None:
    """
    Save visualization figures.

    Args:
        results: {seed: {'mean_cosine_sim': float, 'variance': float, 'per_sample': Tensor(50,)}}
    """
```

**Required figures:**
1. **Bar chart** (`cosine_similarity_per_seed.png`): 3 bars (seeds 1-3), mean cosine similarity, red dashed line at 0.9999 threshold
2. **Histogram** (`per_sample_distribution.png`): 3 subplots, per-sample cosine similarity distribution (50 samples each), x-axis [0.999, 1.001]
3. **PCA scatter** (`pca_feature_scatter.png`): 2D PCA of ERM vs DFR features for seed 1

**Pseudo-code for bar chart:**
```
fig, ax = plt.subplots()
seeds = [1, 2, 3]
means = [results[s]['mean_cosine_sim'] for s in seeds]
ax.bar(seeds, means, color='steelblue')
ax.axhline(y=0.9999, color='red', linestyle='--', label='Gate threshold (0.9999)')
ax.set_ylim([0.9990, 1.0005])
ax.set_xlabel('Seed'); ax.set_ylabel('Mean Cosine Similarity')
ax.set_title('DFR vs ERM Layer4 Feature Cosine Similarity (H-P0)')
ax.legend()
plt.savefig(f"{output_dir}/cosine_similarity_per_seed.png", dpi=150, bbox_inches='tight')
plt.close()
```

---

### Function 10: `save_results`

```python
def save_results(
    results: dict,
    gate_passed: bool,
    probe_acc: float,
    output_dir: str = "h-p0"
) -> None:
    """
    Save results.json and 04_validation.md.
    """
```

**results.json schema:**
```json
{
  "hypothesis_id": "h-p0",
  "gate_passed": true,
  "gate_threshold_mean_sim": 0.9999,
  "gate_threshold_variance": 1e-6,
  "per_seed": {
    "1": {"mean_cosine_sim": 1.0, "variance": 0.0},
    "2": {"mean_cosine_sim": 1.0, "variance": 0.0},
    "3": {"mean_cosine_sim": 1.0, "variance": 0.0}
  },
  "secondary_probe_accuracy": 0.72,
  "conclusion": "PASS: DFR and ERM backbones are numerically identical"
}
```

---

### Function 11: `main`

```python
def main() -> None:
    """
    Orchestrate full H-P0 sanity check experiment.
    """
```

**Pseudo-code:**
```
# Setup
os.makedirs("h-p0/figures", exist_ok=True)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load fixed test images once
images, background_labels = load_test_images(n=50, seed=42)

# Run per-seed comparison
results = {}
erm_features_seed1 = None

for seed in [1, 2, 3]:
    # Load ERM checkpoint
    erm_ckpt = download_checkpoint(seed=seed, method="erm")
    erm_model = load_model(erm_ckpt, device=device)
    erm_feats = extract_layer4_features(erm_model, images, device=device)
    del erm_model  # free GPU memory

    # Load DFR checkpoint
    dfr_ckpt = download_checkpoint(seed=seed, method="dfr")
    dfr_model = load_model(dfr_ckpt, device=device)
    dfr_feats = extract_layer4_features(dfr_model, images, device=device)
    del dfr_model

    # Compute cosine similarity
    sim_result = compute_cosine_similarity(erm_feats, dfr_feats)
    results[seed] = {
        'mean_cosine_sim': sim_result['mean'],
        'variance': sim_result['variance'],
        'per_sample': sim_result['per_sample'],
        'erm_feats': erm_feats,  # keep seed1 for probe
    }
    print(f"Seed {seed}: mean_cosine_sim={sim_result['mean']:.6f}, variance={sim_result['variance']:.2e}")

    if seed == 1:
        erm_features_seed1 = erm_feats

# Gate evaluation
gate_passed = evaluate_gate(results)
print(f"H-P0 Gate: {'PASS' if gate_passed else 'FAIL'}")

# Secondary validation: ERM probe accuracy
probe_acc = run_probe(erm_features_seed1, background_labels)
print(f"ERM probe accuracy (background): {probe_acc:.3f}")

# Outputs
save_figures(results)
save_results(results, gate_passed, probe_acc)
```

---

## Verification Assertions

```python
# Shape verification (add to extract_layer4_features)
assert erm_feats.shape == (50, 2048), f"ERM feature shape wrong: {erm_feats.shape}"
assert dfr_feats.shape == (50, 2048), f"DFR feature shape wrong: {dfr_feats.shape}"
assert erm_feats.norm(dim=1).min() > 0, "ERM features contain zero vectors"
assert dfr_feats.norm(dim=1).min() > 0, "DFR features contain zero vectors"
```

---

*Generated from: h-p0/02c_experiment_brief.md + h-p0/03_architecture.md + h-p0/03_prd.md*
*Archon KB: no domain-relevant results (diffusers content, <0.49 similarity)*
*Serena MCP: skipped (green-field project)*
