# Config: H-E1
# Behavioral Proxy Signal Detection

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-31

Applied: Dataclass configuration pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** dataclass + YAML

---

## C-E4-1: LMSYS Loading Config [Complexity: E4, Budget: E4]

**Applied**: Standard dataset loading pattern

```python
from dataclasses import dataclass

@dataclass
class LMSYSConfig:
    dataset_id: str = "lmsys/chatbot_arena_conversations"
    date_start: str = "2023-01"
    date_end: str = "2024-12"
    min_votes_per_bin: int = 100
    top_n_models: int = 5
    cache_dir: str = None
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-1 | LMSYS Loading Config | Dataset ID, date range, vote threshold, model count |

---

## C-E4-2: Shannon Entropy Config [Complexity: E4, Budget: E4]

**Applied**: Standard statistical analysis pattern

```python
@dataclass
class EntropyConfig:
    entropy_base: int = 2          # bits
    min_categories: int = 3        # win/lose/tie
    handle_zero_counts: str = "laplace"
    laplace_alpha: float = 1e-6    # Non-standard: near-zero to avoid log(0) without bias
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-2 | Entropy Config | Base, category floor, zero-count handling |

---

## C-E4-3: Model Selection Config [Complexity: E4, Budget: E4]

**Applied**: Standard filtering pattern

```python
@dataclass
class ModelSelectionConfig:
    top_n_models: int = 5
    selection_criterion: str = "total_votes"  # total_votes | distinct_bins
    min_bins_per_model: int = 6
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-3 | Model Selection Config | Top-N, criterion, bin threshold |

---

## C-E3-1: Proxy Computation Config [Complexity: E3, Budget: E3]

**Applied**: Standard statistical threshold pattern

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ProxyConfig:
    # WildChat cohort
    min_monthly_appearances: int = 3
    date_start: str = "2023-01"
    date_end: str = "2024-12"
    token_count_method: str = "approx"  # approx | tiktoken
    correction_markers: List[str] = field(default_factory=lambda: [
        "actually", "that's wrong", "no, I meant",
        "please redo", "that is incorrect", "you're wrong"
    ])
    # Statistical test
    significance_threshold: float = 0.05
    effect_size_threshold: float = 0.2
    min_proxies_passing: int = 2   # gate condition for H-E1 success
    seed: int = 42
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-E3-1 | Proxy Computation Config | Cohort filters, token method, markers, test thresholds |

---

## Master Config YAML

Save as `h-e1/config.yaml`:

```yaml
wildchat:
  dataset_id: "allenai/WildChat-1M"
  date_start: "2023-01"
  date_end: "2024-12"
  min_monthly_appearances: 3
  token_count_method: "approx"

lmsys:
  dataset_id: "lmsys/chatbot_arena_conversations"
  date_start: "2023-01"
  date_end: "2024-12"
  min_votes_per_bin: 100
  top_n_models: 5

proxy:
  correction_markers:
    - "actually"
    - "that's wrong"
    - "no, I meant"
    - "please redo"
    - "that is incorrect"
    - "you're wrong"

statistical:
  significance_threshold: 0.05
  effect_size_threshold: 0.2
  min_proxies_passing: 2
  entropy_base: 2
  seed: 42

output:
  figures_dir: "h-e1/figures"
  results_dir: "h-e1/results"
  results_file: "h-e1/results/results.json"
  cache_dir: null
```

Load with:
```python
import yaml
with open("h-e1/config.yaml") as f:
    cfg = yaml.safe_load(f)
```
