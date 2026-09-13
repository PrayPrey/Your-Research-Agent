import argparse
import json
import os
import sys
from typing import Dict, List

from evalplus.data import get_human_eval_plus


def get_paths(base_dir: str) -> dict:
    data_dir = os.path.join(base_dir, "data")
    results_dir = os.path.join(base_dir, "results")
    figures_dir = os.path.join(base_dir, "figures")
    h_e1_dir = os.path.join(os.path.dirname(base_dir), "h-e1", "data")
    return {
        "data_dir": data_dir,
        "results_dir": results_dir,
        "figures_dir": figures_dir,
        "baseline_pool": os.path.join(data_dir, "baseline_pool.jsonl"),
        "syncode_pool": os.path.join(data_dir, "syncode_pool.jsonl"),
        "progress_baseline": os.path.join(data_dir, "progress_baseline.json"),
        "progress_syncode": os.path.join(data_dir, "progress_syncode.json"),
        "h_e1_baseline": os.path.join(h_e1_dir, "baseline_pool.jsonl"),
        "ast_results": os.path.join(results_dir, "ast_failure_rates.json"),
        "bootstrap_results": os.path.join(results_dir, "bootstrap_ci.json"),
        "fmd_results": os.path.join(results_dir, "fmd_results.json"),
        "transitions": os.path.join(results_dir, "F_SynCode_success_transitions.json"),
        "mechanism_verification": os.path.join(results_dir, "mechanism_verification.json"),
        "metrics": os.path.join(results_dir, "metrics.json"),
    }


def load_pool_from_jsonl(path: str) -> Dict[str, List[dict]]:
    """Load JSONL pool with backward compatibility for h-e1 format (no ast_valid field)."""
    import ast as ast_module
    pool: Dict[str, List[dict]] = {}
    if not os.path.exists(path):
        return pool
    with open(path, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            task_id = rec["task_id"]
            # Backfill missing fields (h-e1 compat)
            if "ast_valid" not in rec:
                completion = rec.get("completion", "")
                try:
                    ast_module.parse(completion)
                    rec["ast_valid"] = True
                except SyntaxError:
                    rec["ast_valid"] = False
            if "sample_idx" not in rec:
                rec["sample_idx"] = None
            if "problem_idx" not in rec:
                rec["problem_idx"] = None
            pool.setdefault(task_id, []).append(rec)
    return pool


def main() -> int:
    parser = argparse.ArgumentParser(description="h-m1: SynCode Mechanism Experiment")
    parser.add_argument("--load_pools", action="store_true", help="Skip generation, load pools from disk")
    parser.add_argument("--skip_syncode", action="store_true", help="Baseline only (for testing)")
    parser.add_argument("--base_dir", default=None, help="Output root directory")
    parser.add_argument("--num_problems", type=int, default=164, help="Number of HumanEval problems")
    parser.add_argument("--skip_mechanism_check", action="store_true", help="Skip pre-verification")
    args = parser.parse_args()

    # Determine base_dir
    if args.base_dir is None:
        # Default: parent of code/ directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        args.base_dir = os.path.dirname(script_dir)

    paths = get_paths(args.base_dir)
    os.makedirs(paths["data_dir"], exist_ok=True)
    os.makedirs(paths["results_dir"], exist_ok=True)
    os.makedirs(paths["figures_dir"], exist_ok=True)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from baseline_generator import ExtendedBaselineGenerator
    from syncode_generator import ExtendedSyncodeGenerator
    from ast_metrics import ASTFailureRateComputer
    from bootstrap_ci import BootstrapCI
    from fmd_classifier import FMDClassifier
    from transition_extractor import TransitionExtractor
    from mechanism_verifier import MechanismVerifier
    from visualization import HM1Visualizer

    # Step 1: Load 164 HumanEval+ problems
    print("\n=== Step 1: Loading HumanEval+ problems ===")
    all_problems = get_human_eval_plus()
    task_ids_sorted = sorted(all_problems.keys())
    if args.num_problems < 164:
        task_ids_sorted = task_ids_sorted[:args.num_problems]
    problems = {k: all_problems[k] for k in task_ids_sorted}
    print(f"Loaded {len(problems)} problems")

    # Step 2: Generate/load baseline pool
    print("\n=== Step 2: Baseline Pool ===")
    if args.load_pools:
        baseline_pool = load_pool_from_jsonl(paths["baseline_pool"])
        print(f"Loaded baseline pool: {len(baseline_pool)} problems")
    else:
        bgen = ExtendedBaselineGenerator()
        bgen.load_model()
        h_e1_path = paths["h_e1_baseline"] if os.path.exists(paths["h_e1_baseline"]) else None
        baseline_pool = bgen.generate_pool(
            problems,
            paths["baseline_pool"],
            paths["progress_baseline"],
            h_e1_pool_path=h_e1_path,
        )

    # Step 3: Generate/load SynCode pool
    print("\n=== Step 3: SynCode Pool ===")
    syncode_pool = {}
    sgen = None
    if not args.skip_syncode:
        if args.load_pools:
            syncode_pool = load_pool_from_jsonl(paths["syncode_pool"])
            print(f"Loaded syncode pool: {len(syncode_pool)} problems")
        else:
            sgen = ExtendedSyncodeGenerator()
            sgen.load_model()
            syncode_pool = sgen.generate_pool(
                problems,
                paths["syncode_pool"],
                paths["progress_syncode"],
            )

    # Step 0: Mechanism pre-verification (after model load for efficiency)
    print("\n=== Step 0: Mechanism Verification ===")
    mech_result = {"grammar_lp_present": False, "constraint_active_rate": 0.0, "pre_check_passed": False}
    if not args.skip_mechanism_check and sgen is not None:
        verifier = MechanismVerifier()
        test_prompt = list(problems.values())[0].get("prompt", "def foo():\n    pass")
        mech_result = verifier.verify(sgen, test_prompt, paths["mechanism_verification"])
        if not mech_result["pre_check_passed"]:
            print(f"WARNING: Mechanism pre-check failed. Proceeding anyway.")
    else:
        # Save placeholder
        with open(paths["mechanism_verification"], "w") as f:
            json.dump(mech_result, f, indent=2)

    # Compute constraint_active_rate from pool
    constraint_active_rate = 0.0
    if sgen is not None and syncode_pool:
        constraint_active_rate = sgen.compute_constraint_active_rate(syncode_pool)
    elif syncode_pool:
        # Compute from loaded pool
        total = sum(len(v) for v in syncode_pool.values())
        active = sum(1 for v in syncode_pool.values() for r in v if r.get("constraint_active", False))
        constraint_active_rate = active / total if total > 0 else 0.0

    # Step 4: Compute AST failure rates
    print("\n=== Step 4: AST Failure Rate Computation ===")
    computer = ASTFailureRateComputer()
    if syncode_pool:
        baseline_rates, syncode_rates, ordered_task_ids = computer.compute_arrays(baseline_pool, syncode_pool)
    else:
        baseline_rates_dict = computer.compute_per_problem_rates(baseline_pool)
        ordered_task_ids = sorted(baseline_rates_dict.keys())
        import numpy as np
        baseline_rates = np.array([baseline_rates_dict[t] for t in ordered_task_ids])
        syncode_rates = baseline_rates.copy()  # No SynCode data

    ast_results = computer.save_results(baseline_rates, syncode_rates, ordered_task_ids, paths["ast_results"])
    delta_ast = ast_results["delta_ast"]
    print(f"delta_ast = {delta_ast:.4f}")

    # Step 5: Bootstrap CI
    print("\n=== Step 5: Bootstrap CI Statistical Test ===")
    ci = BootstrapCI(n_bootstrap=10000, alpha=0.05)
    delta_mean, ci_lower, ci_upper, p_value = ci.compute(baseline_rates, syncode_rates)
    gate_result = ci.evaluate_gate(delta_mean, ci_lower)
    bootstrap_results = ci.save_results(delta_mean, ci_lower, ci_upper, p_value, gate_result, paths["bootstrap_results"])
    print(f"Gate: {gate_result} | delta={delta_mean:.4f} | CI=[{ci_lower:.4f}, {ci_upper:.4f}] | p={p_value:.4f}")

    # Step 6: FMD Classification
    print("\n=== Step 6: FMD Classification ===")
    fmd = FMDClassifier()
    baseline_cls = fmd.classify_pool(baseline_pool, problems)
    baseline_dist = fmd.compute_distribution(baseline_cls)
    fmd_results_data = {"baseline_distribution": {k: baseline_dist.get(k, 0.0) for k in ["syntax", "type", "functional", "success"]}}

    if syncode_pool:
        syncode_cls = fmd.classify_pool(syncode_pool, problems)
        syncode_dist = fmd.compute_distribution(syncode_cls)
    else:
        syncode_dist = {k: 0.0 for k in ["syntax", "type", "functional", "success"]}

    syntax_shift = fmd.compute_syntax_shift(baseline_dist, syncode_dist)
    fmd_results_data = fmd.save_results(baseline_dist, syncode_dist, syntax_shift, paths["fmd_results"])
    print(f"Syntax shift: {syntax_shift:.4f}")

    # Step 7: Transition Extraction
    print("\n=== Step 7: Transition Extraction ===")
    transition_count = 0
    if syncode_pool:
        extractor = TransitionExtractor()
        transitions = extractor.extract(baseline_pool, syncode_pool)
        coverage = extractor.compute_coverage_by_problem(transitions)
        extractor.save_results(transitions, coverage, paths["transitions"])
        transition_count = len(transitions)
        print(f"Transitions (F_SynCode->success): {transition_count}")
    else:
        with open(paths["transitions"], "w") as f:
            json.dump({"transitions": [], "transition_count": 0, "transition_rate": 0.0, "coverage_by_problem": []}, f)

    # Step 8: Consolidated metrics
    print("\n=== Step 8: Writing metrics.json ===")
    metrics = {
        "gate_result": gate_result,
        "delta_ast": delta_ast,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": p_value,
        "constraint_active_rate": constraint_active_rate,
        "syntax_shift": syntax_shift,
        "transition_count": transition_count,
        "n_problems": len(problems),
    }
    with open(paths["metrics"], "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {paths['metrics']}")

    # Step 9: Figures
    print("\n=== Step 9: Generating Figures ===")
    viz = HM1Visualizer(paths["figures_dir"])
    if syncode_pool:
        viz.save_all(ast_results, bootstrap_results, fmd_results_data, baseline_pool, syncode_pool, baseline_rates, syncode_rates, ordered_task_ids)
    print("Figures saved.")

    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE")
    print(f"Gate Result: {gate_result}")
    print(f"delta_ast = {delta_ast:.4f}")
    print(f"{'='*60}")

    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
