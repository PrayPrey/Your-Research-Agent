# Architecture: H-C1 (Influence Fragility Ratio)

**Type:** CONDITION / EXISTENCE-style PoC (mechanistic follow-up to H-M2)
**Applied:** Gradient-based attribution (TRAK) + k-NN redundancy normalization (RL-Selector ε-cover pattern)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends H-M2, reuses H-M1 CCR labels)
**Status:** Patterns found from H-M2/H-M1 actual code
**Analyzed Path:** `docs/youra_research/h-m2/code/`, `docs/youra_research/h-m1/code/`
**Findings:** Both prior hypotheses use flat-file modules (`config.py`, `evaluate.py`, `visualize.py`) loaded via `importlib` in `main.py`, with a `Config` dataclass and a `run_simulated()` fallback (synthetic RNG data) since no GPU/real checkpoints are available in this environment. H-C1 follows the same simulated-data pattern: real Pythia-1B checkpoint and TRAK scores from H-M2 don't exist as files, so embeddings/TRAK/CCR are synthesized with fixed seed for PoC gate testing, with real-path functions (`extract_embeddings`, real `np.load`) present but unused unless artifacts exist.

## File Structure

- `h-c1/code/config.py` — Config dataclass
- `h-c1/code/ifr_computer.py` — IFRComputer class + embedding extraction
- `h-c1/code/evaluate.py` — statistical gate tests
- `h-c1/code/visualize.py` — figures
- `h-c1/code/main.py` — orchestration (real-data path, mirrors H-M2 main.py)
- `h-c1/code/main_simulated.py` — synthetic-data fallback (mirrors H-M2 pattern)
- `h-c1/figures/` — output plots

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    trak_scores_path: str = "../h-m2/trak_attribution_scores.npy"
    ccr_scores_path: str = "../h-m1/ccr_scores.npy"
    checkpoint_path: str = "../h-m2/checkpoint-final"
    top_pct: float = 0.01
    knn_k: int = 50
    seed: int = 42
    output_dir: str = "figures"
```

### IFRComputer / extract_embeddings (`ifr_computer.py`)

**Dependencies**: numpy, scipy, sklearn, transformers (real path only)

```python
def extract_embeddings(model, tokenizer, texts: list[str], batch_size: int = 32) -> np.ndarray: ...
    # mean-pool last_hidden_state over attention_mask, returns [N, D]

class IFRComputer:
    def __init__(self, embeddings: np.ndarray, trak_scores: np.ndarray, k: int = 50): ...
    def compute_redundancy(self) -> np.ndarray: ...       # 1 - mean cosine dist to k-NN
    def compute_ifr(self, redundancy: np.ndarray) -> np.ndarray: ...  # |trak| / max(1-redundancy, 0.01)
    def compute_correlation(self, ifr: np.ndarray, redundancy: np.ndarray) -> tuple[float, float]: ...  # spearmanr
```

### evaluate.py

**Dependencies**: ifr_computer.IFRComputer, scipy.stats

```python
def compute_ifr_statistics(embeddings: np.ndarray, trak_scores: np.ndarray,
                            contaminated_mask: np.ndarray, k: int = 50) -> dict: ...
    # returns ifr_contaminated_mean, ifr_non_contaminated_mean, ifr_diff_pvalue (mannwhitneyu, greater),
    # ifr_redundancy_correlation, correlation_pvalue, gate_1_satisfied, gate_2_satisfied

def validate_gate_conditions(results: dict) -> dict: ...
    # returns gate_1_passed, gate_2_passed, overall_passed, details
```

### visualize.py

**Dependencies**: matplotlib

```python
def plot_ifr_boxplot(ifr_contaminated: np.ndarray, ifr_non_contaminated: np.ndarray,
                      pvalue: float, out_path: str) -> None: ...   # REQUIRED figure
def plot_ifr_redundancy_scatter(ifr: np.ndarray, redundancy: np.ndarray,
                                 rho: float, out_path: str) -> None: ...
def plot_redundancy_by_contamination(redundancy: np.ndarray, contaminated_mask: np.ndarray,
                                      out_path: str) -> None: ...
def plot_trak_by_contamination(trak_scores: np.ndarray, contaminated_mask: np.ndarray,
                                out_path: str) -> None: ...
```

### main.py (real-data path)

**Dependencies**: config, ifr_computer, evaluate, visualize (loaded via `_load_local`, mirrors H-M2/H-M1 pattern)

```python
def run(cfg: Config) -> dict: ...
    # load trak_scores, ccr_scores (np.load); if files missing -> fall back to main_simulated.run_simulated
    # select top 1% by |trak|; contaminated_mask = ccr[top_idx] > median(ccr)
    # extract_embeddings from checkpoint (if present) else raise/fallback
    # compute_ifr_statistics -> validate_gate_conditions -> save figures + results JSON
```

### main_simulated.py (fallback, always runnable)

**Dependencies**: config, evaluate, visualize

```python
def run_simulated(cfg: Config) -> dict: ...
    # rng = np.random.default_rng(cfg.seed)
    # synthesize embeddings [N,D], trak_scores [N], contaminated_mask (~half True)
    #   with contaminated examples given systematically higher |trak| and lower redundancy
    #   so PoC gate logic is exercised meaningfully (not just random noise)
    # calls compute_ifr_statistics + validate_gate_conditions + plotting, same as main.run
```

## Data Flow

- Input: `h-m2/trak_attribution_scores.npy`, `h-m1/ccr_scores.npy`, `h-m2/checkpoint-final` (if present) → else synthetic
- Process: top-1% TRAK selection → CCR-median contamination split → embedding extraction → k-NN redundancy → IFR → Mann-Whitney U + Spearman
- Output: `figures/ifr_boxplot.png` (required), `figures/ifr_redundancy_scatter.png`, `figures/redundancy_by_contamination.png`, `figures/trak_by_contamination.png`, results dict/JSON with gate_1_passed/gate_2_passed/overall_passed

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| H-M2 TRAK scores | `np.load("../h-m2/trak_attribution_scores.npy")` | `h-m2/trak_attribution_scores.npy` (not yet generated — H-M2 ran simulated) |
| H-M1 CCR scores | `np.load("../h-m1/ccr_scores.npy")` | `h-m1/ccr_scores.npy` (not yet generated — H-M1 ran simulated) |
| H-M2 checkpoint | `AutoModelForCausalLM.from_pretrained("../h-m2/checkpoint-final")` | `h-m2/checkpoint-final` (not present — no GPU training occurred) |

**Verified from**: `docs/youra_research/h-m2/code/` and `docs/youra_research/h-m1/code/` — both hypotheses ran `main_simulated.py` (real artifacts were never produced, since no GPU was available). H-C1 must therefore default to `main_simulated.py` as the actual runnable path, same as its predecessors.

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Config | Config dataclass with paths/hyperparams | 4 | 1+1+1+1 |
| C-2 | IFRComputer | redundancy + IFR + correlation methods | 9 | 3+2+3+1 |
| C-3 | Embedding extraction | mean-pool hidden states (real-path fn) | 5 | 2+1+2+0 |
| C-4 | Statistical gate logic | compute_ifr_statistics, validate_gate_conditions | 7 | 2+2+2+1 |
| C-5 | Visualization | 4 plot functions | 6 | 2+1+2+1 |
| C-6 | Simulated data generator | synthetic embeddings/trak/ccr with signal | 8 | 3+1+3+1 |
| C-7 | main_simulated orchestration | wire config→gen→compute→plot | 6 | 2+2+1+1 |
| C-8 | main orchestration (real-data path + fallback) | load artifacts, fallback to simulated if missing | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-2], Low(4-8): [C-1, C-3, C-4, C-5, C-6, C-7, C-8]
