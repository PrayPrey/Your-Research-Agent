#!/usr/bin/env python3
"""Test gradient concentration analysis components."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gradient_analysis import (
    tokenize_with_lines,
    parse_traceback_line,
    classify_error,
    compute_concentration_metrics,
)


def test_parse_traceback():
    tb = 'Traceback (most recent call last):\n  File "<string>", line 3, in <module>\nNameError: name \'x\' is not defined'
    assert parse_traceback_line(tb) == 3, "Should extract line 3"

    tb2 = 'File "test.py", line 10\n  File "<string>", line 5'
    assert parse_traceback_line(tb2) == 5, "Should extract last line number"

    assert parse_traceback_line("") is None
    assert parse_traceback_line("no line info here") is None
    print("test_parse_traceback PASSED")


def test_classify_error():
    assert classify_error("NameError: name 'x'") == "U_line"
    assert classify_error("TypeError: unsupported") == "U_line"
    assert classify_error("SyntaxError: invalid") == "U_line"
    assert classify_error("IndexError: list index") == "U_line"

    assert classify_error("RecursionError: max depth") == "U_ignore"
    assert classify_error("TimeoutError: exceeded") == "U_ignore"
    assert classify_error("MemoryError: unable") == "U_ignore"

    assert classify_error(None) == "pass"
    print("test_classify_error PASSED")


def test_concentration_metrics():
    line_grads = {1: 0.1, 2: 0.2, 3: 0.5, 4: 0.1, 5: 0.1}
    metrics = compute_concentration_metrics(line_grads, error_line=3)

    assert metrics["error_line"] == 3
    assert metrics["error_line_gradient"] == 0.5
    assert metrics["concentration_ratio"] > 1.0, "Error line should have higher gradient"

    print(f"  ratio={metrics['concentration_ratio']:.3f}")
    print(f"  within_2_pct={metrics['within_2_lines_pct']:.3f}")
    print("test_concentration_metrics PASSED")


def test_tokenize_with_lines():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-small")

    code = "def foo():\n    x = 1\n    return x"
    tokens, line_numbers = tokenize_with_lines(code, tokenizer)

    assert len(tokens) > 0, "Should produce tokens"
    assert len(tokens) == len(line_numbers), "Token count should match line count"
    assert 1 in line_numbers, "Should have line 1"
    assert 2 in line_numbers, "Should have line 2"
    assert 3 in line_numbers, "Should have line 3"

    print(f"  tokens={len(tokens)}, lines={set(line_numbers)}")
    print("test_tokenize_with_lines PASSED")


def main():
    print("Running H-M1 unit tests...")
    print()

    test_parse_traceback()
    test_classify_error()
    test_concentration_metrics()
    test_tokenize_with_lines()

    print()
    print("All tests PASSED")


if __name__ == "__main__":
    main()
