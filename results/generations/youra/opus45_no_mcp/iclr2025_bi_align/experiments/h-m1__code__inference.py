"""Inference module for extracting logprobs from language models."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, List, Tuple
from tqdm import tqdm

from data import Task


def load_model(model_id: str) -> Tuple:
    """Load HuggingFace model in fp16 on CUDA, eval mode."""
    print(f"Loading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    model.eval()
    return model, tokenizer


def get_sequence_logprob(model, tokenizer, prompt: str, answer: str) -> float:
    """Compute sum of log P(answer_token | prompt, prev_answer_tokens)."""
    prompt_ids = tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=True)
    answer_ids = tokenizer.encode(answer, return_tensors="pt", add_special_tokens=False)

    input_ids = torch.cat([prompt_ids, answer_ids], dim=1).to(model.device)

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits

    prompt_len = prompt_ids.shape[1]
    answer_len = answer_ids.shape[1]

    answer_logits = logits[:, prompt_len-1:prompt_len+answer_len-1, :]
    log_probs = torch.log_softmax(answer_logits, dim=-1)

    answer_ids_flat = answer_ids.to(model.device)
    token_logprobs = log_probs.gather(2, answer_ids_flat.unsqueeze(-1)).squeeze(-1)

    return token_logprobs.sum().item()


def get_length_normalized_logprob(model, tokenizer, prompt: str, answer: str) -> float:
    """Get sequence logprob normalized by answer length."""
    answer_ids = tokenizer.encode(answer, add_special_tokens=False)
    seq_logprob = get_sequence_logprob(model, tokenizer, prompt, answer)
    return seq_logprob / max(len(answer_ids), 1)


def run_inference_on_tasks(
    model, tokenizer, tasks: List[Task], batch_size: int = 8
) -> Dict[str, Dict]:
    """Run inference on all tasks, return per-task logprobs."""
    results = {}

    for task in tqdm(tasks, desc="Inference"):
        try:
            correct_lp = get_length_normalized_logprob(
                model, tokenizer, task["question"], task["correct_answer"]
            )

            wrong_lps = []
            for wrong in task["incorrect_answers"]:
                if wrong:
                    wrong_lp = get_length_normalized_logprob(
                        model, tokenizer, task["question"], wrong
                    )
                    wrong_lps.append(wrong_lp)

            max_wrong_lp = max(wrong_lps) if wrong_lps else float("-inf")

            results[task["task_id"]] = {
                "correct_logprob_norm": correct_lp,
                "max_wrong_logprob_norm": max_wrong_lp
            }
        except Exception as e:
            print(f"Error on task {task['task_id']}: {e}")
            results[task["task_id"]] = {
                "correct_logprob_norm": 0.0,
                "max_wrong_logprob_norm": 0.0
            }

    return results
