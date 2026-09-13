# model.py - h-m3: HF model load with hidden states for RCI flip detection
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import CONFIG


def load_model(model_id=None, device=None):
    """Load LLaMA-2-7B with output_hidden_states enabled."""
    model_id = model_id or CONFIG["model_id"]
    device = device or CONFIG["device"]
    dtype = torch.float16 if CONFIG["dtype"] == "float16" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto",
        output_hidden_states=True,
    )
    model.eval()
    return model, tokenizer


def get_hidden_states(model, tokenizer, prompt, device=None):
    """Get hidden states for a prompt. Returns tuple of (33,) tensors."""
    device = device or CONFIG["device"]
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    return outputs.hidden_states  # tuple of 33 tensors [B, seq, 4096]


def greedy_decode(model, tokenizer, prompt, max_new_tokens=50, device=None):
    """Greedy decode to get model's answer."""
    device = device or CONFIG["device"]
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            pad_token_id=tokenizer.pad_token_id,
        )

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def label_hallucination(model, tokenizer, prompt, correct_answer):
    """Check if model's greedy answer matches correct answer."""
    model_answer = greedy_decode(model, tokenizer, prompt, max_new_tokens=50)
    correct_lower = correct_answer.lower().strip()
    model_lower = model_answer.lower().strip()
    is_correct = correct_lower in model_lower or model_lower in correct_lower
    return not is_correct, model_answer
