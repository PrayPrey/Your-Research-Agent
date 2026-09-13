"""
H-M1 Experiment Runner: Conditional Log-Odds Demographic-Occupation Analysis.

15-step pipeline:
  1. parse_args
  2. load_config
  3. setup_h1_imports
  4. mkdir data/figures dirs
  5. load_corpora (C1-C6)
  6. get_he1_lexicons
  7. LogOddsComputer
  8. compute_all_configs
  9. aggregate_mean_log_odds
 10. run_all_tests
 11. generate_all visualizations
 12. verify_mechanism_activated
 13. save_log_odds_matrix
 14. write_results_json
 15. write_validation_md
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# ---- Path bootstrap -------------------------------------------------------
CODE_DIR = str(Path(__file__).parent)
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

# Defer h-e1 import to after config is loaded
# ---------------------------------------------------------------------------


def setup_h1_imports(he1_code_dir: str) -> None:
    """Add h-e1/code to sys.path so CorpusFilter and CONFIG are importable."""
    if he1_code_dir not in sys.path:
        sys.path.insert(0, he1_code_dir)


def load_corpora(config) -> Dict[str, List[dict]]:
    """
    Load C1-C6 corpora from h-e1/data/corpora/*.jsonl.

    If any corpus is missing, build all corpora via CorpusFilter.build_all_corpora().
    """
    from corpus_filter import CorpusFilter  # type: ignore

    data_dir = config.he1_data_dir
    corpora_dir = Path(data_dir) / "corpora"
    config_ids = config.all_configs  # ["C1", ..., "C6"]

    cf = CorpusFilter(fasttext_model_path=config.fasttext_model_path, seed=42)

    # Check which corpora exist
    missing = [cid for cid in config_ids if not (corpora_dir / f"{cid}.jsonl").exists()]

    if missing:
        logger.info("Missing corpora: %s — building all corpora", missing)
        n_docs = getattr(config, "_n_docs", 10_000_000)
        # build_all_corpora calls `from config import CONFIG` — temporarily remove h-m1
        # code dir from sys.path so h-e1's config.py is found instead
        hm1_code_dir = CODE_DIR
        removed = False
        if hm1_code_dir in sys.path:
            sys.path.remove(hm1_code_dir)
            removed = True
        # Also remove cached h-m1 config module so h-e1's is freshly imported
        sys.modules.pop("config", None)
        try:
            cf.build_all_corpora(data_dir=data_dir, n_docs=n_docs)
        finally:
            # Restore h-m1 code dir
            if removed:
                sys.path.insert(0, hm1_code_dir)
            sys.modules.pop("config", None)  # Clear h-e1's config from cache

    # Load all corpora
    corpora = {}
    for cid in config_ids:
        try:
            docs = cf.load_corpus(config_id=cid, data_dir=data_dir)
            corpora[cid] = docs
            logger.info("Loaded %d docs for %s", len(docs), cid)
        except Exception as e:
            logger.error("Failed to load corpus %s: %s", cid, e)
            corpora[cid] = []

    return corpora


def verify_mechanism_activated(
    log_odds_df,
    stats_results: Dict[str, Any],
) -> Dict[str, bool]:
    """
    Verify that the H-M1 mechanism was activated.

    Returns dict with keys:
        log_odds_computed, shape_valid, variation_exists,
        spearman_computed, mechanism_activated
    """
    import pandas as pd

    log_odds_computed = log_odds_df is not None and not log_odds_df.empty
    shape_valid = log_odds_computed and log_odds_df["config_id"].nunique() == 6

    variation_exists = False
    if log_odds_computed:
        finite_vals = log_odds_df["log_odds"].replace([float("inf"), float("-inf")], float("nan")).dropna()
        variation_exists = finite_vals.std() > 0 if len(finite_vals) > 1 else False

    spearman_computed = (
        "spearman" in stats_results
        and "rho" in stats_results.get("spearman", {})
        and not (stats_results["spearman"].get("rho") != stats_results["spearman"].get("rho"))  # not NaN
    )

    mechanism_activated = (
        log_odds_computed
        and shape_valid
        and variation_exists
        and spearman_computed
        and stats_results.get("gate", {}).get("gate_passed", False)
    )

    return {
        "log_odds_computed": log_odds_computed,
        "shape_valid": shape_valid,
        "variation_exists": variation_exists,
        "spearman_computed": spearman_computed,
        "mechanism_activated": mechanism_activated,
    }


def _json_serializable(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types."""
    if isinstance(obj, dict):
        return {k: _json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_serializable(v) for v in obj]
    if isinstance(obj, tuple):
        return [_json_serializable(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, float) and (obj != obj):  # NaN
        return None
    if obj == float("inf"):
        return None
    if obj == float("-inf"):
        return None
    return obj


def write_results_json(results: Dict[str, Any], path: str) -> None:
    """Write results to JSON, handling numpy types."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    serializable = _json_serializable(results)
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
    logger.info("Saved results to %s", path)


def write_validation_md(
    results: Dict[str, Any],
    mechanism_check: Dict[str, bool],
    path: str,
) -> None:
    """Write markdown validation report."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    gate = results.get("gate", {}) if isinstance(results.get("gate"), dict) else {}
    gate_passed = gate.get("gate_passed", results.get("gate_passed", False))
    rho = gate.get("rho", results.get("spearman_rho", float("nan")))
    pvalue = gate.get("pvalue", results.get("spearman_pvalue", float("nan")))
    ci = results.get("bootstrap_ci", (float("nan"), float("nan")))
    mean_lo = results.get("mean_log_odds_per_config", {})

    lines = [
        "# H-M1 Validation Report",
        "",
        "## Gate Result",
        "",
        f"**Gate Passed:** {'YES' if gate_passed else 'NO'}",
        "",
        "## Key Statistics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Spearman ρ | {rho:.4f} |",
        f"| p-value | {pvalue:.4f} |",
        f"| Bootstrap 95% CI | [{ci[0]:.4f}, {ci[1]:.4f}] |",
        "",
        "## Mean Log-Odds per Config",
        "",
        "| Config | Mean Log-Odds |",
        "|--------|---------------|",
    ]
    for cid, val in sorted(mean_lo.items()):
        lines.append(f"| {cid} | {val:.4f} |")

    lines += [
        "",
        "## Mechanism Verification",
        "",
        "| Check | Result |",
        "|-------|--------|",
    ]
    for k, v in mechanism_check.items():
        lines.append(f"| {k} | {'✓' if v else '✗'} |")

    lines += [
        "",
        f"## Conclusion",
        "",
        f"H-M1 mechanism {'activated' if mechanism_check.get('mechanism_activated') else 'NOT activated'}.",
        f"Conditional log-odds demographic-occupation analysis complete.",
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("Saved validation report to %s", path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="H-M1: Conditional Log-Odds Analysis")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: use 50k docs instead of full corpus",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory for results/figures",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config override file",
    )
    return parser.parse_args()


# Module-level logger — will be reconfigured in main()
logger = logging.getLogger(__name__)


def main() -> None:
    """15-step H-M1 experiment pipeline."""
    # Step 1: parse_args
    args = parse_args()

    # Step 2: load_config
    from config import load_config, get_he1_lexicons, HM1Config  # type: ignore

    config = load_config(args.config)

    if args.output_dir:
        out = Path(args.output_dir)
        config.data_dir = str(out / "data")
        config.figures_dir = str(out / "figures")
        config.results_path = str(out / "results.json")
        config.validation_path = str(out / "04_validation.md")
        config.log_odds_matrix_path = str(out / "data" / "log_odds_matrix.csv")

    if args.quick:
        config._n_docs = 50_000
    else:
        config._n_docs = 10_000_000

    # Step 3: setup_h1_imports
    setup_h1_imports(config.he1_code_dir)

    # Configure logging
    log_file = str(Path(config.data_dir).parent / "code" / "experiment.log")
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )
    global logger
    logger = logging.getLogger(__name__)
    logger.info("H-M1 experiment started (quick=%s)", args.quick)

    # Step 4: mkdir
    Path(config.data_dir).mkdir(parents=True, exist_ok=True)
    Path(config.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(config.log_odds_matrix_path).parent.mkdir(parents=True, exist_ok=True)

    # Step 5: load_corpora
    logger.info("Step 5: Loading corpora C1-C6")
    corpora = load_corpora(config)

    # Step 6: get_he1_lexicons
    logger.info("Step 6: Loading lexicons from H-E1")
    lexicons = get_he1_lexicons()
    occ_lexicon = lexicons["occupation_lexicon"]
    demo_lexicon = lexicons["demographic_lexicon"]
    logger.info("Lexicons: %d occupations, %d demographics", len(occ_lexicon), len(demo_lexicon))

    # Step 7: LogOddsComputer
    logger.info("Step 7: Initializing LogOddsComputer")
    from log_odds import LogOddsComputer  # type: ignore

    computer = LogOddsComputer(
        occ_lexicon=occ_lexicon,
        demo_lexicon=demo_lexicon,
        window_size=10,
        alpha=0.5,
    )

    # Step 8: compute_all_configs
    logger.info("Step 8: Computing log-odds for all configs")
    log_odds_df = computer.compute_all_configs(corpora)
    logger.info("Log-odds DataFrame shape: %s", log_odds_df.shape)

    # Step 9: aggregate_mean_log_odds
    logger.info("Step 9: Aggregating mean log-odds per config")
    mean_log_odds = computer.aggregate_mean_log_odds(log_odds_df)
    logger.info("Mean log-odds per config: %s", mean_log_odds)

    # Step 10: run_all_tests
    logger.info("Step 10: Running statistical tests")
    from statistical_tests import StatisticalTests  # type: ignore

    stats = StatisticalTests(n_bootstrap=config.n_bootstrap, seed=config.seed).run_all_tests(
        log_odds_df, mean_log_odds, config.filtering_intensities
    )
    logger.info("Gate result: %s", stats.get("gate", {}))

    # Step 11: generate_all visualizations
    logger.info("Step 11: Generating visualizations")
    from visualize import Visualizer  # type: ignore

    Visualizer(config.figures_dir, dpi=config.dpi).generate_all(log_odds_df, mean_log_odds, stats)

    # Step 12: verify_mechanism_activated
    logger.info("Step 12: Verifying mechanism activation")
    mechanism_check = verify_mechanism_activated(log_odds_df, stats)
    logger.info("Mechanism check: %s", mechanism_check)

    # Step 13: save_log_odds_matrix
    logger.info("Step 13: Saving log-odds matrix CSV")
    computer.save_log_odds_matrix(log_odds_df, config.log_odds_matrix_path)

    # Step 14: write_results_json
    logger.info("Step 14: Writing results JSON")
    gate_info = stats.get("gate", {})
    bootstrap_ci = stats.get("bootstrap_ci", (None, None))
    results_dict = {
        "hypothesis_id": "H-M1",
        "gate_passed": gate_info.get("gate_passed", False),
        "gate_type": "spearman_rank_correlation",
        "spearman_rho": gate_info.get("rho", None),
        "spearman_pvalue": gate_info.get("pvalue", None),
        "bootstrap_ci": bootstrap_ci,
        "mean_log_odds_per_config": mean_log_odds,
        "mechanism_check": mechanism_check,
        "gate": gate_info,
    }
    write_results_json(results_dict, config.results_path)

    # Step 15: write_validation_md
    logger.info("Step 15: Writing validation markdown")
    write_validation_md(results_dict, mechanism_check, config.validation_path)

    logger.info(
        "H-M1 experiment complete. Gate: %s",
        "PASSED" if gate_info.get("gate_passed") else "FAILED",
    )


if __name__ == "__main__":
    main()
