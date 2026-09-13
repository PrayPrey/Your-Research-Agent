import math
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from bert_score import score as bert_score_fn

class SemanticEntropyDetector:
    def __init__(self, nli_model: str = "microsoft/deberta-v3-large-mnli"):
        self.tokenizer = AutoTokenizer.from_pretrained(nli_model)
        self.model = AutoModelForSequenceClassification.from_pretrained(nli_model)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.entail_idx = 2  # deberta-mnli: 0=contradiction, 1=neutral, 2=entailment

    def _nli_entail_prob(self, premise: str, hypothesis: str) -> float:
        inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)
        return probs[0, self.entail_idx].item()

    def _cluster_by_entailment(self, responses: list[str], threshold: float = 0.5) -> list[list[str]]:
        clusters = []
        for r in responses:
            placed = False
            for c in clusters:
                rep = c[0]
                p_fwd = self._nli_entail_prob(rep, r)
                p_bwd = self._nli_entail_prob(r, rep)
                if p_fwd > threshold and p_bwd > threshold:
                    c.append(r)
                    placed = True
                    break
            if not placed:
                clusters.append([r])
        return clusters

    def compute_entropy(self, responses: list[str], threshold: float = 0.5) -> float:
        if len(responses) <= 1:
            return 0.0
        clusters = self._cluster_by_entailment(responses, threshold)
        n = len(responses)
        probs = [len(c) / n for c in clusters]
        return -sum(p * math.log(p) for p in probs if p > 0)

class SelfConsistencyDetector:
    def __init__(self, lang: str = "en"):
        self.lang = lang

    def compute_consistency(self, responses: list[str]) -> float:
        n = len(responses)
        if n <= 1:
            return 1.0
        cands, refs = [], []
        for i in range(n):
            for j in range(n):
                if i != j:
                    cands.append(responses[i])
                    refs.append(responses[j])
        _, _, f1 = bert_score_fn(cands, refs, lang=self.lang, verbose=False)
        return f1.mean().item()
