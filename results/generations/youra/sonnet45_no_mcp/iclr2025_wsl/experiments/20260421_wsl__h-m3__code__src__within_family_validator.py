"""WithinFamilyValidator: Validate depth signal within architecture families
NEW for h-m2 - isolates depth signal from architecture type confounds
"""

import numpy as np
from sklearn.model_selection import train_test_split
from .classifier import DepthClassifier


class WithinFamilyValidator:
    """Validate depth signal within architecture families."""

    def __init__(self, random_state: int = 42):
        """Initialize validator with random seed."""
        self.random_state = random_state

    def classify_model_family(self, model_name: str) -> str:
        """Detect family from model name. Returns: 'resnet' | 'vgg' | 'densenet' | 'other'"""
        model_name_lower = model_name.lower()

        if 'resnet' in model_name_lower or 'resnext' in model_name_lower or 'wide_resnet' in model_name_lower:
            return 'resnet'
        elif 'vgg' in model_name_lower:
            return 'vgg'
        elif 'densenet' in model_name_lower:
            return 'densenet'
        else:
            return 'other'

    def validate_within_family(self, X: np.ndarray, y: np.ndarray,
                               model_names: list, test_size: float = 0.2) -> dict:
        """Train per-family classifiers. X: [N, 8], y: [N,], names: [N] -> results: dict"""
        # Group models by family
        families = {}
        for i, name in enumerate(model_names):
            family = self.classify_model_family(name)
            if family not in families:
                families[family] = []
            families[family].append(i)

        # Train classifier for each family
        results = {}
        for family, indices in families.items():
            if len(indices) < 4:  # Need at least 4 for 80/20 split
                print(f"  Warning: Skipping {family} (only {len(indices)} models)")
                continue

            X_family = X[indices]
            y_family = y[indices]

            # Check if both classes are present
            unique_classes = np.unique(y_family)
            if len(unique_classes) < 2:
                print(f"  Warning: Skipping {family} (only one class present: {unique_classes})")
                continue

            family_result = self.train_family_classifier(X_family, y_family, family)
            if family_result is not None:
                results[family] = family_result

        return results

    def train_family_classifier(self, X_family: np.ndarray, y_family: np.ndarray,
                               family_name: str) -> dict:
        """Train classifier on single family. Returns: {accuracy, num_samples} or None if failed"""
        # Split family data
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X_family, y_family,
                test_size=0.2,
                stratify=y_family,
                random_state=self.random_state
            )
        except ValueError as e:
            # If stratification fails (e.g., one class only), use regular split
            print(f"  Warning: Stratification failed for {family_name}: {e}")
            X_train, X_test, y_train, y_test = train_test_split(
                X_family, y_family,
                test_size=0.2,
                random_state=self.random_state
            )

        # Check if training set has both classes
        if len(np.unique(y_train)) < 2:
            print(f"  Warning: {family_name} training set has only one class, skipping")
            return None

        # Train classifier
        try:
            classifier = DepthClassifier(random_state=self.random_state)
            classifier.train(X_train, y_train)

            # Evaluate
            accuracy = classifier.score(X_test, y_test)
            train_accuracy = classifier.score(X_train, y_train)

            return {
                'accuracy': accuracy,
                'train_accuracy': train_accuracy,
                'num_samples': len(X_family),
                'num_train': len(X_train),
                'num_test': len(X_test)
            }
        except Exception as e:
            print(f"  Warning: Failed to train {family_name} classifier: {e}")
            return None
