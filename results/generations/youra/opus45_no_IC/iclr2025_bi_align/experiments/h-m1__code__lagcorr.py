"""Lagged cross-correlation analysis for H-M1."""

import numpy as np
from scipy.stats import pearsonr
from typing import List, Tuple, Dict
from multiprocessing import Pool
from tqdm import tqdm

from config import MAX_LAG, N_WORKERS


def compute_lagged_correlation(user: List[float], ai: List[float], lag: int = 1) -> Tuple[float, float]:
    """AI[t] vs User[t+lag]. Returns (r, p). (nan, nan) if <3 aligned points."""
    user_arr = np.array(user)
    ai_arr = np.array(ai)

    if lag > 0:
        if lag >= len(ai_arr):
            return np.nan, np.nan
        aligned_ai = ai_arr[:-lag]
        aligned_user = user_arr[lag:]
    elif lag < 0:
        if -lag >= len(user_arr):
            return np.nan, np.nan
        aligned_user = user_arr[:lag]
        aligned_ai = ai_arr[-lag:]
    else:
        aligned_ai = ai_arr
        aligned_user = user_arr

    min_len = min(len(aligned_ai), len(aligned_user))
    if min_len < 3:
        return np.nan, np.nan

    aligned_ai = aligned_ai[:min_len]
    aligned_user = aligned_user[:min_len]

    if np.std(aligned_ai) == 0 or np.std(aligned_user) == 0:
        return 0.0, 1.0

    r, p = pearsonr(aligned_ai, aligned_user)
    return r, p


def analyze_conversation(args: Tuple[List[float], List[float], int]) -> Dict[str, Dict]:
    """Analyze single conversation for all lags. Returns {'lag_-3': {'r':.., 'p':..}, ...}"""
    user_turns, ai_turns, max_lag = args
    results = {}
    for lag in range(-max_lag, max_lag + 1):
        r, p = compute_lagged_correlation(user_turns, ai_turns, lag)
        results[f'lag_{lag}'] = {'r': r, 'p': p}
    return results


def batch_lag1(trajectories: List[Tuple[List[float], List[float]]]) -> List[float]:
    """Per-convo lag-1 r, filtering nan."""
    lag1_rs = []
    for user, ai in tqdm(trajectories, desc="Computing lag-1"):
        r, _ = compute_lagged_correlation(user, ai, lag=1)
        if not np.isnan(r):
            lag1_rs.append(r)
    return lag1_rs


def batch_multilag(trajectories: List[Tuple[List[float], List[float]]], max_lag: int = MAX_LAG) -> Dict[int, List[float]]:
    """Returns {lag: [r1, r2, ...]} across all conversations."""
    results = {lag: [] for lag in range(-max_lag, max_lag + 1)}

    args_list = [(user, ai, max_lag) for user, ai in trajectories]

    with Pool(N_WORKERS) as pool:
        per_convo = list(tqdm(
            pool.imap(analyze_conversation, args_list, chunksize=100),
            total=len(trajectories),
            desc="Multi-lag analysis"
        ))

    for convo_result in per_convo:
        for lag in range(-max_lag, max_lag + 1):
            r = convo_result[f'lag_{lag}']['r']
            if not np.isnan(r):
                results[lag].append(r)

    return results
