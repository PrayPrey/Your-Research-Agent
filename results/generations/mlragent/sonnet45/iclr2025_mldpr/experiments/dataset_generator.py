"""
Dataset Generator for Temporal Dataset Card Experiments
Simulates evolving datasets with multiple versions
"""

import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class DatasetEvolutionSimulator:
    """Simulates dataset evolution across multiple versions"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

    def generate_base_dataset(
        self,
        n_samples: int = 1000,
        n_features: int = 10,
        n_classes: int = 3
    ) -> Tuple[List[Dict], List[str]]:
        """Generate initial dataset version"""
        data = []
        labels = []

        class_names = [f"class_{i}" for i in range(n_classes)]

        for i in range(n_samples):
            sample = {
                f"feature_{j}": float(np.random.randn())
                for j in range(n_features)
            }
            sample['id'] = f"sample_{i}"
            data.append(sample)

            label = np.random.choice(class_names)
            labels.append(label)

        return data, labels

    def evolve_dataset_add_samples(
        self,
        data: List[Dict],
        labels: List[str],
        add_ratio: float = 0.1
    ) -> Tuple[List[Dict], List[str]]:
        """Evolve dataset by adding new samples (MINOR version change)"""
        n_add = int(len(data) * add_ratio)
        n_features = len([k for k in data[0].keys() if k != 'id'])

        new_data = data.copy()
        new_labels = labels.copy()

        class_names = list(set(labels))

        start_id = len(data)
        for i in range(n_add):
            sample = {
                f"feature_{j}": float(np.random.randn())
                for j in range(n_features)
            }
            sample['id'] = f"sample_{start_id + i}"
            new_data.append(sample)

            label = np.random.choice(class_names)
            new_labels.append(label)

        return new_data, new_labels

    def evolve_dataset_remove_samples(
        self,
        data: List[Dict],
        labels: List[str],
        remove_ratio: float = 0.05
    ) -> Tuple[List[Dict], List[str]]:
        """Evolve dataset by removing samples (BREAKING change if significant)"""
        n_remove = int(len(data) * remove_ratio)
        indices_to_keep = np.random.choice(
            len(data),
            len(data) - n_remove,
            replace=False
        )

        new_data = [data[i] for i in sorted(indices_to_keep)]
        new_labels = [labels[i] for i in sorted(indices_to_keep)]

        return new_data, new_labels

    def evolve_dataset_fix_annotations(
        self,
        data: List[Dict],
        labels: List[str],
        fix_ratio: float = 0.02
    ) -> Tuple[List[Dict], List[str]]:
        """Evolve dataset by fixing annotation errors (PATCH change)"""
        n_fix = int(len(labels) * fix_ratio)
        indices_to_fix = np.random.choice(len(labels), n_fix, replace=False)

        new_labels = labels.copy()
        class_names = list(set(labels))

        for idx in indices_to_fix:
            # Change to a different class
            current_class = new_labels[idx]
            other_classes = [c for c in class_names if c != current_class]
            new_labels[idx] = np.random.choice(other_classes)

        return data.copy(), new_labels

    def evolve_dataset_modify_distribution(
        self,
        data: List[Dict],
        labels: List[str],
        shift_magnitude: float = 0.5
    ) -> Tuple[List[Dict], List[str]]:
        """Evolve dataset by modifying feature distributions (MAJOR change)"""
        new_data = []

        for sample in data:
            new_sample = sample.copy()
            for key in sample.keys():
                if key != 'id':
                    # Add distribution shift
                    new_sample[key] = sample[key] + np.random.randn() * shift_magnitude

            new_data.append(new_sample)

        return new_data, labels.copy()

    def generate_dataset_versions(
        self,
        n_versions: int = 5,
        base_size: int = 1000
    ) -> List[Tuple[str, List[Dict], List[str]]]:
        """Generate multiple versions of a dataset with realistic evolution patterns"""

        versions = []

        # Version 1.0.0: Initial release
        data, labels = self.generate_base_dataset(n_samples=base_size)
        versions.append(("1.0.0", data, labels))

        # Version 1.0.1: Fix annotation errors (PATCH)
        data, labels = self.evolve_dataset_fix_annotations(data, labels, fix_ratio=0.02)
        versions.append(("1.0.1", data, labels))

        # Version 1.1.0: Add new samples (MINOR)
        data, labels = self.evolve_dataset_add_samples(data, labels, add_ratio=0.15)
        versions.append(("1.1.0", data, labels))

        # Version 1.1.1: Fix more annotation errors (PATCH)
        data, labels = self.evolve_dataset_fix_annotations(data, labels, fix_ratio=0.01)
        versions.append(("1.1.1", data, labels))

        # Version 2.0.0: Major revision - modify distribution (MAJOR)
        data, labels = self.evolve_dataset_modify_distribution(data, labels, shift_magnitude=0.3)
        versions.append(("2.0.0", data, labels))

        return versions[:n_versions]


class PaperSimulator:
    """Simulates research papers citing dataset versions"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

    def generate_papers(
        self,
        n_papers: int = 100,
        dataset_versions: List[str] = None
    ) -> List[Dict]:
        """Generate simulated papers with dataset citations"""

        if dataset_versions is None:
            dataset_versions = ["1.0.0", "1.0.1", "1.1.0", "1.1.1", "2.0.0"]

        papers = []

        # Simulate realistic version adoption: newer versions cited more initially
        # but older versions still used due to reproducibility
        version_weights = np.array([0.15, 0.20, 0.30, 0.20, 0.15])
        version_weights = version_weights / version_weights.sum()

        for i in range(n_papers):
            # Select a version based on adoption pattern
            version_idx = np.random.choice(len(dataset_versions), p=version_weights)
            version = dataset_versions[version_idx]

            # Simulate paper results (varies by version due to dataset differences)
            base_accuracy = 0.85
            # Add version-specific bias
            version_effect = np.random.randn() * 0.02
            # Add paper-specific variation
            paper_variation = np.random.randn() * 0.03

            accuracy = base_accuracy + version_effect + paper_variation
            accuracy = np.clip(accuracy, 0, 1)

            paper = {
                'id': f"paper_{i}",
                'title': f"Research Paper {i}",
                'dataset_version': version,
                'reported_accuracy': float(accuracy),
                'text': f"We use dataset version {version} for our experiments."
            }

            papers.append(paper)

        return papers


class DeprecationScenarioGenerator:
    """Generate deprecation scenarios for testing retrospective annotations"""

    @staticmethod
    def generate_bias_discovery_scenario() -> Dict:
        """Simulate discovery of dataset bias"""
        return {
            'type': 'WARNING',
            'description': 'Gender bias discovered in training samples',
            'affected_versions': ['1.0.0', '1.0.1', '1.1.0'],
            'severity': 4,
            'discovery_date': (datetime.now() - timedelta(days=30)).isoformat(),
            'evidence': 'Statistical analysis revealed 80-20 gender imbalance',
            'recommended_action': 'Use version 2.0.0 or later with balanced samples'
        }

    @staticmethod
    def generate_privacy_violation_scenario() -> Dict:
        """Simulate discovery of privacy violation"""
        return {
            'type': 'CRITICAL',
            'description': 'Personal identifiable information (PII) found in samples',
            'affected_versions': ['1.0.0', '1.0.1'],
            'severity': 5,
            'discovery_date': (datetime.now() - timedelta(days=60)).isoformat(),
            'evidence': 'Manual review found email addresses in 15 samples',
            'recommended_action': 'IMMEDIATE: Stop using affected versions. Use version 1.1.0 or later.'
        }

    @staticmethod
    def generate_annotation_error_scenario() -> Dict:
        """Simulate discovery of systematic annotation errors"""
        return {
            'type': 'CORRECTION',
            'description': 'Systematic annotation errors in class_2 samples',
            'affected_versions': ['1.0.0'],
            'severity': 3,
            'discovery_date': (datetime.now() - timedelta(days=45)).isoformat(),
            'evidence': 'Expert review found 5% mislabeling in class_2',
            'recommended_action': 'Use version 1.0.1 or later with corrected annotations'
        }
