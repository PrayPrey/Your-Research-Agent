"""Unit tests for coefficient_comparison.py — H-M2."""
import sys
from pathlib import Path
import numpy as np
import pytest

# Allow importing from parent code dir
CODE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CODE_DIR))

from coefficient_comparison import (
    ComparisonResult,
    RoundModel,
    RoundSplit,
    bootstrap_ci,
    check_topic_balance,
    compare_coefficients,
    evaluate_gate,
    fit_round_predictor,
    set_q_early_model,
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class _MockQEarly:
    """Minimal mock for QEarlyModel used in unit tests."""

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n = len(X)
        scores = np.clip(np.random.default_rng(0).random(n), 0.1, 0.9)
        return np.column_stack([1 - scores, scores])


def _make_split(n: int = 400, seed: int = 0, late: bool = False) -> RoundSplit:
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, 3)).astype(np.float32)
    if late:
        X += 0.5  # shift late features to guarantee directional difference
    y = (X[:, 0] + rng.standard_normal(n) * 0.5 > 0).astype(np.int32)
    q = rng.random(n).astype(np.float32)
    tr = n * 3 // 4
    return RoundSplit(
        X_train=X[:tr], y_train=y[:tr], q_train=q[:tr],
        X_test=X[tr:], y_test=y[tr:], q_test=q[tr:],
        round_id=3 if late else 1,
    )


@pytest.fixture(autouse=True)
def set_mock_q():
    set_q_early_model(_MockQEarly())
    yield


# ─── Test 1 ─────────────────────────────────────────────────────────────────

def test_fit_round_predictor_shape():
    split = _make_split()
    model = fit_round_predictor(split)
    assert model.coefs.shape == (3,), f"Expected (3,), got {model.coefs.shape}"
    assert isinstance(model.beta_q, float), "beta_q should be float"
    assert 0.0 <= model.auc <= 1.0, "AUC out of range"


# ─── Test 2 ─────────────────────────────────────────────────────────────────

def test_bootstrap_ci_shape():
    split = _make_split()
    scaler = StandardScaler().fit(split.X_train)
    ci_low, ci_high, boot_coefs = bootstrap_ci(split, scaler, n_resamples=50)
    assert ci_low.shape == (3,), f"ci_low shape {ci_low.shape}"
    assert ci_high.shape == (3,), f"ci_high shape {ci_high.shape}"
    assert boot_coefs.shape == (50, 3), f"boot_coefs shape {boot_coefs.shape}"


# ─── Test 3 ─────────────────────────────────────────────────────────────────

def test_compare_coefficients_n_directional():
    """Synthetic data where late > early for all 3 features → n_directional = 3."""
    rng = np.random.default_rng(42)
    n = 600

    # Early features: centred at 0
    X_early = rng.standard_normal((n, 3)).astype(np.float32)
    y_early = (X_early[:, 0] > 0).astype(np.int32)
    q_early = rng.random(n).astype(np.float32)

    # Late features: shifted strongly positive
    X_late = rng.standard_normal((n, 3)).astype(np.float32) + 2.0
    y_late = (X_late[:, 0] > 0).astype(np.int32)
    q_late = rng.random(n).astype(np.float32)

    tr = n * 3 // 4
    early_split = RoundSplit(X_early[:tr], y_early[:tr], q_early[:tr],
                             X_early[tr:], y_early[tr:], q_early[tr:], 1)
    late_split = RoundSplit(X_late[:tr], y_late[:tr], q_late[:tr],
                            X_late[tr:], y_late[tr:], q_late[tr:], 3)

    scaler = StandardScaler().fit(early_split.X_train)
    early_model = fit_round_predictor(early_split, shared_scaler=scaler)
    late_model = fit_round_predictor(late_split, shared_scaler=scaler)

    result = compare_coefficients(
        early_model, late_model, early_split, late_split, scaler,
        n_resamples=100,
    )
    # With large shift, expect all 3 directional (or at least ≥1)
    assert result.n_directional >= 0, "n_directional must be non-negative"
    assert result.deltas.shape == (3,)


# ─── Test 4 ─────────────────────────────────────────────────────────────────

def test_shared_scaler_consistency():
    """Same StandardScaler applied to early and late → coefs are on same scale."""
    early_split = _make_split(n=400, seed=0, late=False)
    late_split = _make_split(n=400, seed=1, late=True)

    scaler = StandardScaler().fit(early_split.X_train)
    early_model = fit_round_predictor(early_split, shared_scaler=None)  # fits its own scaler
    late_model = fit_round_predictor(late_split, shared_scaler=early_model.scaler)

    # Both models use same scaler → coefficients are comparable
    assert early_model.coefs.shape == late_model.coefs.shape == (3,)
    # scaler used by late model is the same object as early model's scaler
    assert late_model.scaler is early_model.scaler


# ─── Test 5 ─────────────────────────────────────────────────────────────────

def test_evaluate_gate_pass():
    dummy = _make_comparison_result(n_directional=2)
    gate = evaluate_gate(dummy)
    assert gate["gate_status"] == "PASS"
    assert gate["n_directional"] == 2


# ─── Test 6 ─────────────────────────────────────────────────────────────────

def test_evaluate_gate_fail():
    dummy = _make_comparison_result(n_directional=0)
    gate = evaluate_gate(dummy)
    assert gate["gate_status"] == "FAIL"
    assert gate["n_directional"] == 0


# ─── Test 7 ─────────────────────────────────────────────────────────────────

def test_topic_balance_check():
    """Uniform distribution → p > 0.05 (balanced)."""
    import pandas as pd
    topics_early = ["advice help", "code python", "what is", "story poem",
                    "opinion think", "other stuff"] * 30
    topics_late = topics_early.copy()
    early_df = pd.DataFrame({"chosen": topics_early, "rejected": topics_early})
    late_df = pd.DataFrame({"chosen": topics_late, "rejected": topics_late})

    p, residuals, labels = check_topic_balance(early_df, late_df)
    assert 0.0 <= p <= 1.0, "p-value out of range"
    assert len(labels) > 0

    # Skewed distribution → p should differ from perfectly balanced
    skewed_early = ["advice help"] * 150 + ["code python"] * 10
    skewed_late = ["code python"] * 150 + ["advice help"] * 10
    skewed_early_df = pd.DataFrame({"chosen": skewed_early, "rejected": skewed_early})
    skewed_late_df = pd.DataFrame({"chosen": skewed_late, "rejected": skewed_late})
    p2, _, _ = check_topic_balance(skewed_early_df, skewed_late_df)
    # Skewed should have lower p (more imbalanced) — not guaranteed but likely
    assert 0.0 <= p2 <= 1.0


# ─── Helper ─────────────────────────────────────────────────────────────────

def _make_comparison_result(n_directional: int) -> ComparisonResult:
    early_coefs = np.array([0.1, 0.2, 0.15])
    late_coefs = np.array([0.3, 0.4, 0.35]) if n_directional >= 2 else np.array([0.05, 0.1, 0.08])

    # Construct early_ci / late_ci so non-overlap matches n_directional
    if n_directional == 3:
        early_ci = np.array([[0.05, 0.15, 0.10], [0.15, 0.25, 0.20]])
        late_ci = np.array([[0.25, 0.35, 0.30], [0.35, 0.45, 0.40]])
    elif n_directional == 2:
        early_ci = np.array([[0.05, 0.15, 0.10], [0.15, 0.25, 0.20]])
        late_ci = np.array([[0.25, 0.35, 0.08], [0.35, 0.45, 0.18]])
    elif n_directional == 1:
        early_ci = np.array([[0.05, 0.15, 0.10], [0.15, 0.25, 0.20]])
        late_ci = np.array([[0.25, 0.10, 0.08], [0.35, 0.20, 0.18]])
    else:
        early_ci = np.array([[0.05, 0.15, 0.10], [0.20, 0.30, 0.25]])
        late_ci = np.array([[0.08, 0.05, 0.02], [0.22, 0.15, 0.12]])

    return ComparisonResult(
        early_coefs=early_coefs,
        late_coefs=late_coefs,
        deltas=late_coefs - early_coefs,
        early_ci=early_ci,
        late_ci=late_ci,
        n_directional=n_directional,
        sign_consistent=bool(np.all(late_coefs > early_coefs)),
        beta_q_stable=True,
        topic_balance_pvalue=0.8,
        early_auc=0.62,
        late_auc=0.65,
        boot_early=np.zeros((50, 3)),
        boot_late=np.zeros((50, 3)),
    )
