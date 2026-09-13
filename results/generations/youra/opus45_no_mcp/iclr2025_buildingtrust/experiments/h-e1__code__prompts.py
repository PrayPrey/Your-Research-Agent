"""Prompt templates for 5 experimental conditions."""

PROMPTS = {
    "baseline": """Question: {question}
Choices:
{choices}
Answer with the letter of the correct choice, then provide your confidence.
Format: Answer: [letter]. Confidence: [0-100]%""",

    "cot_only": """Question: {question}
Choices:
{choices}
Let's think step by step, then provide your answer and confidence.
Format: [reasoning]. Answer: [letter]. Confidence: [0-100]%""",

    "confidence_only": """Question: {question}
Choices:
{choices}
Answer with the letter, then carefully consider your confidence level.
Format: Answer: [letter]. Confidence: [0-100]%""",

    "cot_confidence": """Question: {question}
Choices:
{choices}
Let's think step by step. After reasoning, provide your answer and confidence.
Format: [reasoning]. Answer: [letter]. Confidence: [0-100]%""",

    "token_padding": """Question: {question}
Choices:
{choices}
Please consider this question thoroughly. This text is included to match the token count of extended reasoning prompts. The goal is to ensure comparable context length while maintaining the direct question-answer format without step-by-step reasoning. Now provide your response.
Answer with the letter of the correct choice, then provide your confidence.
Format: Answer: [letter]. Confidence: [0-100]%"""
}


def build_prompt(condition: str, question: str, choices: str) -> str:
    """Build prompt from template."""
    return PROMPTS[condition].format(question=question, choices=choices)
