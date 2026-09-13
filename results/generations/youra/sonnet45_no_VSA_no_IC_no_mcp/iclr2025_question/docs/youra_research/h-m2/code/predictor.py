"""Bayesian predictors for Gate 1 and Gate 2."""

import numpy as np


class Gate1Predictor:
    """Baseline predictor from H-M1 (linear extrapolation)."""

    def __init__(self, k: float = 1.000, prior_variance: float = 0.01):
        """Initialize with scaling factor k and prior uncertainty."""
        self.k = k
        self.prior_var = prior_variance

    def predict(self, O_10: float) -> tuple[float, float]:
        """Linear extrapolation. Returns (prior_mean, prior_variance)."""
        prior_mean = self.k * O_10
        return prior_mean, self.prior_var


class Gate2BayesianPredictor:
    """Bayesian posterior predictor combining Gate 1 prior + Gate 2 likelihood."""

    def __init__(self, k: float = 1.000, prior_var: float = 0.02, likelihood_var: float = 0.002):
        """Initialize with scaling and variance parameters."""
        self.k = k
        self.prior_var = prior_var
        self.likelihood_var = likelihood_var

    def predict(self, O_10: float, O_100: float) -> tuple[float, float]:
        """
        Bayesian update combining prior and likelihood.
        Returns (posterior_mean, posterior_variance).
        """
        prior_mean, prior_var = self._gate1_prior(O_10)
        likelihood_mean = O_100 / self.k  # Inverse scaling

        posterior_mean, posterior_var = self._bayesian_update(
            prior_mean, prior_var,
            likelihood_mean, self.likelihood_var
        )
        return posterior_mean, posterior_var

    def _gate1_prior(self, O_10: float) -> tuple[float, float]:
        """Compute Gate 1 prior. Returns (prior_mean, prior_variance)."""
        return self.k * O_10, self.prior_var

    def _bayesian_update(
        self,
        prior_mean: float,
        prior_var: float,
        likelihood_mean: float,
        likelihood_var: float
    ) -> tuple[float, float]:
        """
        Gaussian-Gaussian conjugate update.
        posterior_var = 1 / (1/prior_var + 1/likelihood_var)
        posterior_mean = posterior_var * (prior_mean/prior_var + likelihood_mean/likelihood_var)
        """
        posterior_var = 1.0 / (1.0 / prior_var + 1.0 / likelihood_var)
        posterior_mean = posterior_var * (prior_mean / prior_var + likelihood_mean / likelihood_var)
        return posterior_mean, posterior_var
