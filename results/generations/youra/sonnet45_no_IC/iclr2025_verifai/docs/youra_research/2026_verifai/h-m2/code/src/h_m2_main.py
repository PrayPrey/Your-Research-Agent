"""Main pipeline for h-m2 extraction validation."""
import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from trace_parser import TraceParser
from nl_content_validator import NLContentValidator
from sample_selector import SampleSelector
from llm_extractor import LLMExtractor
from annotation_manager import AnnotationManager
from extraction_evaluator import ExtractionEvaluator
from h_m2_visualizer import Visualizer

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))
from config import Config

def main():
    parser = argparse.ArgumentParser(description="H-M2 Extraction Validation")
    parser.add_argument("--trace-folder", type=Path, default=Config.DATA_FOLDER)
    parser.add_argument("--output-folder", type=Path, default=Config.OUTPUT_FOLDER)
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM extraction (annotation only)")
    args = parser.parse_args()
    
    config = Config()
    print("=" * 60)
    print("H-M2: Semantic NLP Extraction Validation")
    print("=" * 60)
    
    # Step 1: Load traces
    print("\n[1/7] Loading MCP traces...")
    parser_obj = TraceParser(args.trace_folder)
    traces = parser_obj.load_all_traces()
    print(f"✓ Loaded {len([c for t in traces for c in t['tool_calls']])} tool calls")
    
    # Step 2: Sample selection
    print("\n[2/7] Stratified sampling...")
    validator = NLContentValidator(min_word_count=config.MIN_NL_WORDS)
    selector = SampleSelector(validator, random_seed=config.RANDOM_SEED)
    samples = selector.stratified_sample(traces, n_queries=config.N_QUERIES, n_results=config.N_RESULTS)
    print(f"✓ Sampled {len(samples['queries'])} queries, {len(samples['results'])} results")
    
    # Step 3: Create annotation template
    print("\n[3/7] Creating annotation template...")
    ann_manager = AnnotationManager(config.ANNOTATIONS_FOLDER)
    template_file = config.ANNOTATIONS_FOLDER / "annotation_template.json"
    ann_manager.create_annotation_template(samples, template_file)
    print(f"✓ Template saved: {template_file}")
    print("\n⚠️  MANUAL STEP REQUIRED:")
    print(f"    1. Open {template_file}")
    print(f"    2. Have 2 annotators fill in items")
    print(f"    3. Save as: {config.ANNOTATIONS_FOLDER / 'annotations_completed.json'}")
    print(f"    4. Re-run this script to continue")
    
    # Check if annotations exist
    completed_file = config.ANNOTATIONS_FOLDER / "annotations_completed.json"
    if not completed_file.exists():
        print("\n⏸️  Paused: Waiting for human annotations")
        return 0
    
    # Step 4: Load annotations and compute consensus
    print("\n[4/7] Computing inter-rater agreement...")
    annotations = ann_manager.load_annotations(completed_file)
    consensus = ann_manager.compute_consensus(annotations, kappa_threshold=config.KAPPA_THRESHOLD)
    print(f"✓ Cohen's Kappa: {consensus['kappa']:.3f} (threshold: {config.KAPPA_THRESHOLD})")
    
    # Step 5: LLM extraction (optional)
    if not args.skip_llm:
        print("\n[5/7] Running LLM extraction...")
        extractor = LLMExtractor(
            model_name=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            api_key=args.api_key
        )
        
        assumption_prompt = (config.PROMPTS_FOLDER / "assumption_prompt.txt").read_text()
        claim_prompt = (config.PROMPTS_FOLDER / "claim_prompt.txt").read_text()
        
        llm_results = []
        for sample in consensus["samples"]:
            if sample["type"] == "query":
                llm_items = extractor.multi_vote_extract(
                    sample["text"], assumption_prompt, "assumptions",
                    n_votes=config.MULTI_VOTE_COUNT,
                    consensus_threshold=config.CONSENSUS_THRESHOLD
                )
            else:
                llm_items = extractor.multi_vote_extract(
                    sample["text"], claim_prompt, "claims",
                    n_votes=config.MULTI_VOTE_COUNT,
                    consensus_threshold=config.CONSENSUS_THRESHOLD
                )
            
            llm_results.append({
                "id": sample["id"],
                "llm_items": llm_items,
                "gold_items": sample["consensus_items"]
            })
        
        print(f"✓ LLM extraction complete ({len(llm_results)} samples)")
    else:
        print("\n[5/7] Skipping LLM extraction (--skip-llm)")
        llm_results = []
    
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
    
    print(f"✓ Precision: {gate_result['precision']:.3f} (threshold: {config.PRECISION_THRESHOLD})")
    print(f"✓ Recall: {gate_result['recall']:.3f} (threshold: {config.RECALL_THRESHOLD})")
    print(f"✓ Kappa: {gate_result['kappa']:.3f} (threshold: {config.KAPPA_THRESHOLD})")
    print(f"\n{'✅' if gate_result['gate_passed'] else '❌'} Gate: {'PASSED' if gate_result['gate_passed'] else 'FAILED'}")
    
    # Save results
    results_file = config.OUTPUT_FOLDER / "h_m2_results.json"
    evaluator.save_results(gate_result, results_file)
    print(f"✓ Results saved: {results_file}")
    
    # Step 7: Visualization
    print("\n[7/7] Generating figures...")
    visualizer = Visualizer(config.FIGURES_FOLDER)
    visualizer.plot_gate_metrics(gate_result, {
        "precision": config.PRECISION_THRESHOLD,
        "recall": config.RECALL_THRESHOLD,
        "kappa": config.KAPPA_THRESHOLD
    })
    visualizer.plot_confusion_matrix(sample_results)
    print(f"✓ Figures saved: {config.FIGURES_FOLDER}")
    
    print("\n" + "=" * 60)
    print("H-M2 Experiment Complete")
    print("=" * 60)
    
    return 0 if gate_result["gate_passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
