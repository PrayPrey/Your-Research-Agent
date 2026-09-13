"""Code refinement with feedback."""
from model_client import ModelClient

REFINE_PROMPT_TEMPLATE = """Problem:
{prompt}

Current code:
{code}

Feedback:
{feedback}

Provide corrected code only (no explanation):"""


def refine_with_feedback(
    client: ModelClient, code: str, feedback: str, problem: dict
) -> str:
    """Single-iteration refinement using feedback. Same template for both mechanisms."""
    if "All tests passed" in feedback:
        return code
    prompt = REFINE_PROMPT_TEMPLATE.format(
        prompt=problem["prompt"], code=code, feedback=feedback
    )
    return client.generate(prompt)


if __name__ == "__main__":
    print("Refine module loaded")
