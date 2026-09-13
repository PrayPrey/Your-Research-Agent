"""Dataset loader for h-m4."""

from datasets import load_dataset


def load_humaneval() -> list[dict]:
    """Load HumanEval benchmark dataset."""
    dataset = load_dataset("openai_humaneval")
    test_data = dataset['test']

    # Convert to list of dicts
    return [
        {
            'task_id': item['task_id'],
            'prompt': item['prompt'],
            'canonical_solution': item['canonical_solution'],
            'test': item['test'],
            'entry_point': item['entry_point']
        }
        for item in test_data
    ]
