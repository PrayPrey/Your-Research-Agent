"""Linguistic marker extraction module.

This module implements extraction of three types of linguistic agency markers:
1. Modal verbs (via spaCy POS tagging)
2. Hedging language (via lexicon matching)
3. Alternative-framing phrases (via regex patterns)
"""

import spacy
import re
from typing import Dict, Set, List


class LinguisticMarkerExtractor:
    """Extractor for linguistic agency markers."""

    def __init__(self, spacy_model: str = "en_core_web_sm",
                 hedging_markers: Set[str] = None,
                 alternative_patterns: List[str] = None):
        """Initialize extractor.

        Args:
            spacy_model: Name of spaCy model to load
            hedging_markers: Set of hedging marker words
            alternative_patterns: List of regex patterns for alternative-framing
        """
        print(f"Loading spaCy model: {spacy_model}...")
        self.nlp = spacy.load(spacy_model)
        print("✓ spaCy model loaded")

        # Default hedging markers
        if hedging_markers is None:
            hedging_markers = {
                'perhaps', 'maybe', 'might', 'could', 'possibly',
                'probably', 'likely', 'seems', 'appears', 'suggests',
                'tend', 'often', 'sometimes', 'generally', 'typically'
            }
        self.hedging_markers = hedging_markers

        # Default alternative patterns
        if alternative_patterns is None:
            alternative_patterns = [
                r'\byou (could|might|may)\b',
                r'\b(one|another) (option|approach|alternative|way)\b',
                r'\balternatively\b',
                r'\bon the other hand\b',
                r'\byou (can|have) the option\b'
            ]
        self.alternative_patterns = alternative_patterns

    def extract_modal_verbs(self, text: str) -> float:
        """Extract modal verb frequency.

        Args:
            text: Input text

        Returns:
            Modal verb count per 100 words
        """
        doc = self.nlp(text)

        # Count alpha words
        word_count = len([token for token in doc if token.is_alpha])

        if word_count == 0:
            return 0.0

        # Count modal verbs (POS tag MD)
        modal_count = len([token for token in doc if token.tag_ == 'MD'])

        # Normalize to per 100 words
        modal_freq = (modal_count / word_count) * 100

        return modal_freq

    def extract_hedging(self, text: str) -> float:
        """Extract hedging marker frequency.

        Args:
            text: Input text

        Returns:
            Hedging marker count per 100 words
        """
        # Convert to lowercase for matching
        text_lower = text.lower()
        words = text_lower.split()

        # Count hedging markers
        hedging_count = sum(1 for marker in self.hedging_markers
                           if marker in words)

        # Count alpha words for normalization
        doc = self.nlp(text)
        word_count = len([token for token in doc if token.is_alpha])

        if word_count == 0:
            return 0.0

        # Normalize to per 100 words
        hedging_freq = (hedging_count / word_count) * 100

        return hedging_freq

    def extract_alternatives(self, text: str) -> float:
        """Extract alternative-framing phrase frequency.

        Args:
            text: Input text

        Returns:
            Alternative-framing count per 100 words
        """
        # Count matches for all patterns
        alt_count = sum(len(re.findall(pattern, text, re.IGNORECASE))
                       for pattern in self.alternative_patterns)

        # Count alpha words for normalization
        doc = self.nlp(text)
        word_count = len([token for token in doc if token.is_alpha])

        if word_count == 0:
            return 0.0

        # Normalize to per 100 words
        alt_freq = (alt_count / word_count) * 100

        return alt_freq

    def extract_all_features(self, text: str) -> Dict[str, float]:
        """Extract all three marker types.

        Args:
            text: Input text

        Returns:
            Dictionary with modal_freq, hedging_freq, alt_freq keys
        """
        # Process text once with spaCy for efficiency
        doc = self.nlp(text)
        word_count = len([token for token in doc if token.is_alpha])

        if word_count == 0:
            return {
                'modal_freq': 0.0,
                'hedging_freq': 0.0,
                'alt_freq': 0.0,
                'word_count': 0
            }

        # Extract modal verbs from doc
        modal_count = len([token for token in doc if token.tag_ == 'MD'])
        modal_freq = (modal_count / word_count) * 100

        # Extract hedging markers
        text_lower = text.lower()
        words = text_lower.split()
        hedging_count = sum(1 for marker in self.hedging_markers
                           if marker in words)
        hedging_freq = (hedging_count / word_count) * 100

        # Extract alternative-framing
        alt_count = sum(len(re.findall(pattern, text, re.IGNORECASE))
                       for pattern in self.alternative_patterns)
        alt_freq = (alt_count / word_count) * 100

        return {
            'modal_freq': modal_freq,
            'hedging_freq': hedging_freq,
            'alt_freq': alt_freq,
            'word_count': word_count
        }
