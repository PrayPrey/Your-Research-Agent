# Logic: H-E1 (EXISTENCE / PoC)

**Hypothesis:** Collaboration score extracts agency signals orthogonal to preference labels (correlation < 0.7)
**Type:** EXISTENCE - statistical analysis, no training/tensors

Applied: No relevant KB pattern found (searched "statistical correlation analysis Python pattern"); standard scipy/numpy/matplotlib pipeline used.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Setup config & project structure [Complexity: 3, Budget: 0]

**Applied**: Standard Python config module

```python
# config.py
SEED: int = 42
SAMPLE_SIZE: int = 1000
DATASET_NAME: str = "Anthropic/hh-rlhf"
DATASET_SUBSET: str = "helpful-base"
FIGURES_DIR: str = "figures/"
RESULTS_PATH: str = "results.json"
CORRELATION_THRESHOLD: float = 0.7
```

### Subtasks [0/0 used]
None - single flat config, no breakdown needed.

---

## A-2: Data loading module [Complexity: 6, Budget: 0]

**Applied**: HuggingFace `datasets` load + shuffle + select pattern

```python
# data.py
from datasets import Dataset

def load_hh_rlhf_sample(seed: int, n: int) -> Dataset:
    """Load Anthropic/hh-rlhf helpful-base, shuffle(seed), select(n). Returns Dataset with 'chosen'/'rejected' str cols."""
    ...

def extract_assistant_response(conversation: str) -> str:
    """Extract final 'Assistant:' turn text from raw HH-RLHF conversation string."""
    ...
```

### Pseudo-code

```
extract_assistant_response(conversation):
    turns = conversation.split("\n\nAssistant:")
    last = turns[-1]
    last = last.split("\n\nHuman:")[0]  # strip trailing human turn if present
    return last.strip()
```

### Subtasks [0/0 used]
None.

---

## A-3: Implement collab_score_v2 [Complexity: 7, Budget: 0]

**Applied**: Regex signal counting + sqrt length normalization

```python
# collab_score.py
def compute_collab_score_v2(response: str) -> float:
    """Sum of 4 regex signal category counts, normalized by sqrt(word_count). Returns float >= 0."""
    ...
```

### Pseudo-code

```
compute_collab_score_v2(response):
    word_count = len(response.split())
    if word_count == 0: return 0.0

    reasoning = count_matches(response, r"\b(because|since|therefore)\b")
    uncertainty = count_matches(response, r"\b(i think|might|could)\b")
    engagement = count_matches(response, r"\b(you could|consider)\b|\?")
    depth = count_matches(response, r"\b(first|second|step \d+)\b|^\s*\d+\.")

    raw_score = reasoning + uncertainty + engagement + depth
    return raw_score / sqrt(word_count)
```

Note: regex matching case-insensitive (`re.IGNORECASE`).

### Subtasks [0/0 used]
None.

---

## A-4: Correlation analysis module [Complexity: 6, Budget: 0]

**Applied**: `scipy.stats.pearsonr` standard pattern

```python
# analysis.py
from typing import TypedDict

class CorrelationResult(TypedDict):
    correlation: float
    p_value: float
    chosen_mean: float
    chosen_std: float
    rejected_mean: float
    rejected_std: float
    gate_passed: bool

def compute_correlation(dataset, n_samples: int) -> CorrelationResult:
    """Compute collab_score for chosen/rejected, pearsonr(scores, labels), gate_passed = abs(r) < 0.7."""
    ...
```

### Pseudo-code

```
compute_correlation(dataset, n_samples):
    scores, labels = [], []
    for row in dataset[:n_samples]:
        chosen_resp = extract_assistant_response(row["chosen"])
        rejected_resp = extract_assistant_response(row["rejected"])
        scores += [compute_collab_score_v2(chosen_resp), compute_collab_score_v2(rejected_resp)]
        labels += [1, 0]

    r, p = pearsonr(scores, labels)
    chosen_scores = scores[0::2]
    rejected_scores = scores[1::2]
    return {
        "correlation": r, "p_value": p,
        "chosen_mean": mean(chosen_scores), "chosen_std": std(chosen_scores),
        "rejected_mean": mean(rejected_scores), "rejected_std": std(rejected_scores),
        "gate_passed": abs(r) < config.CORRELATION_THRESHOLD,
    }
```

### Subtasks [0/0 used]
None.

---

## A-5: Visualization suite [Complexity: 6, Budget: 0]

**Applied**: Standard matplotlib bar/hist/scatter/box patterns

```python
# visualize.py
def plot_gate_bar_chart(correlation: float, threshold: float, out_path: str) -> None:
    """Bar of abs(correlation) vs threshold line. Saves PNG to out_path."""
    ...

def plot_score_histogram(chosen: list[float], rejected: list[float], out_path: str) -> None:
    """Overlaid histograms of chosen vs rejected scores. Saves PNG."""
    ...

def plot_scatter_regression(scores: list[float], labels: list[int], out_path: str) -> None:
    """Scatter scores vs labels + np.polyfit degree-1 regression line. Saves PNG."""
    ...

def plot_boxplot(chosen: list[float], rejected: list[float], out_path: str) -> None:
    """Side-by-side boxplot chosen vs rejected. Saves PNG."""
    ...
```

### Subtasks [0/0 used]
None.

---

## A-6: Run experiment end-to-end [Complexity: 5, Budget: 0]

**Applied**: Standard main() orchestration script

```python
# run_experiment.py
def main() -> None:
    """Load data -> compute_correlation -> save 4 figures + results.json."""
    ...
```

### Pseudo-code

```
main():
    dataset = load_hh_rlhf_sample(config.SEED, config.SAMPLE_SIZE)
    result = compute_correlation(dataset, config.SAMPLE_SIZE)

    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    plot_gate_bar_chart(result["correlation"], config.CORRELATION_THRESHOLD, f"{FIGURES_DIR}/gate_bar.png")
    plot_score_histogram(chosen_scores, rejected_scores, f"{FIGURES_DIR}/hist.png")
    plot_scatter_regression(scores, labels, f"{FIGURES_DIR}/scatter.png")
    plot_boxplot(chosen_scores, rejected_scores, f"{FIGURES_DIR}/box.png")

    json.dump(result, open(config.RESULTS_PATH, "w"), indent=2)
```

### Subtasks [0/0 used]
None.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Subtask count within budget (0/0)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included (green-field)
