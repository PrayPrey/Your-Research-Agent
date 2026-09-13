"""Real experiment runner with actual LLM API calls (NO MOCK DATA)."""
import sys
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from trace_parser import TraceParser
from nl_content_validator import NLContentValidator
from sample_selector import SampleSelector
from llm_extractor import LLMExtractor
from annotation_manager import AnnotationManager
from extraction_evaluator import ExtractionEvaluator
from h_m2_visualizer import Visualizer
from config import Config

def main():
    config = Config()

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it before running the experiment:")
        print("  export ANTHROPIC_API_KEY=your-api-key")
        return 1

    print("=" * 70)
    print("H-M2: Semantic NLP Extraction Validation (REAL LLM API)")
    print("=" * 70)
    print(f"Model: {config.LLM_MODEL}")
    print(f"Temperature: {config.LLM_TEMPERATURE}")
    print(f"Multi-vote count: {config.MULTI_VOTE_COUNT}")

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

    if not completed_file.exists():
        print(f"ERROR: Annotations file not found: {completed_file}")
        print("Please ensure human annotations are completed before running experiment")
        return 1

    annotations = ann_manager.load_annotations(completed_file)
    print(f"✓ Loaded annotations from {completed_file}")

    # Step 4: Compute consensus
    print("\n[4/7] Computing inter-rater agreement...")
    consensus = ann_manager.compute_consensus(annotations, kappa_threshold=config.KAPPA_THRESHOLD)
    print(f"✓ Cohen's Kappa: {consensus['kappa']:.3f} (threshold: {config.KAPPA_THRESHOLD})")

    if consensus['kappa'] < config.KAPPA_THRESHOLD:
        print(f"ERROR: Inter-rater agreement too low ({consensus['kappa']:.3f} < {config.KAPPA_THRESHOLD})")
        print("Please re-annotate with clearer guidelines")
        return 1

    # Step 5: REAL LLM extraction (NOT MOCK!)
    print("\n[5/7] Running REAL LLM extraction...")
    print("  ⚠️  This will make actual API calls to Anthropic")
    print(f"  Estimated cost: ~{config.SAMPLE_SIZE * config.MULTI_VOTE_COUNT * 0.02:.2f} USD")

    extractor = LLMExtractor(
        model_name=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        api_key=api_key
    )

    # Load prompt templates
    assumption_prompt_file = config.PROMPTS_FOLDER / "assumption_prompt.txt"
    claim_prompt_file = config.PROMPTS_FOLDER / "claim_prompt.txt"

    if not assumption_prompt_file.exists() or not claim_prompt_file.exists():
        print(f"ERROR: Prompt templates not found")
        print(f"  Expected: {assumption_prompt_file}")
        print(f"  Expected: {claim_prompt_file}")
        return 1

    assumption_prompt = assumption_prompt_file.read_text()
    claim_prompt = claim_prompt_file.read_text()

    llm_results = []
    for i, sample in enumerate(consensus["samples"], 1):
        print(f"  Processing sample {i}/{len(consensus['samples'])}...", end=" ", flush=True)

        if sample["type"] == "query":
            llm_items = extractor.multi_vote_extract(
                sample["text"],
                assumption_prompt,
                "assumptions",
                n_votes=config.MULTI_VOTE_COUNT,
                consensus_threshold=config.CONSENSUS_THRESHOLD
            )
        else:
            llm_items = extractor.multi_vote_extract(
                sample["text"],
                claim_prompt,
                "claims",
                n_votes=config.MULTI_VOTE_COUNT,
                consensus_threshold=config.CONSENSUS_THRESHOLD
            )

        llm_results.append({
            "id": sample["id"],
            "type": sample["type"],
            "text": sample["text"],
            "llm_items": llm_items,
            "gold_items": sample["consensus_items"]
        })

        print(f"✓ ({len(llm_items)} items extracted)")

    print(f"\n✓ LLM extraction complete ({len(llm_results)} samples)")

    # Save LLM extraction results
    llm_results_file = config.OUTPUT_FOLDER / "llm_extraction_results.json"
    with open(llm_results_file, 'w') as f:
        json.dump(llm_results, f, indent=2)
    print(f"✓ LLM results saved: {llm_results_file}")

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

    print(f"\n📊 Results:")
    print(f"  Precision: {gate_result['precision']:.3f} (threshold: ≥{config.PRECISION_THRESHOLD})")
    print(f"  Recall: {gate_result['recall']:.3f} (threshold: ≥{config.RECALL_THRESHOLD})")
    print(f"  Kappa: {gate_result['kappa']:.3f} (threshold: ≥{config.KAPPA_THRESHOLD})")
    print(f"\n{'✅' if gate_result['gate_passed'] else '❌'} Gate Status: {'PASSED' if gate_result['gate_passed'] else 'FAILED'}")

    # Save results
    results_file = config.OUTPUT_FOLDER / "h_m2_results.json"
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
    print(f"  ✓ gate_metrics.png")

    visualizer.plot_confusion_matrix(sample_results)
    print(f"  ✓ confusion_matrix.png")

    # Per-category (split by type)
    query_results = [r for i, r in enumerate(sample_results) if llm_results[i]["type"] == "query"]
    result_results = [r for i, r in enumerate(sample_results) if llm_results[i]["type"] == "result"]

    query_agg = evaluator.aggregate_results(query_results) if query_results else {"mean_precision": 0, "mean_recall": 0}
    result_agg = evaluator.aggregate_results(result_results) if result_results else {"mean_precision": 0, "mean_recall": 0}

    visualizer.plot_per_category_performance({
        "Assumptions (Queries)": {"precision": query_agg["mean_precision"], "recall": query_agg["mean_recall"]},
        "Claims (Results)": {"precision": result_agg["mean_precision"], "recall": result_agg["mean_recall"]}
    })
    print(f"  ✓ per_category_performance.png")

    print(f"\n✓ All figures saved to: {config.FIGURES_FOLDER}")

    print("\n" + "=" * 70)
    print("H-M2 Experiment Complete")
    print("=" * 70)

    return 0 if gate_result["gate_passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
