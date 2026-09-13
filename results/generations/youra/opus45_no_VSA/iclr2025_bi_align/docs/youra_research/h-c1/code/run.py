#!/usr/bin/env python3
"""H-C1: Semantic Coherence Analysis of BAI-Reward Disagreement Slice."""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import hc1_config as config
from slice_loader import load_disagreement_slice
from cluster import AgencyPatternClusterer
from metrics import compute_coverage, compute_silhouette, compute_agency_pattern_rate, verify_mechanism
import evaluate


def main():
    print("=" * 60)
    print("H-C1: Semantic Coherence Analysis")
    print("=" * 60)

    figures_dir = os.path.join(os.path.dirname(__file__), "..", config.FIGURES_DIR)
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    print("\n[1/6] Loading disagreement slice from H-M2...")
    hl_texts, lh_texts = load_disagreement_slice()
    texts = hl_texts + lh_texts
    print(f"Total disagreement samples: {len(texts)}")

    print("\n[2/6] Clustering with BERTopic...")
    clusterer = AgencyPatternClusterer(min_cluster_size=config.MIN_CLUSTER_SIZE)
    topics, probs = clusterer.fit_transform(texts)
    embeddings = clusterer.embeddings

    print("\n[3/6] Computing metrics...")
    coverage = compute_coverage(topics)
    silhouette = compute_silhouette(embeddings, topics)
    agency_result = compute_agency_pattern_rate(clusterer)
    agency_rate = agency_result["agency_pattern_rate"]

    print(f"Coverage: {coverage:.2%}")
    print(f"Silhouette Score: {silhouette:.4f}")
    print(f"Agency Pattern Rate: {agency_rate:.2%}")
    print(f"Agency Clusters: {agency_result['agency_clusters']}/{agency_result['total_clusters']}")

    print("\n[4/6] Verifying mechanism...")
    verification = verify_mechanism(topics, clusterer.topic_embeddings_)
    print(f"Mechanism Verification: {'PASSED' if verification['verification_passed'] else 'FAILED'}")
    for check, result in verification.items():
        if check != "verification_passed":
            print(f"  {check}: {result}")

    print("\n[5/6] Generating figures...")
    evaluate.plot_gate_bar(
        agency_rate,
        os.path.join(figures_dir, "gate_agency_rate.png")
    )
    evaluate.plot_umap_projection(
        embeddings, topics,
        os.path.join(figures_dir, "umap_projection.png")
    )
    evaluate.plot_topic_wordclouds(
        clusterer, 5,
        os.path.join(figures_dir, "topic_wordclouds.png")
    )
    evaluate.plot_cluster_size_histogram(
        topics,
        os.path.join(figures_dir, "cluster_sizes.png")
    )
    evaluate.save_representative_docs_table(
        clusterer, agency_result["agency_topic_ids"],
        os.path.join(figures_dir, "representative_docs.md")
    )

    print("\n[6/6] Determining gate result...")
    if agency_rate >= config.AGENCY_RATE_PASS_THRESHOLD and coverage >= config.COVERAGE_PASS_THRESHOLD:
        gate_result = "PASS"
    elif agency_rate >= config.AGENCY_RATE_PARTIAL_THRESHOLD:
        gate_result = "PARTIAL"
    else:
        gate_result = "FAIL"

    results = {
        "hypothesis_id": "h-c1",
        "timestamp": datetime.now().isoformat(),
        "sample_count": len(texts),
        "hl_count": len(hl_texts),
        "lh_count": len(lh_texts),
        "metrics": {
            "coverage": coverage,
            "silhouette": silhouette,
            "agency_pattern_rate": agency_rate,
            "total_clusters": agency_result["total_clusters"],
            "agency_clusters": agency_result["agency_clusters"],
            "agency_topic_ids": agency_result["agency_topic_ids"],
        },
        "mechanism_verification": verification,
        "gate_result": gate_result,
        "gate_thresholds": {
            "pass": config.AGENCY_RATE_PASS_THRESHOLD,
            "partial": config.AGENCY_RATE_PARTIAL_THRESHOLD,
            "coverage_required": config.COVERAGE_PASS_THRESHOLD,
        },
    }

    results_path = os.path.join(outputs_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved: {results_path}")

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {gate_result}")
    print("=" * 60)

    return gate_result


if __name__ == "__main__":
    result = main()
    print(f"\nExperiment completed with result: {result}")
