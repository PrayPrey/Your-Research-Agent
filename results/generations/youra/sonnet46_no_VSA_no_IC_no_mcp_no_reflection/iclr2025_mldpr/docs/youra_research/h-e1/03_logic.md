---
title: "Logic: H-E1 — Data Acquisition Pipeline Feasibility"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-31"
---

Applied: coverage-audit-script pattern
Applied: data-pipeline-sequential-orchestrator pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

# Logic: H-E1

## L-E1-3-1: HFCoverageChecker.check_all() [Complexity: 6, Budget: 2]

### API Signatures

```python
import time
import logging
from huggingface_hub import DatasetCard
from huggingface_hub.utils import RepositoryNotFoundError, EntryNotFoundError, HfHubHTTPError

class HFCoverageChecker:
    def __init__(self, fields: list[str], token: str | None = None):
        """fields: list of card fields to score; token: optional HF auth token."""
        self.fields = fields  # e.g. HF_FIELDS from config
        self.token = token

    def check_all(self, dataset_names: list[str]) -> dict[str, float | None]:
        """Query HF Hub for each dataset. Returns {name: score} where score=None if not found."""
        scores: dict[str, float | None] = {}
        for name in dataset_names:
            scores[name] = self._query_one(name)
            time.sleep(HF_RATE_LIMIT_SEC)  # rate limit between calls
        return scores

    def _query_one(self, name: str) -> float | None:
        """Single dataset query. Returns field-presence score or None."""
        ...
```

### Algorithm: `check_all` / `_query_one`

```
for name in dataset_names:
    try:
        card = DatasetCard.load(name, token=self.token)
        card_data = card.data.to_dict()
        n_present = sum(1 for f in self.fields if card_data.get(f) not in (None, "", []))
        score = n_present / len(self.fields)
        log: "HF card found: {name}, score={score:.2f}"
        scores[name] = score
    except (RepositoryNotFoundError, EntryNotFoundError):
        log: "HF card not found: {name}"
        scores[name] = None
    except HfHubHTTPError as e:
        if e.response.status_code == 403:
            # retry once with token from env HF_TOKEN if self.token is None
            if self.token is None and os.getenv("HF_TOKEN"):
                self.token = os.getenv("HF_TOKEN")
                return self._query_one(name)  # one retry
            log: "HF card 403 forbidden: {name}"
        else:
            log: "HF card HTTP error {e.response.status_code}: {name}"
        scores[name] = None
    except Exception as e:
        log: "HF card unexpected error: {name}: {e}"
        scores[name] = None
    time.sleep(HF_RATE_LIMIT_SEC)
return scores
```

### Error Handling

| Error | Action |
|-------|--------|
| `RepositoryNotFoundError` | score = None, log, continue |
| `EntryNotFoundError` | score = None, log, continue |
| `HfHubHTTPError` 403 | retry once with env `HF_TOKEN`; else None |
| `HfHubHTTPError` other | score = None, log status code, continue |
| Any other exception | score = None, log, continue — never crash |

### Input / Output

```python
# Input
dataset_names = ["mnist", "cifar10", "unknown-dataset-xyz"]

# Output
{
    "mnist":                  0.857,   # 6/7 fields present
    "cifar10":                0.571,   # 4/7 fields present
    "unknown-dataset-xyz":    None,    # not found
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-3-1a | `_query_one` | DatasetCard.load + field-presence scoring + error catch |
| L-E1-3-1b | Rate limiting | `time.sleep(HF_RATE_LIMIT_SEC)` between each call in loop |

---

## L-E1-3-2: HFCoverageChecker.aggregate() [Complexity: 6, Budget: 2]

### API Signatures

```python
def aggregate(self, scores: dict[str, float | None]) -> dict:
    """Compute coverage stats from check_all output."""
    ...
```

### Algorithm

```
n_queried = len(scores)
found = {k: v for k, v in scores.items() if v is not None}
n_found = len(found)
coverage_rate = n_found / n_queried if n_queried > 0 else 0.0
mean_field_score = sum(found.values()) / n_found if n_found > 0 else 0.0

# per_dataset: field-level dict for heatmap — caller must pass fields separately
# aggregate only reports scalar stats; per_dataset is the raw scores dict
return {
    "coverage_rate": coverage_rate,
    "mean_field_score": mean_field_score,
    "n_found": n_found,
    "n_queried": n_queried,
    "per_dataset": scores,   # {name: float|None} — used directly for heatmap
}
```

### Input / Output

```python
# Input
scores = {"mnist": 0.857, "cifar10": 0.571, "unknown-xyz": None}

# Output
{
    "coverage_rate":    0.667,    # 2/3
    "mean_field_score": 0.714,   # mean of [0.857, 0.571]
    "n_found":          2,
    "n_queried":        3,
    "per_dataset":      {"mnist": 0.857, "cifar10": 0.571, "unknown-xyz": None},
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-3-2a | Scalar metrics | coverage_rate, mean_field_score, n_found, n_queried |
| L-E1-3-2b | per_dataset passthrough | Pass raw scores dict for heatmap consumption |

---

## L-E1-4-1: OpenMLTemporalChecker.fetch_all() [Complexity: 5, Budget: 2]

### API Signatures

```python
import openml
import pandas as pd

class OpenMLTemporalChecker:
    def __init__(self): ...

    def fetch_all(self) -> pd.DataFrame:
        """Single bulk OpenML call. Returns cleaned df with 'name' and 'upload_date' columns."""
        ...
```

### Algorithm

```
df = openml.datasets.list_datasets(output_format='dataframe')
# Normalize name: lowercase + strip for later case-insensitive matching
df["name_norm"] = df["name"].str.lower().str.strip()
# Parse upload_date → datetime, coerce bad values to NaT
df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
# Drop rows with NaT upload_date (unusable for temporal filter)
df = df.dropna(subset=["upload_date"])
return df
```

### Input / Output

```python
# Input: none (bulk API call)

# Output: pd.DataFrame with columns including:
#   name         (str, original)
#   name_norm    (str, lowercased+stripped)
#   upload_date  (datetime64[ns], NaT rows dropped)
#   ... (other OpenML columns preserved)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-4-1a | Bulk fetch | `list_datasets(output_format='dataframe')` |
| L-E1-4-1b | Cleaning | `name_norm`, `upload_date` coerce+dropna |

---

## L-E1-4-2: OpenMLTemporalChecker.check_all() [Complexity: 5, Budget: 2]

### API Signatures

```python
def check_all(
    self,
    dataset_names: list[str],
    paper_years: dict[str, int],
    openml_df: pd.DataFrame,
) -> dict:
    """Client-side temporal filter per dataset. Returns filter success stats."""
    ...
```

### Algorithm

```
pre_pub_counts: dict[str, int] = {}
n_valid = 0

for name in dataset_names:
    name_norm = name.lower().strip()
    paper_year = paper_years.get(name)

    # Case-insensitive match in OpenML df
    matches = openml_df[openml_df["name_norm"] == name_norm]

    if matches.empty or paper_year is None:
        pre_pub_counts[name] = 0
        continue

    # Temporal filter: pre-publication rows only
    pre_pub = matches[matches["upload_date"].dt.year < paper_year]
    count = len(pre_pub)
    pre_pub_counts[name] = count

    if count >= 1:
        n_valid += 1

n_queried = len(dataset_names)
filter_success_rate = n_valid / n_queried if n_queried > 0 else 0.0

return {
    "filter_success_rate": filter_success_rate,
    "n_valid": n_valid,
    "n_queried": n_queried,
    "pre_pub_counts": pre_pub_counts,  # {name: int} — used for histogram
}
```

### Input / Output

```python
# Input
dataset_names = ["mnist", "cifar10", "unknown-xyz"]
paper_years   = {"mnist": 1998, "cifar10": 2009, "unknown-xyz": 2010}
openml_df     = fetch_all()  # cleaned df from L-E1-4-1

# Output
{
    "filter_success_rate": 0.667,   # 2/3 have ≥1 pre-pub entry
    "n_valid":    2,
    "n_queried":  3,
    "pre_pub_counts": {
        "mnist":        12,   # 12 OpenML rows uploaded before 1998
        "cifar10":       3,
        "unknown-xyz":   0,   # not found in OpenML
    },
}
```

### Error Handling

- `paper_year is None`: count = 0, not valid (no year to compare against)
- Dataset not in OpenML (`matches.empty`): count = 0, not valid
- NaT rows already dropped in `fetch_all`, so no NaT comparison risk

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-4-2a | Name match + temporal filter | pandas boolean mask per dataset |
| L-E1-4-2b | Aggregation | filter_success_rate, n_valid, pre_pub_counts |
