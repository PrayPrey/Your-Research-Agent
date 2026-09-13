"""Main orchestration script for H-M1 n-gram overlap detection."""

import os
import json
import sys
from datetime import datetime

from config import (
    NGRAM_SIZE, PILE_SUBSET_DOCS, PILE_DATASET,
    OUTPUT_DIR, INDEX_PATH, RESULTS_JSON, FIGURES_DIR, OVERLAP_THRESHOLD
)
from ngram_utils import extract_ngram_hashes, tokenize, extract_ngrams
from pile_indexer import PileIndexer
from benchmark_loader import load_all_benchmarks
from overlap_detector import OverlapDetector
from aggregator import aggregate_all, check_gate
from visualize import plot_overlap_by_benchmark, plot_overlap_histogram, plot_comparison_with_prior_work


def verify_mechanism() -> bool:
    """PRD verification: confirm mechanism detects known overlap."""
    print("Running mechanism verification...")
    # 20 words needed for 13-gram extraction (13 + 7 for overlap test)
    base = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
    training_text = base + " extra words here"
    test_text = base

    training_hashes = extract_ngram_hashes(training_text, n=13)
    detector = OverlapDetector(training_hashes, ngram_size=13)
    result = detector.compute_item_overlap(test_text)

    assert result["overlap"] > 0, "Mechanism failed: no overlap detected for known match"
    print(f"✓ Mechanism verified: {result['overlap']:.2%} overlap detected")
    return True


def main():
    """Run full n-gram overlap detection pipeline."""
    print("=" * 60)
    print("H-M1: 13-gram Overlap Detection")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    verify_mechanism()

    print("\n[1/5] Building Pile n-gram index...")
    indexer = PileIndexer(ngram_size=NGRAM_SIZE)

    if os.path.exists(INDEX_PATH):
        print(f"Loading existing index from {INDEX_PATH}")
        indexer.load(INDEX_PATH)
        print(f"Loaded {len(indexer.index):,} unique ngram hashes")
    else:
        print(f"Streaming Pile dataset: {PILE_DATASET}")
        print(f"Processing {PILE_SUBSET_DOCS:,} documents...")
        try:
            from datasets import load_dataset
            pile = load_dataset(PILE_DATASET, split="train", streaming=True)
            doc_iter = (item["text"] for item in pile)
            indexer.build_from_stream(doc_iter, max_docs=PILE_SUBSET_DOCS)
            indexer.save(INDEX_PATH)
            print(f"Saved index with {len(indexer.index):,} unique ngram hashes")
        except Exception as e:
            print(f"Warning: Could not load Pile dataset: {e}")
            print("Using empty index for demonstration")

    print("\n[2/5] Loading benchmark test sets...")
    benchmarks = load_all_benchmarks()
    for name, items in benchmarks.items():
        print(f"  {name}: {len(items)} items")

    print("\n[3/5] Computing overlap...")
    detector = OverlapDetector(indexer.index, ngram_size=NGRAM_SIZE)
    results_by_benchmark = {}
    for name, items in benchmarks.items():
        print(f"  Processing {name}...")
        results_by_benchmark[name] = detector.compute_benchmark_overlap(items)

    print("\n[4/5] Aggregating results...")
    aggregated = aggregate_all(results_by_benchmark)
    gate_result = check_gate(aggregated, threshold=OVERLAP_THRESHOLD)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, stats in aggregated.items():
        print(f"\n{name}:")
        print(f"  Mean overlap:    {stats['mean_overlap']*100:.4f}%")
        print(f"  Median overlap:  {stats['median_overlap']*100:.4f}%")
        print(f"  Max overlap:     {stats['max_overlap']*100:.4f}%")
        print(f"  Items > 1%:      {stats['items_above_1pct']}/{stats['total_items']}")

    print("\n" + "-" * 60)
    print(f"GATE RESULT: {'PASS' if gate_result['pass'] else 'FAIL'}")
    print(f"Benchmarks above {OVERLAP_THRESHOLD*100}%: {gate_result['benchmarks_above_threshold']}")
    print(f"Highest overlap: {gate_result['max_overlap_benchmark']}")
    print("-" * 60)

    print("\n[5/5] Generating figures...")
    plot_overlap_by_benchmark(aggregated, os.path.join(FIGURES_DIR, "overlap_by_benchmark.png"))
    plot_overlap_histogram(results_by_benchmark, os.path.join(FIGURES_DIR, "overlap_histograms.png"))
    plot_comparison_with_prior_work(aggregated, os.path.join(FIGURES_DIR, "comparison_prior_work.png"))
    print("  Saved: overlap_by_benchmark.png, overlap_histograms.png, comparison_prior_work.png")

    results = {
        "hypothesis_id": "h-m1",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "ngram_size": NGRAM_SIZE,
            "pile_subset_docs": PILE_SUBSET_DOCS,
            "overlap_threshold": OVERLAP_THRESHOLD,
        },
        "pile_index_size": len(indexer.index),
        "aggregated": aggregated,
        "gate_result": gate_result,
    }

    with open(RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_JSON}")

    print("\n" + "=" * 60)
    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 60)

    return gate_result["pass"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
