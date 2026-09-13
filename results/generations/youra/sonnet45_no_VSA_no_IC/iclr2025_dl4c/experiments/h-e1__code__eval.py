"""Evaluation pipeline for HumanEval pass@1 metric."""

import torch
import logging
import json
import os
from typing import Dict, List
from tqdm import tqdm
from sandbox import ExecutionSandbox

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self, config: dict, model, tokenizer, sandbox: ExecutionSandbox):
        self.config = config
        self.model = model
        self.tokenizer = tokenizer
        self.sandbox = sandbox
        self.device = model.device

    def evaluate_checkpoint(self, test_suites: List[Dict]) -> Dict:
        """Generate completions and compute pass@1."""
        logger.info("Starting evaluation...")

        self.model.eval()

        results = []
        passed_count = 0

        for problem in tqdm(test_suites, desc="Evaluating"):
            inputs = self.tokenizer(problem["prompt"], return_tensors="pt", padding=True, truncation=True).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config["generation"]["evaluation"]["max_new_tokens"],
                    temperature=self.config["generation"]["evaluation"]["temperature"],
                    top_p=self.config["generation"]["evaluation"]["top_p"],
                    do_sample=self.config["generation"]["evaluation"]["do_sample"],
                    num_return_sequences=self.config["generation"]["evaluation"]["num_return_sequences"],
                    pad_token_id=self.tokenizer.pad_token_id
                )

            completion = self.tokenizer.decode(outputs[0], skip_special_tokens=True).replace(problem["prompt"], "").strip()

            reward = self.sandbox.compute_binary_reward(completion, problem["test"], problem["entry_point"])
            passed = reward > 0.5

            results.append({
                "task_id": problem["task_id"],
                "completion": completion,
                "passed": passed
            })

            if passed:
                passed_count += 1

        pass_at_1 = passed_count / len(test_suites)

        logger.info(f"Evaluation complete: pass@1 = {pass_at_1:.4f} ({passed_count}/{len(test_suites)})")

        return {
            "pass@1": pass_at_1,
            "results": results,
            "total": len(test_suites),
            "passed": passed_count
        }

    def save_results(self, results: Dict, output_path: str):
        """Save evaluation results to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_path}")
