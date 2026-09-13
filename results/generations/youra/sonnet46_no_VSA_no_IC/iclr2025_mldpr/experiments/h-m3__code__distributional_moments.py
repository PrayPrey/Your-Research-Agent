from dataclasses import dataclass
from typing import Tuple
import numpy as np
from scipy.stats import describe as scipy_describe


@dataclass
class SegmentMoments:
    n: int
    mean: float
    variance: float
    skewness: float
    kurtosis: float
    p10: float
    p25: float
    p75: float


def compute_moments(segment: np.ndarray) -> SegmentMoments:
    desc = scipy_describe(segment, bias=False)
    return SegmentMoments(
        n=int(desc.nobs),
        mean=float(desc.mean),
        variance=float(desc.variance),
        skewness=float(desc.skewness),
        kurtosis=float(desc.kurtosis),
        p10=float(np.percentile(segment, 10)),
        p25=float(np.percentile(segment, 25)),
        p75=float(np.percentile(segment, 75)),
    )


def compute_both_segments(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    breakpoint_idx: int,
) -> Tuple[SegmentMoments, SegmentMoments, np.ndarray, np.ndarray]:
    pre_arr = residual_cov[:breakpoint_idx]
    post_arr = residual_cov[breakpoint_idx:]
    assert len(pre_arr) + len(post_arr) == len(residual_cov), "Segment split mismatch"
    pre_moments = compute_moments(pre_arr)
    post_moments = compute_moments(post_arr)
    print(f"Segments: n_pre={pre_moments.n}, n_post={post_moments.n}")
    print(f"Pre  moments: mean={pre_moments.mean:.4f}, var={pre_moments.variance:.6f}, "
          f"skew={pre_moments.skewness:.4f}, kurt={pre_moments.kurtosis:.4f}")
    print(f"Post moments: mean={post_moments.mean:.4f}, var={post_moments.variance:.6f}, "
          f"skew={post_moments.skewness:.4f}, kurt={post_moments.kurtosis:.4f}")
    return pre_moments, post_moments, pre_arr, post_arr
