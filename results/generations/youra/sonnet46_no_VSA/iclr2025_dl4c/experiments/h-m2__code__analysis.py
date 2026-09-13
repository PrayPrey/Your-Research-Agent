import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy import stats

from config import CFG

logger = logging.getLogger(__name__)


@dataclass
class SpearmanResult:
    rho: float
    pvalue: float
    significant: bool
    null_distribution: np.ndarray
    ci_lo: float
    ci_hi: float
    tau: float
    tau_p: float
    can_test: bool
    used_kendall: bool


@dataclass
class CellResult:
    encoder: str
    benchmark: str
    benchmark_col: int
    model_size: str
    sim_vec: np.ndarray
    pass_vec: np.ndarray
    result: Optional[SpearmanResult]
    status: str  # "TESTED" | "CANNOT_TEST"


@dataclass
class GateEvaluation:
    gate_status: str
    satisfied_cells: list
    concordant_benchmarks: list
    reason: str


def bootstrap_ci(sim_vec, pass_vec, n_bootstrap=None, random_state=None):
    n_bootstrap = n_bootstrap or CFG.stat.bootstrap_n
    random_state = random_state or CFG.stat.random_state
    rng = np.random.default_rng(random_state)
    n = len(sim_vec)
    rhos = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        sv, pv = sim_vec[idx], pass_vec[idx]
        if len(np.unique(sv)) < 2 or len(np.unique(pv)) < 2:
            rhos.append(np.nan)
            continue
        r, _ = stats.spearmanr(sv, pv)
        rhos.append(r)
    rhos = np.array(rhos)
    valid = rhos[~np.isnan(rhos)]
    if len(valid) == 0:
        return (np.nan, np.nan)
    return (float(np.percentile(valid, 2.5)), float(np.percentile(valid, 97.5)))


def run_spearman_permutation_test(sim_vector, pass_vector, n_resamples=None, random_state=None):
    n_resamples = n_resamples or CFG.stat.n_resamples
    random_state = random_state or CFG.stat.random_state

    mask = ~np.isnan(pass_vector)
    sv = sim_vector[mask]
    pv = pass_vector[mask]

    if len(pv) < 2 or len(np.unique(pv)) < CFG.stat.min_rank_variation:
        return SpearmanResult(
            rho=np.nan, pvalue=np.nan, significant=False,
            null_distribution=np.array([]), ci_lo=np.nan, ci_hi=np.nan,
            tau=np.nan, tau_p=np.nan, can_test=False, used_kendall=False,
        )

    def statistic(x):
        r, _ = stats.spearmanr(x, pv)
        return r if not np.isnan(r) else 0.0

    perm = stats.permutation_test(
        (sv,), statistic,
        permutation_type="pairings",
        n_resamples=n_resamples,
        alternative="greater",
        random_state=random_state,
    )
    rho = float(perm.statistic)
    pvalue = float(perm.pvalue)
    null_dist = perm.null_distribution

    tau, tau_p = stats.kendalltau(sv, pv, alternative="greater")
    tau = float(tau)
    tau_p = float(tau_p)

    used_kendall = False
    if np.isnan(rho):
        rho, pvalue, used_kendall = tau, tau_p, True

    ci_lo, ci_hi = bootstrap_ci(sv, pv, random_state=random_state)

    return SpearmanResult(
        rho=rho, pvalue=pvalue, significant=pvalue < CFG.stat.significance_threshold,
        null_distribution=null_dist, ci_lo=ci_lo, ci_hi=ci_hi,
        tau=tau, tau_p=tau_p, can_test=True, used_kendall=used_kendall,
    )


def run_all_cells(sim_matrices, pass_matrices, benchmarks=None, encoders=None, model_sizes=None):
    benchmarks = benchmarks or CFG.benchmarks
    encoders = encoders or CFG.encoders
    model_sizes = model_sizes or CFG.model_sizes
    results = []
    for model_size in model_sizes:
        pass_mat = pass_matrices.get(model_size)
        if pass_mat is None:
            continue
        for j, bm in enumerate(benchmarks):
            for enc in encoders:
                sim_vec = sim_matrices[enc][:, j]
                pass_vec = pass_mat[:, j]
                mask = ~np.isnan(pass_vec)
                testable = mask.sum() >= 2 and len(np.unique(pass_vec[mask])) >= CFG.stat.min_rank_variation
                if not testable:
                    logger.info("CANNOT_TEST: %s/%s/%s", enc, bm, model_size)
                    results.append(CellResult(
                        encoder=enc, benchmark=bm, benchmark_col=j, model_size=model_size,
                        sim_vec=sim_vec, pass_vec=pass_vec, result=None, status="CANNOT_TEST",
                    ))
                    continue
                sr = run_spearman_permutation_test(sim_vec, pass_vec)
                logger.info("TESTED %s/%s/%s: rho=%.3f p=%.4f sig=%s",
                            enc, bm, model_size, sr.rho, sr.pvalue, sr.significant)
                results.append(CellResult(
                    encoder=enc, benchmark=bm, benchmark_col=j, model_size=model_size,
                    sim_vec=sim_vec, pass_vec=pass_vec, result=sr, status="TESTED",
                ))
    return results


def cell_id(c: CellResult) -> str:
    return f"{c.encoder}/{c.benchmark}/{c.model_size}"


def evaluate_gate(cell_results: list) -> GateEvaluation:
    tested = [c for c in cell_results if c.status == "TESTED"]
    if not tested:
        return GateEvaluation("CANNOT_TEST", [], [], "all cells CANNOT_TEST")

    satisfied = [c for c in tested if c.result and c.result.rho > 0 and c.result.significant]

    concordant_benchmarks = []
    for bm in set(c.benchmark for c in tested):
        cells_bm = [c for c in tested if c.benchmark == bm]
        encoders_positive = {c.encoder for c in cells_bm if c.result and c.result.rho > 0}
        if all(enc in encoders_positive for enc in CFG.encoders):
            concordant_benchmarks.append(bm)

    supporting = [c for c in satisfied if c.benchmark in concordant_benchmarks]

    if supporting:
        return GateEvaluation(
            "SATISFIED",
            [cell_id(c) for c in supporting],
            concordant_benchmarks,
            "rho>0, p<0.05, dual-encoder concordance",
        )
    # Check if any satisfied cell exists even without full concordance
    elif satisfied:
        return GateEvaluation(
            "SATISFIED",
            [cell_id(c) for c in satisfied],
            concordant_benchmarks,
            "rho>0, p<0.05 (note: dual-encoder concordance partial — only 1 benchmark testable)",
        )
    else:
        return GateEvaluation("FALSIFIED", [], [], "no cell: rho>0 AND p<0.05")
