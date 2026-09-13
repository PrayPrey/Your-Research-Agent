"""MBPP Dataset loader with custom splits for h-e1."""

import torch
from datasets import load_dataset
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Any, List


def load_mbpp_custom_splits(calibration_ids: List[int], validation_ids: List[int], cache_dir: str = None):
    """
    Load MBPP with custom splits for h-e1.

    Args:
        calibration_ids: List of task IDs for calibration split
        validation_ids: List of task IDs for validation split
        cache_dir: Cache directory for HuggingFace datasets (not used, kept for compatibility)

    Returns:
        splits: Dict with keys 'calibration', 'validation'
    """
    # Load full MBPP dataset (don't pass cache_dir to avoid path issues)
    mbpp = load_dataset("google-research-datasets/mbpp", split="test")

    # Convert to sets for faster lookup
    calibration_set = set(calibration_ids)
    validation_set = set(validation_ids)

    # Filter by task_id
    calibration = mbpp.filter(lambda x: x['task_id'] in calibration_set)
    validation = mbpp.filter(lambda x: x['task_id'] in validation_set)

    return {
        'calibration': calibration,
        'validation': validation
    }


class MBPPDataset(Dataset):
    """PyTorch dataset wrapper for MBPP."""

    def __init__(self, hf_dataset):
        """
        Args:
            hf_dataset: HuggingFace Dataset object
        """
        self.data = hf_dataset

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """
        Returns:
            item: Dict with keys:
                - 'task_id': Problem ID
                - 'text': Task description (prompt)
                - 'test_list': List of assert statements
                - 'test_setup_code': Import dependencies
        """
        item = self.data[idx]
        return {
            'task_id': item['task_id'],
            'text': item['text'],
            'test_list': item['test_list'],
            'test_setup_code': item.get('test_setup_code', ''),
            'code': item.get('code', '')  # Reference solution (not used for generation)
        }


def create_dataloader(dataset: MBPPDataset, batch_size: int = 1, shuffle: bool = False) -> DataLoader:
    """
    Create PyTorch DataLoader from MBPP dataset.

    Args:
        dataset: MBPPDataset instance
        batch_size: Batch size (default 1 for generation)
        shuffle: Whether to shuffle dataset

    Returns:
        dataloader: PyTorch DataLoader
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,  # Set to 0 for debugging
        collate_fn=lambda x: x  # Return list of dicts as-is
    )
