"""Evaluation module using EleutherAI lm-evaluation-harness"""
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
from typing import Dict, List
import numpy as np
from pathlib import Path
import tempfile
import subprocess
import json

class TrustEvaluator:
    """Evaluator using lm-evaluation-harness for TruthfulQA"""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize evaluator.

        Args:
            model: Model to evaluate
            tokenizer: Tokenizer for preprocessing
        """
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()

    def evaluate(self, dimension: str, model_path: str = None) -> float:
        """Evaluate model on specified dimension using lm-eval harness.

        Args:
            dimension: One of "truthfulness", "fairness", "robustness"
            model_path: Path to saved model (if None, saves current model temporarily)

        Returns:
            Evaluation score (accuracy for the dimension)
        """
        # Map dimension to lm-eval task
        task_map = {
            "truthfulness": "truthfulqa_mc2",
            "fairness": "bbq",  # Simplified - would need specific category
            "robustness": "adversarial_qa"  # Simplified proxy
        }

        if dimension not in task_map:
            raise ValueError(f"Unknown dimension: {dimension}")

        task = task_map[dimension]

        # For H-M1, we focus on TruthfulQA only
        if dimension != "truthfulness":
            # Fallback to simple evaluation for non-target dimensions
            return self._simple_evaluate(dimension)

        # Save model temporarily if not provided
        temp_dir = None
        if model_path is None:
            temp_dir = tempfile.mkdtemp()
            model_path = temp_dir
            self.model.save_pretrained(model_path)
            self.tokenizer.save_pretrained(model_path)

        try:
            # Run lm-eval harness
            result = self._run_lm_eval(task, model_path)
            return result
        finally:
            # Cleanup temp directory
            if temp_dir is not None:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _run_lm_eval(self, task: str, model_path: str) -> float:
        """Run lm-evaluation-harness and extract score.

        Args:
            task: Task name (e.g., "truthfulqa_mc2")
            model_path: Path to model

        Returns:
            Task accuracy/score
        """
        try:
            # Use lm_eval Python API instead of CLI for better control
            from lm_eval import evaluator
            from lm_eval.models.huggingface import HFLM

            # Create model wrapper
            lm_obj = HFLM(
                pretrained=model_path,
                device=str(self.model.device),
                batch_size=4
            )

            # Run evaluation
            results = evaluator.simple_evaluate(
                model=lm_obj,
                tasks=[task],
                num_fewshot=0,
                batch_size=4
            )

            # Extract score
            if task in results["results"]:
                task_results = results["results"][task]
                # TruthfulQA MC2 uses "acc" metric
                if "acc" in task_results:
                    return float(task_results["acc"])
                elif "acc_norm" in task_results:
                    return float(task_results["acc_norm"])
                else:
                    # Return first numeric metric found
                    for key, value in task_results.items():
                        if isinstance(value, (int, float)):
                            return float(value)

            return 0.0

        except Exception as e:
            print(f"Warning: lm-eval harness failed: {e}")
            print("Falling back to simple evaluation")
            return self._simple_evaluate_truthfulqa()

    def _simple_evaluate_truthfulqa(self) -> float:
        """Simple TruthfulQA evaluation fallback."""
        from datasets import load_dataset
        from torch.utils.data import DataLoader

        try:
            dataset = load_dataset("truthful_qa", "multiple_choice", split="validation")

            correct = 0
            total = 0

            with torch.no_grad():
                for item in dataset:
                    if "question" not in item or "mc2_targets" not in item:
                        continue

                    question = item["question"]
                    choices = item["mc2_targets"]["choices"]
                    labels = item["mc2_targets"]["labels"]

                    # Get correct answer indices
                    correct_indices = [i for i, label in enumerate(labels) if label == 1]
                    if not correct_indices:
                        continue

                    # Evaluate each choice
                    choice_logits = []
                    for choice in choices:
                        prompt = f"{question} {choice}"
                        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
                        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

                        outputs = self.model(**inputs)
                        # Use mean logit as score
                        logit = outputs.logits.mean().item()
                        choice_logits.append(logit)

                    # Check if highest logit corresponds to a correct answer
                    best_idx = np.argmax(choice_logits)
                    if best_idx in correct_indices:
                        correct += 1
                    total += 1

                    # Limit for PoC
                    if total >= 100:
                        break

            return correct / total if total > 0 else 0.0

        except Exception as e:
            print(f"Warning: Simple TruthfulQA evaluation failed: {e}")
            return 0.0

    def _simple_evaluate(self, dimension: str) -> float:
        """Simple evaluation for non-target dimensions."""
        from src.data import TrustworthinessDataset

        try:
            dataset = TrustworthinessDataset(dimension)

            correct = 0
            total = 0

            with torch.no_grad():
                for i in range(min(100, len(dataset))):
                    item = dataset[i]
                    text, label = self._extract_text_label(item)

                    inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                    inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

                    outputs = self.model(**inputs)
                    pred = torch.argmax(outputs.logits[:, -1, :], dim=-1).item()

                    if pred == label:
                        correct += 1
                    total += 1

            return correct / total if total > 0 else 0.0

        except Exception as e:
            print(f"Warning: Simple evaluation failed for {dimension}: {e}")
            return 0.0

    def _extract_text_label(self, item: Dict) -> tuple:
        """Extract text and label from dataset item."""
        if "question" in item:
            text = item["question"]
            label = item.get("mc1_targets", {}).get("labels", [0])[0]
        elif "context" in item:
            text = f"{item['context']} {item['question']}"
            label = item.get("label", 0)
        elif "sentence" in item:
            text = item["sentence"]
            label = item.get("label", 0)
        else:
            text = str(item)
            label = 0
        return text, label


class CorrelationAnalyzer:
    """Correlation analysis for cross-dimensional effects"""

    def __init__(self):
        """Initialize correlation analyzer"""
        pass

    def compute_pearson_correlation(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> Dict[str, float]:
        """Compute Pearson correlation coefficient with p-value.

        Args:
            deltas1: Delta scores for dimension 1
            deltas2: Delta scores for dimension 2

        Returns:
            Dictionary with rho (correlation) and p_value
        """
        from scipy.stats import pearsonr

        # Compute correlation
        rho, p_value = pearsonr(deltas1, deltas2)

        return {
            "rho": float(rho),
            "p_value": float(p_value),
            "significant": p_value < 0.01,
            "n": len(deltas1)
        }

    def compute_paired_ttest(
        self,
        pre_scores: List[float],
        post_scores: List[float]
    ) -> Dict[str, float]:
        """Compute paired t-test for pre/post comparison.

        Args:
            pre_scores: Pre-intervention scores
            post_scores: Post-intervention scores

        Returns:
            Dictionary with t_statistic, p_value, and mean_delta
        """
        from scipy.stats import ttest_rel

        # Compute paired t-test
        t_stat, p_value = ttest_rel(post_scores, pre_scores)

        deltas = [post - pre for post, pre in zip(post_scores, pre_scores)]
        mean_delta = np.mean(deltas)

        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "mean_delta": float(mean_delta),
            "significant": p_value < 0.05,
            "n": len(pre_scores)
        }

    def analyze_cross_dimensional_effects(
        self,
        baseline_scores: Dict[str, float],
        intervention_scores: Dict[str, Dict[str, float]]
    ) -> Dict:
        """Analyze cross-dimensional effects from intervention.

        Args:
            baseline_scores: Baseline scores for each dimension
            intervention_scores: Intervention scores indexed by [replicate][dimension]

        Returns:
            Correlation analysis results
        """
        results = {
            "correlations": {},
            "significant_pairs": [],
            "summary": {}
        }

        # Extract dimensions
        dimensions = list(baseline_scores.keys())

        # Compute deltas for each replicate
        deltas = {dim: [] for dim in dimensions}

        for replicate_scores in intervention_scores.values():
            for dim in dimensions:
                delta = replicate_scores[dim] - baseline_scores[dim]
                deltas[dim].append(delta)

        # Compute correlations for all dimension pairs
        for i, dim1 in enumerate(dimensions):
            for dim2 in dimensions[i+1:]:
                pair_key = f"{dim1}_vs_{dim2}"

                corr_result = self.compute_pearson_correlation(
                    deltas[dim1],
                    deltas[dim2]
                )

                results["correlations"][pair_key] = corr_result

                if corr_result["significant"]:
                    results["significant_pairs"].append(pair_key)

        # Summary statistics
        total_pairs = len(results["correlations"])
        significant_count = len(results["significant_pairs"])

        results["summary"] = {
            "total_pairs": total_pairs,
            "significant_pairs": significant_count,
            "significance_rate": significant_count / total_pairs if total_pairs > 0 else 0.0
        }

        return results
