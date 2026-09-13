#!/usr/bin/env python
"""Run H-E1 experiment with configurable data path."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from train import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Benchmark Fingerprint Detection")
    parser.add_argument("--data_root", type=str, default="./data",
                        help="Root directory containing datasets")
    parser.add_argument("--epochs", type=int, default=30,
                        help="Number of fine-tuning epochs")
    parser.add_argument("--batch_size", type=int, default=32,
                        help="Batch size for training")
    parser.add_argument("--output_dir", type=str, default=".",
                        help="Output directory for results")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    cfg = Config(
        data_root=args.data_root,
        epochs=args.epochs,
        batch_size=args.batch_size,
        ckpt_dir=str(output_dir / "models" / "finetuned"),
        feature_dir=str(output_dir / "features"),
        results_path=str(output_dir / "results" / "h_e1_results.json"),
        figure_path=str(output_dir / "figures" / "confusion_matrix.png"),
    )

    results = main(cfg)
    sys.exit(0 if results["probe"]["test_acc"] > 0.60 else 1)
