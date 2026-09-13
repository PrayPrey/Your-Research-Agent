# Logic: H-M2

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-E2: data_loader.py [Complexity: 12, Budget: 12]

**Applied**: Standard HF `datasets` load + requests fallback with rate limiting (no exact KB match; stdlib/requests pattern used)

### API Signatures

```python
import time
import requests
from datasets import load_dataset

def load_pwc_datasets(dataset_id: str = "pwc-archive/datasets") -> list[dict]:
    """Load PWC datasets.json via HF datasets lib. Returns list of raw records."""
    ds = load_dataset(dataset_id, split="train")
    return [dict(row) for row in ds]

def fetch_semantic_scholar_date(paper_title: str, session: requests.Session | None = None) -> str | None:
    """Query Semantic Scholar for paper pubDate by title. Returns 'YYYY-MM-DD' or None."""
    ...

class RateLimiter:
    def __init__(self, max_per_min: int = 100): ...
    def wait(self) -> None:
        """Blocks until next request slot available."""
        ...
```

### Data Structures

| Field | Type | Note |
|-------|------|------|
| raw record | dict | keys: name, description, tasks (list[str]), introducing_paper (dict\|None) |
| introducing_paper | dict | keys: title, date (str\|None), url |

### Pseudo-code (rate-limited fallback lookup)

```
1. limiter = RateLimiter(100)
2. for record in raw_datasets:
3.     if record.introducing_paper.date is None and record.introducing_paper.title:
4.         limiter.wait()
5.         date = fetch_semantic_scholar_date(title)  # GET api.semanticscholar.org/graph/v1/paper/search
6.         record.introducing_paper.date = date  # None on failure/timeout, caught via try/except
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | load_pwc_datasets | HF datasets.load_dataset wrapper, convert to list[dict] |
| L-E2-2 | fetch_semantic_scholar_date | requests.get to SS API, parse JSON, extract date |
| L-E2-3 | RateLimiter | sliding-window token limiter, 100 req/min |
| L-E2-4 | Error handling | try/except around network calls, return None on failure |

---

## A-E4: date_extractor.py [Complexity: 10, Budget: 10]

**Applied**: Standard stdlib date parsing (no KB match; regex/datetime pattern)

### API Signatures

```python
from datetime import datetime

def extract_benchmark_date(benchmark_metadata: dict) -> int | None:
    """Extract creation year from PWC benchmark metadata. Returns year or None."""
    ...

def parse_paper_date(paper: dict) -> int | None:
    """Parse 'date' field (various formats) -> year int, or None if unparseable."""
    ...

def resolve_missing_dates(benchmarks: list[dict]) -> list[dict]:
    """For records with date=None, calls fetch_semantic_scholar_date fallback. Mutates+returns list."""
    ...
```

### Data Structures

| Field | Type | Note |
|-------|------|------|
| benchmark_metadata | dict | raw PWC record (see A-E2) |
| year | int \| None | extracted 4-digit year |

### Pseudo-code (date parsing + fallback resolution)

```
parse_paper_date(paper):
1. raw = paper.get("date")
2. if raw is None: return None
3. try: return datetime.strptime(raw, "%Y-%m-%d").year
4. except ValueError: try regex r"(19|20)\d{2}" on raw, return int(match) if found else None

resolve_missing_dates(benchmarks):
1. for b in benchmarks:
2.     if b["year"] is None and b["introducing_paper"].get("title"):
3.         ss_date = fetch_semantic_scholar_date(title)  # from data_loader
4.         b["year"] = parse_paper_date({"date": ss_date}) if ss_date else None
5. return benchmarks
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | extract_benchmark_date | Pull date field from metadata, delegate to parse_paper_date |
| L-E4-2 | parse_paper_date | ISO date parse + regex fallback for year extraction |
| L-E4-3 | resolve_missing_dates | Loop + SS API fallback, skip if no title available |

*(1 pt reserved for error-handling glue, no separate subtask needed)*

---

## A-E5: analysis.py [Complexity: 11, Budget: 11]

**Applied**: Standard ratio/threshold gate computation (no KB match; basic stats pattern)

### API Signatures

```python
def build_benchmark_records(raw_datasets: list[dict]) -> list[dict]:
    """Merge classification + date extraction into unified records."""
    ...

def compute_post2020_ratio(benchmarks: list[dict]) -> dict:
    """Ratio of emergent-capability benchmarks with year>=2020. Returns metrics dict."""
    ...

def compute_creation_rate_acceleration(benchmarks: list[dict]) -> dict:
    """Compare emergent-benchmark creation rate pre/post 2020."""
    ...

def evaluate_hypothesis(results: dict) -> dict:
    """Apply gate threshold (0.80) to post_2020_ratio. Returns {pass: bool, ...results}."""
    ...
```

### Data Structures

| Field | Type | Note |
|-------|------|------|
| record | dict | {name, description, tasks, category ("emergent-capability"\|"traditional"), year} |
| ratio_result | dict | {post_2020_ratio: float, emergent_count: int, post_2020_count: int} |
| accel_result | dict | {pre_2020_rate: float, post_2020_rate: float, acceleration_ratio: float} |

### Pseudo-code (record build + ratio + gate)

```
build_benchmark_records(raw_datasets):
1. for raw in raw_datasets:
2.     category = classify_benchmark(raw.name, raw.description, raw.tasks)
3.     year = extract_benchmark_date(raw)
4.     records.append({name, description, tasks, category, year})
5. return records

compute_post2020_ratio(benchmarks):
1. emergent = [b for b in benchmarks if b.category == "emergent-capability" and b.year is not None]
2. post2020 = [b for b in emergent if b.year >= 2020]
3. ratio = len(post2020) / len(emergent) if emergent else 0.0
4. return {post_2020_ratio: ratio, emergent_count: len(emergent), post_2020_count: len(post2020)}

compute_creation_rate_acceleration(benchmarks):
1. emergent = filter category == "emergent-capability", year not None
2. pre = [b for b in emergent if b.year < 2020]; post = [b for b in emergent if b.year >= 2020]
3. pre_rate = len(pre) / 20   # years 2000-2019 window (approx, config-tunable if needed)
4. post_rate = len(post) / 6  # years 2020-2025 window
5. return {pre_2020_rate: pre_rate, post_2020_rate: post_rate, acceleration_ratio: post_rate / pre_rate if pre_rate else float("inf")}

evaluate_hypothesis(results):
1. passed = results["post_2020_ratio"] > POST_2020_THRESHOLD  # 0.80, from config.py
2. return {**results, gate_pass: passed}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | build_benchmark_records | Merge classifier + date_extractor outputs per raw record |
| L-E5-2 | compute_post2020_ratio | Filter emergent+dated, compute ratio |
| L-E5-3 | compute_creation_rate_acceleration | Pre/post 2020 rate comparison |
| L-E5-4 | evaluate_hypothesis | Threshold gate check against config.POST_2020_THRESHOLD |

---

## External Dependencies

None — green-field, no base hypothesis code reuse.
