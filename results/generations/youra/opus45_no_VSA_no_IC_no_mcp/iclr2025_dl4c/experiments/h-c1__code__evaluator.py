"""Evaluation: pass@1 and feedback mechanism comparison."""
from base.sandbox_executor import SandboxExecutor, ExecutionResult
from model_client import ModelClient
from feedback import build_exec_feedback, build_critic_feedback
from refine import refine_with_feedback


def pass_at_1(executor: SandboxExecutor, code: str, tests: str) -> float:
    """1.0 if exit_code==0 and not timed_out, else 0.0."""
    result = executor.run(code, tests)
    return 1.0 if result.exit_code == 0 and not result.timed_out else 0.0


def compare_feedback_mechanisms(
    client: ModelClient,
    executor: SandboxExecutor,
    problem: dict,
    initial_code: str,
) -> dict:
    """Compare execution feedback vs AI-critic for single problem."""
    exec_result = executor.run(initial_code, problem["tests"])
    exec_feedback = build_exec_feedback(exec_result)
    critic_feedback = build_critic_feedback(client, initial_code, problem)

    exec_refined = refine_with_feedback(client, initial_code, exec_feedback, problem)
    critic_refined = refine_with_feedback(client, initial_code, critic_feedback, problem)

    execution_pass = pass_at_1(executor, exec_refined, problem["tests"])
    critic_pass = pass_at_1(executor, critic_refined, problem["tests"])

    return {
        "problem_id": problem["id"],
        "execution_pass": execution_pass,
        "critic_pass": critic_pass,
        "execution_advantage": execution_pass - critic_pass,
        "exec_feedback_type": "pass" if exec_result.exit_code == 0 else "fail",
    }


if __name__ == "__main__":
    print("Evaluator module loaded")
