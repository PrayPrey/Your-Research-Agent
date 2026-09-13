# Logic: H-M3 (Researcher Attention Shift)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

Applied: standard-http-client-retry-backoff pattern (no directly relevant KB match; using stdlib/requests conventions).

---

## A-2: PWC API Client [Complexity: 12, Budget: 12]

**Applied**: paginated-REST-client-with-retry pattern (standard `requests` + tenacity-style backoff; no KB example found)

### API Signatures

```python
from dataclasses import dataclass
from typing import Literal, Optional
import time
import logging

logger = logging.getLogger(__name__)

class PWCAPIError(Exception):
    """Raised when PWC API is unavailable after retries."""

def _pwc_get_paginated(
    endpoint: str,
    params: Optional[dict] = None,
    max_pages: int = 50,
    page_size: int = 100,
    timeout: float = 10.0,
) -> list[dict]:
    """GET all pages from PWC REST endpoint. Returns concatenated 'results' list."""
    ...

def _rate_limited_request(url: str, params: dict, min_interval_s: float = 0.5) -> dict:
    """Single request with rate-limit sleep + HTTP error handling."""
    ...

def fetch_from_pwc_api(
    benchmarks: list[str],
    time_range: tuple[str, str] = ("2018-01", "2024-12"),
    retries: int = 3,
    backoff_base: float = 2.0,
) -> list[PaperCountRecord]:
    """
    Fetch monthly paper counts per benchmark from paperswithcode.com API.
    Raises PWCAPIError after exhausting retries (caller falls back to HF).
    """
    ...
```

### Pseudo-code

```
for benchmark in benchmarks:
    for attempt in range(retries):
        try:
            sota_data = _pwc_get_paginated(f"/sota/{benchmark}/")
            # sota_data: list of {evaluation_date, paper: {id, ...}}
            monthly_counts = group_by_year_month(sota_data)  # dict[str, int]
            for ym, count in monthly_counts.items():
                records.append(PaperCountRecord(benchmark, category=None, year_month=ym, paper_count=count))
            break
        except (HTTPError, Timeout) as e:
            if attempt == retries - 1:
                raise PWCAPIError(f"{benchmark}: {e}") from e
            time.sleep(backoff_base ** attempt)
return records
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Paginated GET + rate limiting | `_pwc_get_paginated`, `_rate_limited_request` |
| L-A2-2 | Per-benchmark retry/backoff loop | `fetch_from_pwc_api` main loop, exponential backoff |
| L-A2-3 | Monthly aggregation from SOTA results | group evaluation dates -> `year_month` counts |

---

## A-3: HuggingFace Fallback [Complexity: 10, Budget: 10]

**Applied**: dataset-load-and-filter pattern (standard `datasets.load_dataset` usage)

### API Signatures

```python
from datasets import load_dataset

def _load_pwc_archive(split: str = "train") -> "datasets.Dataset":
    """Load pwc-archive/datasets from HuggingFace Hub."""
    ...

def _filter_and_aggregate(
    ds: "datasets.Dataset",
    benchmarks: list[str],
    time_range: tuple[str, str],
) -> list[PaperCountRecord]:
    """Filter dataset rows to target benchmarks/time range, aggregate paper_count by (benchmark, year_month)."""
    ...

def fetch_from_huggingface_fallback(
    benchmarks: list[str],
    time_range: tuple[str, str] = ("2018-01", "2024-12"),
) -> list[PaperCountRecord]:
    """Fallback data source when PWC API fails. Raises RuntimeError if dataset load fails."""
    ...
```

### Pseudo-code

```
ds = _load_pwc_archive()
records = []
for row in ds:
    if row["benchmark"] not in benchmarks:
        continue
    ym = row["date"][:7]  # "YYYY-MM"
    if not (time_range[0] <= ym <= time_range[1]):
        continue
    records.append(PaperCountRecord(row["benchmark"], category=None, ym, row["paper_count"]))
return aggregate_duplicates(records)  # sum paper_count on (benchmark, year_month) collisions
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Dataset load | `_load_pwc_archive` with HF `load_dataset`, error wrap |
| L-A3-2 | Filter + time-range clip | `_filter_and_aggregate` benchmark/date filtering |
| L-A3-3 | Duplicate aggregation | sum `paper_count` on (benchmark, year_month) collisions |

---

## Orchestration: collect_paper_counts (not separately budgeted — glue code)

```python
import pandas as pd

def collect_paper_counts(retries: int = 3) -> pd.DataFrame:
    """Try PWC API first, fall back to HF dataset on failure. Returns flat DataFrame of PaperCountRecord fields."""
    benchmarks = EMERGENT_BENCHMARKS + TRADITIONAL_BENCHMARKS
    try:
        records = fetch_from_pwc_api(benchmarks, retries=retries)
    except PWCAPIError as e:
        logger.warning(f"PWC API failed ({e}), falling back to HuggingFace")
        records = fetch_from_huggingface_fallback(benchmarks)
    return pd.DataFrame([r.__dict__ for r in records])
```

### Tensor/Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| records | `list[PaperCountRecord]` | one row per (benchmark, year_month) |
| DataFrame | `[N_rows, 4]` cols: benchmark, category, year_month, paper_count | category filled later by `label_dataframe` |
