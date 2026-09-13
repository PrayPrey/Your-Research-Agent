"""H-E1 Bridge: Re-exports H-E1 functions after sys.path is configured by config.py."""

# Import config first to set up sys.path with H-E1 code directory
import config  # noqa: F401 - triggers sys.path insertion

# Now import from H-E1 analyze.py (available via sys.path)
from analyze import (
    extract_b_matrices,
    compute_pairwise_matrix,
    grassmann_distance,
    compute_orthonormal_basis,
    split_within_between,
    _bootstrap_ci,
)

__all__ = [
    "extract_b_matrices",
    "compute_pairwise_matrix",
    "grassmann_distance",
    "compute_orthonormal_basis",
    "split_within_between",
    "_bootstrap_ci",
]
