"""
Data Pipeline for HumanEval + MBPP
Task: A-1 (Data Pipeline)
"""
import os
import random
from typing import Dict, List, Tuple
from datasets import load_dataset, DatasetDict, Dataset
from transformers import AutoTokenizer
import torch
from torch.utils.data import DataLoader


class CodeGenerationDataset:
    """Combined HumanEval + MBPP dataset for code generation"""

    def __init__(self, cache_dir: str = "./.data_cache/datasets"):
        self.cache_dir = cache_dir
        self.humaneval = None
        self.mbpp = None
        self.combined_data = None

    def load_datasets(self):
        """Load HumanEval and MBPP from HuggingFace"""
        print("Loading datasets...")

        # Load HumanEval (164 samples)
        try:
            self.humaneval = load_dataset(
                "evalplus/humanevalplus",
                cache_dir=f"{self.cache_dir}/humaneval"
            )
            print(f"✓ HumanEval: {len(self.humaneval['test'])} samples")
        except Exception as e:
            print(f"Warning: HumanEval load failed: {e}")
            self.humaneval = None

        # Load MBPP (964 samples)
        try:
            self.mbpp = load_dataset(
                "google-research-datasets/mbpp",
                cache_dir=f"{self.cache_dir}/mbpp"
            )
            print(f"✓ MBPP: {len(self.mbpp['train']) + len(self.mbpp['test'])} samples")
        except Exception as e:
            print(f"Warning: MBPP load failed: {e}")
            self.mbpp = None

        if not self.humaneval and not self.mbpp:
            raise RuntimeError("Failed to load any datasets")

    def prepare_combined_dataset(
        self,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 42
    ) -> DatasetDict:
        """Combine datasets and create train/val/test splits"""
        combined_samples = []

        # Add HumanEval samples
        if self.humaneval:
            for sample in self.humaneval['test']:
                combined_samples.append({
                    'prompt': sample.get('prompt', ''),
                    'canonical_solution': sample.get('canonical_solution', ''),
                    'test': sample.get('test', ''),
                    'entry_point': sample.get('entry_point', ''),
                    'task_id': sample.get('task_id', ''),
                    'source': 'humaneval'
                })

        # Add MBPP samples
        if self.mbpp:
            for split in ['train', 'test', 'validation']:
                if split in self.mbpp:
                    for sample in self.mbpp[split]:
                        combined_samples.append({
                            'prompt': sample.get('text', ''),
                            'canonical_solution': sample.get('code', ''),
                            'test': sample.get('test_list', [''])[0] if sample.get('test_list') else '',
                            'entry_point': '',  # MBPP doesn't have entry points
                            'task_id': f"mbpp_{sample.get('task_id', 0)}",
                            'source': 'mbpp'
                        })

        print(f"Combined dataset: {len(combined_samples)} samples")

        # Shuffle and split
        random.seed(seed)
        random.shuffle(combined_samples)

        total = len(combined_samples)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        splits = {
            'train': combined_samples[:train_end],
            'validation': combined_samples[train_end:val_end],
            'test': combined_samples[val_end:]
        }

        print(f"Splits: train={len(splits['train'])}, val={len(splits['validation'])}, test={len(splits['test'])}")

        # Convert to HuggingFace Dataset
        dataset_dict = DatasetDict({
            split_name: Dataset.from_list(samples)
            for split_name, samples in splits.items()
        })

        self.combined_data = dataset_dict
        return dataset_dict


def create_dataloaders(
    tokenizer,
    cache_dir: str = "./.data_cache/datasets",
    batch_size: int = 32,
    max_length: int = 512,
    num_workers: int = 4,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train/val/test dataloaders

    Returns:
        (train_loader, val_loader, test_loader)
    """
    # Load and prepare dataset
    dataset = CodeGenerationDataset(cache_dir=cache_dir)
    dataset.load_datasets()
    dataset_dict = dataset.prepare_combined_dataset(seed=seed)

    # Tokenization function
    def tokenize_function(examples):
        # Combine prompt and canonical solution for training
        texts = [
            f"{prompt}\n{solution}"
            for prompt, solution in zip(examples['prompt'], examples['canonical_solution'])
        ]

        tokenized = tokenizer(
            texts,
            max_length=max_length,
            truncation=True,
            padding='max_length',
            return_tensors=None
        )

        # Add original fields for evaluation
        tokenized['prompt'] = examples['prompt']
        tokenized['test_cases'] = examples['test']
        tokenized['sample_id'] = examples['task_id']

        return tokenized

    # Tokenize datasets
    tokenized_datasets = dataset_dict.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset_dict['train'].column_names
    )

    # Create dataloaders
    train_loader = DataLoader(
        tokenized_datasets['train'],
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        tokenized_datasets['validation'],
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        tokenized_datasets['test'],
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    print(f"✓ Dataloaders created: {len(train_loader)} train batches, {len(test_loader)} test batches")

    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    # Test data pipeline
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_dl, val_dl, test_dl = create_dataloaders(
        tokenizer=tokenizer,
        batch_size=4,
        cache_dir="../.data_cache/datasets"
    )

    # Test batch
    batch = next(iter(train_dl))
    print(f"\nSample batch keys: {batch.keys()}")
    print(f"Batch size: {len(batch['input_ids'])}")
    print(f"Test set size: {len(test_dl.dataset)} (should be ~10% of total)")
