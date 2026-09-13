# H-M1 Model loading and token entropy computation
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import config

def load_model():
    """Load LLaMA-2-7B with float16."""
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        config.MODEL_ID, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

def compute_response_entropy(model, tokenizer, question: str, max_new_tokens: int) -> tuple[float, str, int]:
    """Generate greedy response, return (mean_token_entropy, response_text, num_tokens)."""
    prompt = f"Q: {question}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            output_scores=True, return_dict_in_generate=True
        )

    generated_ids = outputs.sequences[0, inputs.input_ids.shape[1]:]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    num_tokens = len(generated_ids)

    if not outputs.scores:
        return 0.0, response, num_tokens

    entropies = []
    for logits in outputs.scores:
        probs = torch.softmax(logits[0], dim=-1)
        probs = probs.clamp(min=1e-10)  # numerical stability
        ent = -torch.sum(probs * torch.log(probs)).item()
        entropies.append(ent)

    mean_entropy = sum(entropies) / len(entropies) if entropies else 0.0
    return mean_entropy, response, num_tokens
