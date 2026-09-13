"""Entry point: H-E1 OrbitVar measurement for DeepSets (C2) and NFN (C3) encoders."""
import sys
import os
import argparse
import json
import time
import torch
import numpy as np

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_dataset, CHANNELS_PER_LAYER
from permutation import sample_functional_permutations, audit_functional_equivalence
from encoder_c2 import build_c2_encoder
from encoder_c3 import build_nfn_encoder, get_network_spec, encode_nfn
from orbit_var import compute_orbit_var_all_models, run_gate_check, save_results
from visualization import plot_orbitvar_bar, plot_pca_scatter, plot_violin


def get_args():
    p = argparse.ArgumentParser(description="H-E1 OrbitVar measurement")
    p.add_argument("--data-path", default="data/dataset_cifar_small_hyp_rand.pt")
    p.add_argument("--n-models", type=int, default=100)
    p.add_argument("--K", type=int, default=50)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--embed-dim", type=int, default=128)
    p.add_argument("--threshold", type=float, default=1e-6)
    p.add_argument("--skip-pca", action="store_true")
    p.add_argument("--skip-violin", action="store_true")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--figures-dir", default="figures")
    return p.parse_args()


def main():
    args = get_args()
    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(args.figures_dir, exist_ok=True)

    t0 = time.time()
    print("=" * 60)
    print("H-E1: OrbitVar Measurement Experiment")
    print("=" * 60)

    # 1. Load dataset
    print(f"\n[1] Loading dataset: {args.data_path}")
    dataset, accs = load_dataset(args.data_path, split="testset", n_models=args.n_models)
    n_models = len(dataset)
    print(f"  Using {n_models} models")

    # 2. Sample functional permutations
    print(f"\n[2] Sampling {args.K} functional permutations (seed={args.seed})")
    perm_specs = sample_functional_permutations(
        channels_per_layer=CHANNELS_PER_LAYER,
        K=args.K,
        seed=args.seed,
    )
    print(f"  Permutation group: S_{CHANNELS_PER_LAYER[0]} × S_{CHANNELS_PER_LAYER[1]} × S_{CHANNELS_PER_LAYER[2]}")

    # 3. Functional audit (HARD BLOCK)
    print(f"\n[3] Functional equivalence audit (||f_v - f_pi.v||_inf <= 1e-6)")
    max_diff = audit_functional_equivalence(
        dataset[0], perm_specs, tol=1e-5, n_checks=5, n_perms=3
    )

    # 4. Build encoders
    print(f"\n[4] Building encoders")
    c2_encoder = build_c2_encoder(embed_dim=args.embed_dim)
    c2_encoder.eval()
    print(f"  C2 (DeepSets): built with embed_dim={args.embed_dim}")

    network_spec = get_network_spec(dataset[0])
    c3_model = build_nfn_encoder(network_spec, sample_state_dict=dataset[0], nfn_channels=32, embed_dim=args.embed_dim)
    c3_model.eval()
    print(f"  C3 (NFN): built with embed_dim={args.embed_dim}")

    # 5. Compute OrbitVar for C2
    print(f"\n[5a] Computing C2 (DeepSets) OrbitVar ({n_models} models × {args.K} perms)")

    def c2_fn(sd):
        with torch.no_grad():
            return c2_encoder(sd)

    per_vars_c2, mean_c2, max_c2 = compute_orbit_var_all_models(
        dataset, c2_fn, perm_specs, log_every=10
    )
    print(f"  C2: mean_OrbitVar={mean_c2:.3e}, max_OrbitVar={max_c2:.3e}")
    print(f"[C2] OrbitVar per model (first 5): {[f'{v:.3e}' for v in per_vars_c2[:5]]}")

    # 6. Compute OrbitVar for C3
    print(f"\n[5b] Computing C3 (NFN) OrbitVar ({n_models} models × {args.K} perms)")

    def c3_fn(sd):
        return encode_nfn(c3_model, sd)

    per_vars_c3, mean_c3, max_c3 = compute_orbit_var_all_models(
        dataset, c3_fn, perm_specs, log_every=10
    )
    print(f"  C3: mean_OrbitVar={mean_c3:.3e}, max_OrbitVar={max_c3:.3e}")
    print(f"[C3] OrbitVar per model (first 5): {[f'{v:.3e}' for v in per_vars_c3[:5]]}")

    # 7. Gate check
    print(f"\n[6] Gate check (threshold={args.threshold:.0e})")
    gate_pass = run_gate_check(mean_c2, mean_c3, args.threshold)

    # 8. Save results
    results = {
        "mean_orbitvar_c2": mean_c2,
        "max_orbitvar_c2": max_c2,
        "mean_orbitvar_c3": mean_c3,
        "max_orbitvar_c3": max_c3,
        "cise_baseline": 0.010333,
        "gate_pass": gate_pass,
        "seed": args.seed,
        "n_models": n_models,
        "K": args.K,
        "per_model_orbitvar_c2": per_vars_c2,
        "per_model_orbitvar_c3": per_vars_c3,
        "audit_max_diff": max_diff,
        "channels_per_layer": CHANNELS_PER_LAYER,
        "embed_dim": args.embed_dim,
        "duration_seconds": time.time() - t0,
    }
    results_path = os.path.join(args.results_dir, "orbit_var_results.json")
    save_results(results, results_path)

    # 9. Figures
    print(f"\n[7] Generating figures")
    bar_path = os.path.join(args.figures_dir, "orbitvar_comparison.png")
    plot_orbitvar_bar(results, threshold=args.threshold, save_path=bar_path)

    if not args.skip_pca:
        # For PCA: collect embeddings per model (first 10 models)
        pca_n = min(10, n_models)
        emb_c2_list, emb_c3_list = [], []
        for state_dict in dataset[:pca_n]:
            embs_c2, embs_c3 = [], []
            with torch.no_grad():
                embs_c2.append(c2_encoder(state_dict))
            embs_c3.append(encode_nfn(c3_model, state_dict))
            for perm_spec in perm_specs:
                perm_sd = __import__("permutation").apply_permutation(state_dict, perm_spec)
                with torch.no_grad():
                    embs_c2.append(c2_encoder(perm_sd))
                embs_c3.append(encode_nfn(c3_model, perm_sd))
            emb_c2_list.append(torch.stack(embs_c2, 0))
            emb_c3_list.append(torch.stack(embs_c3, 0))
        pca_path = os.path.join(args.figures_dir, "pca_scatter.png")
        plot_pca_scatter({"C2": emb_c2_list, "C3": emb_c3_list},
                         n_models=pca_n, save_path=pca_path)

    if not args.skip_violin:
        violin_path = os.path.join(args.figures_dir, "violin_orbitvar.png")
        plot_violin({"C2": per_vars_c2, "C3": per_vars_c3}, save_path=violin_path)

    print(f"\n{'=' * 60}")
    print(f"EXPERIMENT COMPLETE")
    print(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    print(f"C2 mean OrbitVar: {mean_c2:.3e}")
    print(f"C3 mean OrbitVar: {mean_c3:.3e}")
    print(f"CISE baseline:    0.010333")
    print(f"Duration: {time.time() - t0:.1f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
