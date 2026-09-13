"""A-9: Pipeline Orchestrator — checkpoint/resume over all 7 stages."""
import argparse
import json
import sys
from pathlib import Path

from config import (
    PIPELINE_STAGES, CHECKPOINT_DIR, FIGURES_DIR, BASE_DIR,
    BENCHMARKS, SAMPLE_SIZE, RANDOM_SEED, NGRAM_SIZE, PILE_HF_ID, PILE_DEDUP_HF_ID
)


def stage_done(stage: str) -> bool:
    """Check if a stage has a completed checkpoint."""
    from config import PipelineConfig
    cfg = PipelineConfig()
    ckpt_file = cfg.checkpoint_files.get(stage)
    if not ckpt_file:
        return False
    return (cfg.checkpoint_dir / ckpt_file).exists()


def run(resume: bool = True, skip_stages: list[str] | None = None) -> dict:
    """End-to-end pipeline.

    Stages: hash_diff → sample → ngrams → overlaps → stats → ablations → figures
    Each stage skips if checkpoint exists and resume=True.
    """
    skip_stages = skip_stages or []
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    # ── Stage 1: hash_diff ──────────────────────────────────────────────────
    if "hash_diff" not in skip_stages and (not resume or not stage_done("hash_diff")):
        print("\n═══ Stage: hash_diff ═══")
        from corpus_streamer import find_removed_hashes
        removed_hashes = find_removed_hashes(
            pile_id=PILE_HF_ID,
            dedup_id=PILE_DEDUP_HF_ID,
            checkpoint_path=CHECKPOINT_DIR / "removed_hashes.json",
        )
    else:
        print("\n═══ Stage: hash_diff (skipped — checkpoint exists) ═══")
        ckpt = CHECKPOINT_DIR / "removed_hashes.json"
        payload = json.loads(ckpt.read_text())
        removed_hashes = payload.get("hashes", payload)

    results["n_removed_total"] = len(removed_hashes)
    print(f"  Removed hash pool: {len(removed_hashes):,}")

    # ── Stage 2: sample ──────────────────────────────────────────────────────
    if "sample" not in skip_stages and (not resume or not stage_done("sample")):
        print("\n═══ Stage: sample ═══")
        from sampler import stratified_reservoir_sample
        sampled_docs = stratified_reservoir_sample(
            removed_hashes=removed_hashes,
            checkpoint_path=CHECKPOINT_DIR / "sampled_docs.json",
        )
    else:
        print("\n═══ Stage: sample (skipped — checkpoint exists) ═══")
        from sampler import _docs_from_json
        data = json.loads((CHECKPOINT_DIR / "sampled_docs.json").read_text())
        sampled_docs = {
            "removed": _docs_from_json(data["removed"]),
            "retained": _docs_from_json(data["retained"]),
        }

    results["n_removed_sampled"] = len(sampled_docs["removed"])
    results["n_retained_sampled"] = len(sampled_docs["retained"])
    print(f"  Removed sampled: {len(sampled_docs['removed'])}, "
          f"Retained sampled: {len(sampled_docs['retained'])}")

    # ── Stage 3: ngrams ──────────────────────────────────────────────────────
    if "ngrams" not in skip_stages and (not resume or not stage_done("ngrams")):
        print("\n═══ Stage: ngrams ═══")
        from benchmark_ngrams import extract_ngrams
        ngram_sets = extract_ngrams(
            benchmarks=BENCHMARKS, n=NGRAM_SIZE,
            checkpoint_path=CHECKPOINT_DIR / "ngram_sets.pkl",
        )
    else:
        print("\n═══ Stage: ngrams (skipped — checkpoint exists) ═══")
        import pickle
        with open(CHECKPOINT_DIR / "ngram_sets.pkl", "rb") as f:
            ngram_sets = pickle.load(f)

    for b, ngs in ngram_sets.items():
        print(f"  {b}: {len(ngs):,} unique 13-grams")

    # ── Stage 4: overlaps ────────────────────────────────────────────────────
    if "overlaps" not in skip_stages and (not resume or not stage_done("overlaps")):
        print("\n═══ Stage: overlaps ═══")
        from overlap_computer import compute_all_overlaps
        overlap_scores = compute_all_overlaps(
            sampled_docs=sampled_docs,
            ngram_sets=ngram_sets,
            checkpoint_path=CHECKPOINT_DIR / "overlap_scores.json",
        )
    else:
        print("\n═══ Stage: overlaps (skipped — checkpoint exists) ═══")
        from overlap_computer import load_overlap_checkpoint
        cached = load_overlap_checkpoint(CHECKPOINT_DIR / "overlap_scores.json")
        if cached is None:
            raise RuntimeError("overlap_scores.json missing despite stage_done=True")
        removed_arr, retained_arr, benchmarks = cached
        overlap_scores = {"removed": {}, "retained": {}}
        for i, b in enumerate(benchmarks):
            overlap_scores["removed"][b] = removed_arr[:, i].tolist()
            overlap_scores["retained"][b] = retained_arr[:, i].tolist()

    results["overlap_summary"] = {
        b: {
            "mean_removed": float(sum(overlap_scores["removed"][b]) / len(overlap_scores["removed"][b])),
            "mean_retained": float(sum(overlap_scores["retained"][b]) / len(overlap_scores["retained"][b])),
        }
        for b in overlap_scores["removed"]
    }

    # ── Stage 5: stats ───────────────────────────────────────────────────────
    if "stats" not in skip_stages and (not resume or not stage_done("stats")):
        print("\n═══ Stage: stats ═══")
        from statistical_tester import run_tests
        stat_results = run_tests(
            overlap_scores=overlap_scores,
            checkpoint_path=CHECKPOINT_DIR / "statistical_results.json",
        )
    else:
        print("\n═══ Stage: stats (skipped — checkpoint exists) ═══")
        stat_results = json.loads((CHECKPOINT_DIR / "statistical_results.json").read_text())

    results["statistical_results"] = stat_results
    gate_pass = stat_results.get("summary", {}).get("gate_pass", False)
    n_sig = stat_results.get("summary", {}).get("n_significant", 0)
    print(f"  Gate: {'PASS' if gate_pass else 'FAIL'} ({n_sig}/4 significant)")

    # ── Stage 6: ablations ───────────────────────────────────────────────────
    if "ablations" not in skip_stages and (not resume or not stage_done("ablations")):
        print("\n═══ Stage: ablations ═══")
        from ablation_runner import run_all_ablations
        ablation_results = run_all_ablations(
            sampled_docs=sampled_docs,
            ngram_sets=ngram_sets,
            checkpoint_path=CHECKPOINT_DIR / "ablation_results.json",
        )
    else:
        print("\n═══ Stage: ablations (skipped — checkpoint exists) ═══")
        ablation_results = json.loads((CHECKPOINT_DIR / "ablation_results.json").read_text())

    results["ablation_results"] = ablation_results

    # ── Stage 7: figures ─────────────────────────────────────────────────────
    if "figures" not in skip_stages:
        print("\n═══ Stage: figures ═══")
        from visualizer import generate_all_figures
        generate_all_figures(overlap_scores, stat_results, ablation_results)

    # ── Final summary ─────────────────────────────────────────────────────────
    results["gate_result"] = "PASS" if gate_pass else "FAIL"
    results["gate_condition"] = "n_significant >= 2"
    results["n_significant"] = n_sig

    print("\n" + "═" * 60)
    print(f"PIPELINE COMPLETE")
    print(f"Gate: {results['gate_result']} ({n_sig}/4 benchmarks significant)")
    if stat_results.get("per_benchmark"):
        for b, s in stat_results["per_benchmark"].items():
            sig = "✅" if s["significant"] else "❌"
            print(f"  {sig} {b}: p_corr={s['p_corrected']:.4f}, ratio={s['ratio']:.2f}×")
    print("═" * 60)

    # Save final results
    out_path = BASE_DIR / "experiment_results.json"
    import os
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(results, indent=2))
    os.replace(tmp, out_path)
    print(f"✓ Results saved to {out_path}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M1 corpus contamination analysis pipeline")
    parser.add_argument("--no-resume", action="store_true", help="Rerun from scratch")
    parser.add_argument("--skip", nargs="+", metavar="STAGE",
                        choices=PIPELINE_STAGES, default=[],
                        help="Skip named stages")
    args = parser.parse_args()
    run(resume=not args.no_resume, skip_stages=args.skip)
