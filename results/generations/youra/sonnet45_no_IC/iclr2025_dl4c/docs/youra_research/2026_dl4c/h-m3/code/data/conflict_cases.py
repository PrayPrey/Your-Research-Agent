"""
Conflict Case Dataset for Phase 3 Edge Case Evaluation

Filters samples where:
- Execution succeeds (pass@1 = 1.0)
- Human preference is low (<0.3)

These are "conflict cases" where execution-only models generate correct but low-quality code.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from torch.utils.data import Dataset, DataLoader


class ConflictCaseDataset(Dataset):
    """
    Dataset of conflict cases for edge case evaluation.

    Conflict cases: Execution passes, human preference low
    Target: 50 samples for robust median estimation
    """

    def __init__(self, target_count: int = 50):
        self.target_count = target_count
        self.conflict_cases = []
        self.metadata = {}

    def filter_conflict_cases(self,
                              baseline_results: Dict,
                              pass_threshold: float = 1.0,
                              preference_threshold: float = 0.3) -> List[Dict]:
        """
        Filter conflict cases from baseline results.

        Args:
            baseline_results: Results from h-m1 execution-only baseline
                              Format: {sample_id: {pass_at_1, human_preference}}
            pass_threshold: Minimum pass@1 score (default: 1.0)
            preference_threshold: Maximum preference score (default: 0.3)

        Returns:
            List of conflict case samples
        """
        conflict_cases = []

        for sample_id, results in baseline_results.items():
            pass_score = results.get("pass_at_1", 0.0)
            preference = results.get("human_preference", 0.0)

            # Conflict condition: Execution passes BUT quality is low
            if pass_score >= pass_threshold and preference < preference_threshold:
                conflict_cases.append({
                    "sample_id": sample_id,
                    "pass_at_1": pass_score,
                    "baseline_preference": preference,
                    "prompt": results.get("prompt", ""),
                    "baseline_code": results.get("generated_code", "")
                })

        # Limit to target count
        if len(conflict_cases) > self.target_count:
            conflict_cases = conflict_cases[:self.target_count]

        self.conflict_cases = conflict_cases
        self.metadata = {
            "total_filtered": len(conflict_cases),
            "pass_threshold": pass_threshold,
            "preference_threshold": preference_threshold,
            "target_count": self.target_count
        }

        print(f"✓ Filtered {len(conflict_cases)} conflict cases")
        print(f"  Pass threshold: {pass_threshold}")
        print(f"  Preference threshold: {preference_threshold}")

        return conflict_cases

    def load_from_h_m1(self, h_m1_results_path: str) -> List[Dict]:
        """
        Load and filter conflict cases from h-m1 baseline results.

        Args:
            h_m1_results_path: Path to h-m1 baseline results JSON

        Returns:
            List of conflict cases
        """
        h_m1_path = Path(h_m1_results_path)

        if not h_m1_path.exists():
            print(f"⚠ h-m1 results not found: {h_m1_results_path}")
            print("  Generating synthetic conflict cases for testing...")
            return self._generate_synthetic_conflict_cases()

        with open(h_m1_path, 'r') as f:
            baseline_results = json.load(f)

        return self.filter_conflict_cases(baseline_results)

    def _generate_synthetic_conflict_cases(self) -> List[Dict]:
        """
        Generate synthetic conflict cases for testing when h-m1 results unavailable.
        """
        import random
        random.seed(42)

        synthetic_cases = []
        for i in range(min(self.target_count, 50)):
            synthetic_cases.append({
                "sample_id": f"synthetic_conflict_{i:03d}",
                "pass_at_1": 1.0,
                "baseline_preference": random.uniform(0.05, 0.25),
                "prompt": f"def function_{i}(x):\n    # TODO: implement",
                "baseline_code": f"def function_{i}(x):\n    return x  # minimal correct solution"
            })

        self.conflict_cases = synthetic_cases
        self.metadata = {
            "total_filtered": len(synthetic_cases),
            "synthetic": True,
            "target_count": self.target_count
        }

        print(f"⚠ Generated {len(synthetic_cases)} synthetic conflict cases")
        return synthetic_cases

    def save(self, output_path: str):
        """Save conflict cases to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "metadata": self.metadata,
            "conflict_cases": self.conflict_cases
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Conflict cases saved: {output_path}")

    def load(self, input_path: str):
        """Load conflict cases from JSON."""
        with open(input_path, 'r') as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self.conflict_cases = data.get("conflict_cases", [])

        print(f"✓ Loaded {len(self.conflict_cases)} conflict cases")

    def __len__(self) -> int:
        return len(self.conflict_cases)

    def __getitem__(self, idx: int) -> Dict:
        return self.conflict_cases[idx]

    def get_dataloader(self, batch_size: int = 8, shuffle: bool = False) -> DataLoader:
        """Create DataLoader for conflict cases."""
        return DataLoader(
            self,
            batch_size=batch_size,
            shuffle=shuffle,
            collate_fn=lambda x: x  # Return list of dicts
        )
