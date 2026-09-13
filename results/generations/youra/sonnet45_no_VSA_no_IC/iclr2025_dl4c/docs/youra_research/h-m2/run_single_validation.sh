#!/bin/bash
# Single-config validation (binary_350m only)
set -e

LOG=logs/run_single_validation.log
mkdir -p logs checkpoints analysis

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd src
python3 -u << 'PYEOF' 2>&1 | tee -a ../"$LOG"
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

CONFIG_PATH = "../configs/binary_350m.yaml"

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

logger.info(f"Starting validation: {config['experiment_id']}")

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

model_name = config["model"]["name"]
tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

policy_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

model_name_lower = config["model"]["name"].lower()
if "phi" in model_name_lower:
    target_modules = ["q_proj", "v_proj"]
elif "codegen" in model_name_lower:
    target_modules = ["qkv_proj", "out_proj"]
else:
    target_modules = ["q_proj", "v_proj"]  # Default

lora_config = LoraConfig(
    r=config["model"]["lora_r"],
    lora_alpha=config["model"]["lora_alpha"],
    target_modules=target_modules,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

policy_model = get_peft_model(policy_model, lora_config)
policy_model.print_trainable_parameters()

ref_lora_config = LoraConfig(
    r=config["model"]["lora_r"],
    lora_alpha=config["model"]["lora_alpha"],
    target_modules=target_modules,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

ref_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
ref_model = get_peft_model(ref_model, ref_lora_config)
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

logger.info(f"Validation complete. Checkpoint: {checkpoint_path}")
PYEOF
