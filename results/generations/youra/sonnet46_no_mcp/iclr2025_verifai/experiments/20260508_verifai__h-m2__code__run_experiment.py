"""
h-m2 Experiment: mypy/ast Feedback Repair — Mechanistic Complementarity with SynCode
Gate: SHOULD_WORK
"""
import ast
import json
import logging
import os
import sys
from typing import Dict, List, Set, Tuple

# h-m1 code path is injected at runtime via cfg.h_m1_code_dir
# (sys.path.insert done in setup_paths)

from config import (
    H2ExperimentConfig,
    MypyRepairConfig,
    CScoreConfig,
    Z3DeltaConfig,
    H2VisualizationConfig,
)
from mypy_feedback_repair import MypyFeedbackRepair
from c_score_calculator import CScoreCalculator
from z3_eligibility_delta import Z3EligibilityDelta
from visualization_h2 import H2Visualizer


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(log_path: str) -> None:
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path),
        ],
    )


def setup_paths(cfg: H2ExperimentConfig) -> None:
    # h-m1 inserted AFTER h-m2 (already on path via direct import), so h-m1 h-m1 config.py doesn't shadow h-m2 config
    if cfg.h_m1_code_dir and cfg.h_m1_code_dir not in sys.path:
        sys.path.append(cfg.h_m1_code_dir)


def setup_directories(cfg: H2ExperimentConfig) -> None:
    for d in [cfg.output.data_dir, cfg.output.results_dir, cfg.output.figures_dir]:
        os.makedirs(d, exist_ok=True)


def load_jsonl(path: str) -> Dict[str, List[dict]]:
    pool: Dict[str, List[dict]] = {}
    if not os.path.exists(path):
        return pool
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                pool.setdefault(rec["task_id"], []).append(rec)
            except (json.JSONDecodeError, KeyError):
                pass
    return pool


def compute_pass_at_1(pool: Dict[str, List[dict]]) -> Dict[str, float]:
    rates = {}
    for task_id, records in pool.items():
        if not records:
            rates[task_id] = 0.0
            continue
        # pass@1 = fraction of samples that pass
        passed = sum(1 for r in records if r.get("success", False) or r.get("ast_valid", False))
        rates[task_id] = passed / len(records)
    return rates


def extract_f_syncode_pass_at_1(
    baseline_pool: Dict[str, List[dict]],
    syncode_pool: Dict[str, List[dict]],
    baseline_pass_rates: Dict[str, float],
    syncode_pass_rates: Dict[str, float],
) -> Set[str]:
    f_syncode = set()
    for task_id in syncode_pool:
        if task_id not in baseline_pool:
            continue
        b_rate = baseline_pass_rates.get(task_id, 0.0)
        s_rate = syncode_pass_rates.get(task_id, 0.0)
        if b_rate == 0.0 and s_rate > 0.0:
            f_syncode.add(task_id)
    return f_syncode


def extend_syncode_pool(
    cfg: H2ExperimentConfig,
    problems: Dict,
    generator,
) -> Dict[str, List[dict]]:
    from syncode_generator import ExtendedSyncodeGenerator  # type: ignore[import]
    h_m1_pool = {}
    if cfg.h_m1_syncode_pool and os.path.exists(cfg.h_m1_syncode_pool):
        h_m1_pool = load_jsonl(cfg.h_m1_syncode_pool)
        logger.info(f"Loaded h-m1 SynCode pool: {len(h_m1_pool)} problems")

    out_path = os.path.join(cfg.output.data_dir, cfg.output.syncode_pool_file)
    progress_path = os.path.join(cfg.output.data_dir, cfg.output.progress_syncode_file)
    existing = load_jsonl(out_path)

    with open(out_path, "a") as f:
        for task_id, records in h_m1_pool.items():
            if task_id not in existing:
                for rec in records:
                    f.write(json.dumps(rec) + "\n")
                existing[task_id] = records

    completed = set(existing.keys())
    remaining = {t: p for t, p in problems.items() if t not in completed}
    logger.info(f"SynCode: {len(completed)} done, {len(remaining)} remaining")

    if remaining:
        new_pool = generator.generate_pool(remaining, out_path, progress_path)
        existing.update(new_pool)
    return existing


# ─────────────────────────────────────────────────────────────────────────────
# Phase Functions
# ─────────────────────────────────────────────────────────────────────────────

def run_phase_baseline_pool(
    cfg: H2ExperimentConfig, problems: Dict, dry_run: bool = False
) -> Dict[str, List[dict]]:
    from baseline_generator import ExtendedBaselineGenerator  # type: ignore[import]
    logger.info("=== Phase 1: Baseline Pool Generation ===")
    out_path = os.path.join(cfg.output.data_dir, cfg.output.baseline_pool_file)
    progress_path = os.path.join(cfg.output.data_dir, cfg.output.progress_baseline_file)

    if dry_run:
        problems = dict(list(problems.items())[:cfg.integration.dry_run_n_problems])

    gen = ExtendedBaselineGenerator(
        model_name="codellama/CodeLlama-7b-hf",
        temperature=0.8,
        max_new_tokens=512,
        n_samples=20,
    )
    h_e1_pool_path = cfg.h_e1_baseline_pool if cfg.baseline_pool.reuse_h_e1_pool else None

    existing = load_jsonl(out_path)
    if len(existing) >= len(problems):
        logger.info(f"Baseline pool already complete: {len(existing)} problems")
        return existing

    gen.load_model()

    # Wrap _generate_single with SIGALRM-based timeout (works on main thread, kills GPU op)
    import signal
    _orig_generate = gen._generate_single

    def _generate_single_with_timeout(prompt: str, seed: int, timeout: int = 90) -> str:
        def _handler(signum, frame):
            raise TimeoutError(f"_generate_single exceeded {timeout}s (seed={seed})")
        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(timeout)
        try:
            result = _orig_generate(prompt, seed)
            signal.alarm(0)
            return result
        except TimeoutError:
            signal.alarm(0)
            logger.warning(f"_generate_single timed out after {timeout}s (seed={seed}), skipping sample")
            return ""
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)

    gen._generate_single = _generate_single_with_timeout  # type: ignore[method-assign]

    pool = gen.generate_pool(problems, out_path, progress_path, h_e1_pool_path=h_e1_pool_path)
    logger.info(f"Baseline pool: {len(pool)} problems, {sum(len(v) for v in pool.values())} samples")
    return pool


def run_phase_fmd_classification(
    cfg: H2ExperimentConfig,
    baseline_pool: Dict[str, List[dict]],
    problems: Dict,
) -> Dict[str, List[str]]:
    from fmd_classifier import FMDClassifier  # type: ignore[import]
    logger.info("=== Phase 2: FMD Classification ===")
    out_path = os.path.join(cfg.output.data_dir, cfg.output.fmd_classification_file)

    if os.path.exists(out_path):
        logger.info("FMD classification already exists, loading...")
        fmd_results: Dict[str, List[str]] = {}
        with open(out_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    fmd_results.setdefault(rec["task_id"], []).append(rec["stratum"])
        return fmd_results

    classifier = FMDClassifier(mypy_timeout=cfg.fmd.cross_validate_n)
    pool_by_task = {t: [{"completion": r["completion"]} for r in recs] for t, recs in baseline_pool.items()}
    pool_fmt = {t: recs for t, recs in baseline_pool.items()}

    fmd_raw = classifier.classify_pool(pool_fmt, problems)
    fmd_classifications: Dict[str, List[str]] = {}
    with open(out_path, "w") as f:
        for task_id, labels in fmd_raw.items():
            fmd_classifications[task_id] = labels
            for i, lbl in enumerate(labels):
                f.write(json.dumps({"task_id": task_id, "sample_idx": i, "stratum": lbl}) + "\n")

    stratum_counts: Dict[str, int] = {}
    for labels in fmd_classifications.values():
        for lbl in labels:
            stratum_counts[lbl] = stratum_counts.get(lbl, 0) + 1
    logger.info(f"FMD counts: {stratum_counts}")
    type_problems = sum(1 for lbls in fmd_classifications.values() if any(l == "type" for l in lbls))
    logger.info(f"type_structural stratum: {type_problems} problems")
    if type_problems < 10:
        logger.warning(f"WARNING: type_structural stratum only {type_problems} problems (< 10 threshold)")
    return fmd_classifications


def run_phase_mypy_repair(
    cfg: H2ExperimentConfig,
    baseline_pool: Dict[str, List[dict]],
    problems: Dict,
    dry_run: bool = False,
) -> Dict[str, List[dict]]:
    logger.info("=== Phase 3: mypy/ast Iterative Feedback Repair ===")
    out_path = os.path.join(cfg.output.data_dir, cfg.output.mypy_repair_pool_file)
    progress_path = os.path.join(cfg.output.data_dir, cfg.output.progress_repair_file)

    existing = load_jsonl(out_path)
    repair_problems = problems if not dry_run else dict(list(problems.items())[:cfg.integration.dry_run_n_problems])

    if len(existing) >= len(repair_problems):
        logger.info(f"Repair pool already complete: {len(existing)} problems")
        mar = MypyFeedbackRepair(cfg.mypy_repair).compute_mechanism_activated_rate(existing)
        logger.info(f"mechanism_activated_rate: {mar:.3f}")
        return existing

    repair = MypyFeedbackRepair(cfg.mypy_repair)
    repair.load_model()
    pool = repair.repair_pool(baseline_pool, repair_problems, out_path, progress_path)
    mar = repair.compute_mechanism_activated_rate(pool)
    logger.info(f"Repair complete. mechanism_activated_rate: {mar:.3f}")
    if mar < cfg.mypy_repair.mechanism_activated_threshold:
        logger.warning(f"mechanism_activated_rate {mar:.3f} < threshold {cfg.mypy_repair.mechanism_activated_threshold}")
    return pool


def run_phase_syncode_pool(
    cfg: H2ExperimentConfig,
    problems: Dict,
    baseline_pool: Dict[str, List[dict]],
    dry_run: bool = False,
) -> Dict[str, List[dict]]:
    from syncode_generator import ExtendedSyncodeGenerator  # type: ignore[import]
    logger.info("=== Phase 4: SynCode Pool Extension ===")

    gen = ExtendedSyncodeGenerator(
        model_name="codellama/CodeLlama-7b-hf",
        grammar="python",
        mode="grammar_mask",
        temperature=0.8,
        max_new_tokens=512,
        n_samples=20,
    )

    if not dry_run:
        syncode_pool = extend_syncode_pool(cfg, problems, gen)
    else:
        dry_probs = dict(list(problems.items())[:cfg.integration.dry_run_n_problems])
        syncode_pool = extend_syncode_pool(cfg, dry_probs, gen)
    logger.info(f"SynCode pool: {len(syncode_pool)} problems")
    return syncode_pool


def run_phase_extract_transitions(
    cfg: H2ExperimentConfig,
    baseline_pool: Dict[str, List[dict]],
    syncode_pool: Dict[str, List[dict]],
    repair_pool: Dict[str, List[dict]],
    fmd_classifications: Dict[str, List[str]],
    problems: Dict,
) -> Tuple[Set[str], Set[str], Set[str]]:
    logger.info("=== Phase 5: Transition Set Extraction ===")
    baseline_pass_rates = compute_pass_at_1(baseline_pool)
    syncode_pass_rates = compute_pass_at_1(syncode_pool)

    f_syncode = extract_f_syncode_pass_at_1(
        baseline_pool, syncode_pool, baseline_pass_rates, syncode_pass_rates
    )
    logger.info(f"F_SynCode→✓: {len(f_syncode)} problems")

    f_syncode_path = os.path.join(cfg.output.data_dir, cfg.output.f_syncode_transitions_file)
    with open(f_syncode_path, "w") as f:
        json.dump({"f_syncode": sorted(f_syncode), "n_transitions": len(f_syncode),
                   "n_problems": len(syncode_pool)}, f, indent=2)

    # F_mypy→✓: problems where baseline pass@1=0 AND post-mypy success > 0
    mypy_eligible: Set[str] = set()
    f_mypy: Set[str] = set()
    for task_id, records in repair_pool.items():
        has_mypy_error = any(r.get("rounds_used", 0) > 0 for r in records)
        if has_mypy_error:
            mypy_eligible.add(task_id)
        b_rate = baseline_pass_rates.get(task_id, 0.0)
        repair_pass_rate = sum(1 for r in records if r.get("success", False)) / len(records) if records else 0.0
        if b_rate == 0.0 and repair_pass_rate > 0.0:
            f_mypy.add(task_id)

    logger.info(f"F_mypy→✓: {len(f_mypy)} problems, mypy_eligible: {len(mypy_eligible)}")

    repair_success_rate = len(f_mypy) / len(mypy_eligible) if mypy_eligible else 0.0
    mar = MypyFeedbackRepair(cfg.mypy_repair).compute_mechanism_activated_rate(repair_pool)

    f_mypy_path = os.path.join(cfg.output.data_dir, cfg.output.f_mypy_transitions_file)
    with open(f_mypy_path, "w") as f:
        json.dump({
            "f_mypy": sorted(f_mypy),
            "n_transitions": len(f_mypy),
            "repair_success_rate": repair_success_rate,
            "mechanism_activated_rate": mar,
        }, f, indent=2)

    if len(f_mypy) == 0:
        logger.warning("PoC pre-condition FAIL: F_mypy→✓ is empty")

    return f_syncode, f_mypy, mypy_eligible


def run_phase_c_score(
    cfg: H2ExperimentConfig,
    f_syncode: Set[str],
    f_mypy: Set[str],
    fmd_classifications: Dict[str, List[str]],
    mypy_eligible: Set[str],
    baseline_pool: Dict[str, List[dict]],
) -> Dict:
    logger.info("=== Phase 6: C_score Computation ===")
    calc = CScoreCalculator(cfg.c_score)

    baseline_pass_rates = compute_pass_at_1(baseline_pool)
    all_problems = list(fmd_classifications.keys())

    # Eligibility-conditioned stratum
    conditioned_stratum = calc.define_eligibility_conditioned_stratum(fmd_classifications, mypy_eligible)
    logger.info(f"Conditioned stratum size: {len(conditioned_stratum)}")
    if len(conditioned_stratum) < cfg.c_score.min_stratum_size:
        logger.warning(f"Stratum too small ({len(conditioned_stratum)} < {cfg.c_score.min_stratum_size})")

    conditioned_result = calc.compute_c_score(f_syncode, f_mypy, conditioned_stratum)
    conditioned_ci = calc.bootstrap_c_score_ci(f_syncode, f_mypy, conditioned_stratum)
    raw_result = calc.compute_c_score(f_syncode, f_mypy, all_problems)
    quintiles = calc.compute_difficulty_quintiles(all_problems, baseline_pass_rates)
    quintile_results = calc.compute_c_score_by_quintile(f_syncode, f_mypy, quintiles)

    logger.info(f"C_score (conditioned): {conditioned_result['c_score']:.4f}")
    logger.info(f"Bootstrap CI: [{conditioned_ci['ci_lower']:.4f}, {conditioned_ci['ci_upper']:.4f}]")
    logger.info(f"p_value: {conditioned_ci['p_value']:.4f}")

    out_path = os.path.join(cfg.output.results_dir, cfg.output.c_score_results_file)
    results = calc.save_results(conditioned_result, conditioned_ci, raw_result, quintile_results, out_path)
    return results


def run_phase_z3_delta(
    cfg: H2ExperimentConfig,
    baseline_pool: Dict[str, List[dict]],
    repair_pool: Dict[str, List[dict]],
) -> Dict:
    logger.info("=== Phase 7: Z3 Eligibility Delta ===")
    z3 = Z3EligibilityDelta(cfg.z3_delta)

    baseline_eligible = z3.compute_eligibility_rate(baseline_pool)
    post_mypy_eligible = z3.compute_eligibility_rate(repair_pool)

    n_base = sum(1 for v in baseline_eligible.values() if v)
    n_post = sum(1 for v in post_mypy_eligible.values() if v)
    logger.info(f"Z3 eligible: baseline={n_base}, post-mypy={n_post}")

    delta_p, ci_lower, ci_upper, p_value = z3.compute_delta_p(baseline_eligible, post_mypy_eligible)
    logger.info(f"ΔP={delta_p:.4f}, CI=[{ci_lower:.4f}, {ci_upper:.4f}], p={p_value:.4f}")

    out_path = os.path.join(cfg.output.results_dir, cfg.output.z3_eligibility_delta_file)
    results = z3.save_results(delta_p, ci_lower, ci_upper, p_value, out_path,
                               baseline_eligible, post_mypy_eligible)
    return results


def run_phase_visualization(
    cfg: H2ExperimentConfig,
    c_score_results: Dict,
    z3_results: Dict,
    fmd_classifications: Dict,
    repair_pool: Dict,
) -> List[str]:
    logger.info("=== Phase 8: Visualization ===")
    viz = H2Visualizer(cfg.visualization, cfg.output.figures_dir)
    figures = viz.generate_all(c_score_results, z3_results, fmd_classifications, repair_pool)
    logger.info(f"Generated {len(figures)} figures")
    return figures


def evaluate_gate(c_score_results: Dict, z3_results: Dict) -> str:
    c_score = c_score_results.get("c_score", 0.0)
    p_value = c_score_results.get("bootstrap_p_value", 1.0)
    ci_lower = c_score_results.get("ci_lower", 0.0)
    delta_p = z3_results.get("delta_p", 0.0)
    z3_ci_lower = z3_results.get("ci_lower", 0.0)

    if c_score <= 0:
        logger.warning("NULL RESULT: methods address same failure subset (C_score <= 0)")
        return "FAIL"
    if c_score > 0 and p_value < 0.0167 and ci_lower > 0 and delta_p > 0.05 and z3_ci_lower > 0:
        return "PASS"
    # C_score > 0 but not fully significant
    return "PARTIAL"


def save_metrics(
    cfg: H2ExperimentConfig,
    c_score_results: Dict,
    z3_results: Dict,
    fmd_classifications: Dict,
    repair_pool: Dict,
    gate_result: str,
) -> None:
    mar = MypyFeedbackRepair(cfg.mypy_repair).compute_mechanism_activated_rate(repair_pool)
    stratum_counts: Dict[str, int] = {}
    for labels in fmd_classifications.values():
        for lbl in labels:
            stratum_counts[lbl] = stratum_counts.get(lbl, 0) + 1

    metrics = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_result": gate_result,
        "n_problems": 164,
        "primary_metric": {
            "c_score": c_score_results.get("c_score"),
            "j_obs": c_score_results.get("j_obs"),
            "e_j": c_score_results.get("e_j"),
            "bootstrap_p_value": c_score_results.get("bootstrap_p_value"),
            "ci_lower": c_score_results.get("ci_lower"),
            "ci_upper": c_score_results.get("ci_upper"),
            "stratum_size": c_score_results.get("stratum_size"),
        },
        "secondary_metric": {
            "delta_p_z3": z3_results.get("delta_p"),
            "ci_lower": z3_results.get("ci_lower"),
            "ci_upper": z3_results.get("ci_upper"),
            "p_baseline": z3_results.get("p_baseline"),
            "p_post_mypy": z3_results.get("p_post_mypy"),
        },
        "fmd_stats": stratum_counts,
        "repair_stats": {
            "mechanism_activated_rate": mar,
        },
    }
    if gate_result == "FAIL":
        metrics["null_result_note"] = "NULL RESULT: methods address same failure subset (C_score <= 0)"

    out_path = os.path.join(cfg.output.results_dir, cfg.output.metrics_file)
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved to {out_path}")
    logger.info(f"Gate result: {gate_result}")


def validate_outputs(cfg: H2ExperimentConfig) -> bool:
    ok = True
    for fname in cfg.integration.required_output_files:
        if fname.endswith(".json"):
            path = os.path.join(cfg.output.results_dir, fname)
        else:
            path = os.path.join(cfg.output.data_dir, fname)
        exists = os.path.exists(path)
        logger.info(f"  {'✓' if exists else '✗'} {fname}")
        if not exists:
            ok = False
    return ok


def main(cfg: H2ExperimentConfig, dry_run: bool = False) -> None:
    setup_paths(cfg)
    setup_directories(cfg)

    # Import h-m1 modules after sys.path patch
    from evalplus.data import get_human_eval_plus  # type: ignore[import]
    problems = get_human_eval_plus()
    logger.info(f"Loaded {len(problems)} HumanEval+ problems")

    if dry_run:
        logger.info(f"DRY RUN: limiting to {cfg.integration.dry_run_n_problems} problems")

    # Phase 1: Baseline pool
    baseline_pool = run_phase_baseline_pool(cfg, problems, dry_run=dry_run)

    # Phase 2: FMD classification
    fmd_classifications = run_phase_fmd_classification(cfg, baseline_pool, problems)

    # Phase 3: mypy repair
    repair_pool = run_phase_mypy_repair(cfg, baseline_pool, problems, dry_run=dry_run)

    # Phase 4: SynCode pool extension
    syncode_pool = run_phase_syncode_pool(cfg, problems, baseline_pool, dry_run=dry_run)

    # Phase 5: Extract transitions
    f_syncode, f_mypy, mypy_eligible = run_phase_extract_transitions(
        cfg, baseline_pool, syncode_pool, repair_pool, fmd_classifications, problems
    )

    # Phase 6: C_score
    c_score_results = run_phase_c_score(
        cfg, f_syncode, f_mypy, fmd_classifications, mypy_eligible, baseline_pool
    )

    # Phase 7: Z3 eligibility delta
    z3_results = run_phase_z3_delta(cfg, baseline_pool, repair_pool)

    # Phase 8: Visualization
    figures = run_phase_visualization(cfg, c_score_results, z3_results, fmd_classifications, repair_pool)

    # Gate evaluation
    gate_result = evaluate_gate(c_score_results, z3_results)

    # Save metrics
    save_metrics(cfg, c_score_results, z3_results, fmd_classifications, repair_pool, gate_result)

    # Validate outputs
    logger.info("Output validation:")
    all_ok = validate_outputs(cfg)

    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate: SHOULD_WORK → {gate_result}")
    logger.info(f"C_score: {c_score_results.get('c_score', 'N/A'):.4f}")
    logger.info(f"ΔP(Z3): {z3_results.get('delta_p', 'N/A'):.4f}")
    logger.info(f"Figures generated: {len(figures)}")
    logger.info(f"Output validation: {'PASS' if all_ok else 'PARTIAL'}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="h-m2 Experiment")
    parser.add_argument("--dry-run", action="store_true", help="Run on 5 problems only")
    parser.add_argument("--h-m1-code-dir", required=True, help="Path to h-m1/code/")
    parser.add_argument("--h-e1-baseline-pool", default="", help="Path to h-e1 baseline pool")
    parser.add_argument("--h-m1-baseline-pool", default="", help="Path to h-m1 baseline pool")
    parser.add_argument("--h-m1-syncode-pool", default="", help="Path to h-m1 syncode pool")
    parser.add_argument("--data-dir", default="", help="Override data output dir")
    parser.add_argument("--results-dir", default="", help="Override results output dir")
    parser.add_argument("--figures-dir", default="", help="Override figures output dir")
    args = parser.parse_args()

    cfg = H2ExperimentConfig(
        h_m1_code_dir=args.h_m1_code_dir,
        h_e1_baseline_pool=args.h_e1_baseline_pool,
        h_m1_baseline_pool=args.h_m1_baseline_pool,
        h_m1_syncode_pool=args.h_m1_syncode_pool,
    )
    if args.data_dir:
        cfg.output.data_dir = args.data_dir
    if args.results_dir:
        cfg.output.results_dir = args.results_dir
    if args.figures_dir:
        cfg.output.figures_dir = args.figures_dir
    if args.dry_run:
        cfg.integration.dry_run = True

    setup_logging(os.path.join(os.path.dirname(args.data_dir or "h-m2/code"), "experiment.log"))
    main(cfg, dry_run=args.dry_run)
