"""H-M3 main orchestrator: 3 seeds × 2 datasets × 2 conditions × all problems."""

import json
import logging
import os
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_code_dir = str(pathlib.Path(__file__).parent)
_h_e1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code")
if _h_e1_path not in sys.path:
    sys.path.append(_h_e1_path)
if _code_dir not in sys.path:
    sys.path.insert(0, _code_dir)

from openai import OpenAI
from config import ExperimentConfig
from repair_loop import run_condition_a_h3, run_condition_b_h3, _make_key
from analysis import compute_summary
from visualize import generate_all_figures
from pipeline import load_problems


def _load_checkpoint(path: pathlib.Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"completed": {}, "results": []}


def _save_checkpoint(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def main() -> None:
    cfg = ExperimentConfig()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("OPENAI_API_KEY", "")
        except ImportError:
            pass
    if not api_key:
        logger.error("OPENAI_API_KEY not set.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    results_dir = pathlib.Path(cfg.results_dir)
    figures_dir = pathlib.Path(cfg.figures_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_path = pathlib.Path(cfg.checkpoint_path)
    ckpt = _load_checkpoint(checkpoint_path)
    completed = ckpt["completed"]
    results = ckpt["results"]

    logger.info(f"H-M3: datasets={cfg.datasets}, seeds={cfg.seeds}, k_max={cfg.k_max}")
    logger.info(f"Resuming: {len(completed)} completed, {len(results)} results loaded")

    # Outer loop: datasets × seeds × conditions × problems
    for dataset in cfg.datasets:
        logger.info(f"=== Dataset: {dataset} ===")
        problems = load_problems(dataset)
        task_ids = list(problems.keys())
        logger.info(f"  {len(task_ids)} problems")

        for seed in cfg.seeds:
            for condition in cfg.conditions:
                logger.info(f"  Seed={seed}, Condition={condition}")
                remaining = [
                    tid for tid in task_ids
                    if _make_key(dataset, seed, condition, tid) not in completed
                ]
                logger.info(f"  Remaining: {len(remaining)} problems")

                for i, tid in enumerate(remaining):
                    if i % 20 == 0:
                        logger.info(f"    [{condition}] {i}/{len(remaining)} (seed={seed})")
                    key = _make_key(dataset, seed, condition, tid)
                    try:
                        if condition == "A":
                            result = run_condition_a_h3(client, tid, problems[tid], seed, cfg.k_max)
                        else:
                            result = run_condition_b_h3(client, tid, problems[tid], seed, cfg.k_max)
                        result["dataset"] = dataset
                        results.append(result)
                        completed[key] = True
                        ckpt["completed"] = completed
                        ckpt["results"] = results
                        _save_checkpoint(checkpoint_path, ckpt)
                    except Exception as e:
                        logger.error(f"[Cond{condition}] Error on {tid} seed={seed}: {e}")

    logger.info(f"Collected {len(results)} total records")

    # Analysis per dataset
    summaries = {}
    for dataset in cfg.datasets:
        logger.info(f"=== Analysis: {dataset} ===")
        summary = compute_summary(results, dataset)
        summaries[dataset] = summary
        wt = summary["welch_test"]
        logger.info(f"  pass@1: A={wt['mean_pass_a']:.3f}, B={wt['mean_pass_b']:.3f}, "
                    f"delta={wt['absolute_improvement']:+.4f}")
        logger.info(f"  Welch: t={wt['t_stat']:.3f}, p={wt['p_value']:.4f}")
        logger.info(f"  Gate: {'PASS' if wt['gate_passed'] else 'FAIL'} "
                    f"(p<0.05 AND delta>=1%): p={wt['p_value']:.4f}, "
                    f"delta={wt['absolute_improvement']:+.4f}")
        logger.info(f"  Mechanism activated: {summary['mechanism_activated']}, "
                    f"mypy triggered: {summary['mypy_triggered_fraction']:.1%}")
        logger.info(f"  Context-length delta: {summary['confound']['mean_delta']:.1f} tokens per prompt")

    # Gate assertion
    assert summaries.get("mbpp+", {}).get("mechanism_activated", False), \
        "mechanism_activated == False: mypy never produced errors (MBPP+)"

    mbpp_gate = summaries.get("mbpp+", {}).get("gate_passed", False)
    he_gate = summaries.get("humaneval+", {}).get("gate_passed", False)
    gate_passed = mbpp_gate

    logger.info(f"=== GATE RESULT (MUST_WORK) ===")
    logger.info(f"MBPP+ gate: {'PASS' if mbpp_gate else 'FAIL'}")
    logger.info(f"HumanEval+ (secondary): {'PASS' if he_gate else 'FAIL'}")
    logger.info(f"Overall gate: {'PASS' if gate_passed else 'FAIL'}")

    # Save results
    for dataset in cfg.datasets:
        safe = dataset.replace("+", "plus")
        ds_results_a = [r for r in results if r.get("dataset") == dataset and r.get("condition") == "A"]
        ds_results_b = [r for r in results if r.get("dataset") == dataset and r.get("condition") == "B"]
        with open(results_dir / f"condition_a_{safe}.jsonl", "w") as f:
            for r in ds_results_a:
                f.write(json.dumps(r) + "\n")
        with open(results_dir / f"condition_b_{safe}.jsonl", "w") as f:
            for r in ds_results_b:
                f.write(json.dumps(r) + "\n")

    with open(results_dir / "analysis.json", "w") as f:
        # pass_a/pass_b are plain lists — JSON-serializable
        json.dump({d: {k: v for k, v in s.items() if k not in ("pass_a", "pass_b")}
                   for d, s in summaries.items()}, f, indent=2)

    mbpp_wt = summaries.get("mbpp+", {}).get("welch_test", {})
    he_wt = summaries.get("humaneval+", {}).get("welch_test", {})
    gate_result = {
        "gate_type": "MUST_WORK",
        "gate_passed": gate_passed,
        "primary_dataset": "mbpp+",
        "mbpp_plus": {
            "t_stat": mbpp_wt.get("t_stat"),
            "p_value": mbpp_wt.get("p_value"),
            "absolute_improvement": mbpp_wt.get("absolute_improvement"),
            "ci_95": mbpp_wt.get("ci_95"),
            "n": mbpp_wt.get("n"),
            "mean_pass_a": mbpp_wt.get("mean_pass_a"),
            "mean_pass_b": mbpp_wt.get("mean_pass_b"),
            "gate_passed": mbpp_gate,
        },
        "humaneval_plus": {
            "p_value": he_wt.get("p_value"),
            "absolute_improvement": he_wt.get("absolute_improvement"),
            "mean_pass_a": he_wt.get("mean_pass_a"),
            "mean_pass_b": he_wt.get("mean_pass_b"),
            "gate_passed": he_gate,
        },
        "mechanism_activated": summaries.get("mbpp+", {}).get("mechanism_activated"),
        "mypy_triggered_fraction": summaries.get("mbpp+", {}).get("mypy_triggered_fraction"),
        "context_length_delta_tokens": summaries.get("mbpp+", {}).get("confound", {}).get("mean_delta"),
    }
    with open(results_dir / "gate_result.json", "w") as f:
        json.dump(gate_result, f, indent=2)

    # Figures
    try:
        generate_all_figures(summaries, results, figures_dir)
        logger.info("Figures generated.")
    except Exception as e:
        logger.warning(f"Figure generation failed (non-fatal): {e}")

    logger.info(f"H-M3 complete. Gate (MUST_WORK): {'PASS' if gate_passed else 'FAIL'}")
    logger.info("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
