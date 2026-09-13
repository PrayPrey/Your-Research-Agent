"""
A-3 F-UJI Async Batch Scorer
Scores OpenML dataset landing pages via F-UJI REST API with caching and fallback.
"""
import asyncio
import json
import os
from typing import Optional

import aiohttp
import numpy as np
import pandas as pd


# F-UJI sub-criteria dimension mapping (17 criteria: F=4, A=4, I=4, R=5 approx)
# Grouped by first letter of metric_identifier prefix
_DIMENSION_PREFIXES = {
    "F": ["FsF-F1", "FsF-F2", "FsF-F3", "FsF-F4"],
    "A": ["FsF-A1", "FsF-A2"],
    "I": ["FsF-I1", "FsF-I2", "FsF-I3"],
    "R": ["FsF-R1"],
}


def _load_cache(cache_dir: str, did: int) -> Optional[dict]:
    """Load cached F-UJI result for did. Returns None if not cached."""
    path = os.path.join(cache_dir, f"{did}.json")
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_cache(cache_dir: str, did: int, result: dict) -> None:
    """Persist F-UJI result to cache_dir/{did}.json."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{did}.json")
    try:
        with open(path, "w") as f:
            json.dump(result, f)
    except OSError:
        pass


def _parse_fuji_response(did: int, response_json: dict) -> dict:
    """Extract aggregate FAIR score and per-dimension scores from F-UJI response.

    F-UJI response structure: {"results": [{"metric_identifier": "FsF-F1-01D",
                                             "score": {"earned": 1, "total": 1}}, ...]}
    Returns dict with did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
                        sub_criteria (list[float]), status
    """
    try:
        results = response_json.get("results", [])
        if not results:
            return {"did": did, "fair_aggregate": 0.0, "fair_F": 0.0,
                    "fair_A": 0.0, "fair_I": 0.0, "fair_R": 0.0,
                    "sub_criteria": [], "status": "parse_error"}

        scores_by_dim = {"F": [], "A": [], "I": [], "R": []}
        all_scores = []

        for item in results:
            metric_id = item.get("metric_identifier", "")
            score_obj = item.get("score", {})
            total = score_obj.get("total", 1) or 1
            earned = score_obj.get("earned", 0)
            normalized = float(earned) / float(total) if total > 0 else 0.0
            all_scores.append(normalized)

            # Assign to dimension
            for dim, prefixes in _DIMENSION_PREFIXES.items():
                if any(metric_id.startswith(p) for p in prefixes):
                    scores_by_dim[dim].append(normalized)
                    break
            else:
                # Default: assign by first character after "FsF-"
                if metric_id.startswith("FsF-"):
                    dim_char = metric_id[4] if len(metric_id) > 4 else "R"
                    if dim_char in scores_by_dim:
                        scores_by_dim[dim_char].append(normalized)

        fair_aggregate = float(np.mean(all_scores)) if all_scores else 0.0

        def dim_mean(dim):
            vals = scores_by_dim[dim]
            return float(np.mean(vals)) if vals else fair_aggregate

        return {
            "did": did,
            "fair_aggregate": fair_aggregate,
            "fair_F": dim_mean("F"),
            "fair_A": dim_mean("A"),
            "fair_I": dim_mean("I"),
            "fair_R": dim_mean("R"),
            "sub_criteria": all_scores,
            "status": "ok",
        }
    except Exception:
        return {"did": did, "fair_aggregate": 0.0, "fair_F": 0.0,
                "fair_A": 0.0, "fair_I": 0.0, "fair_R": 0.0,
                "sub_criteria": [], "status": "parse_error"}


async def score_one(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    did: int,
    landing_url: str,
    fuji_base: str,
    retry_max: int = 3,
    retry_base: float = 2.0,
    cache_dir: Optional[str] = None,
) -> dict:
    """Score one dataset landing page via F-UJI API with retry and cache.

    Returns dict: {did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
                   sub_criteria, status}
    """
    # Check cache first
    if cache_dir:
        cached = _load_cache(cache_dir, did)
        if cached is not None:
            return cached

    payload = {"object_identifier": landing_url, "object_type": "landing_page"}
    endpoint = f"{fuji_base}/fuji/api/v1/evaluate"
    auth = aiohttp.BasicAuth("marvel", "wonderwoman")

    for attempt in range(retry_max + 1):
        async with sem:
            try:
                async with session.post(
                    endpoint,
                    json=payload,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status >= 400:
                        raise aiohttp.ClientResponseError(
                            resp.request_info, resp.history, status=resp.status
                        )
                    data = await resp.json(content_type=None)
                    result = _parse_fuji_response(did, data)
                    if cache_dir:
                        _save_cache(cache_dir, did, result)
                    return result
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < retry_max:
                    await asyncio.sleep(retry_base ** attempt)
                else:
                    return {
                        "did": did, "fair_aggregate": 0.0, "fair_F": 0.0,
                        "fair_A": 0.0, "fair_I": 0.0, "fair_R": 0.0,
                        "sub_criteria": [], "status": "retry_exhausted",
                    }


async def score_batch(
    cohort: pd.DataFrame,
    fuji_base: str,
    concurrency: int = 10,
    retry_max: int = 3,
    retry_base: float = 2.0,
    cache_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Async batch score all cohort URLs with optional disk cache.

    Returns DataFrame: did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
                       sub_criteria, status
    """
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)

    sem = asyncio.Semaphore(concurrency)
    total = len(cohort)

    async with aiohttp.ClientSession() as session:
        tasks = [
            score_one(
                session, sem,
                int(row.did), row.landing_page_url,
                fuji_base, retry_max, retry_base, cache_dir,
            )
            for row in cohort.itertuples(index=False)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Normalize exceptions to failed-status dicts
    cleaned = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            did_val = int(cohort.iloc[i]["did"])
            cleaned.append({
                "did": did_val, "fair_aggregate": 0.0, "fair_F": 0.0,
                "fair_A": 0.0, "fair_I": 0.0, "fair_R": 0.0,
                "sub_criteria": [], "status": "failed",
            })
        else:
            cleaned.append(r)

        # Progress reporting every 100
        n_done = i + 1
        if n_done % 100 == 0 or n_done == total:
            print(f"  Scored {n_done}/{total}...")

        # Checkpoint CSV every 100
        if cache_dir and (n_done % 100 == 0 or n_done == total):
            partial_df = pd.DataFrame(cleaned)
            chk_path = os.path.join(cache_dir, "checkpoint.csv")
            partial_df.drop(columns=["sub_criteria"], errors="ignore").to_csv(
                chk_path, index=False
            )

    return pd.DataFrame(cleaned)


def fuji_fallback_proxy(cohort: pd.DataFrame) -> pd.DataFrame:
    """Compute FAIR proxy from OpenML machine-computed qualities when F-UJI unavailable.

    Proxy = normalized composite of NumberOfInstances (log1p min-max),
            NumberOfFeatures (log1p min-max), 1 - MajorityClassPercentage/100.
    Returns DataFrame with same schema as score_batch output, status='fallback'.
    """
    df = cohort.copy()

    def safe_norm(series: pd.Series) -> pd.Series:
        """Min-max normalize after log1p transform."""
        vals = np.log1p(series.clip(lower=0).fillna(0))
        mn, mx = vals.min(), vals.max()
        if mx == mn:
            return pd.Series(0.5, index=series.index)
        return (vals - mn) / (mx - mn)

    scores = pd.DataFrame(index=df.index)

    if "NumberOfInstances" in df.columns:
        scores["s_instances"] = safe_norm(df["NumberOfInstances"])
    else:
        scores["s_instances"] = 0.5

    if "NumberOfFeatures" in df.columns:
        scores["s_features"] = safe_norm(df["NumberOfFeatures"])
    else:
        scores["s_features"] = 0.5

    if "MajorityClassPercentage" in df.columns:
        mcp = df["MajorityClassPercentage"].fillna(50.0).clip(0, 100)
        scores["s_balance"] = 1.0 - mcp / 100.0
    else:
        scores["s_balance"] = 0.5

    fair_aggregate = scores.mean(axis=1).clip(0, 1)

    result_df = pd.DataFrame({
        "did": df["did"].astype(int),
        "fair_aggregate": fair_aggregate,
        "fair_F": fair_aggregate,
        "fair_A": fair_aggregate,
        "fair_I": fair_aggregate,
        "fair_R": fair_aggregate,
        "sub_criteria": [[] for _ in range(len(df))],
        "status": "fallback",
    })
    print(f"  → Fallback proxy computed for {len(result_df)} datasets")
    return result_df


def score_cohort(cohort: pd.DataFrame, cfg) -> pd.DataFrame:
    """Synchronous entry: run score_batch via asyncio.run(), with fallback on connection error."""
    cache_dir = getattr(cfg, "cache_dir", None) or getattr(cfg, "CACHE_DIR", None)
    use_fallback = getattr(cfg, "use_fallback", False)

    if use_fallback:
        print("  Using fallback proxy (--use-fallback flag set)")
        return fuji_fallback_proxy(cohort)

    print(f"  Scoring {len(cohort)} datasets via F-UJI API at {cfg.FUJI_API_BASE}...")
    scored = asyncio.run(
        score_batch(
            cohort,
            fuji_base=cfg.FUJI_API_BASE,
            concurrency=cfg.FUJI_CONCURRENCY,
            retry_max=cfg.FUJI_RETRY_MAX,
            retry_base=cfg.FUJI_RETRY_BASE_S,
            cache_dir=cache_dir,
        )
    )
    ok_count = (scored["status"] == "ok").sum()
    print(f"  → Scored: {ok_count} ok, {len(scored) - ok_count} failed/error")
    return scored
