"""
SymVAE: Symmetry-Aware Variational Autoencoder for Neural Network Weight Generation
This module contains the main model implementations including SymVAE and baselines.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional


class SinkhornLayer(nn.Module):
    """Differentiable Sinkhorn algorithm for optimal transport-based soft permutation."""

    def __init__(self, n_iters: int = 10, epsilon: float = 0.1):
        super().__init__()
        self.n_iters = n_iters
        self.epsilon = epsilon

    def forward(self, cost_matrix: torch.Tensor) -> torch.Tensor:
        """
        Compute soft permutation matrix using Sinkhorn algorithm.
        Args:
            cost_matrix: (batch, n, n) cost matrix
        Returns:
            soft_perm: (batch, n, n) doubly stochastic matrix
        """
        K = torch.exp(-cost_matrix / self.epsilon)

        # Sinkhorn iterations
        for _ in range(self.n_iters):
            K = K / (K.sum(dim=-1, keepdim=True) + 1e-8)
            K = K / (K.sum(dim=-2, keepdim=True) + 1e-8)

        return K


class CanonicalizeModule(nn.Module):
    """Learned canonicalization module for handling weight space symmetries."""

    def __init__(self, hidden_dims: List[int], n_sinkhorn_iters: int = 10):
        super().__init__()
        self.hidden_dims = hidden_dims
        self.sinkhorn = SinkhornLayer(n_iters=n_sinkhorn_iters)

        # Learned reference neurons for each layer size
        self.reference_neurons = nn.ParameterDict()
        for dim in hidden_dims:
            self.reference_neurons[str(dim)] = nn.Parameter(torch.randn(dim, dim) * 0.1)

        # Learned scale normalization parameters
        self.scale_weights = nn.ParameterDict()
        for dim in hidden_dims:
            self.scale_weights[str(dim)] = nn.Parameter(torch.ones(dim))

    def compute_permutation(self, weights: torch.Tensor, layer_idx: int) -> torch.Tensor:
        """Compute soft permutation matrix for a layer."""
        n_neurons = weights.shape[-2]
        dim_key = str(n_neurons)

        if dim_key not in self.reference_neurons:
            # For dimensions not in our predefined list, use identity
            return torch.eye(n_neurons, device=weights.device).unsqueeze(0).expand(weights.shape[0], -1, -1)

        ref = self.reference_neurons[dim_key][:n_neurons, :min(weights.shape[-1], n_neurons)]

        # Compute cost matrix
        # weights: (batch, n_neurons, in_features)
        # ref: (n_neurons, in_features)
        w_norm = weights / (weights.norm(dim=-1, keepdim=True) + 1e-8)
        r_norm = ref / (ref.norm(dim=-1, keepdim=True) + 1e-8)

        # Use negative cosine similarity as cost
        cost = -torch.einsum('bni,mi->bnm', w_norm, r_norm)

        return self.sinkhorn(cost)

    def apply_permutation(self, weight: torch.Tensor, perm: torch.Tensor,
                          prev_perm: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Apply permutation to weights."""
        # weight: (batch, out_features, in_features)
        # perm: (batch, out_features, out_features) - permutation for current layer
        # prev_perm: (batch, in_features, in_features) - permutation from previous layer

        result = torch.bmm(perm, weight)
        if prev_perm is not None:
            result = torch.bmm(result, prev_perm.transpose(-1, -2))
        return result

    def scale_normalize(self, weight: torch.Tensor, layer_idx: int) -> torch.Tensor:
        """Apply learned scale normalization."""
        n_neurons = weight.shape[-2]
        dim_key = str(n_neurons)

        if dim_key in self.scale_weights:
            gamma = self.scale_weights[dim_key][:n_neurons].view(1, -1, 1)
        else:
            gamma = torch.ones(1, n_neurons, 1, device=weight.device)

        scale = (gamma * weight).norm(dim=-1, keepdim=True) + 1e-8
        return weight / scale

    def forward(self, weights: List[torch.Tensor]) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """
        Canonicalize a list of weight matrices.
        Args:
            weights: List of (batch, out_features, in_features) tensors
        Returns:
            canon_weights: Canonicalized weights
            permutations: List of permutation matrices used
        """
        canon_weights = []
        permutations = []
        prev_perm = None

        for i, w in enumerate(weights):
            perm = self.compute_permutation(w, i)
            permutations.append(perm)

            w_perm = self.apply_permutation(w, perm, prev_perm)
            w_norm = self.scale_normalize(w_perm, i)
            canon_weights.append(w_norm)

            prev_perm = perm

        return canon_weights, permutations


class SymVAE(nn.Module):
    """Symmetry-Aware Variational Autoencoder for Neural Network Weight Generation."""

    def __init__(self,
                 architecture: List[int],
                 latent_dim: int = 128,
                 task_latent_dim: int = 64,
                 arch_latent_dim: int = 64,
                 hidden_dim: int = 256,
                 n_gnn_layers: int = 3,
                 task_cond_dim: int = 32,
                 use_canonicalization: bool = True,
                 use_hierarchical: bool = True):
        super().__init__()
        self.architecture = architecture
        self.latent_dim = latent_dim
        self.task_latent_dim = task_latent_dim
        self.arch_latent_dim = arch_latent_dim
        self.hidden_dim = hidden_dim
        self.use_canonicalization = use_canonicalization
        self.use_hierarchical = use_hierarchical

        # Total number of weights
        self.n_weights = sum(architecture[i] * architecture[i+1] for i in range(len(architecture)-1))
        self.n_biases = sum(architecture[1:])

        # Canonicalization module
        if use_canonicalization:
            self.canonicalizer = CanonicalizeModule(architecture[1:-1])

        # Encoder (simple MLP for efficiency)
        self.encoder = nn.Sequential(
            nn.Linear(self.n_weights + self.n_biases, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        if use_hierarchical:
            self.fc_mu_task = nn.Linear(hidden_dim, task_latent_dim)
            self.fc_logvar_task = nn.Linear(hidden_dim, task_latent_dim)
            self.fc_mu_arch = nn.Linear(hidden_dim, arch_latent_dim)
            self.fc_logvar_arch = nn.Linear(hidden_dim, arch_latent_dim)
            decoder_input_dim = task_latent_dim + arch_latent_dim + task_cond_dim
        else:
            self.fc_mu = nn.Linear(hidden_dim, latent_dim)
            self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
            decoder_input_dim = latent_dim + task_cond_dim

        # Task conditioning
        self.task_cond_dim = task_cond_dim
        self.task_encoder = nn.Sequential(
            nn.Linear(task_cond_dim, task_cond_dim),
            nn.ReLU(),
            nn.Linear(task_cond_dim, task_cond_dim)
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(decoder_input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, self.n_weights + self.n_biases)
        )

    def flatten_weights(self, weights: List[torch.Tensor], biases: List[torch.Tensor]) -> torch.Tensor:
        """Flatten weight matrices and biases into a single vector."""
        flat_weights = [w.view(w.shape[0], -1) for w in weights]
        flat_biases = [b.view(b.shape[0], -1) for b in biases]
        return torch.cat(flat_weights + flat_biases, dim=-1)

    def unflatten_weights(self, flat: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """Unflatten vector back to weight matrices and biases."""
        weights = []
        biases = []
        idx = 0

        # Unflatten weights
        for i in range(len(self.architecture) - 1):
            n_params = self.architecture[i] * self.architecture[i+1]
            w = flat[:, idx:idx+n_params].view(-1, self.architecture[i+1], self.architecture[i])
            weights.append(w)
            idx += n_params

        # Unflatten biases
        for i in range(1, len(self.architecture)):
            n_params = self.architecture[i]
            b = flat[:, idx:idx+n_params]
            biases.append(b)
            idx += n_params

        return weights, biases

    def encode(self, weights: List[torch.Tensor], biases: List[torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Encode weights to latent distribution parameters."""
        # Optionally canonicalize
        if self.use_canonicalization:
            weights, perms = self.canonicalizer(weights)

        # Flatten and encode
        flat = self.flatten_weights(weights, biases)
        h = self.encoder(flat)

        if self.use_hierarchical:
            return {
                'mu_task': self.fc_mu_task(h),
                'logvar_task': self.fc_logvar_task(h),
                'mu_arch': self.fc_mu_arch(h),
                'logvar_arch': self.fc_logvar_arch(h)
            }
        else:
            return {
                'mu': self.fc_mu(h),
                'logvar': self.fc_logvar(h)
            }

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z: torch.Tensor, task_cond: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """Decode latent code to weights."""
        task_embed = self.task_encoder(task_cond)
        decoder_input = torch.cat([z, task_embed], dim=-1)
        flat = self.decoder(decoder_input)
        return self.unflatten_weights(flat)

    def forward(self, weights: List[torch.Tensor], biases: List[torch.Tensor],
                task_cond: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass."""
        # Encode
        enc_out = self.encode(weights, biases)

        # Sample latent
        if self.use_hierarchical:
            z_task = self.reparameterize(enc_out['mu_task'], enc_out['logvar_task'])
            z_arch = self.reparameterize(enc_out['mu_arch'], enc_out['logvar_arch'])
            z = torch.cat([z_task, z_arch], dim=-1)
            mu = torch.cat([enc_out['mu_task'], enc_out['mu_arch']], dim=-1)
            logvar = torch.cat([enc_out['logvar_task'], enc_out['logvar_arch']], dim=-1)
        else:
            z = self.reparameterize(enc_out['mu'], enc_out['logvar'])
            mu = enc_out['mu']
            logvar = enc_out['logvar']

        # Decode
        recon_weights, recon_biases = self.decode(z, task_cond)

        return {
            'recon_weights': recon_weights,
            'recon_biases': recon_biases,
            'mu': mu,
            'logvar': logvar,
            'z': z
        }

    def sample(self, n_samples: int, task_cond: torch.Tensor,
               device: torch.device) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """Sample weights from the prior."""
        if self.use_hierarchical:
            z = torch.randn(n_samples, self.task_latent_dim + self.arch_latent_dim, device=device)
        else:
            z = torch.randn(n_samples, self.latent_dim, device=device)
        return self.decode(z, task_cond)


class VanillaVAE(nn.Module):
    """Vanilla VAE without symmetry handling (baseline)."""

    def __init__(self, architecture: List[int], latent_dim: int = 128,
                 hidden_dim: int = 256, task_cond_dim: int = 32):
        super().__init__()
        self.architecture = architecture
        self.latent_dim = latent_dim

        # Total parameters
        self.n_weights = sum(architecture[i] * architecture[i+1] for i in range(len(architecture)-1))
        self.n_biases = sum(architecture[1:])
        input_dim = self.n_weights + self.n_biases

        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)

        # Task encoder
        self.task_cond_dim = task_cond_dim
        self.task_encoder = nn.Sequential(
            nn.Linear(task_cond_dim, task_cond_dim),
            nn.ReLU()
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim + task_cond_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim)
        )

    def flatten_weights(self, weights: List[torch.Tensor], biases: List[torch.Tensor]) -> torch.Tensor:
        flat_weights = [w.view(w.shape[0], -1) for w in weights]
        flat_biases = [b.view(b.shape[0], -1) for b in biases]
        return torch.cat(flat_weights + flat_biases, dim=-1)

    def unflatten_weights(self, flat: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        weights = []
        biases = []
        idx = 0

        for i in range(len(self.architecture) - 1):
            n_params = self.architecture[i] * self.architecture[i+1]
            w = flat[:, idx:idx+n_params].view(-1, self.architecture[i+1], self.architecture[i])
            weights.append(w)
            idx += n_params

        for i in range(1, len(self.architecture)):
            n_params = self.architecture[i]
            b = flat[:, idx:idx+n_params]
            biases.append(b)
            idx += n_params

        return weights, biases

    def encode(self, weights: List[torch.Tensor], biases: List[torch.Tensor]) -> Dict[str, torch.Tensor]:
        flat = self.flatten_weights(weights, biases)
        h = self.encoder(flat)
        return {
            'mu': self.fc_mu(h),
            'logvar': self.fc_logvar(h)
        }

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z: torch.Tensor, task_cond: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        task_embed = self.task_encoder(task_cond)
        flat = self.decoder(torch.cat([z, task_embed], dim=-1))
        return self.unflatten_weights(flat)

    def forward(self, weights: List[torch.Tensor], biases: List[torch.Tensor],
                task_cond: torch.Tensor) -> Dict[str, torch.Tensor]:
        enc_out = self.encode(weights, biases)
        mu, logvar = enc_out['mu'], enc_out['logvar']
        z = self.reparameterize(mu, logvar)
        recon_weights, recon_biases = self.decode(z, task_cond)

        return {
            'recon_weights': recon_weights,
            'recon_biases': recon_biases,
            'mu': mu,
            'logvar': logvar,
            'z': z
        }

    def sample(self, n_samples: int, task_cond: torch.Tensor,
               device: torch.device) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        z = torch.randn(n_samples, self.latent_dim, device=device)
        return self.decode(z, task_cond)


class HyperNetwork(nn.Module):
    """HyperNetwork baseline that directly maps task conditioning to weights."""

    def __init__(self, architecture: List[int], hidden_dim: int = 256, task_cond_dim: int = 32):
        super().__init__()
        self.architecture = architecture

        self.n_weights = sum(architecture[i] * architecture[i+1] for i in range(len(architecture)-1))
        self.n_biases = sum(architecture[1:])
        output_dim = self.n_weights + self.n_biases

        self.network = nn.Sequential(
            nn.Linear(task_cond_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

        # Add noise for diversity
        self.noise_dim = 32
        self.noise_encoder = nn.Linear(self.noise_dim, hidden_dim)

        self.network_with_noise = nn.Sequential(
            nn.Linear(task_cond_dim + hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def unflatten_weights(self, flat: torch.Tensor) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        weights = []
        biases = []
        idx = 0

        for i in range(len(self.architecture) - 1):
            n_params = self.architecture[i] * self.architecture[i+1]
            w = flat[:, idx:idx+n_params].view(-1, self.architecture[i+1], self.architecture[i])
            weights.append(w)
            idx += n_params

        for i in range(1, len(self.architecture)):
            n_params = self.architecture[i]
            b = flat[:, idx:idx+n_params]
            biases.append(b)
            idx += n_params

        return weights, biases

    def forward(self, task_cond: torch.Tensor,
                noise: Optional[torch.Tensor] = None) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        if noise is not None:
            noise_embed = self.noise_encoder(noise)
            flat = self.network_with_noise(torch.cat([task_cond, noise_embed], dim=-1))
        else:
            flat = self.network(task_cond)
        return self.unflatten_weights(flat)

    def sample(self, n_samples: int, task_cond: torch.Tensor,
               device: torch.device) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        noise = torch.randn(n_samples, self.noise_dim, device=device)
        return self.forward(task_cond, noise)


class TargetMLP(nn.Module):
    """Simple MLP that the weight generation models learn to produce weights for."""

    def __init__(self, architecture: List[int]):
        super().__init__()
        self.architecture = architecture
        layers = []
        for i in range(len(architecture) - 1):
            layers.append(nn.Linear(architecture[i], architecture[i+1]))
            if i < len(architecture) - 2:
                layers.append(nn.ReLU())
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

    def set_weights(self, weights: List[torch.Tensor], biases: List[torch.Tensor]):
        """Set the weights of the network."""
        linear_idx = 0
        for module in self.network:
            if isinstance(module, nn.Linear):
                module.weight.data = weights[linear_idx].squeeze(0)
                module.bias.data = biases[linear_idx].squeeze(0)
                linear_idx += 1

    def get_weights(self) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        """Get the weights of the network."""
        weights = []
        biases = []
        for module in self.network:
            if isinstance(module, nn.Linear):
                weights.append(module.weight.data.unsqueeze(0))
                biases.append(module.bias.data.unsqueeze(0))
        return weights, biases
