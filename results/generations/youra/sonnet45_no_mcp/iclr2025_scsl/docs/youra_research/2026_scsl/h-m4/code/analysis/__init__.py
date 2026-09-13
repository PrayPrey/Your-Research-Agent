"""Analysis module for correlation and statistical tests"""

from .correlation import compute_spearman_correlation
from .results_aggregator import ResultsAggregator, CouplingResults

__all__ = [
    'compute_spearman_correlation',
    'ResultsAggregator',
    'CouplingResults'
]
