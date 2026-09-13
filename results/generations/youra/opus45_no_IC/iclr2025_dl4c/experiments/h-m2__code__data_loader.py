"""Data loader for HumanEval + MBPP datasets and code sample generation."""

import random
from typing import List, Dict, Any, Optional
from datasets import load_dataset
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_problems(include_humaneval: bool = True, include_mbpp: bool = True) -> List[Dict[str, Any]]:
    """Load HumanEval (164) + MBPP test (500) = 664 problems."""
    problems = []

    if include_humaneval:
        humaneval = load_dataset("openai/openai_humaneval", split="test")
        for idx, item in enumerate(humaneval):
            problems.append({
                "id": f"humaneval_{idx}",
                "source": "humaneval",
                "prompt": item["prompt"],
                "canonical_solution": item.get("canonical_solution", ""),
                "test": item.get("test", ""),
                "entry_point": item.get("entry_point", ""),
            })

    if include_mbpp:
        mbpp = load_dataset("google-research-datasets/mbpp", "full", split="test")
        for idx, item in enumerate(mbpp):
            test_code = "\n".join(item.get("test_list", []))
            problems.append({
                "id": f"mbpp_{idx}",
                "source": "mbpp",
                "prompt": item["text"] + "\n" + item["code"].split("\n")[0] if "def " in item["code"] else item["text"],
                "canonical_solution": item.get("code", ""),
                "test": test_code,
                "entry_point": "",
            })

    return problems


def load_model_and_tokenizer(
    model_name: str = "meta-llama/CodeLlama-7b-Instruct-hf",
    device: str = "cuda",
    dtype: str = "bfloat16"
) -> tuple:
    """Load CodeLlama-7B-Instruct model and tokenizer."""
    dtype_map = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
    torch_dtype = dtype_map.get(dtype, torch.bfloat16)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        device_map="auto",
        trust_remote_code=True
    )
    model.eval()

    return model, tokenizer


def generate_code_sample(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.95,
    do_sample: bool = True
) -> str:
    """Generate code completion using the model."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature if do_sample else 1.0,
            top_p=top_p if do_sample else 1.0,
            do_sample=do_sample,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
    generated_code = tokenizer.decode(generated_ids, skip_special_tokens=True)

    return generated_code


def generate_batch_samples(
    model,
    tokenizer,
    problems: List[Dict[str, Any]],
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.95,
    seed: int = 42,
    max_samples: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Generate code samples for multiple problems."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    if max_samples:
        problems = problems[:max_samples]

    results = []
    for i, problem in enumerate(problems):
        if (i + 1) % 50 == 0:
            print(f"Generated {i + 1}/{len(problems)} samples")

        generated = generate_code_sample(
            model, tokenizer, problem["prompt"],
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p
        )

        full_code = problem["prompt"] + generated

        results.append({
            **problem,
            "generated_code": generated,
            "full_code": full_code
        })

    return results


def load_pregenerated_samples(path: str) -> List[Dict[str, Any]]:
    """Load pre-generated code samples from JSON file."""
    import json
    with open(path, "r") as f:
        return json.load(f)


def save_generated_samples(samples: List[Dict[str, Any]], path: str):
    """Save generated samples to JSON file."""
    import json
    with open(path, "w") as f:
        json.dump(samples, f, indent=2)
