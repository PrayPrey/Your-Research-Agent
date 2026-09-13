"""Model generation script for H-E1 experiment.

Generates model outputs with logits extraction.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_loader import load_jsonl
from model_engine import ModelEngine, save_generated_outputs


def main():
    """Execute generation pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--test-data',
        type=str,
        default='./data/halueval/processed/test.jsonl',
        help='Path to test data'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=8,
        help='Batch size for generation'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./data/halueval/generated_outputs.pkl',
        help='Output path for generated outputs'
    )
    parser.add_argument(
        '--checkpoint',
        type=str,
        default='./data/halueval/generation_checkpoint.pkl',
        help='Checkpoint path for resume capability'
    )
    parser.add_argument(
        '--use-gpt2',
        action='store_true',
        help='Use GPT-2 instead of LLaMA-2 (no auth required)'
    )
    args = parser.parse_args()

    print("=" * 80)
    print("H-E1: Model Generation")
    print("=" * 80)

    # Load test data
    print(f"Loading test data from {args.test_data}")
    test_samples = load_jsonl(args.test_data)
    print(f"Loaded {len(test_samples)} test samples")

    # Initialize model engine
    if args.use_gpt2:
        print("Using GPT-2 model (fallback)")
        model_name = "gpt2"
        cache_dir = "./models/gpt2"
    else:
        print("Using LLaMA-2-7B model")
        model_name = "meta-llama/Llama-2-7b-hf"
        cache_dir = "./models/llama-2-7b-hf"

    engine = ModelEngine(
        model_name=model_name,
        cache_dir=cache_dir,
        seed=42
    )

    # Generate outputs
    print(f"Generating outputs (batch_size={args.batch_size})")
    results = engine.process_dataset(
        test_samples,
        batch_size=args.batch_size,
        checkpoint_path=args.checkpoint
    )

    # Save results
    save_generated_outputs(results, args.output)

    print("\n" + "=" * 80)
    print("Generation complete!")
    print("=" * 80)
    print(f"Generated {len(results)} outputs")
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
