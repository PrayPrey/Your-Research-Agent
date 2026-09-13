"""Response generation with logit access (from h-e1 spec)"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import config


def load_model(model_name: str = None):
    """Load model and tokenizer with FP16."""
    model_name = model_name or config.MODEL_NAME
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=config.HF_TOKEN)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map=config.DEVICE_MAP,
        token=config.HF_TOKEN
    )
    model.eval()
    return model, tokenizer


def generate_responses(model, tokenizer, question: str, n_samples: int = None,
                       temperature: float = None, max_new_tokens: int = None,
                       seed: int = None) -> list[dict]:
    """Generate n_samples responses with logit scores."""
    n_samples = n_samples or config.NUM_RESPONSES
    temperature = temperature or config.TEMPERATURE
    max_new_tokens = max_new_tokens or config.MAX_NEW_TOKENS
    seed = seed or config.SEED

    prompt = f"Question: {question}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    results = []
    for i in range(n_samples):
        torch.manual_seed(seed + i)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=config.TOP_P,
                do_sample=True,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=tokenizer.pad_token_id
            )

        gen_ids = outputs.sequences[0, inputs.input_ids.shape[1]:]
        text = tokenizer.decode(gen_ids, skip_special_tokens=True)
        scores = [s[0].cpu() for s in outputs.scores]  # list of [vocab_size] tensors

        results.append({"text": text, "scores": scores})

    return results
