import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import openai
from config import CONFIG, OPENAI_API_KEY

_model_cache = {}

def load_hf_model(model_id: str):
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

def generate_code(model_ref, tokenizer, prompt: str, is_openai: bool = False,
                  max_new_tokens: int = None, temperature: float = None) -> str:
    max_new_tokens = max_new_tokens or CONFIG["max_new_tokens"]
    temperature = temperature if temperature is not None else CONFIG["temperature"]

    if is_openai:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        for attempt in range(CONFIG["openai_max_retries"]):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_new_tokens
                )
                return resp.choices[0].message.content
            except openai.RateLimitError:
                time.sleep(CONFIG["openai_backoff_base_sec"] ** attempt)
                continue
        raise RuntimeError("GPT-4 call failed after max retries")

    inputs = tokenizer(prompt, return_tensors="pt").to(model_ref.device)
    with torch.no_grad():
        out = model_ref.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
