"""Model loading for H-M2 inference comparison."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import config as cfg


def load_tokenizer(model_name: str):
    """Load tokenizer with pad_token = eos_token."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_baseline_model(model_name: str):
    """Load baseline model for inference (bfloat16, device_map='auto', .eval())."""
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return model


def load_bidpo_model(base_model_name: str, checkpoint_path: str):
    """Load BiDPO model: base arch + trained state_dict, .eval()."""
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    state_dict = torch.load(checkpoint_path, map_location="cpu")
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model
