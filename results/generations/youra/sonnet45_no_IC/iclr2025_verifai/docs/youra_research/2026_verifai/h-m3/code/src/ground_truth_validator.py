"""Validate detected contradictions against known failures."""

import json
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

class GroundTruthValidator:
    """Validate detected contradictions against known failures."""

    def __init__(self, ground_truth_path: Path):
        """Initialize validator."""
        self.ground_truth_path = Path(ground_truth_path)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

    def load_ground_truth(self) -> List[Dict]:
        """Load known failures."""
        with open(self.ground_truth_path, 'r') as f:
            return json.load(f)

    def match_detected_to_ground_truth(
        self,
        detected: List[Dict],
        ground_truth: List[Dict]
    ) -> Dict:
        """Match with fuzzy similarity."""
        tp = []
        fn = list(ground_truth)

        for detected_item in detected:
            matched = False
            for gt_item in fn:
                if self.semantic_fuzzy_match(detected_item, gt_item):
                    tp.append(detected_item)
                    fn.remove(gt_item)
                    matched = True
                    break

        fp = [d for d in detected if d not in tp]

        return {"TP": tp, "FP": fp, "FN": fn}

    def semantic_fuzzy_match(
        self,
        detected_item: Dict,
        gt_item: Dict,
        threshold: float = 0.7
    ) -> bool:
        """Semantic fuzzy matching."""
        det_text = detected_item["assumption"]["text"] + " " + detected_item["claim"]["text"]
        gt_text = gt_item["assumption"]["text"] + " " + gt_item["claim"]["text"]

        det_emb = self.encoder.encode(det_text, convert_to_tensor=True)
        gt_emb = self.encoder.encode(gt_text, convert_to_tensor=True)

        similarity = util.cos_sim(det_emb, gt_emb).item()
        return similarity >= threshold

    def compute_confusion_matrix(self, matches: Dict, total_pairs: int) -> Dict:
        """Compute TP/FP/FN/TN."""
        tp = len(matches["TP"])
        fp = len(matches["FP"])
        fn = len(matches["FN"])
        tn = total_pairs - tp - fp - fn

        return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}
