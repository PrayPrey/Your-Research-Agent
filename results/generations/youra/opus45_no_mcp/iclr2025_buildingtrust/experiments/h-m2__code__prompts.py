"""Prompt templates for H-M2 CoT+confidence generation."""


def build_cot_confidence_prompt(question: str) -> str:
    """Build CoT + confidence free-text prompt.

    Args:
        question: The question to answer.

    Returns:
        Formatted prompt string with CoT instructions.
    """
    return f"""Question: {question}

Let's think step by step about this question, considering possible answers and reasoning through them.

After your reasoning, conclude with a line stating: My confidence: <0-100>"""
