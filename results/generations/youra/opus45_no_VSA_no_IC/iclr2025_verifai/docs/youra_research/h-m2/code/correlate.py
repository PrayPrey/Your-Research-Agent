import pandas as pd
import pingouin as pg

def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    result = pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
    return float(result["r"].iloc[0]), float(result["p_val"].iloc[0])
