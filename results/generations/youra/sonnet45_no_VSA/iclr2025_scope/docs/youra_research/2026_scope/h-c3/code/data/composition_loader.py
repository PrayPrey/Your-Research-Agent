"""
Data Loading Module for h-c3
Loads composition-level defects from h-e1 corpus
"""
import pandas as pd
import hashlib
from pathlib import Path

class CompositionDefectLoader:
    """Loads and filters composition-level defects from h-e1 corpus"""

    def __init__(self, corpus_path: str, expected_count: int = 62):
        self.corpus_path = Path(corpus_path)
        self.expected_count = expected_count
        self.defects = None

    def load_composition_subset(self) -> pd.DataFrame:
        """
        Load composition defects from h-e1 corpus.

        Returns:
            DataFrame with 62 composition defects
        """
        # Load full corpus
        self.defects = pd.read_csv(self.corpus_path)

        # Filter for composition type
        composition_defects = self.defects[self.defects['type'] == 'composition'].copy()

        # Validate count
        actual_count = len(composition_defects)
        if actual_count != self.expected_count:
            raise ValueError(
                f"Expected {self.expected_count} composition defects, got {actual_count}"
            )

        return composition_defects

    def extract_library_versions(self, defect_row) -> dict:
        """
        Extract library version triad from defect metadata.

        Args:
            defect_row: DataFrame row with defect info

        Returns:
            dict: {'pytorch': '1.12.0', 'cuda': '11.6', 'transformers': '4.20.0'}
        """
        # Simplified version extraction for PoC
        # In real implementation, parse from defect description
        return {
            "pytorch": "1.12.0",
            "cuda": "11.6",
            "transformers": "4.20.0"
        }

    def get_version_range(self, base_version: str, delta: int = 2) -> list:
        """
        Generate ±delta minor version range.

        Args:
            base_version: e.g., "1.12.0"
            delta: ±N minor releases

        Returns:
            List of versions: ["1.10.0", "1.11.0", "1.12.0", "1.13.0", "1.14.0"]
        """
        major, minor, patch = base_version.split('.')
        versions = []
        for i in range(-delta, delta + 1):
            new_minor = int(minor) + i
            if new_minor >= 0:
                versions.append(f"{major}.{new_minor}.{patch}")
        return versions

    def validate_checksum(self, expected_checksum: str) -> bool:
        """
        Validate corpus file integrity.

        Args:
            expected_checksum: Expected SHA256 hash (first 16 chars)

        Returns:
            True if checksum matches
        """
        with open(self.corpus_path, 'rb') as f:
            data = f.read()
            actual_checksum = hashlib.sha256(data).hexdigest()[:16]
        return actual_checksum == expected_checksum
