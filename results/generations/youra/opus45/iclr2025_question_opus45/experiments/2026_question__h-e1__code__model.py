"""Probe models: SEP (baseline) and SEDP (proposed)."""

import numpy as np
from sklearn.linear_model import LogisticRegression

from config import ExperimentConfig


class SEProbe:
    """Baseline SEP: logistic regression on hidden states only."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.clf = LogisticRegression(
            C=config.probe_C,
            max_iter=config.probe_max_iter,
            solver="lbfgs",
            random_state=config.seed,
        )

    def fit(self, hidden_states: np.ndarray, labels: np.ndarray) -> None:
        """Fit on hidden states [N, 4096]."""
        print(f"Training SEP on {hidden_states.shape[0]} samples, "
              f"{hidden_states.shape[1]} features...")
        self.clf.fit(hidden_states, labels)
        print("SEP training complete.")

    def predict_proba(self, hidden_states: np.ndarray) -> np.ndarray:
        """Returns positive class probabilities [N,]."""
        return self.clf.predict_proba(hidden_states)[:, 1]


class SEDProbe:
    """Proposed SEDP: logistic regression on hidden states + similarity features."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.clf = LogisticRegression(
            C=config.probe_C,
            max_iter=config.probe_max_iter,
            solver="lbfgs",
            random_state=config.seed,
        )

    def fit(
        self,
        hidden_states: np.ndarray,
        sim_features: np.ndarray,
        labels: np.ndarray,
    ) -> None:
        """Fit on concatenated [hidden_states || sim_features] -> [N, 4100]."""
        X = np.concatenate([hidden_states, sim_features], axis=1)
        print(f"Training SEDP on {X.shape[0]} samples, {X.shape[1]} features...")
        self.clf.fit(X, labels)
        print("SEDP training complete.")

    def predict_proba(
        self,
        hidden_states: np.ndarray,
        sim_features: np.ndarray,
    ) -> np.ndarray:
        """Returns positive class probabilities [N,]."""
        X = np.concatenate([hidden_states, sim_features], axis=1)
        return self.clf.predict_proba(X)[:, 1]
