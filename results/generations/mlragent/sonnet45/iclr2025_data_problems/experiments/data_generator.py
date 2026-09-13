"""
Data generation for multi-stage training experiments.
Generates synthetic data for pretraining, instruction tuning, and alignment stages.
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Tuple
import random


class SyntheticLanguageDataset(Dataset):
    """Synthetic dataset simulating language modeling data."""

    def __init__(self, num_samples: int, vocab_size: int, max_length: int,
                 stage: str, seed: int = 42):
        """
        Args:
            num_samples: Number of samples to generate
            vocab_size: Size of vocabulary
            max_length: Maximum sequence length
            stage: Training stage ('pretraining', 'instruction_tuning', 'alignment')
            seed: Random seed
        """
        self.num_samples = num_samples
        self.vocab_size = vocab_size
        self.max_length = max_length
        self.stage = stage

        np.random.seed(seed)
        random.seed(seed)

        # Generate data based on stage
        self.data = self._generate_data()

    def _generate_data(self) -> List[Dict]:
        """Generate stage-specific data."""
        data = []

        for i in range(self.num_samples):
            if self.stage == "pretraining":
                # Pretraining: simple sequences with patterns
                seq_len = np.random.randint(self.max_length // 2, self.max_length)
                # Create sequences with some structure (e.g., repeating patterns)
                pattern_len = np.random.randint(5, 15)
                pattern = np.random.randint(1, self.vocab_size, pattern_len)
                repeats = seq_len // pattern_len + 1
                sequence = np.tile(pattern, repeats)[:seq_len]

                data.append({
                    "input_ids": sequence,
                    "labels": np.roll(sequence, -1),  # Next token prediction
                    "sample_id": i,
                    "stage": self.stage
                })

            elif self.stage == "instruction_tuning":
                # Instruction tuning: input-output pairs
                input_len = np.random.randint(10, self.max_length // 2)
                output_len = np.random.randint(10, self.max_length // 2)

                input_seq = np.random.randint(1, self.vocab_size, input_len)
                # Output is a transformation of input (e.g., reversed)
                output_seq = np.flip(input_seq[:output_len])

                # Concatenate input and output
                full_seq = np.concatenate([input_seq, output_seq])
                labels = np.concatenate([
                    np.full(input_len, -100),  # Ignore input tokens in loss
                    output_seq
                ])

                data.append({
                    "input_ids": full_seq,
                    "labels": labels,
                    "sample_id": i,
                    "stage": self.stage
                })

            elif self.stage == "alignment":
                # Alignment: preference pairs
                seq_len = np.random.randint(20, self.max_length)

                # Generate chosen and rejected responses
                chosen = np.random.randint(1, self.vocab_size, seq_len)
                rejected = np.random.randint(1, self.vocab_size, seq_len)

                # Add some correlation between chosen and rejected
                mask = np.random.random(seq_len) > 0.3
                rejected = np.where(mask, rejected, chosen)

                data.append({
                    "chosen": chosen,
                    "rejected": rejected,
                    "sample_id": i,
                    "stage": self.stage
                })

        return data

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict:
        return self.data[idx]


def collate_fn(batch: List[Dict], max_length: int) -> Dict[str, torch.Tensor]:
    """Collate function for batching."""
    if "chosen" in batch[0]:  # Alignment stage
        # Pad sequences
        chosen_ids = []
        rejected_ids = []

        for item in batch:
            chosen = np.pad(item["chosen"], (0, max_length - len(item["chosen"])),
                          constant_values=0)[:max_length]
            rejected = np.pad(item["rejected"], (0, max_length - len(item["rejected"])),
                            constant_values=0)[:max_length]
            chosen_ids.append(chosen)
            rejected_ids.append(rejected)

        return {
            "chosen": torch.tensor(chosen_ids, dtype=torch.long),
            "rejected": torch.tensor(rejected_ids, dtype=torch.long),
            "sample_ids": torch.tensor([item["sample_id"] for item in batch])
        }
    else:
        # Pretraining or instruction tuning
        input_ids = []
        labels = []

        for item in batch:
            inp = np.pad(item["input_ids"], (0, max_length - len(item["input_ids"])),
                        constant_values=0)[:max_length]
            lab = np.pad(item["labels"], (0, max_length - len(item["labels"])),
                        constant_values=-100)[:max_length]
            input_ids.append(inp)
            labels.append(lab)

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "sample_ids": torch.tensor([item["sample_id"] for item in batch])
        }


def create_dataloaders(config: Dict) -> Dict[str, DataLoader]:
    """Create dataloaders for all training stages."""
    dataloaders = {}

    model_config = config["model_config"]
    data_config = config["data_config"]

    stages = ["pretraining", "instruction_tuning", "alignment"]
    stage_samples = {
        "pretraining": data_config["pretrain_samples"],
        "instruction_tuning": data_config["instruction_samples"],
        "alignment": data_config["alignment_samples"]
    }

    for stage in stages:
        dataset = SyntheticLanguageDataset(
            num_samples=stage_samples[stage],
            vocab_size=model_config["vocab_size"],
            max_length=model_config["max_seq_length"],
            stage=stage,
            seed=data_config["seed"]
        )

        batch_size = config["stage_configs"][stage]["batch_size"]

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            collate_fn=lambda x: collate_fn(x, model_config["max_seq_length"])
        )

        dataloaders[stage] = dataloader

    # Create test dataloader
    test_dataset = SyntheticLanguageDataset(
        num_samples=data_config["test_samples"],
        vocab_size=model_config["vocab_size"],
        max_length=model_config["max_seq_length"],
        stage="pretraining",  # Use pretraining format for testing
        seed=data_config["seed"] + 1000
    )

    dataloaders["test"] = DataLoader(
        test_dataset,
        batch_size=16,
        shuffle=False,
        collate_fn=lambda x: collate_fn(x, model_config["max_seq_length"])
    )

    return dataloaders
