"""
run_experiment.py — H-E1 main pipeline driver.

Usage:
  python run_experiment.py              # full run (10M docs)
  python run_experiment.py --quick      # quick test (50k docs)
  python run_experiment.py --output-dir /path/to/out
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# No GPU needed for this corpus-statistics experiment
os.environ["CUDA_VISIBLE_DEVICES"] = ""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_experiment")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def setup_directories(data_dir: str, figures_dir: str) -> None:
    """Ensure all required directories exist."""
    for subdir in ["corpora", "scores", "models"]:
        Path(data_dir, subdir).mkdir(parents=True, exist_ok=True)
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Directories ready.")


def verify_mechanism_activated(
    config_entropies: Dict[str, float],
    results: Dict[str, Any],
    gate_threshold_pct: float = 5.0,
) -> Dict[str, Any]:
    """Check H-E1 mechanism activation criteria.

    Pass criteria:
    - >= 6 configurations have been processed
    - Entropies vary across configurations (std > 0)
    - Gate has passed (from StatisticalTests)
    """
    import numpy as np

    n_configs = len(config_entropies)
    values = list(config_entropies.values())
    entropies_differ = float(np.std(values)) > 0 if len(values) > 1 else False
    gate_passed = results.get("gate_passed", False)

    check = {
        "n_configs_processed": n_configs,
        "entropies_differ": entropies_differ,
        "gate_passed": gate_passed,
        "mechanism_activated": n_configs >= 6 and entropies_differ and gate_passed,
    }
    return check


def write_results_json(results: Dict[str, Any], path: str) -> None:
    """Serialise results dict to JSON."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info("Results written to %s", path)


def write_validation_md(
    results: Dict[str, Any],
    mechanism_check: Dict[str, Any],
    path: str,
) -> None:
    """Write 04_validation.md with gate result."""
    gate_passed = mechanism_check.get("gate_passed", False)
    gate_emoji = "PASS" if gate_passed else "FAIL"
    entropies = results.get("entropies", {})
    rel_change = results.get("relative_change_pct", 0.0)
    threshold = results.get("gate_threshold_pct", 5.0)
    spearman = results.get("spearman", {})
    ci = results.get("bootstrap_ci", {})

    lines = [
        "# H-E1 Validation Report",
        "",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "---",
        "",
        "## Gate Result",
        "",
        f"**Gate Status: {gate_emoji}**",
        "",
        f"- Relative entropy change C1→C5: `{rel_change:.2f}%`",
        f"- Gate threshold: `{threshold:.1f}%`",
        f"- Configs processed: `{mechanism_check.get('n_configs_processed', 0)}`",
        f"- Entropies differ: `{mechanism_check.get('entropies_differ', False)}`",
        "",
        "---",
        "",
        "## Entropy Values H(Demographic | Occupation)",
        "",
        "| Config | Filter | Entropy (bits) |",
        "|--------|--------|----------------|",
    ]
    config_meta = {
        "C0": "unfiltered",
        "C1": "fasttext ≥10%",
        "C2": "fasttext ≥30%",
        "C3": "fasttext ≥50%",
        "C4": "fasttext ≥70%",
        "C5": "fasttext ≥90%",
        "C6": "DoReMi",
    }
    for cid in ["C0", "C1", "C2", "C3", "C4", "C5", "C6"]:
        h = entropies.get(cid, "N/A")
        h_str = f"{h:.4f}" if isinstance(h, float) else str(h)
        lines.append(f"| {cid} | {config_meta.get(cid, '')} | {h_str} |")

    lines += [
        "",
        "---",
        "",
        "## Statistical Tests",
        "",
    ]
    if spearman:
        lines.append(f"**Spearman ρ:** `{spearman.get('rho', 'N/A'):.4f}`  "
                     f"(p = `{spearman.get('pvalue', 'N/A'):.4e}`)")
        lines.append("")
    if ci:
        lines.append(f"**Bootstrap 95% CI for H(C5)−H(C1):** "
                     f"[`{ci.get('low', 'N/A'):.4f}`, `{ci.get('high', 'N/A'):.4f}`]")
        lines.append("")

    lines += [
        "---",
        "",
        "## Mechanism Check",
        "",
        f"- Mechanism activated: **{mechanism_check.get('mechanism_activated', False)}**",
        "",
    ]

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("Validation report written to %s", path)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="H-E1 corpus statistical analysis")
    p.add_argument("--quick", action="store_true",
                   help="Use 50,000 docs for quick testing")
    p.add_argument("--output-dir", default=None,
                   help="Override base output directory (data/figures)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Import config
    sys.path.insert(0, str(Path(__file__).parent))
    from config import CONFIG
    from corpus_filter import CorpusFilter
    from entropy_measure import EntropyMeasure
    from statistical_tests import StatisticalTests
    from visualize import Visualizer

    # Override paths if requested
    data_dir = CONFIG["data_dir"]
    figures_dir = CONFIG["figures_dir"]
    results_path = CONFIG["results_path"]
    validation_path = CONFIG["validation_path"]

    if args.output_dir:
        base = Path(args.output_dir)
        data_dir = str(base / "data")
        figures_dir = str(base / "figures")
        results_path = str(base / "results.json")
        validation_path = str(base / "04_validation.md")

    n_docs = 50_000 if args.quick else CONFIG["n_docs"]
    logger.info("H-E1 pipeline starting | n_docs=%d | quick=%s", n_docs, args.quick)

    # Step 1: Setup directories
    setup_directories(data_dir, figures_dir)

    # Step 2: Build corpora
    cf = CorpusFilter(
        fasttext_model_path=CONFIG["fasttext_model_path"],
        seed=CONFIG["seed"],
    )
    corpus_paths = cf.build_all_corpora(
        data_dir=data_dir,
        dataset_id=CONFIG["dataset_id"],
        n_docs=n_docs,
        configurations=CONFIG["configurations"],
    )

    # Load corpora into memory for entropy computation
    corpora: Dict[str, list] = {}
    for cid in corpus_paths:
        corpora[cid] = cf.load_corpus(cid, data_dir)

    # Step 3: Compute entropies
    em = EntropyMeasure(
        occ_lexicon=CONFIG["occupation_lexicon"],
        demo_lexicon=CONFIG["demographic_lexicon"],
        window_size=CONFIG["window_size"],
    )
    entropies = em.compute_all_entropies(corpora)
    joint_counts = getattr(em, "joint_counts_per_config", {})

    # Step 4: Statistical tests
    st = StatisticalTests(n_bootstrap=CONFIG["n_bootstrap"])
    stats_results = st.run_all_tests(
        entropies=entropies,
        joint_counts_per_config=joint_counts,
        gate_threshold_pct=CONFIG["gate_threshold_pct"],
    )
    stats_results["entropies"] = entropies

    # Step 5: Visualizations
    viz = Visualizer(figures_dir=figures_dir)
    figure_paths = viz.generate_all(entropies, joint_counts, stats_results)
    stats_results["figure_paths"] = figure_paths

    # Step 6: Verify mechanism
    mechanism_check = verify_mechanism_activated(
        entropies, stats_results, CONFIG["gate_threshold_pct"]
    )
    stats_results["mechanism_check"] = mechanism_check

    # Step 7: Write outputs
    write_results_json(stats_results, results_path)
    write_validation_md(stats_results, mechanism_check, validation_path)

    # Step 8: Report
    gate_status = "PASS" if mechanism_check.get("gate_passed", False) else "FAIL"
    print(f"\n{'='*60}")
    print(f"H-E1 Gate Result: {gate_status}")
    print(f"Relative entropy change C1→C5: {stats_results.get('relative_change_pct', 0):.2f}%")
    print(f"Gate threshold: {CONFIG['gate_threshold_pct']}%")
    print(f"Configs processed: {mechanism_check.get('n_configs_processed', 0)}")
    print(f"Figures: {len(figure_paths)} files generated")
    print(f"Results: {results_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
