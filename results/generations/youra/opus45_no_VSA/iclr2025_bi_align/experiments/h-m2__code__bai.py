import sys
import os
import math

LENGTH_NORM_COEF = 0.1

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code"))
import config as e1_config
from data import load_hh_rlhf, build_labels
from model import AgencyProxyDetector


def train_proxy_detectors():
    """Fit one detector per proxy type using HH-RLHF texts."""
    print("Loading HH-RLHF for proxy training...")
    texts = load_hh_rlhf()
    print(f"Loaded {len(texts)} texts for training")

    detectors = {}
    for proxy in e1_config.PROXY_TYPES:
        labels = build_labels(texts, proxy)
        detector = AgencyProxyDetector()
        detector.fit(texts, labels)
        pos_rate = sum(labels) / len(labels) if labels else 0
        print(f"Trained {proxy}: {sum(labels)}/{len(labels)} positives ({pos_rate:.2%})")
        detectors[proxy] = detector

    return detectors


def length_normalize(raw_bai, response):
    """Normalize BAI score by response length."""
    word_count = max(1, len(response.split()))
    return raw_bai / (1 + LENGTH_NORM_COEF * math.log(word_count))


def compute_bai_scores(responses, detectors):
    """Compute BAI score for each response (mean of 4 proxy scores, length-normalized)."""
    all_proxy_scores = []
    for proxy, detector in detectors.items():
        scores = detector.predict_proba(responses)
        all_proxy_scores.append(scores)

    bai_scores = []
    for i, response in enumerate(responses):
        raw_bai = sum(scores[i] for scores in all_proxy_scores) / len(all_proxy_scores)
        normalized = length_normalize(raw_bai, response)
        bai_scores.append(normalized)

    return bai_scores
