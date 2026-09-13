"""Main orchestration for H-M1 Attention Entropy Analysis."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AnalysisConfig
from data import get_long_documents
from model import load_model_and_tokenizer
from analysis import run_analysis, compute_gate_metrics, save_results
from visualize import generate_all_figures

def main():
    print("=" * 60)
    print("H-M1: Phi-1.5 Attention Entropy Analysis")
    print("=" * 60)

    config = AnalysisConfig()
    print(f"Config: {config.num_samples} samples, lengths {config.target_lengths}")

    model, tokenizer = load_model_and_tokenizer(config)

    documents = get_long_documents(config, tokenizer)
    if len(documents) < config.num_samples:
        print(f"Warning: Only found {len(documents)} documents, expected {config.num_samples}")

    print("\nRunning attention entropy analysis...")
    results = run_analysis(config, model, tokenizer, documents)

    print("\nComputing gate metrics...")
    gate_metrics = compute_gate_metrics(results, config)

    print("\nSaving results...")
    save_results(results, gate_metrics, config)

    print("\nGenerating figures...")
    generate_all_figures(results, config)

    print("\n" + "=" * 60)
    print("GATE RESULT")
    print("=" * 60)
    print(f"Entropy change (2K -> 16K): {gate_metrics['overall_change_pct']*100:.2f}%")
    print(f"Gate threshold: >{gate_metrics['gate_threshold']*100:.1f}%")
    print(f"Gate verdict: {'PASS' if gate_metrics['pass'] else 'FAIL'}")
    print("=" * 60)

    return gate_metrics

if __name__ == "__main__":
    main()
