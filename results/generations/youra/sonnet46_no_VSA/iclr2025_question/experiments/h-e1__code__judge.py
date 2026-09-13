"""LM-as-a-judge correctness labeling using Qwen-2.5-7B-Instruct."""
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import (
    JUDGE_ID, LLM_ID, JUDGE_BATCH_SIZE, JUDGE_PROMPT, JUDGE_LOAD_KWARGS,
)


def load_judge(model_id: str = JUDGE_ID):
    """Load judge model. Must differ from generator model family."""
    assert model_id.split("/")[0] != LLM_ID.split("/")[0], (
        "Judge must differ from generator model family"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


def _parse_yes_no(text: str) -> int | None:
    """Parse YES/NO from judge output. Returns 1 for YES, 0 for NO, None if ambiguous."""
    text_lower = text.strip().lower()
    # Check first token first
    first_word = text_lower.split()[0] if text_lower.split() else ""
    if first_word.startswith("yes"):
        return 1
    if first_word.startswith("no"):
        return 0
    # Broader search
    if "yes" in text_lower[:20]:
        return 1
    if "no" in text_lower[:20]:
        return 0
    return None


def _alias_match(answer: str, aliases: list[str]) -> int:
    """Exact string match against aliases. Fallback when judge is ambiguous."""
    answer_lower = answer.strip().lower()
    return int(any(answer_lower == a.strip().lower() for a in aliases))


def label_correctness(
    model,
    tokenizer,
    questions: list[str],
    greedy_answers: list[str],
    aliases_list: list[list[str]],
    batch_size: int = JUDGE_BATCH_SIZE,
) -> np.ndarray:
    """Returns binary correctness labels shape (N_PROMPTS,) dtype int."""
    labels = []

    for i in tqdm(range(0, len(questions), batch_size), desc="Judge labeling"):
        batch_qs = questions[i: i + batch_size]
        batch_ans = greedy_answers[i: i + batch_size]
        batch_aliases = aliases_list[i: i + batch_size]

        prompts = [
            JUDGE_PROMPT.format(question=q, answer=a)
            for q, a in zip(batch_qs, batch_ans)
        ]

        inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=10,
            )

        prompt_len = inputs.input_ids.shape[1]
        decoded = tokenizer.batch_decode(out[:, prompt_len:], skip_special_tokens=True)

        for j, (dec, ans, aliases) in enumerate(zip(decoded, batch_ans, batch_aliases)):
            parsed = _parse_yes_no(dec)
            if parsed is not None:
                labels.append(parsed)
            else:
                # Fallback: alias matching
                labels.append(_alias_match(ans, aliases))

    return np.array(labels, dtype=int)
