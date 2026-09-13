"""Main execution script for H-M1 validation."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trace_parser import TraceParser
from src.nl_content_validator import NLContentValidator
from src.metrics_calculator import MetricsCalculator
from src.evaluator import Evaluator
from src.visualizer import Visualizer
from config.config import Config


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='H-M1: Natural Language Content Validation'
    )

    parser.add_argument(
        '--trace_folder',
        type=str,
        required=True,
        help='Path to folder containing .jsonl trace files'
    )

    parser.add_argument(
        '--output_folder',
        type=str,
        required=True,
        help='Path to hypothesis folder for output'
    )

    return parser.parse_args()


def main() -> int:
    """Main execution function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()

    # Setup configuration
    Config.setup(args.trace_folder, args.output_folder)

    print("=" * 60)
    print("H-M1: NATURAL LANGUAGE CONTENT VALIDATION")
    print("=" * 60)
    print(f"\nTrace folder: {Config.TRACE_FOLDER}")
    print(f"Output folder: {Config.HYPOTHESIS_FOLDER}")
    print(f"Threshold: {Config.NL_THRESHOLD:.2%}")

    try:
        # Step 1: Parse traces
        print("\n📂 Step 1: Loading traces...")
        parser = TraceParser(Config.TRACE_FOLDER)
        traces = parser.load_all_traces()
        print(f"✓ Loaded {len(traces)} trace files")

        # Step 2: Validate NL content
        print("\n✓ Step 2: Validating NL content...")
        validator = NLContentValidator(min_word_count=Config.MIN_WORD_COUNT)
        calculator = MetricsCalculator(validator)

        # Step 3: Evaluate hypothesis
        print("\n📊 Step 3: Evaluating hypothesis...")
        evaluator = Evaluator(calculator, threshold=Config.NL_THRESHOLD)
        results = evaluator.evaluate_hypothesis(traces)

        # Step 4: Generate visualizations
        visualizer = Visualizer(Config.FIGURES_DIR, dpi=Config.FIGURE_DPI)
        visualizer.generate_all_figures(traces, results, validator)

        # Step 5: Save results
        print("\n💾 Step 4: Saving results...")
        evaluator.save_results(results, Config.RESULTS_FILE)

        # Step 6: Print summary
        evaluator.print_summary(results)

        # Return exit code based on gate decision
        if results['gate_passed']:
            return 0
        else:
            return 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
