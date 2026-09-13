# model.py - Llama-3-8B-Instruct loading and generation
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import MODEL_ID, DTYPE, DEVICE_MAP, MAX_NEW_TOKENS, NUM_SAMPLES, TEMPERATURE


def load_model_and_tokenizer(model_id: str = MODEL_ID):
    """Load model and tokenizer with bf16 and device_map=auto."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.bfloat16 if DTYPE == "bfloat16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map=DEVICE_MAP,
        trust_remote_code=True,
    )
    model.eval()
    return model, tokenizer


def generate_greedy(model, tokenizer, prompt: str) -> tuple[str, torch.Tensor]:
    """Generate greedy response and return (text, last_token_logits)."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    generated_ids = outputs.sequences[0, inputs.input_ids.shape[1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True)
    last_logits = outputs.scores[-1][0] if outputs.scores else None
    return text, last_logits


def generate_samples(model, tokenizer, prompt: str, n: int = NUM_SAMPLES,
                     temperature: float = TEMPERATURE) -> list[str]:
    """Generate n temperature-sampled responses."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    samples = []
    with torch.no_grad():
        for _ in range(n):
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=temperature,
                pad_token_id=tokenizer.pad_token_id,
            )
            generated_ids = outputs[0, inputs.input_ids.shape[1]:]
            text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            samples.append(text)
    return samples
