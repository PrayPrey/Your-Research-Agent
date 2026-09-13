"""Llama-3.1-8B-Instruct wrapper for answer generation."""
from typing import List, Tuple
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LlamaWrapper:
    """Wrapper for Llama-3.1-8B-Instruct inference."""

    def __init__(
        self,
        model_id: str = "meta-llama/Llama-3.1-8B-Instruct",
        cache_dir: str = "/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_question/docs/youra_research/.data_cache/models"
    ):
        """
        Initialize Llama model with FP16 and device_map.

        Args:
            model_id: HuggingFace model identifier
            cache_dir: Path to model cache
        """
        self.model_id = model_id
        self.cache_dir = cache_dir

        print(f"Loading {model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=cache_dir
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            cache_dir=cache_dir
        )
        self.model.eval()
        print(f"Model loaded on {self.model.device}")

    def generate(
        self,
        questions: List[str],
        batch_size: int = 8,
        max_tokens: int = 100,
        temperature: float = 1.0,
        top_p: float = 1.0
    ) -> List[Tuple[str, torch.Tensor]]:
        """
        Generate answers for questions and extract logits.

        Args:
            questions: List of question strings
            batch_size: Batch size for generation
            max_tokens: Maximum new tokens per answer
            temperature: Generation temperature
            top_p: Nucleus sampling threshold

        Returns:
            List of (answer_text, logits) tuples
        """
        results = []

        for i in range(0, len(questions), batch_size):
            batch = questions[i:i+batch_size]

            # Format with chat template
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.model.device)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=False,  # Deterministic
                    return_dict_in_generate=True,
                    output_scores=True
                )

            # Decode answers
            answers = self.tokenizer.batch_decode(
                outputs.sequences[:, inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )

            # Extract logits from first generated token (uncertainty signal)
            # scores is tuple of tensors (batch_size, vocab_size)
            logits = outputs.scores[0]  # First token logits

            for answer, logit in zip(answers, logits):
                results.append((answer.strip(), logit.cpu()))

        return results

    def enable_dropout(self, rate: float = 0.1):
        """
        Enable dropout layers during inference for MC Dropout.

        Args:
            rate: Dropout rate (default 0.1 for Llama)
        """
        self.model.train()  # Enable dropout
        for module in self.model.modules():
            if isinstance(module, torch.nn.Dropout):
                module.p = rate
