"""Baseline safety classifiers for comparison with CARE."""

import numpy as np
import torch
from transformers import pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class OpenAIModerationBaseline:
    """Baseline using OpenAI Moderation API (rule-based simulation for offline eval)."""

    def __init__(self):
        # We simulate the OpenAI moderation API behavior using a keyword-based approach
        # since running actual API calls for each sample would be expensive
        self.harmful_patterns = [
            "kill", "hurt", "hate", "attack", "bomb", "shoot", "murder",
            "die", "suicide", "self-harm", "racist", "sexist", "nigger",
            "faggot", "bitch", "fuck", "shit", "ass", "sex", "porn",
            "illegal", "drug", "weapon", "terrorist", "molest", "rape",
        ]

    def predict_proba(self, texts):
        probs = []
        for text in texts:
            text_lower = text.lower()
            hits = sum(1 for pat in self.harmful_patterns if pat in text_lower)
            # Sigmoid-like scaling
            prob = min(1.0, hits * 0.15 + (0.1 if hits > 0 else 0.0))
            probs.append(prob)
        return np.array(probs)

    def predict(self, texts):
        return (self.predict_proba(texts) > 0.5).astype(int)


class BertBinaryClassifier:
    """BERT-based binary safety classifier using ToxiDetect."""

    def __init__(self, device=None):
        if device is None:
            device = 0 if torch.cuda.is_available() else -1
        self.device = device
        self.pipe = None

    def load(self):
        print("  Loading BERT-based hate speech detector...")
        try:
            self.pipe = pipeline(
                "text-classification",
                model="Hate-speech-CNERG/bert-base-uncased-hatexplain",
                device=self.device,
                truncation=True,
                max_length=128,
            )
        except Exception as e:
            print(f"  Primary model failed: {e}, using backup...")
            self.pipe = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-offensive",
                device=self.device,
                truncation=True,
                max_length=128,
            )
        print("  BERT classifier loaded.")
        return self

    def predict_proba(self, texts, batch_size=32):
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            out = self.pipe(batch, truncation=True, max_length=128)
            for item in out:
                label = item["label"].lower()
                score = item["score"]
                # Map to unsafe probability
                if any(x in label for x in ["hate", "offensive", "toxic", "label_1"]) and "nothate" not in label and "not_" not in label:
                    results.append(score)
                elif any(x in label for x in ["normal", "nothate", "not_hate", "label_0", "non"]):
                    results.append(1.0 - score)
                else:
                    results.append(score)
        return np.array(results)

    def predict(self, texts):
        return (self.predict_proba(texts) > 0.5).astype(int)


class LlamaGuardBaseline:
    """
    Llama Guard simulation baseline.
    Uses a strong RoBERTa-based safety model as a proxy for Llama Guard
    (actual Llama Guard would require the Meta model which may not be available).
    """

    def __init__(self, device=None):
        if device is None:
            device = 0 if torch.cuda.is_available() else -1
        self.device = device
        self.pipe = None

    def load(self):
        print("  Loading Llama Guard proxy (TweetEval offensive)...")
        try:
            self.pipe = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-offensive",
                device=self.device,
                truncation=True,
                max_length=128,
            )
        except Exception as e:
            print(f"  Failed to load primary: {e}")
            try:
                self.pipe = pipeline(
                    "text-classification",
                    model="Hate-speech-CNERG/bert-base-uncased-hatexplain",
                    device=self.device,
                    truncation=True,
                    max_length=128,
                )
            except Exception as e2:
                print(f"  Fallback also failed: {e2}")
                self.pipe = pipeline(
                    "text-classification",
                    model="facebook/roberta-hate-speech-dynabench-r4-target",
                    device=self.device,
                    truncation=True,
                    max_length=128,
                )
        print("  Llama Guard proxy loaded.")
        return self

    def predict_proba(self, texts, batch_size=32):
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            out = self.pipe(batch, truncation=True, max_length=128)
            for item in out:
                label = item["label"].lower()
                score = item["score"]
                if any(x in label for x in ["hate", "toxic", "label_1", "offensive"]) and "nothate" not in label and "not_" not in label:
                    results.append(score)
                elif any(x in label for x in ["nothate", "not_hate", "non_offensive", "label_0", "normal"]):
                    results.append(1.0 - score)
                else:
                    results.append(score)
        return np.array(results)

    def predict(self, texts):
        return (self.predict_proba(texts) > 0.5).astype(int)


def evaluate_baseline(clf, test_texts, test_labels, name="Baseline"):
    """Evaluate a baseline classifier."""
    test_labels = np.array(test_labels)
    probs = clf.predict_proba(test_texts)
    preds = (probs > 0.5).astype(int)

    acc = accuracy_score(test_labels, preds)
    prec = precision_score(test_labels, preds, zero_division=0)
    rec = recall_score(test_labels, preds, zero_division=0)
    f1 = f1_score(test_labels, preds, zero_division=0)
    try:
        auroc = roc_auc_score(test_labels, probs)
    except Exception:
        auroc = float("nan")

    return {
        "name": name,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "auroc": float(auroc),
    }, probs
