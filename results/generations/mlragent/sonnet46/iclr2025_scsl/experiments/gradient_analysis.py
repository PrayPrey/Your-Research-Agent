"""
Gradient decomposition and Hessian analysis utilities for CGD framework.
"""
import torch
import torch.nn as nn
import numpy as np
from torch.func import functional_call, vmap, grad


def compute_per_sample_gradients(model, loss_fn, inputs, targets, device):
    """
    Compute per-sample gradients for a batch.
    Returns tensor of shape (batch_size, n_params).
    """
    model.eval()
    params = {k: v for k, v in model.named_parameters() if v.requires_grad}
    param_names = list(params.keys())

    def compute_loss(params, x, y):
        logits = functional_call(model, params, (x.unsqueeze(0),))
        return loss_fn(logits, y.unsqueeze(0))

    per_sample_grads = []

    for i in range(len(inputs)):
        x_i = inputs[i]
        y_i = targets[i]

        grads_i = {}
        loss_i = compute_loss(params, x_i, y_i)
        for name, param in params.items():
            g = torch.autograd.grad(loss_i, param, retain_graph=True, create_graph=False)[0]
            grads_i[name] = g.detach().flatten()

        flat_grad = torch.cat([grads_i[n] for n in param_names])
        per_sample_grads.append(flat_grad)

    return torch.stack(per_sample_grads)  # (batch_size, n_params)


def identify_gradient_subspaces(model, loss_fn, dataloader, causal_idx, spurious_idx,
                                 device, n_batches=5):
    """
    Estimate gradient subspaces associated with causal vs spurious features.
    Uses PCA on per-sample gradients from different groups.

    For synthetic data: causal_idx and spurious_idx are feature indices.
    """
    model.eval()

    # Collect gradients for samples with different feature patterns
    causal_grads = []
    spurious_grads = []

    batch_count = 0
    for batch in dataloader:
        if batch_count >= n_batches:
            break

        if len(batch) == 3:
            inputs, targets, groups = batch
        else:
            inputs, targets = batch
            groups = torch.zeros(len(targets), dtype=torch.long)

        inputs, targets = inputs.to(device), targets.to(device)

        # Compute gradients with respect to parameters
        model.zero_grad()

        logits = model(inputs)
        loss = loss_fn(logits, targets)
        loss.backward()

        # Collect gradient vectors
        flat_grad = []
        for param in model.parameters():
            if param.grad is not None:
                flat_grad.append(param.grad.detach().flatten())
        if flat_grad:
            flat_grad = torch.cat(flat_grad)

            # Separate by whether the batch has more causal or spurious signal
            # Use a simple heuristic based on input features if available
            if hasattr(inputs, 'shape') and inputs.dim() == 2:
                # Linear case: can separate causal vs spurious input contribution
                causal_input_norm = inputs[:, causal_idx].norm(dim=1).mean().item()
                spurious_input_norm = inputs[:, spurious_idx].norm(dim=1).mean().item()
                if causal_input_norm > spurious_input_norm:
                    causal_grads.append(flat_grad.cpu().numpy())
                else:
                    spurious_grads.append(flat_grad.cpu().numpy())
            else:
                # For image data, alternate assignment
                if batch_count % 2 == 0:
                    causal_grads.append(flat_grad.cpu().numpy())
                else:
                    spurious_grads.append(flat_grad.cpu().numpy())

        model.zero_grad()
        batch_count += 1

    # Estimate subspace directions via PCA
    n_components = min(5, len(causal_grads), len(spurious_grads))

    V_c = None
    V_s = None

    if len(causal_grads) >= 2:
        C_grads = np.stack(causal_grads)
        # Simple: use mean direction as subspace
        mean_c = C_grads.mean(axis=0)
        norm_c = np.linalg.norm(mean_c)
        if norm_c > 1e-10:
            V_c = torch.tensor(mean_c / norm_c, dtype=torch.float32).unsqueeze(1)  # (n_params, 1)

    if len(spurious_grads) >= 2:
        S_grads = np.stack(spurious_grads)
        mean_s = S_grads.mean(axis=0)
        norm_s = np.linalg.norm(mean_s)
        if norm_s > 1e-10:
            V_s = torch.tensor(mean_s / norm_s, dtype=torch.float32).unsqueeze(1)  # (n_params, 1)

    return V_c, V_s


def decompose_gradient(flat_grad, V_c, V_s):
    """
    Decompose gradient into causal, spurious, and residual components.
    flat_grad: (n_params,)
    V_c: (n_params, k_c) - causal subspace basis
    V_s: (n_params, k_s) - spurious subspace basis
    Returns: g_c, g_s, g_perp
    """
    g_c = torch.zeros_like(flat_grad)
    g_s = torch.zeros_like(flat_grad)

    if V_c is not None:
        V_c = V_c.to(flat_grad.device)
        proj_c = V_c @ (V_c.t() @ flat_grad)
        g_c = proj_c

    if V_s is not None:
        V_s = V_s.to(flat_grad.device)
        proj_s = V_s @ (V_s.t() @ flat_grad)
        g_s = proj_s

    g_perp = flat_grad - g_c - g_s

    return g_c, g_s, g_perp


def compute_spurious_dominance_ratio(g_c, g_s):
    """
    rho = ||g_s||^2 / (||g_c||^2 + ||g_s||^2)
    """
    norm_c_sq = (g_c.norm() ** 2).item()
    norm_s_sq = (g_s.norm() ** 2).item()
    denom = norm_c_sq + norm_s_sq + 1e-10
    return norm_s_sq / denom


def estimate_hessian_curvature(model, loss_fn, dataloader, V_subspace, device,
                                n_batches=3, n_power_iter=10):
    """
    Estimate top eigenvalue of block Hessian restricted to subspace V.
    Uses power iteration with Hessian-vector products.
    Returns estimated top eigenvalue.
    """
    if V_subspace is None:
        return 1.0

    model.eval()
    V = V_subspace.to(device)  # (n_params, k)

    # Get a batch for Hessian estimation
    for batch in dataloader:
        if len(batch) == 3:
            inputs, targets, _ = batch
        else:
            inputs, targets = batch
        inputs, targets = inputs.to(device), targets.to(device)
        break

    # Flatten model parameters
    params_list = [p for p in model.parameters() if p.requires_grad]

    # Power iteration to find top eigenvalue of H restricted to V
    v = V[:, 0].clone()  # Initial vector
    v = v / (v.norm() + 1e-10)

    eigenvalue = 0.0

    for _ in range(n_power_iter):
        # Hessian-vector product: H @ v
        model.zero_grad()
        logits = model(inputs)
        loss = loss_fn(logits, targets)

        # First derivative
        grads = torch.autograd.grad(loss, params_list, create_graph=True)
        flat_grad = torch.cat([g.flatten() for g in grads])

        # Dot product with v
        gv = (flat_grad * v.detach()).sum()

        # Second derivative (Hessian-vector product)
        try:
            hvp = torch.autograd.grad(gv, params_list, retain_graph=False)
            Hv = torch.cat([h.flatten() for h in hvp]).detach()
        except Exception:
            Hv = v.clone()

        # Project onto subspace V
        Hv_proj = V @ (V.t() @ Hv)

        # Rayleigh quotient
        eigenvalue = (v * Hv_proj).sum().item()

        # Update v
        norm = Hv_proj.norm()
        if norm > 1e-10:
            v = Hv_proj / norm

        model.zero_grad()

    return abs(eigenvalue)
