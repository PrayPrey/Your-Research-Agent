"""User group assignment for RCT experiment."""
import hashlib
from typing import Dict, Any
from .config import RCT_EXPERIMENT_CONFIG

class UserGroupAssigner:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.groups = list(RCT_EXPERIMENT_CONFIG['groups'].keys())
        self.config = RCT_EXPERIMENT_CONFIG

    def assign_group(self, user_id: str, complexity: str = None) -> str:
        """Assign user to group deterministically."""
        hash_val = int(hashlib.sha256(f"{self.seed}{user_id}".encode()).hexdigest(), 16)

        if complexity and self.config['stratification']['enabled']:
            hash_val ^= hash(complexity)

        group_idx = hash_val % len(self.groups)
        return self.groups[group_idx]

    def get_complexity_stratum(self, impact_summary: Dict[str, Any]) -> str:
        """Classify dependency complexity."""
        if not impact_summary.get('by_depth'):
            return 'low'

        max_depth = max(impact_summary['by_depth'].keys()) if impact_summary['by_depth'] else 0
        bins = self.config['stratification']['bins']

        if bins['low']['min_depth'] <= max_depth <= bins['low']['max_depth']:
            return 'low'
        elif bins['medium']['min_depth'] <= max_depth <= bins['medium']['max_depth']:
            return 'medium'
        else:
            return 'high'
