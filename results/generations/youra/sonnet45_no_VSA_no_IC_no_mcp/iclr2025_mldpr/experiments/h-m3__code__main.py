"""Main experiment script for h-m3: Dependency-Aware Migration Plans."""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.graph_builder import DependencyGraphBuilder
from src.impact_analyzer import ImpactAnalyzer
from src.schema_diff import SchemaCompatibilityDetector
from src.migration_planner import MigrationPlanner, display_migration_plan
from src.user_group_assigner import UserGroupAssigner
from src.ground_truth_validator import GroundTruthValidator

def load_mock_data():
    """Load mock dataset and dependency data."""
    data_dir = Path(__file__).parent / 'data'

    with open(data_dir / 'mock_datasets.json') as f:
        datasets = json.load(f)

    with open(data_dir / 'mock_dependencies.json') as f:
        dependencies = json.load(f)

    return datasets, dependencies

def run_experiment():
    """Run h-m3 experiment: dependency-aware migration planning."""
    print("=" * 60)
    print("H-M3: Dependency-Aware Migration Plans")
    print("=" * 60)

    # Phase 1: Build dependency graph
    print("\n[Phase 1] Building dependency graph...")
    datasets, dependencies = load_mock_data()

    builder = DependencyGraphBuilder()
    graph = builder.build_graph(
        hf_metadata=datasets,
        github_deps=dependencies,
        pwc_citations=[]
    )

    print(f"Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    # Save graph
    graph_path = Path(__file__).parent / 'data' / 'dependency_graph.json.gz'
    builder.save(str(graph_path))
    print(f"Graph saved to {graph_path}")

    # Phase 2: Analyze impact
    print("\n[Phase 2] Analyzing impact...")
    analyzer = ImpactAnalyzer(graph)
    impact = analyzer.compute_impact('deprecated/old-nlp-dataset')

    print(f"Impact radius: {impact['summary']['total']} affected entities")
    print(f"By type: {impact['summary']['by_type']}")
    print(f"By depth: {impact['summary']['by_depth']}")

    # Phase 3: Schema compatibility
    print("\n[Phase 3] Detecting schema compatibility...")
    detector = SchemaCompatibilityDetector()
    old_schema = graph.nodes['deprecated/old-nlp-dataset']['schema']
    new_schema = graph.nodes['active/new-nlp-dataset']['schema']

    classification, changes = detector.detect_breaking_changes(old_schema, new_schema)
    print(f"Compatibility: {classification}")
    print(f"Breaking changes: {len(changes)}")
    for change in changes:
        print(f"  - {change}")

    # Phase 4: Generate migration plan
    print("\n[Phase 4] Generating migration plan...")
    planner = MigrationPlanner(graph, analyzer, detector)
    plan = planner.generate_plan('deprecated/old-nlp-dataset', 'active/new-nlp-dataset')

    display_migration_plan(plan)

    # Phase 5: User group assignment
    print("\n[Phase 5] User group assignment (RCT)...")
    assigner = UserGroupAssigner(seed=42)
    complexity = assigner.get_complexity_stratum(impact['summary'])
    test_users = ['user001', 'user002', 'user003', 'user004', 'user005']

    for user_id in test_users:
        group = assigner.assign_group(user_id, complexity)
        print(f"User {user_id} -> Group: {group} (Complexity: {complexity})")

    # Phase 6: Validation
    print("\n[Phase 6] Validating against ground truth...")
    gt_path = Path(__file__).parent / 'data' / 'ground_truth' / 'ground_truth_labels.csv'
    validator = GroundTruthValidator(str(gt_path), analyzer, detector)

    precision, recall = validator.validate_impact_completeness()
    schema_accuracy = validator.validate_schema_accuracy()

    print(f"Impact Completeness - Precision: {precision:.2%}, Recall: {recall:.2%}")
    print(f"Schema Accuracy: {schema_accuracy:.2%}")

    # Compute final metrics
    print("\n[Results Summary]")
    print("=" * 60)
    print(f"Impact Completeness (Recall): {recall:.2%} (Target: ≥95%)")
    print(f"Schema Accuracy: {schema_accuracy:.2%} (Target: ≥80%)")

    # Gate evaluation (SHOULD_WORK)
    gate_pass = recall >= 0.95 and schema_accuracy >= 0.80
    print(f"\nGate Result: {'PASS' if gate_pass else 'FAIL'} (SHOULD_WORK)")

    if gate_pass:
        print("✓ Mechanism validated: dependency-aware migration planning works")
    else:
        print("✗ Mechanism failed validation criteria")

    print("\n" + "=" * 60)
    print("Experiment complete.")
    print("=" * 60)

    return {
        'impact_completeness': recall,
        'schema_accuracy': schema_accuracy,
        'gate_result': 'PASS' if gate_pass else 'FAIL'
    }

if __name__ == '__main__':
    results = run_experiment()
    sys.exit(0 if results['gate_result'] == 'PASS' else 1)
