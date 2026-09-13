"""
Baseline Methods for h-m-integrated
Permutation, LDA, and Lexical baselines for comparison
"""

import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from typing import List
import re


class PermutationBaseline:
    """Random label permutation baseline."""

    def __init__(self, config):
        """
        Initialize permutation baseline.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.random_state = config.baseline.permutation_seed

    def predict(self, labels_true: np.ndarray) -> np.ndarray:
        """
        Randomly shuffle true labels.

        Args:
            labels_true: [N] true labels

        Returns:
            np.ndarray: [N] shuffled labels
        """
        print("Running permutation baseline (random shuffle)...")
        rng = np.random.RandomState(self.random_state)
        labels_permuted = rng.permutation(labels_true)
        print(f"Permutation completed. Distribution: {np.bincount(labels_permuted)}")
        return labels_permuted


class LDABaseline:
    """LDA 2-topic modeling baseline."""

    def __init__(self, config):
        """
        Initialize LDA baseline.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.baseline_config = config.baseline
        self.vectorizer = None
        self.lda_model = None

    def fit_predict(self, texts: List[str]) -> np.ndarray:
        """
        LDA topic modeling with 2 topics.

        Args:
            texts: List of text strings

        Returns:
            np.ndarray: [N] topic assignments {0, 1}
        """
        print("Running LDA baseline (2-topic model)...")

        # Vectorize texts
        self.vectorizer = CountVectorizer(
            max_features=self.baseline_config.lda_max_features,
            stop_words='english'
        )
        doc_term_matrix = self.vectorizer.fit_transform(texts)

        # Fit LDA
        self.lda_model = LatentDirichletAllocation(
            n_components=self.baseline_config.lda_n_components,
            max_iter=self.baseline_config.lda_max_iter,
            random_state=self.baseline_config.lda_random_state,
            n_jobs=-1
        )
        topic_distributions = self.lda_model.fit_transform(doc_term_matrix)

        # Assign to dominant topic
        labels_lda = topic_distributions.argmax(axis=1)

        print(f"LDA completed. Topic distribution: {np.bincount(labels_lda)}")
        return labels_lda


class LexicalBaseline:
    """Lexical keyword matching baseline."""

    def __init__(self, config):
        """
        Initialize lexical baseline.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.baseline_config = config.baseline
        self.keywords = self.baseline_config.rai_keywords
        self.case_sensitive = self.baseline_config.case_sensitive

    def predict(self, texts: List[str]) -> np.ndarray:
        """
        Keyword-based clustering.

        Args:
            texts: List of text strings

        Returns:
            np.ndarray: [N] binary labels (0=General, 1=RAI if keyword found)
        """
        print(f"Running lexical baseline (keywords: {len(self.keywords)})...")

        labels_lexical = []
        for text in texts:
            has_keyword = self._has_rai_keyword(text)
            label = 1 if has_keyword else 0
            labels_lexical.append(label)

        labels_lexical = np.array(labels_lexical, dtype=np.int32)
        print(f"Lexical completed. Distribution: {np.bincount(labels_lexical)}")
        return labels_lexical

    def _has_rai_keyword(self, text: str) -> bool:
        """
        Check if text contains any RAI keyword.

        Args:
            text: Input text

        Returns:
            bool: True if keyword found
        """
        if not self.case_sensitive:
            text = text.lower()

        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword.lower() if not self.case_sensitive else keyword) + r'\b'
            if re.search(pattern, text):
                return True
        return False
