#!/usr/bin/env python3
import json
import os
import sys
import logging
from datetime import datetime

from config import ExperimentConfig, set_seed, ensure_dirs, results_path
from data_loader import load_security_eval_prompts
from generator import CodeGenerator
from analyzers import BanditAnalyzer, PylintAnalyzer
from feedback_loop import IterationController
from evaluate import evaluate_condition, check_gate
from visualize import (
    plot_gate_metrics_comparison,
    plot_issue_reduction_over_iterations,
    plot_cwe_distribution
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def main():
    config = ExperimentConfig()
    logger.info(f"Starting H-M2 experiment with config: {config}")

    set_seed(config.seed)
    ensure_dirs(config)

    logger.info(f"Loading dataset: {config.dataset_id}")
    prompts = load_security_eval_prompts(config.dataset_id)
    logger.info(f"Loaded {len(prompts)} Python prompts")

    logger.info(f"Loading model: {config.model_id}")
    generator = CodeGenerator(config.model_id, config.device, config.seed)

    bandit = BanditAnalyzer()
    pylint = PylintAnalyzer()
    controller = IterationController(
        generator=generator,
        bandit=bandit,
        pylint=pylint,
        max_iterations=config.max_iterations,
        timeout_s=config.analysis_timeout_s
    )

    baseline_results = []
    loop_results = []

    logger.info("Starting baseline generation and feedback loop...")
    for i, prompt_data in enumerate(prompts):
        prompt_id = prompt_data["id"]
        prompt_text = prompt_data["prompt"]
        cwe = prompt_data["cwe"]

        logger.info(f"[{i+1}/{len(prompts)}] Processing {prompt_id} (CWE: {cwe})")

        initial_code = generator.generate(
            prompt_text,
            temperature=config.temperature,
            max_new_tokens=config.max_new_tokens
        )

        baseline_results.append({
            "id": prompt_id,
            "prompt": prompt_text,
            "cwe": cwe,
            "code": initial_code
        })

        result = controller.run(
            initial_code=initial_code,
            prompt=prompt_text,
            temperature=config.temperature,
            max_new_tokens=config.max_new_tokens
        )

        loop_results.append({
            "id": prompt_id,
            "cwe": cwe,
            "initial": result["initial"],
            "final": result["final"],
            "iterations": result["iterations"],
            "history": result["history"]
        })

        logger.info(
            f"  Security: {result['initial']['security_count']} -> {result['final']['security_count']}, "
            f"Reliability: {result['initial']['reliability_count']} -> {result['final']['reliability_count']}, "
            f"Iterations: {result['iterations']}"
        )

    logger.info("Saving baseline generations...")
    with open(results_path(config, "baseline_generations.jsonl"), "w") as f:
        for item in baseline_results:
            f.write(json.dumps(item) + "\n")

    logger.info("Saving loop results...")
    with open(results_path(config, "loop_results.jsonl"), "w") as f:
        for item in loop_results:
            f.write(json.dumps(item) + "\n")

    logger.info("Evaluating results...")
    agg = evaluate_condition(loop_results)
    gate_pass = check_gate(agg)

    evaluation = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_id": config.model_id,
            "dataset_id": config.dataset_id,
            "max_iterations": config.max_iterations,
            "temperature": config.temperature,
            "seed": config.seed
        },
        "results": agg,
        "gate": {
            "type": "SHOULD_WORK",
            "condition": "final_security < initial_security AND final_reliability < initial_reliability",
            "passed": gate_pass
        }
    }

    with open(results_path(config, "evaluation.json"), "w") as f:
        json.dump(evaluation, f, indent=2)

    logger.info("Generating visualizations...")

    total_initial = {
        "security": agg["total_initial_security"],
        "reliability": agg["total_initial_reliability"]
    }
    total_final = {
        "security": agg["total_final_security"],
        "reliability": agg["total_final_reliability"]
    }
    plot_gate_metrics_comparison(
        total_initial,
        total_final,
        os.path.join(config.figures_dir, "gate_metrics_comparison.png")
    )

    if loop_results:
        aggregated_history = []
        max_iters = max(len(r["history"]) for r in loop_results)
        for it in range(max_iters):
            sec_sum = 0
            rel_sum = 0
            count = 0
            for r in loop_results:
                if it < len(r["history"]):
                    sec_sum += r["history"][it]["security_count"]
                    rel_sum += r["history"][it]["reliability_count"]
                    count += 1
            if count > 0:
                aggregated_history.append({
                    "iteration": it,
                    "security_count": sec_sum,
                    "reliability_count": rel_sum
                })

        plot_issue_reduction_over_iterations(
            aggregated_history,
            os.path.join(config.figures_dir, "issue_reduction_over_iterations.png")
        )

    plot_cwe_distribution(
        prompts,
        os.path.join(config.figures_dir, "cwe_distribution.png")
    )

    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Samples processed: {agg['sample_count']}")
    logger.info(f"Mean security issue reduction: {agg['security_issue_reduction']:.2%}")
    logger.info(f"Mean reliability issue reduction: {agg['reliability_issue_reduction']:.2%}")
    logger.info(f"Mean iterations: {agg['mean_iterations']:.2f}")
    logger.info(f"Initial security (avg): {agg['initial_security']:.2f}")
    logger.info(f"Final security (avg): {agg['final_security']:.2f}")
    logger.info(f"Initial reliability (avg): {agg['initial_reliability']:.2f}")
    logger.info(f"Final reliability (avg): {agg['final_reliability']:.2f}")
    logger.info(f"GATE: {'PASS' if gate_pass else 'FAIL'}")
    logger.info("=" * 60)

    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
