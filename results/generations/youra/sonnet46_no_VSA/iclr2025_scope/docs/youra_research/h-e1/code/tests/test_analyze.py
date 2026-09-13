"""Tests for analyze.py: bootstrap CI, mechanism verification, gate logic."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_delta_norms(ssm_retrieval=0.3, ssm_gen=0.1, lawcat_retrieval=0.1, lawcat_gen=0.08):
    from config import CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY
    mohawk = {}
    lawcat = {}
    for cat in CATEGORIES:
        if cat in RETRIEVAL_HEAVY:
            mohawk[cat] = ssm_retrieval
            lawcat[cat] = lawcat_retrieval
        elif cat in GENERATION_HEAVY:
            mohawk[cat] = ssm_gen
            lawcat[cat] = lawcat_gen
        else:
            mohawk[cat] = 0.15
            lawcat[cat] = 0.12
    return {"mohawk": mohawk, "lawcat": lawcat, "hybrid4": {c: 0.12 for c in CATEGORIES}}


def test_bootstrap_returns_tuple():
    from analyze import bootstrap_interaction_ratio
    dn = _make_delta_norms()
    ratio, ci_low, ci_high = bootstrap_interaction_ratio(
        delta_norm_ssm=dn["mohawk"],
        delta_norm_lawcat=dn["lawcat"],
        n_resamples=100,
    )
    assert isinstance(ratio, float)
    assert isinstance(ci_low, float)
    assert isinstance(ci_high, float)
    assert ci_low <= ratio <= ci_high


def test_bootstrap_ratio_known_value():
    from analyze import bootstrap_interaction_ratio
    # SSM retrieval = 0.30, LAWCAT retrieval = 0.10 → ratio = 3.0
    dn = _make_delta_norms(ssm_retrieval=0.30, lawcat_retrieval=0.10)
    ratio, ci_low, ci_high = bootstrap_interaction_ratio(
        delta_norm_ssm=dn["mohawk"],
        delta_norm_lawcat=dn["lawcat"],
        n_resamples=200,
        seed=42,
    )
    assert abs(ratio - 3.0) < 0.5, f"Expected ratio ~3.0, got {ratio}"


def test_bootstrap_ci_above_1_for_large_effect():
    from analyze import bootstrap_interaction_ratio
    dn = _make_delta_norms(ssm_retrieval=0.40, lawcat_retrieval=0.10)
    ratio, ci_low, ci_high = bootstrap_interaction_ratio(
        delta_norm_ssm=dn["mohawk"],
        delta_norm_lawcat=dn["lawcat"],
        n_resamples=500,
        seed=42,
    )
    assert ci_low > 1.0, f"CI low {ci_low} should be > 1.0 for large effect"


def test_verify_mechanism_direction():
    from analyze import verify_mechanism_activated
    dn = _make_delta_norms(ssm_retrieval=0.3, lawcat_retrieval=0.1)
    all_pass, indicators = verify_mechanism_activated(
        mohawk_checkpoint=None,
        lawcat_checkpoint=None,
        training_logs={},
        delta_norms=dn,
    )
    assert indicators.get("interaction_direction_correct") == True
    assert indicators.get("both_students_degrade") == True


def test_verify_mechanism_wrong_direction():
    from analyze import verify_mechanism_activated
    # If LAWCAT has more degradation, direction check should fail
    dn = _make_delta_norms(ssm_retrieval=0.05, lawcat_retrieval=0.30)
    _, indicators = verify_mechanism_activated(
        mohawk_checkpoint=None, lawcat_checkpoint=None,
        training_logs={}, delta_norms=dn,
    )
    assert indicators.get("interaction_direction_correct") == False


def test_fit_mixed_effects_returns_floats():
    from analyze import fit_mixed_effects_model
    dn = _make_delta_norms()
    p_val, holm_p = fit_mixed_effects_model(dn)
    assert isinstance(p_val, float)
    assert isinstance(holm_p, float)
    assert 0.0 <= p_val <= 1.0
    assert 0.0 <= holm_p <= 1.0


def test_gate_logic():
    """Verify gate passes when criteria are met."""
    from analyze import bootstrap_interaction_ratio
    # Large effect: ratio=4, CI should be above 1
    dn = _make_delta_norms(ssm_retrieval=0.4, lawcat_retrieval=0.1)
    ratio, ci_low, ci_high = bootstrap_interaction_ratio(
        delta_norm_ssm=dn["mohawk"],
        delta_norm_lawcat=dn["lawcat"],
        n_resamples=1000,
        seed=0,
    )
    gate_passed = ratio >= 2.0 and ci_low > 1.0
    assert gate_passed, (
        f"Gate should pass with ratio={ratio:.2f}, ci_low={ci_low:.2f}"
    )
