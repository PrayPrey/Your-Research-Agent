"""Model wrapper for SpecBridge using HuggingFace transformers."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import MODEL_NAME, DEVICE, GPU_ID

class LLMWrapper:
    """Wrapper for HuggingFace code generation models."""

    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LLMWrapper._model is None:
            print(f"Loading model {MODEL_NAME}...")
            device_map = f"cuda:{GPU_ID}" if torch.cuda.is_available() else "cpu"

            LLMWrapper._tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                trust_remote_code=True
            )

            LLMWrapper._model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=device_map,
                trust_remote_code=True
            )

            if LLMWrapper._tokenizer.pad_token is None:
                LLMWrapper._tokenizer.pad_token = LLMWrapper._tokenizer.eos_token

            print(f"Model loaded on {device_map}")

    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.0) -> str:
        """Generate text from prompt."""
        messages = [
            {"role": "user", "content": prompt}
        ]

        text = LLMWrapper._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = LLMWrapper._tokenizer([text], return_tensors="pt").to(LLMWrapper._model.device)

        with torch.no_grad():
            if temperature > 0:
                outputs = LLMWrapper._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    pad_token_id=LLMWrapper._tokenizer.eos_token_id
                )
            else:
                outputs = LLMWrapper._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=LLMWrapper._tokenizer.eos_token_id
                )

        generated_text = LLMWrapper._tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return generated_text.strip()

# Global model instance
_llm = None

def get_llm():
    """Get or create the global LLM instance."""
    global _llm
    if _llm is None:
        _llm = LLMWrapper()
    return _llm
