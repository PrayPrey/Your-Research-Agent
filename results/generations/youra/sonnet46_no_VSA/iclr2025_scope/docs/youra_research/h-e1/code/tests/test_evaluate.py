"""Tests for evaluate.py: API signatures, delta_norm computation, category mapping."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_compute_delta_norm_basic():
    from evaluate import compute_delta_norm
    from config import CATEGORIES
    teacher = {cat: 0.4 for cat in CATEGORIES}
    student = {cat: 0.3 for cat in CATEGORIES}
    dn = compute_delta_norm(teacher, student)
    assert set(dn.keys()) == set(CATEGORIES)
    # delta_norm = (0.4 - 0.3) / 0.4 = 0.25
    for cat, val in dn.items():
        assert abs(val - 0.25) < 1e-6, f"{cat}: expected 0.25, got {val}"


def test_compute_delta_norm_zero_teacher():
    from evaluate import compute_delta_norm
    from config import CATEGORIES
    teacher = {cat: 0.0 for cat in CATEGORIES}
    student = {cat: 0.1 for cat in CATEGORIES}
    dn = compute_delta_norm(teacher, student)
    # With acc_teacher=0, denominator=1e-8; result should not be NaN/inf
    for val in dn.values():
        assert not (val != val)  # no NaN
        assert abs(val) < 1e10   # no inf


def test_compute_delta_norm_perfect_student():
    from evaluate import compute_delta_norm
    from config import CATEGORIES
    teacher = {cat: 0.5 for cat in CATEGORIES}
    student = {cat: 0.5 for cat in CATEGORIES}
    dn = compute_delta_norm(teacher, student)
    for val in dn.values():
        assert abs(val) < 1e-6


def test_category_map():
    from evaluate import _map_category, CATEGORY_MAP
    assert _map_category("multi-document QA") == "multi_doc_qa"
    assert _map_category("single-document QA") == "single_doc_qa"
    assert _map_category("long in-context learning") == "long_in_context_learning"


def test_format_mcq_prompt():
    from evaluate import _format_mcq_prompt
    example = {
        "context": "Alice went to the store.",
        "input": "Where did Alice go?",
        "options": ["home", "store", "school", "park"],
    }
    prompt = _format_mcq_prompt(example)
    assert "Alice went to the store." in prompt
    assert "A." in prompt
    assert "B." in prompt
    assert "Answer:" in prompt


def test_evaluate_model_longbench_signature():
    """Verify the function has correct signature."""
    import inspect
    from evaluate import evaluate_model_longbench
    sig = inspect.signature(evaluate_model_longbench)
    params = list(sig.parameters.keys())
    assert "model_path" in params
    assert "model_name" in params
    assert "output_json" in params


def test_run_all_evaluations_signature():
    import inspect
    from evaluate import run_all_evaluations
    sig = inspect.signature(run_all_evaluations)
    params = list(sig.parameters.keys())
    assert "teacher_path" in params
    assert "mohawk_ckpt" in params
    assert "lawcat_ckpt" in params
    assert "hybrid4_ckpt" in params
