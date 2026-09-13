import torch
from distance_metrics import cosine_distance


def _unpack(weights_flat):
    D = weights_flat.shape[0]
    D_in, h, D_out = 784, 64, 10
    i0 = D_in * h          # 50176
    i1 = i0 + h            # 50240
    i2 = i1 + h * D_out   # 50880
    W1 = weights_flat[:i0].reshape(D_in, h)
    b1 = weights_flat[i0:i1]
    W2 = weights_flat[i1:i2].reshape(h, D_out)
    b2 = weights_flat[i2:]
    return W1, b1, W2, b2


def _repack(W1, b1, W2, b2):
    return torch.cat([W1.flatten(), b1, W2.flatten(), b2])


def construct_orbit_member(weights_flat, transform_type, seed):
    if weights_flat.ndim != 1:
        raise ValueError(f"Expected 1D, got shape {weights_flat.shape}")

    W1, b1, W2, b2 = _unpack(weights_flat)
    h = 64

    if transform_type == "scaling":
        torch.manual_seed(seed)
        log_scales = torch.empty(h).uniform_(-1.0, 1.0)
        scales = 10.0 ** log_scales
        W1_t = W1 * scales.unsqueeze(0)
        b1_t = b1 * scales
        W2_t = W2 / scales.unsqueeze(1)
        b2_t = b2
        result = _repack(W1_t, b1_t, W2_t, b2_t)

    elif transform_type == "signflip":
        torch.manual_seed(seed)
        signs = (torch.randint(0, 2, (h,)) * 2 - 1).float()
        W1_t = W1 * signs.unsqueeze(0)
        b1_t = b1 * signs
        W2_t = W2 * signs.unsqueeze(1)
        b2_t = b2
        result = _repack(W1_t, b1_t, W2_t, b2_t)

    elif transform_type == "combined":
        # scaling first, then signflip
        result_scaled = construct_orbit_member(weights_flat, "scaling", seed)
        result = construct_orbit_member(result_scaled, "signflip", seed + 1000)

    else:
        raise ValueError(f"Unknown transform_type: {transform_type}")

    dist = cosine_distance(result, weights_flat)
    if dist < 1e-6:
        raise ValueError(f"Trivial {transform_type} transform (cosine_dist={dist:.2e})")

    return result


def build_all_orbits(weights, K=5, base_seed=42):
    N, D = weights.shape
    results = {}
    max_scales = {}

    for sym_type in ("scaling", "signflip", "combined"):
        tensor = torch.zeros(N, K, D, dtype=torch.float32)
        scales_per_model = [] if sym_type == "scaling" else None

        for i in range(N):
            for k in range(K):
                seed = base_seed + k
                tensor[i, k] = construct_orbit_member(weights[i], sym_type, seed)

            if sym_type == "scaling":
                # representative scale for this model (seed=base_seed, same as k=0)
                torch.manual_seed(base_seed)
                log_scales = torch.empty(64).uniform_(-1.0, 1.0)
                s = 10.0 ** log_scales
                max_s = torch.max(torch.maximum(s, 1.0 / s)).item()
                scales_per_model.append(max_s)

        results[sym_type] = tensor
        if sym_type == "scaling":
            results["_max_scale_scaling"] = scales_per_model

    return results
