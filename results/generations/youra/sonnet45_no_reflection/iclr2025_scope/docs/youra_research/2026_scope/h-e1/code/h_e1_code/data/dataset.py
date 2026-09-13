"""
Multi-task dataset for GLUE + SuperGLUE benchmarks.
Handles loading, tokenization, and batching for 17 NLP tasks.
"""
import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
from transformers import AutoTokenizer
from typing import Dict, Tuple, List, Optional
from config import DataConfig


class MultiTaskDataset(Dataset):
    """Multi-task dataset combining GLUE + SuperGLUE tasks."""

    def __init__(
        self,
        config: DataConfig,
        split: str = "train",
        tokenizer: AutoTokenizer = None,
        max_samples: Optional[int] = None,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize multi-task dataset.

        Args:
            config: DataConfig with task lists and preprocessing params
            split: Dataset split ('train', 'validation', 'test')
            tokenizer: HuggingFace tokenizer
            max_samples: Optional limit on samples per task (for testing)
            cache_dir: Optional cache directory for datasets
        """
        self.config = config
        self.split = split
        self.tokenizer = tokenizer
        self.max_samples = max_samples
        self.cache_dir = cache_dir or "../.data_cache/datasets"

        self.datasets = {}
        self.task_indices = []
        self.task_name_to_id = {}

        # Load all tasks
        self._load_all_tasks()

    def _load_all_tasks(self) -> None:
        """Load all GLUE and SuperGLUE tasks and build task indices."""
        task_id = 0

        # Load GLUE tasks
        for task_name in self.config.glue_tasks:
            try:
                dataset = load_glue_task(task_name, self.split, self.cache_dir)
                if dataset is not None:
                    self.datasets[task_name] = dataset
                    self.task_name_to_id[task_name] = task_id

                    # Build task indices
                    num_samples = len(dataset) if self.max_samples is None else min(len(dataset), self.max_samples)
                    for idx in range(num_samples):
                        self.task_indices.append((task_name, idx))

                    task_id += 1
            except Exception as e:
                print(f"Warning: Failed to load GLUE task {task_name}: {e}")

        # Load SuperGLUE tasks
        for task_name in self.config.superglue_tasks:
            try:
                dataset = load_superglue_task(task_name, self.split, self.cache_dir)
                if dataset is not None:
                    self.datasets[task_name] = dataset
                    self.task_name_to_id[task_name] = task_id

                    # Build task indices
                    num_samples = len(dataset) if self.max_samples is None else min(len(dataset), self.max_samples)
                    for idx in range(num_samples):
                        self.task_indices.append((task_name, idx))

                    task_id += 1
            except Exception as e:
                print(f"Warning: Failed to load SuperGLUE task {task_name}: {e}")

    def __len__(self) -> int:
        """Total samples across all tasks."""
        return len(self.task_indices)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get item at index.

        Returns:
            Dictionary with keys: input_ids, attention_mask, labels, task_id
        """
        task_name, task_idx = self.task_indices[idx]
        sample = self.datasets[task_name][task_idx]

        # Get text inputs based on task
        text_a, text_b = self._extract_text_fields(task_name, sample)

        # Tokenize
        if text_b is not None:
            encoding = self.tokenizer(
                text_a,
                text_b,
                max_length=self.config.max_length,
                truncation=True,
                padding=False  # Dynamic padding in collate_fn
            )
        else:
            encoding = self.tokenizer(
                text_a,
                max_length=self.config.max_length,
                truncation=True,
                padding=False
            )

        # Get label
        label = self._extract_label(task_name, sample)

        return {
            'input_ids': torch.tensor(encoding['input_ids']),
            'attention_mask': torch.tensor(encoding['attention_mask']),
            'labels': torch.tensor(label, dtype=torch.long),
            'task_id': torch.tensor(self.task_name_to_id[task_name], dtype=torch.long)
        }

    def _extract_text_fields(self, task_name: str, sample: Dict) -> Tuple[str, Optional[str]]:
        """Extract text fields from sample based on task."""
        # GLUE tasks
        if task_name == 'cola':
            return sample['sentence'], None
        elif task_name == 'sst2':
            return sample['sentence'], None
        elif task_name in ['mrpc', 'rte', 'wnli']:
            return sample['sentence1'], sample['sentence2']
        elif task_name == 'qqp':
            return sample['question1'], sample['question2']
        elif task_name == 'mnli':
            return sample['premise'], sample['hypothesis']
        elif task_name == 'qnli':
            return sample['question'], sample['sentence']
        elif task_name == 'stsb':
            return sample['sentence1'], sample['sentence2']

        # SuperGLUE tasks
        elif task_name == 'boolq':
            return sample['question'], sample['passage']
        elif task_name == 'cb':
            return sample['premise'], sample['hypothesis']
        elif task_name == 'copa':
            premise = sample['premise']
            choice1 = sample['choice1']
            choice2 = sample['choice2']
            # For COPA, we'll concatenate premise with both choices
            return premise, f"{choice1} [SEP] {choice2}"
        elif task_name == 'multirc':
            return sample['paragraph'], f"{sample['question']} {sample['answer']}"
        elif task_name == 'record':
            return sample['passage'], f"{sample['query']} {sample.get('entities', [''])[0]}"
        elif task_name == 'wic':
            return sample['sentence1'], sample['sentence2']
        elif task_name == 'wsc':
            return sample['text'], None
        else:
            raise ValueError(f"Unknown task: {task_name}")

    def _extract_label(self, task_name: str, sample: Dict) -> int:
        """Extract label from sample."""
        if 'label' in sample:
            label = sample['label']
            # Handle -1 labels (test set)
            return label if label != -1 else 0
        elif 'idx' in sample:
            # Some tasks use idx as identifier
            return 0  # Placeholder for test set
        else:
            return 0


def load_glue_task(task_name: str, split: str, cache_dir: Optional[str] = None):
    """
    Load single GLUE task.

    Args:
        task_name: GLUE task name (cola, sst2, mrpc, etc.)
        split: Dataset split
        cache_dir: Optional cache directory

    Returns:
        Dataset or None if loading fails
    """
    try:
        # Handle split naming variations
        actual_split = split
        if split == 'validation':
            actual_split = 'validation'

        dataset = load_dataset('glue', task_name, split=actual_split, cache_dir=cache_dir, trust_remote_code=True)
        return dataset
    except Exception as e:
        print(f"Error loading GLUE task {task_name}: {e}")
        return None


def load_superglue_task(task_name: str, split: str, cache_dir: Optional[str] = None):
    """
    Load single SuperGLUE task.

    Args:
        task_name: SuperGLUE task name (boolq, cb, copa, etc.)
        split: Dataset split
        cache_dir: Optional cache directory

    Returns:
        Dataset or None if loading fails
    """
    try:
        # Handle split naming variations
        actual_split = split
        if split == 'validation':
            actual_split = 'validation'

        dataset = load_dataset('super_glue', task_name, split=actual_split, cache_dir=cache_dir, trust_remote_code=True)
        return dataset
    except Exception as e:
        print(f"Error loading SuperGLUE task {task_name}: {e}")
        return None


def collate_fn(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """
    Dynamic padding collate function for batching.

    Args:
        batch: List of samples from dataset

    Returns:
        Batched dictionary with padded tensors
    """
    # Find max length in batch
    max_length = max(len(item['input_ids']) for item in batch)

    # Pad all sequences to max length
    input_ids = []
    attention_mask = []
    labels = []
    task_ids = []

    for item in batch:
        # Pad input_ids
        padding_length = max_length - len(item['input_ids'])
        padded_input_ids = torch.cat([
            item['input_ids'],
            torch.zeros(padding_length, dtype=torch.long)
        ])
        input_ids.append(padded_input_ids)

        # Pad attention_mask
        padded_attention_mask = torch.cat([
            item['attention_mask'],
            torch.zeros(padding_length, dtype=torch.long)
        ])
        attention_mask.append(padded_attention_mask)

        labels.append(item['labels'])
        task_ids.append(item['task_id'])

    return {
        'input_ids': torch.stack(input_ids),
        'attention_mask': torch.stack(attention_mask),
        'labels': torch.stack(labels),
        'task_ids': torch.stack(task_ids)
    }


def create_dataloaders(
    config: DataConfig,
    tokenizer: AutoTokenizer,
    max_samples: Optional[int] = None,
    cache_dir: Optional[str] = None
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders.

    Args:
        config: DataConfig instance
        tokenizer: HuggingFace tokenizer
        max_samples: Optional limit on samples per task
        cache_dir: Optional cache directory

    Returns:
        Tuple of (train_loader, val_loader)
    """
    train_dataset = MultiTaskDataset(
        config,
        split='train',
        tokenizer=tokenizer,
        max_samples=max_samples,
        cache_dir=cache_dir
    )

    val_dataset = MultiTaskDataset(
        config,
        split='validation',
        tokenizer=tokenizer,
        max_samples=max_samples,
        cache_dir=cache_dir
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        collate_fn=collate_fn,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        collate_fn=collate_fn,
        pin_memory=True
    )

    return train_loader, val_loader
