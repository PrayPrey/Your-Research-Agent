# Architecture: H-M2 BAI-Reward Disagreement Analysis

**Type:** MECHANISM
**Applied:** Statistical quartile-disagreement analysis pattern (sklearn StandardScaler + percentile quadrant counting); reward model scoring via HF sequence-classification head (RewardBench pattern)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** H-E1 code found and analyzed — no persisted model artifacts exist
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:**
- `AgencyProxyDetector` (`h-e1/code/model.py:8-34`): `__init__()`, `match_pattern(text, proxy)`, `fit(texts, labels)`, `predict_proba(texts)` — wraps `TfidfVectorizer` + `LogisticRegression`.
- `train.py` fits 4 detectors **in-memory only** — no `joblib`/`pickle` persistence to `h-e1/models/`. PRD's "load H-E1 trained proxy models" must fall back to **inline retraining** using H-E1's `data.py`/`model.py`/`config.py` directly (reusable as library, not artifact loading).
- `data.py` exposes `load_hh_rlhf()`, `load_reward_bench_safety()`, `extract_responses()`, `normalize_text()`, `build_labels(texts, proxy)`.
- `config.py` holds `PROXY_TYPES`, `PROXY_PATTERNS`, `RANDOM_STATE=42`, `TFIDF_PARAMS`, `LOGREG_PARAMS`.

---

## File Structure

```
h-m2/code/
  config.py       # fixed config constants (imports/mirrors h-e1 params)
  bai.py          # BAI computation: retrain proxies via h-e1, aggregate, length-normalize
  reward.py       # reward model loading + scoring (OpenAssistant DeBERTa)
  analysis.py     # quartile disagreement, correlation, mechanism verification
  evaluate.py     # figure generation (bar, scatter, heatmap, histograms)
  run.py          # entrypoint: orchestrate pipeline end-to-end
figures/          # output plots
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| AgencyProxyDetector | `from h_e1.model import AgencyProxyDetector` (or `sys.path` insert to `h-e1/code/`) | `h-e1/code/model.py` |
| Config (PROXY_TYPES, TFIDF_PARAMS, LOGREG_PARAMS, RANDOM_STATE) | `from h_e1.config import PROXY_TYPES, TFIDF_PARAMS, LOGREG_PARAMS, RANDOM_STATE` | `h-e1/code/config.py` |
| Data loading | `from h_e1.data import load_hh_rlhf, load_reward_bench_safety, build_labels` | `h-e1/code/data.py` |

**Verified from**: `h-e1/code/` (actual implementation — `h-e1` dir has no `__init__.py`, so H-M2 `run.py` must `sys.path.insert(0, "../h-e1/code")` before importing, since module names are flat: `import model, data, config` not `h_e1.model`).

**Actual import pattern (matches h-e1/train.py style):**
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code"))
import config as e1_config
from data import load_hh_rlhf, load_reward_bench_safety, build_labels
from model import AgencyProxyDetector
```

---

## Modules

### config.py (`h-m2/code/config.py`)

**Dependencies**: None

```python
RANDOM_STATE = 42
REWARD_MODEL_NAME = "OpenAssistant/reward-model-deberta-v3-large-v2"
MAX_TOKENS = 512
BATCH_SIZE = 32
LENGTH_NORM_COEF = 0.1
DISAGREEMENT_THRESHOLD = 0.20
PARTIAL_THRESHOLD = 0.10
MIN_SAMPLE_COUNT = 500
FIGURES_DIR = "h-m2/figures"
```

### bai.py (`h-m2/code/bai.py`)

**Dependencies**: config.py, h-e1/code/{model,data,config}.py

```python
def train_proxy_detectors() -> dict[str, "AgencyProxyDetector"]: ...
    # for each h_e1.config.PROXY_TYPES: build_labels + AgencyProxyDetector().fit()

def compute_bai_scores(responses: list[str], detectors: dict) -> list[float]: ...
    # mean of 4 detector.predict_proba(text), then length normalization

def length_normalize(raw_bai: float, response: str) -> float: ...
    # raw_bai / (1 + LENGTH_NORM_COEF * log(word_count))
```

### reward.py (`h-m2/code/reward.py`)

**Dependencies**: config.py

```python
def load_reward_model() -> tuple: ...  # (model, tokenizer), auto device_map
def compute_reward_scores(prompts: list[str], responses: list[str], model, tokenizer) -> list[float]: ...
    # batched inference, truncation=True, max_length=MAX_TOKENS
```

### analysis.py (`h-m2/code/analysis.py`)

**Dependencies**: config.py

```python
def compute_disagreement_rate(bai_scores: "np.ndarray", reward_scores: "np.ndarray") -> dict: ...
    # StandardScaler + Q25/Q75 quadrant counts, returns disagreement_rate + counts

def compute_correlations(bai_scores, reward_scores) -> dict: ...
    # pearsonr, spearmanr

def verify_mechanism(results: dict) -> dict: ...
    # variance/range/sample-count checks -> verification_passed bool
```

### evaluate.py (`h-m2/code/evaluate.py`)

**Dependencies**: analysis.py, config.py

```python
def plot_gate_bar(disagreement_rate: float, out_path: str) -> None: ...       # mandatory gate figure
def plot_scatter_quadrants(bai_z, reward_z, q_bounds: dict, out_path: str) -> None: ...
def plot_density_heatmap(bai_z, reward_z, out_path: str) -> None: ...
def plot_distributions(bai_scores, reward_scores, out_path: str) -> None: ...
def top_disagreement_examples(responses, bai_z, reward_z, n: int = 10) -> dict: ...
```

### run.py (`h-m2/code/run.py`)

**Dependencies**: bai.py, reward.py, analysis.py, evaluate.py, config.py

```python
def main() -> str: ...
# load HH-RLHF+RewardBench responses -> train_proxy_detectors -> compute_bai_scores ->
# load_reward_model -> compute_reward_scores -> compute_disagreement_rate ->
# compute_correlations -> verify_mechanism -> generate figures -> save results.json -> return gate_result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | H-E1 module bridging | sys.path wiring + reuse data.py/model.py/config.py from h-e1 | 6 | 1+3+1+1 |
| B-2 | Dataset loading | Load HH-RLHF test split + RewardBench eval set, extract prompt-response pairs | 7 | 2+2+2+1 |
| B-3 | Proxy detector retraining | Fit 4 AgencyProxyDetector instances (inline, no saved artifacts) | 6 | 2+2+2+0 |
| B-4 | BAI score computation | Aggregate 4 proxy scores, apply length normalization | 5 | 1+1+2+1 |
| B-5 | Reward model loading | Load OpenAssistant DeBERTa-v3, tokenizer, device auto-detect | 6 | 2+2+1+1 |
| B-6 | Reward score computation | Batched inference (batch_size=32), truncation handling | 7 | 2+2+2+1 |
| B-7 | Quartile disagreement analysis | Standardize scores, compute Q25/Q75 quadrants, disagreement rate | 8 | 2+1+3+2 |
| B-8 | Correlation + mechanism verification | Pearson/Spearman + verify_mechanism checks | 5 | 1+2+2+0 |
| B-9 | Visualization suite | Gate bar chart, scatter+quadrants, heatmap, histograms, example table | 7 | 2+1+1+3 |
| B-10 | Integration + gate check | run.py orchestration, results.json, PASS/PARTIAL/FAIL gate reporting | 6 | 1+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [B-1, B-2, B-3, B-4, B-5, B-6, B-7, B-8, B-9, B-10]
