#!/usr/bin/env python3
"""
Main entry point for h-e1 CCP domain degradation experiment.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from main.experiment import CCPExperiment
from config import CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG['output']['log']),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Run the experiment."""
    try:
        # Create experiment
        experiment = CCPExperiment(CONFIG)

        # Run experiment
        results = experiment.run()

        # Print summary
        print("\n" + "=" * 80)
        print("EXPERIMENT SUMMARY")
        print("=" * 80)
        print(f"ρ_j (factual):     {results['rho_j_factual']:.4f}")
        print(f"ρ_j (creative):    {results['rho_j_creative']:.4f}")
        print(f"Δρ_j:              {results['delta_rho_j']:.4f}")
        print(f"p-value:           {results['p_value']:.4f}")
        print(f"Gate satisfied:    {results['gate_satisfied']}")
        print("=" * 80)

        # Exit with appropriate code
        sys.exit(0 if results['gate_satisfied'] else 1)

    except Exception as e:
        logger.error(f"Experiment failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
