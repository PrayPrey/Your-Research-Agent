"""LLM generation: stochastic (N=5) and greedy with token log-probs."""
import os
import pickle
import torch
from pathlib import Path
from tqdm import tqdm
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import (
    DATASET_ID, DATASET_CONFIG, DATASET_SPLIT, N_PROMPTS, SEED,
    LLM_ID, N_SAMPLES, TEMPERATURE, TOP_P, MAX_NEW_TOKENS,
    CHECKPOINT_PATH,
)


def load_dataset_slice(seed: int = SEED, n: int = N_PROMPTS) -> list[dict]:
    """Load n TriviaQA examples, shuffled with given seed."""
    ds = load_dataset(DATASET_ID, DATASET_CONFIG, split=DATASET_SPLIT)
    ds = ds.shuffle(seed=seed)
    ds = ds.select(range(n))
    result = []
    for row in ds:
        aliases = list(row["answer"]["aliases"]) + list(row["answer"]["normalized_aliases"])
        result.append({"question": row["question"], "aliases": aliases})
    assert len(result) == n, f"Expected {n} samples, got {len(result)}"
    return result


def load_llm(model_id: str = LLM_ID):
    """Load LLM with bfloat16 and device_map=auto."""
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


def _generate_stochastic_single(
    model, tokenizer, question: str, n_samples: int, temperature: float, top_p: float
) -> list[str]:
    """Single-item fallback for OOM recovery."""
    inputs = tokenizer([question], return_tensors="pt", padding=True).to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=MAX_NEW_TOKENS,
            num_return_sequences=n_samples,
        )
    decoded = tokenizer.batch_decode(
        out[:, inputs.input_ids.shape[1]:], skip_special_tokens=True
    )
    return decoded[:n_samples]


def generate_stochastic(
    model,
    tokenizer,
    questions: list[str],
    n_samples: int = N_SAMPLES,
    temperature: float = TEMPERATURE,
    top_p: float = TOP_P,
    batch_size: int = 4,
    existing: list[list[str]] | None = None,
) -> list[list[str]]:
    """Generate n_samples stochastic responses per question. Returns (N, n_samples) list."""
    results = list(existing) if existing else []
    start_idx = len(results)

    for i in tqdm(range(start_idx, len(questions), batch_size), desc="Stochastic gen"):
        batch_qs = questions[i: i + batch_size]
        try:
            inputs = tokenizer(batch_qs, return_tensors="pt", padding=True, truncation=True).to(model.device)
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    max_new_tokens=MAX_NEW_TOKENS,
                    num_return_sequences=n_samples,
                )
            # out shape: [B * n_samples, L_total]
            decoded = tokenizer.batch_decode(
                out[:, inputs.input_ids.shape[1]:], skip_special_tokens=True
            )
            for j in range(len(batch_qs)):
                results.append(decoded[j * n_samples: (j + 1) * n_samples])
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            for q in batch_qs:
                results.append(
                    _generate_stochastic_single(model, tokenizer, q, n_samples, temperature, top_p)
                )

    return results


def generate_greedy(
    model,
    tokenizer,
    questions: list[str],
    batch_size: int = 4,
) -> tuple[list[str], list[list[float]]]:
    """Greedy decode with per-token log-probs. Fails fast if output_scores unavailable."""
    all_answers, all_logprobs = [], []

    for i in tqdm(range(0, len(questions), batch_size), desc="Greedy gen"):
        batch_qs = questions[i: i + batch_size]
        inputs = tokenizer(batch_qs, return_tensors="pt", padding=True, truncation=True).to(model.device)
        prompt_len = inputs.input_ids.shape[1]
        with torch.no_grad():
            out = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=MAX_NEW_TOKENS,
                output_scores=True,
                return_dict_in_generate=True,
            )
        assert out.scores is not None, "output_scores=True required; check model/transformers version"

        # out.scores: tuple of T tensors, each (B, vocab)
        stacked = torch.stack(out.scores, dim=0)           # [T, B, vocab]
        log_probs_full = stacked.log_softmax(-1)            # [T, B, vocab]
        gen_ids = out.sequences[:, prompt_len:]             # [B, T]

        # Gather log-prob of the actually generated token
        token_lp = log_probs_full.gather(
            -1, gen_ids.T.unsqueeze(-1)                    # [T, B, 1]
        ).squeeze(-1)                                       # [T, B]
        token_lp = token_lp.T                              # [B, T]

        decoded = tokenizer.batch_decode(gen_ids, skip_special_tokens=True)
        for j in range(len(batch_qs)):
            all_answers.append(decoded[j])
            all_logprobs.append(token_lp[j].tolist())

    return all_answers, all_logprobs


def load_or_generate(force: bool = False) -> dict:
    """Load checkpoint if exists and not force, else generate and save."""
    checkpoint = Path(CHECKPOINT_PATH)

    if checkpoint.exists() and not force:
        print(f"Loading checkpoint from {CHECKPOINT_PATH}")
        with open(checkpoint, "rb") as f:
            data = pickle.load(f)
        required_keys = {"stochastic", "greedy_answers", "token_logprobs", "questions", "aliases"}
        assert required_keys <= data.keys(), f"Checkpoint missing keys: {required_keys - data.keys()}"
        print(f"  Loaded {len(data['greedy_answers'])} samples from checkpoint")
        return data

    print("Generating fresh data...")
    samples = load_dataset_slice()
    questions = [s["question"] for s in samples]
    aliases = [s["aliases"] for s in samples]

    model, tokenizer = load_llm()
    print("Running stochastic generation (N=5)...")
    stochastic = generate_stochastic(model, tokenizer, questions)
    print("Running greedy generation with scores...")
    greedy_answers, token_logprobs = generate_greedy(model, tokenizer, questions)

    # Free GPU before NLI/judge models
    del model, tokenizer
    torch.cuda.empty_cache()

    data = {
        "stochastic": stochastic,
        "greedy_answers": greedy_answers,
        "token_logprobs": token_logprobs,
        "questions": questions,
        "aliases": aliases,
    }

    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Checkpoint saved to {CHECKPOINT_PATH}")
    return data
