"""Llama-2-7B baseline model with multi-sampling capability."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LlamaGenerator:
    """Llama-2-7B generation with multi-sampling capability."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        device: str = "cuda"
    ):
        """Load Llama-2-7B model."""
        self.device = device
        self.model_name = model_name

        print(f"    Loading {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None
        )
        self.model.eval()

    def generate_single(
        self,
        input_text: str,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> str:
        """Generate single completion."""
        inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove input text from output
        generated_text = generated_text[len(input_text):].strip()
        return generated_text

    def generate_multiple(
        self,
        input_text: str,
        num_samples: int = 5,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> list[str]:
        """Generate multiple diverse completions (for consistency scoring)."""
        samples = []
        for _ in range(num_samples):
            sample = self.generate_single(input_text, max_tokens, temperature)
            samples.append(sample)
        return samples
