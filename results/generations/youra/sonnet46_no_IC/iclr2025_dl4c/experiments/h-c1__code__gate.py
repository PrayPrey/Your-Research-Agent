"""Gate check for H-C1 doctest prevalence scan."""

PASS_THRESHOLD = 0.03
SCOPE_THRESHOLD = 0.01


def run_gate_check(aggregate: dict) -> str:
    """Check gate criteria. Returns 'PASS' | 'SCOPE' | 'PIVOT'."""
    rate = aggregate["doctest_executable_rate"]
    n_sampled = aggregate["n_sampled"]

    assert aggregate["doctest_executable_rate"] <= aggregate["doctest_pattern_rate"], \
        f"Sanity failed: executable_rate ({rate}) > pattern_rate ({aggregate['doctest_pattern_rate']})"
    assert n_sampled == 10000, f"Sanity failed: n_sampled={n_sampled} != 10000"

    if rate >= PASS_THRESHOLD:
        status = "PASS"
    elif rate >= SCOPE_THRESHOLD:
        status = "SCOPE"
    else:
        status = "PIVOT"

    print(f"GATE CHECK: executable_rate={rate:.4f}")
    print(f"STATUS: {status} ({'≥3%' if status == 'PASS' else '1-3%' if status == 'SCOPE' else '<1%'})")
    return status
