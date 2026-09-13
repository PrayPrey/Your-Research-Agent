"""Data loader for WikiText-103 dataset."""

import torch
import json
from datasets import load_dataset
from transformers import AutoTokenizer
from typing import List, Dict
import random


class WikiTextSampler:
    """Sample sequences from WikiText-103 for smoke testing."""

    def __init__(self, model_name: str, dataset_name: str, dataset_config: str,
                 split: str, sequence_length: int, seed: int = 42):
        self.dataset_name = dataset_name
        self.dataset_config = dataset_config
        self.split = split
        self.sequence_length = sequence_length
        self.seed = seed

        # Use GPT-2 tokenizer as Mamba doesn't have one
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load dataset
        self.dataset = load_dataset(dataset_name, dataset_config, split=split)

    def sample_sequences(self, num_sequences: int) -> Dict[str, torch.Tensor]:
        """Sample sequences from the dataset."""
        random.seed(self.seed)
        torch.manual_seed(self.seed)

        sequences = []
        sequence_ids = []

        # Tokenize full dataset text
        full_text = " ".join([example['text'] for example in self.dataset if example['text'].strip()])

        tokenized = self.tokenizer(
            full_text,
            return_tensors='pt',
            truncation=False
        )

        input_ids = tokenized['input_ids'][0]

        # Sample random starting positions
        max_start = len(input_ids) - self.sequence_length
        if max_start <= 0:
            raise ValueError("Dataset too small for requested sequence length")

        sampled_starts = random.sample(range(max_start), min(num_sequences, max_start))

        for idx, start_pos in enumerate(sampled_starts):
            seq = input_ids[start_pos:start_pos + self.sequence_length]
            sequences.append(seq)
            sequence_ids.append({
                'id': f'seq_{idx:04d}',
                'start_pos': start_pos,
                'length': len(seq)
            })

        sequences_tensor = torch.stack(sequences)

        return {
            'input_ids': sequences_tensor,
            'sequence_ids': sequence_ids
        }

    def save_sequence_ids(self, sequence_ids: List[Dict], output_path: str):
        """Save sequence IDs for reproducibility."""
        with open(output_path, 'w') as f:
            json.dump(sequence_ids, f, indent=2)
