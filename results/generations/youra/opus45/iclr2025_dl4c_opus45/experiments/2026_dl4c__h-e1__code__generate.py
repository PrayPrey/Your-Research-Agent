"""Code generation for RL and DPO aligned models."""

import json
import os
from typing import List, Tuple

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    T5ForConditionalGeneration,
)
from tqdm import tqdm

from config import ExperimentConfig


def load_rl_model(config: ExperimentConfig) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load Salesforce/codet5-large-ntp-py (T5ForConditionalGeneration, 770M).

    Returns:
        (model, tokenizer) on cuda, eval mode.
    """
    print(f"Loading RL model: {config.rl_model_id}")
    tokenizer = AutoTokenizer.from_pretrained(config.rl_model_id)
    model = T5ForConditionalGeneration.from_pretrained(
        config.rl_model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    model.eval()
    print(f"RL model loaded: {model.config.name_or_path}")
    return model, tokenizer


def load_dpo_model(config: ExperimentConfig) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load codellama/CodeLlama-7b-Instruct-hf (AutoModelForCausalLM, 7B).

    Returns:
        (model, tokenizer) on cuda, eval mode; 8-bit quantization if OOM.
    """
    print(f"Loading DPO model: {config.dpo_model_id}")
    tokenizer = AutoTokenizer.from_pretrained(config.dpo_model_id)

    # Set pad token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    try:
        model = AutoModelForCausalLM.from_pretrained(
            config.dpo_model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    except Exception as e:
        print(f"Failed to load in fp16, trying 8-bit: {e}")
        model = AutoModelForCausalLM.from_pretrained(
            config.dpo_model_id,
            load_in_8bit=True,
            device_map="auto"
        )

    model.eval()
    print(f"DPO model loaded: {model.config.name_or_path}")
    return model, tokenizer


def format_prompt_t5(problem: dict) -> str:
    """Format prompt for T5 encoder-decoder model (CodeT5)."""
    return problem["prompt"]


def format_prompt_causal(problem: dict) -> str:
    """Format prompt for causal LM (CodeLlama)."""
    # CodeLlama Instruct format
    return f"[INST] Complete the following Python function:\n{problem['prompt']}[/INST]\n"


def generate_samples(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    problems: List[dict],
    model_id: str,
    config: ExperimentConfig,
) -> List[dict]:
    """Generate n_samples completions per problem.

    Args:
        model: The pretrained model
        tokenizer: The tokenizer
        problems: List of problem dicts
        model_id: "rl" or "dpo"
        config: Experiment configuration

    Returns:
        List of dicts: [{task_id, model, sample_idx, completion}]
        Total: 542 * 10 = 5420 per model.
    """
    samples = []
    is_t5 = "t5" in model.config.model_type.lower() if hasattr(model.config, "model_type") else "t5" in config.rl_model_id.lower()

    format_prompt = format_prompt_t5 if model_id == "rl" else format_prompt_causal

    # Set device
    device = next(model.parameters()).device

    for problem in tqdm(problems, desc=f"Generating {model_id}"):
        prompt = format_prompt(problem)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        for sample_idx in range(config.n_samples):
            # Set seed for reproducibility
            torch.manual_seed(config.seed + sample_idx)

            with torch.no_grad():
                if is_t5 and model_id == "rl":
                    # T5 encoder-decoder generation
                    outputs = model.generate(
                        input_ids=inputs["input_ids"],
                        attention_mask=inputs.get("attention_mask"),
                        max_new_tokens=config.max_new_tokens,
                        temperature=config.temperature,
                        top_p=config.top_p,
                        do_sample=True,
                        num_return_sequences=1,
                    )
                    completion = tokenizer.decode(outputs[0], skip_special_tokens=True)
                else:
                    # Causal LM generation
                    outputs = model.generate(
                        input_ids=inputs["input_ids"],
                        attention_mask=inputs.get("attention_mask"),
                        max_new_tokens=config.max_new_tokens,
                        temperature=config.temperature,
                        top_p=config.top_p,
                        do_sample=True,
                        num_return_sequences=1,
                        pad_token_id=tokenizer.pad_token_id,
                    )
                    # Extract only the new tokens (completion)
                    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
                    completion = tokenizer.decode(generated_ids, skip_special_tokens=True)

            samples.append({
                "task_id": problem["task_id"],
                "model": model_id,
                "sample_idx": sample_idx,
                "completion": completion,
                "entry_point": problem["entry_point"]
            })

    print(f"Generated {len(samples)} samples for {model_id}")
    return samples


def save_samples(samples: List[dict], path: str) -> None:
    """Save samples as JSONL to outputs/samples_{model_id}.jsonl."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    print(f"Saved {len(samples)} samples to {path}")


def load_samples(path: str) -> List[dict]:
    """Load samples from JSONL file."""
    samples = []
    with open(path, "r") as f:
        for line in f:
            samples.append(json.loads(line.strip()))
    return samples
