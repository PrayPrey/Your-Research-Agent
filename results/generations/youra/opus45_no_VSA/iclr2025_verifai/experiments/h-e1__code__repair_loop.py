"""Repair loop: 3 iterations with early-exit on success."""
from dataclasses import dataclass, asdict
from typing import List
from data import Problem
from config import ExperimentConfig
from sandbox import ExecResult, run_tests_majority_vote
from feedback import get_static_feedback, get_execution_feedback, build_feedback_prompt
from llm import generate_initial_code, repair_code


@dataclass
class IterationLog:
    problem_id: str
    condition: str  # "A" | "B"
    iteration: int  # 0 = initial gen, 1..n = repairs
    code: str
    passed: bool
    static_fb: str
    exec_fb: str

    def to_dict(self):
        return asdict(self)


def run_condition(problem: Problem, condition: str, cfg: ExperimentConfig) -> List[IterationLog]:
    """Run initial gen + up to n_iterations repairs for one problem/condition."""
    logs = []

    # Initial generation
    code = generate_initial_code(problem, cfg)
    result = run_tests_majority_vote(code, problem, cfg)
    logs.append(IterationLog(
        problem_id=problem.problem_id,
        condition=condition,
        iteration=0,
        code=code,
        passed=result.passed,
        static_fb="",
        exec_fb="",
    ))

    # Repair iterations
    for it in range(1, cfg.n_iterations + 1):
        if result.passed:
            break

        static_fb = get_static_feedback(code, cfg.feedback_token_budget)
        exec_fb = get_execution_feedback(result, cfg.feedback_token_budget)
        prompt = build_feedback_prompt(static_fb, exec_fb, condition)

        code = repair_code(problem, code, prompt, cfg)
        result = run_tests_majority_vote(code, problem, cfg)

        logs.append(IterationLog(
            problem_id=problem.problem_id,
            condition=condition,
            iteration=it,
            code=code,
            passed=result.passed,
            static_fb=static_fb,
            exec_fb=exec_fb,
        ))

    return logs


def run_all(problems: List[Problem], cfg: ExperimentConfig) -> List[IterationLog]:
    """Run both conditions A and B for all problems."""
    all_logs = []
    for problem in problems:
        all_logs.extend(run_condition(problem, "A", cfg))
        all_logs.extend(run_condition(problem, "B", cfg))
    return all_logs
