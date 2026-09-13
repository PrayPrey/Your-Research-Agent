"""A-2: Prompt Templates - Baseline + CoT template builders"""


def build_baseline_prompt(question: str, options: str) -> str:
    """Direct-answer prompt: no CoT trigger."""
    return f"""Question: {question}

Options:
{options}

Answer directly with the letter of the correct option.
Format: Answer: <letter> Confidence: <0-100>"""


def build_cot_prompt(question: str, options: str) -> str:
    """CoT prompt: includes 'Let's think step by step.' trigger."""
    return f"""Question: {question}

Options:
{options}

Let's think step by step. Provide numbered reasoning steps, then conclude with:
Answer: <letter> Confidence: <0-100>"""


if __name__ == "__main__":
    q = "What is the capital of France?"
    opts = "A) London\nB) Paris\nC) Berlin"
    print("=== Baseline ===")
    print(build_baseline_prompt(q, opts))
    print("\n=== CoT ===")
    print(build_cot_prompt(q, opts))
