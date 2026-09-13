"""
Framework Adapters for H-C2 Cross-Framework Contract Validation
Implements unified interface for PyTorch and TensorFlow models
"""

from typing import Any, Tuple
import numpy as np
import torch


class PyTorchAdapter:
    """Adapter for PyTorch models."""

    def __init__(self, device: str = "cpu"):
        self.device = device

    def infer_dtype(self, model: torch.nn.Module, test_input: np.ndarray) -> str:
        """Infer output dtype from PyTorch model."""
        model.eval()
        tensor_input = torch.from_numpy(test_input).to(self.device)
        with torch.no_grad():
            output = model(tensor_input)
        return str(output.dtype).replace('torch.', '')

    def infer_shape(self, model: torch.nn.Module, test_input: np.ndarray) -> Tuple[int, ...]:
        """Infer output shape from PyTorch model."""
        model.eval()
        tensor_input = torch.from_numpy(test_input).to(self.device)
        with torch.no_grad():
            output = model(tensor_input)
        return tuple(output.shape)

    def run_inference(self, model: torch.nn.Module, test_input: np.ndarray) -> np.ndarray:
        """Run forward pass on PyTorch model."""
        model.eval()
        tensor_input = torch.from_numpy(test_input).to(self.device)
        with torch.no_grad():
            output = model(tensor_input)
        return output.cpu().numpy()

    def convert_input(self, input_array: np.ndarray) -> torch.Tensor:
        """Convert NumPy array to PyTorch tensor."""
        return torch.from_numpy(input_array).to(self.device)


class TensorFlowAdapter:
    """Adapter for TensorFlow/Keras models."""

    def __init__(self):
        try:
            import tensorflow as tf
            self.tf = tf
        except ImportError:
            self.tf = None

    def infer_dtype(self, model: Any, test_input: np.ndarray) -> str:
        """Infer output dtype from TensorFlow model."""
        if self.tf is None:
            raise RuntimeError("TensorFlow not available")
        tf_input = self.tf.convert_to_tensor(test_input, dtype=self.tf.float32)
        output = model(tf_input, training=False)
        return str(output.dtype).replace('_ref', '').split('.')[-1]

    def infer_shape(self, model: Any, test_input: np.ndarray) -> Tuple[int, ...]:
        """Infer output shape from TensorFlow model."""
        if self.tf is None:
            raise RuntimeError("TensorFlow not available")
        tf_input = self.tf.convert_to_tensor(test_input, dtype=self.tf.float32)
        output = model(tf_input, training=False)
        return tuple(output.shape)

    def run_inference(self, model: Any, test_input: np.ndarray) -> np.ndarray:
        """Run forward pass on TensorFlow model."""
        if self.tf is None:
            raise RuntimeError("TensorFlow not available")
        tf_input = self.tf.convert_to_tensor(test_input, dtype=self.tf.float32)
        output = model(tf_input, training=False)
        return output.numpy()

    def convert_input(self, input_array: np.ndarray) -> Any:
        """Convert NumPy array to TensorFlow tensor."""
        if self.tf is None:
            raise RuntimeError("TensorFlow not available")
        return self.tf.convert_to_tensor(input_array, dtype=self.tf.float32)
