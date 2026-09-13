"""H-M2 Experiment Orchestrator: 12-step pipeline for corpus entropy → logit margin."""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import HM2Config, ALL_CONFIGS, load_config

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


def step_01_validate_prerequisites(cfg: HM2Config) -> Dict:
    """Step 1: Validate prerequisites (h-e1 corpora, conda env, GPU)."""
    logger.info("=== Step 01: Validate Prerequisites ===")
    he1_dir = Path(cfg.he1_data_dir)
    issues = []

    for config_id in ["C0", "C1", "C2", "C3", "C4", "C5", "C6"]:
        corpus = he1_dir / f"{config_id}.jsonl"
        if not corpus.exists():
            issues.append(f"Missing corpus: {corpus}")

    if issues:
        for iss in issues:
            logger.error(f"[step01] {iss}")
        return {"status": "failed", "issues": issues}

    logger.info(f"[step01] All h-e1 corpora found in {he1_dir}")
    return {"status": "success"}


def step_02_generate_c7(cfg: HM2Config) -> Dict:
    """Step 2: Generate C7 shuffled-demographic negative control."""
    logger.info("=== Step 02: Generate C7 Corpus ===")
    from data_prep import generate_c7_corpus
    c3_path = str(Path(cfg.he1_data_dir) / "C3.jsonl")
    c7_path = str(Path(cfg.he1_data_dir) / "C7.jsonl")

    if Path(c7_path).exists():
        logger.info(f"[step02] C7 already exists: {c7_path}")
    else:
        generate_c7_corpus(c3_path, c7_path, seed=cfg.seed)

    return {"status": "success", "c7_path": c7_path}


def step_03_tokenize_corpora(cfg: HM2Config, quick: bool = True) -> Dict:
    """Step 3: Tokenize all 8 corpora (C0-C7)."""
    logger.info("=== Step 03: Tokenize Corpora ===")
    from data_prep import tokenize_corpus
    he1_dir = Path(cfg.he1_data_dir)
    tokenized_dir = Path(cfg.tokenized_dir)
    tokenized = []
    skipped = []

    for config_id in ALL_CONFIGS:
        corpus_path = str(he1_dir / f"{config_id}.jsonl")
        if not Path(corpus_path).exists():
            logger.warning(f"[step03] {config_id}.jsonl not found — skipping")
            skipped.append(config_id)
            continue
        out_dir = str(tokenized_dir / f"config_{config_id}")
        bin_path = Path(out_dir) / "text_document.bin"
        if bin_path.exists():
            logger.info(f"[step03] {config_id} already tokenized")
            tokenized.append(config_id)
            continue
        tokenize_corpus(corpus_path, out_dir)
        tokenized.append(config_id)

    return {"status": "success", "tokenized": tokenized, "skipped": skipped}


def step_04_generate_yaml_configs(cfg: HM2Config, quick: bool = True) -> Dict:
    """Step 4: Generate gpt-neox YAML configs for all 8 corpus configs."""
    logger.info("=== Step 04: Generate gpt-neox YAML Configs ===")
    from data_prep import build_all_yaml_configs
    build_all_yaml_configs(cfg, quick=quick)
    return {"status": "success", "configs_dir": cfg.configs_dir}


def step_05_train_models(
    cfg: HM2Config,
    configs: Optional[List[str]] = None,
    gpu_id: int = 1,
    dry_run: bool = False,
) -> Dict:
    """Step 5: Train Pythia-1B on each corpus config sequentially."""
    logger.info("=== Step 05: Train Models ===")
    from train import train_all_configs
    results = train_all_configs(
        cfg=cfg,
        configs=configs,
        gpu_id=gpu_id,
        dry_run=dry_run,
    )
    n_success = sum(1 for r in results.values() if r.get("status") == "success")
    return {"status": "success", "train_results": results, "n_success": n_success}


def step_06_probe_models(
    cfg: HM2Config,
    configs: Optional[List[str]] = None,
    gpu_id: int = 1,
) -> Dict:
    """Step 6: Run logit margin probe on all trained models."""
    logger.info("=== Step 06: Probe Models ===")
    from probe import run_all_configs
    probe_results = run_all_configs(cfg, configs=configs, gpu_id=gpu_id)
    return {"status": "success", "probe_results": probe_results}


def step_07_run_statistical_tests(
    cfg: HM2Config,
    probe_results: Dict,
) -> Dict:
    """Step 7: Run Spearman gate, OLS, and negative control tests."""
    logger.info("=== Step 07: Statistical Tests ===")
    from statistical_tests import StatisticalTests
    tester = StatisticalTests(
        n_bootstrap=cfg.n_bootstrap,
        seed=cfg.seed,
        alpha_level=cfg.alpha_level,
        negative_control_threshold=cfg.negative_control_delta_threshold,
    )
    stat_results = tester.run_all_tests(probe_results)
    return {"status": "success", "stat_results": stat_results}


def step_08_generate_visualizations(
    cfg: HM2Config,
    probe_results: Dict,
    stat_results: Dict,
    training_results: Optional[Dict] = None,
) -> Dict:
    """Step 8: Generate 5 analysis figures."""
    logger.info("=== Step 08: Generate Visualizations ===")
    from visualize import Visualizer
    viz = Visualizer(cfg)
    figure_paths = viz.generate_all_figures(probe_results, stat_results, training_results)
    return {"status": "success", "figure_paths": figure_paths}


def step_09_evaluate_gate(stat_results: Dict) -> Dict:
    """Step 9: Evaluate SHOULD_WORK gate."""
    logger.info("=== Step 09: Evaluate Gate ===")
    gate = stat_results.get("gate", {})
    gate_pass = gate.get("gate_pass", False)
    rho = gate.get("rho", 0)
    pvalue = gate.get("pvalue", 1)
    reason = gate.get("reason", "unknown")
    verdict = "PASS" if gate_pass else "FAIL_EXPLORE"
    logger.info(f"[step09] Gate verdict: {verdict} (rho={rho:.4f}, p={pvalue:.4f})")
    logger.info(f"[step09] Reason: {reason}")
    return {"gate_pass": gate_pass, "verdict": verdict, "rho": rho, "pvalue": pvalue, "reason": reason}


def step_10_collect_results(
    cfg: HM2Config,
    probe_results: Dict,
    stat_results: Dict,
    gate_result: Dict,
    figure_paths: Dict,
) -> Dict:
    """Step 10: Serialize all results to JSON."""
    logger.info("=== Step 10: Collect Results ===")
    results = {
        "hypothesis_id": "h-m2",
        "timestamp": datetime.utcnow().isoformat(),
        "gate_verdict": gate_result["verdict"],
        "gate_pass": gate_result["gate_pass"],
        "spearman_rho": gate_result["rho"],
        "spearman_pvalue": gate_result["pvalue"],
        "probe_results": {
            k: {kk: vv for kk, vv in v.items() if kk != "margins"}
            for k, v in probe_results.items()
        },
        "statistical_tests": stat_results,
        "figure_paths": figure_paths,
    }
    results_path = Path(cfg.results_path)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"[step10] Results saved: {results_path}")
    return results


def step_11_generate_validation_report(
    cfg: HM2Config,
    results: Dict,
    stat_results: Dict,
    gate_result: Dict,
) -> str:
    """Step 11: Generate 04_validation.md report."""
    logger.info("=== Step 11: Generate Validation Report ===")
    from report import generate_validation_report
    report_path = generate_validation_report(cfg, results, stat_results, gate_result)
    return report_path


def step_12_finalize(cfg: HM2Config, results: Dict) -> None:
    """Step 12: Log completion summary."""
    logger.info("=== Step 12: Finalize ===")
    gate_verdict = results.get("gate_verdict", "unknown")
    rho = results.get("spearman_rho", 0)
    pvalue = results.get("spearman_pvalue", 1)
    logger.info(f"[step12] H-M2 experiment COMPLETE")
    logger.info(f"[step12] Gate: {gate_verdict}")
    logger.info(f"[step12] Spearman ρ={rho:.4f}, p={pvalue:.6f}")
    logger.info(f"[step12] Results: {cfg.results_path}")
    logger.info(f"[step12] Report: {cfg.validation_path}")


def run_experiment(
    cfg: HM2Config,
    gpu_id: int = 1,
    quick: bool = True,
    dry_run: bool = False,
    configs: Optional[List[str]] = None,
) -> Dict:
    """Run the full H-M2 12-step experiment pipeline."""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("H-M2 EXPERIMENT PIPELINE START")
    logger.info(f"Quick run: {quick}, GPU: {gpu_id}, Dry run: {dry_run}")
    logger.info("=" * 60)

    # Set GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    # File logger
    log_path = Path(cfg.results_dir) / "experiment.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(str(log_path))
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(file_handler)

    # Execute steps
    r1 = step_01_validate_prerequisites(cfg)
    if r1["status"] == "failed":
        return {"status": "failed", "step": 1, "details": r1}

    r2 = step_02_generate_c7(cfg)
    r3 = step_03_tokenize_corpora(cfg, quick=quick)
    r4 = step_04_generate_yaml_configs(cfg, quick=quick)

    if not dry_run:
        r5 = step_05_train_models(cfg, configs=configs, gpu_id=gpu_id, dry_run=dry_run)
        training_results = r5.get("train_results", {})
    else:
        logger.info("[run] DRY RUN: Skipping training")
        training_results = {}

    r6 = step_06_probe_models(cfg, configs=configs, gpu_id=gpu_id)
    probe_results = r6["probe_results"]

    r7 = step_07_run_statistical_tests(cfg, probe_results)
    stat_results = r7["stat_results"]

    r8 = step_08_generate_visualizations(cfg, probe_results, stat_results, training_results)
    figure_paths = r8["figure_paths"]

    gate_result = step_09_evaluate_gate(stat_results)

    results = step_10_collect_results(
        cfg, probe_results, stat_results, gate_result, figure_paths
    )

    try:
        step_11_generate_validation_report(cfg, results, stat_results, gate_result)
    except Exception as e:
        logger.warning(f"[step11] Report generation failed: {e}")

    step_12_finalize(cfg, results)

    elapsed = time.time() - start_time
    logger.info(f"Total experiment time: {elapsed:.1f}s")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M2 Experiment Pipeline")
    parser.add_argument("--config", type=str, default=None, help="YAML config override")
    parser.add_argument("--gpu", type=int, default=1, help="GPU ID")
    parser.add_argument("--quick", action="store_true", help="50B token quick run")
    parser.add_argument("--dry-run", action="store_true", help="Skip training")
    parser.add_argument("--configs", nargs="+", default=None, help="Specific config IDs")
    args = parser.parse_args()

    cfg = load_config(args.config)
    results = run_experiment(
        cfg=cfg,
        gpu_id=args.gpu,
        quick=args.quick,
        dry_run=args.dry_run,
        configs=args.configs,
    )
    gate = results.get("gate_verdict", "unknown")
    print(f"\nGate verdict: {gate}")
    sys.exit(0 if results.get("gate_pass") else 1)
