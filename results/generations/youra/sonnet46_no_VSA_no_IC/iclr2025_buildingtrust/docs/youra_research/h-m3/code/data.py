"""H-M3 data loading."""
import json
import logging

import pandas as pd

from config import H_M1_RESULTS, H_M2_DATA_DIR, N_COMMON_MIN, RHO_FAIRNESS_HM1

log = logging.getLogger(__name__)

REQUIRED_COLS = ["model_name", "glue_score", "advglue_score", "anli_r1_score", "anli_r3_score", "mmlu"]


def load_scores() -> pd.DataFrame:
    path = H_M2_DATA_DIR / "trustllm_scores_hm2.csv"
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df.dropna(subset=REQUIRED_COLS)
    assert len(df) >= N_COMMON_MIN, f"Only {len(df)} rows after dropna, need {N_COMMON_MIN}"
    log.info("Loaded %d models from %s", len(df), path)
    return df


def load_rho_fairness() -> float:
    try:
        data = json.loads(H_M1_RESULTS.read_text())
        val = data.get("rho_fairness", RHO_FAIRNESS_HM1)
        log.info("rho_fairness from h-m1: %.4f", val)
        return float(val)
    except Exception:
        log.warning("Could not load h-m1 results.json, using fallback %.2f", RHO_FAIRNESS_HM1)
        return RHO_FAIRNESS_HM1
