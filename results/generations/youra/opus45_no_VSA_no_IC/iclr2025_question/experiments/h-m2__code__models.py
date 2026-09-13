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

    def get_hidden_states(self, question: str, layer_idx: int, token_position: str = "last"):
        """Extract hidden state at specified layer for a question string."""
        inputs = self.tokenizer(question, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                output_hidden_states=True,
            )
        hidden_states = out.hidden_states[layer_idx]
        if token_position == "last":
            seq_len = inputs["attention_mask"].sum().item()
            hidden = hidden_states[0, seq_len - 1, :]
        else:
            hidden = hidden_states[0, -1, :]
        return hidden.cpu().numpy()

    def unload(self):
        """Unload model to free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
