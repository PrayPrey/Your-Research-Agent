"""H-M1 survival DataFrame construction: TTFR, right-censoring, covariate encoding."""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

YEAR_QUARTILE_MAP = {
    2018: 1, 2019: 1,
    2020: 2, 2021: 2,
    2022: 3, 2023: 3,
    2024: 4, 2025: 4,
}


def compute_time_to_first_run(
    cohort: pd.DataFrame,
    observation_window_days: int,
) -> pd.DataFrame:
    """Compute time_to_first_run (days) and event flag (right-censoring)."""
    df = cohort.copy()
    upload = pd.to_datetime(df["upload_date"], errors="coerce")
    first_run = pd.to_datetime(df["first_run_timestamp"], errors="coerce")
    raw_ttfr = (first_run - upload).dt.days
    df["event"] = (~first_run.isna() & (raw_ttfr >= 0)).astype(int)
    df["time_to_first_run"] = np.where(
        df["event"] == 1,
        raw_ttfr.clip(lower=0),
        observation_window_days
    )
    df["time_to_first_run"] = df["time_to_first_run"].clip(upper=observation_window_days)
    df = df.dropna(subset=["upload_date"])
    logger.info(f"Survival prep: {df['event'].sum()} events, {(df['event']==0).sum()} censored")
    return df


def encode_covariates(cohort: pd.DataFrame) -> pd.DataFrame:
    """Encode matching covariates: creation_year_quartile, task_type_encoded, size_decile."""
    df = cohort.copy()
    upload = pd.to_datetime(df.get("upload_date", pd.Series(dtype="datetime64[ns]")), errors="coerce")
    year = upload.dt.year
    df["creation_year_quartile"] = year.map(YEAR_QUARTILE_MAP).fillna(2).astype(int)
    if "task_type" in df.columns:
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        task_vals = df["task_type"].fillna("other").astype(str)
        df["task_type_encoded"] = le.fit_transform(task_vals)
    else:
        df["task_type_encoded"] = 0
    if "NumberOfInstances" in df.columns:
        n = df["NumberOfInstances"].fillna(df["NumberOfInstances"].median())
        try:
            df["size_decile"] = pd.qcut(n, q=10, labels=False, duplicates="drop") + 1
        except Exception:
            df["size_decile"] = 5
        df["size_decile"] = df["size_decile"].fillna(5).astype(int)
    else:
        df["size_decile"] = 5
    return df


def build_survival_df(
    cohort: pd.DataFrame,
    observation_window_days: int,
) -> pd.DataFrame:
    """Full survival DataFrame builder."""
    df = compute_time_to_first_run(cohort, observation_window_days)
    df = encode_covariates(df)
    return df


def validate_preconditions(survival_df: pd.DataFrame, cfg) -> dict:
    """Check mechanism_exists, mechanism_isolatable, baseline_measurable."""
    result = {}
    if "findable_score" in survival_df.columns and survival_df["findable_score"].std() > 0:
        cv = survival_df["findable_score"].std() / survival_df["findable_score"].mean()
        result["mechanism_exists"] = cv > 0.1
        result["cv_findable"] = float(cv)
    else:
        result["mechanism_exists"] = False
        result["cv_findable"] = 0.0
    result["mechanism_isolatable"] = len(survival_df) >= 2 * getattr(cfg, "MIN_MATCHED_PAIRS", 100)
    result["baseline_measurable"] = int(survival_df.get("event", pd.Series()).sum()) >= 50
    result["n_with_runs"] = int(survival_df.get("event", pd.Series()).sum())
    logger.info(f"Preconditions: {result}")
    return result
