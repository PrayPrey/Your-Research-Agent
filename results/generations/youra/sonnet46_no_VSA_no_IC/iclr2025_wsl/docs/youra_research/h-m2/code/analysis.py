"""Efficiency ratio computation, bootstrap CI, gate check, mechanism verification."""
import numpy as np
import config as cfg


def compute_efficiency_ratio(plain_curve, equiv_curve, training_sizes=None, peak_fraction=0.90):
    """
    N_plain(90% peak) / N_equiv(90% peak).
    plain_curve, equiv_curve: {str(size) -> float} mean_r2 per size.
    """
    if training_sizes is None:
        training_sizes = cfg.TRAINING_SIZES

    # Build ordered (numeric_size, r2) lists
    size_to_num = {str(s): (3402 if s == "full" else int(s)) for s in training_sizes}

    def curve_list(curve):
        out = []
        for s in training_sizes:
            k = str(s)
            if k in curve:
                out.append((size_to_num[k], curve[k]))
        return out

    plain_list = curve_list(plain_curve)
    equiv_list = curve_list(equiv_curve)

    if not plain_list or not equiv_list:
        return float('inf')

    plain_peak = max(r2 for _, r2 in plain_list)
    equiv_peak = max(r2 for _, r2 in equiv_list)

    plain_thr = peak_fraction * plain_peak
    equiv_thr = peak_fraction * equiv_peak

    plain_90 = next((n for n, r2 in plain_list if r2 >= plain_thr), None)
    equiv_90 = next((n for n, r2 in equiv_list if r2 >= equiv_thr), None)

    if plain_90 is None or equiv_90 is None:
        return float('inf')
    if equiv_90 == 0:
        return float('inf')

    return plain_90 / equiv_90


def compute_all_efficiency_ratios(results):
    """
    results: {encoder: {zoo: {size: {mean_r2, ...}}}}
    Returns {equivariant_encoder: {zoo: efficiency_ratio}} vs flat_mlp baseline.
    """
    equivariant = [e for e in results if e not in ("flat_mlp", "flat_mlp_perm_aug")]
    ratios = {}
    for enc in equivariant:
        ratios[enc] = {}
        for zoo in results.get(enc, {}):
            if "flat_mlp" not in results or zoo not in results["flat_mlp"]:
                continue
            plain_curve = {k: v["mean_r2"] for k, v in results["flat_mlp"][zoo].items()}
            equiv_curve = {k: v["mean_r2"] for k, v in results[enc][zoo].items()}
            ratio = compute_efficiency_ratio(plain_curve, equiv_curve)
            ratios[enc][zoo] = ratio
    return ratios


def check_gate(efficiency_ratios, gate=2.0):
    """
    Gate: ratio >= 2.0 for >= 1 equivariant encoder on BOTH zoos.
    SHOULD_WORK gate — failure is a limitation, not pipeline stop.
    Returns (gate_passed: bool, details: dict).
    """
    equivariant_encoders = [e for e in efficiency_ratios if e in ("gnn_nfn", "dwsnets")]
    details = {}
    for enc in equivariant_encoders:
        per_zoo = efficiency_ratios[enc]
        meets_both = all(per_zoo.get(zoo, 0) >= gate for zoo in cfg.ZOO_NAMES)
        details[enc] = {"ratios": per_zoo, "meets_gate": meets_both}

    gate_passed = any(d["meets_gate"] for d in details.values())
    return gate_passed, details


def verify_mechanism_activated_batch(encoder_name, results, device, zoo_name="cifar10", n_check=1):
    """
    Sanity check: equivariance holds (max_diff < 1e-4) for equivariant encoders.
    Inherited from H-M1 pattern. Returns {"equivariance_holds", "max_diff", "encoder"}.
    """
    import sys
    import torch

    for p in [cfg.H_E1_CODE_DIR, cfg.H_M1_CODE_DIR, cfg.MZDATASET_CODE_PATH]:
        if p not in sys.path:
            sys.path.insert(0, p)

    # Monkey-patch H-E1 config
    import config as h_e1_cfg
    h_e1_cfg.ZOO_PATHS = cfg.ZOO_PATHS
    h_e1_cfg.MZDATASET_CODE_PATH = cfg.MZDATASET_CODE_PATH

    try:
        from data import load_zoo, FlatCollator, GNNCollator
        from encoders import build_encoder, GNNNFNEncoder
        from permute import permute_weights, get_perm

        train_ds, val_ds, test_ds = load_zoo(zoo_name)
        state_dict, _ = test_ds[0]

        # Get input_dim from flat collated sample
        fc = FlatCollator()
        x_batch, _ = fc([(state_dict, torch.tensor(0.0))])
        input_dim = x_batch.shape[1]

        # Build encoder with fresh random init
        encoder = build_encoder(encoder_name, input_dim=input_dim,
                                target_params=cfg.PRIMARY_BUDGET,
                                zoo_arch=cfg.ZOO_ARCH)
        encoder = encoder.to(device)
        encoder.eval()

        # Find first hidden FC layer for permutation
        fc_keys = [k for k in state_dict
                   if "weight" in k and hasattr(state_dict[k], "dim") and state_dict[k].dim() == 2]
        if not fc_keys:
            return {"equivariance_holds": False, "max_diff": float('nan'),
                    "encoder": encoder_name, "note": "no FC layers in zoo model"}

        hidden_key = fc_keys[0]
        hidden_size = state_dict[hidden_key].shape[0]
        perm = get_perm(hidden_size, device=torch.device("cpu"))
        sd_perm = permute_weights(dict(state_dict), hidden_key, perm)

        with torch.no_grad():
            if encoder_name in {"flat_mlp", "flat_mlp_perm_aug"}:
                x_orig, _ = fc([(state_dict, torch.tensor(0.0))])
                x_perm, _ = fc([(sd_perm, torch.tensor(0.0))])
                out_orig = encoder(x_orig.to(device))
                out_perm = encoder(x_perm.to(device))
            else:
                # GNN path — GNNCollator returns (DataBatch, targets)
                gnn_col = GNNCollator()
                b_orig, _ = gnn_col([(state_dict, torch.tensor(0.0))])
                b_perm, _ = gnn_col([(sd_perm, torch.tensor(0.0))])
                b_orig = b_orig.to(device)
                b_perm = b_perm.to(device)
                out_orig = encoder(b_orig)
                out_perm = encoder(b_perm)

        max_diff = float((out_orig - out_perm).abs().max().item())
        return {
            "equivariance_holds": max_diff < 1e-4,
            "max_diff": max_diff,
            "encoder": encoder_name,
        }
    except Exception as e:
        return {"equivariance_holds": False, "max_diff": float('nan'),
                "encoder": encoder_name, "note": str(e)}
