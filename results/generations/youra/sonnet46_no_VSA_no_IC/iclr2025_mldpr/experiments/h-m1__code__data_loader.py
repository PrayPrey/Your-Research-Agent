"""data_loader.py — Load H-E1 outputs for H-M1 analysis."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def load_residual_cov(csv_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load pwc_cov_computed.csv; return (paper_counts, residual_cov) sorted ascending.

    Raises:
        FileNotFoundError: if csv_path does not exist
        ValueError: if N != 111 or required columns missing or not sorted ascending
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"H-E1 CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    required = {"benchmark_name", "paper_count", "cov", "residual_cov"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in H-E1 CSV: {missing}")

    if len(df) < 100 or len(df) > 200:
        raise ValueError(f"Unexpected N={len(df)} benchmarks (expected ~111-115)")

    df = df.sort_values("paper_count", ascending=True, kind="stable").reset_index(drop=True)

    paper_counts = df["paper_count"].to_numpy(dtype=int)
    residual_cov = df["residual_cov"].to_numpy(dtype=float)

    if not np.all(paper_counts[:-1] <= paper_counts[1:]):
        raise ValueError("paper_counts not sorted ascending after sort — data integrity issue")

    return paper_counts, residual_cov


def load_paper_count_star_idx(
    results_json_path: Path,
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
) -> int:
    """Load paper_count_star_idx (0-based) from H-E1 JSON, or recompute via PELT.

    Raises:
        ValueError: if idx not in (0, 111) or leads to pre_segment len < 3
    """
    idx = None

    if results_json_path.exists():
        with open(results_json_path) as f:
            h_e1_results = json.load(f)
        raw_idx = h_e1_results.get("breakpoint_idx")
        if raw_idx is not None:
            idx = int(raw_idx)
            print(f"Loaded paper_count_star_idx={idx} from H-E1 JSON")
        else:
            print("WARNING: 'breakpoint_idx' absent from H-E1 JSON — recomputing via PELT")
    else:
        print(f"WARNING: H-E1 JSON not found at {results_json_path} — recomputing via PELT")

    if idx is None:
        import ruptures as rpt

        sigma = float(np.std(residual_cov, ddof=1))
        bic_pen = sigma ** 2 * np.log(len(residual_cov))

        algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(residual_cov)
        bkps = algo.predict(pen=bic_pen)
        n_bkps = len(bkps) - 1

        if n_bkps < 1:
            raise ValueError(
                "PELT fallback found no breakpoints — cannot determine paper_count_star_idx. "
                "Ensure H-E1 ran successfully and its outputs are present."
            )
        idx = bkps[0] - 1
        print(f"Fallback PELT recomputed paper_count_star_idx={idx}")

    N = len(residual_cov)
    if not (0 < idx < N):
        raise ValueError(
            f"paper_count_star_idx={idx} is at boundary (must be in (0, {N})). "
            "Pre-segment would be empty or full series."
        )
    if idx < 3:
        raise ValueError(
            f"pre_segment length={idx} < 3 (min_pre_segment_n=3). Cannot compute stable variance."
        )

    return idx
