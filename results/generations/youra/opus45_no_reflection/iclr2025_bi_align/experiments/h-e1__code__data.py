"""HH-RLHF data loading and preprocessing."""
from datasets import load_dataset
import config

def load_hh_rlhf_sample(seed: int = None, n: int = None):
    """Load HH-RLHF helpful-base, shuffle, select n samples."""
    seed = seed or config.SEED
    n = n or config.SAMPLE_SIZE
    dataset = load_dataset(config.DATASET_NAME, data_dir=config.DATASET_SUBSET, split="train")
    dataset = dataset.shuffle(seed=seed).select(range(n))
    return dataset

def extract_assistant_response(conversation: str) -> str:
    """Extract final assistant turn from HH-RLHF conversation format."""
    parts = conversation.split('\n\nAssistant: ')
    if len(parts) > 1:
        response = parts[-1]
        if '\n\nHuman:' in response:
            response = response.split('\n\nHuman:')[0]
        return response.strip()
    return conversation.strip()
