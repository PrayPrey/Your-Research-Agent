# Architecture: H-M2 (AI Formality Response Varies)

**Type:** MECHANISM | **Tier:** STANDARD

Applied: No direct KB match for human-AI formality correlation pipeline (searched "DL experiment architecture correlation analysis pipeline" — only unrelated diffusers results); design follows PRD/brief spec directly, reusing H-M1 data-loading pattern + DeBERTa scoring from brief pseudo-code.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** `h-m1/code/` exists on disk (implemented, not spec-only). Verified actual functions via Serena.
**Analyzed Path:** `docs/youra_research/h-m1/code/data.py`, `bcs.py`, `config.py`
**Findings:**
- `data.py::load_conversations(dataset_name: str, max_samples: int = None) -> list` — loads + parses HF hh-rlhf into `{'turns': [...]}` dicts.
- `data.py::extract_role_turns(conversation: dict) -> tuple[list[str], list[str]]` — splits into (user_texts, ai_texts), directly reusable to get human_1/AI_1 (first element of each list).
- `config.py` uses `BASE_DIR`/`H_E1_DIR` path pattern relative to `os.path.dirname(os.path.dirname(__file__))` — H-M2 will follow same convention.
- No formality-scoring code exists in H-M1 (H-M1 used BCS complexity, not DeBERTa formality) — must implement `formality.py` fresh per brief's `HumanAIFormalityCorrelationAnalyzer` pseudo-code.

---

## Module Structure

### config.py (`h-m2/code/config.py`)

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_M1_DIR = os.path.join(os.path.dirname(BASE_DIR), "h-m1")
SEED = 42
DATASET_NAME = "Anthropic/hh-rlhf"
MIN_TURNS = 4
MIN_MSG_LEN = 5
MODEL_NAME = "s-nlp/deberta-large-formality-ranker"
MAX_SEQ_LEN = 512
BATCH_SIZE = 32
N_PERMUTATIONS = 1000
GATE_R_THRESHOLD = 0.1
GATE_P_THRESHOLD = 0.001
MIN_SAMPLE_SIZE = 10000
OUTPUT_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "formality_correlation.pkl")
```

### data.py (`h-m2/code/data.py`)

**Dependencies:** config.py; reuses `h-m1/code/data.py` functions (see External Dependencies)

```python
def load_and_pair(dataset_name: str = DATASET_NAME, min_turns: int = MIN_TURNS) -> list[tuple[str, str]]: ...
    # returns [(human_1, ai_1), ...] using h_m1 load_conversations + extract_role_turns
def validate_pair(human_1: str, ai_1: str, min_len: int = MIN_MSG_LEN) -> bool: ...
    # non-empty after strip, len >= min_len, valid utf-8
```

### formality.py (`h-m2/code/formality.py`)

**Dependencies:** config.py, transformers, torch, tqdm

```python
class FormalityScorer:
    def __init__(self, model_name: str = MODEL_NAME): ...
    def score_batch(self, texts: list[str], batch_size: int = BATCH_SIZE) -> list[float]: ...
        # softmax(logits)[:,1], truncation=True, max_length=512, padding=True

def score_pairs(pairs: list[tuple[str, str]], scorer: FormalityScorer) -> tuple[list[float], list[float]]: ...
    # returns (human_scores, ai_scores)
```

### correlation.py (`h-m2/code/correlation.py`)

**Dependencies:** config.py, numpy, scipy.stats

```python
def compute_correlation(human_scores: list[float], ai_scores: list[float]) -> dict: ...
    # {'n','pearson_r','pearson_p','spearman_rho','spearman_p','human_mean','human_sd','ai_mean','ai_sd'}
def check_gate(results: dict, r_thresh: float = GATE_R_THRESHOLD, p_thresh: float = GATE_P_THRESHOLD) -> bool: ...
    # |r| > r_thresh AND p < p_thresh AND n >= MIN_SAMPLE_SIZE
```

### baseline.py (`h-m2/code/baseline.py`)

**Dependencies:** config.py, numpy, scipy.stats

```python
def run_permutation_test(human_scores: list[float], ai_scores: list[float], n_permutations: int = N_PERMUTATIONS, seed: int = SEED) -> dict: ...
    # shuffle ai_scores n times, returns {'null_rs', 'null_p', 'observed_r'}
```

### ablation.py (`h-m2/code/ablation.py`)

**Dependencies:** config.py, correlation.py, numpy

```python
def per_model_breakdown(pairs: list[tuple[str, str]], scores: tuple, model_ids: list[str] | None) -> dict: ...
def turn_position_variation(dataset_name: str, turn_position: int = 2) -> dict: ...
    # rerun pipeline on (human_2, AI_2)
def extreme_formality_filter(human_scores, ai_scores, low_q: float = 0.25, high_q: float = 0.75) -> dict: ...
def length_partial_correlation(human_scores, ai_scores, human_texts, ai_texts) -> dict: ...
    # partial correlation controlling for message length
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies:** matplotlib, seaborn, correlation.py

```python
def plot_scatter_regression(human_scores: list[float], ai_scores: list[float], r: float, save_path: str) -> None: ...
def plot_correlation_bar(observed_r: float, threshold: float, save_path: str) -> None: ...
def plot_hexbin(human_scores: list[float], ai_scores: list[float], save_path: str) -> None: ...
def plot_qq(residuals: list[float], save_path: str) -> None: ...
def plot_residuals(human_scores: list[float], ai_scores: list[float], save_path: str) -> None: ...
```

### run_experiment.py (`h-m2/code/run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> dict: ...  # load -> score -> correlate -> baseline -> gate -> figures -> (ablation if fail)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Data loading + pairing | Reuse H-M1 load_conversations/extract_role_turns, extract (human_1, AI_1), validate | 6 | 1+2+1+2 |
| M2-2 | DeBERTa formality scorer | Load model, batch inference, GPU/CPU handling, tqdm | 8 | 2+2+3+1 |
| M2-3 | Score all pairs | Run scorer over ~52K messages, memory-efficient batching | 6 | 1+1+2+2 |
| M2-4 | Correlation analysis | Pearson + Spearman, stats dict, sample size check | 5 | 1+1+2+1 |
| M2-5 | Permutation baseline | 1000 shuffles, null distribution, seed=42 | 6 | 1+2+2+1 |
| M2-6 | Gate evaluation | Combine r/p/n thresholds, PASS/FAIL decision | 3 | 1+1+1+0 |
| M2-7 | Visualization suite | Scatter+regression, correlation bar (required); hexbin/QQ/residual (optional) | 6 | 2+1+1+2 |
| M2-8 | Ablation studies (conditional) | Per-model, turn-2 position, extreme filter, length partial-corr — only if gate fails | 9 | 2+2+3+2 |
| M2-9 | End-to-end orchestration + report | Run full pipeline on 26K+ pairs, verify gate, save results | 6 | 1+2+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2-8], Low(4-8): [M2-1, M2-2, M2-3, M2-4, M2-5, M2-6, M2-7, M2-9]

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_conversations | `from h_m1.code.data import load_conversations` | `h-m1/code/data.py` |
| extract_role_turns | `from h_m1.code.data import extract_role_turns` | `h-m1/code/data.py` |

**Verified from:** `h-m1/code/data.py` (actual implementation, via Serena `get_symbols_overview`/`find_symbol`). `load_conversations(dataset_name, max_samples=None) -> list` returns dicts with `'turns'` key; `extract_role_turns(conversation) -> (user_texts, ai_texts)`. H-M2's `load_and_pair` takes `user_texts[0]`/`ai_texts[0]` as human_1/AI_1. If import fails at runtime, Phase 4 Coder must inline equivalent parse logic from brief's `parse_conversation`.

---

## File Organization

```
h-m2/code/
  config.py
  data.py
  formality.py
  correlation.py
  baseline.py
  ablation.py
  visualize.py
  run_experiment.py
h-m2/results/
  formality_correlation.pkl
h-m2/figures/
  scatter_regression.png
  correlation_bar.png
  hexbin_density.png
  qq_plot.png
  residual_plot.png
```
