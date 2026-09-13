import os
import sys
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer

from config import H_M2Config
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


def build_grpo_config(cfg: H_M2Config, output_dir: str, condition: str) -> GRPOConfig:
    """Build TRL GRPOConfig from H_M2Config."""
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
        max_completion_length=cfg.max_new_tokens,
        per_device_train_batch_size=1,
        report_to="none",
    )


def run_grpo(
    cfg: H_M2Config,
    dataset: Dataset,
    output_dir: str,
    condition: str,
) -> list:
    """
    Load model, run GRPO training for one condition.
    Returns trainer.state.log_history.
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

    # Add prompt column; preserve test_list column for reward_fn kwargs
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
    return log_history
