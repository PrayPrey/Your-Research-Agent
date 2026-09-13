# nli_cluster.py - NLI-based semantic clustering
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config import NLI_MODEL_ID, NLI_MAX_LENGTH, ENTAILMENT_THRESHOLD


def load_nli_model(model_id: str = NLI_MODEL_ID, device: str = "cuda"):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    model.to(device).eval()
    return model, tokenizer


def entailment_prob(nli_model, nli_tokenizer, premise: str, hypothesis: str, device: str = "cuda") -> float:
    """P(entailment) from DeBERTa-mnli. Logits: [contradiction, neutral, entailment]."""
    inputs = nli_tokenizer(
        premise, hypothesis,
        truncation=True, max_length=NLI_MAX_LENGTH,
        return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        logits = nli_model(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1)
    return probs[2].item()


def bidirectional_entailment(nli_model, nli_tokenizer, text1: str, text2: str,
                              threshold: float = ENTAILMENT_THRESHOLD, device: str = "cuda") -> bool:
    """True if min(P(1->2), P(2->1)) > threshold."""
    p1 = entailment_prob(nli_model, nli_tokenizer, text1, text2, device)
    p2 = entailment_prob(nli_model, nli_tokenizer, text2, text1, device)
    return min(p1, p2) > threshold


def cluster_samples(nli_model, nli_tokenizer, samples: list[str],
                    threshold: float = ENTAILMENT_THRESHOLD, device: str = "cuda") -> list[list[str]]:
    """Greedy clustering: assign each sample to first matching cluster or create new one."""
    if not samples:
        return []
    clusters = [[samples[0]]]
    for s in samples[1:]:
        placed = False
        for c in clusters:
            if bidirectional_entailment(nli_model, nli_tokenizer, c[0], s, threshold, device):
                c.append(s)
                placed = True
                break
        if not placed:
            clusters.append([s])
    return clusters
