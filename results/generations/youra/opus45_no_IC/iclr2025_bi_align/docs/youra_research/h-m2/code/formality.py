"""DeBERTa formality scoring for H-M2 experiment."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from tqdm import tqdm
from config import MODEL_NAME, MAX_SEQ_LEN, BATCH_SIZE


class FormalityScorer:
    """Score text formality using DeBERTa formality ranker."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        print(f"FormalityScorer loaded on {self.device}")

    def score_batch(self, texts: list, batch_size: int = BATCH_SIZE) -> list:
        """Score formality for a list of texts."""
        scores = []

        for i in tqdm(range(0, len(texts), batch_size), desc="Scoring formality"):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=MAX_SEQ_LEN,
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)

            probs = torch.softmax(outputs.logits, dim=-1)
            batch_scores = probs[:, 1].cpu().numpy().tolist()
            scores.extend(batch_scores)

        return scores


def score_pairs(pairs: list, scorer: FormalityScorer) -> tuple:
    """Score formality for all (human, AI) pairs."""
    human_texts = [p[0] for p in pairs]
    ai_texts = [p[1] for p in pairs]

    print(f"Scoring {len(human_texts)} human messages...")
    human_scores = scorer.score_batch(human_texts)

    print(f"Scoring {len(ai_texts)} AI messages...")
    ai_scores = scorer.score_batch(ai_texts)

    return human_scores, ai_scores
