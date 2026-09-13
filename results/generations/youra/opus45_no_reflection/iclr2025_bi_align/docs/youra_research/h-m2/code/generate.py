"""Response generation for H-M2."""
import torch
from tqdm import tqdm
from data import format_mistral_prompt
import config as cfg


def generate_responses(model, tokenizer, prompts: list, max_new_tokens: int,
                       temperature: float, top_p: float, seed: int) -> list:
    """Seeded do_sample=True generation. Returns decoded response strings."""
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    responses = []
    model.eval()

    for prompt in tqdm(prompts, desc="Generating"):
        formatted = format_mistral_prompt(prompt)
        inputs = tokenizer(
            formatted,
            return_tensors="pt",
            truncation=True,
            max_length=cfg.MAX_PROMPT_LENGTH
        )
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=cfg.DO_SAMPLE,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=tokenizer.pad_token_id
            )

        gen_ids = outputs[0][inputs["input_ids"].shape[1]:]
        response = tokenizer.decode(gen_ids, skip_special_tokens=True)
        responses.append(response)

    return responses
