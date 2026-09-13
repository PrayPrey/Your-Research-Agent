import torch


def cosine_distance(v1: torch.Tensor, v2: torch.Tensor) -> float:
    v1 = v1.float()
    v2 = v2.float()
    sim = torch.dot(v1, v2) / (v1.norm() * v2.norm() + 1e-8)
    return float(1.0 - sim)


def l2_distance(v1: torch.Tensor, v2: torch.Tensor) -> float:
    return float((v1 - v2).norm())


def compute_distances(weights, orbits):
    results = {}
    for sym_type, orbit_tensor in orbits.items():
        if sym_type.startswith("_"):
            continue
        N, K, D = orbit_tensor.shape
        cosine_list = []
        l2_list = []
        max_scale_list = [] if sym_type == "scaling" else None

        for i in range(N):
            for k in range(K):
                cd = cosine_distance(weights[i], orbit_tensor[i, k])
                ld = l2_distance(weights[i], orbit_tensor[i, k])
                cosine_list.append(cd)
                l2_list.append(ld)

        entry = {"cosine": cosine_list, "l2": l2_list}
        results[sym_type] = entry

    return results
