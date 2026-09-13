# Architecture: h-c1

**Type**: CONDITION | **Gate**: SHOULD_WORK

Applied: HF Trainer + PEFT LoRA sweep pattern (reused from h-e1; KB search returned no new relevant hits, fallback to prior validated pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-e1 code read directly (Serena has no active project for this workspace; used direct file reads on `h-e1/code/` per fallback — actual implementation verified, not just specs)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 code is a flat module set (`config.py`, `data.py`, `model.py`, `train.py`, `main.py`, `analyze.py`) at package root (no `src/` package prefix, imported via plain `from config import ...`). `MODELS`, `MODEL_HF_IDS`, `RANKS`, `SEEDS`, `TARGET_MODULES`, `TrainConfig`, `Paths` in `config.py` are reusable as-is. `model.py::load_base_model/apply_lora` and `data.py` tokenization pattern generalize directly. `analyze.py::fit_scaling_law`/`compute_r_opt` are dataset-agnostic (operate on CSV with model/rank/seed/f1_score columns) — reusable unmodified for HotpotQA by pointing at a different CSV.

---

## File Structure

- `config.py` — NEW: HotpotQA-specific paths (extends h-e1 `Paths`); imports MODELS/RANKS/SEEDS/TrainConfig from h-e1
- `data_hotpot.py` — NEW: HotpotQA load + multi-doc tokenization (mirrors `h-e1/code/data.py::tokenize_squad`)
- `train_hotpot.py` — NEW: training loop for HotpotQA (mirrors `h-e1/code/train.py`, swaps F1 eval)
- `main.py` — NEW: sweep driver for 72 HotpotQA runs (mirrors `h-e1/code/main.py::run_sweep`)
- `compare.py` — NEW: cross-task comparison (loads h-e1 + h-c1 scaling fits, computes |Δα|, CI overlap, plots)
- (reused unmodified via import) `model.py`, `analyze.py` from h-e1 code path

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| MODELS, MODEL_HF_IDS, RANKS, SEEDS, TrainConfig | `from h_e1.config import MODELS, MODEL_HF_IDS, RANKS, SEEDS, TrainConfig` | `h-e1/code/config.py` |
| load_base_model, load_tokenizer, apply_lora | `from h_e1.model import load_base_model, load_tokenizer, apply_lora` | `h-e1/code/model.py` |
| compute_r_opt, fit_scaling_law, plot_scaling | `from h_e1.analyze import compute_r_opt, fit_scaling_law, plot_scaling` | `h-e1/code/analyze.py` |
| set_seed | `from h_e1.train import set_seed` | `h-e1/code/train.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation; module files are flat, no package `__init__.py` present — h-c1 code dir should add h-e1 code dir to `sys.path` or copy the 3 reused files directly since h-e1 has no package structure)

**Note**: Given h-e1 has no installable package (flat scripts), the pragmatic approach is to copy `config.py`, `model.py`, `analyze.py` into h-c1's code dir unmodified (or symlink) rather than cross-repo import — matches h-e1's own style (no packaging).

## Modules

### Config (`config.py`)

**Dependencies**: h-e1 config (copied)

```python
# Reuse: MODELS, MODEL_HF_IDS, RANKS, SEEDS, TARGET_MODULES, TrainConfig, AnalysisConfig (copy from h-e1/code/config.py)

@dataclass
class Paths:
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_dir: str = "checkpoints"
    rank_sweep_csv: str = "results/h-c1_rank_sweep.csv"
    optimal_ranks_csv: str = "results/h-c1_optimal_ranks.csv"
    scaling_fit_json: str = "results/h-c1_scaling_fit.json"
    comparison_json: str = "results/h-c1_cross_task_comparison.json"
    dual_plot_png: str = "figures/h-c1_dual_scaling_plot.png"
    h_e1_scaling_fit_json: str = "../h-e1/code/results/h-e1_scaling_fit.json"
```

### Data (`data_hotpot.py`)

**Dependencies**: Config

```python
def load_hotpot_qa(cache_dir: str | None = None) -> DatasetDict:
    """load_dataset('hotpotqa/hotpot_qa', 'distractor', cache_dir=cache_dir)"""
    ...

def tokenize_hotpot(dataset: DatasetDict, tokenizer, max_length: int = 512) -> DatasetDict:
    """Concat supporting + distractor docs into single context, then
    reuse SQuAD-style answer-span tokenization (same offset-mapping logic as h-e1/data.py)."""
    ...
```

### Model (reused unmodified, copied from h-e1)

**Dependencies**: Config

```python
# model.py — identical to h-e1/code/model.py: load_base_model, load_tokenizer, apply_lora
```

### Train (`train_hotpot.py`)

**Dependencies**: data_hotpot, model (reused), Config

```python
def train_one_run(model_id: str, rank: int, seed: int, cfg: TrainConfig,
                   output_dir: str = "checkpoints", data_cache_dir: str | None = None) -> dict:
    """Trains LoRA adapter on HotpotQA; returns {'answer_f1': float, 'sp_f1': float}."""
    ...

def evaluate_hotpot(model, val_loader, tokenizer, val_dataset, device) -> dict:
    """Answer F1 (span-based, same decode as h-e1) + Supporting Facts F1
    (sentence-level overlap vs gold supporting_facts)."""
    ...

def compute_sp_f1(predicted_sentences: list, gold_supporting_facts: list) -> float: ...
```

### Main / Sweep Driver (`main.py`)

**Dependencies**: train_hotpot, Config

```python
def run_sweep() -> None:
    """Loops MODELS x RANKS x SEEDS (72 runs). Appends each run's
    (model,rank,seed,f1_score,sp_f1,timestamp) to results/h-c1_rank_sweep.csv.
    Structure identical to h-e1/code/main.py::run_sweep (resume-safe, error log)."""
    ...
```

### Analyze (reused unmodified, copied from h-e1)

**Dependencies**: Config

```python
# analyze.py — identical to h-e1/code/analyze.py:
#   compute_r_opt(sweep_csv) -> writes results/h-c1_optimal_ranks.csv
#   fit_scaling_law(optimal_ranks, n_bootstrap=1000) -> writes results/h-c1_scaling_fit.json
#   plot_scaling(...) -> single-dataset plot (not the required dual plot; see compare.py)
```

### Compare (`compare.py`)

**Dependencies**: Config, analyze (reused)

```python
def load_scaling_fit(path: str) -> dict:
    """Read h-e1 or h-c1 *_scaling_fit.json."""
    ...

def compare_alphas(fit_squad: dict, fit_hotpot: dict) -> dict:
    """|alpha_squad - alpha_hotpot|, CI overlap bool, pass = diff <= 0.15.
    Writes results/h-c1_cross_task_comparison.json."""
    ...

def plot_dual_scaling(optimal_squad: pd.DataFrame, optimal_hotpot: pd.DataFrame,
                       fit_squad: dict, fit_hotpot: dict, comparison: dict) -> None:
    """Dual log-log scaling plot (both datasets + fit lines + CI bands) and
    |Δα| bar with 0.15 threshold line. Writes figures/h-c1_dual_scaling_plot.png."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Verify + copy h-e1 artifacts | Check h-e1_scaling_fit.json exists; copy config.py/model.py/analyze.py | 4 | 1+2+1+0 |
| C-2 | HotpotQA data pipeline | Load distractor split, concat docs, span tokenization (max_length=512) | 8 | 2+1+3+2 |
| C-3 | HotpotQA train/eval loop | Training loop + Answer F1 + Supporting Facts F1 | 10 | 3+2+3+2 |
| C-4 | Sweep driver (72 runs) | Orchestrate model x rank x seed, resume-safe CSV writer | 7 | 2+2+1+2 |
| C-5 | r_opt + scaling fit (HotpotQA) | Reuse analyze.py compute_r_opt/fit_scaling_law on h-c1 CSV | 3 | 1+1+1+0 |
| C-6 | Cross-task comparison | Load both fits, |Δα|, CI overlap, pass/fail | 5 | 1+1+2+1 |
| C-7 | Dual visualization | Dual scaling plot + Δα threshold bar chart | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-3], Low(4-8): [C-1, C-2, C-4, C-5, C-6, C-7]
