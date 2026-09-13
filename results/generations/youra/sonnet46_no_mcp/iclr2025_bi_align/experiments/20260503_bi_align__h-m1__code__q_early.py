import logging
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
from config import LR_PARAMS, BRIER_GATE_THRESHOLD

logger = logging.getLogger(__name__)


class QEarlyModel:
    """Logistic regression quality control model trained on round-1 data."""

    def __init__(self) -> None:
        self.base_lr = LogisticRegression(**LR_PARAMS)
        self.calibrated = None
        self._fitted = False

    def fit(self, X_r1: np.ndarray, y_r1: np.ndarray) -> None:
        """Train base LR on round-1 features."""
        logger.info(f"Fitting QEarlyModel on {len(X_r1)} round-1 samples")
        self.base_lr.fit(X_r1, y_r1)
        self._fitted = True
        logger.info("QEarlyModel base LR fitted")

    def calibrate(self, X: np.ndarray, y: np.ndarray) -> None:
        """Platt-scale calibration on held-out data."""
        if not self._fitted:
            raise RuntimeError("Call fit() before calibrate()")
        logger.info(f"Calibrating QEarlyModel on {len(X)} samples")
        self.calibrated = CalibratedClassifierCV(
            self.base_lr, method="sigmoid", cv="prefit"
        )
        self.calibrated.fit(X, y)
        logger.info("QEarlyModel calibration done")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return calibrated probabilities [N, 2]."""
        if self.calibrated is not None:
            return self.calibrated.predict_proba(X)
        if self._fitted:
            return self.base_lr.predict_proba(X)
        raise RuntimeError("Model not fitted")

    def brier_score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute Brier score."""
        proba = self.predict_proba(X)[:, 1]
        score = brier_score_loss(y, proba)
        logger.info(f"Brier score: {score:.4f}")
        return float(score)

    def gate_check(self, brier_r1: float, brier_r2: float) -> bool:
        """Returns True if |brier_r2 - brier_r1| < BRIER_GATE_THRESHOLD."""
        diff = abs(brier_r2 - brier_r1)
        logger.info(f"Brier gate check: diff={diff:.4f}, threshold={BRIER_GATE_THRESHOLD}")
        if diff >= BRIER_GATE_THRESHOLD:
            raise RuntimeError(
                f"Q_early Brier gate FAILED: diff={diff:.4f} >= {BRIER_GATE_THRESHOLD}"
            )
        return True
