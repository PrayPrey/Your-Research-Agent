import sys
import torch
import numpy as np
from collections import OrderedDict
import config
import permute as perm_module

sys.path.insert(0, config.H_E1_CODE_DIR)
sys.path.insert(0, config.DWSNETS_PATH)


def _flatten_state_dict(state_dict: dict) -> torch.Tensor:
    parts = []
    for key in sorted(state_dict.keys()):
        parts.append(state_dict[key].flatten())
    return torch.cat(parts)


def encoder_dispatch(encoder_name: str, encoder, state_dict: dict) -> torch.Tensor:
    """Forward pass for one state_dict. Returns (128,) embedding."""
    if encoder_name == "flat_mlp":
        flat = _flatten_state_dict(state_dict)
        x = flat.unsqueeze(0)  # (1, D)
        out = encoder(x)       # (1, 128)
        return out.squeeze(0)

    elif encoder_name == "gnn_nfn":
        from data import state_dict_to_graph
        from torch_geometric.data import Batch
        graph = state_dict_to_graph(state_dict)
        batch = Batch.from_data_list([graph])
        out = encoder(batch)  # (1, 128)
        return out.squeeze(0)

    elif encoder_name == "dwsnet":
        # encoder may be (model, synthetic_sds, fc_specs) tuple or bare model
        if isinstance(encoder, tuple):
            model = encoder[0]
        else:
            model = encoder
        out = model(state_dict)  # (128,)
        return out

    else:
        raise ValueError(f"Unknown encoder: {encoder_name}")


def run_single_model_check(
    encoder_name: str,
    encoder,
    state_dict: dict,
    hidden_keys: list,
    num_perms: int,
) -> list:
    """Run num_perms permutation checks on one model. Returns list of max_abs_diff."""
    out_orig = encoder_dispatch(encoder_name, encoder, state_dict)
    diffs = []
    for _ in range(num_perms):
        if not hidden_keys:
            diffs.append(0.0)
            continue
        layer_key = hidden_keys[0]
        hidden_size = state_dict[layer_key].shape[0]
        p = perm_module.get_perm(hidden_size)
        sd_perm = perm_module.permute_weights(state_dict, layer_key, p)
        out_perm = encoder_dispatch(encoder_name, encoder, sd_perm)
        diff = (out_orig - out_perm).abs().max().item()
        diffs.append(diff)
    return diffs


def compute_stats(diffs: list, tol: float = None) -> dict:
    arr = np.array(diffs, dtype=np.float64)
    return {
        "max_diff": float(arr.max()),
        "mean_diff": float(arr.mean()),
        "median_diff": float(np.median(arr)),
        "p95_diff": float(np.percentile(arr, 95)),
        "all_diffs": diffs,
        "n_checks": len(diffs),
        "pass": bool(arr.max() < tol) if tol is not None else None,
    }


def verify_equivariance(
    encoder_name: str,
    encoder,
    weight_samples: list,
    hidden_keys_per_model: list,
    num_perms: int = config.N_PERMS,
    tol: float = None,
) -> dict:
    """Run full N*K permutation checks. Returns stats dict."""
    model = encoder[0] if isinstance(encoder, tuple) else encoder
    model.eval()
    all_diffs = []
    with torch.no_grad():
        for i, (sd, hkeys) in enumerate(zip(weight_samples, hidden_keys_per_model)):
            if i % 20 == 0:
                print(f"  {encoder_name}: model {i}/{len(weight_samples)}")
            diffs = run_single_model_check(encoder_name, encoder, sd, hkeys, num_perms)
            all_diffs.extend(diffs)
    return compute_stats(all_diffs, tol=tol)


def verify_mechanism_activated(results: dict) -> tuple:
    """Check gate conditions. Returns (activated: bool, indicators: dict)."""
    indicators = {}
    active_encoders = {k: v for k, v in results.items() if v is not None}

    if "dwsnet" in active_encoders:
        indicators["dwsnet_equivariant"] = active_encoders["dwsnet"]["max_diff"] < config.TOL_EQUIV
    else:
        indicators["dwsnet_equivariant"] = None  # skipped

    if "gnn_nfn" in active_encoders:
        indicators["gnn_equivariant"] = active_encoders["gnn_nfn"]["max_diff"] < config.TOL_EQUIV
    else:
        indicators["gnn_equivariant"] = False

    if "flat_mlp" in active_encoders:
        indicators["flat_not_equivariant"] = active_encoders["flat_mlp"]["max_diff"] > config.TOL_NON_EQUIV
    else:
        indicators["flat_not_equivariant"] = False

    if "dwsnet" in active_encoders and "flat_mlp" in active_encoders:
        gap = active_encoders["flat_mlp"]["max_diff"] / (active_encoders["dwsnet"]["max_diff"] + 1e-10)
        indicators["gap_exists"] = gap > 100
    elif "gnn_nfn" in active_encoders and "flat_mlp" in active_encoders:
        gap = active_encoders["flat_mlp"]["max_diff"] / (active_encoders["gnn_nfn"]["max_diff"] + 1e-10)
        indicators["gap_exists"] = gap > 100
    else:
        indicators["gap_exists"] = False

    # Gate: GNN-NFN MUST be equivariant; DWSNets if available must be equivariant
    gnn_ok = indicators.get("gnn_equivariant", False)
    dwsnet_ok = indicators.get("dwsnet_equivariant") is not False  # None (skipped) counts as not blocking
    flat_ok = indicators.get("flat_not_equivariant", False)

    activated = gnn_ok and flat_ok
    if "dwsnet" in active_encoders:
        activated = activated and (indicators["dwsnet_equivariant"] is True)

    return activated, indicators
