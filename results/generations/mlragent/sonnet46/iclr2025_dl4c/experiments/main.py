"""
Main entry point for HierAlign experiment.
Runs experiment then visualizes results.
"""
import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
LOG_FILE = RESULTS_DIR / "log.txt"


def setup_logging():
    RESULTS_DIR.mkdir(exist_ok=True)
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='w'),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True,
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("HierAlign: Execution-Guided RL with Hierarchical Feedback")
    logger.info("Experiment Pipeline Start")
    logger.info("=" * 70)

    # Step 1: Run experiments
    logger.info("\n--- Phase 1: Running Experiments ---")
    from run_experiment import main as run_exp
    results = run_exp()

    # Step 2: Generate visualizations
    logger.info("\n--- Phase 2: Generating Visualizations ---")
    from visualize import generate_all_figures
    figures = generate_all_figures()

    logger.info("\n--- Experiment Complete ---")
    logger.info(f"Results: {BASE_DIR}/results/")
    logger.info(f"Figures: {BASE_DIR}/results/figures/")
    logger.info(f"Log: {LOG_FILE}")


if __name__ == "__main__":
    main()
