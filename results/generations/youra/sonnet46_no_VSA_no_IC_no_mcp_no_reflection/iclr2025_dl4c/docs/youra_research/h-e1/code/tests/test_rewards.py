import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rewards import execute_code, binary_reward, ratio_reward, make_reward_fn


def test_execute_code_pass():
    code = 'print(3)'
    assert execute_code(code, "", "3") is True


def test_execute_code_fail():
    code = 'print(999)'
    assert execute_code(code, "", "3") is False


def test_execute_code_timeout():
    code = 'while True: pass'
    assert execute_code(code, "", "", timeout=1) is False


def test_execute_code_syntax_error():
    code = 'def ('
    # syntax error produces no stdout, so comparing to "expected_output" must fail
    assert execute_code(code, "", "expected_output") is False


def test_binary_reward_all_pass():
    code = 'print(int(input()) * 2)'
    test_cases = [
        {"input": "3\n", "output": "6"},
        {"input": "5\n", "output": "10"},
    ]
    assert binary_reward(code, test_cases) == 1.0


def test_binary_reward_partial_fail():
    code = 'print(3)'
    test_cases = [
        {"input": "", "output": "3"},
        {"input": "", "output": "5"},
    ]
    assert binary_reward(code, test_cases) == 0.0


def test_binary_reward_empty():
    assert binary_reward("print(1)", []) == 0.0


def test_ratio_reward_all_pass():
    code = 'print(int(input()) * 2)'
    test_cases = [
        {"input": "3\n", "output": "6"},
        {"input": "5\n", "output": "10"},
    ]
    assert ratio_reward(code, test_cases) == 1.0


def test_ratio_reward_partial():
    code = 'print(3)'
    test_cases = [
        {"input": "", "output": "3"},
        {"input": "", "output": "5"},
        {"input": "", "output": "7"},
    ]
    result = ratio_reward(code, test_cases)
    assert abs(result - 1/3) < 1e-9


def test_ratio_reward_empty():
    assert ratio_reward("print(1)", []) == 0.0


def test_make_reward_fn_binary():
    fn = make_reward_fn("binary")
    code = 'print(3)'
    completions = [code, code]
    tc_list = [
        [{"input": "", "output": "3"}],
        [{"input": "", "output": "5"}],
    ]
    results = fn(completions, test_cases=tc_list)
    assert results[0] == 1.0
    assert results[1] == 0.0


def test_make_reward_fn_ratio():
    fn = make_reward_fn("ratio")
    code = 'print(3)'
    completions = [code]
    tc_list = [
        [{"input": "", "output": "3"}, {"input": "", "output": "5"}]
    ]
    results = fn(completions, test_cases=tc_list)
    assert abs(results[0] - 0.5) < 1e-9


if __name__ == "__main__":
    test_execute_code_pass()
    test_execute_code_fail()
    test_execute_code_timeout()
    test_execute_code_syntax_error()
    test_binary_reward_all_pass()
    test_binary_reward_partial_fail()
    test_binary_reward_empty()
    test_ratio_reward_all_pass()
    test_ratio_reward_partial()
    test_ratio_reward_empty()
    test_make_reward_fn_binary()
    test_make_reward_fn_ratio()
    print("rewards tests passed")
