"""Data loading for H-M1: TriviaQA subset."""

from datasets import load_dataset


def load_triviaqa_subset(n: int = 1000):
    """Load TriviaQA validation subset."""
    dataset = load_dataset("trivia_qa", "rc", split=f"validation[:{n}]")
    return dataset


def format_prompt(example: dict) -> str:
    """Format TriviaQA example as Llama-3 chat prompt."""
    question = example["question"]
    return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nAnswer concisely: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
