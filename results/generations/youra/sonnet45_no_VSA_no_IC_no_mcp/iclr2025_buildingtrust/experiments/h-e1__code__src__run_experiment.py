"""Main experiment runner for h-e1."""
import json
import csv
import sys
import os
import spacy
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from src.attention_extractor import AttentionExtractor
from src.span_mapper import SpanMapper
from src.entropy_calculator import EntropyCalculator
from src.statistical_tester import StatisticalTester
from src.visualizer import plot_violin, plot_histograms


class AttentionEntropyExperiment:
    """Run full h-e1 experiment."""

    def __init__(self):
        print("[1/5] Initializing components...")
        self.extractor = AttentionExtractor(
            CONFIG["model"]["name"],
            device_map=CONFIG["model"]["device_map"]
        )
        self.mapper = SpanMapper(self.extractor.tokenizer)
        self.calculator = EntropyCalculator(epsilon=CONFIG["entropy"]["epsilon"])
        self.tester = StatisticalTester()

        print("Loading NER model...")
        self.ner = spacy.load(CONFIG["ner"]["model_name"])
        print("NER model loaded.")

    def load_data(self):
        """Load entity and non-entity error samples from h-c1."""
        print("\n[2/5] Loading dataset from h-c1...")

        with open(CONFIG["data"]["entity_errors_path"]) as f:
            entity_samples = json.load(f)

        with open(CONFIG["data"]["non_entity_errors_path"]) as f:
            non_entity_samples = json.load(f)

        dataset = []
        for sample in entity_samples[:CONFIG["data"]["entity_error_samples"]]:
            dataset.append({
                "question": sample["question"],
                "error_type": "entity",
                "entities": sample.get("entities", [])
            })

        for sample in non_entity_samples[:CONFIG["data"]["non_entity_error_samples"]]:
            dataset.append({
                "question": sample["question"],
                "error_type": "non-entity",
                "entities": sample.get("entities", [])
            })

        print(f"Loaded {len(dataset)} samples ({len(entity_samples[:50])} entity + {len(non_entity_samples[:50])} non-entity)")
        return dataset

    def run(self):
        """Execute full experiment."""
        dataset = self.load_data()

        print("\n[3/5] Extracting attention and calculating entropy...")
        entity_entropies = []
        non_entity_entropies = []
        skipped = 0
        all_scores = []

        for i, sample in enumerate(dataset):
            try:
                # Extract entity span from h-c1 annotations (or NER fallback)
                if "entities" in sample and len(sample["entities"]) > 0:
                    # h-c1 format: entities = [[start, end, type], ...]
                    entity_data = sample["entities"][0]
                    entity_char_span = (entity_data[0], entity_data[1])
                else:
                    # Fallback to NER
                    doc = self.ner(sample["question"])
                    if not doc.ents:
                        skipped += 1
                        continue
                    entity_char_span = (doc.ents[0].start_char, doc.ents[0].end_char)

                # Extract attention
                attn = self.extractor.extract(sample["question"])

                # Map span to tokens
                entity_token_span = self.mapper.char_to_token_span(
                    sample["question"], entity_char_span
                )

                # Calculate entropy
                entropy = self.calculator.calculate(attn, entity_token_span)

                # Store result
                all_scores.append({
                    "sample_id": i,
                    "question": sample["question"][:50],
                    "error_type": sample["error_type"],
                    "entropy": entropy
                })

                if sample["error_type"] == "entity":
                    entity_entropies.append(entropy)
                else:
                    non_entity_entropies.append(entropy)

                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(dataset)} samples...")

            except Exception as e:
                print(f"Skipped sample {i}: {e}")
                skipped += 1

        print(f"Processed {len(dataset) - skipped}/{len(dataset)} samples ({skipped} skipped)")

        # Statistical test
        print("\n[4/5] Running statistical test...")
        results = self.tester.compare(entity_entropies, non_entity_entropies)
        print(f"Entity mean: {results['mean_entity']:.4f}")
        print(f"Non-entity mean: {results['mean_non_entity']:.4f}")
        print(f"p-value: {results['p_value']:.4f}")
        print(f"Cohen's d: {results['cohens_d']:.4f}")

        # Save results
        print("\n[5/5] Saving results...")
        Path(CONFIG["output"]["figures_dir"]).mkdir(parents=True, exist_ok=True)
        Path(CONFIG["output"]["results_file"]).parent.mkdir(parents=True, exist_ok=True)

        # Figures
        plot_violin(
            entity_entropies, non_entity_entropies,
            results["p_value"],
            f"{CONFIG['output']['figures_dir']}/entropy_violin.png"
        )
        plot_histograms(
            entity_entropies, non_entity_entropies,
            f"{CONFIG['output']['figures_dir']}/entropy_histograms.png"
        )

        # JSON results
        results_out = {
            **results,
            "entity_entropies": entity_entropies,
            "non_entity_entropies": non_entity_entropies,
            "n_entity": len(entity_entropies),
            "n_non_entity": len(non_entity_entropies),
            "n_skipped": skipped
        }
        with open(CONFIG["output"]["results_file"], "w") as f:
            json.dump(results_out, f, indent=2)

        # CSV scores
        with open(CONFIG["output"]["scores_file"], "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["sample_id", "question", "error_type", "entropy"])
            writer.writeheader()
            writer.writerows(all_scores)

        print(f"Results saved to {CONFIG['output']['results_file']}")
        print(f"Figures saved to {CONFIG['output']['figures_dir']}")

        # Gate evaluation
        gate_pass = results["pass"]
        print(f"\n{'='*60}")
        print(f"GATE EVALUATION (MUST_WORK): {'PASS' if gate_pass else 'FAIL'}")
        print(f"{'='*60}")

        return results_out


def main():
    experiment = AttentionEntropyExperiment()
    results = experiment.run()

    # Exit code based on gate
    sys.exit(0 if results["pass"] else 1)


if __name__ == "__main__":
    main()
