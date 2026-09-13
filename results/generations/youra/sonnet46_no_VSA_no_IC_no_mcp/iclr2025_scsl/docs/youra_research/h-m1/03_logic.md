# Logic Design: H-M1
# SimCLR Background-Replacement Augmentation — Mechanism Hypothesis

---
stepsCompleted:
  - logic
hypothesis_id: h-m1
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-26T10:35:00Z"
---

Applied: Causal-isolation two-view contrastive API pattern
Applied: Frozen-backbone linear-probe evaluation pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. All APIs designed from PRD + architecture specs.

---

## Subtask: L-E3-1 — BackgroundReplacementTransform.__call__

**Epic**: E3 — Background Replacement Augmentation

### API Signature

```python
def __call__(
    self,
    image: Image.Image,       # (H, W, 3) PIL RGB image
    seg_mask: Image.Image,    # (H, W) binary PIL image: 255=bird, 0=background
) -> tuple[Tensor, Tensor]:   # (view1, view2) each (3, 224, 224) normalized tensors
```

### Tensor Shape Flow

```
image PIL (H, W, 3)
seg_mask PIL (H, W)
  ↓ np.array(seg_mask) > 127  →  mask_bool (H, W) bool
  ↓ sample bg1, bg2 from Places365Pool  →  bg1_arr, bg2_arr (H, W, 3)
  ↓ np.where(mask[:,:,None], img_arr, bg_arr)  →  replaced1, replaced2 (H, W, 3)
  ↓ self.simclr_transform(Image.fromarray(replaced1))  →  view1 (3, 224, 224)
  ↓ self.simclr_transform(Image.fromarray(replaced2))  →  view2 (3, 224, 224)
```

### Pseudo-code

```python
def __call__(self, image: Image.Image, seg_mask: Image.Image):
    img_arr = np.array(image)                        # (H, W, 3) uint8
    mask_bool = np.array(seg_mask) > 127             # (H, W) bool; True=bird

    # Each view gets an INDEPENDENT background sample
    bg1 = np.array(self.places_pool.sample().resize(image.size, Image.BILINEAR))
    bg2 = np.array(self.places_pool.sample().resize(image.size, Image.BILINEAR))

    replaced1 = np.where(mask_bool[:, :, None], img_arr, bg1).astype(np.uint8)
    replaced2 = np.where(mask_bool[:, :, None], img_arr, bg2).astype(np.uint8)

    view1 = self.simclr_transform(Image.fromarray(replaced1))
    view2 = self.simclr_transform(Image.fromarray(replaced2))
    return view1, view2

# Key invariants:
# - mask_bool[:,:,None] broadcasts (H,W) → (H,W,1) for element-wise selection
# - Bird pixels (mask=True) are preserved from original image
# - Background pixels (mask=False) are replaced from Places365
# - Two independent backgrounds → makes background a non-stable feature across views
```

### Edge Cases

- `image.size != seg_mask.size`: resize mask to match image before conversion
- Places365Pool exhausted: pool is pre-loaded list; sampling is `random.choice`, never exhausted
- Alpha channel in mask: threshold > 127 handles both binary {0,255} and soft masks

---

## Subtask: L-E3-2 — verify_mechanism_activated()

**Epic**: E3 — Background Replacement Augmentation

### API Signature

```python
def verify_mechanism_activated(
    augmented_view: Tensor,    # (3, H, W) tensor, pixel values in [0,1] or normalized
    original_image: Tensor,    # (3, H, W) tensor, same preprocessing
    seg_mask: Tensor,          # (H, W) bool tensor, True=bird foreground
    threshold: float = 0.05,
) -> dict:                     # {"background_changed": bool, "pixel_diff": float, "mechanism_active": bool}
```

### Pseudo-code

```python
def verify_mechanism_activated(augmented_view, original_image, seg_mask, threshold=0.05):
    bg_mask = ~seg_mask                              # (H, W) True=background
    bg_pixels_view = augmented_view[:, bg_mask]     # (3, N_bg_pixels)
    bg_pixels_orig = original_image[:, bg_mask]     # (3, N_bg_pixels)

    pixel_diff = (bg_pixels_view - bg_pixels_orig).abs().mean().item()

    result = {
        "background_changed": pixel_diff > threshold,
        "pixel_diff": pixel_diff,
        "mechanism_active": pixel_diff > threshold,
    }
    assert result["mechanism_active"], (
        f"FAIL: Background replacement not active — pixel_diff={pixel_diff:.4f} "
        f"(threshold={threshold}). Check CUB mask loading and Places365 pool."
    )
    return result

# Key invariant: call on FIRST batch before training starts (trainer._verify_mechanism)
# Normalization: both tensors must use same normalization; diff is still meaningful
```

---

## Subtask: L-E3-3 — DataLoader integration for two-view augmentation

**Epic**: E3 — Background Replacement Augmentation

### API Signature

```python
class SimCLRDataset(Dataset):
    def __init__(
        self,
        wilds_dataset,          # WILDS WaterbirdsDataset subset
        mask_index: dict,       # {wilds_idx: cub_mask_path}
        transform,              # SimCLRTransform (Original) OR BackgroundReplacementTransform (NoBackground)
        condition: str,         # "original" | "no_background"
    ): ...

    def __getitem__(self, idx: int) -> tuple:
        # Returns: (view1, view2, bird_label, background_label)
        # view1, view2: (3, 224, 224) tensors
```

### Pseudo-code

```python
def __getitem__(self, idx):
    image, labels, metadata = self.wilds_dataset[idx]
    # image: PIL Image (already loaded by WILDS)
    bird_label = labels[0].item()       # 0=landbird, 1=waterbird
    background_label = metadata[0].item()  # 0=land, 1=water

    if self.condition == "original":
        view1 = self.transform(image)
        view2 = self.transform(image)
    else:  # no_background
        mask_path = self.mask_index[idx]
        seg_mask = Image.open(mask_path).convert("L")
        seg_mask = seg_mask.resize(image.size, Image.NEAREST)
        view1, view2 = self.transform(image, seg_mask)

    return view1, view2, bird_label, background_label

# DataLoader: num_workers=4, pin_memory=True, drop_last=True (NT-Xent needs full batches)
```

---

## Subtask: L-E3-4 — CUB mask loading + resize pipeline

**Epic**: E3 — Background Replacement Augmentation

### API Signature

```python
def load_cub_mask(mask_path: str, target_size: tuple[int, int]) -> Image.Image:
    """Load and resize CUB segmentation mask to target_size (W, H)."""

def build_mask_index(
    waterbirds_metadata_csv: str,   # path to Waterbirds metadata.csv
    cub_segmentations_dir: str,     # path to CUB_200_2011/segmentations/
) -> dict[int, str]:                # {waterbirds_idx: absolute_mask_path}
```

### Pseudo-code (build_mask_index)

```python
def build_mask_index(waterbirds_metadata_csv, cub_segmentations_dir):
    df = pd.read_csv(waterbirds_metadata_csv)
    # metadata.csv columns: img_id, img_filename, y, split, place, ...
    # img_filename format: "001.Black_footed_Albatross/Black_Footed_Albatross_0001.jpg"

    index = {}
    for wilds_idx, row in df.iterrows():
        img_filename = row["img_filename"]           # e.g. "001.Black.../image.jpg"
        # Mask path mirrors image path with .png extension
        mask_rel = img_filename.replace(".jpg", ".png")
        mask_abs = os.path.join(cub_segmentations_dir, mask_rel)
        if not os.path.exists(mask_abs):
            raise FileNotFoundError(
                f"CUB mask missing: {mask_abs}\n"
                "Download CUB-200-2011 from http://www.vision.caltech.edu/datasets/cub_200_2011/"
            )
        index[wilds_idx] = mask_abs
    return index

# Key invariant: called ONCE at dataset init; fail-fast if any mask missing
```

---

## Subtask: L-E5-1 — SimCLRTrainer.train()

**Epic**: E5 — SimCLR Training Loop

### API Signature

```python
def train(self) -> str:
    """Train SimCLR for self.config.epochs. Returns path to saved checkpoint."""
```

### Pseudo-code

```python
def train(self) -> str:
    self._set_seed(self.seed)
    model = SimCLRModel().to(self.device)
    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs, eta_min=0)
    criterion = NTXentLoss(temperature=cfg.temperature)
    loader = self._build_loader()   # SimCLRDataset + DataLoader

    if self.condition == "no_background":
        self._verify_mechanism(loader)   # Halt if pixel_diff < 0.05

    for epoch in range(cfg.epochs):
        model.train()
        epoch_loss = 0.0
        for view1, view2, _, _ in loader:
            view1, view2 = view1.to(device), view2.to(device)
            optimizer.zero_grad()
            _, z1 = model(view1)    # z1: (B, 128) L2-normalized
            _, z2 = model(view2)    # z2: (B, 128) L2-normalized
            loss = criterion(z1, z2)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        scheduler.step()
        log(f"Epoch {epoch+1}/{cfg.epochs} | loss={epoch_loss/len(loader):.4f}")

    ckpt_path = cfg.checkpoint_path(self.condition, self.seed)
    torch.save({"backbone": model.get_backbone().state_dict()}, ckpt_path)
    return ckpt_path
```

---

## Subtask: L-E5-2 — NTXentLoss.forward()

**Epic**: E5 — SimCLR Training Loop

### Tensor Shape Flow

```
z1: (B, 128) L2-normalized
z2: (B, 128) L2-normalized
  ↓ cat([z1, z2], dim=0)          → z: (2B, 128)
  ↓ mm(z, z.T)                    → sim_raw: (2B, 2B)  cosine similarities (already normalized)
  ↓ sim_raw / temperature         → sim: (2B, 2B)
  ↓ mask diagonal (self-sim)      → sim: (2B, 2B)  -inf on diagonal
  ↓ positive labels               → labels: (2B,)
  ↓ cross_entropy(sim, labels)    → scalar loss
```

### Pseudo-code

```python
def forward(self, z1: Tensor, z2: Tensor) -> Tensor:
    B = z1.shape[0]
    z = torch.cat([z1, z2], dim=0)          # (2B, 128)
    sim = torch.mm(z, z.t()) / self.temperature  # (2B, 2B); cosine sim (z already L2-normed)

    # Mask self-similarity (diagonal)
    mask = torch.eye(2 * B, dtype=torch.bool, device=z.device)
    sim.masked_fill_(mask, float('-inf'))

    # Positive pair labels: z1[i] pairs with z2[i] = position i+B in concat
    labels = torch.cat([
        torch.arange(B, 2 * B, device=z.device),   # z1[i] → z2[i] at position i+B
        torch.arange(B, device=z.device),           # z2[i] → z1[i] at position i
    ])
    return F.cross_entropy(sim, labels)

# Key: z must be L2-normalized before calling (ProjectionHead outputs normalized)
# Key: drop_last=True in DataLoader ensures B is constant (avoids shape mismatch)
```

---

## Subtask: L-E5-3 — Collapse detection logic

**Epic**: E5 — SimCLR Training Loop

### API Signature

```python
def check_collapse(
    task_probe_acc: float,
    majority_class_baseline: float = 0.534,  # Waterbirds majority class
) -> dict:
    # Returns: {"collapsed": bool, "task_probe_acc": float, "threshold": float}
```

### Pseudo-code

```python
def check_collapse(task_probe_acc, majority_class_baseline=0.534):
    collapsed = task_probe_acc < majority_class_baseline
    result = {
        "collapsed": collapsed,
        "task_probe_acc": task_probe_acc,
        "threshold": majority_class_baseline,
    }
    if collapsed:
        logger.warning(
            f"COLLAPSE DETECTED: task_probe_acc={task_probe_acc:.3f} < {majority_class_baseline:.3f}. "
            f"Seed marked FAILED. Continuing to next seed."
        )
    return result

# Waterbirds majority class: ~726/4795 ≈ 53.4% (landbird-on-land dominant class)
# Collapse = representation no better than predicting majority class
# Action: log WARNING, record seed as FAILED in JSON, continue (do not abort)
```

---

## Subtask: L-E5-4 — Two-condition seed orchestration

**Epic**: E5 — SimCLR Training Loop

### API Signature

```python
def run_all_seeds_and_conditions(config: ExperimentConfig) -> dict:
    """Run both conditions × 5 seeds. Returns nested results dict."""
```

### Pseudo-code

```python
def run_all_seeds_and_conditions(config):
    results = {"original": {}, "no_background": {}}

    for seed in config.seeds:              # [0, 1, 2, 3, 4]
        for condition in ["original", "no_background"]:
            trainer = SimCLRTrainer(config, condition=condition, seed=seed)
            ckpt_path = trainer.train()    # saves checkpoint

            probe_result = run_probes(ckpt_path, config.data_root, config.device)
            # probe_result: {spurious_probe_acc, task_probe_acc, ratio}

            collapse = check_collapse(probe_result["task_probe_acc"])
            probe_result["collapsed"] = collapse["collapsed"]

            result_path = config.result_path(condition, seed)
            json.dump(probe_result, open(result_path, "w"))
            results[condition][seed] = probe_result

    return results

# Checkpoint naming: checkpoints/h-m1/{condition}_seed{seed}_epoch50.pt
# Result naming:     results/h-m1/{condition}_seed{seed}.json
# run_experiment.py wraps single (seed, condition) pair for parallelization
```

---

## Subtask: L-E1-1 — build_mask_index()

*(See L-E3-4 above for full implementation — shared utility)*

**Additional note**: `build_mask_index` is called once in `WaterbirdsDataset.__init__` and stored as `self.mask_index`. The dict is passed to `SimCLRDataset` for the `no_background` condition only. For the `original` condition, mask_index is not required.

---

## Subtask: L-E1-2 — WaterbirdsDataset.__getitem__ multi-label return

**Epic**: E1 — Data Pipeline

### API Signature

```python
def __getitem__(self, idx: int) -> tuple[Image.Image, int, int, int]:
    """Returns: (pil_image, bird_label, background_label, group_id)"""
```

### Pseudo-code

```python
def __getitem__(self, idx):
    wilds_item = self.wilds_subset[idx]
    # WILDS returns: (x, y, metadata) where x is PIL Image
    image = wilds_item[0]                           # PIL Image
    bird_label = int(wilds_item[1])                 # 0=landbird, 1=waterbird
    metadata = wilds_item[2]                        # tensor with group info
    background_label = int(metadata[0])             # 0=land, 1=water
    group_id = bird_label * 2 + background_label    # 0,1,2,3

    return image, bird_label, background_label, group_id

# Note: WILDS WaterbirdsDataset already handles splits (train/val/test)
# group_id encoding: 0=landbird-land, 1=landbird-water, 2=waterbird-land, 3=waterbird-water
```

---

## Subtask: L-E4-1 — SimCLRModel.forward() tensor shape flow

**Epic**: E4 — SimCLR Model + NT-Xent Loss

### Tensor Shape Flow

```
Input:  x (B, 3, 224, 224)
  ↓ ResNet-50 backbone (fc=Identity)
  h: (B, 2048)          ← global average pool output
  ↓ ProjectionHead
  z_raw: (B, 128)
  ↓ F.normalize(z_raw, dim=1)
  z: (B, 128)           ← L2-normalized projection (used for NT-Xent)

Returns: (h, z)
  h: (B, 2048) — used for linear probe (backbone features)
  z: (B, 128)  — used for NT-Xent loss during training
```

### Pseudo-code

```python
def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
    h = self.backbone(x)               # (B, 2048); backbone.fc = Identity()
    z = self.projection_head(h)        # (B, 128) L2-normalized
    return h, z

# During training: use z for loss
# During eval: use h for linear probe (projection head discarded)
# backbone.fc = nn.Identity() set in __init__
```

---

## Subtask: L-E4-2 — ProjectionHead architecture

**Epic**: E4 — SimCLR Model + NT-Xent Loss

### Pseudo-code

```python
class ProjectionHead(nn.Module):
    def __init__(self, in_dim=2048, hidden_dim=2048, out_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, h: Tensor) -> Tensor:
        z = self.net(h)                    # (B, 128)
        return F.normalize(z, dim=1)       # (B, 128) L2-normalized

# No BatchNorm (SimCLR-v1 uses no BN in projection head)
# L2-norm is INSIDE ProjectionHead so NTXentLoss can assume input is normalized
```

---

## Subtask: L-E9-1 — run_experiment.py CLI + JSON output schema

**Epic**: E9 — Entrypoints + Orchestration

### API Signature

```python
def main(seed: int, condition: str) -> None:
    """Single seed/condition experiment run. Saves result JSON."""
```

### JSON Output Schema

```json
{
  "hypothesis_id": "h-m1",
  "condition": "original",
  "seed": 0,
  "epoch": 50,
  "spurious_probe_acc": 0.847,
  "task_probe_acc": 0.683,
  "ratio": 1.240,
  "collapsed": false,
  "mechanism_verified": true,
  "pixel_diff": 0.312,
  "timestamp": "2026-08-26T12:00:00Z"
}
```

### Pseudo-code

```python
# CLI: python run_experiment.py --seed 0 --condition original
import argparse

def main(seed: int, condition: str):
    assert condition in ("original", "no_background"), f"Invalid condition: {condition}"
    config = ExperimentConfig()
    os.makedirs(config.checkpoint_dir, exist_ok=True)
    os.makedirs(config.results_dir, exist_ok=True)

    trainer = SimCLRTrainer(config, condition=condition, seed=seed)
    ckpt_path = trainer.train()

    probe_result = run_probes(ckpt_path, config.data_root, config.device)
    probe_result.update({
        "hypothesis_id": "h-m1",
        "condition": condition,
        "seed": seed,
        "epoch": config.epochs,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })

    result_path = config.result_path(condition, seed)
    with open(result_path, "w") as f:
        json.dump(probe_result, f, indent=2)
    print(f"Saved: {result_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition", type=str, required=True)
    args = parser.parse_args()
    main(args.seed, args.condition)
```

---

## Subtask: L-E6-1 — extract_features() batched forward pass

**Epic**: E6 — Linear Probe Evaluation

### API Signature

```python
def extract_features(
    backbone: nn.Module,
    dataset: WaterbirdsDataset,
    device: str,
    batch_size: int = 256,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns: (features N×2048, bird_labels N, background_labels N)"""
```

### Pseudo-code

```python
def extract_features(backbone, dataset, device, batch_size=256):
    backbone.eval()
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False,
                        num_workers=4, pin_memory=True)
    all_features, all_bird, all_bg = [], [], []

    with torch.no_grad():
        for images, bird_labels, bg_labels, _ in loader:
            # images: (B, 3, 224, 224) — use standard eval transform (no augmentation)
            images = images.to(device)
            features = backbone(images)          # (B, 2048)
            all_features.append(features.cpu().numpy())
            all_bird.append(bird_labels.numpy())
            all_bg.append(bg_labels.numpy())

    return (
        np.concatenate(all_features, axis=0),   # (N, 2048)
        np.concatenate(all_bird, axis=0),        # (N,)
        np.concatenate(all_bg, axis=0),          # (N,)
    )

# Key: backbone here = SimCLRModel.get_backbone() (fc=Identity; outputs 2048-dim)
# Key: eval transform = Resize(256) → CenterCrop(224) → Normalize (NO augmentation)
# Key: run for train split (for probe fitting) and test split (for probe eval) separately
```

---

## Summary

| Subtask | Epic | Complexity | API |
|---------|------|-----------|-----|
| L-E3-1 | E3 | High | BackgroundReplacementTransform.__call__ |
| L-E3-2 | E3 | High | verify_mechanism_activated() |
| L-E3-3 | E3 | High | SimCLRDataset.__getitem__ (two-view) |
| L-E3-4 | E3 | High | build_mask_index() + load_cub_mask() |
| L-E5-1 | E5 | High | SimCLRTrainer.train() |
| L-E5-2 | E5 | High | NTXentLoss.forward() |
| L-E5-3 | E5 | Medium | check_collapse() |
| L-E5-4 | E5 | High | run_all_seeds_and_conditions() |
| L-E1-1 | E1 | Medium | build_mask_index() (detailed) |
| L-E1-2 | E1 | Medium | WaterbirdsDataset.__getitem__ |
| L-E4-1 | E4 | Medium | SimCLRModel.forward() shape flow |
| L-E4-2 | E4 | Medium | ProjectionHead pseudo-code |
| L-E9-1 | E9 | Medium | run_experiment.py CLI + JSON schema |
| L-E6-1 | E6 | Medium | extract_features() |

**Total subtasks: 14** (12 logic + 2 bonus; within budget allocation)
