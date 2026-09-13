"""Mistral-7B text generator for answer generation."""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List


class MistralGenerator:
    """Mistral-7B generator for diverse answer sampling."""

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        device: str = "cuda",
        dtype = torch.float16
    ):
        """
        Initialize Mistral-7B model.

        Args:
            model_name: HuggingFace model identifier
            device: Device to run model on
            dtype: Data type for model weights
        """
        self.model_name = model_name
        self.device = device
        self.dtype = dtype
        self.model = None
        self.tokenizer = None

    def load(self) -> None:
        """Load model and tokenizer."""
        print(f"Loading {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=self.dtype
        )
        # Set pad token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Model loaded successfully")

    def generate_samples(
        self,
        question: str,
        k: int = 10,
        temperature: float = 0.7,
        max_new_tokens: int = 50,
        seed: int = 42
    ) -> List[str]:
        """
        Generate K diverse answers for a question.

        Args:
            question: Input question string
            k: Number of samples to generate
            temperature: Sampling temperature
            max_new_tokens: Maximum tokens to generate
            seed: Random seed

        Returns:
            List of K generated answer strings
        """
        if self.model is None:
            self.load()

        # Set seed for reproducibility
        torch.manual_seed(seed)

        # Prepare prompt
        prompt = f"Question: {question}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate K samples
        answers = []
        for i in range(k):
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode and extract answer
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = generated_text.split("Answer:")[-1].strip()
            answers.append(answer)

        return answers
