# Configuration: h-e1 (EXISTENCE PoC)

**Type**: EXISTENCE — single fixed config, no ablation grid, 1 seed

Applied: weight-space-classification-pipeline (standard PyTorch defaults: AdamW + CosineAnnealingLR)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Config Schema (config.py)

Single dataclass, all hyperparameters fixed per architecture spec. No variations.

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Data
    data_dir: str = "data/mnist_inrs"
    data_url: str = "https://www.dropbox.com/s/mnist_inrs.zip"  # DWSNets source
    batch_size: int = 64
    num_workers: int = 2
    train_split: float = 0.8

    # Model dims
    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    dws_hidden: int = 128
    mlp_hidden: list = field(default_factory=lambda: [512, 256, 128])
    dropout: float = 0.1
    num_classes: int = 10

    # Training (FR-5)
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    cosine_t_max: int = 50
    seed: int = 42
    device: str = "cuda"

    # Output paths
    results_path: str = "results/results.json"
    fig_dir: str = "results/figures"
    checkpoint_dir: str = "results/checkpoints"
```

No YAML file — hardcode `Config()` defaults in `main.py` (`cfg = Config()`). Skipped: YAML loader/CLI overrides — EXISTENCE PoC needs one fixed run, add if hyperparameter sweeps become necessary later.

---

## A-1: Data Pipeline [Complexity: 10, Budget: 3]

**Applied**: Standard PyTorch Dataset/DataLoader defaults

### Data Loading Parameters
```python
# get_dataloaders(cfg: Config) -> (train_loader, test_loader)
DataLoader(
    dataset,
    batch_size=cfg.batch_size,   # 64
    shuffle=True,                 # train only
    num_workers=cfg.num_workers,  # 2
    pin_memory=True,
)
```
- Normalization: per-layer zero-mean/unit-variance over weight tensors (`normalize_weights`)
- Split: 80/20 train/test (`cfg.train_split`), fixed by `cfg.seed`
- Download trigger: if `cfg.data_dir` missing, call `download_mnist_inrs(cfg.data_dir)` from `cfg.data_url`

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Download + extract | Fetch zip from Dropbox, unzip to `data_dir` if missing |
| C-1-2 | Dataset + normalize | `MNISTINRDataset` loading `.pt` files, `normalize_weights` |
| C-1-3 | DataLoaders + split | 80/20 split, build train/test `DataLoader` per params above |

---

## A-6: Training Loop [Complexity: 8, Budget: 3]

**Applied**: AdamW + CosineAnnealingLR (standard schedule per FR-5)

### Training Config (uses Config fields above)
```python
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=cfg.lr,                    # 1e-3
    weight_decay=cfg.weight_decay # 1e-4
)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer, T_max=cfg.cosine_t_max  # 50
)
criterion = torch.nn.CrossEntropyLoss()

torch.manual_seed(cfg.seed)  # 42, set once before training all 3 models
```
- Loop: 50 epochs, step scheduler once per epoch (after optimizer.step())
- Eval: `torchmetrics.Accuracy` on test set after training

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Setup | Build optimizer/scheduler/criterion, seed everything |
| C-6-2 | train_model loop | Epoch loop: forward, loss, backward, step, scheduler.step() |
| C-6-3 | evaluate + run_experiment | Test accuracy dict; orchestrate train/eval across MLP/DWS/NFT |

---

## A-8: Visualization Suite [Complexity: 9, Budget: 3]

**Applied**: matplotlib + scikit-learn t-SNE (per FR-7 dependencies)

### Output Paths (from Config.fig_dir = "results/figures")
```python
ACCURACY_FIG   = f"{cfg.fig_dir}/accuracy_comparison.png"
ATTENTION_FIG  = f"{cfg.fig_dir}/attention_heatmap.png"
ACTIVATION_FIG = f"{cfg.fig_dir}/layer_activation_profile.png"
TSNE_FIG       = f"{cfg.fig_dir}/tsne_representations.png"
```
- All figures: `dpi=150`, saved via `plt.savefig(out_path, bbox_inches="tight")`
- t-SNE: `sklearn.manifold.TSNE(n_components=2, random_state=cfg.seed)`

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Accuracy + attention plots | `plot_accuracy_comparison`, `plot_attention_heatmap` |
| C-8-2 | Activation profile plot | `plot_layer_activation_profile` for DWS |
| C-8-3 | t-SNE plot | `plot_tsne_representations` (DWS vs NFT reprs, sklearn TSNE) |
