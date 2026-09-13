"""
Log-Odds Computation for H-M1: Conditional Log-Odds Demographic-Occupation Analysis.

Computes co-occurrence-based conditional log-odds between demographic tokens
and occupation tokens across corpus configurations using sliding window approach.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class LogOddsComputer:
    """Compute conditional log-odds of demographic-occupation co-occurrences."""

    def __init__(
        self,
        occ_lexicon: List[str],
        demo_lexicon: List[str],
        window_size: int = 10,
        alpha: float = 0.5,
    ):
        self.occ_lexicon = [t.lower() for t in occ_lexicon]
        self.demo_lexicon = [t.lower() for t in demo_lexicon]
        self.window_size = window_size
        self.alpha = alpha
        self._occ_set = set(self.occ_lexicon)
        self._demo_set = set(self.demo_lexicon)

    # ------------------------------------------------------------------
    # Tokenization
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text using regex pattern matching word characters."""
        return re.findall(r"[a-zA-Z']+", text.lower())

    # ------------------------------------------------------------------
    # Co-occurrence counting
    # ------------------------------------------------------------------

    def compute_cooccurrence_counts(
        self, docs: List[dict]
    ) -> Tuple[Dict, Dict, Dict, int]:
        """
        Compute co-occurrence counts using sliding window around occupation anchors.

        For each occupation token in a document, count demographic tokens within
        ±window_size positions.

        Returns:
            cooc_demo_occ: Dict[(demo_token, occ_token), count]
            count_demo: Dict[demo_token, count]
            count_occ: Dict[occ_token, count]
            total_windows: int
        """
        cooc_demo_occ: Dict[Tuple[str, str], int] = {}
        count_demo: Dict[str, int] = {}
        count_occ: Dict[str, int] = {}
        total_windows = 0

        for doc in docs:
            text = doc.get("text", "") or ""
            if not text.strip():
                continue

            tokens = self._tokenize(text)
            n = len(tokens)

            # For each occupation anchor, scan window for demographics
            # count_demo[d] = # occ-anchor windows where demo d appeared (per spec)
            for i, tok in enumerate(tokens):
                if tok not in self._occ_set:
                    continue

                count_occ[tok] = count_occ.get(tok, 0) + 1
                total_windows += 1

                # Sliding window ±window_size
                start = max(0, i - self.window_size)
                end = min(n, i + self.window_size + 1)

                for j in range(start, end):
                    if j == i:
                        continue
                    context_tok = tokens[j]
                    if context_tok in self._demo_set:
                        key = (context_tok, tok)  # (demo, occ)
                        cooc_demo_occ[key] = cooc_demo_occ.get(key, 0) + 1
                        # count_demo[d] incremented per window occurrence (per spec pseudo-code)
                        count_demo[context_tok] = count_demo.get(context_tok, 0) + 1

        return cooc_demo_occ, count_demo, count_occ, total_windows

    # ------------------------------------------------------------------
    # Log-odds computation
    # ------------------------------------------------------------------

    def compute_log_odds_pair(
        self,
        n_demo_occ: float,
        n_demo_not_occ: float,
        n_not_demo_occ: float,
        n_not_demo_not_occ: float,
    ) -> Tuple[float, float, float]:
        """
        Compute log-odds ratio with 95% CI using statsmodels Table2x2.

        Returns:
            (log_odds, ci_low, ci_high)
        """
        from statsmodels.stats.contingency_tables import Table2x2

        a = n_demo_occ
        b = n_demo_not_occ
        c = n_not_demo_occ
        d = n_not_demo_not_occ

        try:
            t = Table2x2([[a, b], [c, d]])
            lo = t.log_oddsratio
            ci = t.log_oddsratio_confint()
            if np.isnan(lo):
                return (0.0, -np.inf, np.inf)
            return (float(lo), float(ci[0]), float(ci[1]))
        except Exception:
            return (0.0, -np.inf, np.inf)

    # ------------------------------------------------------------------
    # Matrix computation
    # ------------------------------------------------------------------

    def compute_log_odds_matrix(
        self, docs: List[dict], config_id: str
    ) -> pd.DataFrame:
        """
        Compute log-odds for all (demographic, occupation) pairs.

        Returns:
            DataFrame with columns: [demographic, occupation, log_odds, ci_low, ci_high, config_id]
        """
        if not docs:
            logger.warning("Empty docs for config %s; returning empty DataFrame", config_id)
            return pd.DataFrame(
                columns=["demographic", "occupation", "log_odds", "ci_low", "ci_high", "config_id"]
            )

        cooc, count_demo, count_occ, N = self.compute_cooccurrence_counts(docs)

        rows = []
        alpha = self.alpha

        for demo in self.demo_lexicon:
            for occ in self.occ_lexicon:
                a = cooc.get((demo, occ), 0) + alpha
                b = max(0, count_demo.get(demo, 0) - cooc.get((demo, occ), 0)) + alpha
                c = max(0, count_occ.get(occ, 0) - cooc.get((demo, occ), 0)) + alpha
                d = (
                    N
                    - count_demo.get(demo, 0)
                    - count_occ.get(occ, 0)
                    + cooc.get((demo, occ), 0)
                    + alpha
                )
                # Ensure d is non-negative
                d = max(alpha, d)

                lo, ci_low, ci_high = self.compute_log_odds_pair(a, b, c, d)
                rows.append(
                    {
                        "demographic": demo,
                        "occupation": occ,
                        "log_odds": lo,
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                        "config_id": config_id,
                    }
                )

        df = pd.DataFrame(rows)
        logger.info(
            "Computed log-odds matrix for %s: %d pairs", config_id, len(df)
        )
        return df

    def compute_all_configs(
        self, corpora: Dict[str, List[dict]]
    ) -> pd.DataFrame:
        """
        Compute log-odds matrices for all corpus configurations.

        Args:
            corpora: Dict mapping config_id to list of documents

        Returns:
            Concatenated DataFrame for all configs
        """
        dfs = []
        for config_id, docs in corpora.items():
            logger.info("Computing log-odds for config %s (%d docs)", config_id, len(docs))
            df = self.compute_log_odds_matrix(docs, config_id)
            dfs.append(df)

        if not dfs:
            return pd.DataFrame(
                columns=["demographic", "occupation", "log_odds", "ci_low", "ci_high", "config_id"]
            )

        return pd.concat(dfs, ignore_index=True)

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def aggregate_mean_log_odds(self, log_odds_df: pd.DataFrame) -> Dict[str, float]:
        """
        Compute mean log-odds per config_id.

        Returns:
            Dict mapping config_id to mean log_odds
        """
        if log_odds_df.empty:
            return {}

        result = {}
        for config_id, group in log_odds_df.groupby("config_id"):
            # Filter out infinite values for mean computation
            finite_vals = group["log_odds"].replace([np.inf, -np.inf], np.nan).dropna()
            result[str(config_id)] = float(finite_vals.mean()) if len(finite_vals) > 0 else 0.0

        return result

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_log_odds_matrix(
        self, log_odds_df: pd.DataFrame, output_path: str
    ) -> None:
        """
        Save log-odds matrix as wide-format CSV.

        Pivots to: index=(demographic, occupation), columns=config_ids
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if log_odds_df.empty:
            logger.warning("Empty log_odds_df; saving empty CSV to %s", output_path)
            pd.DataFrame().to_csv(output_path)
            return

        wide = log_odds_df.pivot_table(
            index=["demographic", "occupation"],
            columns="config_id",
            values="log_odds",
            aggfunc="first",
        )
        wide.to_csv(output_path)
        logger.info("Saved log-odds matrix to %s (shape: %s)", output_path, wide.shape)
