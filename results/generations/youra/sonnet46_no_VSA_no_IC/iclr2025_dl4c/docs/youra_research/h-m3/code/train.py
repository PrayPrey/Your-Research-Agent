import os
import sys
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer

from config import H_M3Config
from reward import make_execution_reward

INSTRUCTION_TEMPLATE = (
    "Write a Python function to solve the following problem.\n\n"
    "Problem: {problem}\n\n"
    "Provide only the function implementation, no explanations.\n"
)


def format_prompt(example: dict) -> dict:
    """Add 'prompt' field for GRPOTrainer using DeepSeek-Coder instruction format."""
    return {
        **example,
        "prompt": INSTRUCTION_TEMPLATE.format(problem=example["text"]),
    }


def build_grpo_config(cfg: H_M3Config, output_dir: str, condition: str) -> GRPOConfig:
    """Build TRL GRPOConfig from H_M3Config."""
    return GRPOConfig(
        output_dir=output_dir,
        num_generations=cfg.num_generations,
        generation_batch_size=cfg.generation_batch_size,
        max_steps=cfg.max_steps,
        learning_rate=cfg.learning_rate,
        beta=cfg.beta,
        logging_steps=cfg.logging_steps,
        save_strategy="no",
        use_vllm=cfg.use_vllm,
        seed=cfg.seed,
        max_completion_length=cfg.max_completion_length,
        per_device_train_batch_size=1,
        report_to="none",
        gradient_checkpointing=True,
    )


def run_grpo(
    cfg: H_M3Config,
    dataset: Dataset,
    output_dir: str,
    condition: str,
) -> tuple:
    """
    H-M3 version: run GRPO with warm-start config.
    Returns (log_history, early_stopped).
    early_stopped=True if frac=1.0 for ALL first early_stop_check_steps steps (cold-start).
    """
    print(f"[train] Starting GRPO: {condition}")

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = dataset.map(format_prompt)

    grpo_config = build_grpo_config(cfg, output_dir, condition)
    reward_fn = make_execution_reward(timeout=cfg.exec_timeout)

    trainer = GRPOTrainer(
        model=model,
        args=grpo_config,
        train_dataset=dataset,
        reward_funcs=[reward_fn],
        processing_class=tokenizer,
    )
    trainer.train()

    log_history = list(trainer.state.log_history)
    print(f"[train] {condition} done. log_history entries: {len(log_history)}")

    # Post-hoc cold-start detection
    frac_values = [
        e.get("frac_reward_zero_std", 1.0)
        for e in log_history
        if "frac_reward_zero_std" in e
    ]
    early_check = frac_values[:cfg.early_stop_check_steps]
    early_stopped = len(early_check) > 0 and all(v >= 1.0 for v in early_check)

    if early_stopped:
        print(
            f"[train] WARNING: {condition} — frac=1.0 for first "
            f"{cfg.early_stop_check_steps} steps (cold-start detected)"
        )

    return log_history, early_stopped
