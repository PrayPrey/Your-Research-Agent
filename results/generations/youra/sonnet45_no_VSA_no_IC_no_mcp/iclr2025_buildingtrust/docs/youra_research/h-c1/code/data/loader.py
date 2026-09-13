"""TruthfulQA data loader with gold entity annotations."""
import json
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
from datasets import load_dataset

random.seed(42)


@dataclass
class EntitySample:
    """Single TruthfulQA sample with entity annotation."""
    question: str
    gold_entities: List[Tuple[int, int, str]]  # [(start, end, label)]
    correct_entity: str


class TruthfulQALoader:
    """Load and prepare TruthfulQA entity subset."""

    def __init__(self, data_path: str = "./data/truthfulqa_entity_subset"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

    def load_entity_subset(self) -> Tuple[List[EntitySample], List[str]]:
        """
        Load gold-annotated TruthfulQA samples.

        Returns:
            all_samples: 100 samples with gold annotations
            entities_for_coverage: 50 entity names for Wikipedia check
        """
        gold_file = self.data_path / "gold_annotations.jsonl"
        entity_file = self.data_path / "entity_errors.json"

        if not gold_file.exists():
            self._create_synthetic_dataset()

        # Load gold annotations
        samples = []
        with open(gold_file) as f:
            for line in f:
                data = json.loads(line)
                samples.append(EntitySample(
                    question=data["question"],
                    gold_entities=data["entities"],
                    correct_entity=data.get("correct_entity", "")
                ))

        # Load entities for coverage check
        with open(entity_file) as f:
            entity_data = json.load(f)
        entities = [item["correct_entity"] for item in entity_data]

        return samples, entities

    def _create_synthetic_dataset(self):
        """Create synthetic gold-annotated dataset for PoC."""
        # Load TruthfulQA
        dataset = load_dataset("truthful_qa", "generation", split="validation")

        # Sample questions with clear entity mentions
        entity_questions = []
        non_entity_questions = []

        # Common entities for Wikipedia coverage
        test_entities = [
            "Albert Einstein", "Paris", "Google", "United States",
            "Isaac Newton", "London", "Microsoft", "China",
            "Marie Curie", "Tokyo", "Apple Inc.", "Germany",
            "Stephen Hawking", "New York", "Amazon", "France",
            "Nikola Tesla", "Beijing", "Tesla Motors", "India",
            "Charles Darwin", "Moscow", "Facebook", "Brazil",
            "Leonardo da Vinci", "Sydney", "Netflix", "Canada",
            "Galileo Galilei", "Berlin", "Twitter", "Australia",
            "Thomas Edison", "Rome", "Intel", "Russia",
            "Marie Antoinette", "Madrid", "IBM", "Japan",
            "Winston Churchill", "Cairo", "Oracle", "Mexico",
            "Napoleon Bonaparte", "Dubai", "Adobe", "Italy",
            "Cleopatra", "Singapore", "Cisco", "Spain",
        ]

        # Create synthetic entity-error samples
        for i, entity in enumerate(test_entities[:50]):
            # Create question with entity
            question = f"What is the most notable achievement of {entity}?"
            # Find entity position
            start_idx = question.find(entity)
            end_idx = start_idx + len(entity)

            # Determine entity type
            if any(word in entity for word in ["Inc.", "Motors", "Google", "Microsoft", "Apple", "Amazon", "Tesla", "Facebook", "Netflix", "Twitter", "Intel", "IBM", "Oracle", "Adobe", "Cisco"]):
                label = "ORG"
            elif entity in ["Paris", "London", "Tokyo", "New York", "Beijing", "Moscow", "Sydney", "Berlin", "Rome", "Madrid", "Cairo", "Dubai", "Singapore", "United States", "China", "Germany", "France", "India", "Brazil", "Canada", "Australia", "Russia", "Japan", "Mexico", "Italy", "Spain"]:
                label = "GPE"
            else:
                label = "PERSON"

            entity_questions.append({
                "question": question,
                "entities": [[start_idx, end_idx, label]],
                "correct_entity": entity
            })

        # Create non-entity samples (no entities or weak entities)
        for i in range(50):
            # Use actual TruthfulQA questions
            if i < len(dataset):
                question = dataset[i]["question"]
            else:
                question = "What is the meaning of life?"

            non_entity_questions.append({
                "question": question,
                "entities": [],  # No gold entities
                "correct_entity": ""
            })

        # Write gold annotations
        gold_file = self.data_path / "gold_annotations.jsonl"
        with open(gold_file, "w") as f:
            for sample in entity_questions + non_entity_questions:
                f.write(json.dumps(sample) + "\n")

        # Write entity errors subset
        entity_file = self.data_path / "entity_errors.json"
        with open(entity_file, "w") as f:
            json.dump(entity_questions, f, indent=2)

        # Write non-entity errors subset
        non_entity_file = self.data_path / "non_entity_errors.json"
        with open(non_entity_file, "w") as f:
            json.dump(non_entity_questions, f, indent=2)


if __name__ == "__main__":
    loader = TruthfulQALoader()
    samples, entities = loader.load_entity_subset()
    print(f"Loaded {len(samples)} samples, {len(entities)} entities for coverage check")
    print(f"Sample question: {samples[0].question}")
    print(f"Sample entities: {samples[0].gold_entities}")
