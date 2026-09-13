# Architecture: H-M3 (MECHANISM)

**Hypothesis:** Amplification Index (AI) is positive for perplexity filtering vs random (AI > 0, 95% CI excludes zero)
**Type:** MECHANISM — inference/analysis only, no new training in principle... but see Codebase Analysis (PoC reality below)

Applied: accuracy-differential-with-bootstrap-CI pattern (mirrors H-M1's `bootstrap_ccr_diff`, generalized to paired group statistic)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1)
**Status:** Actual code exists at `h-m1/code/` (contradicts PRD assumption). Read directly (get_symbols_overview on directory failed; read files individually).
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings — IMPORTANT DEVIATION FROM PRD:**
- PRD FR-1 assumes 15 **saved** Pythia-1B checkpoints (`random_seed{1-5}`, `perplexity_seed{1-5}`, `dedup_seed{1-5}`) exist on disk. **They do not.** H-M1's `main.py` trains models in-memory (`train_one_run` returns `(model, tokenizer)` objects, never calls `save_checkpoint` — that function doesn't exist) and never persists them. No `checkpoints/` directory exists.
- H-M1 is a PoC: `model_id="EleutherAI/pythia-70m"` (not pythia-1b), `seeds=(42,)` (1 seed, not 5), 3 strategies are `("perplexity", "random", "inverse_perplexity")` — **no "dedup" strategy exists**.
- H-M1 evaluates CCR (corpus/benchmark n-gram overlap), not MMLU accuracy. There is no `eval_mmlu_accuracy` implementation despite being named in spec — H-M1 never actually computes MMLU accuracy per model.
- **Consequence for H-M3**: Cannot "load 15 checkpoints" as PRD FR-1 states. H-M3 must reuse H-M1's actual `train_one_run`, `filter_by_strategy`, `load_corpus` functions to retrain small models in-process (matching PoC scale: pythia-70m, few seeds), then run its own MMLU log-likelihood evaluation on the resulting in-memory models. Strategies used: `perplexity` and `random` only (drop `dedup`, not present in H-M1).
- `detect.py::compute_ccr` and `ngram_overlap_detect` are reusable as-is for optional contamination cross-checks but are NOT required for AI (AI uses MMLU vs MMLU-Redux partition, not n-gram detection).

---

## File Structure

```
h-m3/code/
  config.py       # seeds, strategies (perplexity/random), eval settings
  data.py         # MMLU + MMLU-Redux loading, contaminated/clean masks
  models.py       # thin wrapper: reuse h-m1 train_one_run per (strategy, seed)
  evaluate.py      # 5-shot MMLU log-likelihood scoring per model
  metrics.py       # Amplification Index + paired bootstrap CI
  visualize.py     # AI bar chart (required) + optional figures
  main.py          # orchestrates N models -> eval -> AI -> gate -> figures
figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"     # matches h-m1 PoC scale
    strategies: tuple = ("perplexity", "random")  # h-m1 has no "dedup"
    seeds: tuple = (42, 43, 44)                   # ponytail: 3 seeds for PoC CI, not 5
    percentile: int = 30
    corpus_size: int = 2000
    mmlu_subset: int = 500        # subset for eval speed (PoC)
    num_fewshot: int = 5
    batch_size: int = 32
    n_bootstrap: int = 10000
    out_dir: str = "figures/"
```

### Data (`data.py`)

**Dependencies**: Config, `datasets`

```python
def load_mmlu_eval(cfg: Config) -> list[dict]: ...            # cais/mmlu test, verbalized MCQ items
def load_mmlu_redux_clean() -> list[dict]: ...                 # edinburgh-dawg/mmlu-redux-2.0, error_type=="ok"
def build_contamination_masks(mmlu: list[dict], clean: list[dict]) -> tuple[np.ndarray, np.ndarray]: ...
    # returns (contaminated_mask, clean_mask) aligned to mmlu index, via question-text match against clean set
```

### Models (`models.py`)

**Dependencies**: Config, `h-m1/code/train.py::train_one_run`, `h-m1/code/data.py::load_corpus,filter_by_strategy`

```python
def train_all_models(cfg: Config) -> dict:  # {f"{strategy}_seed{seed}": (model, tokenizer)}
    ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: Config

```python
def score_mcq_loglikelihood(model, tokenizer, item: dict, num_fewshot: int) -> int:  # predicted choice idx
    ...
def eval_model_on_mmlu(model, tokenizer, mmlu: list[dict], cfg: Config) -> np.ndarray:  # bool correctness array
    ...
def eval_all(models: dict, mmlu: list[dict], cfg: Config) -> dict:  # {model_id: correctness_array}
    ...
```

### Metrics (`metrics.py`)

**Dependencies**: None (numpy only)

```python
def compute_deltas(correctness: dict, contaminated_mask: np.ndarray, clean_mask: np.ndarray) -> dict:
    # {model_id: acc_contaminated - acc_clean}
    ...
def amplification_index(deltas: dict, treatment: str = "perplexity", baseline: str = "random") -> float:
    ...
def bootstrap_ai_ci(perplexity_deltas: np.ndarray, random_deltas: np.ndarray,
                     n_bootstrap: int = 10000, confidence: float = 0.95) -> tuple[float, float]:
    ...
def gate_check(ai: float, ci_lower: float) -> bool:  # AI > 0 and ci_lower > 0
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: Config

```python
def plot_ai_bar_with_ci(ai: float, ci: tuple[float, float], out_dir: str) -> str: ...   # required
def plot_accuracy_heatmap(deltas: dict, out_dir: str) -> str: ...                        # optional
def plot_delta_boxplot(deltas: dict, out_dir: str) -> str: ...                           # optional
```

### Main (`main.py`)

**Dependencies**: all above

```python
def run_experiment(cfg: Config) -> dict:
    ...

if __name__ == "__main__":
    run_experiment(Config())
```

---

## External Dependencies (Base Hypothesis)

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, read directly)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| train_one_run | `from h_m1_train import train_one_run` (copy or path-extend `h-m1/code/`) | `h-m1/code/train.py` |
| load_corpus | `from h_m1_data import load_corpus, filter_by_strategy` | `h-m1/code/data.py` |
| compute_ccr (optional cross-check) | `from h_m1_detect import compute_ccr` | `h-m1/code/detect.py` |

**Note**: `h-m1/code/` has no `__init__.py`/package structure; Phase 4 Coder should either (a) add `h-m1/code/` to `sys.path` and import directly, or (b) copy the 3 needed functions into `h-m3/code/` (consistent with how H-M1 itself copied from H-E1 due to missing package structure). No `save_checkpoint`/`load_checkpoint` exists in h-m1 — do not assume disk-based model loading.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Config + MMLU/Redux loading | Load cais/mmlu + mmlu-redux-2.0 clean subset | 5 | 1+1+2+1 |
| M3-2 | Contamination masks | Build contaminated/clean boolean masks via question match | 6 | 2+1+2+1 |
| M3-3 | Model training reuse | Wire h-m1 train_one_run for perplexity+random x 3 seeds (6 models) | 8 | 2+3+2+1 |
| M3-4 | 5-shot MCQ log-likelihood scorer | Fewshot prompt build + log-prob scoring | 7 | 2+1+3+1 |
| M3-5 | Batch MMLU evaluation | Run eval_all over 6 in-memory models | 6 | 2+2+1+1 |
| M3-6 | Delta + AI computation | Per-model delta, AI aggregate | 5 | 1+1+2+1 |
| M3-7 | Paired bootstrap CI | 10k resample CI for AI | 6 | 1+2+2+1 |
| M3-8 | Gate + visualization | Gate check, AI bar chart (required), optional figures | 6 | 2+1+1+2 |
| M3-9 | Orchestration | main.py end-to-end run + summary JSON | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M3-1, M3-2, M3-3, M3-4, M3-5, M3-6, M3-7, M3-8, M3-9]

---

## Notes

- Scale reduced from PRD (15x pythia-1B) to PoC-consistent scale (6x pythia-70m, 2 strategies x 3 seeds) to match actually-implemented H-M1 code; `dedup` strategy dropped since H-M1 never implemented it.
- M3-3 is highest complexity: retrains 6 small models in-process since no checkpoints were persisted by H-M1.
- If a future full-scale H-M1 run with persisted pythia-1B checkpoints becomes available, swap `models.py::train_all_models` for a `load_checkpoints` variant — interface (`dict[str, (model, tokenizer)]`) stays the same.
