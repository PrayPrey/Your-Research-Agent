"""Domain boundary detector using keyword similarity."""

from typing import Dict, List, Set
import re


class DomainBoundaryDetector:
    """Detect if hypothesis domain is outside KB coverage."""

    def __init__(self, kb_domains: List[Dict], similarity_threshold: float = 0.7):
        self.kb_domains = kb_domains
        self.threshold = similarity_threshold
        self.domain_embeddings = self._build_domain_embeddings()

    def _build_domain_embeddings(self) -> Dict[str, Set[str]]:
        """Build keyword sets for each KB domain."""
        embeddings = {}
        for domain in self.kb_domains:
            embeddings[domain['name']] = set(kw.lower() for kw in domain['keywords'])
        return embeddings

    def forward(self, hypothesis_text: str) -> Dict:
        """Check if hypothesis domain is covered by KB.

        Returns:
            {
                'in_scope': bool,
                'domain': str or None,
                'flag': str or None
            }
        """
        query_keywords = self.extract_domain_keywords(hypothesis_text)

        # Compute similarity to all known domains
        similarities = []
        for domain_name, domain_keywords in self.domain_embeddings.items():
            sim = self.keyword_similarity(query_keywords, domain_keywords)
            similarities.append((domain_name, sim))

        best_domain, max_sim = max(similarities, key=lambda x: x[1])

        if max_sim < self.threshold:
            return {
                'in_scope': False,
                'domain': None,
                'flag': 'BOUNDARY: Domain outside KB coverage'
            }

        return {
            'in_scope': True,
            'domain': best_domain,
            'flag': None
        }

    def extract_domain_keywords(self, text: str) -> Set[str]:
        """Extract domain keywords from hypothesis text.

        Simple approach: lowercase, split, filter common words.
        """
        text_lower = text.lower()
        # Remove punctuation
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        tokens = text_clean.split()

        # Filter stopwords (simple list)
        stopwords = {
            'using', 'improve', 'achieve', 'outperform', 'using', 'with',
            'the', 'a', 'an', 'on', 'in', 'for', 'than', 'and', 'or', 'of',
            'to', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'accuracy', 'performance', 'model', 'models', 'system', 'systems'
        }

        keywords = {t for t in tokens if t not in stopwords and len(t) > 2}
        return keywords

    def keyword_similarity(self, query_keywords: Set[str], domain_keywords: Set[str]) -> float:
        """Compute Jaccard similarity between keyword sets."""
        if not query_keywords or not domain_keywords:
            return 0.0

        intersection = query_keywords & domain_keywords
        union = query_keywords | domain_keywords

        if len(union) == 0:
            return 0.0

        return len(intersection) / len(union)
