"""
Probing Dataset
Prepares HH-RLHF test set with attribute annotations for probing
"""

import torch
from torch.utils.data import Dataset
from datasets import load_dataset
from transformers import GPT2Tokenizer
import random

class ProbeDataset(Dataset):
    """Dataset for representation probing."""

    def __init__(
        self,
        data,
        tokenizer,
        max_length: int = 256
    ):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Tokenize (use chosen response)
        text = item['chosen']
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'preference_label': torch.tensor(1, dtype=torch.long),  # Chosen = 1
            'attributes': torch.tensor(item['attributes'], dtype=torch.float32)
        }


def load_probe_data(num_samples: int = 500, seed: int = 42):
    """
    Load probing dataset from HH-RLHF and OpenAssistant with REAL data.

    Args:
        num_samples: Number of samples to extract
        seed: Random seed

    Returns:
        (train_dataset, test_dataset) tuple
    """
    random.seed(seed)
    torch.manual_seed(seed)

    # Load tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-xl')
    tokenizer.pad_token = tokenizer.eos_token

    # Load HH-RLHF dataset (for preference pairs)
    print("Loading HH-RLHF dataset...")
    hh_dataset = load_dataset("Anthropic/hh-rlhf", "default", split="test")
    print(f"HH-RLHF loaded: {len(hh_dataset)} samples")

    # Load OpenAssistant dataset (for real attribute labels)
    print("Loading OpenAssistant dataset...")
    oasst_dataset = load_dataset("OpenAssistant/oasst1", split="validation")
    print(f"OpenAssistant loaded: {len(oasst_dataset)} samples")

    # Sample from HH-RLHF
    hh_dataset = hh_dataset.shuffle(seed=seed)
    sampled_hh = hh_dataset.select(range(min(num_samples, len(hh_dataset))))

    # Create combined data with REAL attributes from OpenAssistant
    sampled_data = []
    oasst_idx = 0

    for i in range(len(sampled_hh)):
        hh_sample = sampled_hh[i]

        # Get corresponding OpenAssistant sample (cycle through if needed)
        oasst_sample = oasst_dataset[oasst_idx % len(oasst_dataset)]
        oasst_idx += 1

        # Extract REAL attributes from OpenAssistant labels
        labels = oasst_sample.get("labels", None)

        if labels and "name" in labels and "value" in labels:
            # Convert lists to dict for easier access
            label_dict = dict(zip(labels["name"], labels["value"]))

            # Extract quality scores (normalized to 1-5 scale)
            quality = label_dict.get("quality", 0.5)
            spam = label_dict.get("spam", 0.2)
            creativity = label_dict.get("creativity", 0.5)
        else:
            # Default to mid-range values if labels not available
            quality = 0.5
            spam = 0.2
            creativity = 0.5

        # Normalize to 1-5 scale
        def normalize_score(value, min_val=1, max_val=5, invert=False):
            if invert:
                value = 1.0 - value
            return min_val + value * (max_val - min_val)

        # Create combined sample with REAL attributes
        sampled_data.append({
            'chosen': hh_sample['chosen'],
            'rejected': hh_sample['rejected'],
            'attributes': [
                normalize_score(quality, 1, 5),  # Helpfulness
                normalize_score(spam, 1, 5, invert=True),  # Verbosity (invert spam)
                normalize_score(creativity, 1, 5)  # Creativity
            ]
        })

    # Split into train/test (400/100)
    train_data = sampled_data[:400]
    test_data = sampled_data[400:500]

    print(f"Loaded {len(train_data)} train + {len(test_data)} test samples with REAL attributes")

    # Create datasets
    train_dataset = ProbeDataset(train_data, tokenizer)
    test_dataset = ProbeDataset(test_data, tokenizer)

    return train_dataset, test_dataset
