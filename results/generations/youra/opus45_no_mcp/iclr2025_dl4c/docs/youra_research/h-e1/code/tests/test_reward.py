"""Tests for reward module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reward import classify_error, parse_traceback_line, compute_gated_reward, Token


def test_classify_error():
    assert classify_error(None) == "pass"
    assert classify_error("SyntaxError: invalid syntax") == "U_line"
    assert classify_error("NameError: name 'x' is not defined") == "U_line"
    assert classify_error("TypeError: unsupported operand type") == "U_line"
    assert classify_error("RuntimeError: maximum recursion depth") == "U_ignore"
    assert classify_error("RecursionError: maximum recursion depth") == "U_ignore"
    assert classify_error("MemoryError") == "U_ignore"
    print("test_classify_error: PASS")


def test_parse_traceback_line():
    tb = '''Traceback (most recent call last):
  File "test.py", line 10, in <module>
    result = func()
  File "test.py", line 5, in func
    return x + y
NameError: name 'x' is not defined'''
    assert parse_traceback_line(tb) == 5
    assert parse_traceback_line("") is None
    assert parse_traceback_line(None) is None
    print("test_parse_traceback_line: PASS")


def test_compute_gated_reward():
    tokens = [Token("def", 1), Token("foo", 1), Token(":", 1),
              Token("return", 2), Token("x", 2)]

    r_pass = compute_gated_reward(tokens, None, "fine_gated")
    assert all(v == 1.0 for v in r_pass.tolist()), "Pass case should give +1.0"

    tb_u_line = 'File "x.py", line 2\nNameError: name \'x\' is not defined'
    r_line = compute_gated_reward(tokens, tb_u_line, "fine_gated")
    assert r_line[3] == -1.0, f"Token at line 2 should be -1.0, got {r_line[3]}"
    assert r_line[4] == -1.0, f"Token at line 2 should be -1.0, got {r_line[4]}"

    tb_u_ignore = "RuntimeError: maximum recursion depth exceeded"
    r_ignore = compute_gated_reward(tokens, tb_u_ignore, "fine_gated")
    assert all(abs(v - (-0.1)) < 0.01 for v in r_ignore.tolist()), "U_ignore with gating should give -0.1"

    r_always = compute_gated_reward(tokens, tb_u_ignore, "fine_always")
    assert abs(r_always[0] - (-0.1)) < 0.01, "fine_always still gives -0.1 for coarse"

    print("test_compute_gated_reward: PASS")


if __name__ == "__main__":
    test_classify_error()
    test_parse_traceback_line()
    test_compute_gated_reward()
    print("\nAll tests passed!")
