"""SAT (Stall-time Amplitude Throughput) Profiler for batch time variance measurement."""

import time
from typing import Callable, List
import torch
from torch import nn, Tensor
from torch.optim import Optimizer
from torch.utils.data import DataLoader
import numpy as np


class SATProfiler:
    """
    Measures GPU-normalized SAT (P95/Median batch time × GPU utilization fraction)
    to predict epoch-time degradation from data loading bottlenecks.
    """

    def __init__(self):
        """Initialize profiler."""
        self.batch_times: List[float] = []
        self.gpu_utils: List[float] = []

    def profile_step(
        self,
        model: nn.Module,
        batch: tuple,
        optimizer: Optimizer,
        criterion: Callable
    ) -> float:
        """
        Profile a single training step.

        Args:
            model: PyTorch model
            batch: (inputs, labels) tuple
            optimizer: PyTorch optimizer
            criterion: Loss function

        Returns:
            batch_time: Time for this batch in seconds
        """
        # Synchronize before timing (CUDA only)
        device = next(model.parameters()).device
        if device.type == 'cuda':
            torch.cuda.synchronize()

        start = time.time()

        # Unpack batch
        if isinstance(batch, (tuple, list)) and len(batch) >= 2:
            inputs, labels = batch[0], batch[1]
        else:
            raise ValueError(f"Expected batch to be (inputs, labels) tuple, got {type(batch)}")

        # Move to device
        device = next(model.parameters()).device
        inputs = inputs.to(device)
        labels = labels.to(device)

        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Synchronize after training step (CUDA only)
        if device.type == 'cuda':
            torch.cuda.synchronize()

        batch_time = time.time() - start

        # GPU utilization measurement (placeholder for CPU mode)
        if device.type == 'cuda':
            try:
                # Estimate from memory usage as proxy
                mem_allocated = torch.cuda.memory_allocated() / max(torch.cuda.max_memory_allocated(), 1)
                gpu_util = mem_allocated * 100
            except:
                gpu_util = 50.0
        else:
            # CPU mode - use placeholder value
            gpu_util = 100.0  # CPU always "utilized" when active

        self.batch_times.append(batch_time)
        self.gpu_utils.append(gpu_util)

        return batch_time

    def compute_SAT(self) -> float:
        """
        Compute GPU-normalized SAT after profiling multiple batches.

        Returns:
            SAT: P95/Median × (avg_GPU_util / 100)
        """
        if len(self.batch_times) < 2:
            raise ValueError("Need at least 2 batch times to compute SAT")

        p95 = np.percentile(self.batch_times, 95)
        median = np.median(self.batch_times)
        avg_gpu_util = np.mean(self.gpu_utils) if self.gpu_utils else 50.0

        # Avoid division by zero
        if median == 0:
            return 1.0

        # GPU-normalized SAT
        SAT = (p95 / median) * (avg_gpu_util / 100.0)

        return SAT

    def measure_epoch_time(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        optimizer: Optimizer,
        criterion: Callable
    ) -> float:
        """
        Measure full epoch time to validate degradation prediction.

        Args:
            model: PyTorch model
            dataloader: Training dataloader
            optimizer: PyTorch optimizer
            criterion: Loss function

        Returns:
            epoch_time: Total epoch time in seconds
        """
        epoch_start = time.time()

        for batch in dataloader:
            self.profile_step(model, batch, optimizer, criterion)

        epoch_time = time.time() - epoch_start
        return epoch_time

    def get_batch_times(self) -> List[float]:
        """Get recorded batch times."""
        return self.batch_times.copy()

    def get_gpu_utils(self) -> List[float]:
        """Get recorded GPU utilization values."""
        return self.gpu_utils.copy()

    def reset(self) -> None:
        """Clear all recorded profiling data."""
        self.batch_times.clear()
        self.gpu_utils.clear()
