"""CCP (Claim-Conditioned Probability) evaluator."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np
from typing import List, Dict, Tuple
from tqdm import tqdm


class CCPEvaluator:
    """Evaluate ρ_j metric using NLI-based claim classification."""

    def __init__(self, nli_model: str = "microsoft/deberta-large-mnli", K: int = 10, batch_size: int = 32):
        self.K = K
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading NLI model: {nli_model} on {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(nli_model)
        self.model = AutoModelForSequenceClassification.from_pretrained(nli_model)
        self.model.to(self.device)
        self.model.eval()

        # Label mapping for NLI (DeBERTa MNLI uses: 0=contradiction, 1=neutral, 2=entailment)
        self.label_map = {0: "contradiction", 1: "neutral", 2: "entailment"}

    def classify_nli(self, premises: List[str], hypotheses: List[str]) -> List[str]:
        """Classify NLI relationships in batches.

        Args:
            premises: List of premise texts
            hypotheses: List of hypothesis texts

        Returns:
            List of labels: 'entailment', 'contradiction', or 'neutral'
        """
        if not premises or not hypotheses:
            return []

        assert len(premises) == len(hypotheses), "Premises and hypotheses must have same length"

        labels = []
        batch_size = self.batch_size

        # Try with initial batch size, fall back to smaller if OOM
        while batch_size >= 1:
            try:
                for i in range(0, len(premises), batch_size):
                    batch_premises = premises[i:i + batch_size]
                    batch_hypotheses = hypotheses[i:i + batch_size]

                    # Tokenize
                    inputs = self.tokenizer(
                        batch_premises,
                        batch_hypotheses,
                        padding=True,
                        truncation=True,
                        max_length=512,
                        return_tensors="pt"
                    ).to(self.device)

                    # Inference
                    with torch.no_grad():
                        with torch.cuda.amp.autocast(enabled=self.device.type == "cuda"):
                            outputs = self.model(**inputs)
                            predictions = torch.argmax(outputs.logits, dim=-1)

                    # Convert to labels
                    batch_labels = [self.label_map[p.item()] for p in predictions]
                    labels.extend(batch_labels)

                    # Clear GPU cache
                    if self.device.type == "cuda":
                        torch.cuda.empty_cache()

                break  # Success, exit retry loop

            except torch.cuda.OutOfMemoryError:
                batch_size = batch_size // 2
                if batch_size < 1:
                    raise
                print(f"GPU OOM, reducing batch size to {batch_size}")
                labels = []  # Reset and retry
                if self.device.type == "cuda":
                    torch.cuda.empty_cache()

        return labels

    def compute_rho_j(self, response: Dict, alternatives: List[List[Tuple[str, float]]]) -> float:
        """Compute ρ_j metric for a single response.

        Args:
            response: Dict with 'response' key
            alternatives: List of token alternatives (from get_token_alternatives)

        Returns:
            ρ_j value (claim-type mass ratio)
        """
        response_text = response["response"]
        if not response_text or not alternatives:
            return 0.0

        # Prepare NLI pairs for all token alternatives
        premises = []
        hypotheses = []

        for token_idx, token_alts in enumerate(alternatives):
            for alt_token, prob in token_alts:
                # Use full response as both premise and hypothesis
                # (simplified version - in full CCP, we'd replace individual tokens)
                premises.append(response_text)
                hypotheses.append(response_text)  # Placeholder - should be modified text

        if not premises:
            return 0.0

        # Classify all pairs
        nli_labels = self.classify_nli(premises, hypotheses)

        # Count NLI outcomes
        counts = {"entailment": 0, "contradiction": 0, "neutral": 0}
        for label in nli_labels:
            counts[label] += 1

        # Compute ρ_j = (N_e + N_c) / (N_e + N_n + N_c)
        numerator = counts["entailment"] + counts["contradiction"]
        denominator = sum(counts.values())

        if denominator == 0:
            return 0.0

        rho_j = numerator / denominator
        return rho_j

    def evaluate_domain(self, responses: List[Dict], token_generator) -> Dict:
        """Evaluate ρ_j across all responses in a domain.

        Args:
            responses: List of response dicts with 'response' and 'logprobs' keys
            token_generator: ResponseGenerator instance to extract alternatives

        Returns:
            Dict with domain statistics
        """
        rho_j_values = []

        for response in tqdm(responses, desc="Computing ρ_j"):
            if response.get("error") or not response.get("logprobs"):
                continue

            # Extract token alternatives
            tokens, alternatives = token_generator.get_token_alternatives(
                response["logprobs"],
                K=self.K
            )

            # Compute ρ_j
            rho_j = self.compute_rho_j(response, alternatives)
            rho_j_values.append(rho_j)

        median_rho_j = float(np.median(rho_j_values)) if rho_j_values else 0.0

        return {
            "domain": responses[0]["domain"] if responses else "unknown",
            "rho_j_values": rho_j_values,
            "median_rho_j": median_rho_j,
            "n_samples": len(rho_j_values)
        }
