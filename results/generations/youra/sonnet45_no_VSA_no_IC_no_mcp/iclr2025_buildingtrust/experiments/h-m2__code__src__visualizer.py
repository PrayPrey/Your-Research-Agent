"""
Visualization module for h-m2 results.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
import os

def plot_gate_metrics(gpt_results: Dict, llama_results: Dict, save_dir: str):
    """
    Gate metrics comparison: Target vs actual metrics bar chart.

    Mandatory figure showing matched vs mismatched success rates with gate threshold.
    """
    models = ["GPT-3.5", "Llama-2-7B"]
    matched_rates = [gpt_results["matched_rate"] * 100, llama_results["matched_rate"] * 100]
    mismatched_rates = [gpt_results["mismatched_rate"] * 100, llama_results["mismatched_rate"] * 100]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, matched_rates, width, label='Matched (RAG)', color='green', alpha=0.7)
    ax.bar(x + width/2, mismatched_rates, width, label='Mismatched (COT)', color='red', alpha=0.7)

    # Gate threshold line (20pp difference)
    ax.axhline(y=20.0, color='black', linestyle='--', linewidth=2, label='Gate Threshold (20pp diff)')

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('h-m2: Gate Metrics Comparison - Matched vs Mismatched Routing', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    os.makedirs(save_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "gate_metrics_comparison.png"), dpi=150)
    plt.close()

def plot_success_comparison(gpt_results: Dict, llama_results: Dict, save_dir: str):
    """
    Success rate comparison bar chart.
    """
    conditions = ["Matched\n(RAG)", "Mismatched\n(COT)"]
    gpt_rates = [gpt_results["matched_rate"] * 100, gpt_results["mismatched_rate"] * 100]
    llama_rates = [llama_results["matched_rate"] * 100, llama_results["mismatched_rate"] * 100]

    x = np.arange(len(conditions))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, gpt_rates, width, label='GPT-3.5', color='blue', alpha=0.7)
    ax.bar(x + width/2, llama_rates, width, label='Llama-2-7B', color='orange', alpha=0.7)

    ax.set_xlabel('Routing Condition', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Success Rate Comparison: Matched vs Mismatched Routing', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(conditions)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    os.makedirs(save_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "success_rate_comparison.png"), dpi=150)
    plt.close()

def plot_per_model_breakdown(gpt_results: Dict, llama_results: Dict, save_dir: str):
    """
    Per-model breakdown grouped bar chart.
    """
    models = ["GPT-3.5", "Llama-2-7B"]
    matched_rates = [gpt_results["matched_rate"] * 100, llama_results["matched_rate"] * 100]
    mismatched_rates = [gpt_results["mismatched_rate"] * 100, llama_results["mismatched_rate"] * 100]
    differences = [gpt_results["difference"] * 100, llama_results["difference"] * 100]

    x = np.arange(len(models))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, matched_rates, width, label='Matched (RAG)', color='green', alpha=0.7)
    ax.bar(x, mismatched_rates, width, label='Mismatched (COT)', color='red', alpha=0.7)
    ax.bar(x + width, differences, width, label='Difference (pp)', color='purple', alpha=0.7)

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Rate / Difference (pp)', fontsize=12)
    ax.set_title('Per-Model Breakdown: Success Rates and Differences', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    os.makedirs(save_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "per_model_breakdown.png"), dpi=150)
    plt.close()

def plot_outcome_distribution(all_results: Dict, save_dir: str):
    """
    Distribution of correction outcomes histogram.
    """
    # Count successes and failures per condition
    gpt_matched_success = sum(1 for r in all_results["gpt_matched"] if r.get("success", 0) == 1.0)
    gpt_matched_failure = len(all_results["gpt_matched"]) - gpt_matched_success
    gpt_mismatched_success = sum(1 for r in all_results["gpt_mismatched"] if r.get("success", 0) == 1.0)
    gpt_mismatched_failure = len(all_results["gpt_mismatched"]) - gpt_mismatched_success

    llama_matched_success = sum(1 for r in all_results["llama_matched"] if r.get("success", 0) == 1.0)
    llama_matched_failure = len(all_results["llama_matched"]) - llama_matched_success
    llama_mismatched_success = sum(1 for r in all_results["llama_mismatched"] if r.get("success", 0) == 1.0)
    llama_mismatched_failure = len(all_results["llama_mismatched"]) - llama_mismatched_success

    conditions = ["GPT-3.5\nMatched", "GPT-3.5\nMismatched", "Llama-2-7B\nMatched", "Llama-2-7B\nMismatched"]
    successes = [gpt_matched_success, gpt_mismatched_success, llama_matched_success, llama_mismatched_success]
    failures = [gpt_matched_failure, gpt_mismatched_failure, llama_matched_failure, llama_mismatched_failure]

    x = np.arange(len(conditions))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, successes, width, label='Success', color='green', alpha=0.7)
    ax.bar(x + width/2, failures, width, label='Failure', color='red', alpha=0.7)

    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Correction Outcomes', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    os.makedirs(save_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "correction_outcomes.png"), dpi=150)
    plt.close()
