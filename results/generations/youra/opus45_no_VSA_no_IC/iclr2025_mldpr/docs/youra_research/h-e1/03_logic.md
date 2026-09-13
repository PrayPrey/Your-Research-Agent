# Logic: H-E1 Benchmark Fingerprint Detection

**Type:** EXISTENCE (PoC)

Applied: standard feature-extraction + linear-probe pattern (frozen/finetuned backbone -> sklearn probe)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data pipeline [Complexity: 10, Budget: 1]

**Applied**: torchvision ImageFolder/Dataset pattern

```python
def get_transforms(train: bool) -> transforms.Compose:
    """Resize->224, augment if train, normalize (ImageNet stats)."""
    ...

def build_dataset(name: str, root: str, train: bool) -> Dataset:
    # name in {cub, dogs, flowers, cars, aircraft, nabirds}
    ...

def build_dataloader(name: str, root: str, train: bool, batch_size: int) -> DataLoader:
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Data pipeline | transforms + per-dataset Dataset/DataLoader builders for 6 benchmarks |

---

## A-2/A-3: Model + Finetuning [Complexity: 6+12, Budget: 1]

**Applied**: torchvision ResNet-50 with forward-hook feature extraction

```python
class FeatureResNet50(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True):
        """ResNet-50 backbone + linear classifier head."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        # x: [B, 3, 224, 224] -> logits: [B, num_classes]
        ...

    def extract_features(self, x: Tensor) -> Tensor:
        # x: [B, 3, 224, 224] -> feats: [B, 2048] (avgpool output)
        ...


def finetune_one(benchmark: str, seed: int, cfg: Config) -> str:
    """SGD+cosine, cfg.epochs. Returns ckpt path."""
    ...

def run_all_finetuning(cfg: Config) -> list[str]:
    # loops 5 benchmarks x 3 seeds -> 15 ckpt paths
    ...
```

### Pseudo-code (finetune_one)

```
1. model = FeatureResNet50(num_classes=class_count[benchmark], pretrained=True)
2. opt = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
3. sched = CosineAnnealingLR(opt, T_max=cfg.epochs)
4. for epoch in range(cfg.epochs): train one pass, sched.step()
5. save {model.state_dict(), benchmark, seed} -> ckpt_dir/{benchmark}_seed{seed}.pt
6. return ckpt_path
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Model + finetune loop | FeatureResNet50 class, finetune_one, run_all_finetuning |

---

## A-4: Feature extraction [Complexity: 9, Budget: 1]

**Applied**: batched inference + preallocated feature array

```python
def extract_all_features(ckpt_paths: list[str], cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    # returns features [15*N_nabirds_test, 2048], labels [same len] (benchmark idx 0-4)
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [15*24000, 2048] | stacked across all 15 models |
| labels | [15*24000] | int in [0,4], benchmark index per model |

### Pseudo-code

```
1. for ckpt in ckpt_paths:
     model = load(ckpt); model.eval()
     loader = build_dataloader("nabirds", cfg.data_root, train=False, cfg.batch_size)
     for batch x, _ in loader:
         feats = model.extract_features(x)  # [B, 2048]
         append feats, label=benchmark_idx(ckpt) to output arrays
2. concatenate -> (features, labels)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Feature extraction | Batched extract_all_features over 15 ckpts x NABirds test |

---

## A-5/A-6/A-7: Probe, baselines, results [Complexity: 11+7+5, Budget: 1]

**Applied**: sklearn LogisticRegression + bootstrap/t-test stats pattern

```python
def train_linear_probe(features: np.ndarray, labels: np.ndarray, cfg: Config) -> dict:
    # LogisticRegression(C=1.0), split 70/15/15 by model, 3-fold CV
    # returns {"accuracy", "ci_95": (lo, hi), "p_value", "cohens_d", "confusion_matrix"}
    ...

def run_baselines(cfg: Config) -> dict:
    # {"random_init": {...}, "shuffled_labels": {...}, "same_domain": {...}}
    ...

def main(cfg: Config) -> None:
    """Orchestrates full pipeline, writes cfg.results_path."""
    ...
```

### Pseudo-code (train_linear_probe)

```
1. split features/labels by model id -> train/val/test (70/15/15)
2. clf = LogisticRegression(C=1.0, max_iter=1000)
3. cv_scores = cross_val_score(clf, train, groups=model_id, cv=3)
4. clf.fit(train); acc = clf.score(test)
5. boot_accs = [clf refit on bootstrap resample -> score(test) for _ in range(1000)]
6. ci_95 = percentile(boot_accs, [2.5, 97.5])
7. t_stat, p = ttest_1samp(boot_accs, popmean=0.20)
8. cohens_d = (mean(boot_accs) - 0.20) / std(boot_accs)
9. cm = confusion_matrix(y_test, clf.predict(test))
10. return dict(...)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Probe + baselines + results | train_linear_probe, run_baselines, main orchestration + JSON/figure output |
