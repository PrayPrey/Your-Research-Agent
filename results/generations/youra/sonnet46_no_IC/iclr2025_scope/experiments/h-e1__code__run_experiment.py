"""H-E1 Experiment: Effective Rank as Zero-Shot LoRA Rank Predictor."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Add code dir to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))

from config import MODEL_CONFIGS, ExperimentConfig
from erank import compute_erank_map, save_erank_map, load_erank_map
from oracle import run_oracle_sweep, load_or_resume_oracle, compute_oracle_rank_map, layer_to_safe
from analyze import compute_pr_map, run_correlation_analysis, verify_mechanism, check_global_success
from visualize import generate_all_figures


def model_slug(model_name: str) -> str:
    return model_name.replace("/", "-")


def main(args) -> None:
    base_dir = Path(args.output_dir)
    results_dir = base_dir / "results"
    figures_dir = base_dir / "figures"

    for d in [results_dir, figures_dir]:
        d.mkdir(parents=True, exist_ok=True)

    all_erank_maps: dict[str, dict] = {}
    all_oracle_maps: dict[str, dict] = {}
    all_corr_results: dict[str, dict] = {}

    for model_name in args.models:
        slug = model_slug(model_name)
        print(f"\n{'='*60}")
        print(f"Processing: {model_name}")
        print(f"{'='*60}")

        cfg = ExperimentConfig.from_model(model_name, base_dir)
        cfg.oracle_ranks = [4, 8, 16, 32, 64]
        cfg.seeds = [42, 137]

        # Create dirs
        for d in [cfg.results_dir, cfg.figures_dir, cfg.checkpoint_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

        # 1. Compute erank map
        erank_path = results_dir / f"erank_map_{slug}.json"
        if args.resume and erank_path.exists():
            print(f"[resume] Loading erank_map from {erank_path}")
            erank_map = load_erank_map(erank_path)
        else:
            print(f"Computing erank map for {model_name}...")
            erank_map = compute_erank_map(model_name)
            save_erank_map(erank_map, erank_path)
            print(f"  Saved: {erank_path} ({len(erank_map)} layers)")

        # PoC layer sampling: every N-th layer to make oracle sweep tractable
        step = getattr(cfg, "layer_sample_step", 1)
        if step > 1:
            all_keys = sorted(erank_map.keys())
            sampled_keys = all_keys[::step]
            erank_map_oracle = {k: erank_map[k] for k in sampled_keys}
            print(f"  Layer sampling: {len(erank_map)} -> {len(erank_map_oracle)} layers (step={step})")
        else:
            erank_map_oracle = erank_map

        all_erank_maps[model_name] = erank_map  # keep full erank map for analysis

        # 2. Run oracle sweep
        oracle_path = results_dir / f"oracle_rank_map_{slug}.json"
        if args.resume and oracle_path.exists():
            print(f"[resume] Loading oracle_rank_map from {oracle_path}")
            oracle_rank_map = json.loads(oracle_path.read_text())
            # Convert str keys from JSON to proper format
        else:
            print(f"Running oracle sweep for {model_name} ({len(erank_map_oracle)} layers × 5 ranks × 2 seeds)...")
            oracle_rank_map = run_oracle_sweep(cfg, erank_map_oracle, max_workers=args.max_workers)
            oracle_path.write_text(json.dumps(oracle_rank_map, indent=2))
            print(f"  Saved: {oracle_path} ({len(oracle_rank_map)} layers)")
        all_oracle_maps[model_name] = oracle_rank_map

        # 3. Compute PR map (secondary metric)
        pr_path = results_dir / f"pr_map_{slug}.json"
        if args.resume and pr_path.exists():
            pr_map = json.loads(pr_path.read_text())
        else:
            print(f"Computing PR map for {model_name}...")
            try:
                pr_map = compute_pr_map(model_name)
                pr_path.write_text(json.dumps(pr_map, indent=2))
            except Exception as e:
                print(f"  PR map failed (non-critical): {e}")
                pr_map = None

        # 4. Correlation analysis
        corr_path = results_dir / f"correlation_{slug}.json"
        print(f"Running correlation analysis for {model_name}...")
        corr = run_correlation_analysis(erank_map, oracle_rank_map, pr_map, cfg)
        corr_path.write_text(json.dumps(corr, indent=2))
        all_corr_results[model_name] = corr

        status = "PASS ✓" if corr["pass"] else "FAIL ✗"
        print(f"  r={corr['r']:.4f}, p_one={corr['p_one_tailed']:.5f}, CI=[{corr['ci_low']:.3f},{corr['ci_high']:.3f}] → {status}")

        # 5. Mechanism verification
        mech_ok, mech_indicators = verify_mechanism(erank_map, oracle_rank_map, model_name)
        print(f"  Mechanism check: {'OK' if mech_ok else 'WARN'} — {mech_indicators}")

    # 6. Global success check
    global_pass = check_global_success(all_corr_results)
    verdict = "PASS" if global_pass else "FAIL"
    n_pass = sum(1 for r in all_corr_results.values() if r.get("pass"))
    print(f"\n{'='*60}")
    print(f"GLOBAL RESULT: {verdict} ({n_pass}/{len(all_corr_results)} families passed)")
    print(f"{'='*60}")

    # Save summary
    summary = {
        "global_pass": global_pass,
        "global_verdict": verdict,
        "n_families_passed": n_pass,
        "n_families_total": len(all_corr_results),
        "per_family": {
            model_name: {
                "r": all_corr_results[model_name]["r"],
                "p_one_tailed": all_corr_results[model_name]["p_one_tailed"],
                "ci_low": all_corr_results[model_name]["ci_low"],
                "ci_high": all_corr_results[model_name]["ci_high"],
                "n_layers": all_corr_results[model_name]["n_layers"],
                "pass": all_corr_results[model_name]["pass"],
            }
            for model_name in args.models
            if model_name in all_corr_results
        },
    }
    summary_path = results_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Summary saved: {summary_path}")

    # 7. Generate figures
    print(f"\nGenerating figures...")
    try:
        saved_figs = generate_all_figures(all_erank_maps, all_oracle_maps, all_corr_results, figures_dir)
        print(f"  Generated {len(saved_figs)} figures")
    except Exception as e:
        print(f"  Figure generation failed (non-critical): {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1: erank vs oracle rank correlation")
    parser.add_argument("--models", nargs="+", default=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/youra_research/h-e1"))
    parser.add_argument("--resume", action="store_true")
    main(parser.parse_args())
