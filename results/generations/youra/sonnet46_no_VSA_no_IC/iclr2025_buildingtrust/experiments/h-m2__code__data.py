"""H-M2 data assembly: load h-m1 base CSV and extend with robustness scores."""
import logging
import pandas as pd

from config import (
    H_M1_DATA_DIR, DATA_DIR, ROBUSTNESS_SCORES, N_COMMON_MIN
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_hm1_base() -> pd.DataFrame:
    """
    Load h-m1 validated DataFrame from H_M1_DATA_DIR/h_m1_scores.csv.

    Returns:
        pd.DataFrame columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]
        Shape: (N_common, 5)

    Raises:
        FileNotFoundError: if h_m1_scores.csv does not exist
        AssertionError: if required columns missing
    """
    csv_path = H_M1_DATA_DIR / "h_m1_scores.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"h-m1 scores CSV not found at {csv_path}. "
            "Run h-m1 experiment first to generate it."
        )
    df = pd.read_csv(csv_path)
    required = ["model_name", "bbq_disambig", "bbq_ambig", "mmlu"]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"h_m1_scores.csv missing columns: {missing}"
    logging.info(f"Loaded h-m1 base: N={len(df)}, models={df['model_name'].tolist()}")
    return df


def build_robustness_scores() -> pd.DataFrame:
    """
    Build per-model robustness DataFrame from ROBUSTNESS_SCORES constant in config.

    Returns:
        pd.DataFrame columns: [model_name, glue_score, advglue_score, anli_r1_score, anli_r3_score]
        Shape: (N_robustness, 5) — only models with all 4 scores included
    """
    records = [
        {"model_name": model, **scores}
        for model, scores in ROBUSTNESS_SCORES.items()
        if all(scores.get(k) is not None
               for k in ["glue_score", "advglue_score", "anli_r1_score", "anli_r3_score"])
    ]
    df = pd.DataFrame(records)
    logging.info(f"Robustness scores built: N={len(df)}, models={df['model_name'].tolist()}")
    return df


def build_master_dataframe() -> pd.DataFrame:
    """
    Inner join h-m1 base DataFrame with robustness scores on model_name.

    Returns:
        pd.DataFrame columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande,
                               glue_score, advglue_score, anli_r1_score, anli_r3_score]
        Shape: (N_common_robust, 9)

    Side effects:
        Logs N_common_robust and any models dropped vs h-m1
        Saves DataFrame to DATA_DIR/trustllm_scores_hm2.csv

    Raises:
        AssertionError: if N_common_robust < N_COMMON_MIN
    """
    df_base = load_hm1_base()
    df_rob = build_robustness_scores()

    df = df_base.merge(df_rob, on="model_name", how="inner")
    n_robust = len(df)

    dropped = set(df_base["model_name"]) - set(df["model_name"])
    if dropped:
        logging.warning(f"Models dropped (no robustness scores): {dropped}")

    assert n_robust >= N_COMMON_MIN, (
        f"N_common_robust={n_robust} < {N_COMMON_MIN} — "
        "insufficient data for partial correlation"
    )
    logging.info(f"N_common_robust={n_robust}, models={df['model_name'].tolist()}")

    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / "trustllm_scores_hm2.csv"
    df.to_csv(out_path, index=False)
    logging.info(f"Saved master DataFrame to {out_path}")
    return df


def verify_preconditions(df: pd.DataFrame) -> int:
    """
    Assert all mechanism pre-conditions before analysis.

    Args:
        df: master DataFrame from build_master_dataframe()

    Returns:
        int — N_common_robust

    Raises:
        AssertionError: if N < N_COMMON_MIN, required columns missing, or insufficient variance
    """
    required = [
        "bbq_disambig", "bbq_ambig", "glue_score",
        "advglue_score", "anli_r1_score", "anli_r3_score", "mmlu"
    ]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"Missing columns: {missing}"
    assert len(df) >= N_COMMON_MIN, f"N={len(df)} < {N_COMMON_MIN}"
    for col in required[:-1]:  # skip mmlu variance check
        assert df[col].nunique() > 3, f"Insufficient variance in {col}"
    logging.info(f"✅ H-M2 verification: N={len(df)}, all columns present, variance OK")
    print(f"✅ H-M2 verification: N={len(df)}, all columns present, variance OK")
    return len(df)
