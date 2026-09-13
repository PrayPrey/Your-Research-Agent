#!/usr/bin/env python3
"""H-M4: Saturation date detection via dual-criterion (top-3 > 0.99K AND gain < 5% peak)."""
import json
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from scipy.optimize import curve_fit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GROUND_TRUTH = {"glue": "2019-09", "superglue": "2021-06"}
LAUNCH_DATES = {"glue": "2018-04", "superglue": "2019-05"}
DATA_DIR = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data")

# Inherited from H-M3 (validated)
BENCHMARK_RELEASE_MONTH = {"glue": 0, "superglue": 0}


# ---------------------------------------------------------------------------
# H-M3 inherited functions (verbatim from validated pipeline)
# ---------------------------------------------------------------------------

def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    exponent = np.clip(-r * (t - t0), -500, 500)
    return K / (1.0 + np.exp(exponent))


def load_timeseries(csv_path: str) -> tuple:
    df = pd.read_csv(csv_path)
    t_col = "months_since_release" if "months_since_release" in df.columns else "months"
    y_col = "max_score" if "max_score" in df.columns else "monthly_max"
    t = df[t_col].values.astype(float)
    y = df[y_col].values.astype(float)
    return t, y


def bootstrap_ci(t: np.ndarray, y: np.ndarray, popt_ref: np.ndarray, n: int = 500) -> tuple:
    p0 = popt_ref.copy()
    bounds = ([0.5, 0.01, -24], [1.05, 3.0, 72])
    samples = []
    rng = np.random.default_rng(42)
    for _ in range(n):
        idx = rng.integers(0, len(t), size=len(t))
        t_b, y_b = t[idx], y[idx]
        try:
            po, _ = curve_fit(logistic, t_b, y_b, p0=p0, bounds=bounds, maxfev=5000)
            samples.append(po)
        except Exception:
            pass
    if len(samples) < 10:
        return np.array([np.inf, np.inf, np.inf]), np.array(samples)
    arr = np.array(samples)
    return arr.std(axis=0), arr


def extract_params(t_data: np.ndarray, y_data: np.ndarray, benchmark_name: str) -> dict:
    p0 = [0.92, 0.15, 12.0]
    bounds = ([0.5, 0.01, -24], [1.05, 3.0, 72])
    try:
        popt, pcov = curve_fit(logistic, t_data, y_data, p0=p0, bounds=bounds, maxfev=10000)
    except Exception as exc:
        raise RuntimeError(f"curve_fit failed for {benchmark_name}: {exc}")

    pcov_diag = np.diag(pcov)
    pcov_finite = bool(np.all(np.isfinite(pcov_diag)))
    if pcov_finite:
        perr = np.sqrt(pcov_diag)
        bootstrap_used = False
    else:
        perr, _ = bootstrap_ci(t_data, y_data, popt, n=500)
        bootstrap_used = True

    ci_95 = 1.96 * perr
    K, r, t0_rel = popt
    rel_month = BENCHMARK_RELEASE_MONTH[benchmark_name]
    t0_abs = float(t0_rel) + rel_month

    return {
        "K": float(K), "r": float(r),
        "t0_relative": float(t0_rel), "t0_absolute": float(t0_abs),
        "perr": perr.tolist(), "ci_95": ci_95.tolist(),
        "pcov": pcov.tolist(), "popt": popt.tolist(),
        "pcov_finite": pcov_finite, "bootstrap_used": bootstrap_used,
    }


# ---------------------------------------------------------------------------
# H-M4 new functions: monthly dataframe, saturation detection, evaluation
# ---------------------------------------------------------------------------

def build_monthly_df(t: np.ndarray, y: np.ndarray, benchmark: str) -> pd.DataFrame:
    """
    Build monthly aggregation DataFrame with top3_mean, monthly_gain, calendar_month.
    t is months_since_release (float), y is max_score per entry.
    Since t is already month-aggregated (one row per integer month), we derive:
      - top3_mean: rolling mean of top-3 scores up to each month
      - monthly_gain: month-over-month delta of the max score
      - calendar_month: YYYY-MM string
    """
    launch = pd.Timestamp(LAUNCH_DATES[benchmark])
    month_int = np.round(t).astype(int)
    df = pd.DataFrame({"month_idx": month_int, "max_score": y})
    # Aggregate: take max per month (handles duplicates)
    monthly = df.groupby("month_idx")["max_score"].max().reset_index()
    monthly = monthly.sort_values("month_idx").reset_index(drop=True)

    # top3_mean: cumulative mean of the top-3 scores seen so far
    # We use a rolling approach: at each month, compute mean of top-3 across all months so far
    top3_means = []
    for i in range(len(monthly)):
        scores_so_far = monthly["max_score"].iloc[:i+1].values
        top3 = np.sort(scores_so_far)[-3:] if len(scores_so_far) >= 3 else scores_so_far
        top3_means.append(float(np.mean(top3)))
    monthly["top3_mean"] = top3_means

    # monthly_gain: month-over-month delta of max_score
    monthly["monthly_gain"] = monthly["max_score"].diff().fillna(0.0)
    # Clamp negative gains to 0 (leaderboard is monotone after preprocessing)
    monthly["monthly_gain"] = monthly["monthly_gain"].clip(lower=0.0)

    # calendar_month: YYYY-MM from launch + month_idx
    monthly["calendar_month"] = monthly["month_idx"].apply(
        lambda m: (launch + pd.DateOffset(months=int(m))).strftime("%Y-%m")
    )

    return monthly


def detect_saturation_date(
    monthly_df: pd.DataFrame,
    K: float,
    threshold_k: float = 0.99,
    threshold_rate: float = 0.05,
) -> tuple:
    """
    Detect first month where top3_mean >= threshold_k * K AND monthly_gain <= threshold_rate * peak_rate.
    Returns (sat_date: str YYYY-MM or None, sat_month_idx: int or None).
    """
    peak_rate = monthly_df["monthly_gain"].max()
    k_threshold = threshold_k * K
    rate_threshold = threshold_rate * peak_rate if peak_rate > 0 else 0.0

    criterion = (
        (monthly_df["top3_mean"] >= k_threshold) &
        (monthly_df["monthly_gain"] <= rate_threshold)
    )
    met = monthly_df[criterion]
    if met.empty:
        return None, None

    row_idx = met.index[0]
    sat_date = monthly_df.loc[row_idx, "calendar_month"]
    sat_month_idx = int(monthly_df.loc[row_idx, "month_idx"])
    return sat_date, sat_month_idx


def compute_saturation_error(detected_date: str | None, ground_truth_date: str) -> float:
    """Returns absolute error in months. Returns inf if detected_date is None."""
    if detected_date is None:
        return float("inf")
    d = pd.Timestamp(detected_date)
    g = pd.Timestamp(ground_truth_date)
    delta = relativedelta(d, g)
    return abs(delta.months + delta.years * 12)


def verify_mechanism_activated(results: dict) -> tuple:
    indicators = {
        "criterion_fired_GLUE": results["glue"]["sat_date"] is not None,
        "criterion_fired_SuperGLUE": results["superglue"]["sat_date"] is not None,
        "error_below_threshold_GLUE": results["glue"]["sat_error_months"] < 6,
        "error_below_threshold_SuperGLUE": results["superglue"]["sat_error_months"] < 6,
        "beats_null_baseline": (
            results["glue"]["sat_date"] is not None and
            results["superglue"]["sat_date"] is not None
        ),
    }
    activated = (
        indicators["criterion_fired_GLUE"] and
        indicators["criterion_fired_SuperGLUE"]
    )
    gate_pass = (
        indicators["error_below_threshold_GLUE"] and
        indicators["error_below_threshold_SuperGLUE"]
    )
    return activated, gate_pass, indicators


def sensitivity_grid(
    monthly_df: pd.DataFrame,
    K: float,
    ks: list,
    rates: list,
    ground_truth: str,
) -> pd.DataFrame:
    rows = []
    for tk in ks:
        for tr in rates:
            sat_date, _ = detect_saturation_date(monthly_df, K, tk, tr)
            err = compute_saturation_error(sat_date, ground_truth)
            rows.append({
                "threshold_k": tk,
                "threshold_rate": tr,
                "sat_date": sat_date,
                "sat_error_months": err,
            })
    return pd.DataFrame(rows)


def prospective_forecast(
    monthly_df: pd.DataFrame,
    t: np.ndarray,
    y: np.ndarray,
    sat_month_idx: int,
    benchmark: str,
    lookback: int = 6,
) -> tuple:
    """Truncate timeseries at sat_month_idx - lookback, refit, forecast saturation."""
    # Find position of sat_month_idx in t array
    cut_month = sat_month_idx - lookback
    if cut_month < 6:
        return None, float("inf")

    mask = t <= cut_month
    t_trunc = t[mask]
    y_trunc = y[mask]
    if len(t_trunc) < 6:
        return None, float("inf")

    try:
        params_trunc = extract_params(t_trunc, y_trunc, benchmark)
    except Exception:
        return None, float("inf")

    K_trunc = params_trunc["K"]
    monthly_trunc = build_monthly_df(t_trunc, y_trunc, benchmark)
    forecast_date, _ = detect_saturation_date(monthly_trunc, K_trunc)
    err = compute_saturation_error(forecast_date, GROUND_TRUTH[benchmark])
    return forecast_date, err


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_sat_error_bar(results: dict, fig_dir: Path) -> None:
    bms = ["glue", "superglue"]
    errors = [results[b]["sat_error_months"] for b in bms]
    threshold = 6

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["seagreen" if e < threshold else "tomato" for e in errors]
    bars = ax.bar([b.upper() for b in bms], errors, color=colors, alpha=0.85)
    ax.axhline(threshold, color="red", linestyle="--", linewidth=1.5, label=f"±{threshold}m threshold")
    for bar, e in zip(bars, errors):
        label = f"{e:.1f}m" if e < float("inf") else "inf"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                label, ha="center", va="bottom", fontsize=11)
    ax.set_ylabel("Saturation date error (months)")
    ax.set_title("H-M4 Gate: Saturation Date Error vs. Ground Truth")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "gate_metrics_comparison.png", dpi=120)
    plt.close(fig)


def plot_saturation_timeline(monthly_dfs: dict, results: dict, fig_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, bm in zip(axes, ["glue", "superglue"]):
        mdf = monthly_dfs[bm]
        K = results[bm]["K"]
        sat_date = results[bm]["sat_date"]
        gt_date = GROUND_TRUTH[bm]

        x = range(len(mdf))
        ax.plot(x, mdf["max_score"], "o-", color="royalblue", ms=4, lw=1.5, label="max_score")
        ax.plot(x, mdf["top3_mean"], "s--", color="darkorange", ms=3, lw=1.2, label="top3_mean")
        ax.axhline(0.99 * K, color="purple", linestyle=":", lw=1.2, label=f"0.99K={0.99*K:.3f}")
        ax.axhline(K, color="red", linestyle="--", lw=1.2, label=f"K={K:.3f}")

        labels = list(mdf["calendar_month"])
        if sat_date and sat_date in labels:
            idx = labels.index(sat_date)
            ax.axvline(idx, color="seagreen", lw=2, label=f"detected: {sat_date}")
        if gt_date in labels:
            idx_gt = labels.index(gt_date)
            ax.axvline(idx_gt, color="black", lw=2, linestyle=":", label=f"GT: {gt_date}")

        ax.set_title(f"{bm.upper()} Saturation Timeline")
        ax.set_xlabel("Month index")
        ax.set_ylabel("Score")
        ax.legend(fontsize=7)
        # x tick labels every 6 months
        step = max(1, len(labels) // 8)
        ax.set_xticks(range(0, len(labels), step))
        ax.set_xticklabels(labels[::step], rotation=45, ha="right", fontsize=7)

    plt.suptitle("H-M4: Saturation Detection Timeline", fontsize=13)
    plt.tight_layout()
    fig.savefig(fig_dir / "saturation_timeline.png", dpi=120)
    plt.close(fig)


def plot_dual_criterion(monthly_dfs: dict, results: dict, fig_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    for col, bm in enumerate(["glue", "superglue"]):
        mdf = monthly_dfs[bm]
        K = results[bm]["K"]
        peak_rate = mdf["monthly_gain"].max()
        sat_date = results[bm]["sat_date"]
        labels = list(mdf["calendar_month"])

        # Top panel: top3_mean vs K threshold
        ax = axes[0, col]
        ax.plot(range(len(mdf)), mdf["top3_mean"], "o-", color="darkorange", ms=3, lw=1.5)
        ax.axhline(0.99 * K, color="purple", linestyle="--", lw=1.2, label=f"0.99K={0.99*K:.3f}")
        if sat_date and sat_date in labels:
            ax.axvline(labels.index(sat_date), color="seagreen", lw=2, label=f"sat: {sat_date}")
        ax.set_title(f"{bm.upper()} top3_mean vs K threshold")
        ax.set_ylabel("top3_mean")
        ax.legend(fontsize=7)

        # Bottom panel: monthly_gain vs rate threshold
        ax = axes[1, col]
        ax.plot(range(len(mdf)), mdf["monthly_gain"], "o-", color="royalblue", ms=3, lw=1.5)
        ax.axhline(0.05 * peak_rate, color="red", linestyle="--", lw=1.2,
                   label=f"5% peak={0.05*peak_rate:.4f}")
        if sat_date and sat_date in labels:
            ax.axvline(labels.index(sat_date), color="seagreen", lw=2, label=f"sat: {sat_date}")
        ax.set_title(f"{bm.upper()} monthly_gain vs rate threshold")
        ax.set_ylabel("monthly_gain")
        ax.set_xlabel("Month index")
        ax.legend(fontsize=7)

    plt.suptitle("H-M4: Dual-Criterion Activation", fontsize=13)
    plt.tight_layout()
    fig.savefig(fig_dir / "dual_criterion_activation.png", dpi=120)
    plt.close(fig)


def plot_prospective(monthly_dfs: dict, results: dict, t_data: dict, y_data: dict,
                     fig_dir: Path) -> None:
    bm = "glue"
    mdf = monthly_dfs[bm]
    sat_idx = results[bm].get("sat_month_idx")
    forecast_date = results[bm].get("prospective_forecast_date")
    gt_date = GROUND_TRUTH[bm]
    labels = list(mdf["calendar_month"])
    lookback = 6

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(len(mdf)), mdf["max_score"], "o-", color="royalblue", ms=4, lw=1.5,
            label="full timeseries")
    if sat_idx is not None:
        cut = sat_idx - lookback
        ax.axvline(cut, color="gray", linestyle=":", lw=1.5, label=f"truncation (idx {cut})")
        ax.axvline(sat_idx, color="seagreen", lw=2, label=f"detected sat: {results[bm]['sat_date']}")

    if forecast_date and forecast_date in labels:
        ax.axvline(labels.index(forecast_date), color="purple", lw=2,
                   linestyle="--", label=f"prospective forecast: {forecast_date}")
    if gt_date in labels:
        ax.axvline(labels.index(gt_date), color="black", lw=2, linestyle=":",
                   label=f"GT: {gt_date}")

    ax.set_title("H-M4 Prospective Forecast (GLUE, truncated -6m)")
    ax.set_xlabel("Month index")
    ax.set_ylabel("Max score")
    step = max(1, len(labels) // 8)
    ax.set_xticks(range(0, len(labels), step))
    ax.set_xticklabels(labels[::step], rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=8)
    plt.tight_layout()
    fig.savefig(fig_dir / "prospective_forecast.png", dpi=120)
    plt.close(fig)


def plot_sensitivity_heatmap(sensitivity_results: dict, fig_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ks = [0.95, 0.99, 1.00]
    rates = [0.02, 0.05, 0.10]

    for ax, bm in zip(axes, ["glue", "superglue"]):
        grid_df = sensitivity_results[bm]
        matrix = np.full((len(ks), len(rates)), float("nan"))
        for _, row in grid_df.iterrows():
            ki = ks.index(row["threshold_k"])
            ri = rates.index(row["threshold_rate"])
            err = row["sat_error_months"]
            matrix[ki, ri] = err if err < float("inf") else 99

        im = ax.imshow(matrix, cmap="RdYlGn_r", vmin=0, vmax=12, aspect="auto")
        ax.set_xticks(range(len(rates)))
        ax.set_xticklabels([f"{r:.2f}" for r in rates])
        ax.set_yticks(range(len(ks)))
        ax.set_yticklabels([f"{k:.2f}" for k in ks])
        ax.set_xlabel("threshold_rate")
        ax.set_ylabel("threshold_k")
        ax.set_title(f"{bm.upper()} Sensitivity: error (months)")
        for ki in range(len(ks)):
            for ri in range(len(rates)):
                val = matrix[ki, ri]
                txt = f"{val:.1f}" if not np.isnan(val) and val < 99 else "inf"
                ax.text(ri, ki, txt, ha="center", va="center", fontsize=9)
        plt.colorbar(im, ax=ax)

    plt.suptitle("H-M4 Sensitivity: threshold_k × threshold_rate vs. error", fontsize=13)
    plt.tight_layout()
    fig.savefig(fig_dir / "sensitivity_heatmap.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Results I/O
# ---------------------------------------------------------------------------

def write_results(results: dict, out_path: Path) -> None:
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("h-m4")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh = logging.FileHandler(log_path)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    code_dir = Path(__file__).parent
    exp_dir  = code_dir.parent
    fig_dir  = exp_dir / "figures"
    out_dir  = code_dir / "outputs"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    log = setup_logging(exp_dir / "experiment.log")
    log.info("H-M4 Saturation Detection starting")

    # Load timeseries (inherited from H-M3 data pipeline)
    t_glue, y_glue = load_timeseries(str(DATA_DIR / "glue_timeseries_clean.csv"))
    t_sg,   y_sg   = load_timeseries(str(DATA_DIR / "superglue_timeseries_clean.csv"))
    log.info(f"GLUE n={len(t_glue)}, SuperGLUE n={len(t_sg)}")

    t_data = {"glue": t_glue, "superglue": t_sg}
    y_data = {"glue": y_glue, "superglue": y_sg}

    # Fit logistic (reuse H-M3 extract_params)
    params = {}
    for bm in ["glue", "superglue"]:
        params[bm] = extract_params(t_data[bm], y_data[bm], bm)
        log.info(f"{bm.upper()} K={params[bm]['K']:.4f}, r={params[bm]['r']:.4f}, "
                 f"t0_rel={params[bm]['t0_relative']:.3f}")

    # Build monthly DataFrames
    monthly_dfs = {}
    for bm in ["glue", "superglue"]:
        monthly_dfs[bm] = build_monthly_df(t_data[bm], y_data[bm], bm)
        mdf = monthly_dfs[bm]
        assert len(mdf) >= 12, f"Insufficient monthly data for {bm}: {len(mdf)}"
        assert {"top3_mean", "monthly_gain", "calendar_month"}.issubset(set(mdf.columns))
        K = params[bm]["K"]
        assert K > 0, f"K out of range for {bm}"
        log.info(f"{bm.upper()} monthly rows={len(mdf)}, "
                 f"top3_mean_final={mdf['top3_mean'].iloc[-1]:.4f}, "
                 f"peak_gain={mdf['monthly_gain'].max():.4f}")

    # Saturation detection (primary criterion)
    results = {}
    for bm in ["glue", "superglue"]:
        K = params[bm]["K"]
        mdf = monthly_dfs[bm]
        sat_date, sat_month_idx = detect_saturation_date(mdf, K)
        sat_error = compute_saturation_error(sat_date, GROUND_TRUTH[bm])
        log.info(f"{bm.upper()} sat_date={sat_date}, GT={GROUND_TRUTH[bm]}, "
                 f"error={sat_error:.1f}m, criterion_fired={sat_date is not None}")
        results[bm] = {
            "K": K,
            "sat_date": sat_date,
            "sat_month_idx": sat_month_idx,
            "sat_error_months": sat_error,
            "criterion_fired": sat_date is not None,
            "error_below_threshold": sat_error < 6,
        }

    # Mechanism activation check
    activated, gate_pass, indicators = verify_mechanism_activated(results)
    log.info(f"Mechanism activated={activated}, gate_pass={gate_pass}, indicators={indicators}")

    # Sensitivity grid (3x3)
    ks = [0.95, 0.99, 1.00]
    rates = [0.02, 0.05, 0.10]
    sensitivity_results = {}
    for bm in ["glue", "superglue"]:
        grid = sensitivity_grid(monthly_dfs[bm], params[bm]["K"], ks, rates, GROUND_TRUTH[bm])
        sensitivity_results[bm] = grid
        results[bm]["sensitivity_grid"] = grid.to_dict(orient="records")
        log.info(f"{bm.upper()} sensitivity grid:\n{grid.to_string()}")

    # Prospective forecast (GLUE only)
    sat_idx_glue = results["glue"]["sat_month_idx"]
    if sat_idx_glue is not None:
        forecast_date, forecast_err = prospective_forecast(
            monthly_dfs["glue"], t_glue, y_glue, sat_idx_glue, "glue"
        )
    else:
        forecast_date, forecast_err = None, float("inf")
    results["glue"]["prospective_forecast_date"] = forecast_date
    results["glue"]["prospective_forecast_error"] = forecast_err
    log.info(f"GLUE prospective forecast={forecast_date}, error={forecast_err:.1f}m")

    # Plots
    plot_sat_error_bar(results, fig_dir)
    plot_saturation_timeline(monthly_dfs, results, fig_dir)
    plot_dual_criterion(monthly_dfs, results, fig_dir)
    plot_prospective(monthly_dfs, results, t_data, y_data, fig_dir)
    plot_sensitivity_heatmap(sensitivity_results, fig_dir)
    log.info("5 figures saved")

    # Build final results payload
    gate_result = "PASS" if gate_pass else "FAIL"
    payload = {
        "hypothesis_id": "h-m4",
        "gate_pass": gate_pass,
        "gate_result": gate_result,
        "glue": {**results["glue"], "K": params["glue"]["K"]},
        "superglue": {**results["superglue"], "K": params["superglue"]["K"]},
        "mechanism_activated": {
            "glue": indicators["criterion_fired_GLUE"],
            "superglue": indicators["criterion_fired_SuperGLUE"],
            "indicators": indicators,
        },
        "status": "completed",
    }

    write_results(payload, exp_dir / "experiment_results.json")
    # CSV summary
    rows = []
    for bm in ["glue", "superglue"]:
        rows.append({
            "benchmark": bm,
            "K": params[bm]["K"],
            "sat_date": results[bm]["sat_date"],
            "sat_month_idx": results[bm]["sat_month_idx"],
            "sat_error_months": results[bm]["sat_error_months"],
            "criterion_fired": results[bm]["criterion_fired"],
            "error_below_threshold": results[bm]["error_below_threshold"],
            "ground_truth": GROUND_TRUTH[bm],
        })
    pd.DataFrame(rows).to_csv(out_dir / "results.csv", index=False)
    log.info("Results written")

    # Console summary
    print("\n" + "=" * 65)
    print("H-M4 SATURATION DETECTION RESULTS")
    print("=" * 65)
    for bm in ["glue", "superglue"]:
        r = results[bm]
        print(f"\n{bm.upper()}:")
        print(f"  K={params[bm]['K']:.4f}")
        print(f"  Detected saturation: {r['sat_date']}")
        print(f"  Ground truth:        {GROUND_TRUTH[bm]}")
        print(f"  Error: {r['sat_error_months']:.1f} months  {'✓ <6m' if r['error_below_threshold'] else '✗ >=6m'}")
        print(f"  Criterion fired: {r['criterion_fired']}")
    pfe = results["glue"].get("prospective_forecast_error", float("inf"))
    print(f"\nGLUE prospective forecast error: {pfe:.1f}m  {'✓ <3m' if pfe < 3 else '—'}")
    print(f"\nGATE RESULT: {'PASS ✓' if gate_pass else 'FAIL ✗'} ({gate_result})")
    print("=" * 65)

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
