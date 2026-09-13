from config import AnalysisConfig

def compute_delta_pass_12(logs: list[dict], condition: str) -> dict:
    sub = [r for r in logs if r["condition"] == condition]
    problems = {r["problem_id"] for r in sub}
    n = len(problems)
    if n == 0:
        raise ValueError(f"No data for condition {condition}")

    def solved_by(max_iter: int) -> set:
        return {r["problem_id"] for r in sub if r["iteration"] <= max_iter and r["passed"]}

    solved_1 = solved_by(1)
    solved_2 = solved_by(2)

    pass_1 = len(solved_1) / n
    pass_2 = len(solved_2) / n
    newly_solved_2 = solved_2 - solved_1

    return {
        "delta_pass_12": pass_2 - pass_1,
        "pass_at_iter_1": pass_1,
        "pass_at_iter_2": pass_2,
        "n_problems": n,
        "newly_solved_iter_2": newly_solved_2
    }

def compute_cumulative_trajectory(logs: list[dict], condition: str) -> dict[int, float]:
    sub = [r for r in logs if r["condition"] == condition]
    problems = {r["problem_id"] for r in sub}
    n = len(problems)

    out = {}
    for it in (1, 2, 3):
        solved = {r["problem_id"] for r in sub if r["iteration"] <= it and r["passed"]}
        out[it] = len(solved) / n
    return out

def compare_conditions(logs: list[dict], cfg: AnalysisConfig) -> dict:
    static, exec_ = cfg.conditions
    d_static = compute_delta_pass_12(logs, static)
    d_exec = compute_delta_pass_12(logs, exec_)
    diff = d_static["delta_pass_12"] - d_exec["delta_pass_12"]
    return {
        "static_first": d_static,
        "exec_first": d_exec,
        "delta_diff": diff,
        "hypothesis_supported": diff > 0
    }
