def verify_api_accessible() -> tuple[dict, dict]:
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    he_problems = get_human_eval_plus()
    mbpp_problems = get_mbpp_plus()
    assert he_problems, "get_human_eval_plus() returned empty"
    assert mbpp_problems, "get_mbpp_plus() returned empty"
    return he_problems, mbpp_problems


def verify_task_ids(he_failures: dict, mbpp_failures: dict,
                    he_problems: dict, mbpp_problems: dict) -> None:
    for tid in he_failures:
        assert tid in he_problems, f"{tid} not in EvalPlus HE+ dataset"
    for tid in mbpp_failures:
        assert tid in mbpp_problems, f"{tid} not in EvalPlus MBPP+ dataset"
