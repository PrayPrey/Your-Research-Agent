"""Orchestrator for h-c1-v2: RLHF calibration moderation — task-type-conditional ΔΔECE."""
import os, sys, json, traceback
from datetime import datetime

# Ensure this code dir is first on path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# Also set cwd to project root for relative path resolution
_PROJECT_ROOT = os.path.normpath(os.path.join(_THIS_DIR, "../../../.."))
os.chdir(_PROJECT_ROOT)

from config import HC1V2Config
from data.cache_loader import load_h_c1_cache, load_label_preservation_mask
from data.loader import load_hc1v2_datasets
from comparison.conditional_ece import (
    compute_moderation_by_benchmark_type,
    compute_cross_size_moderation,
    evaluate_gate,
    summarize_results,
    run_13b_inference_direct,
)
from visualization.plots import (
    fig1_ddece_bar, fig2_reliability_diagrams, fig3_confidence_histogram,
    fig4_moderation_heatmap, fig5_ddece_vs_difficulty,
)

def write_json(path: str, data) -> None:
    import json
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def write_validation_report(results: dict, gate_passed: bool, config: HC1V2Config) -> str:
    gate_str = "PASS" if gate_passed else "FAIL"
    lines = [
        f"# Validation Report: h-c1-v2",
        f"**Date:** {datetime.now().isoformat()}",
        f"**Gate Type:** SHOULD_WORK",
        f"",
        f"## Gate Result: {gate_str}",
        f"",
        f"| Metric | Value | Threshold |",
        f"|--------|-------|-----------|",
        f"| ANLI moderation rate (7B pair) | {results.get('anli_rate_7b', 0):.4f} | ≥0.60 |",
        f"| ANLI moderation rate (13B pair) | {results.get('anli_rate_13b', 0):.4f} | ≥0.60 (secondary) |",
        f"| AdvGLUE moderation rate (7B pair) | {results.get('advglue_rate_7b', 0):.4f} | boundary |",
        f"",
        f"## Per-Cell ΔΔECE (7B pair)",
        f"",
        f"| Cell | ΔECE_base | ΔECE_chat | ΔΔECE | Moderation |",
        f"|------|-----------|-----------|-------|------------|",
    ]

    for r in results.get("anli_results_7b", []):
        mod = "✓" if r["moderation_confirmed"] else "✗"
        lines.append(
            f"| {r['cell_id']} | {r['delta_ece_base']:.4f} | {r['delta_ece_chat']:.4f} | {r['ddece']:.4f} | {mod} |"
        )
    for r in results.get("advglue_results_7b", []):
        mod = "boundary"
        lines.append(
            f"| {r['cell_id']} (boundary) | {r['delta_ece_base']:.4f} | {r['delta_ece_chat']:.4f} | {r['ddece']:.4f} | {mod} |"
        )

    lines += [
        f"",
        f"## Per-Cell ΔΔECE (13B pair — cross-size validation)",
        f"",
        f"| Cell | ΔECE_base | ΔECE_chat | ΔΔECE | Moderation |",
        f"|------|-----------|-----------|-------|------------|",
    ]
    for r in results.get("anli_results_13b", []):
        mod = "✓" if r["moderation_confirmed"] else "✗"
        lines.append(
            f"| {r['cell_id']} | {r['delta_ece_base']:.4f} | {r['delta_ece_chat']:.4f} | {r['ddece']:.4f} | {mod} |"
        )

    lines += [
        f"",
        f"## Gate Evaluation",
        f"",
        f"- **Gate type**: SHOULD_WORK",
        f"- **Criterion**: ANLI moderation_rate (7B pair) ≥ 0.60",
        f"- **Result**: {gate_str}",
        f"- **ANLI moderation rate**: {results.get('anli_rate_7b', 0):.4f}",
        f"- **Margin**: {results.get('gate', {}).get('margin', 0):.4f}",
        f"",
        f"## Key Findings",
        f"",
        f"- ANLI moderation rate (7B): {results.get('anli_rate_7b', 0):.4f} (threshold 0.60)",
        f"- AdvGLUE reversal documented as benchmark-type boundary condition",
        f"- Cross-size validation (13B-chat) ANLI rate: {results.get('anli_rate_13b', 0):.4f}",
    ]

    if not gate_passed:
        lines += [
            f"",
            f"## Failure Mode Analysis",
            f"",
            f"Gate FAILED. ANLI moderation rate below threshold.",
            f"Documenting as EXPLORE finding: RLHF alignment moderation of calibration",
            f"degradation may be benchmark-type-specific or insufficient at this scale.",
        ]

    report = "\n".join(lines)
    os.makedirs(os.path.dirname(config.validation_report), exist_ok=True)
    with open(config.validation_report, "w") as f:
        f.write(report)
    print(f"✓ Validation report saved: {config.validation_report}")
    return report


def main(config: HC1V2Config = None) -> bool:
    config = config or HC1V2Config()
    os.makedirs(config.results_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)
    os.makedirs(config.new_inference_output, exist_ok=True)

    print("\n" + "="*60)
    print("H-C1-V2: RLHF Calibration Moderation — Conditional ΔΔECE")
    print("="*60)

    # Step 1: Load h-c1 cache (7B base + 7B chat, all cells)
    print("\n[Step 1] Loading h-c1 cache...")
    cache = load_h_c1_cache(config.h_c1_results_file)
    base_7b = cache.get("meta-llama/Llama-2-7b-hf", {})
    chat_7b = cache.get("meta-llama/Llama-2-7b-chat-hf", {})
    print(f"  base_7b cells: {list(base_7b.keys())}")
    print(f"  chat_7b cells: {list(chat_7b.keys())}")

    # Step 2: Run 13B-chat new inference
    print("\n[Step 2] Running 13B-chat inference...")
    try:
        datasets = load_hc1v2_datasets(seed=config.seed, subsample_clean=config.subsample_clean)
        tasks = ["anli_r1", "anli_r2", "anli_r3", "adv_glue_mnli"]
        chat_13b = run_13b_inference_direct(
            model_id="meta-llama/Llama-2-13b-chat-hf",
            datasets=datasets,
            tasks=tasks,
            config=config,
        )
        print(f"  13B cells: {list(chat_13b.keys())}")
    except Exception as e:
        with open(config.errors_log, "a") as f:
            f.write(f"13B inference failed: {e}\n{traceback.format_exc()}\n")
        print(f"✗ 13B inference failed: {e}")
        print("  Continuing with empty 13B results (will affect cross-size validation only)")
        chat_13b = {}

    # Step 3: 7B pair conditional ΔΔECE
    print("\n[Step 3] Computing conditional ΔΔECE (7B pair)...")
    anli_results_7b, advglue_results_7b, anli_rate_7b, advglue_rate_7b = \
        compute_moderation_by_benchmark_type(
            base_7b, chat_7b,
            config.anli_cells, config.advglue_cells,
            config.ddece_threshold,
        )
    print(f"  ANLI moderation rate (7B): {anli_rate_7b:.4f}")
    print(f"  AdvGLUE moderation rate (7B): {advglue_rate_7b:.4f}")

    # Step 4: 13B cross-size ΔΔECE (ANLI only)
    print("\n[Step 4] Computing cross-size ΔΔECE (13B pair, ANLI)...")
    if chat_13b:
        anli_results_13b, anli_rate_13b = compute_cross_size_moderation(
            base_7b, chat_13b, config.anli_cells, config.ddece_threshold
        )
    else:
        anli_results_13b, anli_rate_13b = [], 0.0
    print(f"  ANLI moderation rate (13B): {anli_rate_13b:.4f}")

    # Step 5: Primary gate
    print("\n[Step 5] Evaluating primary gate...")
    gate_passed, gate_report = evaluate_gate(anli_rate_7b, config.moderation_rate_threshold)
    print(f"  Gate: {'PASS' if gate_passed else 'FAIL'} (rate={anli_rate_7b:.4f}, threshold={config.moderation_rate_threshold})")

    # Step 6: Save results
    print("\n[Step 6] Saving results...")
    results = summarize_results(
        (anli_results_7b, advglue_results_7b, anli_rate_7b, advglue_rate_7b),
        (anli_results_13b, anli_rate_13b),
    )
    results["gate"] = gate_report
    results["hypothesis_id"] = "h-c1-v2"
    results["timestamp"] = datetime.now().isoformat()
    write_json(config.results_file, results)
    print(f"  Results saved: {config.results_file}")
    write_validation_report(results, gate_passed, config)

    # Step 7: Generate figures
    print("\n[Step 7] Generating figures...")
    try:
        fig1_ddece_bar(anli_results_7b, advglue_results_7b, "7B pair",
                       os.path.join(config.figures_dir, "ddece_comparison_bar_7b.png"))
        if anli_results_13b:
            fig1_ddece_bar(anli_results_13b, [], "13B pair",
                           os.path.join(config.figures_dir, "ddece_comparison_bar_13b.png"))
        fig2_reliability_diagrams(base_7b, chat_7b,
                                   ["NLI-ANLI-R3", "NLI-AdvGLUE"],
                                   os.path.join(config.figures_dir, "reliability_diagram.png"))
        fig3_confidence_histogram(base_7b, chat_7b, "NLI-ANLI-R1",
                                   os.path.join(config.figures_dir, "confidence_distribution_adv.png"))
        all_model_results = {**cache}
        if chat_13b:
            all_model_results["meta-llama/Llama-2-13b-chat-hf"] = chat_13b
        fig4_moderation_heatmap(
            all_model_results,
            row_models=config.models,
            col_cells=config.anli_cells + config.advglue_cells,
            out_path=os.path.join(config.figures_dir, "moderation_heatmap.png"),
        )
        fig5_ddece_vs_difficulty(anli_results_7b, "7B pair",
                                  os.path.join(config.figures_dir, "ddece_vs_difficulty.png"))
        print("  ✓ All figures generated")
    except Exception as e:
        print(f"  ⚠ Figure generation error (non-fatal): {e}")
        traceback.print_exc()

    print("\n" + "="*60)
    print(f"COMPLETE — Gate: {'PASS' if gate_passed else 'FAIL'}")
    print("="*60)
    return gate_passed


if __name__ == "__main__":
    import sys
    gate = main(HC1V2Config())
    sys.exit(0 if gate else 1)
