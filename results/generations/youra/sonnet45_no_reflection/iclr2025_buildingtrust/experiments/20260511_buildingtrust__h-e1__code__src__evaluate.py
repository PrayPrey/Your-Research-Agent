"""Evaluation module for trustworthiness benchmarks"""
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
from datasets import Dataset
from torch.utils.data import DataLoader
from typing import Dict, List
from tqdm import tqdm
import numpy as np

class TrustEvaluator:
    """Base evaluator for trustworthiness dimensions"""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize evaluator.

        Args:
            model: Model to evaluate
            tokenizer: Tokenizer for preprocessing
        """
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()

    def evaluate(self, dataset: Dataset, batch_size: int = 8) -> float:
        """Evaluate model on dataset.

        Args:
            dataset: Dataset to evaluate
            batch_size: Evaluation batch size

        Returns:
            Accuracy score
        """
        correct = 0
        total = 0

        self.model.eval()

        with torch.no_grad():
            for i in tqdm(range(0, len(dataset), batch_size), desc="Evaluating"):
                batch = dataset[i:min(i + batch_size, len(dataset))]

                # Prepare inputs
                texts = []
                labels = []

                for item in batch:
                    if isinstance(item, dict):
                        text, label = self._extract_text_label(item)
                        texts.append(text)
                        labels.append(label)

                if not texts:
                    continue

                # Tokenize
                encodings = self.tokenizer(
                    texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                ).to(self.model.device)

                # Forward pass
                outputs = self.model(**encodings)
                predictions = torch.argmax(outputs.logits[:, -1, :], dim=-1)

                # Count correct
                for pred, label in zip(predictions.cpu().numpy(), labels):
                    if pred == label:
                        correct += 1
                    total += 1

        accuracy = correct / total if total > 0 else 0.0
        return accuracy

    def _extract_text_label(self, item: Dict) -> tuple:
        """Extract text and label from dataset item."""
        # Handle different dataset formats
        if "question" in item:
            # TruthfulQA
            text = item["question"]
            label = item.get("mc1_targets", {}).get("labels", [0])[0]
        elif "context" in item:
            # BBQ
            text = f"{item['context']} {item['question']}"
            label = item.get("label", 0)
        elif "sentence" in item:
            # AdvGLUE
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
