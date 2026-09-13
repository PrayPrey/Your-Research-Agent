"""Stream 3: Delta-W spectral analysis with SVD + multiple regression + semipartial r²."""
import torch
import numpy as np
from typing import Dict, Tuple
import scipy.stats
from sklearn.linear_model import LinearRegression


def compute_spectral_decay_ratio(
    delta_w: torch.Tensor,
    top_k: int = 4,
) -> float:
    """Covariance-based SVD via eigvalsh on smaller dim.
    Returns: sum(top-k SVs) / Frobenius norm.
    """
    dw = delta_w.float()
    frob_norm = torch.norm(dw, "fro").item()
    if frob_norm < 1e-10:
        return 0.0

    d_out, d_in = dw.shape
    if d_out >= d_in:
        gram = dw.T @ dw   # (d_in, d_in)
    else:
        gram = dw @ dw.T   # (d_out, d_out)

    eigenvalues = torch.linalg.eigvalsh(gram).clamp(min=0.0)
    singular_values = eigenvalues.sqrt()  # ascending order

    top_k_actual = min(top_k, len(singular_values))
    ratio = singular_values[-top_k_actual:].sum().item() / frob_norm
    return float(ratio)


def compute_all_spectral_decays(
    delta_w_dict: Dict[str, torch.Tensor],
    cfg,
) -> np.ndarray:
    """Compute spectral_decay_ratio for all 32 MLP layers.
    Returns: np.ndarray shape (32,).
    """
    import re
    target_projections = {"gate_proj", "up_proj", "down_proj"}
    layer_decays: Dict[int, list] = {}

    for key, dw in delta_w_dict.items():
        m = re.search(r"layers\.(\d+)\.", key)
        if m:
            layer_idx = int(m.group(1))
            # Check if MLP projection
            is_mlp = any(proj in key for proj in target_projections)
            if is_mlp:
                ratio = compute_spectral_decay_ratio(dw, top_k=cfg.top_k_svs)
                if layer_idx not in layer_decays:
                    layer_decays[layer_idx] = []
                layer_decays[layer_idx].append(ratio)

    result = np.zeros(cfg.n_layers)
    for idx in range(cfg.n_layers):
        if idx in layer_decays:
            result[idx] = np.mean(layer_decays[idx])
    return result


def run_multiple_regression(
    sparsity: np.ndarray,
    grad_norms: np.ndarray,
    spectral_decay: np.ndarray,
) -> Dict:
    """Fit [sparsity, grad_norm] → spectral_decay.
    Returns r2_full, r2_grad_only, unique_var_sparsity, p_value_sparsity_beta.
    """
    n = len(sparsity)
    X_full = np.column_stack([sparsity, grad_norms])
    X_grad = grad_norms.reshape(-1, 1)
    y = spectral_decay

    reg_full = LinearRegression().fit(X_full, y)
    reg_grad = LinearRegression().fit(X_grad, y)

    r2_full = float(reg_full.score(X_full, y))
    r2_grad_only = float(reg_grad.score(X_grad, y))
    unique_var_sparsity = max(0.0, r2_full - r2_grad_only)

    # p-value for sparsity coefficient via OLS t-statistic
    X_aug = np.column_stack([np.ones(n), sparsity, grad_norms])
    y_pred = X_aug @ np.linalg.lstsq(X_aug, y, rcond=None)[0]
    residuals = y - y_pred
    mse = np.sum(residuals ** 2) / max(1, n - 3)

    try:
        XtX_inv = np.linalg.pinv(X_aug.T @ X_aug)
        coefs = np.linalg.lstsq(X_aug, y, rcond=None)[0]
        se_sparsity = float(np.sqrt(max(0.0, mse * XtX_inv[1, 1])))
        coef_sparsity = float(coefs[1])
        coef_grad_norm = float(coefs[2])

        if se_sparsity > 1e-12:
            t_stat = coef_sparsity / se_sparsity
            p_value = float(2 * scipy.stats.t.sf(abs(t_stat), df=max(1, n - 3)))
        else:
            p_value = 1.0
    except Exception:
        coef_sparsity = 0.0
        coef_grad_norm = 0.0
        p_value = 1.0

    return {
        "r2_full": r2_full,
        "r2_grad_only": r2_grad_only,
        "unique_var_sparsity": unique_var_sparsity,
        "p_value_sparsity_beta": p_value,
        "coef_sparsity": coef_sparsity,
        "coef_grad_norm": coef_grad_norm,
    }


def compute_semipartial_r2(
    sparsity: np.ndarray,
    grad_norms: np.ndarray,
    spectral_decay: np.ndarray,
) -> Tuple[float, float]:
    """Returns (unique_var_sparsity, p_value_sparsity_beta)."""
    result = run_multiple_regression(sparsity, grad_norms, spectral_decay)
    return result["unique_var_sparsity"], result["p_value_sparsity_beta"]
