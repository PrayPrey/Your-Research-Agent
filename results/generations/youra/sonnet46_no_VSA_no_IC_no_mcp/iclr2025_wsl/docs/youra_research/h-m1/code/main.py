"""H-M1: NFT Orbit Invariance Probe — main experiment runner."""
import sys
import os
import json
import pathlib
import time

import torch

CODE_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from data_loader import load_zoo, get_zoo_tensors
from nft_encoder import load_nft_encoder, extract_embeddings
from nft_training import train_nft_fallback
from orbit_construction import build_orbit_pairs, sample_base_models
from similarity_analysis import build_cross_orbit_pairs, compute_similarity_vectors
from statistics import evaluate_gate, verify_probe_activated
from visualization import generate_all_figures

CHECKPOINT_PATH = str(CODE_DIR.parent.parent.parent / "h-e1/code/checkpoints/nft_condition_a.pt")
HM1_CHECKPOINT  = str(CODE_DIR / "checkpoints/nft_condition_a_hm1.pt")
RESULTS_PATH    = str(CODE_DIR.parent / "results.json")
FIGURES_DIR     = str(CODE_DIR.parent / "figures")
N_ORBIT_PAIRS   = 1000
SEED            = 42
BATCH_SIZE      = 64


def run(
    n_orbit_pairs=N_ORBIT_PAIRS,
    seed=SEED,
    checkpoint_path=CHECKPOINT_PATH,
    results_path=RESULTS_PATH,
    device=None,
):
    t0 = time.time()
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # 1. Load zoo
    print("Loading zoo...")
    zoo_records = load_zoo()
    zoo_weights, zoo_properties = get_zoo_tensors(zoo_records, device="cpu")
    N = len(zoo_weights)
    print(f"Zoo: {N} models, properties shape: {zoo_properties.shape}")

    # 2. Load/train NFT
    try:
        nft = load_nft_encoder(checkpoint_path, device=device)
    except FileNotFoundError as e:
        print(f"H-E1 checkpoint not found ({e}). Checking H-M1 checkpoint...")
        try:
            nft = load_nft_encoder(HM1_CHECKPOINT, device=device)
        except FileNotFoundError:
            print("No checkpoint found. Training NFT fallback (FR-0.3)...")
            nft = train_nft_fallback(
                zoo_weights, zoo_properties,
                save_path=HM1_CHECKPOINT,
                device=device,
                n_epochs=100,
                batch_size=BATCH_SIZE,
                seed=seed,
            )
    nft.to(device)
    nft.eval()
    print(f"NFT loaded. d_model={nft.d_model}")

    # 3. Probe scaling orbits
    print("\n=== Probing SCALING orbits ===")
    base_idx_s, _ = sample_base_models(zoo_weights, n=n_orbit_pairs, seed=seed)
    base_s, orbit_s = build_orbit_pairs(zoo_weights, base_idx_s, "scaling", seed)
    cross_s, cross_idx_s = build_cross_orbit_pairs(zoo_weights, zoo_properties, base_idx_s, seed)

    print(f"Orbit pairs constructed: {len(base_s)} scaling")
    print("Extracting base embeddings...")
    emb_base_s  = extract_embeddings(nft, base_s,  batch_size=BATCH_SIZE, device=device)
    print("Extracting orbit embeddings...")
    emb_orbit_s = extract_embeddings(nft, orbit_s, batch_size=BATCH_SIZE, device=device)
    print("Extracting cross embeddings...")
    emb_cross_s = extract_embeddings(nft, cross_s, batch_size=BATCH_SIZE, device=device)
    sims_s = compute_similarity_vectors(emb_base_s, emb_orbit_s, emb_cross_s)
    results_scaling = {
        "orbit_type": "scaling", **sims_s,
        "base_indices": base_idx_s, "cross_indices": cross_idx_s,
    }
    print(f"[scaling] within_sim: mean={sims_s['within_sim'].mean():.4f}  "
          f"cross_sim: mean={sims_s['cross_sim'].mean():.4f}  "
          f"gap: mean={sims_s['gap'].mean():.4f}")

    # 4. Probe sign-flip orbits
    print("\n=== Probing SIGN-FLIP orbits ===")
    base_idx_sf, _ = sample_base_models(zoo_weights, n=n_orbit_pairs, seed=seed + 1)
    base_sf, orbit_sf = build_orbit_pairs(zoo_weights, base_idx_sf, "signflip", seed)
    cross_sf, cross_idx_sf = build_cross_orbit_pairs(zoo_weights, zoo_properties, base_idx_sf, seed + 1)

    print(f"Orbit pairs constructed: {len(base_sf)} signflip")
    print("Extracting base embeddings...")
    emb_base_sf  = extract_embeddings(nft, base_sf,  batch_size=BATCH_SIZE, device=device)
    print("Extracting orbit embeddings...")
    emb_orbit_sf = extract_embeddings(nft, orbit_sf, batch_size=BATCH_SIZE, device=device)
    print("Extracting cross embeddings...")
    emb_cross_sf = extract_embeddings(nft, cross_sf, batch_size=BATCH_SIZE, device=device)
    sims_sf = compute_similarity_vectors(emb_base_sf, emb_orbit_sf, emb_cross_sf)
    results_signflip = {
        "orbit_type": "signflip", **sims_sf,
        "base_indices": base_idx_sf, "cross_indices": cross_idx_sf,
    }
    print(f"[signflip] within_sim: mean={sims_sf['within_sim'].mean():.4f}  "
          f"cross_sim: mean={sims_sf['cross_sim'].mean():.4f}  "
          f"gap: mean={sims_sf['gap'].mean():.4f}")

    # 5. Mechanism verification
    ok, indicators = verify_probe_activated(
        results_scaling["within_sim"], results_scaling["cross_sim"], n_orbit_pairs
    )

    # 6. Gate evaluation
    print("\n=== Gate Evaluation ===")
    gate = evaluate_gate(results_scaling, results_signflip, n_boot=1000, seed=seed)
    print(f"Verdict: {gate['verdict']}")
    for ot in ["scaling", "signflip"]:
        r = gate[ot]
        print(f"  [{ot}] within={r['mean_within_sim']:.4f}  cross={r['mean_cross_sim']:.4f}  "
              f"gap={r['mean_gap']:.4f}  CI=[{r['ci_low']:.4f},{r['ci_high']:.4f}]  "
              f"gate={'PASS' if r['gate_pass'] else 'FAIL'}")

    # 7. Figures
    print("\n=== Generating Figures ===")
    generate_all_figures(
        results_scaling, results_signflip, zoo_properties, gate,
        emb_base_s, emb_orbit_s, emb_base_sf, emb_orbit_sf,
        out_dir=FIGURES_DIR,
    )

    # 8. Results JSON
    def t(tensor):
        return tensor.tolist() if hasattr(tensor, "tolist") else tensor

    results = {
        "hypothesis": "H-M1",
        "config": {
            "n_orbit_pairs": n_orbit_pairs,
            "seed": seed,
            "device": device,
            "checkpoint_path": checkpoint_path,
        },
        "gate": {
            "overall_pass": gate["overall_pass"],
            "verdict": gate["verdict"],
            "scaling": {k: v for k, v in gate["scaling"].items()
                        if not isinstance(v, dict)},
            "signflip": {k: v for k, v in gate["signflip"].items()
                         if not isinstance(v, dict)},
        },
        "stats": {
            "scaling": {
                "within_mean": float(sims_s["within_sim"].mean()),
                "within_std":  float(sims_s["within_sim"].std()),
                "cross_mean":  float(sims_s["cross_sim"].mean()),
                "cross_std":   float(sims_s["cross_sim"].std()),
                "gap_mean":    float(sims_s["gap"].mean()),
                "gap_ci_low":  gate["scaling"]["ci_low"],
                "gap_ci_high": gate["scaling"]["ci_high"],
            },
            "signflip": {
                "within_mean": float(sims_sf["within_sim"].mean()),
                "within_std":  float(sims_sf["within_sim"].std()),
                "cross_mean":  float(sims_sf["cross_sim"].mean()),
                "cross_std":   float(sims_sf["cross_sim"].std()),
                "gap_mean":    float(sims_sf["gap"].mean()),
                "gap_ci_low":  gate["signflip"]["ci_low"],
                "gap_ci_high": gate["signflip"]["ci_high"],
            },
        },
        "probe_activated": ok,
        "probe_indicators": indicators,
        "elapsed_s": round(time.time() - t0, 1),
    }

    path = pathlib.Path(results_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {results_path}")
    print(f"Elapsed: {results['elapsed_s']}s")

    if not gate["overall_pass"]:
        print("GATE: FAIL — NFT may already be orbit-invariant. EXPLORE path.", file=sys.stderr)
        sys.exit(1)

    print("\nGATE: PASS — NFT NOT orbit-invariant. Mechanism confirmed.")
    return results


if __name__ == "__main__":
    run()
