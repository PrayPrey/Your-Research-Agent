"""H-M4 Generation: Load model and generate with scores."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm


def load_model(model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
    """Load model and tokenizer with fp16."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    return model, tokenizer


def generate_with_scores(model, tokenizer, prompt: str, max_new_tokens: int = 50) -> dict:
    """Generate with per-step logits."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=tokenizer.pad_token_id
        )

    input_len = inputs.input_ids.shape[1]
    generated_ids = outputs.sequences[0, input_len:]

    # Stack scores: list of [1, vocab] -> [gen_len, vocab]
    if outputs.scores:
        scores = torch.stack([s[0] for s in outputs.scores], dim=0)
    else:
        scores = torch.empty(0, tokenizer.vocab_size)

    text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    return {
        "text": text,
        "scores": scores,
        "generated_ids": generated_ids
    }


def run_generation_batch(model, tokenizer, questions: list, max_new_tokens: int = 50) -> list:
    """Generate over all questions with scores."""
    results = []
    for q in tqdm(questions, desc="Generating"):
        prompt = f"Question: {q['question']}\nAnswer:"
        out = generate_with_scores(model, tokenizer, prompt, max_new_tokens)
        results.append({
            "id": q.get("question_id", q.get("id", len(results))),
            "question": q["question"],
            "gold_answers": q.get("answer", {}).get("aliases", []) if isinstance(q.get("answer"), dict) else [str(q.get("answer", ""))],
            "text": out["text"],
            "scores": out["scores"],
            "generated_ids": out["generated_ids"]
        })
    return results
