# Configuration: H-E1 — EquiSSL Distribution Shift PoC

**Applied**: Hardcoded config with argparse overrides (LIGHT tier)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Config Files Found**: None — new config
**Pattern Used**: hardcoded module-level constants

---

## 1. config.py — Full Hardcoded Config Module

```python
# h-e1/code/config.py
# All values hardcoded. Override via argparse in run_experiment.py / train_equissl.py.

import os

# --- Model ---
HIDDEN_DIM   = 256
LATENT_DIM   = 128
NUM_LAYERS   = 4

# --- Training ---
LR           = 1e-3
WEIGHT_DECAY = 1e-4
BETAS        = (0.9, 0.999)
BATCH_SIZE   = 64
EPOCHS       = 100

# --- Scheduler ---
T_MAX        = 100      # matches EPOCHS (full cosine cycle)
ETA_MIN      = 1e-5

# --- SSL Objective ---
TEMPERATURE  = 0.07     # NT-Xent standard; higher → collapse risk, lower → instability
LAMBDA_SWEEP = [0.01, 0.1, 1.0, 10.0]
SEEDS        = [0, 1, 2, 3, 4]

# --- Data ---
VAL_FRACTION = 0.1      # 10% of MultiZoo for reconstruction validation

# --- Evaluation ---
N_MMD_KERNELS  = 5
MMD_RATIO_PASS = 2.0    # gate: PASS if ratio >= this
MMD_RATIO_STOP = 1.5    # gate: STOP if ratio < this; WARN if 1.5 <= ratio < 2.0

# --- Paths (override via argparse --data_root / --checkpoint_dir) ---
DATA_ROOT      = os.environ.get('DATA_ROOT', './data')
CHECKPOINT_DIR = os.environ.get('CHECKPOINT_DIR', 'checkpoints/h-e1/')
RESULTS_DIR    = 'docs/youra_research/h-e1/'
FIGURES_DIR    = 'docs/youra_research/h-e1/figures/'
```

---

## 2. Argparse Schema for run_experiment.py

```python
# Paste into run_experiment.py (and train_equissl.py where applicable)

import argparse
import torch

def get_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='H-E1 EquiSSL Distribution Shift PoC')
    p.add_argument('--data_root',       type=str, required=True,
                   help='Root directory containing multizoo/ and vit/ subdirs')
    p.add_argument('--checkpoint_dir',  type=str, default='checkpoints/h-e1/',
                   help='Where to save model checkpoints')
    p.add_argument('--device',          type=str,
                   default='cuda' if torch.cuda.is_available() else 'cpu')
    p.add_argument('--lam',             type=float, default=None,
                   help='Single lambda override (skips full sweep; for quick tests)')
    p.add_argument('--seed',            type=int, default=None,
                   help='Single seed override (skips 5-seed loop; for quick tests)')
    p.add_argument('--smoke_test',      action='store_true',
                   help='Run 2 epochs on 10 MLP + 10 ViT models; < 5 min on any GPU')
    return p
```

**Override logic** (in `main`):

```python
args = get_parser().parse_args()

# Apply smoke_test overrides
if args.smoke_test:
    import config
    config.EPOCHS     = 2
    config.SEEDS      = [0]           # 1 seed only in smoke test
    N_MLP_SMOKE       = 10
    N_VIT_SMOKE       = 10

# Apply single-run overrides
lambda_list = [args.lam]  if args.lam  is not None else config.LAMBDA_SWEEP
seed_list   = [args.seed] if args.seed is not None else config.SEEDS
```

---

## 3. results.json Schema

```json
{
  "hypothesis_id": "h-e1",
  "lambda_selected": 0.1,
  "seeds": {
    "0": {"mmd_sane": 0.0, "mmd_equi": 0.0, "ratio": 0.0},
    "1": {"mmd_sane": 0.0, "mmd_equi": 0.0, "ratio": 0.0},
    "2": {"mmd_sane": 0.0, "mmd_equi": 0.0, "ratio": 0.0},
    "3": {"mmd_sane": 0.0, "mmd_equi": 0.0, "ratio": 0.0},
    "4": {"mmd_sane": 0.0, "mmd_equi": 0.0, "ratio": 0.0}
  },
  "summary": {
    "mmd_sane_mean": 0.0,
    "mmd_sane_std":  0.0,
    "mmd_equi_mean": 0.0,
    "mmd_equi_std":  0.0,
    "ratio_mean":    0.0,
    "ratio_std":     0.0,
    "gate_result":   "PASS|WARN|STOP"
  }
}
```

Save with:
```python
import json, os
os.makedirs(config.RESULTS_DIR, exist_ok=True)
with open(os.path.join(config.RESULTS_DIR, 'results.json'), 'w') as f:
    json.dump(results, f, indent=2)
```

---

## 4. Smoke Test Protocol

Activated via `--smoke_test` flag. Verified by the override logic in section 2.

**What it does:**
- Loads only the first 10 MLP models from MultiZooGraphDataset (slice dataset)
- Loads only the first 10 ViT models from ViTZooGraphDataset
- Runs 2 training epochs (EquiSSL only; skips SANE full training)
- Computes MMD on the tiny subset — value is meaningless, but confirms shapes are correct
- Checks: no tensor shape error, ratio is a finite float, results.json written

**Dataset slicing** (in `run_experiment.py`):
```python
if args.smoke_test:
    from torch.utils.data import Subset
    train_dataset = Subset(train_dataset, range(min(10, len(train_dataset))))
    vit_dataset   = Subset(vit_dataset,   range(min(10, len(vit_dataset))))
```

**Expected runtime:** < 5 minutes on any GPU (2 epochs x 10 graphs x 1 seed).

**Pass condition for smoke test:** exits with code 0, `results.json` written, no exceptions.

---

## 5. Hyperparameter Justifications

Only non-obvious values noted.

| Parameter | Value | Source / Rationale |
|-----------|-------|--------------------|
| `TEMPERATURE` | 0.07 | SimCLR (Chen et al. 2020) standard; values > 0.1 risk representation collapse |
| `LAMBDA_SWEEP` | [0.01, 0.1, 1.0, 10.0] | Log-uniform span; covers negligible to dominant reconstruction signal |
| `N_MMD_KERNELS` | 5 | yiftachbeer/mmd_loss_pytorch default; sufficient for median-heuristic RBF |
| `MMD_RATIO_PASS` | 2.0 | Pre-registered gate from PRD §8; not tuned post-hoc |
| `MMD_RATIO_STOP` | 1.5 | Below this, EquiSSL offers negligible benefit over SANE |
| `VAL_FRACTION` | 0.1 | Standard 90/10 split; used only for λ selection (not test) |
| `ETA_MIN` | 1e-5 | 100x below LR; prevents cosine schedule from zeroing gradients completely |
| All others | Standard | Adam defaults from PyTorch; batch 64 fits ~24 GB VRAM for graph batches |
