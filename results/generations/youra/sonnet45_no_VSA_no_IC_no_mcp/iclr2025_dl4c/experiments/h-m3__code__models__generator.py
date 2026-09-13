"""Code generation using CodeGen model."""
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class CodeGenModel:
    """Wrapper for CodeGen model."""

    def __init__(self, model_name: str = "Salesforce/codegen-350M-mono"):
        """Load model and tokenizer."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading {model_name} on {self.device}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        top_p: float = 0.95,
        max_tokens: int = 256
    ) -> str:
        """Generate single code sample."""
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Strip prompt from output
        if generated.startswith(prompt):
            generated = generated[len(prompt):]

        return generated.strip()

    def batch_generate(
        self,
        prompts: List[str],
        batch_size: int = 4,
        **kwargs
    ) -> List[str]:
        """Generate code for batch of prompts."""
        results = []

        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            for prompt in batch:
                code = self.generate(prompt, **kwargs)
                results.append(code)

        return results
