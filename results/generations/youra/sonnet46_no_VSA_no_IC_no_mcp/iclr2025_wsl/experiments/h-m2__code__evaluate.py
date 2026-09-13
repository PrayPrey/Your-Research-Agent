"""H-M2 evaluation: PCA concentration test via linear regression R²."""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def evaluate_pca_concentration(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    k_values: list = None,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict:
    """
    PCA sweep + LinearRegression R² with bootstrap 95% CI.
    Returns: {k: {'r2': float, 'ci': [lo, hi], 'y_pred': ndarray}}
    """
    if k_values is None:
        k_values = [10, 20, 50]
    rng = np.random.default_rng(seed)
    results = {}
    for k in k_values:
        pca = PCA(n_components=k, random_state=42)
        X_tr_pca = pca.fit_transform(X_train)
        X_te_pca = pca.transform(X_test)

        reg = LinearRegression()
        reg.fit(X_tr_pca, y_train)
        y_pred = reg.predict(X_te_pca)
        r2 = float(r2_score(y_test, y_pred))

        boot_r2 = []
        n = len(y_test)
        for _ in range(n_boot):
            idx = rng.integers(0, n, size=n)
            boot_r2.append(float(r2_score(y_test[idx], y_pred[idx])))

        ci = list(np.percentile(boot_r2, [2.5, 97.5]))
        results[k] = {"r2": r2, "ci": ci, "y_pred": y_pred}
    return results


def verify_mechanism_preconditions(
    X_A_train: np.ndarray,
    X_D_train: np.ndarray,
) -> None:
    """Assert H-M2 mechanism can activate. Raises AssertionError on failure."""
    assert not np.allclose(X_A_train, X_D_train), \
        "FAIL: Condition D == Condition A (canonicalization has no effect)"

    for label, X in [("A", X_A_train), ("D", X_D_train)]:
        pca = PCA(n_components=20, random_state=42).fit(X)
        evr_sum = pca.explained_variance_ratio_.sum()
        assert evr_sum > 0.01, \
            f"FAIL: PCA degenerate for Condition {label} (EVR sum={evr_sum:.4f})"

    pca_check = PCA(n_components=20, random_state=42).fit(X_A_train)
    dummy_y = np.random.default_rng(0).standard_normal(len(X_A_train))
    reg_check = LinearRegression().fit(pca_check.transform(X_A_train), dummy_y)
    assert np.isfinite(reg_check.coef_).all(), \
        "FAIL: LinearRegression produces non-finite coefficients"

    diff = np.mean(np.abs(X_A_train - X_D_train))
    pca_a = PCA(n_components=20, random_state=42).fit(X_A_train)
    pca_d = PCA(n_components=20, random_state=42).fit(X_D_train)
    print("✅ All H-M2 mechanism preconditions satisfied")
    print(f"  Mean |X_A - X_D|: {diff:.4f}")
    print(f"  PCA-A top-20 EVR: {pca_a.explained_variance_ratio_[:20].sum():.3f}")
    print(f"  PCA-D top-20 EVR: {pca_d.explained_variance_ratio_[:20].sum():.3f}")


def compare_conditions(
    results_a: dict,
    results_d: dict,
    k_gate: int = 20,
    n_tasks_required: int = 2,
) -> dict:
    """
    results_a / results_d: {label_name: {k: {'r2', 'ci'}}}
    Gate pass: R²_D_CI_low > R²_A_CI_high at k=k_gate on >= n_tasks_required labels.
    Returns: {'gate_pass': bool, 'n_pass': int, 'n_required': int,
              'per_task': {label: {'delta_r2', 'ci_nonoverlap', 'pass'}}}
    """
    per_task = {}
    n_pass = 0
    for label in results_a:
        r2_a = results_a[label][k_gate]["r2"]
        ci_a = results_a[label][k_gate]["ci"]
        r2_d = results_d[label][k_gate]["r2"]
        ci_d = results_d[label][k_gate]["ci"]
        delta = r2_d - r2_a
        # Non-overlapping: D's lower bound > A's upper bound
        ci_nonoverlap = ci_d[0] > ci_a[1]
        passed = ci_nonoverlap
        if passed:
            n_pass += 1
        per_task[label] = {
            "delta_r2": float(delta),
            "r2_a": float(r2_a),
            "r2_d": float(r2_d),
            "ci_a": ci_a,
            "ci_d": ci_d,
            "ci_nonoverlap": ci_nonoverlap,
            "pass": passed,
        }
    gate_pass = n_pass >= n_tasks_required
    return {
        "gate_pass": gate_pass,
        "n_pass": n_pass,
        "n_required": n_tasks_required,
        "per_task": per_task,
    }
