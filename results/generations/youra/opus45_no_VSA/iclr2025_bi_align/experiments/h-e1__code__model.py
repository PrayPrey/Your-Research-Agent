import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
import config


class AgencyProxyDetector:
    """TF-IDF + LogisticRegression classifier for agency proxy detection."""

    def __init__(self):
        self.vectorizer = None
        self.classifier = None

    def match_pattern(self, text, proxy):
        """Check if text matches any pattern for given proxy."""
        patterns = config.PROXY_PATTERNS.get(proxy, [])
        return any(re.search(p, text, re.IGNORECASE | re.MULTILINE) for p in patterns)

    def fit(self, texts, labels):
        """Fit TF-IDF vectorizer and LogisticRegression classifier."""
        self.vectorizer = TfidfVectorizer(**config.TFIDF_PARAMS)
        X = self.vectorizer.fit_transform(texts)
        self.classifier = LogisticRegression(**config.LOGREG_PARAMS)
        self.classifier.fit(X, labels)
        return self

    def predict_proba(self, texts):
        """Return P(label=1) for each text."""
        X = self.vectorizer.transform(texts)
        proba = self.classifier.predict_proba(X)
        if proba.shape[1] == 2:
            return proba[:, 1].tolist()
        return proba[:, 0].tolist()


def random_baseline(n, random_state=config.RANDOM_STATE):
    """Return n random scores in [0, 1]."""
    rng = np.random.RandomState(random_state)
    return rng.rand(n).tolist()


def majority_baseline(labels):
    """Return constant scores matching majority class frequency."""
    if not labels:
        return []
    majority_freq = sum(labels) / len(labels)
    return [majority_freq] * len(labels)
