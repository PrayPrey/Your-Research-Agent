"""Data: TriviaQA loader (reused from H-E1)."""

import re
import unicodedata
from datasets import load_dataset
from tqdm import tqdm
import torch


def load_triviaqa(split: str, n: int):
    if split == "train":
        ds = load_dataset("trivia_qa", "rc", split="train")
    else:
        ds = load_dataset("trivia_qa", "rc", split="validation")

    if n > len(ds):
        raise ValueError(f"Requested {n} examples but only {len(ds)} available")
    return ds.select(range(n))


def format_prompt(example: dict) -> str:
    question = example["question"]
    return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nAnswer concisely: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"


def normalize_answer(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = " ".join(s.split())
    return s


def label_correctness(pred_answer: str, gold_aliases: list) -> int:
    if not gold_aliases:
        return 0
    pred_norm = normalize_answer(pred_answer)
    for alias in gold_aliases:
        if normalize_answer(alias) == pred_norm:
            return 1
    return 0


def build_labeled_dataset_batched(model, tokenizer, dataset, n: int, batch_size: int = 8, max_new_tokens: int = 32) -> list:
    results = []
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    total = min(n, len(dataset))

    for i in tqdm(range(0, total, batch_size), desc="Generating answers"):
        batch_end = min(i + batch_size, total)
        batch_examples = [dataset[j] for j in range(i, batch_end)]

        prompts = [format_prompt(ex) for ex in batch_examples]

        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
                temperature=None,
                top_p=None
            )

        for j, (example, output) in enumerate(zip(batch_examples, outputs)):
            prompt_len = inputs.input_ids[j].shape[0]
            generated = output[prompt_len:]
            answer = tokenizer.decode(generated, skip_special_tokens=True).strip()
            gold_aliases = example["answer"]["aliases"]
            label = label_correctness(answer, gold_aliases)
            results.append({"prompt": prompts[j], "label": label, "answer": answer})

    return results


def load_triviaqa_splits(n_train: int, n_val: int):
    train_ds = load_triviaqa("train", n_train)
    val_ds = load_triviaqa("validation", n_val)
    return train_ds, val_ds
