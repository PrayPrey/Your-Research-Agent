"""Analysis functions for H-M2: safety-robustness partial correlation."""
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

from config import (
    ABLATION_MODES, BONFERRONI_ALPHA, DIMENSIONS, ETHICS_IDX, HE1_CODE_DIR,
    HE1_JSON, HE1_RESULTS_DIR, LLAMA2_PAIRS, PRIMARY_COVARIATES, PYTHIA_CACHE_KEY,
    PYTHIA_SIZES, RHO_THRESHOLD, ROBUSTNESS_IDX, SAFETY_IDX, SECONDARY_GATE_MIN,
)


def load_he1_data(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> tuple:
    if he1_code_dir not in sys.path:
        sys.path.insert(0, he1_code_dir)

    from data_loader import load_trustllm_scores, add_annotations

    scores_df = load_trustllm_scores(he1_results_dir)
    annotated_df = add_annotations(scores_df)

    with open(he1_json) as f:
        he1_data = json.load(f)
    rho_partial = np.array(he1_data["rho_partial"])

    return scores_df, annotated_df, rho_partial


def extract_llama2_pairs(scores_df: pd.DataFrame) -> list:
    pairs = []
    for base_name, chat_name, scale in LLAMA2_PAIRS:
        if base_name not in scores_df.index:
            raise ValueError(f"Missing base model '{base_name}'")
        if chat_name not in scores_df.index:
            raise ValueError(f"Missing chat model '{chat_name}'")
        pairs.append({
            "scale": scale,
            "base_scores": scores_df.loc[base_name].values,
            "chat_scores": scores_df.loc[chat_name].values,
        })
    return pairs


def compute_partial_spearman(annotated_df: pd.DataFrame, dim_x: str, dim_y: str, covariates: list) -> tuple:
    """OLS residualization + Spearman, t-dist p-value (df=n-2-k)."""
    x = annotated_df[dim_x].values.astype(float)
    y = annotated_df[dim_y].values.astype(float)
    n = len(x)
    k = len(covariates)

    if k > 0:
        Z = annotated_df[covariates].values.astype(float)
        def residualize(v):
            reg = LinearRegression(fit_intercept=True).fit(Z, v)
            return v - reg.predict(Z)
        x_res = residualize(x)
        y_res = residualize(y)
    else:
        x_res, y_res = x, y

    rho, _ = stats.spearmanr(x_res, y_res)
    df = n - 2 - k
    if df <= 0:
        df = 1
    t_stat = rho * np.sqrt(df / (1 - rho**2 + 1e-15))
    p_val = float(2 * stats.t.sf(abs(t_stat), df=df))

    return float(rho), p_val


def verify_primary_gate(rho_partial: np.ndarray, annotated_df: pd.DataFrame) -> dict:
    """Read rho[SAFETY_IDX][ROBUSTNESS_IDX], cross-validate, evaluate gate."""
    rho_direct = float(rho_partial[SAFETY_IDX][ROBUSTNESS_IDX])

    rho_recomputed, p_recomputed = compute_partial_spearman(
        annotated_df, "safety", "robustness", PRIMARY_COVARIATES
    )

    if abs(rho_direct - rho_recomputed) > 0.001:
        print(f"⚠ rho mismatch: direct={rho_direct:.4f}, recomputed={rho_recomputed:.4f}. Using recomputed.")
        rho_sr = rho_recomputed
        p_sr = p_recomputed
    else:
        rho_sr = rho_direct
        # Recompute p-value with correct df
        _, p_sr = compute_partial_spearman(annotated_df, "safety", "robustness", PRIMARY_COVARIATES)

    gate_pass = rho_sr < RHO_THRESHOLD  # signed: must be < -0.4

    if gate_pass:
        print(f"✓ PRIMARY GATE PASS: rho_partial(safety,robustness)={rho_sr:.4f} < {RHO_THRESHOLD} (p={p_sr:.4e})")
        gate_result = "PASS"
    else:
        print(f"EXPLORE: rho_partial(safety,robustness)={rho_sr:.4f} — does not meet <{RHO_THRESHOLD}; null finding for H-M2 mechanism")
        gate_result = "FAIL/EXPLORE"

    # Cross-validate with pingouin if available
    pingouin_rho = None
    try:
        import pingouin as pg
        res = pg.partial_corr(data=annotated_df, x="safety", y="robustness",
                               covar=PRIMARY_COVARIATES, method="spearman")
        pingouin_rho = float(res["r"].iloc[0])
        print(f"  pingouin cross-validation: rho={pingouin_rho:.4f}")
    except Exception:
        pass

    return {
        "rho_partial_safety_robustness": rho_sr,
        "p_value_safety_robustness": p_sr,
        "rho_direct_from_matrix": rho_direct,
        "rho_recomputed": rho_recomputed,
        "pingouin_rho": pingouin_rho,
        "primary_gate_pass": gate_pass,
        "gate_result": gate_result,
    }


def compute_deltas(pairs: list) -> list:
    """Compute per-dimension deltas (chat - base)."""
    deltas = []
    for p in pairs:
        all_deltas = p["chat_scores"] - p["base_scores"]
        delta_rob = float(all_deltas[ROBUSTNESS_IDX])
        delta_saf = float(all_deltas[SAFETY_IDX])
        delta_eth = float(all_deltas[ETHICS_IDX])
        deltas.append({
            "scale": p["scale"],
            "all_deltas": all_deltas,
            "delta_safety": delta_saf,
            "delta_robustness": delta_rob,
            "delta_ethics": delta_eth,
            "nonpositive_robustness": delta_rob <= 0,
        })
    return deltas


def run_sign_test(deltas: list) -> dict:
    """Sign test: n_nonpositive >= SECONDARY_GATE_MIN (>=2 of 3)."""
    n_nonpositive = sum(d["nonpositive_robustness"] for d in deltas)
    secondary_pass = n_nonpositive >= SECONDARY_GATE_MIN

    if secondary_pass:
        print(f"✓ SECONDARY GATE PASS: {n_nonpositive}/3 pairs have Δ_robustness ≤ 0")
    else:
        print(f"  SECONDARY GATE FAIL: only {n_nonpositive}/3 pairs have Δ_robustness ≤ 0")

    delta_values = {d["scale"]: d["delta_robustness"] for d in deltas}
    for scale, dv in delta_values.items():
        direction = "↓ (RLHF hurts)" if dv <= 0 else "↑ (RLHF helps)"
        print(f"  LLaMA-2-{scale}: Δ_robustness={dv:+.4f} {direction}")

    return {
        "delta_robustness": delta_values,
        "n_nonpositive_delta": n_nonpositive,
        "secondary_gate_pass": secondary_pass,
    }


def run_ablations(annotated_df: pd.DataFrame) -> dict:
    ablation_results = {}
    for mode_name, mode_cfg in ABLATION_MODES.items():
        covariates = mode_cfg["covariates"]
        rho, p = compute_partial_spearman(annotated_df, "safety", "robustness", covariates)
        ablation_results[mode_name] = {
            "rho": rho, "p_value": p, "covariates": covariates
        }
        print(f"  Ablation [{mode_name}]: rho={rho:.4f}, p={p:.4e}")
    return ablation_results


def run_pythia_control(he1_json: str = HE1_JSON) -> dict | None:
    try:
        with open(he1_json) as f:
            he1_data = json.load(f)
        if PYTHIA_CACHE_KEY in he1_data:
            print("Pythia: using cached results")
            cached = he1_data[PYTHIA_CACHE_KEY]
            sizes = list(cached.keys())
            scores = [cached[s] for s in sizes]
            log_params = [float(np.log10(int(s.replace("m","e6").replace("b","e9")
                           .replace("1.4e9", "1.4e9").replace("2.8e9","2.8e9")
                           .replace("6.9e9","6.9e9"))))
                           for s in sizes]
            rho, p = stats.spearmanr(scores, log_params)
            return {"pythia_rho_robustness_scale": float(rho), "p_value": float(p)}
        else:
            print("Pythia: cache miss, attempting lm-eval (optional)")
            raise FileNotFoundError("No pythia_results in cache")
    except Exception as e:
        print(f"Pythia control skipped — unavailable: {e}")
        return None


def run_analysis(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> dict:
    scores_df, annotated_df, rho_partial = load_he1_data(he1_code_dir, he1_results_dir, he1_json)
    pairs = extract_llama2_pairs(scores_df)
    primary = verify_primary_gate(rho_partial, annotated_df)
    deltas = compute_deltas(pairs)
    sign_result = run_sign_test(deltas)
    ablations = run_ablations(annotated_df)
    pythia = run_pythia_control(he1_json)

    return {
        "scores_df": scores_df,
        "annotated_df": annotated_df,
        "rho_partial": rho_partial,
        "pairs": pairs,
        "deltas": deltas,
        "primary": primary,
        "sign_result": sign_result,
        "ablations": ablations,
        "pythia": pythia,
    }
