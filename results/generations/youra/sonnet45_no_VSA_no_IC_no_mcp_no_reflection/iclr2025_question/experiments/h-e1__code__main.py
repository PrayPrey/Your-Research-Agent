#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path

from data import load_triviaqa_subset, prepare_example
from model import load_llama_model, forward_pass
from metrics import compute_entropy, compute_spearman, extraction_rate, quadrant_analysis
from visualization import plot_gate_metrics, plot_scatter, plot_histograms, plot_quadrant

def setup_logging(log_file, level="INFO"):
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config(config_path="config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_experiment(config):
    logging.info("Starting experiment: h-e1-entropy-correlation")

    logging.info("Loading dataset...")
    dataset = load_triviaqa_subset(split=config["dataset"]["split"])
    logging.info(f"Loaded {len(dataset)} examples")

    logging.info("Loading model...")
    model, tokenizer = load_llama_model(
        model_name=config["model"]["name"],
        device=config["model"]["device"]
    )
    logging.info(f"Model loaded on device: {model.device}")

    entropies = []
    correctness = []
    max_probs = []

    logging.info("Running inference loop...")
    for idx, example in enumerate(dataset):
        if idx % 100 == 0:
            logging.info(f"Processing example {idx}/{len(dataset)}")

        try:
            question, answer = prepare_example(example)
            result = forward_pass(model, tokenizer, question, max_length=config["model"]["max_input_length"])

            entropy = compute_entropy(result["logits"])
            max_prob = torch.max(F.softmax(result["logits"], dim=-1)).item()

            is_correct = int(result["pred_text"].strip().lower() == answer.strip().lower())

            if not np.isnan(entropy):
                entropies.append(entropy)
                correctness.append(is_correct)
                max_probs.append(max_prob)
        except Exception as e:
            logging.warning(f"Failed on example {idx}: {e}")
            continue

    logging.info(f"Collected {len(entropies)} valid predictions")

    logging.info("Computing metrics...")
    ext_rate = extraction_rate(entropies)
    correlation, p_value = compute_spearman(entropies, correctness)
    quad_results = quadrant_analysis(max_probs, entropies)

    logging.info(f"Extraction rate: {ext_rate:.4f}")
    logging.info(f"Spearman correlation: {correlation:.4f}, p-value: {p_value:.6f}")
    logging.info(f"Q3 fraction: {quad_results['q3_fraction']:.4f}")

    gate_pass = (
        ext_rate > config["gates"]["extraction_rate_threshold"] and
        p_value < config["gates"]["p_value_threshold"] and
        quad_results["q3_fraction"] > config["gates"]["q3_population_threshold"]
    )

    logging.info(f"Gate status: {'PASS' if gate_pass else 'FAIL'}")

    logging.info("Generating visualizations...")
    figures_dir = Path(config["output"]["figures_dir"])
    figures_dir.mkdir(parents=True, exist_ok=True)

    metrics_dict = {
        "extraction_rate": ext_rate,
        "p_value": p_value,
        "q3_fraction": quad_results["q3_fraction"]
    }

    plot_gate_metrics(metrics_dict, figures_dir / "gate_metrics.png")
    plot_scatter(entropies, correctness, figures_dir / "scatter.png")

    entropies_correct = [e for e, c in zip(entropies, correctness) if c == 1]
    entropies_incorrect = [e for e, c in zip(entropies, correctness) if c == 0]
    plot_histograms(entropies_correct, entropies_incorrect, figures_dir / "histograms.png")

    plot_quadrant(max_probs, entropies, correctness, figures_dir / "quadrant.png")

    logging.info("Generating validation report...")
    report_path = Path(config["output"]["validation_report"])
    generate_validation_report(report_path, config, metrics_dict, correlation, p_value,
                              quad_results, gate_pass, len(dataset), len(entropies))

    logging.info("Experiment complete")

    return {
        "extraction_rate": ext_rate,
        "correlation": correlation,
        "p_value": p_value,
        "q3_fraction": quad_results["q3_fraction"],
        "gate_pass": gate_pass
    }

def generate_validation_report(report_path, config, metrics, correlation, p_value, quad_results, gate_pass, total_examples, valid_examples):
    with open(report_path, 'w') as f:
        f.write("# Validation Report: h-e1\n")
        f.write("## Token Entropy Correlation with Prediction Correctness\n\n")
        f.write(f"**Date:** {config['experiment']['name']}\n")
        f.write(f"**Hypothesis ID:** {config['experiment']['hypothesis_id']}\n")
        f.write(f"**Gate Type:** {config['experiment']['gate']}\n\n")

        f.write("---\n\n")
        f.write("## Gate Validation Results\n\n")
        f.write(f"**Gate Status:** {'PASS ✓' if gate_pass else 'FAIL ✗'}\n\n")

        f.write("### Success Criteria\n\n")
        f.write("| Criterion | Threshold | Actual | Status |\n")
        f.write("|-----------|-----------|--------|--------|\n")
        f.write(f"| Extraction Rate | >0.95 | {metrics['extraction_rate']:.4f} | ")
        f.write("✓\n" if metrics['extraction_rate'] > 0.95 else "✗\n")
        f.write(f"| p-value | <0.05 | {p_value:.6f} | ")
        f.write("✓\n" if p_value < 0.05 else "✗\n")
        f.write(f"| Q3 Population | >0.05 | {quad_results['q3_fraction']:.4f} | ")
        f.write("✓\n" if quad_results['q3_fraction'] > 0.05 else "✗\n")

        f.write("\n---\n\n")
        f.write("## Statistical Analysis\n\n")
        f.write(f"- **Spearman Correlation:** ρ = {correlation:.4f}\n")
        f.write(f"- **p-value:** {p_value:.6f}\n")
        f.write(f"- **Sample Size:** {valid_examples} / {total_examples} examples\n")
        f.write(f"- **Extraction Rate:** {metrics['extraction_rate']:.2%}\n\n")

        f.write("---\n\n")
        f.write("## Quadrant Analysis\n\n")
        f.write(f"- **Median Max-Prob:** {quad_results['median_maxprob']:.4f}\n")
        f.write(f"- **Median Entropy:** {quad_results['median_entropy']:.4f}\n")
        f.write(f"- **Q3 Count:** {quad_results['q3_count']}\n")
        f.write(f"- **Q3 Fraction:** {quad_results['q3_fraction']:.2%}\n\n")

        f.write("---\n\n")
        f.write("## Visualizations\n\n")
        f.write("![Gate Metrics](./figures/gate_metrics.png)\n\n")
        f.write("![Scatter Plot](./figures/scatter.png)\n\n")
        f.write("![Histograms](./figures/histograms.png)\n\n")
        f.write("![Quadrant Analysis](./figures/quadrant.png)\n\n")

        f.write("---\n\n")
        f.write("## Conclusion\n\n")
        if gate_pass:
            f.write("Infrastructure validation PASSED. Entropy signals are extractable and show ")
            f.write("statistically significant correlation with prediction correctness. ")
            f.write("Proceed to next hypothesis.\n")
        else:
            f.write("Infrastructure validation FAILED. Gate criteria not met. ")
            f.write("ABANDON research per MUST_WORK gate condition.\n")

if __name__ == "__main__":
    config = load_config()
    setup_logging(config["logging"]["log_file"], config["logging"]["level"])

    try:
        results = run_experiment(config)
        sys.exit(0 if results["gate_pass"] else 1)
    except Exception as e:
        logging.error(f"Experiment failed: {e}", exc_info=True)
        sys.exit(2)
