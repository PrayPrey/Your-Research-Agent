"""Paired data loader for HH-RLHF preference pairs.

This module organizes the HH-RLHF dataset as matched chosen-rejected pairs.
"""

import sys
import os
from typing import List, Tuple, Dict

# Add h-e1 code path
h_e1_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../h-e1/code')
)
if h_e1_path not in sys.path:
    sys.path.insert(0, h_e1_path)

from data_loader import HHRLHFDataLoader


class PairedDataLoader:
    """Loader for paired chosen-rejected responses."""

    def __init__(self, base_loader: HHRLHFDataLoader):
        """Initialize paired data loader.

        Args:
            base_loader: H-E1 data loader instance
        """
        self.base_loader = base_loader
        self.split_boundaries = {}
        self.all_pairs = []

    def load_paired_dataset(self) -> List[Tuple[str, str]]:
        """Load dataset as matched chosen-rejected pairs.

        Returns:
            List of (chosen_text, rejected_text) tuples
        """
        if not self.base_loader.datasets:
            self.base_loader.load_dataset()

        pairs = []
        current_idx = 0

        print("\nOrganizing as matched pairs...")

        for split_name, split_data in self.base_loader.datasets.items():
            split_start = current_idx
            print(f"Processing {split_name} split...")

            for idx, example in enumerate(split_data):
                # Extract and preprocess chosen and rejected
                chosen_text = self.base_loader.preprocess_text(example['chosen'])
                rejected_text = self.base_loader.preprocess_text(example['rejected'])

                pairs.append((chosen_text, rejected_text))
                current_idx += 1

                if (idx + 1) % 5000 == 0:
                    print(f"  Processed {idx + 1} pairs...")

            split_end = current_idx
            self.split_boundaries[split_name] = (split_start, split_end)
            print(f"  ✓ {split_name}: {split_end - split_start} pairs")

        self.all_pairs = pairs
        print(f"\n✓ Total paired dataset: {len(pairs)} matched pairs")

        return pairs

    def get_split_pairs(self, split_name: str) -> List[Tuple[str, str]]:
        """Get pairs for specific split.

        Args:
            split_name: Name of the split (e.g., 'train', 'test')

        Returns:
            List of (chosen, rejected) pairs for this split
        """
        if not self.all_pairs:
            self.load_paired_dataset()

        if split_name not in self.split_boundaries:
            raise ValueError(f"Split '{split_name}' not found. Available: {list(self.split_boundaries.keys())}")

        start, end = self.split_boundaries[split_name]
        return self.all_pairs[start:end]

    def get_pair_count(self) -> int:
        """Get total number of pairs.

        Returns:
            Total pair count
        """
        if not self.all_pairs:
            self.load_paired_dataset()

        return len(self.all_pairs)

    def get_split_names(self) -> List[str]:
        """Get list of available split names.

        Returns:
            List of split names
        """
        if not self.split_boundaries:
            self.load_paired_dataset()

        return list(self.split_boundaries.keys())
