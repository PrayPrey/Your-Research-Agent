import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path

from config import CFG

logger = logging.getLogger(__name__)


def load_h_e1_similarities(results_path: str = None) -> dict:
    path = results_path or CFG.paths.h_e1_results
    with open(path) as f:
        data = json.load(f)
    sim_matrices = {}
    for enc in CFG.encoders:
        mat = np.array(data["sim_matrices"][enc], dtype=np.float32)
        assert mat.shape == (4, 2), f"{enc} shape {mat.shape} != (4,2)"
        sim_matrices[enc] = mat
    logger.info("Loaded H-E1 sim matrices: %s", {k: v.shape for k, v in sim_matrices.items()})
    return sim_matrices


def load_h_e2_pass_at_1(results_path: str = None) -> np.ndarray:
    path = results_path or CFG.paths.h_e2_csv
    df = pd.read_csv(path)
    grouped = df.groupby(["condition", "benchmark"])["pass1"].mean()
    out = np.full((4, 2), np.nan)
    for i, cond in enumerate(CFG.source_conditions):
        for j, bm_key in enumerate(CFG.h_e2_benchmark_keys):
            try:
                out[i, j] = grouped.loc[cond, bm_key]
            except KeyError:
                pass  # stays NaN → CANNOT_TEST
    logger.info("H-E2 pass@1 matrix:\n%s", out)
    return out


def load_h_c1_pass_at_1(results_path: str = None) -> np.ndarray | None:
    path = results_path or CFG.paths.h_c1_json
    if not Path(path).exists():
        logger.info("H-C1 not found at %s — skipping 7B", path)
        return None
    with open(path) as f:
        data = json.load(f)
    out = np.array(data, dtype=np.float64)
    assert out.shape == (4, 2)
    return out


def validate_inputs(sim_matrices: dict, pass_mat: np.ndarray) -> None:
    for enc, mat in sim_matrices.items():
        assert mat.shape == (4, 2), f"{enc} bad shape"
        assert not np.any(np.isnan(mat)), f"{enc} has NaN"
    assert pass_mat.shape == (4, 2)
    for j, bm in enumerate(CFG.benchmarks):
        col = pass_mat[:, j]
        if np.all(np.isnan(col)):
            logger.warning("Benchmark %s col %d: all NaN → CANNOT_TEST", bm, j)
        else:
            logger.info("Benchmark %s col %d: %s", bm, j, col)
