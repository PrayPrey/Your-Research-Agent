"""Main validation script for h-c1 pre-conditions."""
import sys
from pathlib import Path

# Add module paths
code_dir = Path(__file__).parent
sys.path.insert(0, str(code_dir / "data"))
sys.path.insert(0, str(code_dir / "validation"))
sys.path.insert(0, str(code_dir / "reporting"))

from loader import TruthfulQALoader
from ner_validator import NERValidator
from wikipedia_checker import WikipediaChecker
from gate_evaluator import GateEvaluator
from reporter import Reporter


def main():
    """Execute h-c1 validation experiment."""
    print("=" * 80)
    print("h-c1 Pre-Condition Validation")
    print("=" * 80)
    print()

    # Step 1: Load data
    print("[1/5] Loading TruthfulQA entity subset...")
    loader = TruthfulQALoader()
    samples, entities = loader.load_entity_subset()
    print(f"  ✓ Loaded {len(samples)} samples, {len(entities)} entities")
    print()

    # Step 2: NER validation
    print("[2/5] Validating NER accuracy...")
    ner_validator = NERValidator()
    ner_result = ner_validator.validate(samples)
    print(f"  ✓ NER F1: {ner_result['ents_f']:.3f}")
    print(f"    Precision: {ner_result['ents_p']:.3f}, Recall: {ner_result['ents_r']:.3f}")
    print()

    # Step 3: Wikipedia coverage
    print("[3/5] Checking Wikipedia coverage...")
    wiki_checker = WikipediaChecker()
    wiki_result = wiki_checker.check_coverage(entities)
    print(f"  ✓ Coverage: {wiki_result['coverage']:.3f}")
    print(f"    Covered: {wiki_result['covered_count']}/{wiki_result['total_count']}")
    print()

    # Step 4: Gate evaluation
    print("[4/5] Evaluating MUST_WORK gate...")
    gate_evaluator = GateEvaluator()
    gate_result = gate_evaluator.evaluate(
        ner_result["ents_f"],
        wiki_result["coverage"]
    )
    print(f"  {gate_result['message']}")
    print(f"  Gate Status: {gate_result['status']}")
    print()

    # Step 5: Generate report
    print("[5/5] Generating validation report...")
    reporter = Reporter(output_dir=str(code_dir / "figures"))
    reporter.generate_report(gate_result, ner_result, wiki_result, samples)
    print(f"  ✓ Report: {code_dir.parent / '04_validation.md'}")
    print(f"  ✓ Figures: {code_dir / 'figures'}/*.png")
    print()

    # Final result
    print("=" * 80)
    if gate_result["status"] == "PASS":
        print("✅ VALIDATION PASSED — Pre-conditions satisfied")
        print("   Downstream hypotheses (h-e1, h-m1, h-m2) can proceed.")
        exit_code = 0
    else:
        print("❌ VALIDATION FAILED — Pre-conditions NOT satisfied")
        print("   Downstream hypotheses (h-e1, h-m1, h-m2) are BLOCKED.")
        exit_code = 1

    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
