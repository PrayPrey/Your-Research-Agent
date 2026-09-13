"""Data collection module for H-M3: Fetch benchmark paper counts."""

import logging
import time
from dataclasses import dataclass
from typing import Literal, Optional

import pandas as pd
import requests

from config import EMERGENT_BENCHMARKS, TRADITIONAL_BENCHMARKS, TIME_RANGE

logger = logging.getLogger(__name__)


class PWCAPIError(Exception):
    """Raised when PWC API is unavailable after retries."""


@dataclass
class PaperCountRecord:
    benchmark: str
    category: Optional[Literal["emergent", "traditional"]]
    year_month: str
    paper_count: int


def _rate_limited_request(
    url: str, params: Optional[dict] = None, min_interval_s: float = 0.5, timeout: float = 10.0
) -> dict:
    """Single request with rate-limit sleep + HTTP error handling."""
    time.sleep(min_interval_s)
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _pwc_get_paginated(
    endpoint: str,
    params: Optional[dict] = None,
    max_pages: int = 50,
    page_size: int = 100,
    timeout: float = 10.0,
) -> list[dict]:
    """GET all pages from PWC REST endpoint. Returns concatenated 'results' list."""
    base_url = "https://paperswithcode.com/api/v1"
    all_results = []
    params = params or {}
    params["items_per_page"] = page_size

    next_url = f"{base_url}{endpoint}"
    page = 0

    while next_url and page < max_pages:
        try:
            data = _rate_limited_request(next_url, params if page == 0 else None, timeout=timeout)
            results = data.get("results", [])
            all_results.extend(results)
            next_url = data.get("next")
            page += 1
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for {next_url}: {e}")
            break

    return all_results


def fetch_from_pwc_api(
    benchmarks: list[str],
    time_range: tuple[str, str] = ("2018-01", "2024-12"),
    retries: int = 3,
    backoff_base: float = 2.0,
) -> list[PaperCountRecord]:
    """
    Fetch monthly paper counts per benchmark from paperswithcode.com API.
    Raises PWCAPIError after exhausting retries.
    """
    records = []

    for benchmark in benchmarks:
        for attempt in range(retries):
            try:
                sota_data = _pwc_get_paginated(
                    f"/sota/{benchmark.lower().replace(' ', '-')}/",
                    max_pages=10,
                )

                monthly_counts: dict[str, int] = {}
                for entry in sota_data:
                    eval_date = entry.get("evaluation_date") or entry.get("paper", {}).get("published")
                    if eval_date:
                        ym = eval_date[:7]
                        if time_range[0] <= ym <= time_range[1]:
                            monthly_counts[ym] = monthly_counts.get(ym, 0) + 1

                for ym, count in monthly_counts.items():
                    records.append(PaperCountRecord(
                        benchmark=benchmark,
                        category=None,
                        year_month=ym,
                        paper_count=count,
                    ))

                logger.info(f"Fetched {len(monthly_counts)} months for {benchmark}")
                break

            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
                if attempt == retries - 1:
                    logger.warning(f"PWC API failed for {benchmark} after {retries} attempts: {e}")
                else:
                    time.sleep(backoff_base ** attempt)

    if not records:
        raise PWCAPIError("No data retrieved from PWC API for any benchmark")

    return records


def fetch_from_huggingface_fallback(
    benchmarks: list[str],
    time_range: tuple[str, str] = ("2018-01", "2024-12"),
) -> list[PaperCountRecord]:
    """Fallback data source using HuggingFace pwc-archive/datasets."""
    try:
        from datasets import load_dataset
    except ImportError:
        raise RuntimeError("datasets package required for HuggingFace fallback")

    logger.info("Loading pwc-archive/datasets from HuggingFace...")
    ds = load_dataset("pwc-archive/datasets", split="train")

    records: dict[tuple[str, str], int] = {}

    benchmark_aliases = {
        "MMLU": ["mmlu"],
        "BIG-Bench": ["big-bench", "bigbench", "big bench"],
        "HumanEval": ["humaneval", "human-eval", "human eval"],
        "GSM8K": ["gsm8k", "gsm-8k"],
        "MATH": ["math"],
        "ARC": ["arc", "ai2-arc"],
        "HellaSwag": ["hellaswag", "hella-swag"],
        "WinoGrande": ["winogrande", "wino-grande"],
        "TruthfulQA": ["truthfulqa", "truthful-qa"],
        "LAMBADA": ["lambada"],
        "ImageNet": ["imagenet", "image-net", "ilsvrc"],
        "CIFAR-10": ["cifar-10", "cifar10"],
        "CIFAR-100": ["cifar-100", "cifar100"],
        "MNIST": ["mnist"],
        "SQuAD": ["squad", "sq-uad"],
        "GLUE": ["glue"],
        "CoNLL": ["conll", "conll-2003", "conll2003"],
        "Penn Treebank": ["penn-treebank", "ptb", "penn treebank"],
    }

    for row in ds:
        benchmark_name = (row.get("name") or row.get("full_name") or "").lower()

        matched_benchmark = None
        for canonical, aliases in benchmark_aliases.items():
            for alias in aliases:
                if alias in benchmark_name:
                    matched_benchmark = canonical
                    break
            if matched_benchmark:
                break

        if not matched_benchmark:
            continue

        introduced = row.get("introduced_date") or ""
        num_papers = row.get("num_papers") or row.get("mention_count") or 1

        if introduced:
            ym = introduced[:7]
            if len(ym) == 7 and time_range[0] <= ym <= time_range[1]:
                key = (matched_benchmark, ym)
                records[key] = records.get(key, 0) + num_papers

    result = [
        PaperCountRecord(
            benchmark=b,
            category=None,
            year_month=ym,
            paper_count=count,
        )
        for (b, ym), count in records.items()
    ]

    logger.info(f"Loaded {len(result)} records from HuggingFace")
    return result


def collect_paper_counts(retries: int = 3) -> pd.DataFrame:
    """Try PWC API first, fall back to HF dataset on failure."""
    benchmarks = EMERGENT_BENCHMARKS + TRADITIONAL_BENCHMARKS

    try:
        records = fetch_from_pwc_api(benchmarks, TIME_RANGE, retries=retries)
        logger.info(f"Successfully fetched {len(records)} records from PWC API")
    except PWCAPIError as e:
        logger.warning(f"PWC API failed ({e}), falling back to HuggingFace")
        records = fetch_from_huggingface_fallback(benchmarks, TIME_RANGE)

    df = pd.DataFrame([
        {
            "benchmark": r.benchmark,
            "category": r.category,
            "year_month": r.year_month,
            "paper_count": r.paper_count,
        }
        for r in records
    ])

    return df
