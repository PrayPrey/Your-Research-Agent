# Architecture: H-M2 (MECHANISM)

**Hypothesis:** Removing high-CCR examples causes >=1.5x larger MMLU accuracy drop than random removal (95% CI excludes 1.0 and random mean)
**Type:** MECHANISM — 3 conditions (baseline/high-CCR-removal/random-removal) x removal fractions, PoC scale mirrors H-M1

Applied: contamination-attribution-pipeline pattern (n-gram CCR + bootstrap CI comparison, extended from H-M1)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1) — actual code present and used
**Status:** `h-m1/code/` fully implemented (PoC scale, not full spec). Analyzed via `get_symbols_overview` + `find_symbol` on all modules.
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:**
- Actual H-M1 code uses `EleutherAI/pythia-70m` (not pythia-1b per spec), single seed, `train_steps=50`, `corpus_size=2000` — PoC scale despite MECHANISM type. H-M2 follows same PoC scale for consistency/runnability.
- `compute_ccr(corpus, benchmark, n=8)` lives in `detect.py` (spec said `evaluate.py` — spec was wrong, trusted code) and returns a single **aggregate** CCR float for a whole corpus, not per-example scores.
- H-M2 requires **per-example** CCR to rank/remove top-5% examples — this does not exist in H-M1 code and must be added locally (`per_example_ccr` in h-m2, reusing `get_ngrams` logic).
- `train_one_run(cfg, corpus, strategy, seed) -> (model, tokenizer)` trains in-memory, no checkpoint save/load — H-M2 reuses this pattern directly (import), training 3 conditions instead of 3 strategies.
- `filter_by_strategy` and `TextDataset` reusable as-is.

---

## File Structure

```
h-m2/code/
  config.py        # removal fractions, conditions, seeds (imports h-m1 Config pattern)
  data.py           # loads h-m1 corpus/mmlu loaders (import from h-m1)
  removal.py        # RemovalIntervention: per-example CCR, high-CCR mask, random mask
  train.py           # thin wrapper around h-m1.train_one_run for 3 conditions
  evaluate.py       # MMLU accuracy proxy (n-gram/exact-match), degradation ratio, bootstrap CI
  visualize.py       # 3 required figures
  main.py            # orchestrates conditions x fractions x seeds, gate check
figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"          # PoC scale, matches h-m1
    conditions: tuple = ("baseline", "high_ccr", "random")
    removal_fractions: tuple = (0.01, 0.02, 0.05)
    seeds: tuple = (42,)                               # ponytail: single seed for PoC; 5 for full run
    ngram_n: int = 8
    percentile: int = 30
    corpus_size: int = 2000
    mmlu_subset: int = 500
    lr: float = 1e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01
    batch_size: int = 16
    seq_len: int = 128
    train_steps: int = 50
    grad_clip: float = 1.0
    n_bootstrap: int = 1000
    out_dir: str = "figures/"
```

### Removal (`removal.py`)

**Dependencies**: Config, detect.get_ngrams (imported from h-m1/code/detect.py)

```python
def per_example_ccr(corpus: list[str], benchmark: list[dict], n: int = 8) -> np.ndarray:
    """CCR score per training example (fraction of its n-grams matching benchmark n-grams)."""
    ...

class RemovalIntervention:
    def __init__(self, ccr_scores: np.ndarray, removal_fraction: float): ...
    def get_high_ccr_mask(self) -> np.ndarray: ...
    def get_random_mask(self, seed: int) -> np.ndarray: ...
    def apply(self, corpus: list[str], mask: np.ndarray) -> list[str]:  # returns corpus minus masked
        ...
```

### Data (`data.py`)

**Dependencies**: h-m1.data (imported, not duplicated)

```python
from h_m1_code.data import load_corpus, load_mmlu, verbalize  # sys.path append to h-m1/code
```

### Train (`train.py`)

**Dependencies**: Config, h-m1.train (imported)

```python
from h_m1_code.train import train_one_run  # reused as-is, returns (model, tokenizer)

def train_condition(cfg: Config, corpus: list[str], condition: str, fraction: float, seed: int) -> tuple:
    """Wraps train_one_run; condition name used only for logging/results keying."""
    ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: Config, Removal (per_example_ccr for masks; MMLU eval independent)

```python
def eval_mmlu_accuracy(model, tokenizer, mmlu: list[dict]) -> float:  # multiple-choice log-likelihood scoring
    ...
def compute_degradation_ratio(baseline_acc: float, high_ccr_acc: float, random_acc: float) -> float: ...
def bootstrap_degradation_ci(baseline: np.ndarray, high_ccr: np.ndarray, random: np.ndarray,
                              n_bootstrap: int = 1000) -> tuple[float, float, float]:  # (mean_ratio, ci_low, ci_high)
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: Config

```python
def plot_gate_metrics(target: dict, actual: dict, out_dir: str) -> None: ...       # required
def plot_accuracy_by_fraction(results: dict, out_dir: str) -> None: ...
def plot_bootstrap_distribution(ratios: np.ndarray, ci: tuple, out_dir: str) -> None: ...
```

### Main (`main.py`)

**Dependencies**: all above

```python
def run_all(cfg: Config) -> dict:  # {fraction: {condition: {seed: {acc, ccr_removed}}}}
    ...

if __name__ == "__main__":
    run_all(Config())
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_corpus, load_mmlu, verbalize | `from h_m1_code.data import load_corpus, load_mmlu, verbalize` | `h-m1/code/data.py` |
| get_ngrams, compute_ccr | `from h_m1_code.detect import get_ngrams, compute_ccr` | `h-m1/code/detect.py` |
| train_one_run, TextDataset | `from h_m1_code.train import train_one_run, TextDataset` | `h-m1/code/train.py` |

**Verified from**: `h-m1/code/` (actual implementation, via Serena `get_symbols_overview`/`find_symbol`).
Note: `compute_ccr` is aggregate-only; H-M2 adds `per_example_ccr` locally in `removal.py` since no per-example scoring exists upstream.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| R-1 | Config + reuse imports | Config dataclass, wire h-m1 module imports (sys.path) | 4 | 1+1+1+1 |
| R-2 | Per-example CCR scoring | `per_example_ccr` using h-m1's `get_ngrams`, vectorized over corpus | 7 | 2+2+2+1 |
| R-3 | RemovalIntervention class | High-CCR mask (top-5%), random mask, apply() removal | 6 | 2+1+2+1 |
| R-4 | Corpus + MMLU loading | Reuse h-m1 loaders, build 2000-example base corpus | 3 | 1+1+1+0 |
| R-5 | Training wrapper | Wrap `train_one_run` for 3 conditions x 3 fractions x seeds | 8 | 2+3+2+1 |
| R-6 | MMLU accuracy eval | Multiple-choice log-likelihood scoring on trained models | 7 | 2+2+2+1 |
| R-7 | Degradation ratio + bootstrap CI | Ratio computation, 1000-resample CI, gate check (>=1.5, excludes 1.0) | 8 | 2+2+3+1 |
| R-8 | Visualization | 3 figures (gate metrics, accuracy-by-fraction, bootstrap dist) | 5 | 2+1+1+1 |
| R-9 | Orchestration | main.py loop over fractions x conditions x seeds, results dict, gate summary | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [R-1, R-2, R-3, R-4, R-5, R-6, R-7, R-8, R-9]

---

## Notes

- R-2 (per-example CCR) and R-7 (degradation ratio/bootstrap) are the novel mechanism-specific modules; everything else reuses/wraps h-m1/code/ directly.
- PoC scale (pythia-70m, 50 steps, single seed, 3 fractions x 3 conditions = 9 training runs) mirrors H-M1's actual implementation rather than the full spec (pythia-1b, 15 runs, 5 seeds) — full run requires multi-GPU cluster per H-M1's ponytail notes.
- No checkpoint save/load: `train_one_run` keeps models in-memory per H-M1 pattern; H-M2 evaluates immediately after training within the same process.
