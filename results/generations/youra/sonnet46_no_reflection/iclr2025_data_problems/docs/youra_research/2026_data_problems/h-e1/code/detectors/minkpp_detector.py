from __future__ import annotations
import numpy as np
import torch
import torch.nn.functional as F
from config import ExperimentConfig


class MinkPPDetector:
    """Detector Family 3: Min-K%++ membership inference attack."""

    def __init__(self, cfg: ExperimentConfig, model_name: str = "EleutherAI/pythia-6.9b"):
        self.k: float = cfg.minkpp_k  # 0.20
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _load_model(self) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print(f"  Loading {self.model_name} for Min-K%++...")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        self._model.eval()
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

    def score(self, texts: list[str]) -> np.ndarray:
        """Compute Min-K%++ scores. Returns shape (N,) float32."""
        if self._model is None:
            self._load_model()
        scores = []
        for text in texts:
            try:
                inputs = self._tokenizer(
                    text, return_tensors="pt", truncation=True, max_length=512
                )
                input_ids = inputs["input_ids"].to(self._model.device)
                with torch.no_grad():
                    logits = self._model(input_ids).logits  # (1, L, V)
                log_probs = F.log_softmax(logits[0], dim=-1)  # (L, V)
                L = input_ids.shape[1]
                if L < 2:
                    scores.append(0.0)
                    continue
                token_lp = log_probs[range(L - 1), input_ids[0, 1:]]  # (L-1,)
                k_count = max(1, int(self.k * len(token_lp)))
                bottom_k = torch.topk(token_lp, k_count, largest=False).values
                scores.append(bottom_k.mean().item())
            except Exception as e:
                scores.append(0.0)
        return np.array(scores, dtype=np.float32)

    def predict(self, texts: list[str], threshold: float = 0.0) -> np.ndarray:
        """Binary predictions. Returns shape (N,) int64."""
        return (self.score(texts) >= threshold).astype(np.int64)
