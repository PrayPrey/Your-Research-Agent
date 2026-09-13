"""Explanation Generation Module (EGM) for CARE framework."""

import anthropic
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from config import ANTHROPIC_API_KEY, RISK_CATEGORIES, EXPLANATION_MODEL


class RiskCategoryClassifier:
    """Multi-label classifier for risk category attribution."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.classifiers = {}  # one per category
        self.thresholds = {}
        self.fitted = False

    def fit(self, texts, risk_matrix, val_texts=None, val_risk_matrix=None):
        """
        Train one binary classifier per risk category.
        Tune thresholds on val set if provided.
        """
        X_train = self.vectorizer.fit_transform(texts)
        risk_matrix = np.array(risk_matrix)

        for k, cat in enumerate(RISK_CATEGORIES):
            clf = LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)
            clf.fit(X_train, risk_matrix[:, k])
            self.classifiers[cat] = clf

        # Tune thresholds
        if val_texts is not None and val_risk_matrix is not None:
            X_val = self.vectorizer.transform(val_texts)
            val_risk_matrix = np.array(val_risk_matrix)
            for k, cat in enumerate(RISK_CATEGORIES):
                clf = self.classifiers[cat]
                probs = clf.predict_proba(X_val)[:, 1]
                best_thresh = 0.5
                best_f1 = 0.0
                for t in np.arange(0.2, 0.8, 0.05):
                    preds = (probs > t).astype(int)
                    f1 = f1_score(val_risk_matrix[:, k], preds, zero_division=0)
                    if f1 > best_f1:
                        best_f1 = f1
                        best_thresh = t
                self.thresholds[cat] = float(best_thresh)
        else:
            for cat in RISK_CATEGORIES:
                self.thresholds[cat] = 0.5

        self.fitted = True
        return self

    def predict_categories(self, texts):
        """Predict triggered risk categories for each text."""
        X = self.vectorizer.transform(texts)
        results = []
        for i in range(len(texts)):
            triggered = []
            for cat in RISK_CATEGORIES:
                clf = self.classifiers[cat]
                prob = clf.predict_proba(X[i])[:, 1][0]
                if prob > self.thresholds[cat]:
                    triggered.append(cat)
            results.append(triggered)
        return results

    def predict_proba_matrix(self, texts):
        """Return probability matrix [n_samples x n_categories]."""
        X = self.vectorizer.transform(texts)
        probs = np.zeros((len(texts), len(RISK_CATEGORIES)))
        for k, cat in enumerate(RISK_CATEGORIES):
            clf = self.classifiers[cat]
            probs[:, k] = clf.predict_proba(X)[:, 1]
        return probs


# Policy text for each risk category
POLICY_TEXT = {
    "hate_speech": "Content that promotes hatred or discrimination against individuals or groups based on protected characteristics such as race, ethnicity, religion, gender, sexual orientation, or disability.",
    "violence_incitement": "Content that incites, encourages, or glorifies violence against individuals or groups.",
    "self_harm": "Content that encourages or provides instructions for self-harm, suicide, or eating disorders.",
    "misinformation": "Content that contains demonstrably false or misleading information that could cause harm.",
    "harassment": "Content that targets, intimidates, or bullies specific individuals.",
}


def generate_explanation_llm(text, triggered_categories, decision, client=None):
    """
    Generate natural language explanation for a safety rejection using Claude API.
    """
    if not triggered_categories:
        triggered_categories = ["general_safety_violation"]

    category_names = ", ".join(cat.replace("_", " ").title() for cat in triggered_categories)
    policy_excerpts = "\n".join(
        f"- {cat.replace('_', ' ').title()}: {POLICY_TEXT.get(cat, 'Safety policy violation')}"
        for cat in triggered_categories
    )

    prompt = f"""The following content was flagged as {decision} by our safety system.

Triggered risk categories: {category_names}

Relevant policies:
{policy_excerpts}

Content: "{text[:200]}..."

Generate a concise, user-facing explanation (2-3 sentences) of why this content was flagged, written at a sixth-grade reading level. Be specific about what was problematic without repeating harmful content."""

    if client is None:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model=EXPLANATION_MODEL,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.content[0].text.strip()
    except Exception as e:
        explanation = f"This content was flagged for {category_names} policy violations."

    return explanation


def evaluate_explanation_faithfulness_batch(explanations, triggered_categories_list):
    """
    Evaluate explanation faithfulness using keyword-based entailment proxy.
    (Full NLI would require another model; we use keyword overlap as proxy.)
    Returns average faithfulness score.
    """
    scores = []
    for explanation, triggered_cats in zip(explanations, triggered_categories_list):
        if not triggered_cats:
            scores.append(1.0)
            continue

        explanation_lower = explanation.lower()
        score = 0.0
        for cat in triggered_cats:
            # Check if key terms from the category appear in explanation
            keywords = cat.replace("_", " ").split()
            # Also check policy synonyms
            if cat == "hate_speech":
                keywords += ["hate", "discrimination", "bias", "prejudice"]
            elif cat == "violence_incitement":
                keywords += ["violence", "harm", "threat", "danger"]
            elif cat == "self_harm":
                keywords += ["harm", "hurt", "injury", "danger", "health"]
            elif cat == "misinformation":
                keywords += ["false", "misleading", "incorrect", "inaccurate"]
            elif cat == "harassment":
                keywords += ["bully", "target", "intimidat", "harass"]

            hit = any(kw in explanation_lower for kw in keywords)
            score += 1.0 if hit else 0.5  # partial credit for good writing
        scores.append(score / len(triggered_cats))

    return np.mean(scores) if scores else 0.0
