"""Orchestrator for h-m2 training dynamics measurement (6 runs)."""

import os
import sys
import yaml
import logging
import torch
from pathlib import Path
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType

from dynamics_logger import DynamicsLogger
from sandbox import ExecutionSandbox
from train import GRPOTrainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG_PATHS = [
    "../configs/binary_350m.yaml",
    "../configs/error_type_350m.yaml",
    "../configs/error_trace_350m.yaml",
    "../configs/binary_phi2.yaml",
    "../configs/error_type_phi2.yaml",
    "../configs/error_trace_phi2.yaml"
]

def load_config(config_path: str) -> dict:
    """Load experiment configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_model(config: dict):
    """Initialize model with LoRA."""
    model_name = config["model"]["name"]
    trust_remote_code = "phi" in model_name.lower()

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=trust_remote_code)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=trust_remote_code,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    lora_config = LoraConfig(
        r=config["model"]["lora_r"],
        lora_alpha=config["model"]["lora_alpha"],
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model, tokenizer

def run_single_experiment(config_path: str):
    """Run one GRPO training experiment with dynamics logging."""
    config = load_config(config_path)
    logger.info(f"\n{'='*80}\nStarting experiment: {config['experiment_id']}\n{'='*80}")

    os.makedirs(config["logging"]["checkpoint_dir"], exist_ok=True)
    os.makedirs(Path(config["logging"]["dynamics_log"]).parent, exist_ok=True)

    dataset = load_dataset("openai_humaneval", split="test")
    test_suites = [
        {
            "prompt": item["prompt"],
            "test": item["test"],
            "entry_point": item["entry_point"]
        }
        for item in dataset
    ]

    policy_model, tokenizer = setup_model(config)
    ref_model, _ = setup_model(config)  # Frozen reference
    ref_model.eval()

    sandbox = ExecutionSandbox(config)
    dynamics_logger = DynamicsLogger(
        output_path=config["logging"]["dynamics_log"],
        experiment_id=config["experiment_id"]
    )

    trainer = GRPOTrainer(
        config=config,
        policy_model=policy_model,
        ref_model=ref_model,
        tokenizer=tokenizer,
        sandbox=sandbox,
        dynamics_logger=dynamics_logger
    )

    grpo_config = config["training"].copy()
    grpo_config["checkpoint_dir"] = config["logging"]["checkpoint_dir"]
    grpo_config["log_interval"] = config["training"]["log_interval"]
    grpo_config["save_interval"] = config["training"]["save_interval"]

    checkpoint_path = trainer.train(test_suites, config["feedback_type"], grpo_config)

    dynamics_logger.finalize()
    logger.info(f"Experiment {config['experiment_id']} complete. Checkpoint: {checkpoint_path}")

def main():
    """Run all 6 h-m2 experiments sequentially."""
    logger.info(f"Starting h-m2 dynamics measurement pipeline ({len(CONFIG_PATHS)} experiments)")

    for config_path in CONFIG_PATHS:
        if not os.path.exists(config_path):
            logger.error(f"Config not found: {config_path}")
            continue

        try:
            run_single_experiment(config_path)
        except Exception as e:
            logger.error(f"Experiment {config_path} failed: {e}", exc_info=True)
            continue

    logger.info("\n" + "="*80 + "\nAll h-m2 experiments complete\n" + "="*80)

if __name__ == "__main__":
    main()
