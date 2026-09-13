# Architecture: H-E1 Agency Proxy Extraction

**Type:** EXISTENCE (PoC) — minimal structure
**Applied:** TF-IDF + LogisticRegression text classification pattern (sklearn standard pipeline)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no h-e1/code/ or base hypothesis folder found in repo.

---

## File Structure

```
h-e1/code/
  data.py       # dataset loading + response extraction
  model.py      # AgencyProxyDetector + baselines
  evaluate.py   # AUROC computation + figures
  train.py      # entrypoint: load -> fit -> evaluate
  config.py     # fixed config constants
figures/        # output plots
```

---

## Modules

### config.py (`h-e1/code/config.py`)

**Dependencies**: None

```python
RANDOM_STATE = 42
TFIDF_PARAMS = dict(ngram_range=(1, 2), max_features=5000)
LOGREG_PARAMS = dict(C=1.0, max_iter=1000, random_state=RANDOM_STATE)
PROXY_TYPES = ["clarifying_question", "option_enumeration", "epistemic_hedging", "explicit_deferral"]
AUROC_TARGET = 0.8
FIGURES_DIR = "h-e1/figures"
```

### data.py (`h-e1/code/data.py`)

**Dependencies**: config.py

```python
def load_hh_rlhf() -> list[str]: ...          # harmless-base + helpful-base, extract assistant turns
def load_reward_bench_safety() -> list[str]: ...  # safety subset responses
def extract_responses(dataset) -> list[str]: ...  # dialogue -> assistant text, normalize whitespace/lowercase
def build_labels(texts: list[str], proxy: str) -> list[int]: ...  # regex-derived binary ground truth per proxy
```

### model.py (`h-e1/code/model.py`)

**Dependencies**: config.py

```python
class AgencyProxyDetector:
    PROXY_PATTERNS: dict[str, list[str]]  # from experiment brief FR-4

    def match_pattern(self, text: str, proxy: str) -> bool: ...
    def fit(self, texts: list[str], labels: list[int]) -> "AgencyProxyDetector": ...  # TF-IDF + LogReg
    def predict_proba(self, texts: list[str]) -> list[float]: ...

def random_baseline(n: int) -> list[float]: ...     # DummyClassifier(strategy="uniform")
def majority_baseline(labels: list[int]) -> list[float]: ...  # DummyClassifier(strategy="most_frequent")
```

### evaluate.py (`h-e1/code/evaluate.py`)

**Dependencies**: model.py, config.py

```python
def compute_auroc(y_true: list[int], y_score: list[float]) -> float: ...
def evaluate_all_proxies(detector_results: dict) -> dict[str, float]: ...  # per-proxy AUROC dict
def plot_auroc_bar(results: dict[str, float], out_path: str) -> None: ...      # gate metric, mandatory
def plot_roc_curves(results: dict, out_path: str) -> None: ...                 # 4 subplots
def plot_cooccurrence_heatmap(labels: dict, out_path: str) -> None: ...        # optional
```

### train.py (`h-e1/code/train.py`)

**Dependencies**: data.py, model.py, evaluate.py, config.py

```python
def main() -> None: ...
# loads datasets -> for each proxy: fit AgencyProxyDetector, random/majority baselines ->
# evaluate_all_proxies -> generate figures -> print pass/fail vs AUROC_TARGET
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset loading | Load HH-RLHF + RewardBench Safety, extract responses | 8 | 2+3+2+1 |
| A-2 | Regex pattern detectors | Implement 4 PROXY_PATTERNS + match_pattern | 5 | 2+1+2+0 |
| A-3 | Label construction | Build binary ground-truth labels per proxy from patterns/annotations | 6 | 2+2+2+0 |
| A-4 | AgencyProxyDetector classifier | TF-IDF + LogisticRegression fit/predict_proba | 7 | 2+2+3+0 |
| A-5 | Baseline models | Random + majority DummyClassifier wrappers | 3 | 1+1+1+0 |
| A-6 | Evaluation pipeline | AUROC per proxy via sklearn.metrics | 5 | 1+2+1+1 |
| A-7 | Visualization | AUROC bar chart + ROC subplots to figures/ | 6 | 2+1+1+2 |
| A-8 | Integration + run | train.py wiring, end-to-end run, pass/fail gate check | 7 | 1+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8]
