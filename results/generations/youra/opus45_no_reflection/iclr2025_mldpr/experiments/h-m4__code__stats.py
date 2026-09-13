# H-M4 Statistics: Chi-square test for independence

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from config import TRADITIONAL_BENCHMARKS


def chi_square_test(stats: dict) -> tuple[float, float]:
    """Chi-square test for traditional vs emergent paper distribution.

    Tests H0: paper distribution is independent of benchmark category.
    Rejection suggests significant difference in paper allocation.
    """
    # Contingency table: [traditional, emergent] vs [papers, non-papers]
    # We'll use expected uniform distribution as comparison
    traditional = stats["traditional_papers"]
    emergent = stats["emergent_papers"]
    total = stats["total_papers"]

    if traditional == 0 or emergent == 0:
        return 0.0, 1.0

    # Create observed vs expected comparison
    observed = np.array([[traditional, total - traditional],
                         [emergent, total - emergent]])

    try:
        chi2, p_value, dof, expected = chi2_contingency(observed)
        return float(chi2), float(p_value)
    except Exception:
        return 0.0, 1.0


def compute_dominance_metrics(df: pd.DataFrame) -> dict:
    """Compute additional dominance metrics."""
    traditional_mask = df["category"] == "traditional"
    emergent_mask = df["category"] == "emergent"

    trad_datasets = (traditional_mask).sum()
    emerg_datasets = (emergent_mask).sum()

    trad_avg_papers = df[traditional_mask]["paper_count"].mean() if trad_datasets > 0 else 0
    emerg_avg_papers = df[emergent_mask]["paper_count"].mean() if emerg_datasets > 0 else 0

    return {
        "traditional_datasets": int(trad_datasets),
        "emergent_datasets": int(emerg_datasets),
        "traditional_avg_papers": float(trad_avg_papers),
        "emergent_avg_papers": float(emerg_avg_papers),
    }
