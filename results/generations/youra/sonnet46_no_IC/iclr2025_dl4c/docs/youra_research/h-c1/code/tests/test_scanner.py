"""Tests for scanner.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scanner import phase_a, phase_b, _build_wrapper, _classify_error, phase_c_worker, run_all_phases


def test_phase_a_with_doctest():
    assert phase_a("def f():\n    >>> 1+1\n    2\n") is True


def test_phase_a_without_doctest():
    assert phase_a("def f():\n    pass\n") is False


def test_phase_b_with_valid_doctest():
    src = '''def add(a, b):
    """
    >>> add(1, 2)
    3
    """
    return a + b
'''
    r = phase_b(src)
    assert r["ast_positive"] is True
    assert r["n_examples"] > 0
    assert r["error"] is None


def test_phase_b_syntax_error():
    r = phase_b("def f(:\n    pass")
    assert r["ast_positive"] is False
    assert r["error"] is not None


def test_phase_b_no_doctests():
    src = "def f():\n    pass\n"
    r = phase_b(src)
    assert r["ast_positive"] is False
    assert r["n_examples"] == 0


def test_build_wrapper_roundtrip():
    src = 'def f():\n    """\n    >>> f()\n    42\n    """\n    return 42\n'
    wrapper = _build_wrapper(src)
    assert "base64" in wrapper
    assert "doctest.testmod" in wrapper


def test_classify_error_import():
    assert _classify_error(1, b"ImportError: no module named foo") == "import_error"


def test_classify_error_assertion():
    assert _classify_error(1, b"Failed example: something") == "assertion_error"


def test_classify_error_exception():
    assert _classify_error(1, b"some random error") == "exception"


def test_phase_c_worker_passing():
    src = 'def add(a, b):\n    """\n    >>> add(1, 2)\n    3\n    """\n    return a + b\n'
    r = phase_c_worker(src, timeout=10)
    assert r["passed"] is True
    assert r["error_type"] is None


def test_phase_c_worker_failing():
    src = 'def add(a, b):\n    """\n    >>> add(1, 2)\n    999\n    """\n    return a + b\n'
    r = phase_c_worker(src, timeout=10)
    assert r["passed"] is False


def test_run_all_phases_schema():
    samples = [
        {"content": 'def f():\n    """\n    >>> f()\n    1\n    """\n    return 1\n'},
        {"content": "x = 1"},
        {"content": ""},
    ]
    results = run_all_phases(samples, n_workers=2)
    assert len(results) == 3
    for r in results:
        for key in ["file_id", "content_len", "phase_a", "phase_b", "phase_c", "error_type", "parse_error", "estimated_tokens"]:
            assert key in r
