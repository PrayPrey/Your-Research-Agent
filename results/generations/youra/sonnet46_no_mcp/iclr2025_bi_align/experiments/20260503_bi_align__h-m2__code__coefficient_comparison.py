"""H-M2 core module: round-stratified logistic regression coefficient comparison."""
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from config import (
    BETA_Q_STABILITY_THRESHOLD,
    BOOTSTRAP_ITERS,
    LR_PARAMS,
    N_DIRECTIONAL_GATE,
    RANDOM_SEED,
    ROUND_SIZE_MIN,
    TEST_SIZE,
    TOPIC_BALANCE_ALPHA,
)

log = logging.getLogger(__name__)

# q_early_model is set by run_experiment.py before calling functions here
_q_early_model = None


def set_q_early_model(model) -> None:
    global _q_early_model
    _q_early_model = model


def _get_q_scores(X: np.ndarray) -> np.ndarray:
    """Return q_early scores as [N, 1] column."""
    return _q_early_model.predict_proba(X)[:, 1:2]


@dataclass
class RoundSplit:
    X_train: np.ndarray
    y_train: np.ndarray
    q_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    q_test: np.ndarray
    round_id: int


@dataclass
class RoundModel:
    clf: LogisticRegression
    scaler: StandardScaler
    coefs: np.ndarray   # (3,) = [β_L, β_H, β_S]
    beta_q: float
    auc: float


@dataclass
class ComparisonResult:
    early_coefs: np.ndarray
    late_coefs: np.ndarray
    deltas: np.ndarray
    early_ci: np.ndarray    # (2, 3)
    late_ci: np.ndarray     # (2, 3)
    n_directional: int
    sign_consistent: bool
    beta_q_stable: bool
    topic_balance_pvalue: float
    early_auc: float
    late_auc: float
    boot_early: np.ndarray  # (n_resamples, 3)
    boot_late: np.ndarray   # (n_resamples, 3)


def _text_stylistic_features(text: str) -> np.ndarray:
    """Extract raw stylistic features from a single response text. Returns [3,]."""
    words = text.split()
    n_words = len(words)
    hedge_words = [
        "i think", "i believe", "perhaps", "possibly", "might", "may",
        "could", "probably", "seems", "appears", "arguably", "likely",
    ]
    struct_markers = ["\n-", "\n*", "1.", "2.", "##", "**", "first,", "second,"]
    text_lower = text.lower()
    hedge = sum(text_lower.count(w) for w in hedge_words)
    struct = sum(text_lower.count(m) for m in struct_markers)
    return np.array([n_words, hedge, struct], dtype=np.float32)


def _extract_raw_features(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Extract raw stylistic features [2N, 3] and binary labels [2N,] from pairwise df.

    Each row produces two samples:
      - chosen response features → label=1 (preferred)
      - rejected response features → label=0 (not preferred)
    This ensures both classes are present for logistic regression.
    """
    feat_list = []
    label_list = []
    for _, row in df.iterrows():
        chosen = str(row.get("chosen", ""))
        rejected = str(row.get("rejected", ""))
        if not chosen or not rejected:
            continue
        feat_list.append(_text_stylistic_features(chosen))
        label_list.append(1)
        feat_list.append(_text_stylistic_features(rejected))
        label_list.append(0)

    if not feat_list:
        return np.zeros((0, 3)), np.zeros(0, dtype=np.int32)
    return np.array(feat_list, dtype=np.float32), np.array(label_list, dtype=np.int32)


def prepare_round_splits(
    df: pd.DataFrame,
    q_early_model,
    round_size: int,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_SEED,
) -> Tuple[RoundSplit, RoundSplit]:
    """Extract early/late subsets, hold out 25% each, return RoundSplit pair."""
    set_q_early_model(q_early_model)

    n_total = len(df)
    rs = n_total // 3
    if rs < ROUND_SIZE_MIN:
        log.warning("Round size %d < ROUND_SIZE_MIN %d", rs, ROUND_SIZE_MIN)

    early_df = df.iloc[0:rs].reset_index(drop=True)
    late_df = df.iloc[2 * rs:].reset_index(drop=True)

    splits = []
    for round_id, rdf in [(1, early_df), (3, late_df)]:
        X_raw, y = _extract_raw_features(rdf)
        if len(X_raw) == 0:
            raise ValueError(f"No features extracted for round {round_id}")
        q = q_early_model.predict_proba(X_raw)[:, 1]

        idx = np.arange(len(X_raw))
        tr_idx, te_idx = train_test_split(
            idx, test_size=test_size, random_state=random_state, stratify=y
        )
        splits.append(RoundSplit(
            X_train=X_raw[tr_idx],
            y_train=y[tr_idx],
            q_train=q[tr_idx],
            X_test=X_raw[te_idx],
            y_test=y[te_idx],
            q_test=q[te_idx],
            round_id=round_id,
        ))

    return splits[0], splits[1]


def check_topic_balance(
    early_df: pd.DataFrame,
    late_df: pd.DataFrame,
) -> Tuple[float, np.ndarray, list]:
    """Chi-square test on prompt topic distributions; return (p-value, residuals, labels)."""
    topic_keywords = {
        "advice": ["advice", "help", "suggest", "recommend", "should i"],
        "coding": ["code", "python", "function", "program", "bug", "error"],
        "factual": ["what is", "who is", "when", "where", "how many", "define"],
        "creative": ["story", "poem", "write", "imagine", "fiction", "creative"],
        "opinion": ["think", "believe", "opinion", "view", "feel", "perspective"],
        "other": [],
    }
    topic_labels = list(topic_keywords.keys())

    def categorize(text: str) -> int:
        text_lower = text.lower()
        for i, (_, kws) in enumerate(list(topic_keywords.items())[:-1]):
            if any(k in text_lower for k in kws):
                return i
        return len(topic_labels) - 1

    def count_topics(rdf: pd.DataFrame) -> np.ndarray:
        counts = np.zeros(len(topic_labels), dtype=int)
        for _, row in rdf.iterrows():
            text = str(row.get("chosen", ""))[:200]
            counts[categorize(text)] += 1
        return counts

    early_counts = count_topics(early_df)
    late_counts = count_topics(late_df)

    contingency = np.vstack([early_counts, late_counts])
    # add 1 to avoid zero-count columns
    contingency = contingency + 1
    chi2, p, _, expected = chi2_contingency(contingency)
    residuals = (contingency - expected) / np.sqrt(expected)

    if p < TOPIC_BALANCE_ALPHA:
        log.warning("Topic balance check: chi2=%.3f, p=%.3f — WARNING: imbalanced", chi2, p)
    else:
        log.info("Topic balance check: chi2=%.3f, p=%.3f — balanced", chi2, p)

    return p, residuals[0] - residuals[1], topic_labels


def fit_round_predictor(
    split: RoundSplit,
    shared_scaler: Optional[StandardScaler] = None,
) -> RoundModel:
    """Fit LR on split.X_train + q_train. shared_scaler=None → fit new scaler."""
    X_raw = split.X_train  # [N, 3]

    if shared_scaler is None:
        scaler = StandardScaler().fit(X_raw)
    else:
        scaler = shared_scaler

    X_scaled = scaler.transform(X_raw)  # [N, 3]
    q_scores = _q_early_model.predict_proba(X_raw)[:, 1:2]  # [N, 1]
    X_aug = np.hstack([X_scaled, q_scores])  # [N, 4]

    clf = LogisticRegression(**LR_PARAMS).fit(X_aug, split.y_train)
    coefs = clf.coef_[0]  # [4,]

    # AUC on test split
    X_test_scaled = scaler.transform(split.X_test)
    q_test = _q_early_model.predict_proba(split.X_test)[:, 1:2]
    X_aug_test = np.hstack([X_test_scaled, q_test])
    auc = roc_auc_score(split.y_test, clf.predict_proba(X_aug_test)[:, 1])

    return RoundModel(clf=clf, scaler=scaler, coefs=coefs[:3], beta_q=float(coefs[3]), auc=auc)


def bootstrap_ci(
    split: RoundSplit,
    shared_scaler: StandardScaler,
    n_resamples: int = BOOTSTRAP_ITERS,
    random_state: int = RANDOM_SEED,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Stratified bootstrap; return (ci_low, ci_high, boot_coefs) shapes (3,),(3,),(n,3)."""
    rng = np.random.default_rng(random_state)
    pos_idx = np.where(split.y_train == 1)[0]
    neg_idx = np.where(split.y_train == 0)[0]

    # If all same class, use plain resampling
    if len(pos_idx) == 0 or len(neg_idx) == 0:
        all_idx = np.arange(len(split.y_train))
        pos_idx = all_idx
        neg_idx = all_idx

    boot_coefs = np.zeros((n_resamples, 3))
    for i in range(n_resamples):
        idx = np.concatenate([
            rng.choice(pos_idx, len(pos_idx), replace=True),
            rng.choice(neg_idx, len(neg_idx), replace=True),
        ])
        X_b = shared_scaler.transform(split.X_train[idx])      # [N, 3]
        q_b = _q_early_model.predict_proba(split.X_train[idx])[:, 1:2]  # [N, 1]
        X_aug = np.hstack([X_b, q_b])                           # [N, 4]
        y_b = split.y_train[idx]
        try:
            lr = LogisticRegression(**LR_PARAMS).fit(X_aug, y_b)
            boot_coefs[i] = lr.coef_[0, :3]
        except Exception:
            boot_coefs[i] = np.zeros(3)

    ci_low = np.percentile(boot_coefs, 2.5, axis=0)   # (3,)
    ci_high = np.percentile(boot_coefs, 97.5, axis=0)  # (3,)
    return ci_low, ci_high, boot_coefs


def compare_coefficients(
    early_model: RoundModel,
    late_model: RoundModel,
    early_split: RoundSplit,
    late_split: RoundSplit,
    shared_scaler: StandardScaler,
    topic_balance_pvalue: float = 1.0,
    n_resamples: int = BOOTSTRAP_ITERS,
    random_state: int = RANDOM_SEED,
) -> ComparisonResult:
    """Run bootstrap CIs, compute deltas, n_directional, sign consistency."""
    e_low, e_high, boot_early = bootstrap_ci(early_split, shared_scaler, n_resamples, random_state)
    l_low, l_high, boot_late = bootstrap_ci(late_split, shared_scaler, n_resamples, random_state + 1)

    early_ci = np.stack([e_low, e_high])  # (2, 3)
    late_ci = np.stack([l_low, l_high])   # (2, 3)

    deltas = late_model.coefs - early_model.coefs  # (3,)
    sign_consistent = bool(np.all(deltas > 0))
    beta_q_stable = bool(abs(late_model.beta_q - early_model.beta_q) < BETA_Q_STABILITY_THRESHOLD)

    if not beta_q_stable:
        log.warning(
            "Q_early coefficient unstable across rounds (Δ=%.4f) — A2 assumption may be violated",
            abs(late_model.beta_q - early_model.beta_q),
        )

    n_directional = sum(int(early_ci[1, j] < late_ci[0, j]) for j in range(3))

    if not sign_consistent:
        feat_names = ["β_L", "β_H", "β_S"]
        for j, name in enumerate(feat_names):
            if deltas[j] <= 0:
                log.warning("Sign inconsistency: feature %s delta=%.4f < 0 — consider PIVOT", name, deltas[j])

    return ComparisonResult(
        early_coefs=early_model.coefs,
        late_coefs=late_model.coefs,
        deltas=deltas,
        early_ci=early_ci,
        late_ci=late_ci,
        n_directional=n_directional,
        sign_consistent=sign_consistent,
        beta_q_stable=beta_q_stable,
        topic_balance_pvalue=topic_balance_pvalue,
        early_auc=early_model.auc,
        late_auc=late_model.auc,
        boot_early=boot_early,
        boot_late=boot_late,
    )


def check_cross_round_held_out(
    early_model: RoundModel,
    late_model: RoundModel,
    X_test: np.ndarray,
    y_test: np.ndarray,
    q_test: np.ndarray,
    shared_scaler: StandardScaler,
    ambiguity_threshold: float = 0.1,
) -> Dict:
    """Evaluate both models on shared held-out set, compute high-ambiguity pref rate."""
    X_scaled = shared_scaler.transform(X_test)
    q_col = q_test[:, None] if q_test.ndim == 1 else q_test
    X_aug = np.hstack([X_scaled, q_col])

    early_proba = early_model.clf.predict_proba(X_aug)[:, 1]
    late_proba = late_model.clf.predict_proba(X_aug)[:, 1]

    early_auc = roc_auc_score(y_test, early_proba)
    late_auc = roc_auc_score(y_test, late_proba)

    # High-ambiguity proxy: |q_score - 0.5| < ambiguity_threshold
    q_scores_1d = q_test if q_test.ndim == 1 else q_test[:, 0]
    high_ambiguity_mask = np.abs(q_scores_1d - 0.5) < ambiguity_threshold
    n_high_ambiguity = int(high_ambiguity_mask.sum())

    if n_high_ambiguity > 0:
        longer_pref_rate = float(np.mean(late_proba[high_ambiguity_mask] > early_proba[high_ambiguity_mask]))
    else:
        longer_pref_rate = 0.0

    passed_held_out = longer_pref_rate >= 0.60

    log.info(
        "Held-out AUC: early=%.4f, late=%.4f, longer_pref_rate=%.3f (n_high_amb=%d)",
        early_auc, late_auc, longer_pref_rate, n_high_ambiguity,
    )

    return {
        "early_auc": early_auc,
        "late_auc": late_auc,
        "longer_pref_rate": longer_pref_rate,
        "n_high_ambiguity": n_high_ambiguity,
        "passed_held_out": passed_held_out,
    }


def fit_auxiliary_round2_model(
    df: pd.DataFrame,
    q_early_model,
    shared_scaler: StandardScaler,
    round_size: int,
    random_state: int = RANDOM_SEED,
) -> RoundModel:
    """Fit auxiliary round-2 model for monotonicity check."""
    set_q_early_model(q_early_model)
    n_total = len(df)
    rs = n_total // 3
    mid_df = df.iloc[rs: 2 * rs].reset_index(drop=True)
    X_raw, y = _extract_raw_features(mid_df)

    if len(X_raw) == 0:
        raise ValueError("No features for round-2 auxiliary model")

    q = q_early_model.predict_proba(X_raw)[:, 1]
    idx = np.arange(len(X_raw))
    tr_idx, te_idx = train_test_split(idx, test_size=0.25, random_state=random_state, stratify=y)

    split = RoundSplit(
        X_train=X_raw[tr_idx], y_train=y[tr_idx], q_train=q[tr_idx],
        X_test=X_raw[te_idx], y_test=y[te_idx], q_test=q[te_idx],
        round_id=2,
    )
    return fit_round_predictor(split, shared_scaler=shared_scaler)


def evaluate_gate(result: ComparisonResult) -> Dict:
    """PASS if n_directional >= 2, PARTIAL if == 1, FAIL if == 0."""
    n = result.n_directional
    if n >= N_DIRECTIONAL_GATE:
        gate_status = "PASS"
    elif n == 1:
        gate_status = "PARTIAL"
    else:
        gate_status = "FAIL"

    feat_names = ["β_L", "β_H", "β_S"]
    e = result.early_coefs
    l = result.late_coefs
    d = result.deltas
    log.info(
        "Coefficient comparison: β_L=[%.4f,%.4f] δ=%.4f; β_H=[%.4f,%.4f] δ=%.4f; "
        "β_S=[%.4f,%.4f] δ=%.4f; n_directional=%d/3",
        e[0], l[0], d[0], e[1], l[1], d[1], e[2], l[2], d[2], n,
    )

    if gate_status in ("PARTIAL", "FAIL"):
        confirmed = [feat_names[j] for j in range(3) if result.early_ci[1, j] < result.late_ci[0, j]]
        log.info("PIVOT: document feature-level results; continue H-M3 with reduced scope.")
        log.info("Confirmed directional features: %s", confirmed)

    return {
        "gate_status": gate_status,
        "n_directional": n,
        "sign_consistent": result.sign_consistent,
        "beta_q_stable": result.beta_q_stable,
        "topic_balance_pvalue": result.topic_balance_pvalue,
    }
