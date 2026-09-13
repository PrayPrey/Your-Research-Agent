"""Schema compatibility detection and breaking change classification."""
from typing import Dict, List, Tuple, Any
from enum import Enum
from difflib import SequenceMatcher
from .config import SCHEMA_DIFF_CONFIG

class Severity(Enum):
    COMPATIBLE = "COMPATIBLE"
    MINOR_BREAKING = "MINOR_BREAKING"
    MAJOR_BREAKING = "MAJOR_BREAKING"

class SchemaCompatibilityDetector:
    def __init__(self):
        self.config = SCHEMA_DIFF_CONFIG

    def detect_breaking_changes(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Tuple[str, List[Dict]]:
        """Detect schema changes. Returns (classification, changes_list)."""
        changes = []

        if not schema1 or not schema2:
            return ('MAJOR_BREAKING', [{'type': 'MISSING_SCHEMA', 'severity': 'MAJOR'}])

        removed = set(schema1.keys()) - set(schema2.keys())
        added = set(schema2.keys()) - set(schema1.keys())
        common = set(schema1.keys()) & set(schema2.keys())

        for field in removed:
            changes.append({
                'type': 'FIELD_REMOVAL',
                'field': field,
                'severity': 'MAJOR'
            })

        for field in common:
            type1 = schema1[field].get('type') if isinstance(schema1[field], dict) else str(schema1[field])
            type2 = schema2[field].get('type') if isinstance(schema2[field], dict) else str(schema2[field])

            if type1 != type2:
                severity = 'MINOR' if self._is_coercible(type1, type2) else 'MAJOR'
                changes.append({
                    'type': 'TYPE_CHANGE',
                    'field': field,
                    'old_type': type1,
                    'new_type': type2,
                    'severity': severity
                })

        # Classify overall
        if not changes:
            classification = 'COMPATIBLE'
        elif all(c['severity'] == 'MINOR' for c in changes):
            classification = 'MINOR_BREAKING'
        else:
            classification = 'MAJOR_BREAKING'

        return classification, changes

    def _is_coercible(self, old_type: str, new_type: str) -> bool:
        """Check if type change is coercible."""
        compatible_pairs = self.config['type_compatibility']['compatible_pairs']
        return (old_type, new_type) in compatible_pairs

    def generate_adapters(self, changes: List[Dict]) -> List[str]:
        """Generate code for MINOR changes."""
        adapters = []
        for change in changes:
            if change['severity'] != 'MINOR':
                continue

            if change['type'] == 'TYPE_CHANGE':
                adapters.append(
                    f"dataset = dataset.cast_column('{change['field']}', '{change['new_type']}')"
                )
            elif change['type'] == 'FIELD_RENAME':
                adapters.append(
                    f"dataset = dataset.rename_column('{change['old_name']}', '{change['new_name']}')"
                )

        return adapters[:self.config['adapters']['max_adapters_per_plan']]
