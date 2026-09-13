"""CodeLLM wrapper for generation."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import config


class CodeLLM:
    def __init__(self, model_id: str = config.MODEL_ID):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate(self, prompt: str, temperature: float = config.TEMPERATURE,
                 max_tokens: int = config.MAX_TOKENS) -> str:
        """Generate text from prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature if temperature > 0 else None,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        generated = outputs[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(generated, skip_special_tokens=True)
