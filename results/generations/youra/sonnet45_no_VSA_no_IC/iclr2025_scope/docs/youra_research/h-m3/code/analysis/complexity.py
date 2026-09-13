"""Query complexity classifier using entity density and word count."""
import spacy


class QueryComplexityClassifier:
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Load spaCy model for entity extraction."""
        self.nlp = spacy.load(spacy_model)

    def compute_entity_density(self, query: str) -> float:
        """Compute entity density: num_entities / num_tokens."""
        doc = self.nlp(query)
        tokens = [t for t in doc if not t.is_space]
        return len(doc.ents) / len(tokens) if tokens else 0.0

    def classify(self, query: str) -> str:
        """Classify query as 'simple' or 'complex'.

        Simple: word_count < 10 AND entity_density < 0.3
        Complex: otherwise
        """
        word_count = len(query.split())
        density = self.compute_entity_density(query)
        return "simple" if (word_count < 10 and density < 0.3) else "complex"
