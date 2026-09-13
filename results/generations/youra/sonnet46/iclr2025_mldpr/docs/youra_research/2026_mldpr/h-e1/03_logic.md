# Logic: H-E1
# DTS-Weighted Documentation Completeness Scoring System (EXISTENCE PoC)

**Date:** 2026-03-15
**Hypothesis:** H-E1

Applied: rate-limited-api-collection-with-json-cache
Applied: binary-field-presence-scoring-pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation from scratch

---

## A-2: HF Collector [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# collect_hf.py
import time
import json
import os
from pathlib import Path
from typing import Optional
import pandas as pd
from huggingface_hub import HfApi, DatasetInfo

SEED = 42
HF_RATE_LIMIT_SEC = 1.0   # unauthenticated
HF_RATE_LIMIT_AUTH = 0.2  # authenticated (5 req/sec)


def collect_hf_datasets(
    n_samples: int = 500,
    cache_dir: str = "data/raw_cache",
    hf_token: Optional[str] = None,
    pilot: bool = False,
) -> pd.DataFrame:
    """Collect HF Hub metadata; stratified sample n_samples datasets.
    Returns DataFrame with columns: dataset_id, repository, task_category,
    upload_year, [18 binary DTS field columns], in_human_subsample.
    """
    ...


def load_or_fetch_hf(
    dataset_id: str,
    cache_dir: str,
    api: HfApi,
    rate_limit_sec: float = HF_RATE_LIMIT_SEC,
    max_retries: int = 3,
) -> dict:
    """Load from JSON cache if exists, else fetch from HF API with retry/backoff.
    Cache path: {cache_dir}/hf_{dataset_id.replace('/', '__')}.json
    Returns raw metadata dict (serialized DatasetInfo fields).
    """
    ...


def stratified_sample_hf(
    dataset_list: list,
    n: int,
    seed: int = SEED,
) -> list:
    """Stratify dataset_list by (task_category_bin x upload_year_bin).
    8 bins: 4 task categories x 2 year groups (pre-2021, 2021+).
    Samples proportionally; fills remainder from largest bins.
    Returns list of DatasetInfo objects (length <= n).
    """
    ...
```

### Pseudo-code: `stratified_sample_hf`

```
1. For each dataset_info in dataset_list:
   a. task_bin = classify_task(dataset_info.tags)  # NLP/CV/tabular/audio/multimodal -> 4 buckets
   b. year_bin = "pre2021" if year < 2021 else "post2021"
   c. key = (task_bin, year_bin)
2. Group datasets by key -> bins: dict[tuple, list]
3. Compute proportional quota per bin: quota[k] = int(n * len(bins[k]) / total)
4. Adjust quotas to sum to n (add remainder to largest bins)
5. For each bin: rng.sample(bin, quota[bin])
6. Return flattened list
```

### Pseudo-code: `load_or_fetch_hf` (retry/backoff)

```
1. cache_path = cache_dir / f"hf_{dataset_id.replace('/', '__')}.json"
2. If cache_path.exists(): return json.load(cache_path)
3. For attempt in range(max_retries):
   a. Try: info = api.dataset_info(dataset_id); break
   b. Except HfHubHTTPError(429): sleep(2^attempt * rate_limit_sec); continue
   c. Except Exception: record failure; return {}
4. raw = serialize_dataset_info(info)  # card_data fields -> dict
5. json.dump(raw, cache_path); return raw
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | stratified_sample_hf | 8-bin (task x year) stratification with proportional quota fill |
| L-2-2 | load_or_fetch_hf | JSON cache read-through with exponential backoff on 429 |

---

## A-3: OpenML + UCI Collectors [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# collect_openml.py
import openml
import pandas as pd
import json
from pathlib import Path

def collect_openml_datasets(
    n_samples: int = 200,
    cache_dir: str = "data/raw_cache",
    pilot: bool = False,
) -> pd.DataFrame:
    """Bulk-list OpenML datasets; stratified sample by task_type.
    Returns DataFrame with DTS binary field columns.
    """
    ...


def load_or_fetch_openml(
    dataset_id: int,
    cache_dir: str,
) -> dict:
    """Load from JSON cache if exists, else fetch via openml.datasets.get_dataset().
    Cache path: {cache_dir}/openml_{dataset_id}.json
    Returns raw metadata dict.
    """
    ...


def stratified_sample_openml(
    df: pd.DataFrame,
    n: int,
    seed: int = 42,
) -> pd.DataFrame:
    """Stratify by task_type column (tabular/classification/regression/clustering).
    Returns sampled DataFrame of length <= n.
    """
    ...
```

```python
# collect_uci.py
import time
import json
import requests
from pathlib import Path
from typing import Optional
import pandas as pd
from ucimlrepo import fetch_ucirepo

UCI_RATE_LIMIT = 2.0  # seconds between requests


def collect_uci_datasets(
    cache_dir: str = "data/raw_cache",
    pilot: bool = False,
) -> pd.DataFrame:
    """Fetch all UCI datasets (full population ~100); rate-limited.
    Returns DataFrame with DTS binary field columns.
    """
    ...


def load_or_fetch_uci(
    dataset_id: int,
    cache_dir: str,
    rate_limit_sec: float = UCI_RATE_LIMIT,
) -> dict:
    """Load from JSON cache if exists, else try ucimlrepo then REST fallback.
    Cache path: {cache_dir}/uci_{dataset_id}.json
    Returns raw metadata dict.
    """
    ...


def fetch_uci_rest_fallback(
    dataset_id: int,
    base_url: str = "https://archive.ics.uci.edu/static/public",
    timeout: int = 10,
) -> dict:
    """GET {base_url}/{dataset_id}/ and parse JSON response.
    Returns empty dict on failure (non-200 or timeout).
    """
    ...
```

### Pseudo-code: `load_or_fetch_uci`

```
1. cache_path = cache_dir / f"uci_{dataset_id}.json"
2. If cache_path.exists(): return json.load(cache_path)
3. time.sleep(rate_limit_sec)
4. Try: result = fetch_ucirepo(id=dataset_id); raw = result.metadata.__dict__
5. Except Exception:
   a. raw = fetch_uci_rest_fallback(dataset_id)
6. json.dump(raw, cache_path); return raw
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | collect_openml_datasets | Bulk list + stratified sample by task_type |
| L-3-2 | fetch_uci_rest_fallback | REST GET fallback when ucimlrepo index missing |

---

## A-4: DTS Scorer [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
# scorer.py
import numpy as np
import pandas as pd
from typing import Optional

DTS_SECTIONS: dict[str, list[str]] = {
    "motivation":    ["task_categories", "language", "tags", "license"],
    "composition":   ["size_categories", "num_rows", "num_columns", "features"],
    "collection":    ["source_datasets", "annotations_creators", "original_data_url"],
    "preprocessing": ["preprocessing_steps", "data_augmentation", "data_splits"],
    "uses":          ["known_limitations", "out_of_scope_use", "discussion_best_use"],
    "distribution":  ["license", "citation", "contact", "maintenance_plan"],
}

DTS_WEIGHTS: dict[str, float] = {
    "motivation": 1.0, "composition": 0.9, "collection": 2.1,
    "preprocessing": 1.8, "uses": 1.5, "distribution": 0.7,
}

_WEIGHT_SUM = sum(DTS_WEIGHTS.values())  # 8.0


def compute_dts_score(metadata: dict) -> tuple[float, dict[str, float]]:
    """Compute weighted DTS score from metadata field presence.
    Returns (weighted_score in [0,1], {section: coverage_rate}).
    """
    ...


def compute_unweighted_score(metadata: dict) -> float:
    """Naive coverage: present_fields / total_fields across all sections.
    Returns scalar in [0, 1].
    """
    ...


def score_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """Apply compute_dts_score and compute_unweighted_score to each row.
    Adds columns: weighted_dts_score, unweighted_dts_score, per_section_{name}.
    Returns augmented DataFrame.
    """
    ...


def compute_coverage_rate(
    df: pd.DataFrame,
    repo: Optional[str] = None,
) -> float:
    """Fraction of datasets with weighted_dts_score > 0.
    If repo is not None, filter to df[df.repository == repo] first.
    """
    ...
```

### Pseudo-code: `compute_dts_score`

```
1. section_coverages = {}
2. For section, fields in DTS_SECTIONS.items():
   a. present = sum(1 for f in fields if metadata.get(f) not in [None, "", [], {}])
   b. section_coverages[section] = present / len(fields)
3. weighted_score = sum(DTS_WEIGHTS[s] * section_coverages[s] for s in DTS_SECTIONS) / _WEIGHT_SUM
4. return (weighted_score, section_coverages)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_dts_score core | Binary field presence -> per-section coverage -> weighted sum normalization |
