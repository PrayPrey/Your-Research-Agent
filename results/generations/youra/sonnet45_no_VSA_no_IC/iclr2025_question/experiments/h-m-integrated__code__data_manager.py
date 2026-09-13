"""Data manager for h-m-integrated: load h-e1 artifacts + HaluEval."""
import json
import pickle
from pathlib import Path
from typing import Dict, List, Tuple
from datasets import load_dataset
import random


class DataManager:
    """Load h-e1 artifacts and HaluEval dataset."""

    def __init__(self, h_e1_dir: str, seed: int = 42):
        """
        Initialize data manager.

        Args:
            h_e1_dir: Path to h-e1 code directory
            seed: Random seed for HaluEval split
        """
        self.h_e1_dir = Path(h_e1_dir)
        self.seed = seed
        random.seed(seed)

    def load_h_e1_artifacts(self) -> Dict:
        """
        Load h-e1 uncertainty scores, answers, labels from experiment results.

        Returns:
            {
                "questions": List[str],
                "answers": List[str],
                "labels": List[int],  # 0=correct, 1=incorrect
                "uq_scores": {
                    "temp_scaling": List[float],
                    "conformal": List[float],
                    "mc_k1": List[float],
                    "mc_k3": List[float],
                    "mc_k5": List[float],
                    "mc_k10": List[float]
                },
                "calibration_params": {
                    "temperature": float,
                    "conformal_threshold": float
                }
            }
        """
        results_file = self.h_e1_dir / "experiment_results.json"
        if not results_file.exists():
            raise FileNotFoundError(f"h-e1 results not found: {results_file}")

        with open(results_file, "r") as f:
            h_e1_results = json.load(f)

        return {
            "questions": h_e1_results.get("test_questions", []),
            "answers": h_e1_results.get("test_answers", []),
            "labels": h_e1_results.get("labels", []),
            "uq_scores": h_e1_results.get("uncertainties_by_method", {}),
            "calibration_params": {
                "temperature": h_e1_results.get("temperature", 1.0),
                "conformal_threshold": h_e1_results.get("conformal_threshold", 0.9)
            }
        }

    def load_halueval(
        self,
        split: str = "qa_samples",
        calib_ratio: float = 0.8,
        cache_dir: str = None,
        sample_size: int = 2000
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Load HaluEval QA split, return 80/20 calib/test.

        Args:
            split: HaluEval split name
            calib_ratio: Fraction for calibration (default 0.8)
            cache_dir: Dataset cache directory
            sample_size: Number of samples to use (default 2000)

        Returns:
            (calib_data, test_data): Each item = {question, answer, label}
        """
        # Load HaluEval from HuggingFace
        ds = load_dataset("pminervini/HaluEval", split=split, cache_dir=cache_dir)

        # Convert to list of dicts
        samples = []
        for item in ds:
            samples.append({
                "question": item.get("knowledge", ""),
                "answer": item.get("right_answer", ""),
                "hallucinated_answer": item.get("hallucinated_answer", ""),
                "label": 1 if "hallucinated" in str(item.get("label", "")).lower() else 0
            })

        # Subsample if needed
        if len(samples) > sample_size:
            random.shuffle(samples)
            samples = samples[:sample_size]

        # Split 80/20
        split_idx = int(len(samples) * calib_ratio)
        calib = samples[:split_idx]
        test = samples[split_idx:]

        return calib, test
