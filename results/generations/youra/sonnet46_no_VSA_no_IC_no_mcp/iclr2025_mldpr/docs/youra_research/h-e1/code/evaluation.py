"""Evaluation: summarize linear vs logistic comparison."""


def evaluate(linear: dict, logistic_result: dict) -> dict:
    """Summarize comparison between linear and logistic fit."""
    converged = logistic_result["converged"]
    r2 = float(logistic_result["r2"]) if converged else float("nan")
    delta_aic = (
        float(logistic_result["aic"]) - float(linear["aic"])
        if converged
        else float("nan")
    )

    params = {}
    if converged:
        K, r_val, t0 = logistic_result["popt"]
        ci = logistic_result["ci95"]
        params = {
            "K": float(K), "K_ci95": float(ci[0]),
            "r": float(r_val), "r_ci95": float(ci[1]),
            "t0": float(t0), "t0_ci95": float(ci[2]),
        }

    return {
        "converged": converged,
        "r2": r2,
        "delta_aic": delta_aic,
        "params": params,
    }
