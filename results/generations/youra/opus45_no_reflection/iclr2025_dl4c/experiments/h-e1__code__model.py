"""Baseline and Feedback models for EVAF H-E1."""

import torch
from transformers import AutoModelForSeq2SeqLM, AutoModelForCausalLM, AutoTokenizer
from config import CONFIG


class BaselineModel:
    """CodeT5-770M baseline code generator."""

    def __init__(self, model_id: str = None, device: str = None, seed: int = None):
        model_id = model_id or CONFIG["baseline_model_id"]
        device = device or CONFIG["device"]
        seed = seed if seed is not None else CONFIG["seed"]

        torch.manual_seed(seed)
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(device)
        self.model.eval()

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Generate code completion for prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


class FeedbackModel:
    """CodeLlama-7b-Instruct feedback generator."""

    def __init__(self, model_id: str = None, temperature: float = None,
                 max_tokens: int = None, device: str = None):
        model_id = model_id or CONFIG["feedback_model_id"]
        self.temperature = temperature if temperature is not None else CONFIG["temperature"]
        self.max_tokens = max_tokens if max_tokens is not None else CONFIG["max_tokens"]
        device = device or CONFIG["device"]

        torch.manual_seed(CONFIG["seed"])
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()

    def _build_prompt(self, problem: dict, failing_code: str) -> str:
        """Build instruction prompt for CodeLlama."""
        return f"""[INST] The following code fails some tests:

```python
{failing_code}
```

Problem description:
{problem['prompt']}

Analyze what is wrong and provide a corrected implementation. Output ONLY the corrected Python function inside a ```python code block. [/INST]"""

    def critique(self, problem: dict, failing_code: str) -> str:
        """Generate critique and fix suggestion."""
        torch.manual_seed(CONFIG["seed"])
        prompt = self._build_prompt(problem, failing_code)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return response
