import json
import re
from typing import List, Dict
from pathlib import Path


class FeatureExtractor:
    """Extract features from benchmark papers using standardized protocol."""

    def __init__(self, taxonomy_path: str, metrics_config: str):
        self.taxonomy = self._load_json(taxonomy_path)
        self.metric_patterns = self._load_json(metrics_config)

    def _load_json(self, path: str) -> dict:
        with open(path) as f:
            return json.load(f)

    def extract_task_type(self, abstract: str, title: str) -> str:
        """Map to PWC taxonomy."""
        keywords = (abstract + " " + title).lower()
        scores = {}
        for category, terms in self.taxonomy.items():
            scores[category] = sum(1 for term in terms if term.lower() in keywords)
        return max(scores, key=scores.get) if scores else "unknown"

    def extract_metrics(self, full_text: str) -> List[str]:
        """Regex-based metric extraction."""
        matches = []
        for metric_name, pattern in self.metric_patterns.items():
            if re.search(pattern, full_text, re.IGNORECASE):
                matches.append(metric_name)
        return matches if matches else ["unknown"]

    def extract_modality(self, description: str) -> str:
        """Decision tree classification."""
        desc_lower = description.lower()
        modalities = []
        if any(kw in desc_lower for kw in ["image", "vision", "visual"]):
            modalities.append("image")
        if any(kw in desc_lower for kw in ["text", "language", "nlp"]):
            modalities.append("text")
        if any(kw in desc_lower for kw in ["audio", "speech"]):
            modalities.append("audio")
        if "video" in desc_lower:
            modalities.append("video")

        if len(modalities) > 1:
            return "multimodal"
        return modalities[0] if modalities else "unknown"

    def extract_dataset_size(self, size_field: int) -> int:
        """Extract dataset size from metadata."""
        return size_field

    def extract_all(self, paper: dict) -> dict:
        """Extract all features."""
        return {
            "benchmark_id": paper.get("id", "unknown"),
            "task_type": self.extract_task_type(
                paper.get("task", ""), paper.get("id", "")
            ),
            "modality": self.extract_modality(paper.get("task", "")),
            "metrics": self.extract_metrics(paper.get("task", "")),
            "dataset_size": self.extract_dataset_size(paper.get("size", 0)),
        }
