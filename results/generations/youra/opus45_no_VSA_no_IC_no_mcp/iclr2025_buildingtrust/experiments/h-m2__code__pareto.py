"""Pareto frontier identification."""

import pandas as pd


def identify_pareto_optimal(
    df: pd.DataFrame,
    x_col: str = "truthfulqa_mc1",
    y_col: str = "advglue_avg",
) -> list:
    """Returns list of model ids not dominated on both x_col and y_col."""
    pareto = []
    for i, row_i in df.iterrows():
        dominated = False
        for j, row_j in df.iterrows():
            if i == j:
                continue
            if (row_j[x_col] >= row_i[x_col] and row_j[y_col] >= row_i[y_col] and
                (row_j[x_col] > row_i[x_col] or row_j[y_col] > row_i[y_col])):
                dominated = True
                break
        if not dominated:
            pareto.append(row_i["model"])
    return pareto


def label_pareto(df: pd.DataFrame, pareto_models: list) -> pd.DataFrame:
    """Returns df copy with added bool column 'is_pareto'."""
    df = df.copy()
    df["is_pareto"] = df["model"].isin(pareto_models)
    return df
