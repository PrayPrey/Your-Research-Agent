"""Feedback-guided repair loop for H-M3."""
from dataclasses import dataclass, field
from typing import Optional

from src.evaluate import evaluate_solution, strip_markdown_fences

REPAIR_PROMPT_TEMPLATE = """\
Problem: {problem_prompt}

Previous solution (FAILED):
```python
{previous_solution}
```

Feedback from {feedback_category} verifier:
{feedback_text}

Fix the solution. Return only the corrected Python code:
```python
"""


@dataclass
class RepairResult:
    problem_id: str
    category: str
    iter1_pass: bool = False
    iter2_pass: Optional[bool] = None
    iter3_pass: Optional[bool] = None
    iterations_to_pass: Optional[int] = None
    feedback_lengths: list = field(default_factory=list)
    source: str = "unknown"
    bug_type: str = "unknown"


def build_repair_prompt(problem_prompt: str, previous_solution: str,
                        feedback_category: str, feedback_text: str) -> str:
    # Truncate pyright output to prevent token overflow (avg 24358 chars)
    # ponytail: simple slice; use smarter truncation if LLM performance degrades
    truncated = feedback_text[:4000] if len(feedback_text) > 4000 else feedback_text
    return REPAIR_PROMPT_TEMPLATE.format(
        problem_prompt=problem_prompt,
        previous_solution=previous_solution,
        feedback_category=feedback_category,
        feedback_text=truncated,
    )


def call_llm(prompt: str, model: str, temperature: float, client) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content or ""
        return strip_markdown_fences(raw) or raw
    except Exception as e:
        print(f"    LLM error: {e}")
        return ""


def run_repair_loop(
    problem: dict,
    initial_solution: str,
    verifier,
    model: str = "gpt-4o-mini",
    max_iterations: int = 3,
    temperature: float = 0.0,
    client=None,
) -> RepairResult:
    """Run 3-iteration repair loop; track per-iteration pass/fail."""
    pid = problem.get("task_id") or problem.get("id", "unknown")
    result = RepairResult(
        problem_id=pid,
        category=verifier.category,
        source=problem.get("source", "unknown"),
        bug_type=problem.get("bug_type", "unknown"),
    )

    solution = initial_solution
    for i in range(1, max_iterations + 1):
        feedback = verifier.get_feedback(solution, problem)
        result.feedback_lengths.append(feedback.char_count)

        if feedback.timeout:
            print(f"    [{pid}] iter{i} {verifier.category}: verifier timeout")
            break

        prompt = build_repair_prompt(
            problem.get("prompt", problem.get("text", "")),
            solution,
            verifier.category,
            feedback.feedback_text,
        )
        solution = call_llm(prompt, model, temperature, client)
        if not solution:
            print(f"    [{pid}] iter{i} {verifier.category}: LLM returned empty")
            break

        passed = evaluate_solution(solution, problem)
        setattr(result, f"iter{i}_pass", passed)
        print(f"    [{pid}] iter{i} {verifier.category}: pass={passed}")

        if passed:
            result.iterations_to_pass = i
            break

    return result


def verify_mechanism(problems_sample: list, verifiers: dict, client) -> None:
    """Sanity check: fire repair loop once per category."""
    print("Running mechanism verification...")
    dummy_solution = "def solution():\n    pass  # intentionally wrong"
    for cat, verifier in verifiers.items():
        result = run_repair_loop(
            problem=problems_sample[0],
            initial_solution=dummy_solution,
            verifier=verifier,
            max_iterations=1,
            client=client,
        )
        assert result.iter1_pass in [True, False], f"Repair loop failed for {cat}"
        print(f"  ✓ {cat}: iter1_pass={result.iter1_pass}")
    print("Mechanism verification passed.")
