import pandas as pd
from config import CONFIG

def load_h_m1_data(path: str = None) -> pd.DataFrame:
    path = path or CONFIG.h_m1_data_path
    df = pd.read_csv(path)
    required = ["passed", "pylint_score", "radon_cc", "loc"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df
