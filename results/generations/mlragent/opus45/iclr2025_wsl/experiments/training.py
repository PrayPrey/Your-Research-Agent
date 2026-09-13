"""
Training and evaluation pipelines for SymVAE and baselines.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import time


def vae_loss(recon_weights: List[torch.Tensor], recon_biases: List[torch.Tensor],
             target_weights: List[torch.Tensor], target_biases: List[torch.Tensor],
             mu: torch.Tensor, logvar: torch.Tensor,
             beta: float = 1.0) -> Tuple[torch.Tensor, Dict[str, float]]:
    """Compute VAE loss with reconstruction and KL divergence terms."""
    # Reconstruction loss
    recon_loss = 0
    for rw, tw in zip(recon_weights, target_weights):
        recon_loss = recon_loss + F.mse_loss(rw, tw, reduction='mean')
    for rb, tb in zip(recon_biases, target_biases):
        recon_loss = recon_loss + F.mse_loss(rb, tb, reduction='mean')

    # KL divergence
    kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())

    total_loss = recon_loss + beta * kl_loss

    metrics = {
        'recon_loss': recon_loss.item(),
        'kl_loss': kl_loss.item(),
        'total_loss': total_loss.item()
    }

    return total_loss, metrics


def train_vae_epoch(model: nn.Module, train_loader: DataLoader,
                    optimizer: torch.optim.Optimizer, device: torch.device,
                    beta: float = 1.0) -> Dict[str, float]:
    """Train VAE for one epoch."""
    model.train()
    epoch_metrics = {'recon_loss': 0, 'kl_loss': 0, 'total_loss': 0}
    n_batches = 0

    for batch in train_loader:
        weights = [w.to(device) for w in batch['weights']]
        biases = [b.to(device) for b in batch['biases']]
        task_cond = batch['task_descriptor'].to(device)

        optimizer.zero_grad()

        output = model(weights, biases, task_cond)

        loss, metrics = vae_loss(
            output['recon_weights'], output['recon_biases'],
            weights, biases,
            output['mu'], output['logvar'],
            beta=beta
        )

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        for k, v in metrics.items():
            epoch_metrics[k] += v
        n_batches += 1

    for k in epoch_metrics:
        epoch_metrics[k] /= n_batches

    return epoch_metrics


def evaluate_vae(model: nn.Module, val_loader: DataLoader,
                 device: torch.device, beta: float = 1.0) -> Dict[str, float]:
    """Evaluate VAE on validation set."""
    model.eval()
    val_metrics = {'recon_loss': 0, 'kl_loss': 0, 'total_loss': 0}
    n_batches = 0

    with torch.no_grad():
        for batch in val_loader:
            weights = [w.to(device) for w in batch['weights']]
            biases = [b.to(device) for b in batch['biases']]
            task_cond = batch['task_descriptor'].to(device)

            output = model(weights, biases, task_cond)

            _, metrics = vae_loss(
                output['recon_weights'], output['recon_biases'],
                weights, biases,
                output['mu'], output['logvar'],
                beta=beta
            )

            for k, v in metrics.items():
                val_metrics[k] += v
            n_batches += 1

    for k in val_metrics:
        val_metrics[k] /= n_batches

    return val_metrics


def train_hypernetwork_epoch(model: nn.Module, train_loader: DataLoader,
                             optimizer: torch.optim.Optimizer, device: torch.device) -> Dict[str, float]:
    """Train HyperNetwork for one epoch."""
    model.train()
    epoch_loss = 0
    n_batches = 0

    for batch in train_loader:
        target_weights = [w.to(device) for w in batch['weights']]
        target_biases = [b.to(device) for b in batch['biases']]
        task_cond = batch['task_descriptor'].to(device)

        optimizer.zero_grad()

        # Generate weights with noise for diversity
        batch_size = task_cond.shape[0]
        noise = torch.randn(batch_size, model.noise_dim, device=device)
        pred_weights, pred_biases = model(task_cond, noise)

        # Compute loss
        loss = 0
        for pw, tw in zip(pred_weights, target_weights):
            loss = loss + F.mse_loss(pw, tw)
        for pb, tb in zip(pred_biases, target_biases):
            loss = loss + F.mse_loss(pb, tb)

        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()
        n_batches += 1

    return {'loss': epoch_loss / n_batches}


def evaluate_hypernetwork(model: nn.Module, val_loader: DataLoader,
                          device: torch.device) -> Dict[str, float]:
    """Evaluate HyperNetwork on validation set."""
    model.eval()
    val_loss = 0
    n_batches = 0

    with torch.no_grad():
        for batch in val_loader:
            target_weights = [w.to(device) for w in batch['weights']]
            target_biases = [b.to(device) for b in batch['biases']]
            task_cond = batch['task_descriptor'].to(device)

            batch_size = task_cond.shape[0]
            noise = torch.randn(batch_size, model.noise_dim, device=device)
            pred_weights, pred_biases = model(task_cond, noise)

            loss = 0
            for pw, tw in zip(pred_weights, target_weights):
                loss = loss + F.mse_loss(pw, tw)
            for pb, tb in zip(pred_biases, target_biases):
                loss = loss + F.mse_loss(pb, tb)

            val_loss += loss.item()
            n_batches += 1

    return {'loss': val_loss / n_batches}


def evaluate_generation_quality(gen_model: nn.Module, test_tasks: List[Dict],
                                architecture: List[int], device: torch.device,
                                n_samples: int = 5) -> Dict[str, float]:
    """
    Evaluate the quality of generated weights by testing their functional performance.
    """
    from models import TargetMLP
    from data import SyntheticTaskDataset
    from torch.utils.data import DataLoader

    gen_model.eval()
    task_type = test_tasks[0].get('task_type', 'classification')

    accuracies = []
    losses = []

    with torch.no_grad():
        for task_data in test_tasks:
            task_cond = task_data['task_descriptor'].unsqueeze(0).to(device)

            # Generate weights
            gen_weights, gen_biases = gen_model.sample(n_samples, task_cond.expand(n_samples, -1), device)

            # Create test data for this task
            task_seed = task_data.get('task_seed', 0)
            if task_type == 'classification':
                test_dataset = SyntheticTaskDataset(
                    n_samples=200,
                    input_dim=architecture[0],
                    n_classes=architecture[-1],
                    task_type='classification',
                    seed=task_seed
                )
            else:
                test_dataset = SyntheticTaskDataset(
                    n_samples=200,
                    input_dim=architecture[0],
                    n_classes=1,
                    task_type='regression',
                    seed=task_seed
                )
            test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

            # Evaluate each generated model
            for i in range(n_samples):
                target_mlp = TargetMLP(architecture).to(device)
                weights = [w[i:i+1] for w in gen_weights]
                biases = [b[i:i+1] for b in gen_biases]
                target_mlp.set_weights(weights, biases)

                total_correct = 0
                total_loss = 0
                total_samples = 0

                for X, y in test_loader:
                    X, y = X.to(device), y.to(device)
                    output = target_mlp(X)

                    if task_type == 'classification':
                        pred = output.argmax(dim=1)
                        total_correct += (pred == y).sum().item()
                        total_loss += F.cross_entropy(output, y).item() * X.shape[0]
                    else:
                        total_loss += F.mse_loss(output, y).item() * X.shape[0]

                    total_samples += X.shape[0]

                if task_type == 'classification':
                    accuracies.append(total_correct / total_samples)
                losses.append(total_loss / total_samples)

    results = {'test_loss': np.mean(losses), 'test_loss_std': np.std(losses)}
    if task_type == 'classification':
        results['test_accuracy'] = np.mean(accuracies)
        results['test_accuracy_std'] = np.std(accuracies)

    return results


def evaluate_symmetry_invariance(model: nn.Module, test_data: List[Dict],
                                 device: torch.device, n_permutations: int = 5) -> Dict[str, float]:
    """
    Evaluate how invariant the latent representations are to weight permutations.
    Lower variance indicates better symmetry handling.
    """
    from data import apply_random_permutation

    model.eval()
    latent_variances = []

    with torch.no_grad():
        for data in test_data[:20]:  # Use subset for efficiency
            weights = [w.to(device) for w in data['weights']]
            biases = [b.to(device) for b in data['biases']]
            task_cond = data['task_descriptor'].unsqueeze(0).to(device)

            latents = []

            # Get latent for original weights
            if hasattr(model, 'encode'):
                enc_out = model.encode(weights, biases)
                if 'mu' in enc_out:
                    original_latent = enc_out['mu']
                else:
                    original_latent = torch.cat([enc_out['mu_task'], enc_out['mu_arch']], dim=-1)
                latents.append(original_latent.cpu())

                # Get latents for permuted weights
                for p in range(n_permutations):
                    perm_weights, perm_biases = apply_random_permutation(weights, biases, seed=p)
                    enc_out = model.encode(perm_weights, perm_biases)
                    if 'mu' in enc_out:
                        perm_latent = enc_out['mu']
                    else:
                        perm_latent = torch.cat([enc_out['mu_task'], enc_out['mu_arch']], dim=-1)
                    latents.append(perm_latent.cpu())

                # Compute variance across permutations
                latents_tensor = torch.stack(latents)
                variance = latents_tensor.var(dim=0).mean().item()
                latent_variances.append(variance)

    if latent_variances:
        return {
            'latent_variance_mean': np.mean(latent_variances),
            'latent_variance_std': np.std(latent_variances)
        }
    return {'latent_variance_mean': float('nan'), 'latent_variance_std': float('nan')}


def evaluate_interpolation_smoothness(model: nn.Module, test_data: List[Dict],
                                      architecture: List[int], device: torch.device,
                                      n_steps: int = 10) -> Dict[str, float]:
    """
    Evaluate how smoothly the model interpolates between two weight configurations.
    """
    from models import TargetMLP
    from data import SyntheticTaskDataset
    from torch.utils.data import DataLoader

    model.eval()
    smoothness_scores = []
    task_type = test_data[0].get('task_type', 'classification')

    with torch.no_grad():
        # Sample pairs of models
        for i in range(min(10, len(test_data) - 1)):
            data1 = test_data[i]
            data2 = test_data[i + 1]

            weights1 = [w.to(device) for w in data1['weights']]
            biases1 = [b.to(device) for b in data1['biases']]
            weights2 = [w.to(device) for w in data2['weights']]
            biases2 = [b.to(device) for b in data2['biases']]

            task_cond1 = data1['task_descriptor'].unsqueeze(0).to(device)
            task_cond2 = data2['task_descriptor'].unsqueeze(0).to(device)

            if hasattr(model, 'encode'):
                # Get latents
                enc1 = model.encode(weights1, biases1)
                enc2 = model.encode(weights2, biases2)

                if 'mu' in enc1:
                    z1 = enc1['mu']
                    z2 = enc2['mu']
                else:
                    z1 = torch.cat([enc1['mu_task'], enc1['mu_arch']], dim=-1)
                    z2 = torch.cat([enc2['mu_task'], enc2['mu_arch']], dim=-1)

                # Interpolate
                losses = []
                for t in np.linspace(0, 1, n_steps):
                    z_interp = (1 - t) * z1 + t * z2
                    task_interp = (1 - t) * task_cond1 + t * task_cond2

                    gen_weights, gen_biases = model.decode(z_interp, task_interp)

                    # Evaluate on combined test set
                    target_mlp = TargetMLP(architecture).to(device)
                    target_mlp.set_weights(gen_weights, gen_biases)

                    # Simple evaluation: compute output norm as proxy for stability
                    X = torch.randn(100, architecture[0], device=device)
                    output = target_mlp(X)
                    loss = output.abs().mean().item()
                    losses.append(loss)

                # Compute smoothness as inverse of second derivative
                losses = np.array(losses)
                if len(losses) > 2:
                    second_deriv = np.abs(np.diff(losses, 2))
                    smoothness = 1.0 / (np.mean(second_deriv) + 1e-6)
                    smoothness_scores.append(smoothness)

    if smoothness_scores:
        return {
            'interpolation_smoothness_mean': np.mean(smoothness_scores),
            'interpolation_smoothness_std': np.std(smoothness_scores)
        }
    return {'interpolation_smoothness_mean': float('nan'), 'interpolation_smoothness_std': float('nan')}
