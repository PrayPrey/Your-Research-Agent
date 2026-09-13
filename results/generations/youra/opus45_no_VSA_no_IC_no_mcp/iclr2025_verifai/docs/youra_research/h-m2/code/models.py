import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import CONFIG

_model_cache = {}

def load_hf_model(model_id: str = None):
    model_id = model_id or CONFIG["base_model_id"]
    if model_id in _model_cache:
        return _model_cache[model_id]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        attn_implementation="eager"
    )
    _model_cache[model_id] = (model, tokenizer)
    return model, tokenizer

def generate_code(model_ref, tokenizer, prompt: str,
                  max_new_tokens: int = None, temperature: float = None) -> str:
    max_new_tokens = max_new_tokens or CONFIG["max_new_tokens"]
    temperature = temperature if temperature is not None else CONFIG["temperature"]

    inputs = tokenizer(prompt, return_tensors="pt").to(model_ref.device)
    with torch.no_grad():
        out = model_ref.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0,
            temperature=temperature if temperature > 0 else None,
            top_p=CONFIG.get("top_p", 0.95) if temperature > 0 else None,
            pad_token_id=tokenizer.eos_token_id
        )
    return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
