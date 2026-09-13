"""BSI evaluator: Behavioral Stability Index via paraphrase consistency."""
import json
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_paws(wiki_path: str, qqp_path: str) -> pd.DataFrame:
    with open(wiki_path) as f:
        wiki = json.load(f)
    with open(qqp_path) as f:
        qqp = json.load(f)
    df = pd.concat([pd.DataFrame(wiki), pd.DataFrame(qqp)], ignore_index=True)
    return df[["sentence1", "sentence2", "label"]]


FEW_SHOT_EXAMPLES = """Example 1:
Sentence 1: The cat sat on the mat.
Sentence 2: The mat had a cat sitting on it.
Answer: 1

Example 2:
Sentence 1: I went to the store yesterday.
Sentence 2: Yesterday I visited the market.
Answer: 1

Example 3:
Sentence 1: The quick brown fox jumps over the lazy dog.
Sentence 2: A lazy dog was jumped over by a slow white cat.
Answer: 0

"""


def paraphrase_prompt(s1: str, s2: str, few_shot: bool = False) -> str:
    prefix = FEW_SHOT_EXAMPLES if few_shot else ""
    return f"""{prefix}Are these two sentences paraphrases of each other?
Sentence 1: {s1}
Sentence 2: {s2}
Answer with 1 (yes, paraphrase) or 0 (no, not paraphrase).
Answer:"""


def classify_pair(model, tokenizer, s1: str, s2: str, few_shot: bool = False) -> int:
    prompt = paraphrase_prompt(s1, s2, few_shot)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=5,
            do_sample=False,
            temperature=0.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    gen = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    gen = gen.strip().lower()
    if gen.startswith("1") or "yes" in gen or "paraphrase" in gen:
        return 1
    return 0


def compute_bsi(model, tokenizer, paws_df: pd.DataFrame, few_shot: bool = False) -> float:
    agreements = []
    for _, row in paws_df.iterrows():
        s1, s2 = row["sentence1"], row["sentence2"]
        pred_orig = classify_pair(model, tokenizer, s1, s2, few_shot)
        pred_swap = classify_pair(model, tokenizer, s2, s1, few_shot)
        agreements.append(1 if pred_orig == pred_swap else 0)
    return sum(agreements) / len(agreements)


def evaluate_model_bsi(model_id: str, paws_df: pd.DataFrame, few_shot: bool = False) -> dict:
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        bsi = compute_bsi(model, tokenizer, paws_df, few_shot)
        del model
        torch.cuda.empty_cache()
        return {"model_id": model_id, "bsi": bsi, "n_pairs": len(paws_df), "error": None}
    except Exception as e:
        return {"model_id": model_id, "bsi": None, "n_pairs": 0, "error": str(e)}
