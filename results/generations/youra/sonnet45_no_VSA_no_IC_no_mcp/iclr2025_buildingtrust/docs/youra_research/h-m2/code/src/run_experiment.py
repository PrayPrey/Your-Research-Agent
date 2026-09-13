"""
Main experiment runner for h-m2 correction routing.
"""

import json
import random
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from src.data_loader import DataLoader
from src.rag_pipeline import RAGPipeline
from src.cot_baseline import COTBaseline
from src.evaluator import Evaluator
from src.visualizer import (
    plot_gate_metrics,
    plot_success_comparison,
    plot_per_model_breakdown,
    plot_outcome_distribution
)

class CorrectionExperiment:
    """
    Correction routing experiment comparing matched (RAG) vs mismatched (COT) routing.
    """

    def __init__(self):
        self.config = CONFIG
        random.seed(self.config["seed"])

    def load_data(self) -> tuple:
        """Load entity-error cases from h-e1 outputs."""
        print("[1/5] Loading entity-error cases...")

        loader = DataLoader(
            h_e1_path=self.config["data"]["h_e1_results_path"],
            h_m1_path=self.config["data"]["h_m1_results_path"],
            threshold=self.config["data"]["h_m1_threshold"],
            use_synthetic=self.config["data"]["use_synthetic"],
            seed=self.config["seed"]
        )

        all_cases = loader.load_entity_error_cases()
        gpt_cases, llama_cases = loader.select_per_model_samples(
            all_cases,
            self.config["data"]["n_samples_per_model"]
        )

        print(f"  Loaded {len(gpt_cases)} GPT-3.5 cases, {len(llama_cases)} Llama-2-7B cases")
        return gpt_cases, llama_cases

    def run_corrections(self, gpt_cases: List[Dict], llama_cases: List[Dict]) -> Dict:
        """Run matched and mismatched corrections for both models."""
        print("[2/5] Running correction experiments...")

        # Initialize pipelines
        rag_gpt = RAGPipeline(
            "gpt-3.5-turbo",
            use_mock=self.config["rag"]["use_mock"],
            mock_success_rate=self.config["models"]["mock"]["entity_error_rag_success"],
            seed=self.config["seed"]
        )
        cot_gpt = COTBaseline(
            "gpt-3.5-turbo",
            use_mock=self.config["cot"]["use_mock"],
            mock_success_rate=self.config["models"]["mock"]["entity_error_cot_success"],
            seed=self.config["seed"] + 1  # Different seed for COT
        )

        rag_llama = RAGPipeline(
            "llama-2-7b",
            use_mock=self.config["rag"]["use_mock"],
            mock_success_rate=self.config["models"]["mock"]["entity_error_rag_success"],
            seed=self.config["seed"] + 2
        )
        cot_llama = COTBaseline(
            "llama-2-7b",
            use_mock=self.config["cot"]["use_mock"],
            mock_success_rate=self.config["models"]["mock"]["entity_error_cot_success"],
            seed=self.config["seed"] + 3
        )

        # Run GPT-3.5 corrections
        print("  Running GPT-3.5 matched (RAG)...")
        gpt_matched = []
        for case in gpt_cases:
            corrected = rag_gpt.correct(case["question"], case["incorrect_answer"])
            gpt_matched.append({**case, "corrected": corrected})

        print("  Running GPT-3.5 mismatched (COT)...")
        gpt_mismatched = []
        for case in gpt_cases:
            corrected = cot_gpt.correct(case["question"], case["incorrect_answer"])
            gpt_mismatched.append({**case, "corrected": corrected})

        # Run Llama-2-7B corrections
        print("  Running Llama-2-7B matched (RAG)...")
        llama_matched = []
        for case in llama_cases:
            corrected = rag_llama.correct(case["question"], case["incorrect_answer"])
            llama_matched.append({**case, "corrected": corrected})

        print("  Running Llama-2-7B mismatched (COT)...")
        llama_mismatched = []
        for case in llama_cases:
            corrected = cot_llama.correct(case["question"], case["incorrect_answer"])
            llama_mismatched.append({**case, "corrected": corrected})

        return {
            "gpt_matched": gpt_matched,
            "gpt_mismatched": gpt_mismatched,
            "llama_matched": llama_matched,
            "llama_mismatched": llama_mismatched
        }

    def evaluate_all(self, results: Dict) -> Dict:
        """Evaluate success rates and check gate conditions."""
        print("[3/5] Evaluating correction success rates...")

        evaluator = Evaluator(
            gate_threshold_pp=self.config["evaluation"]["gate_threshold_pp"],
            gate_threshold_rel=self.config["evaluation"]["gate_threshold_rel"]
        )

        # Add success field to each result
        for key in results:
            for r in results[key]:
                r["success"] = evaluator.evaluate_correction(r["corrected"], r["gold_answer"])

        # Compute success rates
        gpt_matched_rate = evaluator.compute_success_rate(results["gpt_matched"])
        gpt_mismatched_rate = evaluator.compute_success_rate(results["gpt_mismatched"])
        llama_matched_rate = evaluator.compute_success_rate(results["llama_matched"])
        llama_mismatched_rate = evaluator.compute_success_rate(results["llama_mismatched"])

        print(f"  GPT-3.5 matched: {gpt_matched_rate:.1%}, mismatched: {gpt_mismatched_rate:.1%}")
        print(f"  Llama-2-7B matched: {llama_matched_rate:.1%}, mismatched: {llama_mismatched_rate:.1%}")

        # Gate checks
        gpt_gate = evaluator.check_gate(gpt_matched_rate, gpt_mismatched_rate, "GPT-3.5")
        llama_gate = evaluator.check_gate(llama_matched_rate, llama_mismatched_rate, "Llama-2-7B")

        print(f"\n  GPT-3.5 gate: {'PASS' if gpt_gate['gate_pass'] else 'FAIL'} "
              f"(diff: {gpt_gate['difference']:.1%}, rel: {gpt_gate['relative_improvement']:.1f}%)")
        print(f"  Llama-2-7B gate: {'PASS' if llama_gate['gate_pass'] else 'FAIL'} "
              f"(diff: {llama_gate['difference']:.1%}, rel: {llama_gate['relative_improvement']:.1f}%)")

        # Overall gate pass requires BOTH models to pass
        overall_gate_pass = gpt_gate["gate_pass"] and llama_gate["gate_pass"]
        print(f"\n  Overall gate: {'PASS' if overall_gate_pass else 'FAIL'} (requires both models)")

        return {
            "gpt": gpt_gate,
            "llama": llama_gate,
            "overall_gate_pass": overall_gate_pass
        }

    def visualize(self, gate_results: Dict, all_results: Dict):
        """Generate all required figures."""
        print("[4/5] Generating visualizations...")

        save_dir = self.config["output"]["figures_dir"]

        plot_gate_metrics(gate_results["gpt"], gate_results["llama"], save_dir)
        print(f"  Saved gate_metrics_comparison.png")

        plot_success_comparison(gate_results["gpt"], gate_results["llama"], save_dir)
        print(f"  Saved success_rate_comparison.png")

        plot_per_model_breakdown(gate_results["gpt"], gate_results["llama"], save_dir)
        print(f"  Saved per_model_breakdown.png")

        plot_outcome_distribution(all_results, save_dir)
        print(f"  Saved correction_outcomes.png")

    def save_results(self, all_results: Dict, gate_results: Dict):
        """Save JSON results with per-sample outcomes and gate status."""
        print("[5/5] Saving results...")

        output = {
            "experiment": "h-m2",
            "hypothesis": "Matched correction routing (entity-error → RAG) achieves higher success rates than mismatched routing (entity-error → COT)",
            "gate_condition": "≥20pp difference OR ≥50% relative improvement, replicated across both models",
            "gate_results": {
                "gpt35": gate_results["gpt"],
                "llama2": gate_results["llama"],
                "overall_pass": gate_results["overall_gate_pass"]
            },
            "corrections": all_results
        }

        os.makedirs(os.path.dirname(self.config["output"]["results_file"]), exist_ok=True)
        with open(self.config["output"]["results_file"], "w") as f:
            json.dump(output, f, indent=2)

        print(f"  Saved {self.config['output']['results_file']}")

    def run(self) -> Dict:
        """Run full correction routing experiment."""
        print("=" * 60)
        print("h-m2: Correction Routing Experiment")
        print("=" * 60)

        # Load data
        gpt_cases, llama_cases = self.load_data()

        # Run corrections
        all_results = self.run_corrections(gpt_cases, llama_cases)

        # Evaluate
        gate_results = self.evaluate_all(all_results)

        # Visualize
        self.visualize(gate_results, all_results)

        # Save
        self.save_results(all_results, gate_results)

        print("\n" + "=" * 60)
        print("EXPERIMENT COMPLETE")
        print("=" * 60)
        print(f"Overall gate: {'PASS' if gate_results['overall_gate_pass'] else 'FAIL'}")
        print(f"GPT-3.5: {gate_results['gpt']['matched_rate']:.1%} (matched) vs {gate_results['gpt']['mismatched_rate']:.1%} (mismatched)")
        print(f"Llama-2-7B: {gate_results['llama']['matched_rate']:.1%} (matched) vs {gate_results['llama']['mismatched_rate']:.1%} (mismatched)")

        return gate_results


if __name__ == "__main__":
    experiment = CorrectionExperiment()
    results = experiment.run()
