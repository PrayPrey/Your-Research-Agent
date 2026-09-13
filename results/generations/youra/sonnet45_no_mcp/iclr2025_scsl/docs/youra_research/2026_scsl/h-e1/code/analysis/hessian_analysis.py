"""
Hessian Analysis Module
Computes Hessian eigenspectrum, Marchenko-Pastur fitting, and alignment metrics
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple
from scipy.optimize import minimize


def compute_hessian_spectrum(
    model: nn.Module,
    data_loader,
    num_eigenthings: int = 100,
    device: str = 'cuda'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Hessian eigenvalues and eigenvectors using pytorch-hessian-eigenthings.

    Args:
        model: PyTorch model
        data_loader: DataLoader for Hessian computation
        num_eigenthings: Number of top eigenvalues/vectors to compute
        device: 'cuda' or 'cpu'

    Returns:
        eigenvalues: (num_eigenthings,) array in descending order
        eigenvectors: (num_params, num_eigenthings) array
    """
    try:
        from hessian_eigenthings import compute_hessian_eigenthings as compute_eigs
    except ImportError:
        raise ImportError("Please install: pip install git+https://github.com/noahgolmant/pytorch-hessian-eigenthings.git")

    model = model.to(device)
    model.eval()

    # Define loss function
    criterion = nn.CrossEntropyLoss()

    def loss_fn(outputs, labels):
        return criterion(outputs, labels)

    # Compute eigenthings
    eigenvalues, eigenvectors = compute_eigs(
        model=model,
        dataloader=data_loader,
        loss=loss_fn,
        num_eigenthings=num_eigenthings,
        power_iter_steps=20,
        power_iter_err_threshold=1e-4,
        momentum=0.0,
        use_gpu=(device == 'cuda')
    )

    # Convert to numpy
    eigenvalues = np.array(eigenvalues)
    eigenvectors = np.array([v.cpu().numpy() for v in eigenvectors]).T  # (P, K)

    return eigenvalues, eigenvectors


def fit_marchenko_pastur(eigenvalues: np.ndarray) -> Tuple[float, float, float]:
    """
    Fit Marchenko-Pastur distribution to eigenvalue spectrum.

    Args:
        eigenvalues: (N,) array of eigenvalues

    Returns:
        bulk_edge: λ_+ = σ²(1 + √γ)²
        sigma_sq: Estimated noise variance
        gamma: Estimated aspect ratio
    """
    # Use middle eigenvalues to avoid obvious outliers
    bulk_eigs = eigenvalues[20:80]

    # Marchenko-Pastur negative log-likelihood
    def neg_log_likelihood(params):
        sigma_sq, gamma = params

        # MP bounds
        lambda_min = sigma_sq * (1 - np.sqrt(gamma))**2
        lambda_max = sigma_sq * (1 + np.sqrt(gamma))**2

        # Filter eigenvalues within MP support
        valid_mask = (bulk_eigs >= lambda_min) & (bulk_eigs <= lambda_max)
        valid_eigs = bulk_eigs[valid_mask]

        if len(valid_eigs) == 0:
            return 1e10

        # MP density
        numerator = np.sqrt(np.maximum((lambda_max - valid_eigs) * (valid_eigs - lambda_min), 1e-10))
        denominator = 2 * np.pi * sigma_sq * gamma * valid_eigs + 1e-10
        density = numerator / denominator

        # Negative log-likelihood
        nll = -np.sum(np.log(density + 1e-10))

        return nll

    # Optimize
    result = minimize(
        neg_log_likelihood,
        x0=[1.0, 0.1],
        bounds=[(0.01, 10.0), (0.01, 1.0)],
        method='L-BFGS-B'
    )

    sigma_sq, gamma = result.x
    bulk_edge = sigma_sq * (1 + np.sqrt(gamma))**2

    return bulk_edge, sigma_sq, gamma


def compute_minority_gradient(
    model: nn.Module,
    minority_loader,
    device: str = 'cuda'
) -> torch.Tensor:
    """
    Compute average gradient on minority groups.

    Args:
        model: PyTorch model
        minority_loader: DataLoader with minority samples
        device: 'cuda' or 'cpu'

    Returns:
        g_minority: (num_params,) flattened gradient tensor
    """
    model = model.to(device)
    model.eval()

    criterion = nn.CrossEntropyLoss()

    total_grad = None
    count = 0

    for images, labels, _ in minority_loader:
        images = images.to(device)
        labels = labels.to(device)

        # Zero gradients
        model.zero_grad()

        # Forward
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backward
        loss.backward()

        # Accumulate gradients
        if total_grad is None:
            total_grad = [p.grad.clone() for p in model.parameters() if p.grad is not None]
        else:
            for i, p in enumerate([p for p in model.parameters() if p.grad is not None]):
                total_grad[i] += p.grad.clone()

        count += 1

    # Average
    total_grad = [g / count for g in total_grad]

    # Flatten
    g_minority = torch.cat([g.flatten() for g in total_grad])

    return g_minority


def compute_alignment(
    g_minority: torch.Tensor,
    eigenvectors: np.ndarray,
    eigenvalues: np.ndarray,
    bulk_edge: float
) -> float:
    """
    Compute alignment A(w) = ||P_S_out g_minority||² / ||g_minority||².

    Args:
        g_minority: (num_params,) gradient tensor
        eigenvectors: (num_params, num_eigenthings) array
        eigenvalues: (num_eigenthings,) array
        bulk_edge: MP bulk edge threshold

    Returns:
        alignment: Fraction of gradient in outlier subspace [0, 1]
    """
    # Identify outlier eigenvectors
    outlier_mask = eigenvalues > bulk_edge
    outlier_eigenvectors = eigenvectors[:, outlier_mask]  # (P, K)

    if outlier_eigenvectors.shape[1] == 0:
        return 0.0

    # Convert to torch
    outlier_eigenvectors = torch.from_numpy(outlier_eigenvectors).float()
    if g_minority.is_cuda:
        outlier_eigenvectors = outlier_eigenvectors.cuda()

    # Project gradient onto outlier subspace
    # projection = V_out @ V_out^T @ g
    projection = outlier_eigenvectors @ (outlier_eigenvectors.T @ g_minority)

    # Compute alignment
    alignment = (projection.norm()**2 / g_minority.norm()**2).item()

    return alignment
