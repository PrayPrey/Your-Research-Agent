from datasets import load_dataset, Dataset

def load_humaneval() -> Dataset:
    """Load HumanEval benchmark dataset."""
    dataset = load_dataset("openai_humaneval")
    return dataset['test']

def extract_poc_subset(dataset: Dataset, n: int = 5) -> list[dict]:
    """Extract first n problems from dataset."""
    subset = dataset.select(range(n))
    return [
        {
            'task_id': item['task_id'],
            'prompt': item['prompt'],
            'canonical_solution': item['canonical_solution'],
            'test': item['test'],
            'entry_point': item['entry_point']
        }
        for item in subset
    ]
