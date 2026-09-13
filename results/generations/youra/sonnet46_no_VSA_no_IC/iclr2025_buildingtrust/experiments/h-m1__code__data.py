"""H-M1 data assembly: build score DataFrame from H-E1 published scores."""
import logging
import sys
from pathlib import Path

import pandas as pd

_H_E1_ROOT = Path(__file__).parent.parent.parent / "h-e1" / "code"

import importlib.util as _ilu, pathlib as _pl
_cfg_spec = _ilu.spec_from_file_location("h_m1_config", _pl.Path(__file__).parent / "config.py")
_cfg = _ilu.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg)
DATA_DIR = _cfg.DATA_DIR
N_COMMON_MIN = _cfg.N_COMMON_MIN
WINOGRANDE_SCORES = _cfg.WINOGRANDE_SCORES

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_score_dataframe() -> pd.DataFrame:
    """
    Assemble H-M1 score matrix from H-E1 published scores + Winogrande.

    Returns:
        DataFrame columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]
        Shape: (N_common, 5), N_common >= 10

    Side effects:
        Saves DataFrame to DATA_DIR/h_m1_scores.csv
    """
    # Load h-e1 modules via importlib to avoid sys.path pollution
    import importlib.util as _ilu
    _ps_spec = _ilu.spec_from_file_location("h_e1_paper_scores", _H_E1_ROOT / "paper_scores.py")
    _ps = _ilu.module_from_spec(_ps_spec)
    _ps_spec.loader.exec_module(_ps)
    TRUSTLLM_SCORES = _ps.TRUSTLLM_SCORES
    MMLU_SCORES = _ps.MMLU_SCORES

    records = []
    for model_name, scores in TRUSTLLM_SCORES.items():
        bbq_dis = scores.get("BBQ-Disambig")
        bbq_amb = scores.get("BBQ-Ambig")
        mmlu = MMLU_SCORES.get(model_name)
        wino = WINOGRANDE_SCORES.get(model_name)
        if all(v is not None for v in [bbq_dis, bbq_amb, mmlu]):
            records.append({
                "model_name": model_name,
                "bbq_disambig": float(bbq_dis),
                "bbq_ambig": float(bbq_amb),
                "mmlu": float(mmlu),
                "winogrande": float(wino) if wino is not None else None,
            })

    df = pd.DataFrame(records).drop_duplicates("model_name").reset_index(drop=True)
    df_common = df.dropna(subset=["bbq_disambig", "bbq_ambig", "mmlu"]).copy()

    logging.info(f"N_common={len(df_common)}, models={df_common['model_name'].tolist()}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_common.to_csv(DATA_DIR / "h_m1_scores.csv", index=False)

    return df_common


def verify_n_common(df: pd.DataFrame, min_n: int = N_COMMON_MIN) -> int:
    """Assert N_common >= min_n, return N_common."""
    n = len(df)
    assert n >= min_n, f"N_common={n} < {min_n}"
    logging.info(f"N_common={n} >= {min_n} ✓")
    return n
