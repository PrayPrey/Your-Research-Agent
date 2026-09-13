"""data_pipeline.py — PWC + OpenML loading and saturation labeling for H-E1."""
import warnings
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


DOMAIN_MAP = {
    # Computer Vision tasks
    "image-classification": "cv",
    "object-detection": "cv",
    "semantic-segmentation": "cv",
    "image-segmentation": "cv",
    "action-recognition": "cv",
    "pose-estimation": "cv",
    "depth-estimation": "cv",
    "image-generation": "cv",
    "face-detection": "cv",
    "face-recognition": "cv",
    "optical-flow-estimation": "cv",
    "video-classification": "cv",
    "instance-segmentation": "cv",
    "3d-object-detection": "cv",
    # NLP tasks
    "question-answering": "nlp",
    "text-classification": "nlp",
    "natural-language-inference": "nlp",
    "machine-translation": "nlp",
    "language-modelling": "nlp",
    "named-entity-recognition": "nlp",
    "sentiment-analysis": "nlp",
    "text-generation": "nlp",
    "summarization": "nlp",
    "word-embeddings": "nlp",
    "coreference-resolution": "nlp",
    "reading-comprehension": "nlp",
    "relation-extraction": "nlp",
    "dependency-parsing": "nlp",
    "semantic-textual-similarity": "nlp",
    "dialogue": "nlp",
    "information-retrieval": "nlp",
}

CC18_TASK_IDS = [
    3, 6, 11, 12, 14, 15, 16, 18, 22, 23,
    28, 29, 31, 32, 37, 44, 46, 50, 54, 151,
    182, 188, 300, 307, 458, 469, 554, 1049,
    1050, 1053, 1063, 1067, 1068, 1590, 4134,
    4534, 4538, 6332, 23381, 40499, 40668,
    40966, 40982, 40983, 40984, 40994, 41027,
]


def load_pwc_panel() -> pd.DataFrame:
    """Load PWC leaderboard panel from HuggingFace pwc-archive/evaluation-tables."""
    from datasets import load_dataset

    print("Loading PWC evaluation tables from HuggingFace...")
    ds = load_dataset(
        "pwc-archive/evaluation-tables",
        split="train",
        storage_options={"client_kwargs": {"timeout": 60}},
    )
    df = ds.to_pandas()

    # Normalize column names
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if "task" in cl and "benchmark" not in cl:
            col_map[c] = "task_raw"
        elif "dataset" in cl or "benchmark" in cl:
            col_map[c] = "benchmark"
        elif "model" in cl:
            col_map[c] = "model"
        elif "date" in cl or "paper_date" in cl:
            col_map[c] = "date"
        elif "score" in cl or "metric_result" in cl or "value" in cl:
            col_map[c] = "score"
        elif "metric" in cl:
            col_map[c] = "metric"
    df = df.rename(columns=col_map)

    required = {"benchmark", "model", "score"}
    missing = required - set(df.columns)
    if missing:
        # Try to infer from available columns
        if "benchmark" not in df.columns and len(df.columns) > 0:
            df["benchmark"] = df.iloc[:, 0].astype(str)
        if "model" not in df.columns:
            df["model"] = "unknown"
        if "score" not in df.columns:
            df["score"] = np.nan

    # Map task to domain
    if "task_raw" in df.columns:
        df["domain"] = df["task_raw"].str.lower().str.strip().map(DOMAIN_MAP)
    else:
        df["domain"] = None

    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.NaT

    # Drop rows with missing key fields
    df = df.dropna(subset=["benchmark", "score"])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])

    # Filter to known CV/NLP domains
    df = df[df["domain"].isin(["cv", "nlp"])]

    # Filter: >=20 submissions per benchmark
    counts = df.groupby("benchmark")["model"].count()
    valid = counts[counts >= 20].index
    df = df[df["benchmark"].isin(valid)]

    # Filter: >=2 years history
    if df["date"].notna().any():
        date_range = df.groupby("benchmark")["date"].agg(lambda x: (x.max() - x.min()).days)
        valid_range = date_range[date_range >= 730].index
        df = df[df["benchmark"].isin(valid_range)]
        # Filter: 2018-2025
        df = df[(df["date"] >= "2018-01-01") & (df["date"] <= "2025-12-31")]

    # Add quarter column
    if df["date"].notna().any():
        df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    else:
        df["quarter"] = "unknown"

    df = df[["benchmark", "domain", "model", "date", "score", "quarter"]].reset_index(drop=True)
    print(f"PWC panel: {len(df)} rows, {df['benchmark'].nunique()} benchmarks")
    return df


def load_openml_panel() -> pd.DataFrame:
    """Load OpenML AMLB + CC18 benchmark panel."""
    import openml

    print("Loading OpenML benchmark panel...")
    all_evals = []

    try:
        suite = openml.study.get_suite("amlb-classification-all")
        task_ids = list(suite.tasks)
    except Exception as e:
        print(f"Warning: Could not load amlb-classification-all suite: {e}")
        task_ids = []

    task_ids = list(set(task_ids + CC18_TASK_IDS))
    print(f"Loading {len(task_ids)} OpenML tasks...")

    task_name_map = {}
    for task_id in task_ids:
        try:
            task = openml.tasks.get_task(task_id, download_splits=False)
            task_name_map[task_id] = getattr(task, "task_name", str(task_id))
        except Exception:
            task_name_map[task_id] = str(task_id)

    for task_id in task_ids:
        try:
            evals = openml.evaluations.list_evaluations(
                function="predictive_accuracy",
                tasks=[task_id],
                output_format="dataframe",
            )
            if evals is None or len(evals) == 0:
                continue
            evals = evals.copy()
            evals["task_id"] = task_id
            evals["benchmark"] = task_name_map.get(task_id, str(task_id))
            all_evals.append(evals)
        except Exception:
            continue

    if not all_evals:
        print("Warning: No OpenML evaluations loaded — returning empty DataFrame")
        return pd.DataFrame(columns=["task_id", "benchmark", "domain", "model", "date", "score", "quarter"])

    df = pd.concat(all_evals, ignore_index=True)

    # Normalize columns
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if cl in ("setup_name", "flow_name"):
            rename[c] = "model"
        elif cl in ("value", "predictive_accuracy"):
            rename[c] = "score"
        elif cl in ("upload_time", "start_time"):
            rename[c] = "date"
    df = df.rename(columns=rename)

    for col, default in [("model", "unknown"), ("score", np.nan)]:
        if col not in df.columns:
            df[col] = default
    if "date" not in df.columns:
        df["date"] = pd.NaT

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])
    df["domain"] = "tabular"

    # Filter: >=20 runs per task
    counts = df.groupby("task_id")["model"].count()
    valid = counts[counts >= 20].index
    df = df[df["task_id"].isin(valid)]

    # Filter: >=2 years history
    if df["date"].notna().any():
        date_range = df.groupby("task_id")["date"].agg(lambda x: (x.max() - x.min()).days)
        valid_range = date_range[date_range >= 730].index
        df = df[df["task_id"].isin(valid_range)]

    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df = df[["task_id", "benchmark", "domain", "model", "date", "score", "quarter"]].reset_index(drop=True)
    print(f"OpenML panel: {len(df)} rows, {df['benchmark'].nunique()} benchmarks")
    return df


def label_saturation(panel: pd.DataFrame) -> pd.DataFrame:
    """Add label column: saturated|healthy|excluded per (benchmark, quarter)."""
    panel = panel.copy()
    labels = {}

    for benchmark in panel["benchmark"].unique():
        bdf = panel[panel["benchmark"] == benchmark].copy()
        if "date" in bdf.columns and bdf["date"].notna().any():
            bdf = bdf.sort_values("date")
        quarters = list(bdf["quarter"].unique())
        # Sort quarters chronologically
        try:
            quarters = sorted(quarters, key=lambda q: pd.Period(q))
        except Exception:
            quarters = sorted(quarters)

        tau_series = []
        prev_scores = None

        for q in quarters:
            qdf = bdf[bdf["quarter"] == q]
            scores_q = qdf.set_index("model")["score"]

            if prev_scores is None:
                prev_scores = scores_q
                continue

            common = scores_q.index.intersection(prev_scores.index)
            if len(common) < 5:
                tau_series.append((q, None))
                prev_scores = scores_q
                continue

            tau, _ = stats.kendalltau(prev_scores[common], scores_q[common])
            tau_series.append((q, tau))
            prev_scores = scores_q

        # Assign labels based on tau series
        consec_sat = 0
        for q, tau in tau_series:
            if tau is None:
                consec_sat = 0
                labels[(benchmark, q)] = "excluded"
            elif tau > 0.90:
                consec_sat += 1
                if consec_sat >= 2:
                    labels[(benchmark, q)] = "saturated"
                else:
                    labels[(benchmark, q)] = "excluded"
            elif tau < 0.70:
                consec_sat = 0
                labels[(benchmark, q)] = "healthy"
            else:
                consec_sat = 0
                labels[(benchmark, q)] = "excluded"

    panel["label"] = panel.apply(
        lambda r: labels.get((r["benchmark"], r["quarter"]), "excluded"), axis=1
    )
    return panel


def get_domain_panels(
    panel: pd.DataFrame,
    domain: str,
    min_saturated: int = 15,
    min_healthy: int = 15,
) -> tuple:
    """Filter panel to domain, split by label. Warn if below min thresholds."""
    domain_panel = panel[panel["domain"] == domain]

    saturated_df = domain_panel[domain_panel["label"] == "saturated"].copy()
    healthy_df = domain_panel[domain_panel["label"] == "healthy"].copy()

    n_sat_benchmarks = saturated_df["benchmark"].nunique()
    n_healthy_benchmarks = healthy_df["benchmark"].nunique()

    if n_sat_benchmarks < min_saturated:
        warnings.warn(
            f"Domain '{domain}': only {n_sat_benchmarks} saturated benchmarks "
            f"(min required: {min_saturated}). Results may have low statistical power.",
            UserWarning,
        )
    if n_healthy_benchmarks < min_healthy:
        warnings.warn(
            f"Domain '{domain}': only {n_healthy_benchmarks} healthy benchmarks "
            f"(min required: {min_healthy}). Results may have low statistical power.",
            UserWarning,
        )

    return saturated_df, healthy_df
