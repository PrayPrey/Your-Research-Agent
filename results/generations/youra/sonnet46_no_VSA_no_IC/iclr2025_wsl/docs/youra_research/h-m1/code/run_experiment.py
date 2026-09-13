import sys
import os
import torch
from pathlib import Path

# Ensure h-m1/code is first in path so our modules take priority over h-e1/code
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

import config
from data_loader import load_zoo_models, get_weight_dim, detect_hidden_layers
from encoder_loader import get_all_encoders
from verify import verify_equivariance, verify_mechanism_activated
sys.path.insert(0, _CODE_DIR)  # re-insert before h-e1/code which encoder_loader adds
from visualize import save_all_figures
from reporter import print_summary_table, save_json


def main() -> None:
    torch.manual_seed(config.SEED)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    print("=== H-M1: Permutation Equivariance Verification ===")

    print(f"Loading {config.N_MODELS} zoo models...")
    weight_samples = load_zoo_models(n=config.N_MODELS, seed=config.SEED)
    weight_dim = get_weight_dim(weight_samples)
    hidden_keys_per_model = [detect_hidden_layers(sd) for sd in weight_samples]
    print(f"  weight_dim={weight_dim}, example hidden_keys={hidden_keys_per_model[0]}")

    print("Loading encoders...")
    encoders = get_all_encoders(weight_dim, weight_samples[0])

    results = {}

    # GNN-NFN: verify on zoo weight samples
    enc = encoders["gnn_nfn"]
    if enc is not None:
        print(f"Verifying gnn_nfn ({config.N_MODELS} models x {config.N_PERMS} perms)...")
        results["gnn_nfn"] = verify_equivariance(
            encoder_name="gnn_nfn",
            encoder=enc,
            weight_samples=weight_samples,
            hidden_keys_per_model=hidden_keys_per_model,
            num_perms=config.N_PERMS,
            tol=config.TOL_EQUIV,
        )
        print(f"  gnn_nfn: max_diff={results['gnn_nfn']['max_diff']:.2e}")
    else:
        results["gnn_nfn"] = None

    # FlatMLP: verify on zoo weight samples
    enc = encoders["flat_mlp"]
    if enc is not None:
        print(f"Verifying flat_mlp ({config.N_MODELS} models x {config.N_PERMS} perms)...")
        results["flat_mlp"] = verify_equivariance(
            encoder_name="flat_mlp",
            encoder=enc,
            weight_samples=weight_samples,
            hidden_keys_per_model=hidden_keys_per_model,
            num_perms=config.N_PERMS,
            tol=None,
        )
        print(f"  flat_mlp: max_diff={results['flat_mlp']['max_diff']:.2e}")
    else:
        results["flat_mlp"] = None

    # DWSNets: if synthetic_sds available, verify on those instead of zoo
    dwsnet_entry = encoders.get("dwsnet")
    if dwsnet_entry is not None:
        dwsnet_model, synthetic_sds, fc_specs = dwsnet_entry
        if synthetic_sds is not None:
            print(f"Verifying dwsnet on {len(synthetic_sds)} synthetic MLP models x 20 perms")
            print("  (Zoo CNNs have only 2 FC layers; DWSNets requires >2. Using synthetic MLP weight space.)")
            # Get hidden keys for synthetic sds
            syn_hidden_keys = []
            for sd in synthetic_sds:
                wkeys = sorted([k for k in sd if k.endswith(".weight")])
                syn_hidden_keys.append(wkeys[1:-1])
            results["dwsnet"] = verify_equivariance(
                encoder_name="dwsnet",
                encoder=(dwsnet_model, synthetic_sds, fc_specs),
                weight_samples=synthetic_sds,
                hidden_keys_per_model=syn_hidden_keys,
                num_perms=20,
                tol=config.TOL_EQUIV,
            )
        else:
            print(f"Verifying dwsnet on zoo models x {config.N_PERMS} perms...")
            results["dwsnet"] = verify_equivariance(
                encoder_name="dwsnet",
                encoder=dwsnet_model,
                weight_samples=weight_samples,
                hidden_keys_per_model=hidden_keys_per_model,
                num_perms=config.N_PERMS,
                tol=config.TOL_EQUIV,
            )
        print(f"  dwsnet: max_diff={results['dwsnet']['max_diff']:.2e}")
    else:
        results["dwsnet"] = None
        print("DWSNets: SKIPPED (error during load)")

    activated, indicators = verify_mechanism_activated(results)
    print_summary_table(results, activated, indicators)
    save_json(results, activated, indicators)
    save_all_figures(results)

    # Assert gate conditions
    gnn_res = results.get("gnn_nfn")
    flat_res = results.get("flat_mlp")
    dwsnet_res = results.get("dwsnet")

    assert gnn_res is not None, "GNN-NFN results missing"
    assert gnn_res["max_diff"] < config.TOL_EQUIV, \
        f"GNN-NFN NOT equivariant: max_diff={gnn_res['max_diff']:.2e}"
    assert flat_res is not None, "FlatMLP results missing"
    assert flat_res["max_diff"] > config.TOL_NON_EQUIV, \
        f"FlatMLP appears equivariant: max_diff={flat_res['max_diff']:.2e}"
    if dwsnet_res is not None:
        assert dwsnet_res["max_diff"] < config.TOL_EQUIV, \
            f"DWSNets NOT equivariant: max_diff={dwsnet_res['max_diff']:.2e}"

    print("\nH-M1 GATE: ALL CONDITIONS PASSED")


if __name__ == "__main__":
    main()
