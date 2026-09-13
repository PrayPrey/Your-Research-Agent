"""
Test Case Generation for H-C2
Generates synthetic defects for cross-framework validation
"""

from dataclasses import dataclass
from typing import Any, List, Optional
import numpy as np
import torch
import torch.nn as nn


@dataclass
class TestCase:
    """Test case with source and target models."""
    case_id: str
    source_framework: str
    target_framework: str
    src_model: Any
    tgt_model: Any
    test_inputs: List[np.ndarray]
    ground_truth_label: str  # "defect" or "valid"
    defect_type: Optional[str] = None  # DtypeCorruption, ShapeInconsistency, NumericalDrift
    source_issue: str = "synthetic"


class SimpleModel(nn.Module):
    """Simple PyTorch model for testing."""
    def __init__(self, input_size=10, hidden_size=20, output_size=5):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


class BrokenDtypeModel(nn.Module):
    """Model that outputs different dtype (simulates dtype corruption)."""
    def __init__(self, input_size=10, hidden_size=20, output_size=5):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x.half()  # Force float16 output


class BrokenShapeModel(nn.Module):
    """Model that outputs different shape (simulates shape mismatch)."""
    def __init__(self, input_size=10, hidden_size=20, output_size=5):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x[:, :3]  # Truncate output to 3 features instead of 5


class BrokenNumericalModel(nn.Module):
    """Model with numerical drift (simulates numerical discrepancy)."""
    def __init__(self, input_size=10, hidden_size=20, output_size=5):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        # Add noise to simulate numerical drift
        return x + torch.randn_like(x) * 0.1


def generate_synthetic_defects(num_samples: int = 100, seed: int = 42) -> List[TestCase]:
    """Generate synthetic test cases with known defects."""
    np.random.seed(seed)
    torch.manual_seed(seed)

    test_cases = []
    samples_per_type = num_samples // 4

    # Generate test inputs (batch of 1, 10 features)
    def generate_test_inputs(count: int = 3):
        return [np.random.randn(1, 10).astype(np.float32) for _ in range(count)]

    # 1. Valid conversions (no defects)
    for i in range(samples_per_type):
        src_model = SimpleModel()
        tgt_model = SimpleModel()

        # Copy weights to ensure same behavior
        tgt_model.load_state_dict(src_model.state_dict())

        test_cases.append(TestCase(
            case_id=f"valid_{i:03d}",
            source_framework="pytorch",
            target_framework="pytorch",  # Simplified: both PyTorch
            src_model=src_model,
            tgt_model=tgt_model,
            test_inputs=generate_test_inputs(),
            ground_truth_label="valid",
            defect_type=None
        ))

    # 2. Dtype corruption defects
    for i in range(samples_per_type):
        src_model = SimpleModel()
        tgt_model = BrokenDtypeModel()

        test_cases.append(TestCase(
            case_id=f"dtype_{i:03d}",
            source_framework="pytorch",
            target_framework="pytorch",
            src_model=src_model,
            tgt_model=tgt_model,
            test_inputs=generate_test_inputs(),
            ground_truth_label="defect",
            defect_type="DtypeCorruption"
        ))

    # 3. Shape inconsistency defects
    for i in range(samples_per_type):
        src_model = SimpleModel()
        tgt_model = BrokenShapeModel()

        test_cases.append(TestCase(
            case_id=f"shape_{i:03d}",
            source_framework="pytorch",
            target_framework="pytorch",
            src_model=src_model,
            tgt_model=tgt_model,
            test_inputs=generate_test_inputs(),
            ground_truth_label="defect",
            defect_type="ShapeInconsistency"
        ))

    # 4. Numerical drift defects
    for i in range(samples_per_type):
        src_model = SimpleModel()
        tgt_model = BrokenNumericalModel()

        test_cases.append(TestCase(
            case_id=f"numerical_{i:03d}",
            source_framework="pytorch",
            target_framework="pytorch",
            src_model=src_model,
            tgt_model=tgt_model,
            test_inputs=generate_test_inputs(),
            ground_truth_label="defect",
            defect_type="NumericalDrift"
        ))

    return test_cases


def prepare_test_set(num_samples: int = 100, train_ratio: float = 0.7, seed: int = 42):
    """Prepare train/test split for experiments."""
    all_cases = generate_synthetic_defects(num_samples, seed)

    # Shuffle
    np.random.seed(seed)
    indices = np.random.permutation(len(all_cases))

    # Split
    train_size = int(len(all_cases) * train_ratio)
    train_indices = indices[:train_size]
    test_indices = indices[train_size:]

    train_cases = [all_cases[i] for i in train_indices]
    test_cases = [all_cases[i] for i in test_indices]

    return train_cases, test_cases
