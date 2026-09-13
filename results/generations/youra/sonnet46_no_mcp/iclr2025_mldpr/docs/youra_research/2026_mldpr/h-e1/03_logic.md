# Logic Design: H-E1 — FAIR Score Variance Existence

**Hypothesis Type**: EXISTENCE (PoC)
**Generated**: 2026-05-04
**Budget**: 6 subtasks (A-3: 4, A-4: 2)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

Green-field project — no existing code. Serena analysis not applicable.

Applied: async-batch-retry pattern (from KB search)
Applied: statistical-analysis-api pattern (from KB search)

---

## Module: F-UJI Async Batch Scorer (`src/score_fuji.py`)

### API Signatures

```python
import asyncio
import json
import os
from typing import Optional

import aiohttp
import pandas as pd


async def score_one(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    did: int,
    landing_url: str,
    fuji_base: str,
    retry_max: int = 3,
    retry_base: float = 2.0,
) -> dict:
    """Score one dataset landing page via F-UJI API with retry.

    Returns: {did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
              sub_criteria: list[float], status: str}
    """
    ...


async def score_batch(
    cohort: pd.DataFrame,          # columns: did, landing_page_url
    fuji_base: str,
    concurrency: int = 10,
    retry_max: int = 3,
    retry_base: float = 2.0,
    cache_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Async batch score all cohort URLs, with optional disk cache.

    Returns DataFrame: did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
                       sub_criteria (list), status
    Saves intermediate checkpoint every 100 records if cache_dir provided.
    """
    ...


def _load_cache(cache_dir: str, did: int) -> Optional[dict]:
    """Load cached F-UJI response for did. Returns None if not cached."""
    ...


def _save_cache(cache_dir: str, did: int, result: dict) -> None:
    """Persist F-UJI response JSON to cache_dir/{did}.json."""
    ...


def _parse_fuji_response(did: int, response_json: dict) -> dict:
    """Extract aggregate FAIR score and per-dimension scores from F-UJI response.

    F-UJI response -> fair_aggregate = mean(17 sub-criteria scores in [0,1])
    Per-dimension: fair_F, fair_A, fair_I, fair_R = mean of respective sub-criteria
    Returns: {did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, sub_criteria, status}
    """
    ...


def fuji_fallback_proxy(cohort: pd.DataFrame) -> pd.DataFrame:
    """Compute FAIR proxy from OpenML machine-computed qualities when F-UJI unavailable.

    Proxy = normalized composite of NumberOfInstances, NumberOfFeatures,
            MajorityClassPercentage (standardized, clipped to [0,1]).
    Returns DataFrame with same columns as score_batch output (status='fallback').
    """
    ...


def score_cohort(cohort: pd.DataFrame, cfg) -> pd.DataFrame:
    """Synchronous entry point: run score_batch via asyncio.run(), with fallback.

    Tries F-UJI API; on connection failure falls back to fuji_fallback_proxy.
    Returns scored DataFrame.
    """
    ...
```

### Subtask Decomposition (4 subtasks for A-3)

**ST-A3-1: Async HTTP core — score_one with semaphore and retry**

- **ID**: ST-A3-1
- **Title**: Implement score_one async function with exponential backoff retry
- **Description**: Implement `score_one` using `aiohttp.ClientSession` with `asyncio.Semaphore` for concurrency control. POST to `{fuji_base}/fuji/api/v1/evaluate` with payload `{"object_identifier": url, "object_type": "landing_page"}`. On HTTP error (status >= 400) or `aiohttp.ClientError`, retry up to `retry_max` times with `await asyncio.sleep(retry_base ** attempt)`. On final failure set `status="failed"` and return zeros for scores.
- **Acceptance Criteria**:
  - Semaphore correctly limits concurrency to `concurrency` simultaneous requests
  - Retry fires on HTTP 429, 500, 503, and `aiohttp.ClientError`
  - After `retry_max` exhausted, returns `{did, fair_aggregate: 0.0, status: "failed"}` without raising
  - `_parse_fuji_response` extracts 17 sub-criteria and computes correct mean

**ST-A3-2: Disk cache layer — load/save per-did JSON**

- **ID**: ST-A3-2
- **Title**: Implement per-dataset disk cache to avoid re-scoring on reruns
- **Description**: Before issuing HTTP request in `score_one`, call `_load_cache(cache_dir, did)`. If cache hit, return parsed result immediately (no HTTP call). After successful parse, call `_save_cache(cache_dir, did, result)`. Cache files stored as `{cache_dir}/{did}.json`. `score_batch` creates `cache_dir` if it does not exist.
- **Acceptance Criteria**:
  - Re-running `score_cohort` on same cohort with populated cache dir issues zero HTTP requests
  - Cache miss path proceeds normally to HTTP call
  - Cache dir creation does not raise if already exists (`os.makedirs(..., exist_ok=True)`)

**ST-A3-3: Batch orchestration — score_batch with progress and checkpointing**

- **ID**: ST-A3-3
- **Title**: Implement score_batch: gather all coroutines, checkpoint every 100 records
- **Description**: Create `asyncio.Semaphore(concurrency)` and `aiohttp.ClientSession`. Build list of `score_one` coroutines for all rows in `cohort`. Use `asyncio.gather(*tasks, return_exceptions=True)` to collect results. After each 100 completed results (tracked by index), append partial DataFrame to `{cache_dir}/checkpoint.csv` (overwrite). Print progress line: `"Scored {n}/{total}"` every 100 records.
- **Acceptance Criteria**:
  - All cohort rows produce a result row (failed rows included with status="failed")
  - `asyncio.gather` exceptions are caught and converted to failed-status dicts, not raised
  - Checkpoint CSV written at 100, 200, ... intervals when `cache_dir` is not None
  - Returned DataFrame has columns: `did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, sub_criteria, status`

**ST-A3-4: Fallback proxy and synchronous entry point**

- **ID**: ST-A3-4
- **Title**: Implement fuji_fallback_proxy and score_cohort synchronous wrapper
- **Description**: `score_cohort` calls `asyncio.run(score_batch(...))`. Wraps the call in `try/except (aiohttp.ClientConnectorError, OSError)` to detect F-UJI unavailability; on failure logs warning and calls `fuji_fallback_proxy(cohort)`. `fuji_fallback_proxy` normalizes `NumberOfInstances` (log1p, min-max), `NumberOfFeatures` (log1p, min-max), and `1 - MajorityClassPercentage/100` to [0,1], computes mean as `fair_aggregate`, sets `fair_F=fair_A=fair_I=fair_R=fair_aggregate`, `sub_criteria=[]`, `status="fallback"`.
- **Acceptance Criteria**:
  - If F-UJI connection refused, `score_cohort` returns fallback proxy without raising
  - Fallback `fair_aggregate` values are in [0, 1] for all rows
  - `status` column contains "fallback" for all rows in fallback path
  - Normal path returns `status` values of "ok" or "failed" (not "fallback")

### Pseudo-code / Algorithm

```
score_batch(cohort, fuji_base, concurrency, retry_max, retry_base, cache_dir):
    os.makedirs(cache_dir, exist_ok=True) if cache_dir
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        tasks = [score_one(session, sem, row.did, row.landing_page_url,
                           fuji_base, retry_max, retry_base, cache_dir)
                 for row in cohort.itertuples()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    # Normalize exceptions to failed-status dicts
    cleaned = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            cleaned.append({did: cohort.iloc[i].did, fair_aggregate: 0.0, status: "failed"})
        else:
            cleaned.append(r)
    return pd.DataFrame(cleaned)

score_one(session, sem, did, url, fuji_base, retry_max, retry_base, cache_dir):
    cached = _load_cache(cache_dir, did)
    if cached: return cached
    payload = {"object_identifier": url, "object_type": "landing_page"}
    for attempt in range(retry_max + 1):
        async with sem:
            try:
                resp = await session.post(fuji_base + "/fuji/api/v1/evaluate",
                                          json=payload, timeout=30)
                if resp.status >= 400:
                    raise aiohttp.ClientResponseError(...)
                data = await resp.json()
                result = _parse_fuji_response(did, data)
                _save_cache(cache_dir, did, result)
                return result
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < retry_max:
                    await asyncio.sleep(retry_base ** attempt)
                else:
                    return {did: did, fair_aggregate: 0.0, ..., status: "failed"}
```

### Error Handling

| Error Type | Handling |
|------------|----------|
| `aiohttp.ClientResponseError` (4xx/5xx) | Retry up to `retry_max` with exponential backoff; failed-status on exhaustion |
| `asyncio.TimeoutError` | Same as above (30s per request timeout) |
| `aiohttp.ClientConnectorError` | Detected in `score_cohort`; triggers fallback proxy |
| `KeyError` in `_parse_fuji_response` | Return `{..., status: "parse_error", fair_aggregate: 0.0}` |
| `asyncio.gather` exception | Caught by `return_exceptions=True`; converted to failed-status dict |

---

## Module: Statistical Analyzer (`src/analyze.py`)

### API Signatures

```python
from typing import Optional
import pandas as pd
import numpy as np
from scipy import stats


def compute_cv(scores: pd.Series) -> float:
    """Coefficient of Variation = std / mean. Returns float."""
    ...


def compute_group_sizes(
    scores: pd.Series,
    threshold: float = 0.5,
) -> tuple[int, int]:
    """Return (n_high, n_low) where n_high = count(scores >= threshold)."""
    ...


def compute_spearman_correlations(
    df: pd.DataFrame,
    score_col: str,                # e.g. "fair_aggregate"
    covariate_cols: list[str],     # e.g. ["upload_date_ordinal", "metadata_richness"]
) -> dict[str, float]:
    """Compute Spearman r between score_col and each covariate.

    Returns: {col_name: r_value, ...}  (p-values omitted for PoC)
    """
    ...


def detect_bimodality(scores: pd.Series) -> dict:
    """Hartigan dip test + bimodality coefficient.

    Returns: {bimodal: bool, dip_stat: float, dip_p: float, bc: float}
    bc = (skew^2 + 1) / (kurtosis + 3*(n-1)^2 / ((n-2)*(n-3)))
    bimodal = True if dip_p < 0.05 or bc > 5/9
    """
    ...


def run_analysis(
    scored: pd.DataFrame,          # columns include: fair_aggregate, fair_F, fair_A,
                                   #   fair_I, fair_R, upload_date_ordinal
    cfg,
) -> dict:
    """Compute all existence metrics and return as dict.

    Returns: {cv, n_high, n_low, r_quality, r_date, bimodality: dict,
              mean_fair, std_fair, n_total, n_failed}
    """
    ...


def evaluate_gate(
    metrics: dict,
    cfg,
) -> dict:
    """Evaluate primary gate conditions.

    Returns: {passed: bool, cv: float, n_high: int, n_low: int,
              reason: str}  # reason = "PASS" or first failing condition
    """
    ...
```

### Subtask Decomposition (2 subtasks for A-4)

**ST-A4-1: Core metric computation — CV, group sizes, Spearman correlations**

- **ID**: ST-A4-1
- **Title**: Implement compute_cv, compute_group_sizes, compute_spearman_correlations
- **Description**: `compute_cv` = `scores.std(ddof=1) / scores.mean()`. `compute_group_sizes` counts `scores >= threshold` and `scores < threshold`. `compute_spearman_correlations` calls `scipy.stats.spearmanr(df[score_col], df[col])` for each covariate col; skips col if it has fewer than 10 non-null values (returns `nan`). All three functions exclude NaN values before computation.
- **Acceptance Criteria**:
  - `compute_cv` returns float, handles empty/all-zero series gracefully (returns `nan`)
  - `compute_group_sizes` returns `(n_high, n_low)` summing to total non-NaN count
  - `compute_spearman_correlations` returns dict with one key per covariate_col; NaN for insufficient data
  - All functions filter `scored[scored["status"] == "ok"]` rows before analysis (or accept pre-filtered)

**ST-A4-2: Analysis orchestration — run_analysis, detect_bimodality, evaluate_gate**

- **ID**: ST-A4-2
- **Title**: Implement detect_bimodality, run_analysis, evaluate_gate
- **Description**: `detect_bimodality` uses `diptest.diptest(scores.values)` for dip_stat/dip_p and computes BC formula. `run_analysis` calls all metric functions, assembles metrics dict, adds `metadata_richness` proxy column if missing (count of non-null OpenML qualities columns). `evaluate_gate` checks CV > `cfg.CV_GATE`, n_high >= `cfg.GROUP_SIZE_GATE`, n_low >= `cfg.GROUP_SIZE_GATE`; sets `passed = all three true`; sets `reason` to first failing condition string or "PASS".
- **Acceptance Criteria**:
  - `run_analysis` returns dict with keys: `cv, n_high, n_low, r_quality, r_date, bimodality, mean_fair, std_fair, n_total, n_failed`
  - `evaluate_gate` `passed=True` iff all three primary gate conditions met
  - `reason` string is human-readable (e.g. `"CV=0.12 below threshold 0.15"`)
  - `diptest` import wrapped in `try/except ImportError`; if unavailable, `dip_stat=nan, dip_p=nan`

### Pseudo-code / Algorithm

```
run_analysis(scored, cfg):
    valid = scored[scored["status"].isin(["ok", "fallback"])]
    scores = valid["fair_aggregate"]

    cv = compute_cv(scores)
    n_high, n_low = compute_group_sizes(scores, cfg.FAIR_THRESHOLD)

    # metadata_richness: count of non-null OpenML quality columns per row
    quality_cols = ["NumberOfInstances", "NumberOfFeatures", "MajorityClassPercentage"]
    valid["metadata_richness"] = valid[quality_cols].notna().sum(axis=1)

    covariates = compute_spearman_correlations(
        valid, "fair_aggregate",
        ["upload_date_ordinal", "metadata_richness"]
    )

    bimodality = detect_bimodality(scores)

    return {
        "cv": cv, "n_high": n_high, "n_low": n_low,
        "r_quality": covariates.get("metadata_richness", nan),
        "r_date": covariates.get("upload_date_ordinal", nan),
        "bimodality": bimodality,
        "mean_fair": scores.mean(), "std_fair": scores.std(),
        "n_total": len(valid), "n_failed": len(scored) - len(valid),
    }

evaluate_gate(metrics, cfg):
    failures = []
    if metrics["cv"] <= cfg.CV_GATE:
        failures.append(f"CV={metrics['cv']:.3f} below threshold {cfg.CV_GATE}")
    if metrics["n_high"] < cfg.GROUP_SIZE_GATE:
        failures.append(f"n_high={metrics['n_high']} below {cfg.GROUP_SIZE_GATE}")
    if metrics["n_low"] < cfg.GROUP_SIZE_GATE:
        failures.append(f"n_low={metrics['n_low']} below {cfg.GROUP_SIZE_GATE}")
    passed = len(failures) == 0
    return {"passed": passed, "cv": metrics["cv"],
            "n_high": metrics["n_high"], "n_low": metrics["n_low"],
            "reason": "PASS" if passed else "; ".join(failures)}
```

### Data Flow

| Variable | Type | Shape / Content |
|----------|------|-----------------|
| `scored` (input) | `pd.DataFrame` | rows = N datasets; cols: did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, sub_criteria, status, upload_date, NumberOfInstances, NumberOfFeatures, MajorityClassPercentage |
| `valid` (filtered) | `pd.DataFrame` | subset where status in {ok, fallback} |
| `scores` | `pd.Series[float]` | fair_aggregate values, len = n_valid |
| `metrics` (output) | `dict` | cv: float, n_high: int, n_low: int, r_quality: float, r_date: float, bimodality: dict, mean_fair: float, std_fair: float, n_total: int, n_failed: int |
| `gate` (output) | `dict` | passed: bool, cv: float, n_high: int, n_low: int, reason: str |

---

## Integration Contract

### Output of `score_cohort` (score_fuji.py) -> Input of `run_analysis` (analyze.py)

`score_cohort` returns a DataFrame that is joined with the original cohort on `did` before calling `run_analysis`.

**Required columns in `scored` DataFrame passed to `run_analysis`:**

| Column | Dtype | Source |
|--------|-------|--------|
| `did` | int | OpenML dataset ID (join key) |
| `fair_aggregate` | float64 | mean of 17 F-UJI sub-criteria, range [0, 1] |
| `fair_F` | float64 | Findability dimension mean |
| `fair_A` | float64 | Accessibility dimension mean |
| `fair_I` | float64 | Interoperability dimension mean |
| `fair_R` | float64 | Reusability dimension mean |
| `sub_criteria` | object (list[float]) | raw 17 sub-criteria scores |
| `status` | str | "ok", "failed", "fallback", "parse_error" |
| `upload_date` | datetime64 | from cohort join |
| `upload_date_ordinal` | int64 | `upload_date.map(pd.Timestamp.toordinal)` — added in main.py before run_analysis |
| `NumberOfInstances` | float64 | from cohort join |
| `NumberOfFeatures` | float64 | from cohort join |
| `MajorityClassPercentage` | float64 | from cohort join |

**Invariants:**
- `did` is unique per row
- `fair_aggregate` is NaN only when `status == "failed"` or `"parse_error"`
- `run_analysis` filters on `status in {"ok", "fallback"}` before computing metrics
- `upload_date_ordinal` must be computed in `main.py` (not inside analyze.py) to keep separation of concerns
