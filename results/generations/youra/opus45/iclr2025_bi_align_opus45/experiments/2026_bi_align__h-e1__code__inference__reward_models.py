"""
Multi-RM Inference Infrastructure for H-E1 experiment.

Provides unified interface for 4 architecturally distinct reward models:
- ArmoRM: Llama-3 + MoE gating (8B)
- UltraRM: Llama + regression head (13B)
- StarlingRM: Llama2-7B-Chat (7B)
- PairRM: DeBERTa-v3-large (0.4B)
"""

import gc
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any

import torch
import numpy as np
from tqdm import tqdm


class BaseRewardModel(ABC):
    """Abstract base for all reward model adapters."""

    model_id: str = ""  # HuggingFace model identifier

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self._loaded = False

    @abstractmethod
    def load(self, device: str, use_4bit: bool = False) -> None:
        """Load model and tokenizer onto device."""
        pass

    @abstractmethod
    def score(self, prompt: str, response: str) -> float:
        """Score single (prompt, response) pair. Returns raw scalar."""
        pass

    def score_batch(
        self,
        pairs: List[Tuple[str, str]],
        batch_size: int = 16,
    ) -> List[float]:
        """
        Batch score multiple (prompt, response) pairs.

        Args:
            pairs: List of (prompt, response) tuples
            batch_size: Number of pairs to process at once

        Returns:
            List of scores, one per pair
        """
        scores = []
        for i in range(0, len(pairs), batch_size):
            batch = pairs[i:i + batch_size]
            batch_scores = [self.score(p, r) for p, r in batch]
            scores.extend(batch_scores)
        return scores

    def normalize_scores(self, scores: List[float]) -> List[float]:
        """Min-max normalize to [0, 1]."""
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [0.5] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def unload(self) -> None:
        """Delete model/tokenizer and free GPU memory."""
        if hasattr(self, 'model') and self.model is not None:
            del self.model
            self.model = None
        if hasattr(self, 'tokenizer') and self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if hasattr(self, 'blender') and self.blender is not None:
            del self.blender
            self.blender = None

        self._loaded = False
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @property
    def is_loaded(self) -> bool:
        return self._loaded


class ArmoRM(BaseRewardModel):
    """RLHFlow/ArmoRM-Llama3-8B-v0.1 - Llama3 + MoE gating head."""

    model_id: str = "RLHFlow/ArmoRM-Llama3-8B-v0.1"

    def load(self, device: str, use_4bit: bool = False) -> None:
        """Load ArmoRM model with trust_remote_code."""
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        print(f"Loading ArmoRM from {self.model_id}...")

        load_kwargs = {
            "device_map": device if device != "cuda" else "auto",
            "trust_remote_code": True,
            "torch_dtype": torch.bfloat16,
        }

        if use_4bit:
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, **load_kwargs
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id, use_fast=True, trust_remote_code=True
        )
        self.device = device
        self._loaded = True
        print(f"ArmoRM loaded successfully")

    def score(self, prompt: str, response: str) -> float:
        """Score using ArmoRM's chat template format."""
        # Format as chat
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response}
        ]

        # Tokenize with chat template
        input_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        inputs = self.tokenizer(
            input_text, return_tensors="pt", truncation=True, max_length=4096
        )

        # Move to device
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # Forward pass
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Extract score (ArmoRM uses logits)
        score = outputs.logits[0].item() if hasattr(outputs.logits, 'item') else float(outputs.logits[0])
        return score


class UltraRM(BaseRewardModel):
    """openbmb/UltraRM-13b - Llama + scalar regression head."""

    model_id: str = "openbmb/UltraRM-13b"

    def load(self, device: str, use_4bit: bool = False) -> None:
        """Load UltraRM with optional 4-bit quantization."""
        from transformers import AutoModel, AutoTokenizer

        print(f"Loading UltraRM from {self.model_id}...")

        load_kwargs = {
            "device_map": device if device != "cuda" else "auto",
            "trust_remote_code": True,
            "torch_dtype": torch.bfloat16,
        }

        if use_4bit:
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)

        self.model = AutoModel.from_pretrained(self.model_id, **load_kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        self.device = device
        self._loaded = True
        print(f"UltraRM loaded successfully")

    def score(self, prompt: str, response: str) -> float:
        """Score using UltraRM's expected format."""
        # UltraRM expects: Human: {prompt}\n\nAssistant: {response}
        input_text = f"Human: {prompt}\n\nAssistant: {response}"

        inputs = self.tokenizer(
            input_text, return_tensors="pt", truncation=True, max_length=4096
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        # UltraRM returns reward in the hidden states via custom head
        # The model architecture extracts reward from final token position
        if hasattr(outputs, 'logits'):
            score = outputs.logits[0].item()
        elif hasattr(outputs, 'reward'):
            score = outputs.reward[0].item()
        else:
            # Fallback: get from last hidden state
            hidden = outputs.last_hidden_state
            # UltraRM uses last non-pad token
            score = hidden[:, -1, :].mean().item()

        return score


class StarlingRM(BaseRewardModel):
    """berkeley-nest/Starling-RM-7B-alpha - Llama2-7B-Chat reward head."""

    model_id: str = "berkeley-nest/Starling-RM-7B-alpha"

    def load(self, device: str, use_4bit: bool = False) -> None:
        """Load StarlingRM model."""
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        print(f"Loading StarlingRM from {self.model_id}...")

        load_kwargs = {
            "device_map": device if device != "cuda" else "auto",
            "torch_dtype": torch.bfloat16,
        }

        if use_4bit:
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, **load_kwargs
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.device = device
        self._loaded = True
        print(f"StarlingRM loaded successfully")

    def score(self, prompt: str, response: str) -> float:
        """Score using Starling-RM format."""
        # Format for Starling-RM (Llama2 chat template)
        input_text = f"[INST] {prompt} [/INST] {response}"

        inputs = self.tokenizer(
            input_text, return_tensors="pt", truncation=True, max_length=4096
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        score = outputs.logits[0].item() if hasattr(outputs.logits[0], 'item') else float(outputs.logits[0])
        return score


class PairRM(BaseRewardModel):
    """llm-blender/PairRM - DeBERTa-v3-large pairwise comparator."""

    model_id: str = "llm-blender/PairRM"

    def __init__(self):
        super().__init__()
        self.blender = None

    def load(self, device: str, use_4bit: bool = False) -> None:
        """Load PairRM via llm-blender library."""
        import llm_blender

        print(f"Loading PairRM from {self.model_id}...")

        self.blender = llm_blender.Blender()
        self.blender.loadranker(self.model_id)
        self.device = device
        self._loaded = True
        print(f"PairRM loaded successfully")

    def score(self, prompt: str, response: str) -> float:
        """
        Single-response scoring mode.

        For PairRM, we compare against a minimal baseline to get absolute score.
        """
        # Compare against empty/minimal baseline
        baseline = "I don't know."
        return self.score_pair(prompt, response, baseline)

    def score_pair(
        self, prompt: str, response_a: str, response_b: str
    ) -> float:
        """
        Pairwise comparison mode.

        Args:
            prompt: Input prompt
            response_a: First response (candidate)
            response_b: Second response (baseline)

        Returns:
            P(A > B) in [0, 1]
        """
        # Use blender's comparison API
        inputs = [prompt]
        candidates_a = [[response_a]]
        candidates_b = [[response_b]]

        # blender.compare returns preference scores
        ranks = self.blender.rank(
            inputs,
            [candidates_a[0] + candidates_b[0]],
            return_scores=True
        )

        # ranks[1] contains scores, first score is for response_a
        if isinstance(ranks, tuple) and len(ranks) > 1:
            scores = ranks[1]
            if len(scores) > 0 and len(scores[0]) > 0:
                # Convert rank score to probability
                score_a = scores[0][0]
                return float(score_a)

        return 0.5  # Neutral if comparison fails

    def score_batch(
        self,
        pairs: List[Tuple[str, str]],
        batch_size: int = 16,
    ) -> List[float]:
        """Override batch scoring for PairRM efficiency."""
        scores = []
        baseline = "I don't know."

        for i in range(0, len(pairs), batch_size):
            batch = pairs[i:i + batch_size]
            batch_scores = [self.score_pair(p, r, baseline) for p, r in batch]
            scores.extend(batch_scores)

        return scores

    def unload(self) -> None:
        """Override to handle blender cleanup."""
        if self.blender is not None:
            del self.blender
            self.blender = None
        super().unload()


def load_all_models(config: "InferenceConfig") -> Dict[str, BaseRewardModel]:
    """
    Instantiate all 4 RM adapters.

    Note: Does NOT call .load() - caller manages lifecycle for VRAM efficiency.

    Args:
        config: InferenceConfig with device and dtype settings

    Returns:
        Dict mapping rm_id to model instance
    """
    return {
        "armo": ArmoRM(),
        "ultra": UltraRM(),
        "starling": StarlingRM(),
        "pairrm": PairRM(),
    }


def score_stimuli_with_rm(
    rm: BaseRewardModel,
    pairs: List[Tuple[str, str, str]],  # (prompt, enumerated, synthesized)
    batch_size: int = 16,
    show_progress: bool = True,
) -> List[Dict[str, float]]:
    """
    Score all stimulus pairs with a single reward model.

    Args:
        rm: Loaded reward model
        pairs: List of (prompt, enumerated_response, synthesized_response) tuples
        batch_size: Batch size for scoring
        show_progress: Whether to show tqdm progress bar

    Returns:
        List of {"enum_score": float, "synth_score": float} dicts
    """
    results = []

    iterator = tqdm(pairs, desc=f"Scoring") if show_progress else pairs

    for prompt, enum_resp, synth_resp in iterator:
        enum_score = rm.score(prompt, enum_resp)
        synth_score = rm.score(prompt, synth_resp)
        results.append({
            "enum_score": enum_score,
            "synth_score": synth_score,
        })

    return results
