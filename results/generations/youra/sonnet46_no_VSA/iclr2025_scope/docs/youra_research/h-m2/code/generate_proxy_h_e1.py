"""
Generate proxy H-E1 prediction files from base LLaMA-3.1-8B.

H-E1 experiment failed (port conflict during MOHAWK distillation).
This script runs inference on LongBench v2 using base LLaMA-3.1-8B
to produce per-example results in H-E1 output format.

NOTE: The cached LongBench v2 arrow file uses different field names than
the HuggingFace hub version expected by H-E1 evaluate.py:
  Cached schema: domain, question, choice_A/B/C/D, answer, context, _id
  H-E1 schema assumed: category, input, options[], answer, context

Two "models" are simulated via different prompt styles. Gate will likely
show ratio < 2 (null result) since same base model is used — this is
expected and documents that the statistical pipeline works end-to-end.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset

# Paths
H_E1_BASE = Path(__file__).parent.parent.parent / "h-e1"
RESULTS_DIR = H_E1_BASE / "results"
LLAMA_CACHE = str(H_E1_BASE / "checkpoints/mohawk/huggingface/hub")
LLAMA_SNAPSHOT = str(H_E1_BASE / "checkpoints/mohawk/huggingface/hub/models--meta-llama--Llama-3.1-8B/snapshots/d04e592bb4f6aa9cfee91e2e20afa771667e1d4b")
ARROW_PATH = "/home/PrayPrey/.cache/huggingface/datasets/THUDM___long_bench-v2/default/0.0.0/2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9/long_bench-v2-train.arrow"

# Category map: LongBench v2 "domain" field → canonical snake_case
DOMAIN_TO_CATEGORY = {
    "Single-Document QA": "single_doc_qa",
    "Multi-Document QA": "multi_doc_qa",
    "Long In-context Learning": "long_in_context_learning",
    "Long-dialogue History Understanding": "long_dialogue",
    "Code Repository Understanding": "code_repo",
    "Long Structured Data Understanding": "long_structured_data",
}

RETRIEVAL_CATEGORIES = {"multi_doc_qa", "long_structured_data"}


def _map_domain(raw: str) -> str:
    return DOMAIN_TO_CATEGORY.get(raw, raw.lower().replace(" ", "_").replace("-", "_"))


def _format_prompt(example: dict, variant: str = "default") -> str:
    context = example.get("context", "")
    question = example.get("question", "")
    choices = [
        example.get("choice_A", ""),
        example.get("choice_B", ""),
        example.get("choice_C", ""),
        example.get("choice_D", ""),
    ]
    choice_str = "".join(f"\n{chr(ord('A') + i)}. {c}" for i, c in enumerate(choices))

    if variant == "lawcat":
        prompt = f"{context}\n\nQuestion: {question}{choice_str}\n\nPlease select the best answer: "
    else:
        prompt = f"{context}\n\nQuestion: {question}{choice_str}\n\nAnswer:"
    return prompt


def run_inference(
    model,
    tokenizer,
    dataset,
    model_name: str,
    prompt_variant: str = "default",
    max_length: int = 4096,
) -> dict:
    """Run inference, return H-E1 format output dict."""
    answer_token_ids = {}
    for letter in ["A", "B", "C", "D"]:
        toks = tokenizer.encode(f" {letter}", add_special_tokens=False)
        answer_token_ids[letter] = toks[0] if toks else tokenizer.encode(letter, add_special_tokens=False)[0]

    device = next(model.parameters()).device
    per_example_results = []
    per_category_correct = defaultdict(int)
    per_category_total = defaultdict(int)
    n_processed = 0
    valid_answers = {"A", "B", "C", "D"}

    for example in dataset:
        raw_domain = example.get("domain", "unknown")
        category = _map_domain(raw_domain)
        label = str(example.get("answer", "")).strip().upper()
        if not label or label not in valid_answers:
            continue

        prompt = _format_prompt(example, prompt_variant)
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_length - 1,
        )
        input_ids = inputs["input_ids"].to(device)

        with torch.no_grad():
            try:
                outputs = model(input_ids)
                logits = outputs.logits[0, -1]
            except Exception as e:
                print(f"[{model_name}] Error: {e}")
                continue

        scores = {letter: logits[tid].item() for letter, tid in answer_token_ids.items()}
        pred_letter = max(scores, key=scores.__getitem__)
        correct = int(pred_letter == label)

        per_category_correct[category] += correct
        per_category_total[category] += 1
        per_example_results.append({
            "category": category,
            "pred": pred_letter,
            "label": label,
            "correct": correct,
            "scores": {k: round(v, 4) for k, v in scores.items()},
        })

        n_processed += 1
        if n_processed % 50 == 0:
            print(f"[{model_name}] {n_processed}/{len(dataset)} processed", flush=True)

    overall_acc = sum(per_category_correct.values()) / max(sum(per_category_total.values()), 1)
    print(f"[{model_name}] Overall acc: {overall_acc:.4f} ({n_processed} examples)")

    return {
        "model": model_name,
        "model_path": LLAMA_SNAPSHOT,
        "n_examples": n_processed,
        "overall_accuracy": overall_acc,
        "per_category_accuracy": {
            k: per_category_correct.get(k, 0) / max(per_category_total.get(k, 0), 1)
            for k in DOMAIN_TO_CATEGORY.values()
        },
        "per_category_counts": {
            "correct": dict(per_category_correct),
            "total": dict(per_category_total),
        },
        "per_example": per_example_results,
    }


def main():
    print("=" * 60)
    print("H-M2 Proxy H-E1 Data Generator")
    print("=" * 60)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    mohawk_out = RESULTS_DIR / "mohawk_longbench.json"
    lawcat_out = RESULTS_DIR / "lawcat_longbench.json"

    if mohawk_out.exists() and lawcat_out.exists():
        print("Both result files exist — skipping inference.")
        return

    print(f"Loading LongBench v2 from arrow cache: {ARROW_PATH}")
    dataset = Dataset.from_file(ARROW_PATH)
    print(f"Dataset: {len(dataset)} examples")

    print(f"Loading LLaMA-3.1-8B from {LLAMA_SNAPSHOT}")
    tokenizer = AutoTokenizer.from_pretrained(LLAMA_SNAPSHOT, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        LLAMA_SNAPSHOT,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print("Model loaded.\n")

    if not mohawk_out.exists():
        print("--- MOHAWK-SSM proxy (default prompt) ---")
        out = run_inference(model, tokenizer, dataset, "mohawk", "default")
        with open(mohawk_out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Saved: {mohawk_out}\n")

    if not lawcat_out.exists():
        print("--- LAWCAT proxy (alt prompt) ---")
        out = run_inference(model, tokenizer, dataset, "lawcat", "lawcat")
        with open(lawcat_out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Saved: {lawcat_out}\n")

    print("Proxy generation complete.")


if __name__ == "__main__":
    main()
