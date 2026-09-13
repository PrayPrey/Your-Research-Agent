"""Statistical analysis for H-E1: mixed-effects, bootstrap CI, permutation MANOVA, LOMO."""
import logging
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import confusion_matrix as sk_confusion_matrix
import statsmodels.formula.api as smf

logger = logging.getLogger(__name__)


def run_mixed_effects(
    df: pd.DataFrame,
    formula: str = "delta_star ~ arch_family * attack_type + objective + clean_acc",
    group_var: str = "model_id",
) -> dict:
    """Fit LME; return coef, pvalues, aic."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            model = smf.mixedlm(formula, df, groups=df[group_var])
            result = model.fit(reml=True, method="lbfgs")
            return {
                "coef": result.params.to_dict(),
                "pvalues": result.pvalues.to_dict(),
                "aic": float(result.aic) if hasattr(result, "aic") else None,
                "converged": True,
            }
        except Exception as e:
            logger.warning(f"Mixed-effects model failed: {e}")
            return {"coef": {}, "pvalues": {}, "aic": None, "converged": False, "error": str(e)}


def bootstrap_interaction_ci(
    df: pd.DataFrame,
    formula: str = "delta_star ~ arch_family * attack_type + objective + clean_acc",
    group_var: str = "model_id",
    n_iter: int = 200,
    seed: int = 42,
) -> dict:
    """Bootstrap at model level; return 95% CI per term."""
    rng = np.random.default_rng(seed)
    model_ids = df[group_var].unique()
    coefs = defaultdict(list)

    for _ in range(n_iter):
        sampled = rng.choice(model_ids, size=len(model_ids), replace=True)
        boot_df = pd.concat(
            [df[df[group_var] == m] for m in sampled]
        ).reset_index(drop=True)
        # Re-suffix duplicated model_ids to keep grouping valid
        counts = defaultdict(int)
        new_ids = []
        for mid in boot_df[group_var]:
            new_ids.append(f"{mid}_{counts[mid]}")
            counts[mid] += 1
        boot_df[group_var] = new_ids

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                res = smf.mixedlm(formula, boot_df, groups=boot_df[group_var]).fit(
                    reml=True, method="lbfgs"
                )
                for term, val in res.params.items():
                    coefs[term].append(float(val))
            except Exception:
                continue

    result = {}
    for term, vals in coefs.items():
        if len(vals) >= 10:
            result[term] = (
                float(np.percentile(vals, 2.5)),
                float(np.percentile(vals, 97.5)),
            )

    # Check if interaction term CI excludes zero
    interaction_key = None
    for k in result:
        if "arch_family" in k and "attack_type" in k:
            interaction_key = k
            break

    logger.info(f"Bootstrap CI computed for {len(result)} terms, {n_iter} iters")
    return result


def _eta_sq_per_cat(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute eta^2 per column of X."""
    families = np.unique(y)
    n_cats = X.shape[1]
    eta_sq = np.zeros(n_cats)

    for c in range(n_cats):
        col = X[:, c]
        grand_mean = col.mean()
        ss_total = np.sum((col - grand_mean) ** 2)
        if ss_total == 0:
            eta_sq[c] = 0.0
            continue
        ss_between = sum(
            np.sum(y == f) * (col[y == f].mean() - grand_mean) ** 2
            for f in families
        )
        eta_sq[c] = ss_between / ss_total

    return eta_sq


def permutation_manova(
    X: np.ndarray,
    y: np.ndarray,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """Per-category eta^2 + permutation p-value."""
    rng = np.random.default_rng(seed)
    y = np.array(y)

    observed_eta_per_cat = _eta_sq_per_cat(X, y)
    observed_eta = float(observed_eta_per_cat.mean())

    null_etas = []
    for _ in range(n_permutations):
        y_perm = rng.permutation(y)
        null_etas.append(float(_eta_sq_per_cat(X, y_perm).mean()))

    null_etas = np.array(null_etas)
    p_value = float((null_etas >= observed_eta).mean())

    # Per-category p-values
    cat_p_values = []
    for c in range(X.shape[1]):
        obs = observed_eta_per_cat[c]
        null_c = np.array([float(_eta_sq_per_cat(X, rng.permutation(y))[c]) for _ in range(200)])
        cat_p_values.append(float((null_c >= obs).mean()))

    logger.info(f"Permutation MANOVA: eta^2={observed_eta:.4f}, p={p_value:.4f}")
    return {
        "eta_squared": observed_eta,
        "p_value": p_value,
        "eta_per_category": observed_eta_per_cat.tolist(),
        "cat_p_values": cat_p_values,
    }


def lomo_classify(
    X: np.ndarray,
    family_labels: list,
) -> tuple:
    """Leave-one-model-out cosine KNN k=1. Returns (accuracy, confusion_matrix)."""
    y = np.array(family_labels)
    classes = sorted(np.unique(y).tolist())
    preds = []

    for i in range(len(X)):
        train_X = np.delete(X, i, axis=0)
        train_y = np.delete(y, i)
        test_x = X[i]

        norms = np.linalg.norm(train_X, axis=1, keepdims=True) + 1e-8
        train_norm = train_X / norms
        test_norm = test_x / (np.linalg.norm(test_x) + 1e-8)
        sims = train_norm @ test_norm
        preds.append(train_y[np.argmax(sims)])

    preds = np.array(preds)
    acc = float((preds == y).mean())
    cm = sk_confusion_matrix(y, preds, labels=classes)

    logger.info(f"LOMO accuracy: {acc:.4f}")
    return acc, cm


def build_analysis_df(
    X: np.ndarray,
    model_ids: list,
    family_labels: list,
    reliable_categories: list,
    results_raw: dict,
) -> pd.DataFrame:
    """Build long-format DataFrame for mixed-effects analysis."""
    from fine_tuner import MODEL_CONFIGS

    rows = []
    for i, model_id in enumerate(model_ids):
        family = family_labels[i]
        cfg = MODEL_CONFIGS.get(model_id, {})
        # Objective: autoregressive vs masked vs span
        if family == "decoder":
            objective = "autoregressive"
        elif family == "enc_dec":
            objective = "span_denoising"
        else:
            # encoder: masked LM for bert/roberta/albert, discriminative for electra
            objective = "discriminative" if "electra" in model_id else "masked_lm"

        # Tokenizer type (rough heuristic)
        if "gpt2" in model_id or "opt" in model_id:
            tokenizer_type = "bpe_no_cls"
        elif "t5" in model_id:
            tokenizer_type = "sentencepiece"
        elif "albert" in model_id:
            tokenizer_type = "sentencepiece"
        else:
            tokenizer_type = "wordpiece"

        for j, cat in enumerate(reliable_categories):
            delta_star_val = float(X[i, j])
            # Average clean_acc across tasks for this model+category
            entries = [
                v for v in results_raw.get(model_id, {}).values()
                if v.get("category") == cat
            ]
            clean_acc = float(np.mean([e.get("clean_acc", 0.5) for e in entries])) if entries else 0.5

            rows.append({
                "model_id": model_id,
                "arch_family": family,
                "attack_type": cat,
                "delta_star": delta_star_val,
                "objective": objective,
                "tokenizer": tokenizer_type,
                "clean_acc": clean_acc,
            })

    return pd.DataFrame(rows)


def run_all_analyses(
    X: np.ndarray,
    model_ids: list,
    family_labels: list,
    reliable_categories: list,
    results_raw: dict,
    n_bootstrap: int = 200,
    n_permutations: int = 1000,
) -> dict:
    """Returns full results dict."""
    output = {}

    # Build analysis dataframe
    df = build_analysis_df(X, model_ids, family_labels, reliable_categories, results_raw)
    output["analysis_df_shape"] = list(df.shape)
    output["n_models"] = len(model_ids)
    output["n_reliable_categories"] = len(reliable_categories)
    output["reliable_categories"] = reliable_categories
    output["model_ids"] = model_ids
    output["family_labels"] = family_labels

    # Guard: need at least 2 families and 2 categories for meaningful analysis
    unique_families = np.unique(family_labels)
    if len(unique_families) < 2 or len(reliable_categories) < 2 or X.shape[0] < 4:
        logger.warning("Insufficient data for full statistical analysis")
        output["mixed_effects"] = {"error": "insufficient data"}
        output["bootstrap_ci"] = {}
        output["permutation_manova"] = {"eta_squared": 0.0, "p_value": 1.0, "eta_per_category": []}
        output["lomo"] = {"accuracy": 0.0, "confusion_matrix": []}
        return output

    # Mixed-effects model
    logger.info("Running mixed-effects model...")
    try:
        # Check if we have enough variation in attack_type
        if df["attack_type"].nunique() > 1 and df["arch_family"].nunique() > 1:
            me_result = run_mixed_effects(df)
        else:
            me_result = {"error": "insufficient variation", "converged": False}
        output["mixed_effects"] = me_result
    except Exception as e:
        logger.warning(f"Mixed-effects failed: {e}")
        output["mixed_effects"] = {"error": str(e)}

    # Bootstrap CI
    logger.info(f"Running bootstrap CI ({n_bootstrap} iters)...")
    try:
        if df["attack_type"].nunique() > 1 and df["arch_family"].nunique() > 1:
            boot_ci = bootstrap_interaction_ci(df, n_iter=n_bootstrap)
        else:
            boot_ci = {}
        output["bootstrap_ci"] = boot_ci
    except Exception as e:
        logger.warning(f"Bootstrap CI failed: {e}")
        output["bootstrap_ci"] = {}

    # Check gate: interaction term CI excludes zero
    interaction_ci_excludes_zero = False
    for term, (lo, hi) in output.get("bootstrap_ci", {}).items():
        if "arch_family" in term and "attack_type" in term:
            if lo > 0 or hi < 0:
                interaction_ci_excludes_zero = True
                break
    output["gate_interaction_ci_excludes_zero"] = interaction_ci_excludes_zero

    # Permutation MANOVA
    logger.info(f"Running permutation MANOVA ({n_permutations} permutations)...")
    try:
        manova_result = permutation_manova(X, np.array(family_labels), n_permutations)
        output["permutation_manova"] = manova_result
    except Exception as e:
        logger.warning(f"Permutation MANOVA failed: {e}")
        output["permutation_manova"] = {"eta_squared": 0.0, "p_value": 1.0, "error": str(e)}

    # Check gate: η² > 0.15 in ≥50% of reliable categories
    eta_per_cat = output["permutation_manova"].get("eta_per_category", [])
    if eta_per_cat and len(reliable_categories) > 0:
        frac_above = sum(1 for e in eta_per_cat if e > 0.15) / len(reliable_categories)
    else:
        frac_above = 0.0
    output["gate_eta_fraction_above_015"] = float(frac_above)
    output["gate_manova_satisfied"] = frac_above >= 0.5

    # LOMO classifier
    logger.info("Running LOMO classifier...")
    try:
        lomo_acc, lomo_cm = lomo_classify(X, family_labels)
        output["lomo"] = {
            "accuracy": lomo_acc,
            "confusion_matrix": lomo_cm.tolist(),
            "above_chance": lomo_acc > (1.0 / len(unique_families)),
        }
    except Exception as e:
        logger.warning(f"LOMO failed: {e}")
        output["lomo"] = {"accuracy": 0.0, "confusion_matrix": [], "error": str(e)}

    # Overall gate verdict
    full_gate_satisfied = (
        output["gate_interaction_ci_excludes_zero"]
        and output["gate_manova_satisfied"]
    )
    poc_pass = (
        output["permutation_manova"].get("eta_squared", 0.0) > 0.0
        and output["lomo"].get("accuracy", 0.0) > (1.0 / max(len(unique_families), 1))
    )
    output["gate_full_satisfied"] = full_gate_satisfied
    output["gate_poc_pass"] = poc_pass

    logger.info(f"Gate: full={full_gate_satisfied}, PoC={poc_pass}")
    logger.info(f"MANOVA eta^2={output['permutation_manova'].get('eta_squared', 0):.4f}, "
                f"fraction>{0.15}={frac_above:.2f}")
    logger.info(f"LOMO accuracy={output['lomo'].get('accuracy', 0):.4f}")

    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Quick sanity check
    X = np.random.rand(9, 5)
    families = ["encoder"] * 4 + ["decoder"] * 3 + ["enc_dec"] * 2
    eta_per_cat = _eta_sq_per_cat(X, np.array(families))
    print("eta_sq_per_cat:", eta_per_cat)
    acc, cm = lomo_classify(X, families)
    print(f"LOMO acc={acc:.3f}, cm={cm}")
