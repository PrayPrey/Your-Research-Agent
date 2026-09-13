"""Model loading and hidden state extraction."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import TORCH_DTYPE, DEVICE_MAP, TEMPERATURE


class ModelWrapper:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.model = None
        self.tokenizer = None

    def load(self):
        """Load model (fp16, device_map=auto) + tokenizer."""
        dtype = torch.float16 if TORCH_DTYPE == "float16" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            device_map=DEVICE_MAP,
            trust_remote_code=True,
        )
        self.model.eval()

    def generate(self, prompt: str, n_samples: int, temperature: float) -> list:
        """Generate n_samples responses for prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = []
        with torch.no_grad():
            for _ in range(n_samples):
                out = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
                text = self.tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
                outputs.append(text.strip())
        return outputs

    def get_hidden_states(self, input_ids, attention_mask):
        """Forward with output_hidden_states=True, return all layer states."""
        with torch.no_grad():
            out = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
            )
        return out.hidden_states
