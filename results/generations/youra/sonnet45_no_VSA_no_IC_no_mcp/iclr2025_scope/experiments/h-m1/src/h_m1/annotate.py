import pandas as pd
from typing import List, Dict
from datetime import datetime


class AnnotationWorkflow:
    """Orchestrate annotation process."""

    def __init__(self, protocol_version: str, extractor):
        self.protocol_version = protocol_version
        self.extractor = extractor

    def calibrate(self, practice_benchmarks: List[dict]) -> Dict[str, float]:
        """Pre-study calibration on 3 practice samples."""
        # Mock calibration (returns dummy kappa)
        return {"calibration_kappa": 0.85}

    def annotate(self, benchmarks: List[dict], annotator_id: str) -> pd.DataFrame:
        """Independent annotation."""
        rows = []
        for b in benchmarks:
            features = self.extractor.extract_all(b)
            features["annotator_id"] = annotator_id
            features["timestamp"] = datetime.now().isoformat()
            rows.append(features)
        return pd.DataFrame(rows)

    def save_annotations(self, annotations: pd.DataFrame, output_path: str) -> None:
        """Save with timestamp and protocol version."""
        annotations["protocol_version"] = self.protocol_version
        annotations.to_csv(output_path, index=False)
