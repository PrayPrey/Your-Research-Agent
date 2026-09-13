from dataclasses import dataclass
import numpy as np
from scipy.stats import permutation_test, mannwhitneyu, skew as scipy_skew

from distributional_moments import SegmentMoments


@dataclass
class DirectionalTestResults:
    skew_pre: float
    skew_post: float
    metric1_pass: bool
    p10_pre: float
    p10_post: float
    metric2_pass: bool
    perm_p_skew_diff: float
    metric3_pass: bool
    mw_pvalue: float
    mw_statistic: float
    metric4_pass: bool


def _skew_diff_stat(x: np.ndarray, y: np.ndarray, axis: int = 0) -> float:
    return scipy_skew(y, axis=axis, bias=False) - scipy_skew(x, axis=axis, bias=False)


def _run_permutation_test(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    n_resamples: int = 9999,
    random_state: int = 42,
) -> float:
    result = permutation_test(
        data=(pre_segment, post_segment),
        statistic=_skew_diff_stat,
        permutation_type='independent',
        vectorized=True,
        n_resamples=n_resamples,
        alternative='two-sided',
        random_state=random_state,
    )
    return float(result.pvalue)


def run_directional_tests(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    n_resamples: int = 9999,
    random_state: int = 42,
    p_threshold: float = 0.10,
) -> DirectionalTestResults:
    skew_pre = pre_moments.skewness
    skew_post = post_moments.skewness
    metric1_pass = bool((skew_post < skew_pre) or (skew_post < 0.0))
    print(f"Metric 1 (skewness direction): skew_pre={skew_pre:.4f}, "
          f"skew_post={skew_post:.4f}, pass={metric1_pass}")

    p10_pre = pre_moments.p10
    p10_post = post_moments.p10
    metric2_pass = bool(p10_post < p10_pre)
    print(f"Metric 2 (lower tail): p10_pre={p10_pre:.4f}, p10_post={p10_post:.4f}, "
          f"pass={metric2_pass}")

    perm_p = _run_permutation_test(pre_segment, post_segment, n_resamples, random_state)
    metric3_pass = bool(perm_p < p_threshold)
    print(f"Metric 3 (perm test skewness diff): p={perm_p:.4f}, pass={metric3_pass}")

    mw_result = mannwhitneyu(
        pre_segment,
        post_segment,
        alternative='greater',
        method='auto',
    )
    metric4_pass = bool(mw_result.pvalue < p_threshold)
    print(f"Metric 4 (Mann-Whitney, pre>post): p={mw_result.pvalue:.4f}, "
          f"statistic={mw_result.statistic:.1f}, pass={metric4_pass}")

    return DirectionalTestResults(
        skew_pre=skew_pre,
        skew_post=skew_post,
        metric1_pass=metric1_pass,
        p10_pre=p10_pre,
        p10_post=p10_post,
        metric2_pass=metric2_pass,
        perm_p_skew_diff=perm_p,
        metric3_pass=metric3_pass,
        mw_pvalue=float(mw_result.pvalue),
        mw_statistic=float(mw_result.statistic),
        metric4_pass=metric4_pass,
    )
