"""Evaluation of LLM extraction quality (precision/recall)."""
import json
from pathlib import Path
from typing import List, Dict

class ExtractionEvaluator:
    """Evaluate extraction precision and recall vs gold standard."""
    
    def __init__(
        self,
        precision_threshold: float = 0.70,
        recall_threshold: float = 0.80,
        kappa_threshold: float = 0.70
    ):
        """Initialize evaluator with gate thresholds."""
        self.precision_threshold = precision_threshold
        self.recall_threshold = recall_threshold
        self.kappa_threshold = kappa_threshold
    
    def evaluate_extraction(
        self,
        llm_items: List[str],
        gold_items: List[str]
    ) -> Dict:
        """Compute precision and recall for one sample."""
        llm_set = set(item.lower().strip() for item in llm_items)
        gold_set = set(item.lower().strip() for item in gold_items)
        
        tp = len(llm_set & gold_set)
        fp = len(llm_set - gold_set)
        fn = len(gold_set - llm_set)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall
        }
    
    def aggregate_results(self, sample_results: List[Dict]) -> Dict:
        """Compute mean precision/recall across samples."""
        precisions = [r["precision"] for r in sample_results]
        recalls = [r["recall"] for r in sample_results]
        
        return {
            "mean_precision": sum(precisions) / len(precisions) if precisions else 0.0,
            "mean_recall": sum(recalls) / len(recalls) if recalls else 0.0,
            "sample_count": len(sample_results)
        }
    
    def check_gate_condition(self, aggregated: Dict, kappa: float) -> Dict:
        """Check if gate thresholds are met."""
        precision_pass = aggregated["mean_precision"] >= self.precision_threshold
        recall_pass = aggregated["mean_recall"] >= self.recall_threshold
        kappa_pass = kappa >= self.kappa_threshold
        
        gate_pass = precision_pass and recall_pass and kappa_pass
        
        return {
            "gate_passed": gate_pass,
            "precision_pass": precision_pass,
            "recall_pass": recall_pass,
            "kappa_pass": kappa_pass,
            "precision": aggregated["mean_precision"],
            "recall": aggregated["mean_recall"],
            "kappa": kappa
        }
    
    def save_results(self, results: Dict, output_file: Path):
        """Save evaluation results to JSON."""
        # Convert numpy types to Python native types
        def convert_types(obj):
            import numpy as np
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(v) for v in obj]
            elif isinstance(obj, (np.bool_, np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj

        results_converted = convert_types(results)
        with open(output_file, 'w') as f:
            json.dump(results_converted, f, indent=2)
