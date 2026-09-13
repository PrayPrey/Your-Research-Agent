"""Model loading and response generation with logit access."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model(model_name: str, hf_token: str = None, torch_dtype: str = "float16"):
    """Load Llama-2-7B-chat in FP16 with device_map='auto'."""
    dtype = torch.float16 if torch_dtype == "float16" else torch.bfloat16

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map="auto",
        token=hf_token
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return model, tokenizer


def generate_responses(
    model,
    tokenizer,
    question: str,
    n_samples: int = 10,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_new_tokens: int = 128,
    seed: int = 42
) -> list[dict]:
    """Generate n_samples responses with per-token logits.

    Returns list of {'text': str, 'scores': list[Tensor]}.
    """
    prompt = f"[INST] {question} [/INST]"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_len = inputs.input_ids.shape[1]

    responses = []
    for i in range(n_samples):
        torch.manual_seed(seed + i)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed + i)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                output_scores=True,
                return_dict_in_generate=True,
                pad_token_id=tokenizer.pad_token_id
            )

        response_ids = outputs.sequences[0][prompt_len:]
        response_text = tokenizer.decode(response_ids, skip_special_tokens=True)

        responses.append({
            "text": response_text,
            "scores": outputs.scores  # tuple of [1, vocab_size] tensors
        })

    return responses
