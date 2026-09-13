"""H-M1: Data Pipeline — PWC quarterly panel construction."""
import ast
import warnings
import pandas as pd
import numpy as np
from datasets import load_dataset

warnings.filterwarnings("ignore")

DOMAIN_MAP = {
    "image-classification": "cv", "object-detection": "cv",
    "semantic-segmentation": "cv", "instance-segmentation": "cv",
    "image-generation": "cv", "pose-estimation": "cv",
    "action-recognition": "cv", "face-recognition": "cv",
    "image-super-resolution": "cv", "depth-estimation": "cv",
    "optical-flow-estimation": "cv", "image-inpainting": "cv",
    "visual-question-answering": "cv", "image-captioning": "cv",
    "video-classification": "cv", "3d-object-detection": "cv",
    "deblurring": "cv", "denoising": "cv", "colorization": "cv",
    "language-modelling": "nlp", "text-classification": "nlp",
    "natural-language-inference": "nlp", "question-answering": "nlp",
    "machine-translation": "nlp", "sentiment-analysis": "nlp",
    "named-entity-recognition": "nlp", "coreference-resolution": "nlp",
    "semantic-textual-similarity": "nlp", "text-summarization": "nlp",
    "reading-comprehension": "nlp", "information-retrieval": "nlp",
    "word-embeddings": "nlp", "relation-extraction": "nlp",
    "dialogue": "nlp", "common-sense-reasoning": "nlp",
    "optical character recognition (ocr)": "nlp",
    "tabular-classification": "tabular", "tabular-regression": "tabular",
    "time-series": "tabular", "recommendation-systems": "tabular",
}


def _safe_eval(val):
    if isinstance(val, (list, dict)):
        return val
    if isinstance(val, str):
        try:
            return ast.literal_eval(val)
        except Exception:
            return None
    return None


def _extract_primary_score(metrics_val) -> float | None:
    """Extract the first non-None numeric value from a metrics dict."""
    metrics = _safe_eval(metrics_val) if not isinstance(metrics_val, dict) else metrics_val
    if not isinstance(metrics, dict):
        return None
    for v in metrics.values():
        if v is None:
            continue
        try:
            score = float(str(v).replace(",", "").replace("%", "").strip())
            if not np.isnan(score):
                return score
        except (ValueError, TypeError):
            continue
    return None


def load_pwc_raw() -> pd.DataFrame:
    """Load raw PWC evaluation-tables from HuggingFace, flattening nested structure.
    Returns: DataFrame[task, dataset, model, evaluated_on, score, domain, quarter]
    """
    print("  Fetching pwc-archive/evaluation-tables from HuggingFace...")
    ds = load_dataset(
        "pwc-archive/evaluation-tables",
        split="train",
        storage_options={"client_kwargs": {"timeout": 60}},
    )

    rows = []
    for record in ds:
        task = str(record.get("task", "") or "").strip()
        task_lower = task.lower()
        domain = DOMAIN_MAP.get(task_lower, "other")

        datasets_val = _safe_eval(record.get("datasets")) or []
        if not isinstance(datasets_val, list):
            continue

        for dset_entry in datasets_val:
            if not isinstance(dset_entry, dict):
                continue
            dataset_name = str(dset_entry.get("dataset", "") or "").strip()
            if not dataset_name:
                continue

            sota = dset_entry.get("sota") or {}
            if isinstance(sota, str):
                sota = _safe_eval(sota) or {}
            if not isinstance(sota, dict):
                continue

            sota_rows = sota.get("rows") or []
            if isinstance(sota_rows, str):
                sota_rows = _safe_eval(sota_rows) or []
            if not isinstance(sota_rows, list):
                continue

            for entry in sota_rows:
                if not isinstance(entry, dict):
                    continue
                model = str(entry.get("model_name", "") or "").strip()
                if not model:
                    continue
                paper_date = entry.get("paper_date")
                if not paper_date:
                    continue
                metrics = entry.get("metrics")
                score = _extract_primary_score(metrics)
                if score is None:
                    continue
                rows.append({
                    "task": task,
                    "dataset": dataset_name,
                    "model": model,
                    "evaluated_on": paper_date,
                    "score": score,
                    "domain": domain,
                })

    if not rows:
        raise ValueError("No rows extracted from pwc-archive/evaluation-tables")

    df = pd.DataFrame(rows)
    df["evaluated_on"] = pd.to_datetime(df["evaluated_on"], errors="coerce")
    df = df.dropna(subset=["evaluated_on", "score"])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])
    df = df[(df["evaluated_on"] >= "2018-01-01") & (df["evaluated_on"] <= "2025-12-31")]
    df["quarter"] = df["evaluated_on"].dt.to_period("Q").astype(str)
    print(f"  Extracted {len(df):,} rows from {df['task'].nunique()} tasks")
    return df.reset_index(drop=True)


def compute_quarterly_panel(
    pwc_raw: pd.DataFrame,
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> pd.DataFrame:
    """Build (benchmark_id, quarter) panel.
    Returns: DataFrame[benchmark_id, task, dataset, quarter, submission_count,
                       cumulative_count, score_var_top10]
    """
    panels = []
    for (task, dataset), bm_df in pwc_raw.groupby(["task", "dataset"]):
        if bm_df["model"].nunique() < min_submissions:
            continue
        qdf = (
            bm_df.groupby("quarter")
            .agg(
                submission_count=("model", "nunique"),
                score_var_top10=(
                    "score",
                    lambda x: x.nlargest(min(10, len(x))).var() if len(x) >= 2 else np.nan,
                ),
            )
            .reset_index()
            .sort_values("quarter")
            .reset_index(drop=True)
        )
        if len(qdf) < min_quarters:
            continue
        qdf["cumulative_count"] = qdf["submission_count"].cumsum()
        qdf["benchmark_id"] = f"{task}__{dataset}"
        qdf["task"] = task
        qdf["dataset"] = dataset
        panels.append(qdf)

    if not panels:
        return pd.DataFrame(columns=[
            "benchmark_id", "task", "dataset", "quarter",
            "submission_count", "cumulative_count", "score_var_top10",
        ])
    panel_df = pd.concat(panels, ignore_index=True)
    return panel_df[[
        "benchmark_id", "task", "dataset", "quarter",
        "submission_count", "cumulative_count", "score_var_top10",
    ]]


def load_panel(
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> tuple:
    """Top-level entry: load raw + compute panel.
    Returns: (pwc_raw: pd.DataFrame, panel_df: pd.DataFrame)
    """
    print("Loading PWC raw data from HuggingFace...")
    pwc_raw = load_pwc_raw()
    print(f"  Raw: {len(pwc_raw):,} rows, {pwc_raw['task'].nunique()} tasks")
    print("Computing quarterly panel...")
    panel_df = compute_quarterly_panel(pwc_raw, min_submissions, min_quarters)
    print(f"  Panel: {len(panel_df):,} rows, {panel_df['benchmark_id'].nunique()} benchmarks")
    required = ["benchmark_id", "task", "dataset", "quarter",
                "submission_count", "cumulative_count", "score_var_top10"]
    missing = [c for c in required if c not in panel_df.columns]
    assert not missing, f"Missing panel columns: {missing}"
    return pwc_raw, panel_df
