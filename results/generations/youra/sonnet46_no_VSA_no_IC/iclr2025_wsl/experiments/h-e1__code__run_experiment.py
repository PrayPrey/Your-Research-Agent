"""
H-E1 Experiment: Equivariant vs Flat-MLP weight-space encoders on ModelZooDataset.
Gate condition: equivariant R² > Flat-MLP R² with non-overlapping 95% CI at ≤500 training models.
"""
import os
import sys
import json
import copy
import time
import torch
import numpy as np

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data import (load_zoo, diversity_check, subsample, detect_zoo_arch,
                  make_flat_loader, make_nfn_loader, make_gnn_loader,
                  compute_flat_scaler)
from encoders import build_encoder
from train import train_one, get_predictions
from evaluate import compute_r2_with_ci, ci_overlap, verify_permutation_equivariance
from visualize import generate_all_figures

os.makedirs(config.FIGURES_DIR, exist_ok=True)
os.makedirs(config.RESULTS_DIR, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")
if DEVICE == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")


def make_loader(encoder_name, dataset, batch_size, shuffle, scaler=None):
    if encoder_name in ("flat_mlp", "flat_mlp_perm_aug"):
        return make_flat_loader(dataset, batch_size, shuffle, scaler)
    elif encoder_name == "nfn":
        return make_nfn_loader(dataset, batch_size, shuffle)
    elif encoder_name == "gnn_nfn":
        return make_gnn_loader(dataset, batch_size, shuffle)
    raise ValueError(f"Unknown encoder: {encoder_name}")


def run_experiment() -> dict:
    torch.manual_seed(config.SEED)
    np.random.seed(config.SEED)
    results = {}
    start_time = time.time()

    for zoo_name in config.ZOO_NAMES:
        print(f"\n{'='*60}")
        print(f"Zoo: {zoo_name.upper()}")
        print(f"{'='*60}")

        # Load data
        print("Loading zoo data...")
        train_ds, val_ds, test_ds = load_zoo(zoo_name)
        print(f"  Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

        # Diversity check
        print("Diversity check...")
        div_info = diversity_check(test_ds)
        results[f"{zoo_name}_diversity_ok"] = div_info["passed"]
        results[f"{zoo_name}_test_accuracies"] = div_info["accs"]
        results[f"{zoo_name}_diversity"] = {
            "mean": div_info["mean"],
            "variance": div_info["variance"],
            "passed": div_info["passed"]
        }

        # Detect zoo architecture
        sample_sd, _ = train_ds[0]
        zoo_arch = detect_zoo_arch(sample_sd)
        results[f"{zoo_name}_zoo_arch"] = zoo_arch
        print(f"  Zoo architecture: {zoo_arch}")

        # Compute flat input dimension
        from data import _flatten_state_dict
        flat_dim = _flatten_state_dict(sample_sd).shape[0]
        print(f"  Flat weight dim: {flat_dim}")

        # Compute scaler for flat encoders (fit on full training set)
        print("Computing flat scaler...")
        flat_scaler = compute_flat_scaler(train_ds)

        # Get a sample wsfeat for NFN initialization
        sample_wsfeat = None
        if "nfn" in config.ENCODER_NAMES:
            nfn_loader_sample = make_nfn_loader(
                subsample(train_ds, 2, seed=config.SEED), 2, False
            )
            for batch in nfn_loader_sample:
                sample_wsfeat, _ = batch
                break

        for encoder_name in config.ENCODER_NAMES:
            print(f"\n  Encoder: {encoder_name}")

            # Skip GNN-NFN if PyG not working well (optional)
            for budget_tier, target_params in config.BUDGET_TIERS.items():
                print(f"    Budget tier: {budget_tier} (~{target_params:,} params)")

                # Build encoder
                enc = build_encoder(
                    encoder_name, flat_dim, target_params,
                    zoo_arch=zoo_arch,
                    sample_wsfeat=sample_wsfeat
                )

                # Log actual param count
                if hasattr(enc, 'count_params'):
                    n_params = enc.count_params()
                else:
                    n_params = sum(p.numel() for p in enc.parameters())
                results[f"{zoo_name}_{encoder_name}_{budget_tier}_params"] = n_params
                print(f"      Params: {n_params:,}")

                # Permutation equivariance test (equivariant encoders)
                if encoder_name in ("nfn", "gnn_nfn") and sample_wsfeat is not None:
                    # Move encoder to device first with a quick forward
                    try:
                        enc_temp = copy.deepcopy(enc).to(DEVICE)
                        from train import _move_wsfeat
                        sw_dev = _move_wsfeat(sample_wsfeat, DEVICE)
                        with torch.no_grad():
                            _ = enc_temp(sw_dev)
                        eq_result = verify_permutation_equivariance(
                            enc_temp, sample_wsfeat, encoder_name, device=DEVICE
                        )
                        results[f"{zoo_name}_{encoder_name}_equivariance"] = eq_result
                        print(f"      Equivariance: {eq_result['details']}")
                    except Exception as e:
                        print(f"      Equivariance test error: {e}")
                        results[f"{zoo_name}_{encoder_name}_equivariance"] = {
                            "passed": False, "max_deviation": -1, "details": str(e)
                        }

                for size in config.TRAINING_SIZES:
                    key = f"{zoo_name}_{encoder_name}_{budget_tier}_{size}"
                    print(f"      Training size={size}...", end=" ", flush=True)

                    # Subsample training set
                    sub_train = subsample(train_ds, size if size != "full" else len(train_ds),
                                         seed=config.SEED)
                    size_str = str(size)

                    # Build fresh encoder for each (size, budget_tier) combination
                    enc_fresh = build_encoder(
                        encoder_name, flat_dim, target_params,
                        zoo_arch=zoo_arch,
                        sample_wsfeat=sample_wsfeat
                    )

                    # Make loaders
                    train_loader = make_loader(
                        encoder_name, sub_train,
                        min(config.BATCH_SIZE, len(sub_train)),
                        shuffle=True,
                        scaler=flat_scaler if encoder_name in ("flat_mlp", "flat_mlp_perm_aug") else None
                    )
                    val_loader = make_loader(
                        encoder_name, val_ds, config.BATCH_SIZE, shuffle=False,
                        scaler=flat_scaler if encoder_name in ("flat_mlp", "flat_mlp_perm_aug") else None
                    )
                    test_loader = make_loader(
                        encoder_name, test_ds, config.BATCH_SIZE, shuffle=False,
                        scaler=flat_scaler if encoder_name in ("flat_mlp", "flat_mlp_perm_aug") else None
                    )

                    # Train
                    try:
                        t0 = time.time()
                        train_one(
                            enc_fresh, train_loader, val_loader,
                            encoder_name=encoder_name,
                            epochs=config.EPOCHS,
                            lr=config.LR,
                            weight_decay=config.WEIGHT_DECAY,
                            seed=config.SEED,
                            device=DEVICE
                        )
                        elapsed = time.time() - t0

                        # Evaluate on test set
                        y_true, y_pred = get_predictions(
                            enc_fresh, test_loader, encoder_name, DEVICE
                        )
                        r_info = compute_r2_with_ci(y_true, y_pred, config.N_BOOTSTRAP)
                        results[key] = r_info
                        print(f"R²={r_info['r2']:.4f} "
                              f"CI=[{r_info['ci_low']:.4f},{r_info['ci_high']:.4f}] "
                              f"({elapsed:.0f}s)")

                    except Exception as e:
                        print(f"FAILED: {e}")
                        results[key] = {"r2": float("nan"), "ci_low": float("nan"),
                                        "ci_high": float("nan"), "error": str(e)}

                    # Save intermediate results
                    _save_results(results)

    # Compute gate decision
    gate_result = evaluate_gate(results)
    results["gate"] = gate_result
    print(f"\n{'='*60}")
    print(f"GATE RESULT: {gate_result['verdict']}")
    print(f"Reason: {gate_result['reason']}")
    print(f"{'='*60}")

    # Generate figures
    print("\nGenerating figures...")
    figure_paths = generate_all_figures(results)
    results["figures"] = figure_paths

    # Final save
    _save_results(results)
    total_time = time.time() - start_time
    print(f"\nTotal experiment time: {total_time/60:.1f} min")
    print(f"Results saved to: {config.RESULTS_DIR}")
    return results


def evaluate_gate(results: dict) -> dict:
    """
    Gate: equivariant R² > Flat-MLP R² with non-overlapping 95% CI
    at ≥1 training size ≤500, on ≥1 zoo.
    """
    budget_tier = "medium"
    equivariant_encoders = ["nfn", "gnn_nfn"]
    small_sizes = [s for s in config.TRAINING_SIZES if s != "full" and s <= 500]

    gate_satisfied = False
    evidence = []

    for zoo in config.ZOO_NAMES:
        flat_results = {}
        for size in small_sizes:
            key = f"{zoo}_flat_mlp_{budget_tier}_{size}"
            flat_results[size] = results.get(key, {})

        for enc in equivariant_encoders:
            for size in small_sizes:
                key = f"{zoo}_{enc}_{budget_tier}_{size}"
                eq_r = results.get(key, {})
                flat_r = flat_results.get(size, {})

                r2_eq = eq_r.get("r2", float("nan"))
                r2_flat = flat_r.get("r2", float("nan"))

                if np.isnan(r2_eq) or np.isnan(r2_flat):
                    continue

                ci_eq = (eq_r.get("ci_low", r2_eq), eq_r.get("ci_high", r2_eq))
                ci_flat = (flat_r.get("ci_low", r2_flat), flat_r.get("ci_high", r2_flat))

                r2_higher = r2_eq > r2_flat
                non_overlapping = not ci_overlap(ci_eq, ci_flat)

                evidence.append({
                    "zoo": zoo, "encoder": enc, "size": size,
                    "r2_equivariant": r2_eq, "r2_flat_mlp": r2_flat,
                    "r2_diff": r2_eq - r2_flat,
                    "ci_equivariant": ci_eq, "ci_flat_mlp": ci_flat,
                    "r2_higher": r2_higher,
                    "non_overlapping_ci": non_overlapping,
                    "criterion_met": r2_higher and non_overlapping
                })

                if r2_higher and non_overlapping:
                    gate_satisfied = True

    if gate_satisfied:
        verdict = "PASS"
        reason = ("Equivariant encoder achieves higher R² than Flat-MLP with "
                  "non-overlapping 95% CI at ≥1 training size ≤500.")
    else:
        verdict = "FAIL"
        reason = ("Equivariant encoder did NOT achieve higher R² than Flat-MLP "
                  "with non-overlapping 95% CI at any training size ≤500.")

    return {"verdict": verdict, "reason": reason, "evidence": evidence}


def _save_results(results: dict):
    path = os.path.join(config.RESULTS_DIR, "results.json")

    def _serialize(obj):
        if isinstance(obj, float) and np.isnan(obj):
            return None
        if isinstance(obj, (np.floating, np.integer)):
            return obj.item()
        return obj

    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=_serialize)


if __name__ == "__main__":
    results = run_experiment()
    gate = results.get("gate", {})
    verdict = gate.get("verdict", "UNKNOWN")
    print(f"\nFinal gate verdict: {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)
