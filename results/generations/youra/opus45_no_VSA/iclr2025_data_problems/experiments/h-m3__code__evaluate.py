import torch
import numpy as np
from config import Config


def build_fewshot_prompt(item: dict, fewshot_examples: list[dict], num_fewshot: int) -> str:
    """Build few-shot prompt with examples + target question."""
    prompt_parts = []
    for ex in fewshot_examples[:num_fewshot]:
        q = ex["question"]
        choices = ex["choices"]
        ans_idx = ex["answer"]
        choice_str = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])
        prompt_parts.append(f"Question: {q}\n{choice_str}\nAnswer: {chr(65+ans_idx)}")

    q = item["question"]
    choices = item["choices"]
    choice_str = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])
    prompt_parts.append(f"Question: {q}\n{choice_str}\nAnswer:")

    return "\n\n".join(prompt_parts)


def score_mcq_loglikelihood(model, tokenizer, item: dict, fewshot_examples: list[dict],
                            num_fewshot: int, device) -> int:
    """Score MCQ via log-likelihood. Returns predicted choice idx."""
    prompt = build_fewshot_prompt(item, fewshot_examples, num_fewshot)
    choices = ["A", "B", "C", "D"]
    logprobs = []

    for choice in choices:
        full_text = prompt + " " + choice
        input_ids = tokenizer(full_text, return_tensors="pt").input_ids.to(device)

        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits

        # Get log-prob of the choice token (last token before the choice)
        choice_token_id = tokenizer(" " + choice, add_special_tokens=False).input_ids[-1]
        logprob = torch.log_softmax(logits[0, -2], dim=-1)[choice_token_id].item()
        logprobs.append(logprob)

    return int(np.argmax(logprobs))


def eval_model_on_mmlu(model, tokenizer, mmlu: list[dict], cfg: Config) -> np.ndarray:
    """Evaluate model on MMLU. Returns bool correctness array."""
    device = next(model.parameters()).device
    model.eval()

    # Use first few samples as fewshot examples
    fewshot_examples = mmlu[:cfg.num_fewshot]
    eval_samples = mmlu[cfg.num_fewshot:]

    correct = []
    for i, item in enumerate(eval_samples):
        pred = score_mcq_loglikelihood(model, tokenizer, item, fewshot_examples,
                                       cfg.num_fewshot, device)
        correct.append(pred == item["answer"])
        if (i + 1) % 50 == 0:
            print(f"  Evaluated {i+1}/{len(eval_samples)}")

    return np.array(correct)


def eval_all(models: dict, mmlu: list[dict], cfg: Config) -> dict:
    """Evaluate all models on MMLU. Returns {model_id: correctness_array}."""
    results = {}
    for model_id, (model, tokenizer) in models.items():
        print(f"Evaluating {model_id}...")
        results[model_id] = eval_model_on_mmlu(model, tokenizer, mmlu, cfg)
    return results
