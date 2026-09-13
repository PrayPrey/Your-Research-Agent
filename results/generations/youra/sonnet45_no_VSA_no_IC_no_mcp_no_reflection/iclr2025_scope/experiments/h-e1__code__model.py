import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class CheckpointLoader:
    def __init__(self, model_name: str, device: str, dtype: str):
        self.model_name = model_name
        self.device = device
        self.dtype = getattr(torch, dtype)

    def load_model(self) -> AutoModelForCausalLM:
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=self.dtype,
            device_map={"": 0}
        )
        return model

    def load_tokenizer(self) -> AutoTokenizer:
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        return tokenizer

    def get_memory_stats(self) -> dict:
        if torch.cuda.is_available():
            allocated = torch.cuda.max_memory_allocated() / 1e9
            reserved = torch.cuda.max_memory_reserved() / 1e9
            return {"allocated_gb": allocated, "reserved_gb": reserved, "peak_gb": allocated}
        return {"allocated_gb": 0, "reserved_gb": 0, "peak_gb": 0}
