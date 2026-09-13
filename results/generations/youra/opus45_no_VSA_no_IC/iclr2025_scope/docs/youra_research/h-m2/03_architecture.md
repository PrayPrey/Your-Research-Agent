# Architecture: h-m2

**Type**: MECHANISM | **Gate**: MUST_WORK

Applied: linregress slope + percentile bootstrap CI pattern (scipy/numpy, consistent with h-e1 analyze.py)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable (no active project registered for this path); analyzed h-e1 code directly via file reads instead.
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 code is NOT green-field (contrary to its own 03_architecture.md note) — full implementation exists: `config.py`, `data.py` (SQuAD-v2 only), `model.py` (Pythia+LoRA factory, `apply_lora(model, rank, alpha, dropout, target_modules)`), `train.py` (`train_one_run`, `evaluate_squad_f1`, `compute_squad_f1`), `main.py` (`run_sweep`), `analyze.py` (`compute_r_opt`, `fit_scaling_law`, `plot_scaling`, `check_pass_fail`). All flat modules, no package structure — h-m2 will import these directly via sys.path insert of h-e1 code dir.

---

## File Structure

- `config.py` — h-m2 config: adds HotpotQA path, extends Paths for new artifacts
- `data.py` — HotpotQA (distractor) load + tokenization (mirrors `tokenize_squad` shape)
- `train_hotpotqa.py` — `train_one_run` variant for HotpotQA F1
- `main.py` — sweep driver: SQuAD-v2 (reuse h-e1 CSV) + HotpotQA (72 new runs) → combined CSV
- `sensitivity.py` — `compute_sensitivity`, per-(model,dataset,seed) slope calc
- `analyze.py` — phase transition t-test, bootstrap ratio CI, power-law fit S=a·N^γ
- `visualize.py` — sensitivity-vs-scale plot, rank-curve overlay plot

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| MODELS, MODEL_HF_IDS, RANKS, SEEDS, TrainConfig | `from config import MODELS, MODEL_HF_IDS, RANKS, SEEDS, TrainConfig` | `h-e1/code/config.py` |
| load_base_model, load_tokenizer, apply_lora | `from model import load_base_model, load_tokenizer, apply_lora` | `h-e1/code/model.py` |
| load_squad_v2, tokenize_squad | `from data import load_squad_v2, tokenize_squad` | `h-e1/code/data.py` |
| train_one_run (SQuAD-v2), evaluate_squad_f1 | `from train import train_one_run, evaluate_squad_f1` | `h-e1/code/train.py` |
| h-e1 SQuAD-v2 results (72 runs, reused directly) | n/a — CSV read | `h-e1/code/results/h-e1_rank_sweep.csv` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, read directly).
**Integration approach**: h-m2's `code/` dir prepends h-e1's `code/` path to `sys.path` (or copies the 5 files) to import flat modules with no rename conflicts — `config.py` name collides, so h-m2 config module is renamed internally when importing h-e1 constants (`import h_e1_config as base_config` via importlib, or simplest: copy `model.py`/`data.py`/`train.py` unmodified into h-m2/code/ and only add new files). **Simplest path (chosen)**: copy h-e1's `config.py`, `model.py`, `data.py`, `train.py` verbatim into `h-m2/code/` (no logic changes) and add HotpotQA-specific + analysis modules alongside.

## Modules

### Config (`config.py`, extends h-e1 config)

**Dependencies**: none (copied base + additions)

```python
# ... MODELS, MODEL_HF_IDS, RANKS, SEEDS, TARGET_MODULES, TrainConfig, LoRAConfig unchanged from h-e1

DATASETS = ["squad_v2", "hotpotqa"]

@dataclass
class Paths:
    rank_sweep_squad_csv: str = "../h-e1/code/results/h-e1_rank_sweep.csv"  # reused
    rank_sweep_hotpotqa_csv: str = "results/h-m2_rank_sweep_hotpotqa.csv"
    sensitivities_csv: str = "results/h-m2_sensitivities.csv"
    phase_transition_json: str = "results/h-m2_phase_transition.json"
    sensitivity_plot_png: str = "figures/h-m2_sensitivity_vs_scale.png"
    rank_curves_png: str = "figures/h-m2_rank_curves.png"

@dataclass
class StatsConfig:
    alpha: float = 0.05
    n_bootstrap: int = 1000
    ratio_threshold: float = 2.0
    ci_lower_threshold: float = 1.5
```

### Data (`data.py`, extends h-e1 data)

**Dependencies**: Config

```python
# load_squad_v2, tokenize_squad unchanged (copied from h-e1)

def load_hotpotqa(cache_dir: str | None = None) -> DatasetDict:
    """Load HotpotQA distractor-setting validation split (hotpot_qa, 'distractor')."""
    ...

def tokenize_hotpotqa(dataset: DatasetDict, tokenizer, max_length: int = 384) -> DatasetDict:
    """Tokenize HotpotQA for extractive QA; same span-mapping logic as tokenize_squad,
    context = concatenated supporting + distractor paragraphs."""
    ...
```

### Train HotpotQA (`train_hotpotqa.py`)

**Dependencies**: Data, Model (h-e1 copy), Config

```python
def train_one_run_hotpotqa(model_id: str, rank: int, seed: int, cfg: TrainConfig) -> float:
    """Same training loop as h-e1 train_one_run but uses load_hotpotqa/tokenize_hotpotqa
    and compute_hotpotqa_f1 for eval. Reuses model.load_base_model/apply_lora."""
    ...

def compute_hotpotqa_f1(predictions: list[dict], references: list[dict]) -> float:
    """F1 via evaluate.load('squad') metric applied to HotpotQA span predictions
    (span-based F1, same formula as SQuAD)."""
    ...
```

### Main / Sweep Driver (`main.py`)

**Dependencies**: train_hotpotqa, Config

```python
def run_hotpotqa_sweep(resume: bool = True) -> None:
    """Loops MODELS x RANKS x SEEDS (72 runs) for HotpotQA only (SQuAD-v2 reused
    from h-e1 CSV). Appends to results/h-m2_rank_sweep_hotpotqa.csv:
    (model,rank,seed,f1_score,timestamp). Resume-safe like h-e1 main.py."""
    ...

def build_combined_dataset(squad_csv: str, hotpotqa_csv: str) -> pd.DataFrame:
    """Merges h-e1 SQuAD-v2 CSV + h-m2 HotpotQA CSV into one long-format
    DataFrame with a 'dataset' column."""
    ...
```

### Sensitivity (`sensitivity.py`)

**Dependencies**: Config

```python
def compute_sensitivity(ranks: list[int], f1_scores: list[float]) -> float:
    """S = |slope| of linregress(log2(ranks), f1_scores)."""
    ...

def compute_all_sensitivities(combined_df: pd.DataFrame, output_csv: str | None = None) -> pd.DataFrame:
    """Groups by (model, dataset, seed); applies compute_sensitivity over the 6
    ranks. Writes results/h-m2_sensitivities.csv: (model,dataset,seed,sensitivity)."""
    ...
```

### Analyze (`analyze.py`)

**Dependencies**: Config, Sensitivity output

```python
def test_phase_transition(sens_1b: list[float], sens_12b: list[float], cfg: StatsConfig) -> dict:
    """One-sided t-test H0: S(12B) <= 2*S(1B); bootstrap 95% CI for ratio
    S(12B)/S(1B) (n_bootstrap resamples). Returns
    {ratio, ci_low, ci_high, p_value, pass}."""
    ...

def fit_power_law(sensitivities_df: pd.DataFrame) -> dict:
    """OLS fit log(S) = gamma*log(N) + log(a) per dataset; bootstrap CI for gamma.
    Writes results/h-m2_phase_transition.json (merges with test_phase_transition output)."""
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: Config

```python
def plot_sensitivity_vs_scale(sensitivities_df: pd.DataFrame, fit_result: dict, output_png: str | None = None) -> None:
    """S vs log10(N) scatter with error bars (mean+-std across seeds), power-law
    fit line, per-dataset color. Writes figures/h-m2_sensitivity_vs_scale.png."""
    ...

def plot_rank_curves(combined_df: pd.DataFrame, output_png: str | None = None) -> None:
    """F1 vs rank overlay, one line per (model,dataset), faceted or color-coded.
    Writes figures/h-m2_rank_curves.png."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Import h-e1 base modules | Copy config/model/data/train.py from h-e1, verify SQuAD-v2 path still works | 4 | 1+1+1+1 |
| B-2 | HotpotQA data pipeline | Load hotpot_qa distractor split, tokenize with span mapping | 8 | 3+1+3+1 |
| B-3 | HotpotQA train/eval | Training loop + F1 scoring for HotpotQA | 9 | 2+2+3+2 |
| B-4 | HotpotQA sweep driver | Orchestrate 72 runs, resume-safe, write rank_sweep_hotpotqa.csv | 8 | 2+2+1+3 |
| B-5 | Combine datasets | Merge h-e1 SQuAD CSV + h-m2 HotpotQA CSV into long-format df | 3 | 1+1+0+1 |
| B-6 | Sensitivity calculation | Per-(model,dataset,seed) log-rank slope via linregress | 5 | 1+1+2+1 |
| B-7 | Phase transition test | One-sided t-test + bootstrap CI for S(12B)/S(1B) ratio | 8 | 2+2+3+1 |
| B-8 | Power-law fit | log(S) vs log(N) OLS, bootstrap CI for gamma, write JSON | 6 | 2+1+2+1 |
| B-9 | Visualization | Sensitivity-vs-scale plot + rank-curves overlay plot | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-3, B-7], Low(4-8): [B-1, B-2, B-4, B-5, B-6, B-8, B-9]
