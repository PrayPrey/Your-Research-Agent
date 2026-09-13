# Architecture: H-E1 (EXISTENCE)

Applied: RewardBench unified RM inference pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure (Minimal - EXISTENCE)

```
h-e1/code/
├── config.py
├── data.py
├── rm_scoring.py
├── mode_classify.py
├── stats_test.py
├── run.py
└── outputs/
    ├── rm_scores.parquet
    ├── mode_distribution.json
    └── statistical_results.json
```

---

## Modules

### config.py

**Dependencies**: none

```python
DATASET_ID = "lmsys/chatbot_arena_conversations"
RM_MODELS = {
    "openassistant": "OpenAssistant/reward-model-deberta-v3-large-v2",
    "pairrm": "llm-blender/PairRM",
    "armorm": "RLHFlow/ArmoRM-Llama3-8B-v0.1",
}
BATCH_SIZE = 8
OUTPUT_DIR = "outputs/"
USE_ARMORM = True  # set False for 2-model fallback (FR-6)
```

### data.py

**Dependencies**: config.py

```python
def load_battles(dataset_id: str) -> "pd.DataFrame": ...
def filter_valid(df: "pd.DataFrame") -> "pd.DataFrame": ...
def extract_prompt_response(row: dict) -> tuple[str, str, str]: ...  # prompt, resp_a, resp_b
```

### rm_scoring.py

**Dependencies**: config.py, data.py

```python
class RewardModel:
    def __init__(self, model_id: str, model_type: str): ...
    def score(self, prompt: str, response: str) -> float: ...

def zscore_sigmoid(scores: "np.ndarray") -> "np.ndarray": ...
def score_all_battles(df: "pd.DataFrame", models: dict[str, RewardModel]) -> "pd.DataFrame": ...
def compute_rm_variance(row: dict, model_names: list[str]) -> float: ...
def cache_scores(df: "pd.DataFrame", path: str) -> None: ...
def load_cached_scores(path: str) -> "pd.DataFrame | None": ...
```

### mode_classify.py

**Dependencies**: none (pure pandas/numpy)

```python
def compute_pair_entropy(df: "pd.DataFrame") -> "pd.DataFrame": ...  # adds human_entropy col
def compute_cluster_entropy_fallback(df: "pd.DataFrame") -> "pd.DataFrame": ...  # FR-7
def assign_modes(df: "pd.DataFrame") -> "pd.DataFrame": ...  # median split -> mode 1-4
def mode_distribution(df: "pd.DataFrame") -> dict: ...
```

### stats_test.py

**Dependencies**: scipy

```python
def binomial_test_mode3(count: int, total: int, p0: float = 0.10) -> dict: ...
    # returns {proportion, ci_95_lower, ci_95_upper, p_value, result}
def sensitivity_analysis(count: int, total: int, thresholds: list[float]) -> dict: ...
```

### run.py

**Dependencies**: all modules above

```python
def main() -> None: ...
    # load -> filter -> score (cache-aware) -> classify -> test -> serialize outputs
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load Arena dataset, filter valid battles, extract prompt/response pairs | 8 | 2+2+2+2 |
| A-2 | RM wrapper + scoring loop | Implement RewardModel class for 3 model types, batch scoring with resume cache | 14 | 4+3+4+3 |
| A-3 | Score normalization | Z-score + sigmoid normalization, RM variance computation | 6 | 1+1+3+1 |
| A-4 | Human entropy calculation | Model-pair aggregation, entropy formula, prompt-cluster fallback | 7 | 2+1+3+1 |
| A-5 | Mode classification | Median split on both axes, assign 4 modes, distribution output | 5 | 1+1+2+1 |
| A-6 | Statistical testing | One-sided binomial test, 95% CI, sensitivity analysis | 6 | 1+1+3+1 |
| A-7 | Pipeline integration + outputs | Wire run.py end-to-end, serialize JSON/parquet artifacts | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-7]
