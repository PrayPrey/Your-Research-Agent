"""Ground truth validation for impact and schema accuracy."""
import pandas as pd
from typing import Tuple
from .impact_analyzer import ImpactAnalyzer
from .schema_diff import SchemaCompatibilityDetector

class GroundTruthValidator:
    def __init__(self, ground_truth_csv: str, analyzer: ImpactAnalyzer, detector: SchemaCompatibilityDetector):
        self.ground_truth = pd.read_csv(ground_truth_csv)
        self.analyzer = analyzer
        self.detector = detector

    def validate_impact_completeness(self) -> Tuple[float, float]:
        """Precision/Recall on ground truth dependencies."""
        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for _, row in self.ground_truth.iterrows():
            dataset_id = row['dataset_id']
            affected_entity = row['affected_entity_id']
            ground_truth_label = row['dependency_label']

            impact = self.analyzer.compute_impact(dataset_id)
            predicted_affected = affected_entity in impact['affected']

            if ground_truth_label == 'affected':
                if predicted_affected:
                    tp += 1
                else:
                    fn += 1
            else:  # 'unaffected'
                if predicted_affected:
                    fp += 1
                else:
                    tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        return precision, recall

    def validate_schema_accuracy(self) -> float:
        """% predicted breaking changes matching annotated labels."""
        correct = 0
        total = 0

        for _, row in self.ground_truth.iterrows():
            if pd.isna(row.get('schema_label')):
                continue

            dataset_id = row['dataset_id']
            successor_id = row['successor_id']
            ground_truth_label = row['schema_label']

            # Mock schema fetch (would come from graph nodes in real implementation)
            schema1 = {'field1': {'type': 'int32'}}
            schema2 = {'field1': {'type': 'int64'}}

            classification, _ = self.detector.detect_breaking_changes(schema1, schema2)

            label_map = {
                'compatible': 'COMPATIBLE',
                'minor_breaking': 'MINOR_BREAKING',
                'major_breaking': 'MAJOR_BREAKING'
            }

            if label_map.get(ground_truth_label) == classification:
                correct += 1
            total += 1

        return correct / total if total > 0 else 0
