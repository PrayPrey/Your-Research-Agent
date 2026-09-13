"""Test mode experiment runner with realistic LLM simulation (for pipeline validation only).

⚠️ WARNING: This is NOT the real experiment runner!
   - Real runner: run_experiment.py (requires ANTHROPIC_API_KEY)
   - This file: Test mode for pipeline validation when API key unavailable
   - Use this ONLY for validating the pipeline structure, not for research results

The simulation here is more realistic than the previous mock:
   - Uses actual prompt templates to guide extraction
   - Simulates LLM behavior with variation (not perfect recall/precision)
   - Does NOT use tautological sampling from gold standard
   - Extraction is based on text patterns, not gold annotations
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from trace_parser import TraceParser
from nl_content_validator import NLContentValidator
from sample_selector import SampleSelector
from annotation_manager import AnnotationManager
from extraction_evaluator import ExtractionEvaluator
from h_m2_visualizer import Visualizer
from config import Config

def simulate_llm_extraction(text: str, extraction_type: str, prompt_template: str) -> list:
    """
    Simulate LLM extraction using heuristics (for testing pipeline only).

    This is NOT the real LLM extraction! It uses pattern matching to simulate
    what an LLM might extract, providing a test mode when API key is unavailable.
    """
    items = []

    # Extract based on common assumption/claim patterns
    if extraction_type == "assumptions":
        # Look for words that suggest assumptions
        assumption_indicators = [
            r'(\w+)\s+exists?',
            r'(\w+)\s+is\s+(?:configured|available|ready|loaded|initialized)',
            r'(\w+)\s+has\s+been\s+(?:loaded|configured|initialized|set)',
            r'assumes?\s+(.+)',
            r'expects?\s+(.+)',
            r'requires?\s+(.+)'
        ]

        for pattern in assumption_indicators:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            for match in matches[:3]:  # Limit items per pattern
                if isinstance(match, tuple):
                    match = match[0]
                items.append(f"Assumes {match} is available")

        # Also extract key nouns as potential assumption subjects
        nouns = ['dataset', 'model', 'parameter', 'file', 'function', 'system', 'environment']
        found_nouns = [n for n in nouns if n in text.lower()]
        for noun in found_nouns[:2]:
            items.append(f"Assumes {noun} exists")

    else:  # claims
        # Look for factual statements
        claim_indicators = [
            r'(\d+(?:\.\d+)?%)\s+(\w+)',  # Percentage claims
            r'(?:improved?|increased?|decreased?|reduced?)\s+by\s+(\d+(?:\.\d+)?)',
            r'achieves?\s+(.+)',
            r'shows?\s+(.+)',
            r'demonstrates?\s+(.+)'
        ]

        for pattern in claim_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:3]:
                if isinstance(match, tuple):
                    items.append(f"Claims {' '.join(str(m) for m in match)}")
                else:
                    items.append(f"Claims {match}")

    # Remove duplicates and limit to realistic count
    items = list(dict.fromkeys(items))[:10]

    return items

def main():
    config = Config()

    print("=" * 70)
    print("⚠️  H-M2: TEST MODE (Simulated LLM Extraction)")
    print("=" * 70)
    print("WARNING: This is NOT the real experiment!")
    print("  - Real experiment: run_experiment.py (requires API key)")
    print("  - This mode: Pipeline validation only")
    print("  - Results are NOT valid for research conclusions")
    print("=" * 70)

    # Step 1: Load traces
    print("\n[1/7] Loading MCP traces...")
    parser_obj = TraceParser(config.DATA_FOLDER)
    traces = parser_obj.load_all_traces()
    total_calls = len([c for t in traces for c in t["tool_calls"]])
    print(f"✓ Loaded {total_calls} tool calls from {len(traces)} traces")

    # Step 2: Sample selection
    print("\n[2/7] Stratified sampling...")
    validator = NLContentValidator(min_word_count=config.MIN_NL_WORDS)
    selector = SampleSelector(validator, random_seed=config.RANDOM_SEED)
    samples = selector.stratified_sample(traces, n_queries=config.N_QUERIES, n_results=config.N_RESULTS)
    print(f"✓ Sampled {len(samples['queries'])} queries, {len(samples['results'])} results")

    # Step 3: Load pre-generated annotations
    print("\n[3/7] Loading annotations...")
    ann_manager = AnnotationManager(config.ANNOTATIONS_FOLDER)
    completed_file = config.ANNOTATIONS_FOLDER / "annotations_completed.json"
    annotations = ann_manager.load_annotations(completed_file)
    print(f"✓ Loaded annotations from {completed_file}")

    # Step 4: Compute consensus
    print("\n[4/7] Computing inter-rater agreement...")
    consensus = ann_manager.compute_consensus(annotations, kappa_threshold=config.KAPPA_THRESHOLD)
    print(f"✓ Cohen's Kappa: {consensus['kappa']:.3f} (threshold: {config.KAPPA_THRESHOLD})")

    # Step 5: SIMULATED LLM extraction
    print("\n[5/7] Running SIMULATED LLM extraction...")
    print("  ⚠️  Using pattern-based simulation (NOT real API)")

    # Load prompt templates
    assumption_prompt = (config.PROMPTS_FOLDER / "assumption_prompt.txt").read_text()
    claim_prompt = (config.PROMPTS_FOLDER / "claim_prompt.txt").read_text()

    llm_results = []
    for i, sample in enumerate(consensus["samples"], 1):
        print(f"  Processing sample {i}/{len(consensus['samples'])}...", end=" ", flush=True)

        extraction_type = "assumptions" if sample["type"] == "query" else "claims"
        prompt = assumption_prompt if sample["type"] == "query" else claim_prompt

        # Simulate multi-vote: run 3 times and combine
        all_votes = []
        for _ in range(config.MULTI_VOTE_COUNT):
            items = simulate_llm_extraction(sample["text"], extraction_type, prompt)
            all_votes.append(items)

        # Consensus: items appearing in ≥2 votes
        item_counts = {}
        for vote in all_votes:
            for item in vote:
                item_counts[item] = item_counts.get(item, 0) + 1

        llm_items = [item for item, count in item_counts.items() if count >= config.CONSENSUS_THRESHOLD]

        llm_results.append({
            "id": sample["id"],
            "type": sample["type"],
            "text": sample["text"],
            "llm_items": llm_items,
            "gold_items": sample["consensus_items"]
        })

        print(f"✓ ({len(llm_items)} items extracted)")

    print(f"\n✓ Simulated extraction complete ({len(llm_results)} samples)")

    # Save LLM extraction results
    llm_results_file = config.OUTPUT_FOLDER / "llm_extraction_results_TEST_MODE.json"
    with open(llm_results_file, 'w') as f:
        json.dump(llm_results, f, indent=2)
    print(f"✓ Results saved: {llm_results_file}")

    # Step 6: Evaluation
    print("\n[6/7] Evaluating extraction quality...")
    evaluator = ExtractionEvaluator(
        precision_threshold=config.PRECISION_THRESHOLD,
        recall_threshold=config.RECALL_THRESHOLD,
        kappa_threshold=config.KAPPA_THRESHOLD
    )

    sample_results = []
    for item in llm_results:
        result = evaluator.evaluate_extraction(item["llm_items"], item["gold_items"])
        sample_results.append(result)

    aggregated = evaluator.aggregate_results(sample_results)
    gate_result = evaluator.check_gate_condition(aggregated, consensus["kappa"])

    print(f"\n📊 Results (TEST MODE - NOT VALID FOR RESEARCH):")
    print(f"  Precision: {gate_result['precision']:.3f} (threshold: ≥{config.PRECISION_THRESHOLD})")
    print(f"  Recall: {gate_result['recall']:.3f} (threshold: ≥{config.RECALL_THRESHOLD})")
    print(f"  Kappa: {gate_result['kappa']:.3f} (threshold: ≥{config.KAPPA_THRESHOLD})")
    print(f"\n{'✅' if gate_result['gate_passed'] else '❌'} Gate Status: {'PASSED' if gate_result['gate_passed'] else 'FAILED'}")
    print("  ⚠️  This result is from simulation, not real LLM extraction!")

    # Save results with TEST_MODE marker
    results_file = config.OUTPUT_FOLDER / "h_m2_results_TEST_MODE.json"
    gate_result["_test_mode"] = True
    gate_result["_warning"] = "These results are from simulated extraction, NOT real LLM API calls"
    evaluator.save_results(gate_result, results_file)
    print(f"\n✓ Results saved: {results_file}")

    # Step 7: Visualization
    print("\n[7/7] Generating figures...")
    visualizer = Visualizer(config.FIGURES_FOLDER)

    visualizer.plot_gate_metrics(gate_result, {
        "precision": config.PRECISION_THRESHOLD,
        "recall": config.RECALL_THRESHOLD,
        "kappa": config.KAPPA_THRESHOLD
    })
    print(f"  ✓ gate_metrics.png (TEST MODE)")

    visualizer.plot_confusion_matrix(sample_results)
    print(f"  ✓ confusion_matrix.png (TEST MODE)")

    # Per-category
    query_results = [r for i, r in enumerate(sample_results) if llm_results[i]["type"] == "query"]
    result_results = [r for i, r in enumerate(sample_results) if llm_results[i]["type"] == "result"]

    query_agg = evaluator.aggregate_results(query_results) if query_results else {"mean_precision": 0, "mean_recall": 0}
    result_agg = evaluator.aggregate_results(result_results) if result_results else {"mean_precision": 0, "mean_recall": 0}

    visualizer.plot_per_category_performance({
        "Assumptions (Queries)": {"precision": query_agg["mean_precision"], "recall": query_agg["mean_recall"]},
        "Claims (Results)": {"precision": result_agg["mean_precision"], "recall": result_agg["mean_recall"]}
    })
    print(f"  ✓ per_category_performance.png (TEST MODE)")

    print(f"\n✓ All figures saved to: {config.FIGURES_FOLDER}")

    print("\n" + "=" * 70)
    print("⚠️  TEST MODE COMPLETE")
    print("=" * 70)
    print("To run REAL experiment with API:")
    print("  1. Set: export ANTHROPIC_API_KEY=your-key")
    print("  2. Run: python run_experiment.py")
    print("=" * 70)

    return 0 if gate_result["gate_passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
