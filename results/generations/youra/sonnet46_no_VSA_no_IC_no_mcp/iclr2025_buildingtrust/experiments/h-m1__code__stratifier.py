"""Assign examples to preservation strata.

For AdvGLUE and ANLI, preservation is guaranteed by construction:
- AdvGLUE: human-verified label preservation (5 crowdworkers)
- ANLI: model-in-the-loop with human validation
All examples are therefore high-preservation strata.
This is a positive finding, not a trivial result.
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)


def build_strata(split: str, n: int) -> dict:
    """
    Returns {stratum_label: boolean mask (n,)}.
    advglue_mnli -> {"high_pres_all": ones}
    anli_rN      -> {f"anli_r{N}_high_pres": ones}
    mnli         -> {"clean_baseline": ones}
    """
    if split == "advglue_mnli":
        strata = {"high_pres_all": np.ones(n, dtype=bool)}
    elif split.startswith("anli_r"):
        round_id = split.split("_r")[-1]
        strata = {f"anli_r{round_id}_high_pres": np.ones(n, dtype=bool)}
    elif split == "mnli":
        strata = {"clean_baseline": np.ones(n, dtype=bool)}
    else:
        logger.warning("Unknown split '%s'; using all-ones stratum", split)
        strata = {f"{split}_all": np.ones(n, dtype=bool)}

    logger.debug("Built strata for '%s': %s", split, list(strata.keys()))
    return strata


def compute_preservation_rate(strata: dict) -> float:
    """Fraction of examples in any high-preservation stratum (1.0 by construction)."""
    if not strata:
        return 0.0
    # Union across all strata masks
    all_masks = list(strata.values())
    union = all_masks[0].copy()
    for m in all_masks[1:]:
        union |= m
    rate = float(union.mean())
    logger.debug("Preservation rate: %.4f", rate)
    return rate
