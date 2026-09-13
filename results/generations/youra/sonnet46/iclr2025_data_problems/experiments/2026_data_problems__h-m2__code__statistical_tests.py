"""H-M2 Statistical Tests: Spearman gate, log-linear OLS, negative control."""
import json
import logging
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

from config import HM2Config, ALL_CONFIGS, CORPUS_H_ENTROPY, load_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class StatisticalTests:
    """Statistical testing suite for H-M2 hypothesis validation."""

    def __init__(
        self,
        n_bootstrap: int = 1000,
        seed: int = 42,
        alpha_level: float = 0.01,
        negative_control_threshold: float = 0.01,
    ):
        self.n_bootstrap = n_bootstrap
        self.seed = seed
        self.alpha_level = alpha_level
        self.negative_control_threshold = negative_control_threshold
        self.rng = np.random.default_rng(seed)

    def spearman_correlation(
        self,
        x: List[float],
        y: List[float],
    ) -> Tuple[float, float]:
        """Compute Spearman rank correlation.

        Args:
            x: Corpus entropy values (C0-C6, excludes C7)
            y: Model logit margins (C0-C6, excludes C7)

        Returns:
            Tuple of (rho, pvalue)
        """
        rho, pvalue = stats.spearmanr(x, y)
        return float(rho), float(pvalue)

    def bootstrap_spearman_ci(
        self,
        x: List[float],
        y: List[float],
        confidence: float = 0.95,
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI for Spearman rho.

        Args:
            x: Entropy values
            y: Logit margins
            confidence: Confidence level

        Returns:
            Tuple of (lower, upper) CI bounds
        """
        x_arr = np.array(x)
        y_arr = np.array(y)
        n = len(x)
        bootstrap_rhos = []

        for _ in range(self.n_bootstrap):
            idx = self.rng.integers(0, n, size=n)
            rho, _ = stats.spearmanr(x_arr[idx], y_arr[idx])
            bootstrap_rhos.append(rho)

        alpha = 1 - confidence
        lower = float(np.percentile(bootstrap_rhos, 100 * alpha / 2))
        upper = float(np.percentile(bootstrap_rhos, 100 * (1 - alpha / 2)))
        return lower, upper

    def log_linear_ols(
        self,
        entropy_values: List[float],
        logit_margins: List[float],
    ) -> Dict:
        """OLS regression: logit_margin ~ log(H_entropy).

        Args:
            entropy_values: Corpus entropy H(occ|demo) values (C0-C6)
            logit_margins: Model logit margins (C0-C6)

        Returns:
            Dict with coef, intercept, r_squared, pvalue, stderr
        """
        from scipy.stats import linregress
        x = [math.log(h) for h in entropy_values]
        y = logit_margins
        slope, intercept, r_value, pvalue, stderr = linregress(x, y)
        r_squared = r_value ** 2
        return {
            "coef": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "pvalue": float(pvalue),
            "stderr": float(stderr),
            "meets_r2_criterion": r_squared > 0.3,
        }

    def negative_control_delta(
        self,
        margin_c7: float,
        margin_c0: float,
    ) -> Dict:
        """Compute |margin(C7) - margin(C0)| and check threshold.

        Args:
            margin_c7: Logit margin for C7 (shuffled-demographic)
            margin_c0: Logit margin for C0 (unfiltered baseline)

        Returns:
            Dict with delta, passes, threshold
        """
        delta = abs(margin_c7 - margin_c0)
        passes = delta <= self.negative_control_threshold
        return {
            "delta": float(delta),
            "passes": passes,
            "threshold": self.negative_control_threshold,
            "margin_c7": float(margin_c7),
            "margin_c0": float(margin_c0),
        }

    def evaluate_gate(
        self,
        spearman_rho: float,
        spearman_pvalue: float,
    ) -> Dict:
        """Evaluate SHOULD_WORK gate: rho > 0 AND p < alpha_level.

        Args:
            spearman_rho: Spearman correlation coefficient
            spearman_pvalue: P-value from Spearman test

        Returns:
            Dict with gate_pass, rho, pvalue, reason
        """
        rho_pass = spearman_rho > 0
        p_pass = spearman_pvalue < self.alpha_level

        gate_pass = rho_pass and p_pass

        reasons = []
        if not rho_pass:
            reasons.append(f"rho={spearman_rho:.4f} <= 0 (expected positive)")
        if not p_pass:
            reasons.append(f"p={spearman_pvalue:.4f} >= {self.alpha_level} (not significant)")

        return {
            "gate_pass": gate_pass,
            "rho": float(spearman_rho),
            "pvalue": float(spearman_pvalue),
            "alpha_level": self.alpha_level,
            "reason": "; ".join(reasons) if reasons else "PASS: rho > 0 and p < alpha",
        }

    def run_all_tests(
        self,
        probe_results: Dict[str, Dict],
    ) -> Dict:
        """Orchestrate all statistical tests for H-M2.

        Args:
            probe_results: Dict mapping config_id -> probe result dict
                           (must contain 'mean_logit_margin' key)

        Returns:
            Full test results dict
        """
        # Configs for main analysis (exclude C7 negative control)
        main_configs = [c for c in ALL_CONFIGS if c != "C7"]

        # Build aligned arrays
        entropy_values = []
        logit_margins = []
        configs_used = []

        for config_id in main_configs:
            if config_id not in probe_results:
                logger.warning(f"[stats] {config_id} missing from probe results — skipping")
                continue
            margin = probe_results[config_id].get("mean_logit_margin")
            if margin is None:
                logger.warning(f"[stats] {config_id} has None margin — skipping")
                continue
            entropy_values.append(CORPUS_H_ENTROPY[config_id])
            logit_margins.append(float(margin))
            configs_used.append(config_id)

        if len(configs_used) < 3:
            logger.error(f"[stats] Insufficient data: only {len(configs_used)} configs")
            return {"error": "insufficient_data", "configs_used": configs_used}

        logger.info(f"[stats] Running tests on configs: {configs_used}")

        # 1. Spearman correlation
        rho, pvalue = self.spearman_correlation(entropy_values, logit_margins)
        ci_lower, ci_upper = self.bootstrap_spearman_ci(entropy_values, logit_margins)
        logger.info(f"[stats] Spearman rho={rho:.4f}, p={pvalue:.4f}, CI=[{ci_lower:.4f},{ci_upper:.4f}]")

        # 2. Gate evaluation
        gate_result = self.evaluate_gate(rho, pvalue)
        logger.info(f"[stats] Gate: {'PASS' if gate_result['gate_pass'] else 'FAIL'} — {gate_result['reason']}")

        # 3. Log-linear OLS
        ols_result = self.log_linear_ols(entropy_values, logit_margins)
        logger.info(f"[stats] OLS: coef={ols_result['coef']:.4f}, R²={ols_result['r_squared']:.4f}")

        # 4. Negative control (C7 vs C0)
        neg_ctrl = None
        if "C7" in probe_results and probe_results["C7"].get("mean_logit_margin") is not None:
            if "C0" in probe_results and probe_results["C0"].get("mean_logit_margin") is not None:
                neg_ctrl = self.negative_control_delta(
                    margin_c7=probe_results["C7"]["mean_logit_margin"],
                    margin_c0=probe_results["C0"]["mean_logit_margin"],
                )
                logger.info(
                    f"[stats] Negative control delta={neg_ctrl['delta']:.4f}, "
                    f"passes={neg_ctrl['passes']}"
                )

        return {
            "configs_used": configs_used,
            "entropy_values": entropy_values,
            "logit_margins": logit_margins,
            "spearman": {
                "rho": rho,
                "pvalue": pvalue,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
            },
            "gate": gate_result,
            "ols": ols_result,
            "negative_control": neg_ctrl,
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-results", type=str, required=True)
    parser.add_argument("--config", type=str, default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    with open(args.probe_results) as f:
        probe_results = json.load(f)

    tester = StatisticalTests(
        n_bootstrap=cfg.n_bootstrap,
        seed=cfg.seed,
        alpha_level=cfg.alpha_level,
        negative_control_threshold=cfg.negative_control_delta_threshold,
    )
    results = tester.run_all_tests(probe_results)
    print(json.dumps(results, indent=2, default=str))
