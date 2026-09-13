"""Feedback mechanisms: execution-based vs AI-critic."""
from base.sandbox_executor import ExecutionResult
from model_client import ModelClient

CRITIC_PROMPT_TEMPLATE = """Review this code for correctness bugs. Do not execute it. List issues.

Problem:
{problem}

Code:
{code}

List any bugs or issues you find (be concise):"""


def build_exec_feedback(exec_result: ExecutionResult) -> str:
    """Format ExecutionResult into feedback string for refinement."""
    if exec_result.timed_out:
        return "Execution timed out. The code may have an infinite loop or be too slow."
    if exec_result.exit_code == 0:
        return "All tests passed."
    return f"Execution failed:\n{exec_result.traceback or exec_result.stderr}"


def build_critic_feedback(client: ModelClient, code: str, problem: dict) -> str:
    """LLM critique from code+prompt only, no execution info."""
    prompt = CRITIC_PROMPT_TEMPLATE.format(problem=problem["prompt"], code=code)
    return client.generate(prompt)


if __name__ == "__main__":
    from base.sandbox_executor import SandboxExecutor

    executor = SandboxExecutor()
    code = "def add(a, b): return a - b"
    tests = "assert add(1, 2) == 3"
    result = executor.run(code, tests)
    print("Exec feedback:", build_exec_feedback(result))
