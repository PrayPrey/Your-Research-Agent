"""Consistency scorer using NLI + BERTScore ensemble."""

import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from bert_score import BERTScorer


class ConsistencyScorer:
    """Compute epistemic uncertainty via NLI + BERTScore ensemble."""

    def __init__(
        self,
        nli_model: str = "roberta-large-mnli",
        bertscore_model: str = "microsoft/deberta-xlarge-mnli",
        device: str = "cuda"
    ):
        """Initialize NLI and BERTScore models."""
        self.device = device

        # Load NLI model
        print(f"    Loading NLI model: {nli_model}...")
        self.nli_tokenizer = AutoTokenizer.from_pretrained(nli_model)
        self.nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model)
        self.nli_model.to(device)
        self.nli_model.eval()

        # Initialize BERTScore
        print(f"    Loading BERTScore model: {bertscore_model}...")
        self.bert_scorer = BERTScorer(
            model_type=bertscore_model,
            lang="en",
            rescale_with_baseline=True,
            device=device
        )

    def compute_nli_scores(
        self,
        reference: str,
        samples: list[str]
    ) -> list[float]:
        """Compute NLI entailment scores."""
        scores = []

        for sample in samples:
            # Tokenize premise-hypothesis pair
            inputs = self.nli_tokenizer(
                reference,
                sample,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get entailment probability
            with torch.no_grad():
                logits = self.nli_model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)
                # Index 2 = entailment (0: contradiction, 1: neutral, 2: entailment)
                entailment_prob = probs[0, 2].item()
                scores.append(entailment_prob)

        return scores

    def compute_bertscore(
        self,
        reference: str,
        samples: list[str]
    ) -> list[float]:
        """Compute BERTScore F1 similarities."""
        # BERTScorer expects lists
        references = [reference] * len(samples)

        # Compute scores
        P, R, F1 = self.bert_scorer.score(
            cands=samples,
            refs=references
        )

        # Return F1 scores
        return F1.cpu().numpy().tolist()

    def compute_consistency(
        self,
        reference: str,
        samples: list[str]
    ) -> float:
        """
        Compute ensemble consistency score C.

        Returns:
            float: Consistency score C ∈ [0, 1]
                   High C = low epistemic uncertainty
        """
        if not samples:
            return 0.0

        # Compute both scores
        nli_scores = self.compute_nli_scores(reference, samples)
        bert_scores = self.compute_bertscore(reference, samples)

        # Ensemble average
        C = (np.mean(nli_scores) + np.mean(bert_scores)) / 2

        return float(C)
