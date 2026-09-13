# Architecture Design: H-M3
# SymCanon-WSL — NFT with Weight Symmetry Canonicalization

**Hypothesis:** H-M3
**Type:** MECHANISM (Incremental — extends H-M2)
**Generated:** 2026-08-27
**Source:** 03_prd.md + 02c_experiment_brief.md + h-m2/code (actual code analysis)

---

## Codebase Analysis (Serena)

**[NO-MCP MODE — Serena unavailable. Codebase analysis performed via direct file read.]**

Actual code inspected: `h-m2/code/data_prep.py`, `h-m2/code/main.py`

Key findings from actual h-m2 code:
- `apply_condition_d(X: np.ndarray) -> np.ndarray` in `h-m2/code/data_prep.py` — validated, reusable
- `load_zoo()` from `h-m1/code/data_loader.py` — weights dim 51,850 (SPLITS=[50176,64,640,10])
- `train_test_split_fixed(X, Y, test_size, seed)` — deterministic split utility
- H-M2 used only 50 test models; H-M3 must use full ~5,000-model test split
- No NFT trainer in h-m2 (PCA only); H-M3 must re-introduce NFT from h-m1/h-e1

Applied: extend-existing-codebase pattern (h-m2 data prep reused, new NFT training added)
Applied: condition-flag ablation pattern (single CLI flag selects preprocessing variant)

---

## Module Structure

```
h-m3/code/
├── main.py              # Experiment orchestrator: train + eval all conditions
├── data_prep.py         # Condition preprocessing (A–F); extends h-m2/code/data_prep.py
├── model.py             # CanonicalWeightEncoder + NFT wrapper
├── train.py             # Training loop, optimizer, LR schedule, early stopping
├── evaluate.py          # Spearman ρ, bootstrap CI, gate checks P1/P2
├── figures.py           # All 5 required figures (FR-8.1–FR-8.5)
└── config.py            # ExperimentConfig dataclass

h-m3/
├── figures/             # Output figures (FR-8)
└── results.json         # Per-condition × per-seed results
```

---

## File Organization

| File | Responsibility | Key Imports |
|------|---------------|-------------|
| `main.py` | CLI, orchestrate train+eval per condition × seed, aggregate, gate check | all local modules |
| `data_prep.py` | `apply_condition_{a-f}()`, `verify_canonicalization_activated()` | numpy, sys.path → h-m2 |
| `model.py` | `CanonicalWeightEncoder`, NFT architecture wrapper | torch |
| `train.py` | `train_condition(encoder, loader_train, loader_val, config)` | torch, tqdm |
| `evaluate.py` | `bootstrap_spearman()`, `check_p1()`, `check_p2()` | scipy, numpy |
| `figures.py` | `generate_all_figures(results)` | matplotlib |
| `config.py` | `ExperimentConfig` dataclass, `DEFAULT_CONFIG` | dataclasses |

---

## Epic Tasks

### Epic E1: Data Pipeline (data-pipeline)

**Description:** Extend h-m2 data_prep.py with Conditions B, C, E (Condition D already exists); add `verify_canonicalization_activated()`; switch to full zoo splits (train/val/test ~40k/5k/5k) instead of h-m2's 450/50 split.

**Files:** `h-m3/code/data_prep.py`

**Complexity Score: 10 (Medium)**
- Module Size: 3 (moderate — ~120 lines)
- Dependencies: 2 (h-m1 data_loader, h-m2 data_prep)
- Algorithm: 3 (5 preprocessing variants + verification logic)
- Integration: 2 (used by model.py and evaluate.py)

---

### Epic E2: NFT Model + CanonicalWeightEncoder (model)

**Description:** Implement `CanonicalWeightEncoder(nft, condition)` wrapper that applies preprocessing then NFT encoding. Reuse NFT architecture from h-e1/h-m1 (or re-implement minimal NFT if checkpoint not available). Support frozen-encoder mode via `freeze_encoder()` method.

**Files:** `h-m3/code/model.py`

**Complexity Score: 16 (High)**
- Module Size: 4 (significant — NFT + wrapper, ~200 lines)
- Dependencies: 4 (torch, h-e1 NFT checkpoint/impl, data_prep, config)
- Algorithm: 4 (NFT attention mechanism + condition routing + frozen-encoder logic)
- Integration: 4 (central to all conditions; feeds train.py and evaluate.py)

---

### Epic E3: Training Loop (training)

**Description:** Implement `train_condition(encoder, loader_train, loader_val, config)` with Adam optimizer, ReduceLROnPlateau schedule, early stopping on val Spearman ρ. Train independently per condition × seed. Save best checkpoint.

**Files:** `h-m3/code/train.py`

**Complexity Score: 13 (Medium)**
- Module Size: 3 (moderate — ~150 lines)
- Dependencies: 3 (torch, scipy for val ρ, tqdm)
- Algorithm: 4 (early stopping on ρ, LR scheduling, checkpoint saving)
- Integration: 3 (called by main.py per condition × seed)

---

### Epic E4: Evaluation & Gate Checks (evaluation)

**Description:** Implement `bootstrap_spearman(y_pred, y_true, n_boot=1000)` returning (ρ, ci_lo, ci_hi). Implement `check_p1(rho_D, rho_A, ci_D, ci_A)` and `check_p2(rho_table)`. Aggregate 3-seed results and run gate checks.

**Files:** `h-m3/code/evaluate.py`

**Complexity Score: 12 (Medium)**
- Module Size: 3 (moderate — ~100 lines)
- Dependencies: 2 (scipy, numpy)
- Algorithm: 4 (bootstrap CI + P1/P2 gate logic)
- Integration: 3 (called by main.py; results go to figures.py)

---

### Epic E5: Frozen-Encoder Sub-Experiment (training)

**Description:** Train Condition A NFT to convergence. Freeze encoder. Retrain only final MLP regressor on Conditions B, C, D inputs. Evaluate frozen-encoder ρ vs full-training ρ.

**Files:** `h-m3/code/train.py` (extended with `train_frozen_regressor()`)

**Complexity Score: 11 (Medium)**
- Module Size: 2 (small extension to train.py, ~60 lines)
- Dependencies: 3 (torch, model.py, evaluate.py)
- Algorithm: 3 (regressor-only training loop + frozen encoder protocol)
- Integration: 3 (called by main.py after full-training Condition A completes)

---

### Epic E6: Figures & Results (experiment)

**Description:** Implement all 5 mandatory figures (FR-8.1–FR-8.5). Save `results.json` with per-condition × per-seed ρ values. Load Condition G (PCA) results from h-m2/results.json for comparison table.

**Files:** `h-m3/code/figures.py`, `h-m3/results.json`

**Complexity Score: 9 (Medium)**
- Module Size: 3 (moderate — ~150 lines for 5 figures)
- Dependencies: 2 (matplotlib, numpy)
- Algorithm: 2 (bar charts, heatmap, CI visualization — standard)
- Integration: 2 (called from main.py at end; reads results dict)

---

### Epic E7: Experiment Orchestrator & CLI (experiment)

**Description:** `main.py` CLI that runs all 6 conditions × 3 seeds. Supports `--condition` flag for single-condition runs. Aggregates results, runs gate checks, calls figure generation. Saves `results.json`.

**Files:** `h-m3/code/main.py`

**Complexity Score: 10 (Medium)**
- Module Size: 3 (moderate — ~150 lines)
- Dependencies: 4 (all local modules)
- Algorithm: 2 (orchestration loop, no novel algorithm)
- Integration: 1 (top-level orchestrator)

---

## Epic Task Summary

| ID | Name | Type | Complexity | Level |
|----|------|------|------------|-------|
| E1 | Data Pipeline | data-pipeline | 10 | Medium |
| E2 | NFT Model + CanonicalWeightEncoder | model | 16 | High |
| E3 | Training Loop | training | 13 | Medium |
| E4 | Evaluation & Gate Checks | evaluation | 12 | Medium |
| E5 | Frozen-Encoder Sub-Experiment | training | 11 | Medium |
| E6 | Figures & Results | experiment | 9 | Medium |
| E7 | Experiment Orchestrator & CLI | experiment | 10 | Medium |

**Total Epics: 7** (within FULL tier range 6–12 ✓)

---

## External Dependencies

**From h-m2/code/data_prep.py (actual code, verified):**
- `apply_condition_d(X: np.ndarray) -> np.ndarray` — args: X (N, 51850); returns canonicalized X
- `train_test_split_fixed(X, Y, test_size, seed)` — returns X_tr, X_te, Y_tr, Y_te
- `load_and_flatten()` — returns (X, Y, label_names)

**From h-m1/code/data_loader.py (actual code, verified via h-m2 import):**
- `load_zoo()` — returns list of records with `weights_flat` tensor and property fields
- `SPLITS = [50176, 64, 640, 10]` — layer boundary indices
- `EXPECTED_DIM = 51850` — confirmed weight vector dimension

---

## Dependency Flow

```
data_prep.py ──→ model.py ──→ train.py ──→ main.py
                                 ↓              ↓
              evaluate.py ←──────┘         figures.py
                   ↑
              config.py (shared by all)
```
