def count_issues(bandit_results: list[dict], pylint_results: list[dict]) -> dict:
    return {
        "security": len(bandit_results),
        "reliability": len(pylint_results)
    }


def issue_reduction(initial: int, final: int) -> float:
    return 0.0 if initial == 0 else (initial - final) / initial


if __name__ == "__main__":
    assert abs(issue_reduction(10, 3) - 0.7) < 1e-9
    assert issue_reduction(0, 0) == 0.0
    assert count_issues([{}, {}], [{}]) == {"security": 2, "reliability": 1}
    print("metrics self-check OK")
