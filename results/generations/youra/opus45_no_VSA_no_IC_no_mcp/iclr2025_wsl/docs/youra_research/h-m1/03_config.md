# Configuration: h-m1 (MECHANISM)

**Type**: MECHANISM — extends h-e1 `Config` with tracking/multi-seed fields, dataclass format

Applied: training-dynamics-tracking-pattern (per-epoch hooks around existing train loop)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (`h-e1/code/config.py` read directly — Serena unavailable, file read manually per fallback)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (single `@dataclass Config`)
**Pattern Used**: dataclass (inheritance)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    data_dir: str = "data/mnist_inrs"
    data_url: str = "https://www.dropbox.com/scl/fi/4xmx2e3yzz7u8a0xw6n0n/..."
    batch_size: int = 64
    num_workers: int = 2
    train_split: float = 0.8

    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    dws_hidden: int = 128
    mlp_hidden: list = field(default_factory=lambda: [512, 256, 128])
    dropout: float = 0.1
    num_classes: int = 10

    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    cosine_t_max: int = 50
    seed: int = 42
    device: str = "cuda"

    results_path: str = "results/results.json"
    fig_dir: str = "results/figures"
    checkpoint_dir: str = "results/checkpoints"
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

### Extended Config (h-m1)

PRD specifies `lr=1e-4, epochs=100` (NFR-1) overriding h-e1 defaults; `seed` becomes `seeds` list for 3-seed comparison.

```python
from dataclasses import dataclass, field
from h_e1.config import Config as BaseConfig  # copy into h-m1/code/config.py, edit in place

@dataclass
class Config(BaseConfig):
    lr: float = 1e-4                # NFR-1 override (base: 1e-3)
    epochs: int = 100               # NFR-1 override (base: 50)
    seeds: list = field(default_factory=lambda: [42, 123, 7])  # replaces single `seed`

    # Tracking (FR-3)
    track_every: int = 1            # grad-norm capture interval (epochs)
    snapshot_every: int = 10        # weight snapshot interval (epochs), FR-3.2

    # Success criteria thresholds (FR-4, Success Criteria)
    wasserstein_threshold: float = 0.1   # criterion 1: grad dist DWS vs NFT
    early_signature_epoch: int = 20      # criterion 4: signature detectable by epoch
```

No YAML/CLI — hardcode `Config()` in `main.py`. Note: `seed` (base) unused directly; iterate `cfg.seeds` in `run_seeds.py`, calling `torch.manual_seed(s)` per run.

---

## M-2: TrainingDynamicsTracker [Complexity: 12, Budget: 2]

**Applied**: training-dynamics-tracking-pattern (hook-based per-epoch capture, no new hyperparameters beyond `track_every`)

### Configuration
Uses `cfg.track_every`, `cfg.snapshot_every` from extended Config above. No separate dataclass — tracker is stateful, not config-driven beyond these two intervals.

```python
tracker = TrainingDynamicsTracker(model, model_type)  # model_type: "mlp"|"dws"|"nft"
# per epoch in train_tracked.py:
if epoch % cfg.track_every == 0:
    tracker.track_gradients(epoch)
if epoch % cfg.snapshot_every == 0:
    prev = tracker.snapshot_weights()
if model_type == "nft":
    tracker.track_attention(sample_input)
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Gradient + weight-delta tracking | `track_gradients`, `track_weight_updates`, `snapshot_weights` using `cfg.track_every`/`snapshot_every` |
| C-2-2 | Attention tracking + serialization | `track_attention` (NFT only), `to_dict()` output format |

---

## M-4: Distributional Metrics [Complexity: 8]

**Applied**: distributional-comparison-pattern (Wasserstein + CoV over layer time series)

```python
# Uses cfg.wasserstein_threshold, cfg.early_signature_epoch — no new config fields
def check_success_criteria(dws_stats: dict, nft_stats: dict, cfg: Config) -> dict[str, bool]:
    return {
        "grad_flow_differs": wasserstein_grad_distance(...) > cfg.wasserstein_threshold,
        "dws_more_localized": weight_update_cov(dws_stats) > weight_update_cov(nft_stats),
        "nft_entropy_increases": nft_stats["attention_entropy"][-1] > nft_stats["attention_entropy"][0],
        "early_signature": locality_score(dws_stats, epoch=cfg.early_signature_epoch) differs from nft equivalent,
    }
```

No subtasks allocated (budget exhausted on M-2) — implemented directly in Phase 4 as single-pass functions per architecture.md signatures.

---

## M-5 / M-6 / M-7 / M-8: Remaining Tasks

No config-level parameters beyond `Config` fields above and existing h-e1 patterns (AdamW, CosineAnnealingLR, `torchmetrics.Accuracy`, matplotlib `dpi=150`) — reused as-is from `03_config.md` (h-e1). No new hyperparameters introduced; multi-seed loop iterates `cfg.seeds`, visualization reuses `cfg.fig_dir`.
