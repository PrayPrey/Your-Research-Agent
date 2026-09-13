"""H-M1: Fit NB-2 models (with/without decade FE), compute attenuation ratio and Cramér's V."""
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PARQUET_PATH = PROJECT_ROOT / "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_MODEL_PATH = PROJECT_ROOT / "docs/youra_research/h-e1/results/model_results.json"
MODEL_RESULTS_OUT = PROJECT_ROOT / "docs/youra_research/h-m1/results/model_results.json"

CONTROLS = "log_n_instances + log_n_features + age_years + age_sq"
FORMULA_WITH_FE = f"N_tasks ~ has_tags + {CONTROLS} + C(decade)"
FORMULA_NO_FE   = f"N_tasks ~ has_tags + {CONTROLS}"


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bool):
            return bool(obj)
        return super().default(obj)


def fit_nb2(formula: str, df: pd.DataFrame, label: str) -> dict[str, Any]:
    """Fit NB-2; BFGS with Nelder-Mead fallback."""
    try:
        res = smf.negativebinomial(formula, data=df, loglike_method="nb2").fit(
            method="bfgs", maxiter=100, disp=False
        )
    except Exception:
        print(f"  ⚠ BFGS failed for {label}, trying Nelder-Mead...")
        res = smf.negativebinomial(formula, data=df, loglike_method="nb2").fit(
            method="nm", maxiter=2000, disp=False
        )

    ci = res.conf_int()
    return {
        "label": label,
        "converged": bool(res.mle_retvals.get("converged", True)),
        "llf": float(res.llf),
        "aic": float(res.aic),
        "bic": float(res.bic),
        "n_obs": int(res.nobs),
        "params":   {k: float(v) for k, v in res.params.items()},
        "bse":      {k: float(v) for k, v in res.bse.items()},
        "pvalues":  {k: float(v) for k, v in res.pvalues.items()},
        "conf_int": {k: [float(ci.loc[k, 0]), float(ci.loc[k, 1])] for k in ci.index},
    }


def extract_has_tags_stats(fit_result: dict) -> dict:
    p = fit_result["params"]["has_tags"]
    ci = fit_result["conf_int"]["has_tags"]
    return {
        "irr":      float(np.exp(p)),
        "ci_lower": float(np.exp(ci[0])),
        "ci_upper": float(np.exp(ci[1])),
        "pval":     float(fit_result["pvalues"]["has_tags"]),
    }


def compute_cramers_v(df: pd.DataFrame) -> tuple[float, float]:
    ct = pd.crosstab(df["decade"], df["has_tags"])
    chi2, p_chi2, _, _ = chi2_contingency(ct)
    cramers_v = float(np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1))))
    return cramers_v, float(p_chi2)


def compute_attenuation_ratio(irr_no_fe: float, irr_with_fe: float) -> float:
    return float(irr_no_fe / irr_with_fe)


def load_or_fit_models(df: pd.DataFrame, h_e1_results: dict | None) -> dict:
    if h_e1_results and "proposed" in h_e1_results and "rc7_age_vs_decade" in h_e1_results:
        proposed = h_e1_results["proposed"]
        rc7 = h_e1_results["rc7_age_vs_decade"]

        if "has_tags" in proposed and isinstance(proposed["has_tags"], dict):
            ht = proposed["has_tags"]
        else:
            ht = extract_has_tags_stats(proposed)

        with_fe = {
            "irr":      ht["irr"],
            "ci_lower": ht["ci_lower"],
            "ci_upper": ht["ci_upper"],
            "pval":     ht["pval"],
            "params":   proposed.get("params", {}),
            "pvalues":  proposed.get("pvalues", {}),
            "conf_int": proposed.get("conf_int", {}),
            "converged": proposed.get("converged", True),
            "llf":      proposed.get("llf", None),
        }
        no_fe = {
            "irr":      rc7["irr_without_decade"],
            "ci_lower": rc7.get("ci_lower_without_decade"),
            "ci_upper": None,
            "pval":     None,
            "converged": True,
        }
        return {"with_fe": with_fe, "no_fe": no_fe, "source": "h_e1_cache"}
    else:
        print("  Refitting NB-2 WITH decade FE...")
        fit_with = fit_nb2(FORMULA_WITH_FE, df, "h_m1_with_fe")
        print(f"  converged={fit_with['converged']}, llf={fit_with['llf']:.2f}")
        print("  Refitting NB-2 WITHOUT decade FE...")
        fit_no = fit_nb2(FORMULA_NO_FE, df, "h_m1_no_fe")
        print(f"  converged={fit_no['converged']}")

        ht_with = extract_has_tags_stats(fit_with)
        ht_no   = extract_has_tags_stats(fit_no)
        with_fe = {**ht_with, **{k: fit_with[k] for k in ("params", "pvalues", "conf_int", "converged", "llf")}}
        no_fe   = {**ht_no, "converged": fit_no["converged"]}
        return {"with_fe": with_fe, "no_fe": no_fe, "source": "refitted"}


def main():
    print("=== H-M1: Model Fitting ===")

    df = pd.read_parquet(PARQUET_PATH)
    assert len(df) == 5217, f"Expected N=5217, got {len(df)}"

    h_e1_results = None
    if H_E1_MODEL_PATH.exists():
        with open(H_E1_MODEL_PATH) as f:
            h_e1_results = json.load(f)
        print(f"✓ H-E1 model results loaded (source: {H_E1_MODEL_PATH.name})")

    models = load_or_fit_models(df, h_e1_results)
    print(f"  source:       {models['source']}")
    print(f"  IRR with FE:  {models['with_fe']['irr']:.4f}")
    print(f"  p with FE:    {models['with_fe']['pval']:.2e}" if models['with_fe']['pval'] else "  p with FE:    (from cache)")
    print(f"  IRR no FE:    {models['no_fe']['irr']:.4f}")

    cramers_v, p_chi2 = compute_cramers_v(df)
    print(f"  Cramér's V:   {cramers_v:.4f}  (p={p_chi2:.2e})")

    attenuation = compute_attenuation_ratio(models["no_fe"]["irr"], models["with_fe"]["irr"])
    print(f"  Attenuation:  {attenuation:.4f}")

    has_tags_by_decade = {str(k): float(v) for k, v in df.groupby("decade")["has_tags"].mean().items()}

    output = {
        "with_fe":           models["with_fe"],
        "no_fe":             models["no_fe"],
        "cramers_v":         cramers_v,
        "p_chi2":            p_chi2,
        "attenuation_ratio": attenuation,
        "source":            models["source"],
        "has_tags_by_decade": has_tags_by_decade,
    }

    MODEL_RESULTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_RESULTS_OUT, "w") as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"✓ Saved: {MODEL_RESULTS_OUT}")


if __name__ == "__main__":
    main()
