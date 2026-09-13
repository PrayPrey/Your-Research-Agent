"""
EntropyMeasure: compute H(demographic | occupation) via sliding-window co-occurrence.
"""

import logging
import re
from collections import defaultdict
from typing import Dict, FrozenSet, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EntropyMeasure:
    """Compute conditional entropy H(Demographic | Occupation) over a corpus."""

    def __init__(
        self,
        occ_lexicon: List[str],
        demo_lexicon: List[str],
        window_size: int = 10,
    ):
        self.occ_lexicon: FrozenSet[str] = frozenset(w.lower() for w in occ_lexicon)
        self.demo_lexicon: FrozenSet[str] = frozenset(w.lower() for w in demo_lexicon)
        self.window_size = window_size

    # ------------------------------------------------------------------
    # Co-occurrence counting
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace + punctuation tokenizer."""
        return re.findall(r"[a-zA-Z']+", text.lower())

    def compute_joint_counts(
        self,
        docs: List[dict],
    ) -> Dict[Tuple[str, str], int]:
        """Sliding-window scan: count (occ, demo) pairs within window_size tokens."""
        joint_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        w = self.window_size

        for doc in docs:
            text = doc.get("text", "") or ""
            tokens = self._tokenize(text)
            n = len(tokens)

            for i, tok in enumerate(tokens):
                if tok in self.occ_lexicon:
                    start = max(0, i - w)
                    end = min(n, i + w + 1)
                    for j in range(start, end):
                        if j != i and tokens[j] in self.demo_lexicon:
                            joint_counts[(tok, tokens[j])] += 1

        return dict(joint_counts)

    def joint_counts_to_arrays(
        self,
        joint_counts: Dict[Tuple[str, str], int],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Flatten joint counts to parallel integer arrays (Y=demo, X=occ).

        Each (occ, demo) pair is repeated `count` times to form empirical samples.
        """
        occ_vocab = sorted({k[0] for k in joint_counts})
        demo_vocab = sorted({k[1] for k in joint_counts})
        occ_idx = {w: i for i, w in enumerate(occ_vocab)}
        demo_idx = {w: i for i, w in enumerate(demo_vocab)}

        X_list: List[int] = []
        Y_list: List[int] = []
        for (occ, demo), count in joint_counts.items():
            xi = occ_idx[occ]
            yi = demo_idx[demo]
            X_list.extend([xi] * count)
            Y_list.extend([yi] * count)

        return np.array(Y_list, dtype=np.int32), np.array(X_list, dtype=np.int32)

    # ------------------------------------------------------------------
    # Entropy computation
    # ------------------------------------------------------------------

    def compute_conditional_entropy(self, docs: List[dict]) -> float:
        """Compute H(Demographic | Occupation) in bits via pyitlib."""
        from pyitlib import discrete_random_variable as drv

        joint_counts = self.compute_joint_counts(docs)

        if not joint_counts:
            logger.warning("No joint co-occurrence counts found; returning 0.0")
            return 0.0

        Y_arr, X_arr = self.joint_counts_to_arrays(joint_counts)

        if len(Y_arr) < 2:
            return 0.0

        try:
            h_cond = float(drv.entropy_conditional(Y_arr, X_arr))
        except Exception as exc:
            logger.error("entropy_conditional failed: %s", exc)
            h_cond = 0.0

        return h_cond

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def compute_all_entropies(
        self,
        corpora: Dict[str, List[dict]],
    ) -> Dict[str, float]:
        """Compute conditional entropy for each corpus configuration.

        Args:
            corpora: mapping config_id → list of document dicts

        Returns:
            mapping config_id → H(demo | occ) in bits
        """
        self.joint_counts_per_config: Dict[str, Dict[Tuple[str, str], int]] = {}
        entropies: Dict[str, float] = {}

        for config_id, docs in corpora.items():
            logger.info("Computing entropy for %s (%d docs)…", config_id, len(docs))
            jc = self.compute_joint_counts(docs)
            self.joint_counts_per_config[config_id] = jc

            Y_arr, X_arr = self.joint_counts_to_arrays(jc)

            if len(Y_arr) < 2:
                entropies[config_id] = 0.0
                logger.warning("%s: insufficient co-occurrences; entropy=0.0", config_id)
                continue

            from pyitlib import discrete_random_variable as drv
            try:
                h_cond = float(drv.entropy_conditional(Y_arr, X_arr))
            except Exception as exc:
                logger.error("%s: entropy_conditional failed: %s", config_id, exc)
                h_cond = 0.0

            entropies[config_id] = h_cond
            logger.info("%s: H(demo|occ) = %.4f bits", config_id, h_cond)

        return entropies
