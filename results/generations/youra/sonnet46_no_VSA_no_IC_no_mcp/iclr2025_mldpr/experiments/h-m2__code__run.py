#!/usr/bin/env python3
"""H-M2: AIC-based model comparison (logistic vs linear vs power-law)."""
import json
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# ---------------------------------------------------------------------------
# Reused from h-e1/code/fitting.py (copied inline)
# ---------------------------------------------------------------------------

def _r2_aic(y: np.ndarray, y_pred: np.ndarray, k: int):
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    n = len(y)
    aic = n * np.log(ss_res / n) + 2 * k if ss_res > 0 else np.inf
    return r2, aic


def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    exponent = np.clip(-r * (t - t0), -500, 500)
    return K / (1.0 + np.exp(exponent))


def fit_logistic(t: np.ndarray, y: np.ndarray) -> dict:
    p0 = [0.9, 0.5, np.median(t) * 0.3]
    bounds = ([0.8, 0.01, -20], [1.05, 5.0, 60])
    try:
        popt, pcov = curve_fit(logistic, t, y, p0=p0, bounds=bounds, maxfev=10000)
        y_pred = logistic(t, *popt)
        r2, aic = _r2_aic(y, y_pred, k=3)
        ci95 = 1.96 * np.sqrt(np.diag(pcov))
        return {"popt": popt, "pcov": pcov, "r2": r2, "aic": aic, "ci95": ci95, "converged": True}
    except Exception:
        return {"popt": None, "pcov": None, "r2": 0.0, "aic": np.inf, "ci95": None, "converged": False}


def fit_linear(t: np.ndarray, y: np.ndarray) -> dict:
    coeffs = np.polyfit(t, y, deg=1)
    y_pred = np.polyval(coeffs, t)
    r2, aic = _r2_aic(y, y_pred, k=2)
    return {"coeffs": coeffs, "r2": r2, "aic": aic}

# ---------------------------------------------------------------------------
# New: power-law model
# ---------------------------------------------------------------------------

def _power_law(t, a, b):
    return a * (t + 1) ** b


def fit_power_law(t: np.ndarray, y: np.ndarray) -> dict:
    p0 = [0.5, 0.3]
    bounds = ([0.0, 0.0], [2.0, 1.0])
    try:
        popt, _ = curve_fit(_power_law, t, y, p0=p0, bounds=bounds, maxfev=5000)
        y_pred = _power_law(t, *popt)
        r2, aic = _r2_aic(y, y_pred, k=2)
        return {"popt": popt, "r2": r2, "aic": aic, "converged": True}
    except Exception:
        return {"popt": None, "r2": 0.0, "aic": np.inf, "converged": False}

# ---------------------------------------------------------------------------
# AIC delta
# ---------------------------------------------------------------------------

def compute_delta_aic(fit_a: dict, fit_b: dict) -> float:
    return fit_a["aic"] - fit_b["aic"]

# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

def verify_gate(results: dict):
    indicators = {}
    for bm in ["glue", "superglue"]:
        r = results[bm]
        indicators[f"logistic_converged_{bm}"] = r.get("logistic_converged", True)
        indicators[f"delta_aic_passes_{bm}"] = r["delta_log_vs_lin"] < -4
        indicators[f"power_passes_{bm}"] = r["delta_log_vs_pl"] < -2

    primary = all(indicators[f"delta_aic_passes_{bm}"] for bm in ["glue", "superglue"])
    secondary = all(indicators[f"power_passes_{bm}"] for bm in ["glue", "superglue"])
    gate_pass = primary and secondary
    indicators["primary_gate"] = primary
    indicators["secondary_gate"] = secondary
    indicators["gate_pass"] = gate_pass
    return gate_pass, indicators

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_timeseries(csv_path: str):
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(p)
    for col in ("months", "monthly_max"):
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in {csv_path}. Got: {list(df.columns)}")
    df = df.sort_values("months").reset_index(drop=True)
    t = df["months"].to_numpy(dtype=np.float64)
    y = df["monthly_max"].to_numpy(dtype=np.float64)
    return t, y

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def plot_gate_metrics(results: dict, out_dir: Path) -> None:
    bms = ["glue", "superglue"]
    x = np.arange(len(bms))
    width = 0.35

    d_lin = [results[b]["delta_log_vs_lin"] for b in bms]
    d_pl  = [results[b]["delta_log_vs_pl"]  for b in bms]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars1 = ax.bar(x - width/2, d_lin, width, label="Δ(log−lin)", color=["green" if v < -4 else "red" for v in d_lin])
    bars2 = ax.bar(x + width/2, d_pl,  width, label="Δ(log−pl)",  color=["steelblue" if v < -2 else "orange" for v in d_pl])
    ax.axhline(-4, color="red",      linestyle="--", linewidth=1.2, label="primary threshold (−4)")
    ax.axhline(-2, color="steelblue", linestyle=":",  linewidth=1.2, label="secondary threshold (−2)")
    ax.set_xticks(x)
    ax.set_xticklabels([b.upper() for b in bms])
    ax.set_ylabel("ΔAIC (logistic − competitor)")
    ax.set_title("Gate Metrics: ΔAIC by Benchmark")
    ax.legend(fontsize=8)
    plt.tight_layout()
    fig.savefig(out_dir / "gate_metrics.png", dpi=120)
    plt.close(fig)


def plot_model_fits(data: dict, fits: dict, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, bm in zip(axes, ["glue", "superglue"]):
        t, y = data[bm]
        t_smooth = np.linspace(t.min(), t.max(), 300)
        ax.scatter(t, y, s=20, color="black", zorder=5, label="data")

        f = fits[bm]
        if f["logistic"]["converged"]:
            ax.plot(t_smooth, logistic(t_smooth, *f["logistic"]["popt"]),
                    label=f"logistic R²={f['logistic']['r2']:.3f}", color="blue")
        ax.plot(t_smooth, np.polyval(f["linear"]["coeffs"], t_smooth),
                label=f"linear R²={f['linear']['r2']:.3f}", color="orange", linestyle="--")
        if f["power"]["converged"]:
            ax.plot(t_smooth, _power_law(t_smooth, *f["power"]["popt"]),
                    label=f"power R²={f['power']['r2']:.3f}", color="green", linestyle=":")
        ax.set_title(bm.upper())
        ax.set_xlabel("Months since release")
        ax.set_ylabel("Max score (normalized)")
        ax.legend(fontsize=7)
    plt.tight_layout()
    fig.savefig(out_dir / "model_fits.png", dpi=120)
    plt.close(fig)


def plot_residuals(data: dict, fits: dict, out_dir: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    models = ["logistic", "linear", "power"]
    colors = {"logistic": "blue", "linear": "orange", "power": "green"}
    for row, bm in enumerate(["glue", "superglue"]):
        t, y = data[bm]
        f = fits[bm]
        for col, model in enumerate(models):
            ax = axes[row][col]
            if model == "logistic" and f[model]["converged"]:
                y_pred = logistic(t, *f[model]["popt"])
            elif model == "linear":
                y_pred = np.polyval(f[model]["coeffs"], t)
            elif model == "power" and f[model]["converged"]:
                y_pred = _power_law(t, *f[model]["popt"])
            else:
                ax.set_title(f"{bm.upper()} {model}\n(not converged)")
                continue
            residuals = y - y_pred
            ax.scatter(t, residuals, s=12, color=colors[model])
            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_title(f"{bm.upper()} — {model}")
            ax.set_xlabel("Months")
            ax.set_ylabel("Residual")
    plt.tight_layout()
    fig.savefig(out_dir / "residuals.png", dpi=120)
    plt.close(fig)


def plot_aic_comparison(results: dict, out_dir: Path) -> None:
    bms = ["glue", "superglue"]
    x = np.arange(len(bms))
    width = 0.25
    aic_log = [results[b]["aic_logistic"] for b in bms]
    aic_lin = [results[b]["aic_linear"]   for b in bms]
    aic_pl  = [results[b]["aic_power"]    for b in bms]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - width, aic_log, width, label="logistic", color="blue")
    ax.bar(x,         aic_lin, width, label="linear",   color="orange")
    ax.bar(x + width, aic_pl,  width, label="power",    color="green")
    ax.set_xticks(x)
    ax.set_xticklabels([b.upper() for b in bms])
    ax.set_ylabel("AIC")
    ax.set_title("Raw AIC by Model and Benchmark")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out_dir / "aic_comparison.png", dpi=120)
    plt.close(fig)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_results(results: dict, gate, out_path: Path) -> None:
    gate_pass, indicators = gate
    payload = {
        "hypothesis_id": "h-m2",
        "gate_pass": gate_pass,
        "indicators": indicators,
        "glue": results["glue"],
        "superglue": results["superglue"],
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)


def setup_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("h-m2")
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
    data_dir = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data")
    fig_dir  = exp_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    log = setup_logging(exp_dir / "experiment.log")
    log.info("H-M2 AIC Model Comparison starting")

    t_glue, y_glue = load_timeseries(str(data_dir / "glue_timeseries_clean.csv"))
    t_sg,   y_sg   = load_timeseries(str(data_dir / "superglue_timeseries_clean.csv"))
    log.info(f"GLUE n={len(t_glue)}, SuperGLUE n={len(t_sg)}")

    results = {}
    fits    = {}

    for name, t, y in [("glue", t_glue, y_glue), ("superglue", t_sg, y_sg)]:
        log_fit = fit_logistic(t, y)
        lin_fit = fit_linear(t, y)
        pl_fit  = fit_power_law(t, y)

        if not log_fit["converged"]:
            raise RuntimeError(f"Logistic fit failed for {name}")

        d_log_lin = compute_delta_aic(log_fit, lin_fit)
        d_log_pl  = compute_delta_aic(log_fit, pl_fit)

        results[name] = {
            "aic_logistic":      float(log_fit["aic"]),
            "aic_linear":        float(lin_fit["aic"]),
            "aic_power":         float(pl_fit["aic"]),
            "delta_log_vs_lin":  float(d_log_lin),
            "delta_log_vs_pl":   float(d_log_pl),
            "logistic_params":   dict(zip(["K", "r", "t0"], log_fit["popt"].tolist())),
            "logistic_converged": log_fit["converged"],
            "r2_logistic":       float(log_fit["r2"]),
            "r2_linear":         float(lin_fit["r2"]),
            "r2_power":          float(pl_fit["r2"]) if pl_fit["converged"] else None,
        }
        fits[name] = {"logistic": log_fit, "linear": lin_fit, "power": pl_fit}

        log.info(f"{name}: AIC log={log_fit['aic']:.2f}, lin={lin_fit['aic']:.2f}, pl={pl_fit['aic']:.2f}")
        log.info(f"{name}: delta_log_vs_lin={d_log_lin:.2f}, delta_log_vs_pl={d_log_pl:.2f}")

    gate_pass, indicators = verify_gate(results)
    log.info(f"GATE: {'PASS' if gate_pass else 'FAIL'} — {indicators}")

    plot_gate_metrics(results, fig_dir)
    plot_model_fits({"glue": (t_glue, y_glue), "superglue": (t_sg, y_sg)}, fits, fig_dir)
    plot_residuals({"glue": (t_glue, y_glue), "superglue": (t_sg, y_sg)}, fits, fig_dir)
    plot_aic_comparison(results, fig_dir)
    log.info("4 figures saved")

    write_results(results, (gate_pass, indicators), exp_dir / "results.json")
    log.info(f"Results written to {exp_dir / 'results.json'}")

    print("\n" + "=" * 60)
    print("H-M2 RESULTS SUMMARY")
    print("=" * 60)
    for bm in ["glue", "superglue"]:
        r = results[bm]
        print(f"\n{bm.upper()}:")
        print(f"  AIC  logistic={r['aic_logistic']:.2f}  linear={r['aic_linear']:.2f}  power={r['aic_power']:.2f}")
        print(f"  ΔAIC log-lin={r['delta_log_vs_lin']:.2f}  log-pl={r['delta_log_vs_pl']:.2f}")
        print(f"  Primary gate (Δlog-lin < -4): {'PASS' if r['delta_log_vs_lin'] < -4 else 'FAIL'}")
        print(f"  Secondary gate (Δlog-pl < -2): {'PASS' if r['delta_log_vs_pl'] < -2 else 'FAIL'}")
    print(f"\nOVERALL GATE: {'PASS ✓' if gate_pass else 'FAIL ✗'}")
    print("=" * 60)

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
