"""Main entry point for H-E2 taxonomy construction experiment."""

import yaml
import sys
from pathlib import Path

from src.taxonomy_builder import TaxonomyBuilder


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Execute H-E2 taxonomy construction experiment."""
    # Load configuration
    config = load_config("config.yaml")

    # Initialize taxonomy builder
    builder = TaxonomyBuilder(config)

    # Run full pipeline
    metrics = builder.run_pipeline()

    # Exit with appropriate code
    if metrics.gate_passed:
        print("\n✓ Experiment SUCCESS: Hypothesis H-E2 validated")
        print(f"  Coverage {metrics.aggregate_coverage:.1f}% ≥ {config['evaluation']['coverage_target'] * 100:.0f}%")
        sys.exit(0)
    else:
        print("\n✗ Experiment FAILURE: Hypothesis H-E2 not validated")
        print(f"  Coverage {metrics.aggregate_coverage:.1f}% < {config['evaluation']['coverage_target'] * 100:.0f}%")
        sys.exit(1)


if __name__ == "__main__":
    main()
