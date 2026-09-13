"""LongBench v2 evaluation + Δ_norm computation for all 4 models."""
import os
import sys
import json
import re
from collections import defaultdict
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
MOHAWK_REPO = str(HYPOTHESIS_DIR / "repos" / "mohawk")
if MOHAWK_REPO not in sys.path:
    sys.path.insert(0, MOHAWK_REPO)

from config import (
    CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY,
    LONGBENCH_DATASET, RESULTS_DIR, HF_CACHE,
)

# LongBench v2 category name mapping (dataset field → our canonical names)
CATEGORY_MAP = {
    "single-document QA": "single_doc_qa",
    "multi-document QA": "multi_doc_qa",
    "long in-context learning": "long_in_context_learning",
    "long-dialogue history understanding": "long_dialogue",
    "code repository understanding": "code_repo",
    "long structured data understanding": "long_structured_data",
    # Fallbacks
    "single_doc_qa": "single_doc_qa",
    "multi_doc_qa": "multi_doc_qa",
    "long_in_context_learning": "long_in_context_learning",
    "long_dialogue": "long_dialogue",
    "code_repo": "code_repo",
    "long_structured_data": "long_structured_data",
}


def _map_category(raw: str) -> str:
    """Normalize LongBench v2 category string to canonical form."""
    # Try direct map first
    if raw in CATEGORY_MAP:
        return CATEGORY_MAP[raw]
    # Try case-insensitive
    raw_lower = raw.lower().strip()
    for k, v in CATEGORY_MAP.items():
        if raw_lower == k.lower():
            return v
    # Default: return cleaned version
    return raw_lower.replace(" ", "_").replace("-", "_")


def _format_mcq_prompt(example: dict) -> str:
    """Format a LongBench v2 MCQ example as a 0-shot prompt."""
    context = example.get("context", "")
    input_text = example.get("input", "")
    choices = example.get("options", [])

    # Build choice string
    choice_str = ""
    for i, choice in enumerate(choices):
        letter = chr(ord("A") + i)
        choice_str += f"\n{letter}. {choice}"

    prompt = f"{context}\n\nQuestion: {input_text}{choice_str}\n\nAnswer:"
    return prompt


def _is_mohawk_config(config_path: Path) -> bool:
    """Return True if config.json is a MOHAWK config (not a HF config)."""
    try:
        with open(config_path) as f:
            data = json.load(f)
        return "ComponentsConfig" in data or "DistillConfig" in data or "TrainConfig" in data
    except Exception:
        return False


def evaluate_model_longbench(
    model_path: str,
    model_name: str,
    output_json: str,
    max_examples: int | None = None,
) -> dict[str, float]:
    """
    Evaluate model on LongBench v2. Returns {category: accuracy}.
    Args:
        model_path: HuggingFace model dir or identifier
        model_name: "teacher" | "mohawk" | "lawcat" | "hybrid4"
        output_json: path to write per-model results
        max_examples: if set, limit to first N examples (for quick check)
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"\n[Eval] Loading model: {model_path}")

    # Detect MOHAWK checkpoint (has config.json in MOHAWK format, not HF format)
    is_mohawk = (Path(model_path) / "config.json").exists() and not (
        Path(model_path) / "tokenizer.json"
    ).exists() or (
        (Path(model_path) / "config.json").exists() and
        _is_mohawk_config(Path(model_path) / "config.json")
    )

    if is_mohawk:
        from utils.config import Config
        from utils.init_model import lazy_init

        ckpt_dir = Path(model_path)
        cfg = Config.from_json(str(ckpt_dir / "config.json"))

        # Get tokenizer source from config
        tokenizer_source = None
        try:
            tokenizer_source = cfg.TrainConfig.get("tokenizer") or cfg.TeacherConfig.dir
        except Exception:
            tokenizer_source = "meta-llama/Llama-3.1-8B"

        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_source,
            cache_dir=str(Path(HF_CACHE) / "hub"),
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        wrapper = lazy_init(
            cfg=cfg,
            details_cfg=cfg.TrainConfig,
            load_cfg=Config.from_dict({"model": [{"path": str(ckpt_dir)}]}),
            mode="inference",
            components_cfg=cfg.ComponentsConfig,
        )
        model = wrapper.model
        model.eval()
    else:
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            cache_dir=str(Path(HF_CACHE) / "hub"),
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            cache_dir=str(Path(HF_CACHE) / "hub"),
        )
        model.eval()

    # Pre-compute token IDs for answer letters A, B, C, D
    answer_token_ids = {}
    for letter in ["A", "B", "C", "D"]:
        toks = tokenizer.encode(f" {letter}", add_special_tokens=False)
        answer_token_ids[letter] = toks[0] if toks else tokenizer.encode(letter, add_special_tokens=False)[0]

    # Get model device
    if hasattr(model, "device"):
        model_device = model.device
    else:
        try:
            model_device = next(model.parameters()).device
        except StopIteration:
            model_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"[Eval] Loading LongBench v2 dataset")
    dataset = load_dataset(
        "THUDM/LongBench",
        "v2",
        split="train",  # LongBench v2 uses "train" split for test set
        cache_dir=str(Path(HF_CACHE) / "datasets"),
    )

    per_category_correct: dict[str, int] = defaultdict(int)
    per_category_total: dict[str, int] = defaultdict(int)
    per_example_results: list[dict] = []

    valid_answers = {"A", "B", "C", "D"}
    n_processed = 0

    for example in dataset:
        if max_examples and n_processed >= max_examples:
            break

        raw_cat = example.get("category", "unknown")
        category = _map_category(raw_cat)
        label = str(example.get("answer", "")).strip().upper()
        if not label or label not in valid_answers:
            continue

        prompt = _format_mcq_prompt(example)

        # Tokenize — truncate to model's max context
        max_length = 8192  # safe default for all models
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_length - 1,
        )
        input_ids = inputs["input_ids"].to(model_device)

        with torch.no_grad():
            # Get logits for last position (next-token prediction)
            try:
                outputs = model(input_ids)
                # Handle both HF CausalLMOutput and MOHAWK tuple/dict
                if hasattr(outputs, "logits"):
                    logits = outputs.logits[0, -1]
                elif isinstance(outputs, (tuple, list)):
                    logits = outputs[0][0, -1]
                else:
                    logits = outputs[0, -1]
            except Exception as e:
                print(f"[Eval] Forward pass error: {e}")
                continue

        # Pick answer with highest log-prob among A/B/C/D
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
            "scores": scores,
        })

        n_processed += 1
        if n_processed % 50 == 0:
            print(f"[Eval {model_name}] {n_processed} examples processed")

    # Compute per-category accuracy
    results: dict[str, float] = {}
    for cat in CATEGORIES:
        total = per_category_total.get(cat, 0)
        correct = per_category_correct.get(cat, 0)
        results[cat] = correct / max(total, 1)

    overall_acc = sum(per_category_correct.values()) / max(sum(per_category_total.values()), 1)
    print(f"[Eval {model_name}] Overall accuracy: {overall_acc:.4f}")
    for cat in CATEGORIES:
        print(f"  {cat}: {results[cat]:.4f} ({per_category_correct[cat]}/{per_category_total[cat]})")

    # Save results
    output = {
        "model": model_name,
        "model_path": model_path,
        "n_examples": n_processed,
        "overall_accuracy": overall_acc,
        "per_category_accuracy": results,
        "per_category_counts": {
            "correct": dict(per_category_correct),
            "total": dict(per_category_total),
        },
        "per_example": per_example_results,
    }
    with open(output_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[Eval {model_name}] Results saved to {output_json}")

    return results


def compute_delta_norm(
    teacher_results: dict[str, float],
    student_results: dict[str, float],
) -> dict[str, float]:
    """Compute Δ_norm = (Acc_teacher - Acc_student) / max(Acc_teacher, 1e-8) per category."""
    delta_norm = {}
    for category in CATEGORIES:
        acc_t = teacher_results.get(category, 0.0)
        acc_s = student_results.get(category, 0.0)
        delta_norm[category] = (acc_t - acc_s) / max(acc_t, 1e-8)
    return delta_norm


def run_all_evaluations(
    teacher_path: str,
    mohawk_ckpt: str,
    lawcat_ckpt: str,
    hybrid4_ckpt: str,
    results_dir: str | None = None,
) -> dict[str, dict[str, float]]:
    """
    Evaluate all 4 models on LongBench v2 and compute Δ_norm for students.
    Returns {model_name: {category: delta_norm or accuracy}}.
    """
    if results_dir is None:
        results_dir = str(RESULTS_DIR)
    os.makedirs(results_dir, exist_ok=True)

    models = {
        "teacher": teacher_path,
        "mohawk": mohawk_ckpt,
        "lawcat": lawcat_ckpt,
        "hybrid4": hybrid4_ckpt,
    }

    raw_accuracies: dict[str, dict[str, float]] = {}
    for model_name, model_path in models.items():
        out_json = os.path.join(results_dir, f"{model_name}_longbench.json")
        print(f"\n{'='*60}")
        print(f"Evaluating {model_name}")
        raw_accuracies[model_name] = evaluate_model_longbench(
            model_path=model_path,
            model_name=model_name,
            output_json=out_json,
        )

    # Compute Δ_norm for students
    teacher_acc = raw_accuracies["teacher"]
    delta_norms: dict[str, dict[str, float]] = {}
    for student_name in ["mohawk", "lawcat", "hybrid4"]:
        delta_norms[student_name] = compute_delta_norm(teacher_acc, raw_accuracies[student_name])

    # Save summary
    summary = {
        "raw_accuracies": raw_accuracies,
        "delta_norms": delta_norms,
        "retrieval_heavy_categories": list(RETRIEVAL_HEAVY),
        "generation_heavy_categories": list(GENERATION_HEAVY),
    }
    summary_path = os.path.join(results_dir, "evaluation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {summary_path}")

    return {
        "raw_accuracies": raw_accuracies,
        "delta_norms": delta_norms,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--teacher", type=str, required=True)
    p.add_argument("--mohawk", type=str, required=True)
    p.add_argument("--lawcat", type=str, required=True)
    p.add_argument("--hybrid4", type=str, required=True)
    p.add_argument("--results-dir", type=str, default=str(RESULTS_DIR))
    p.add_argument("--max-examples", type=int, default=None,
                   help="Limit evaluation to first N examples (for debugging)")
    args = p.parse_args()

    results = run_all_evaluations(
        teacher_path=args.teacher,
        mohawk_ckpt=args.mohawk,
        lawcat_ckpt=args.lawcat,
        hybrid4_ckpt=args.hybrid4,
        results_dir=args.results_dir,
    )
    print("\nDelta norms:")
    for model, dn in results["delta_norms"].items():
        print(f"  {model}:")
        for cat, val in dn.items():
            print(f"    {cat}: {val:.4f}")
