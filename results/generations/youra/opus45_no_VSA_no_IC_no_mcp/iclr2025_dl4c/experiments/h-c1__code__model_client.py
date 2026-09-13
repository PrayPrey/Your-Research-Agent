"""Model client for code generation with CodeLlama."""
import re
import random
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import CFG


class ModelClient:
    def __init__(
        self,
        model_id: str = None,
        temperature: float = None,
        max_new_tokens: int = None,
        seed: int = None,
    ):
        self.model_id = model_id or CFG.model_id
        self.temperature = temperature if temperature is not None else CFG.temperature
        self.max_new_tokens = max_new_tokens or CFG.max_new_tokens
        self.seed = seed if seed is not None else CFG.seed

        random.seed(self.seed)
        torch.manual_seed(self.seed)

        print(f"Loading model: {self.model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Model loaded")

    def generate(self, prompt: str) -> str:
        """Generate code completion from prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature if self.temperature > 0 else None,
                do_sample=self.temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        text = self.tokenizer.decode(
            out_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True
        )
        return self._extract_code(text)

    def _extract_code(self, text: str) -> str:
        """Extract code from markdown fences if present."""
        match = re.search(r"```(?:python)?\n?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


if __name__ == "__main__":
    client = ModelClient()
    code = client.generate("def add(a, b):\n    ")
    print(f"Generated: {code[:200]}")
