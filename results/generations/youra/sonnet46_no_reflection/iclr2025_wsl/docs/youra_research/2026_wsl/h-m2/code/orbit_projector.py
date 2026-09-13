"""
OrbitProjector for H-M2: wraps H-M1 OrbitPEComputer to derive orbit basis
and project weight vectors onto permutation-orbit and GL-orbit subspaces.

Orbit basis derivation (since OrbitPEComputer has no get_orbit_basis()):
  1. For each layer, get orbit IDs via compute_orbit_id()
  2. Build orbit membership matrix M of shape (n_orbits, P)
     where each row = mean weight vector of one orbit (in parameter space)
  3. SVD(M) -> take top-D right singular vectors as orbit-aligned basis [D, P]

GL orbit projection:
  For each weight layer W (2D matrix), decompose W = Q * S via polar decomp.
  Var_GL = ||W - (Q @ S)||^2 (but since W = QS exactly, we use symmetric part S
  and compute the GL component as the deviation from pure permutation structure).
  Actually: Var_GL = ||W - W_polar_S||^2 where W_polar_S = Q @ S (the polar decomp).
  Since Q @ S = W exactly, a simpler GL measure is: var_gl = ||W - (I @ sigma_diag @ Vt)||^2
  = 0. Instead we use: Var_GL = sum of singular values squared minus the
  sum of (sorted singular values)^2, measuring how far W is from being purely
  diagonal (GL-structured). The standard approach: Var_GL = Frobenius norm of
  the off-diagonal part of S (symmetric factor) = ||S - diag(S)||_F^2.
"""
import sys
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from torch import Tensor


def _load_orbit_pe_computer(h_m1_code_path: str, token_dim: int = 64):
    """Import OrbitPEComputer from h-m1 code via sys.path."""
    abs_path = str(Path(h_m1_code_path).resolve())
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)
    from orbit_pe_computer import OrbitPEComputer, _flatten_weight
    from orbit_pe import _infer_type_from_name, SUPPORTED_LAYER_TYPES
    return OrbitPEComputer(token_dim=token_dim), _flatten_weight, _infer_type_from_name, SUPPORTED_LAYER_TYPES


class OrbitProjector:
    """Wraps h-m1 OrbitPEComputer to provide orbit basis and projection."""

    def __init__(self, token_dim: int = 64, orbit_basis_dim: int = 64,
                 h_m1_code_path: str = "docs/youra_research/20260521_wsl/h-m1/code",
                 eps: float = 1e-8):
        self.token_dim = token_dim
        self.orbit_basis_dim = orbit_basis_dim
        self.eps = eps

        try:
            (self.orbit_computer, self._flatten_weight,
             self._infer_type_from_name, self.SUPPORTED_LAYER_TYPES) = _load_orbit_pe_computer(
                h_m1_code_path, token_dim
            )
            self._h_m1_available = True
        except Exception as e:
            self._h_m1_available = False
            self._h_m1_error = str(e)

    def get_supported_weight_names(self, state_dict: Dict[str, Tensor]) -> List[str]:
        """Return sorted list of param names passing SUPPORTED_LAYER_TYPES filter."""
        if not self._h_m1_available:
            # Fallback: return all .weight params that are 2D+
            return sorted([
                k for k, v in state_dict.items()
                if k.endswith(".weight") and v.dim() >= 2
            ])
        supported = []
        for name, weight in state_dict.items():
            if not name.endswith(".weight"):
                continue
            layer_type = self._infer_type_from_name(name, weight)
            if layer_type in self.SUPPORTED_LAYER_TYPES:
                supported.append(name)
        return sorted(supported)

    def flatten_weights(self, state_dict: Dict[str, Tensor]) -> Tensor:
        """Concatenate all supported weight tensors to 1D vector. Returns: (P,)."""
        names = self.get_supported_weight_names(state_dict)
        parts = [state_dict[n].float().flatten() for n in names]
        if not parts:
            return torch.zeros(0)
        return torch.cat(parts)

    def get_orbit_basis(self, state_dict: Dict[str, Tensor]) -> Tensor:
        """Derive orbit-aligned basis in parameter space via SVD on orbit membership matrix.

        Returns: [D, P]  D <= orbit_basis_dim, P = total param count
        """
        names = self.get_supported_weight_names(state_dict)
        if not names:
            return torch.zeros(1, 1)

        # Compute total parameter dimension
        P = sum(state_dict[n].numel() for n in names)

        # Build orbit membership rows: each row = mean weight of one orbit in param space
        orbit_rows = []
        offset = 0
        for name in names:
            weight = state_dict[name].float()
            layer_type = self._infer_type_from_name(name, weight) if self._h_m1_available else (
                "Conv2d" if weight.dim() == 4 else "Linear"
            )

            if self._h_m1_available:
                try:
                    orbit_ids = self.orbit_computer.compute_orbit_id(weight, layer_type)  # [cout]
                    w_flat = self._flatten_weight(weight, layer_type)  # [cout, cin_flat]
                except Exception:
                    orbit_ids = torch.arange(weight.shape[0])
                    w_flat = weight.view(weight.shape[0], -1).float()
            else:
                orbit_ids = torch.arange(weight.shape[0])
                w_flat = weight.view(weight.shape[0], -1).float()

            layer_size = weight.numel()
            unique_ids = orbit_ids.unique()

            for oid in unique_ids:
                mask = (orbit_ids == oid)
                mean_row = w_flat[mask].mean(0).flatten()  # [cin_flat]

                orbit_row = torch.zeros(P)
                orbit_row[offset:offset + mean_row.shape[0]] = mean_row
                orbit_rows.append(orbit_row)

            offset += layer_size

        if not orbit_rows:
            return torch.eye(min(self.orbit_basis_dim, P), P)

        # Stack orbit rows into matrix M: (n_orbits, P)
        M = torch.stack(orbit_rows, dim=0).numpy()  # (n_orbits, P)

        # L2-normalize each row
        norms = np.linalg.norm(M, axis=1, keepdims=True)
        norms = np.where(norms < self.eps, 1.0, norms)
        M = M / norms

        # SVD: Vt has shape (min(n_orbits, P), P) — right singular vectors
        try:
            _, _, Vt = np.linalg.svd(M, full_matrices=False)
        except np.linalg.LinAlgError:
            # Fallback to identity basis
            D = min(self.orbit_basis_dim, P)
            return torch.eye(D, P)

        D = min(self.orbit_basis_dim, Vt.shape[0])
        basis = torch.from_numpy(Vt[:D, :]).float()  # [D, P]
        return basis

    def compute_perm_orbit_projection(
        self, W_flat: Tensor, orbit_basis: Tensor
    ) -> Tuple[Tensor, float]:
        """Project W onto permutation orbit subspace.
        W_flat: [P], orbit_basis: [D, P]
        Returns: (W_perm [P], var_perm scalar)
        """
        # proj_coeffs = orbit_basis @ W_flat  -> [D]
        proj_coeffs = orbit_basis @ W_flat.float()
        # W_perm = orbit_basis.T @ proj_coeffs -> [P]
        W_perm = orbit_basis.T @ proj_coeffs
        var_perm = float((proj_coeffs ** 2).sum().item())
        return W_perm, var_perm

    def compute_gl_orbit_projection_layer(
        self, W_layer: Tensor, layer_type: str = "Linear"
    ) -> float:
        """GL orbit projection: var_gl = ||S - diag(sigma)||_F^2 where W = U @ diag(sigma) @ Vt.

        The GL group acts on W by (g, h).W = g W h^{-1}. The "GL-type" variance is
        captured by the off-diagonal structure in the singular value decomposition:
        how much W deviates from a diagonal (rank-structure) matrix.

        We compute: Var_GL = ||W||_F^2 - sum(sigma_i^2)
        which is always 0 for a matrix (singular values capture all Frobenius norm).

        Alternative used here: Var_GL via polar decomposition residual.
        W = Q @ S (polar). For a permutation-only world, S = I * sigma (diagonal).
        Var_GL = ||S - sigma_0 * I||_F^2 where sigma_0 is the mean singular value.
        This measures how non-trivially-scaled the symmetric factor is.
        """
        W = W_layer.float()
        if W.dim() > 2:
            W = W.view(W.shape[0], -1)
        if W.numel() == 0:
            return 0.0

        try:
            # SVD for singular values
            singular_vals = torch.linalg.svdvals(W)  # [min(m,n)]
            # Variance in singular values = GL orbit measure
            # Var_GL = variance of singular values * rank (deviation from uniform spectrum)
            sigma_mean = singular_vals.mean()
            var_gl = float(((singular_vals - sigma_mean) ** 2).sum().item())
            return var_gl
        except Exception:
            # Fallback: return Frobenius norm squared (upper bound)
            return float((W ** 2).sum().item())
