# Logic Specification: H-M1 BFS-Gap Correlation Analysis

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (docs/youra_research/h-e1/code/)
**Analyzed Path**: docs/youra_research/h-e1/code/{model.py, data.py, train.py, config.py}
**Relevant Symbols**: `FeatureResNet50.extract_features`, `FeatureResNet50.forward`, `build_dataloader`, `DATASET_NUM_CLASSES`, `Config`, `train_linear_probe`

**Deviations from PRD/spec found in actual H-E1 code (use these, not the spec):**
- H-E1 uses **5 benchmarks** (`cub, dogs, flowers, cars, aircraft`) x **3 seeds** = **15 models**, not "6 models / 2 benchmarks" as stated in PRD/experiment brief. H-M1 must iterate over all 15 checkpoints found in `h-e1/code/models/finetuned/*.pt`.
- No `fingerprint_classifier.pkl` is saved by H-E1 — `LogisticRegression` is trained in-memory inside `train_linear_probe` and discarded. H-M1 must **retrain the same classifier** on H-E1 features (`h-e1/code/features/{features,labels,model_ids}.npy`) itself, using identical `Config.probe_C` / `probe_max_iter`.
- Checkpoint dict keys: `state_dict`, `benchmark`, `seed`, `acc` (this `acc` is the **in-domain val accuracy**, already computed by H-E1 finetuning loop — reuse directly, do not retrain/re-evaluate in-domain).
- `probe_dataset` = `"nabirds"` is already the cross-dataset probe set used for fingerprinting features. NABirds accuracy per model must be computed separately (H-E1 does not train per-model classification heads for NABirds).
- `FeatureResNet50(num_classes, pretrained=False)` — reconstruct with `DATASET_NUM_CLASSES[benchmark]` then `load_state_dict(ckpt["state_dict"])`.

Applied: scipy.stats.pearsonr for correlation with p-value (standard, no custom implementation).

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
class FeatureResNet50(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True): ...
    def forward(self, x: Tensor) -> Tensor: ...              # [B,3,224,224] -> [B, num_classes]
    def extract_features(self, x: Tensor) -> Tensor: ...     # [B,3,224,224] -> [B, 2048]

# From: docs/youra_research/h-e1/code/data.py
DATASET_NUM_CLASSES: Dict[str, int]  # {"cub":200,"dogs":120,"flowers":102,"cars":196,"aircraft":100,"nabirds":555}
def build_dataloader(name: str, root: str, train: bool, batch_size: int, num_workers: int = 4) -> DataLoader: ...

# From: docs/youra_research/h-e1/code/config.py
@dataclass
class Config:
    benchmarks: list = ["cub","dogs","flowers","cars","aircraft"]
    probe_dataset: str = "nabirds"
    seeds: list = [0,1,2]
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    ckpt_dir: str = "./models/finetuned"
    feature_dir: str = "./features"

# Checkpoint format (from train.py::finetune_one):
# torch.save({"state_dict":..., "benchmark": str, "seed": int, "acc": float, "epoch": int}, path)
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation).

---

## A-1: BFS Computation [Complexity: 3, Budget: 3]

**Applied**: sklearn LogisticRegression.predict_proba for confidence extraction

### API Signatures

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

def load_h_e1_probe_classifier(
    feature_dir: str,   # e.g. "h-e1/code/features"
    probe_C: float = 1.0,
    probe_max_iter: int = 1000,
) -> LogisticRegression:
    """Retrain H-E1's fingerprint classifier (not persisted by H-E1) on saved features."""
    ...

def compute_bfs(
    classifier: LogisticRegression,
    features: np.ndarray,       # [N, 2048] NABirds features for one model
    true_benchmark_idx: int,    # index into cfg.benchmarks
) -> float:
    """BFS = mean predict_proba confidence for true benchmark class."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N, 2048] | NABirds probe features for one model (N = NABirds test size) |
| probs | [N, num_benchmarks] | num_benchmarks = 5 |
| bfs | scalar | probs[:, true_benchmark_idx].mean() |

### Pseudo-code

```
1. all_feats, all_labels, all_model_ids = np.load(feature_dir/{features,labels,model_ids}.npy)
2. classifier = LogisticRegression(C=probe_C, max_iter=probe_max_iter, n_jobs=-1)
   classifier.fit(all_feats, all_labels)   # fit on ALL 15 models' NABirds features (same as H-E1 train_linear_probe, full data — no train/val/test split needed for BFS extraction)
3. for model_idx in range(15):
       mask = (all_model_ids == model_idx)
       feats_i = all_feats[mask]                      # [N_i, 2048]
       true_idx = benchmark_to_idx[ckpt["benchmark"]]
       bfs_i = compute_bfs(classifier, feats_i, true_idx)
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | load_h_e1_probe_classifier | Load npy features, fit LogisticRegression |
| L-1-2 | compute_bfs | predict_proba, mean confidence for true class |

---

## A-2: Gap Computation [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch eval loop, linear-probe head for NABirds

### API Signatures

```python
import torch
from torch.utils.data import DataLoader

def get_in_domain_acc(ckpt: dict) -> float:
    """In-domain val accuracy, reuse H-E1 checkpoint's stored 'acc' field directly."""
    return ckpt["acc"]

def train_nabirds_head(
    model: "FeatureResNet50",
    nabirds_train_loader: DataLoader,
    device: torch.device,
    epochs: int = 5,
    lr: float = 0.01,
) -> torch.nn.Linear:
    """Freeze backbone, train new linear head [2048 -> 555] on NABirds train split."""
    ...

def evaluate_nabirds(
    model: "FeatureResNet50",
    head: torch.nn.Linear,
    nabirds_test_loader: DataLoader,
    device: torch.device,
) -> float:
    """Accuracy on NABirds test set using frozen backbone + trained head."""
    ...

def compute_gap(in_domain_acc: float, nabirds_acc: float) -> float:
    """Gap = in_domain_acc - nabirds_acc."""
    return in_domain_acc - nabirds_acc
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| feats (frozen) | [B, 2048] | via `model.extract_features(x)`, `torch.no_grad()` |
| head.weight | [555, 2048] | new linear head for NABirds classes |
| logits | [B, 555] | head(feats) |

### Pseudo-code

```
1. model = FeatureResNet50(DATASET_NUM_CLASSES[benchmark], pretrained=False)
   model.load_state_dict(ckpt["state_dict"]); model.eval()  # freeze backbone
2. nabirds_train = build_dataloader("nabirds", data_root, train=True, batch_size=32)
   nabirds_test  = build_dataloader("nabirds", data_root, train=False, batch_size=32)
3. head = nn.Linear(2048, 555).to(device)
   opt = SGD(head.parameters(), lr=0.01, momentum=0.9)
   for epoch in range(5):
       for x, y in nabirds_train:
           with torch.no_grad(): feats = model.extract_features(x.to(device))  # [B,2048]
           logits = head(feats)                                                # [B,555]
           loss = CE(logits, y.to(device)); loss.backward(); opt.step(); opt.zero_grad()
4. nabirds_acc = evaluate_nabirds(model, head, nabirds_test, device)
5. gap = ckpt["acc"] - nabirds_acc
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | get_in_domain_acc | Read `ckpt["acc"]` (already computed by H-E1) |
| L-2-2 | train_nabirds_head | Freeze backbone, train linear head on NABirds train |
| L-2-3 | evaluate_nabirds | Eval accuracy on NABirds test |
| L-2-4 | compute_gap | in_domain_acc - nabirds_acc |

---

## A-3: Correlation Analysis [Complexity: 2, Budget: 2]

**Applied**: scipy.stats.pearsonr

### API Signatures

```python
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def run_correlation(bfs_array: np.ndarray, gap_array: np.ndarray) -> tuple[float, float]:
    """Pearson r and two-sided p-value. bfs_array, gap_array: [15]"""
    return pearsonr(bfs_array, gap_array)

def plot_bfs_gap_scatter(
    bfs_array: np.ndarray, gap_array: np.ndarray,
    r: float, p: float, save_path: str,
) -> None:
    """Scatter + linear regression line + r/p annotation."""
    ...
```

### Pseudo-code

```
1. r, p = pearsonr(bfs_array, gap_array)
2. slope, intercept = np.polyfit(bfs_array, gap_array, 1)
3. plt.scatter(bfs_array, gap_array)
   plt.plot(bfs_array, slope*bfs_array + intercept)
   plt.annotate(f"r={r:.3f}, p={p:.4f}")
   plt.savefig(save_path)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | run_correlation | pearsonr(bfs, gap) |
| L-3-2 | plot_bfs_gap_scatter | Scatter + regression + annotation, save to figures/ |

---

## Main Experiment Loop (Pseudo-code)

```python
def main(h_e1_dir: str, data_root: str, output_dir: str):
    cfg = Config()  # reuse H-E1 config (benchmarks, seeds, probe_C, etc.)
    benchmark_to_idx = {b: i for i, b in enumerate(cfg.benchmarks)}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Load H-E1 artifacts
    feats, labels, model_ids = load_npy(f"{h_e1_dir}/features/{{features,labels,model_ids}}.npy")
    classifier = load_h_e1_probe_classifier(f"{h_e1_dir}/features", cfg.probe_C, cfg.probe_max_iter)
    ckpt_paths = sorted(glob(f"{h_e1_dir}/models/finetuned/*.pt"))  # 15 checkpoints

    bfs_scores, gaps, model_meta = [], [], []

    for model_idx, ckpt_path in enumerate(ckpt_paths):
        ckpt = torch.load(ckpt_path, map_location=device)
        benchmark = ckpt["benchmark"]
        true_idx = benchmark_to_idx[benchmark]

        # BFS
        mask = (model_ids == model_idx)
        bfs = compute_bfs(classifier, feats[mask], true_idx)          # scalar

        # Gap
        model = FeatureResNet50(DATASET_NUM_CLASSES[benchmark], pretrained=False)
        model.load_state_dict(ckpt["state_dict"]); model.to(device).eval()
        nabirds_train = build_dataloader("nabirds", data_root, train=True, batch_size=32)
        nabirds_test = build_dataloader("nabirds", data_root, train=False, batch_size=32)
        head = train_nabirds_head(model, nabirds_train, device)
        nabirds_acc = evaluate_nabirds(model, head, nabirds_test, device)
        gap = compute_gap(ckpt["acc"], nabirds_acc)

        bfs_scores.append(bfs); gaps.append(gap)
        model_meta.append({"benchmark": benchmark, "seed": ckpt["seed"], "bfs": bfs, "gap": gap})
        print(f"[{benchmark} seed={ckpt['seed']}] BFS={bfs:.4f} gap={gap:.4f}")

    bfs_array, gap_array = np.array(bfs_scores), np.array(gaps)

    # Mechanism sanity checks (see 03_prd.md verify_mechanism)
    assert len(bfs_array) >= 6
    assert np.std(bfs_array) > 0.01 and np.std(gap_array) > 0.01

    r, p = run_correlation(bfs_array, gap_array)
    plot_bfs_gap_scatter(bfs_array, gap_array, r, p, f"{output_dir}/figures/bfs_gap_scatter.png")

    results = {"per_model": model_meta, "pearson_r": r, "p_value": p,
               "n_models": len(bfs_array), "gate_pass": bool(r > 0.3 and p < 0.05)}
    json.dump(results, open(f"{output_dir}/experiment_results.json", "w"), indent=2)
    return results
```

### Self-Check (assertion-based)

```python
def demo():
    """Sanity check on synthetic data — validates pipeline shapes/logic, not real training."""
    rng = np.random.RandomState(0)
    fake_bfs = rng.uniform(0.5, 1.0, size=15)
    fake_gap = fake_bfs * 0.3 + rng.normal(0, 0.02, size=15)  # engineered positive corr
    r, p = run_correlation(fake_bfs, fake_gap)
    assert r > 0.3 and p < 0.05, f"Sanity check failed: r={r}, p={p}"
    print("demo() OK: run_correlation pipeline sane")

if __name__ == "__main__":
    demo()
```
