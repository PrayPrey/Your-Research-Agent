"""Extract attention weights from LLM."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class AttentionExtractor:
    """Extract last-layer attention from Llama-2."""

    def __init__(self, model_name="gpt2", device_map=None):
        print(f"Loading model: {model_name}...")

        # Handle different dtype for CPU vs GPU
        dtype = torch.float32 if device_map is None else torch.float16

        if device_map is None:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                output_attentions=True,
                torch_dtype=dtype
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                output_attentions=True,
                torch_dtype=dtype,
                device_map=device_map
            )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model.eval()
        print("Model loaded.")

    def extract(self, question):
        """Extract last-layer attention. Returns: [seq_len, seq_len]"""
        inputs = self.tokenizer(question, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model(**inputs, output_attentions=True)

        # Last layer, averaged across heads: [1, heads, seq, seq] -> [seq, seq]
        attn = outputs.attentions[-1].mean(dim=1).squeeze(0).cpu()
        return attn
