"""Migration plan generation with impact analysis and schema diff."""
import networkx as nx
from typing import Dict, List, Any, Set
from .impact_analyzer import ImpactAnalyzer
from .schema_diff import SchemaCompatibilityDetector
from .config import MIGRATION_PLAN_CONFIG

class MigrationPlanner:
    def __init__(self, graph: nx.DiGraph, analyzer: ImpactAnalyzer, detector: SchemaCompatibilityDetector):
        self.graph = graph
        self.analyzer = analyzer
        self.detector = detector
        self.config = MIGRATION_PLAN_CONFIG

    def generate_plan(self, deprecated_id: str, successor_id: str) -> Dict[str, Any]:
        """Generate migration plan."""
        impact = self.analyzer.compute_impact(deprecated_id)

        schema_old = self.graph.nodes[deprecated_id].get('schema', {})
        schema_new = self.graph.nodes[successor_id].get('schema', {})
        classification, changes = self.detector.detect_breaking_changes(schema_old, schema_new)

        # Topological sort for migration order
        affected_nodes = list(impact['affected'])[:self.config['generation']['max_steps']]
        subgraph = self.graph.subgraph([deprecated_id] + affected_nodes)

        try:
            migration_order = list(nx.topological_sort(subgraph))
        except nx.NetworkXError:
            migration_order = list(nx.dfs_postorder_nodes(subgraph, deprecated_id))

        plan = {
            'deprecated': deprecated_id,
            'successor': successor_id,
            'impact_radius': impact['summary'],
            'compatibility': classification,
            'breaking_changes': changes,
            'migration_steps': self._generate_steps(migration_order, changes),
            'adapters': self.detector.generate_adapters(changes) if classification == 'MINOR_BREAKING' else [],
            'verification_checklist': self._generate_checklist(changes)
        }

        return plan

    def _generate_steps(self, order: List[str], changes: List[Dict]) -> List[Dict[str, str]]:
        """Generate ordered task list."""
        steps = []
        for i, entity in enumerate(order[:self.config['generation']['max_steps']]):
            steps.append({
                'order': i + 1,
                'entity': entity,
                'action': f'Update dataset reference: {entity}',
                'priority': 'HIGH' if i < 3 else 'MEDIUM'
            })
        return steps

    def _generate_checklist(self, changes: List[Dict]) -> List[str]:
        """Generate post-migration checks."""
        checklist = ['Run existing test suite']
        for change in changes:
            if change['type'] == 'FIELD_REMOVAL':
                checklist.append(f"Remove references to field '{change['field']}'")
            elif change['type'] == 'TYPE_CHANGE':
                checklist.append(f"Verify type conversion for '{change['field']}'")
        return checklist

def display_migration_plan(plan: Dict[str, Any]):
    """Print migration plan to console."""
    print("\n=== MIGRATION PLAN ===")
    print(f"Deprecated: {plan['deprecated']}")
    print(f"Successor: {plan['successor']}")
    print(f"Impact: {plan['impact_radius']['total']} affected entities")
    print(f"Compatibility: {plan['compatibility']}")

    if plan['breaking_changes']:
        print("\nBreaking Changes:")
        for change in plan['breaking_changes']:
            print(f"  - {change['type']}: {change.get('field', 'N/A')} ({change['severity']})")

    if plan['adapters']:
        print("\nSuggested Adapters:")
        for adapter in plan['adapters']:
            print(f"  {adapter}")

    print("\nVerification Checklist:")
    for item in plan['verification_checklist']:
        print(f"  [ ] {item}")
    print("=" * 40)
