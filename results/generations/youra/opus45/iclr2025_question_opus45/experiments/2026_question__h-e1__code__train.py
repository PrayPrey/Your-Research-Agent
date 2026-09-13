"""Training functions for SEP and SEDP probes."""

import numpy as np

from config import ExperimentConfig
from model import SEDProbe, SEProbe


def train_sep(
    config: ExperimentConfig,
    hidden_states_train: np.ndarray,
    labels_train: np.ndarray,
) -> SEProbe:
    """Train SEP baseline probe."""
    probe = SEProbe(config)
    probe.fit(hidden_states_train, labels_train)
    return probe


def train_sedp(
    config: ExperimentConfig,
    hidden_states_train: np.ndarray,
    sim_features_train: np.ndarray,
    labels_train: np.ndarray,
) -> SEDProbe:
    """Train SEDP proposed probe."""
    probe = SEDProbe(config)
    probe.fit(hidden_states_train, sim_features_train, labels_train)
    return probe
