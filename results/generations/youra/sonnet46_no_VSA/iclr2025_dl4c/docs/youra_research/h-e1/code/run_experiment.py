"""Top-level entry point for H-E1 experiment."""
import sys
import os

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from h_e1.run_experiment import main, parse_args

if __name__ == "__main__":
    args = parse_args()
    main(
        batch_size=args.batch_size,
        device=args.device,
        seed=args.seed,
        figures_dir=args.figures_dir,
        skip_tsne=args.skip_tsne,
        skip_histograms=args.skip_histograms,
        results_json=args.results_json,
    )
