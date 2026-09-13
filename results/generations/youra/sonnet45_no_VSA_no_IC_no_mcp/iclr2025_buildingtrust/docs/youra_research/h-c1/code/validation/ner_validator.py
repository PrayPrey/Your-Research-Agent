"""NER validation using spaCy scorer."""
import spacy
from spacy.training import Example
from spacy.scorer import Scorer
from typing import List, Dict, Tuple
import sys
sys.path.append("../data")
from loader import EntitySample


class NERValidator:
    """Validate NER accuracy against gold annotations."""

    def __init__(self, model_name: str = "en_core_web_lg"):
        self.nlp = spacy.load(model_name)

    def validate(self, samples: List[EntitySample]) -> Dict[str, float]:
        """
        Evaluate spaCy NER against gold annotations.

        Args:
            samples: Gold-labeled samples

        Returns:
            {
                "ents_f": float,  # F1 score (target metric)
                "ents_p": float,  # Precision
                "ents_r": float   # Recall
            }
        """
        examples = []

        for sample in samples:
            # Skip samples with no gold entities
            if not sample.gold_entities:
                continue

            # Get prediction
            predicted_doc = self.nlp(sample.question)

            # Create reference doc with gold entities
            reference_doc = self.nlp.make_doc(sample.question)

            # Convert entity tuples to dict format
            annotations = {
                "entities": sample.gold_entities
            }

            try:
                example = Example(predicted_doc, reference_doc)
                # Set gold entities on reference
                example.reference.set_ents([
                    example.reference.char_span(start, end, label=label)
                    for start, end, label in sample.gold_entities
                ])
                examples.append(example)
            except Exception as e:
                print(f"Warning: Failed to create example for '{sample.question}': {e}")
                continue

        if not examples:
            return {"ents_f": 0.0, "ents_p": 0.0, "ents_r": 0.0}

        # Score predictions
        scorer = Scorer()
        scores = scorer.score(examples)

        return {
            "ents_f": scores.get("ents_f", 0.0),
            "ents_p": scores.get("ents_p", 0.0),
            "ents_r": scores.get("ents_r", 0.0)
        }


if __name__ == "__main__":
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "data"))
    from loader import TruthfulQALoader

    loader = TruthfulQALoader()
    samples, _ = loader.load_entity_subset()

    validator = NERValidator()
    result = validator.validate(samples)

    print(f"NER F1: {result['ents_f']:.3f}")
    print(f"NER Precision: {result['ents_p']:.3f}")
    print(f"NER Recall: {result['ents_r']:.3f}")
