from __future__ import annotations
import numpy as np
import torch
import torch.nn.functional as F
from config import ExperimentConfig


class DCPDDDetector:
    """Detector Family 4: DC-PDD likelihood ratio vs reference model (Zhang et al. 2024)."""

    def __init__(self, cfg: ExperimentConfig, ref_model_name: str = "EleutherAI/pythia-2.8b"):
        self.ref_model_name = ref_model_name
        self._ref_model = None
        self._tokenizer = None
        self._cfg = cfg

    def _load_model(self) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print(f"  Loading {self.ref_model_name} for DC-PDD reference...")
        self._tokenizer = AutoTokenizer.from_pretrained(self.ref_model_name)
        self._ref_model = AutoModelForCausalLM.from_pretrained(
            self.ref_model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        self._ref_model.eval()
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

    def _mean_log_prob(self, text: str) -> float:
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        input_ids = inputs["input_ids"].to(self._ref_model.device)
        with torch.no_grad():
            logits = self._ref_model(input_ids).logits
        log_probs = F.log_softmax(logits[0], dim=-1)
        L = input_ids.shape[1]
        if L < 2:
            return 0.0
        token_lp = log_probs[range(L - 1), input_ids[0, 1:]]
        return token_lp.mean().item()

    def score(self, texts: list[str]) -> np.ndarray:
        """DC-PDD score = negative reference log-prob (higher = more anomalous).
        Returns shape (N,) float32."""
        if self._ref_model is None:
            self._load_model()
        scores = []
        for text in texts:
            try:
                ref_lp = self._mean_log_prob(text)
                # Higher score = lower ref prob = more likely contaminated
                scores.append(-ref_lp)
            except Exception:
                scores.append(0.0)
        return np.array(scores, dtype=np.float32)

    def predict(self, texts: list[str], threshold: float = 0.0) -> np.ndarray:
        """Binary predictions. Returns shape (N,) int64."""
        return (self.score(texts) >= threshold).astype(np.int64)
