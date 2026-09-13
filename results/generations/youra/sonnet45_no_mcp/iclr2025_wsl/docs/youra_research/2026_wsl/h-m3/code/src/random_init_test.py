"""RandomInitTest: Test batch norm features on randomly initialized models
Validates whether features are architectural vs training-induced
"""

import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple
from .model_loader import ModelLoader
from .feature_extractor import BatchNormFeatureExtractor
from .classifier import DepthClassifier


class RandomInitTest:
    """Test batch norm features on randomly initialized models."""

    def __init__(self, shallow_names: list, deep_names: list, random_state: int = 42):
        """Initialize random initialization test.

        Args:
            shallow_names: List of shallow model architectures
            deep_names: List of deep model architectures
            random_state: Random seed for reproducibility
        """
        self.shallow_names = shallow_names
        self.deep_names = deep_names
        self.random_state = random_state
        self.loader = ModelLoader(shallow_names, deep_names)
        self.extractor = BatchNormFeatureExtractor()

    def extract_random_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Extract batch norm features from randomly initialized models.

        Returns:
            features: (20, 6) array of batch norm features
            labels: (20,) array of labels (0=shallow, 1=deep)
        """
        print("\n" + "="*60)
        print("Random Initialization Test")
        print("="*60)
        print("Extracting features from randomly initialized models...")

        features = []
        labels = []

        # Extract from shallow models (label=0)
        print(f"\nProcessing {len(self.shallow_names)} shallow architectures (random weights)...")
        for i, name in enumerate(self.shallow_names, 1):
            print(f"  [{i}/{len(self.shallow_names)}] {name}...", end=" ")
            try:
                model = self.loader.load_random_model(name)
                feat = self.extractor.extract_features(model)
                features.append(feat)
                labels.append(0)
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")

        # Extract from deep models (label=1)
        print(f"\nProcessing {len(self.deep_names)} deep architectures (random weights)...")
        for i, name in enumerate(self.deep_names, 1):
            print(f"  [{i}/{len(self.deep_names)}] {name}...", end=" ")
            try:
                model = self.loader.load_random_model(name)
                feat = self.extractor.extract_features(model)
                features.append(feat)
                labels.append(1)
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")

        features = np.array(features)
        labels = np.array(labels)

        print(f"\n✓ Random features extracted: {features.shape}")
        print(f"  Shallow samples: {np.sum(labels == 0)}")
        print(f"  Deep samples: {np.sum(labels == 1)}")

        return features, labels

    def run_random_test(self, test_size: float = 0.2) -> dict:
        """Run full random initialization test.

        Args:
            test_size: Test set proportion (default: 0.2, same as pretrained)

        Returns:
            Dictionary with random test results
        """
        # Extract features from random models
        X, y = self.extract_random_features()

        # Split data (same split as pretrained models)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            stratify=y,
            random_state=self.random_state
        )

        print(f"\nData split:")
        print(f"  Train: {len(X_train)} samples ({np.sum(y_train == 0)} shallow, {np.sum(y_train == 1)} deep)")
        print(f"  Test:  {len(X_test)} samples ({np.sum(y_test == 0)} shallow, {np.sum(y_test == 1)} deep)")

        # Train classifier on random model features
        print("\nTraining classifier on random model features...")
        classifier = DepthClassifier(random_state=self.random_state)
        classifier.train(X_train, y_train)

        # Evaluate
        train_accuracy = classifier.score(X_train, y_train)
        test_accuracy = classifier.score(X_test, y_test)

        print(f"\nRandom Model Results:")
        print(f"  Train Accuracy: {train_accuracy:.2%}")
        print(f"  Test Accuracy:  {test_accuracy:.2%}")

        # Interpretation
        if test_accuracy < 0.55:
            interpretation = "✓ Random models fail to classify (training-induced patterns confirmed)"
            training_required = True
        else:
            interpretation = "✗ Random models classify well (features are architectural, not gradient-induced)"
            training_required = False

        print(f"\n{interpretation}")

        return {
            'test_accuracy': test_accuracy,
            'train_accuracy': train_accuracy,
            'interpretation': interpretation,
            'training_required': training_required,
            'num_train': len(X_train),
            'num_test': len(X_test)
        }
