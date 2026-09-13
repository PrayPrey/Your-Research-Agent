"""Load h-e1 entropy results."""
import json
import numpy as np
from typing import Tuple


class DataLoader:
    """Load h-e1 entropy results and prepare (X, y) arrays."""

    def load_h_e1_results(self, json_path: str) -> dict:
        """Read JSON from h-e1. Returns raw dict."""
        with open(json_path, 'r') as f:
            return json.load(f)

    def extract_arrays(self, results: dict) -> Tuple[np.ndarray, np.ndarray]:
        """Extract (X, y) arrays. X: (73,) entropy values, y: (73,) labels (0=entity, 1=non-entity)"""
        entity_entropies = np.array(results['entity_entropies'])
        non_entity_entropies = np.array(results['non_entity_entropies'])

        X = np.concatenate([entity_entropies, non_entity_entropies])
        y = np.concatenate([
            np.zeros(len(entity_entropies)),  # 0 = entity-error
            np.ones(len(non_entity_entropies))  # 1 = non-entity-error
        ])

        return X, y
